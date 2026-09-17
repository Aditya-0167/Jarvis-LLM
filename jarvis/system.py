from __future__ import annotations
import json
import time
from pathlib import Path
import torch

from .autonomy import ExperimentRegistry, choose_next_actions
from .chat import answer as chat_answer
from .crawler import PublicWebCrawler
from .evolution import Evolution
from .generate import generate
from .model import make_model, parameter_count, transfer_compatible
from .retrieval import LexicalRetriever
from .policy import IntrinsicPolicy
from .storage import Storage
from .trainer import Trainer
from .web import fetch_public


class JarvisSystem:
    def __init__(self, cfg):
        self.cfg = cfg
        self.storage = Storage(cfg)
        self.storage.experiments = ExperimentRegistry(self.storage.workspace / "experiments.jsonl")
        self.storage.ensure()
        self.storage.cfg_local = lambda: self.cfg["models"]["local"]
        self.trainer = Trainer(cfg, self.storage)
        self.evolver = Evolution(cfg, self.storage, self.trainer)
        self.retriever = LexicalRetriever(self.storage.corpus, cfg["retrieval"]["chunk_chars"])
        self.crawler = PublicWebCrawler(cfg["web"]["timeout"], cfg["web"]["crawl_delay_seconds"], cfg["web"]["max_chars"])
        self.intrinsic_policy = IntrinsicPolicy(self.storage, cfg["seed"])
        self.program_path = self.storage.workspace / "development_plan.json"
        self._chat_model = None
        self._chat_generation = None

    def initialize(self):
        self.storage.ensure()
        state = self.storage.load_state()
        if state["architecture"] is None:
            cfg = self.cfg["models"]["local"].copy()
            torch.manual_seed(int(self.cfg["seed"]))
            model = make_model(cfg)
            self.storage.save_checkpoint(0, model, cfg, metrics={"event": "birth"})
            state.update({"architecture": cfg, "parameters": parameter_count(model), "profile": "local"})
            self.storage.save_state(state)
            self.storage.memory.add("birth", {"generation": 0, "architecture": cfg, "parameters": parameter_count(model)})
        return state

    def _save_model_state(self, model, cfg, state, metrics=None):
        self.storage.save_checkpoint(int(state["generation"]), model, cfg, metrics=metrics or {})
        self.storage.save_state(state)
        self._chat_model = None

    def bootstrap(self, steps=None):
        self.initialize()
        model, cfg = self.storage.load_model()
        result = self.trainer.train(model, cfg, steps or max(40, int(self.cfg["training"]["warmup_steps"])))
        state = self.storage.load_state()
        state["training_steps"] += result["steps"]
        state["best_eval_loss"] = result["loss_after"] if state["best_eval_loss"] is None else min(state["best_eval_loss"], result["loss_after"])
        self._save_model_state(model, cfg, state, result)
        self.storage.memory.add("training", result)
        return result

    def train(self, steps=None, progress=None):
        self.initialize()
        model, cfg = self.storage.load_model()
        total = int(steps or self.cfg["training"]["steps_per_cycle"])
        generation = self.storage.load_state()["generation"]
        self.storage.events.emit("train_start", {"generation": generation, "steps": total, "device": self.trainer.device})
        state = self.storage.load_state()
        state["runtime"] = {"running": True, "operation": "train", "step": 0, "total": total, "loss": None}
        self.storage.save_state(state)

        def on_progress(row):
            current = self.storage.load_state()
            current["runtime"] = {"running": True, "operation": "train", "step": int(row["step"]), "total": int(row["total"]), "loss": float(row["loss"])}
            self.storage.save_state(current)
            self.storage.events.emit("train_step", {"generation": current["generation"], **row})
            if progress is not None:
                progress(row)

        try:
            result = self.trainer.train(model, cfg, total, progress=on_progress)
        finally:
            current = self.storage.load_state()
            current["runtime"] = {"running": False, "operation": None, "step": total, "total": total, "loss": None}
            self.storage.save_state(current)

        state = self.storage.load_state()
        state["training_steps"] += result["steps"]
        state["best_eval_loss"] = result["loss_after"] if state["best_eval_loss"] is None else min(state["best_eval_loss"], result["loss_after"])
        self._save_model_state(model, cfg, state, result)
        self.storage.memory.add("training", result)
        self.storage.events.emit("train_end", {"generation": state["generation"], **result})
        return result

    def evolve(self):
        self.initialize()
        model, cfg = self.storage.load_model()
        profile = self.storage.load_state().get("profile", "local")
        self.storage.events.emit("evolve_start", {"generation": self.storage.load_state()["generation"], "profile": profile})
        result = self.evolver.run_once(model, cfg, profile)
        state = self.storage.load_state()
        gen = int(state["generation"]) + 1
        chosen_model = result["model"]
        chosen_cfg = result["model_cfg"]
        if result["accepted"]:
            state["accepted_changes"] += 1
        state.update({
            "generation": gen,
            "architecture": chosen_cfg,
            "parameters": parameter_count(chosen_model),
            "best_eval_loss": min(float(state["best_eval_loss"]), float(result["best_loss"])) if state["best_eval_loss"] is not None else float(result["best_loss"]),
            "last_evolution": {k: v for k, v in result.items() if k != "model"}
        })
        safe_result = {k: v for k, v in result.items() if k != "model"}
        self._save_model_state(chosen_model, chosen_cfg, state, safe_result)
        gdir = self.storage.generations / f"generation_{gen:06d}"
        gdir.mkdir(parents=True, exist_ok=True)
        (gdir / "result.json").write_text(json.dumps(safe_result, indent=2), encoding="utf-8")
        state["lineage"] = (state.get("lineage", []) + [{"generation": gen, "action": state["last_evolution"]["action"], "accepted": result["accepted"], "parameters": state["parameters"]}])[-500:]
        self.storage.save_state(state)
        self.storage.memory.add("evolution", state["last_evolution"])
        self.storage.events.emit("evolve_end", {"generation": gen, **state["last_evolution"]})
        return state["last_evolution"]

    def ingest_url(self, url: str):
        text = fetch_public(url, self.cfg["web"]["timeout"], self.cfg["web"]["max_chars"])
        record = self.storage.corpus.add(text, url, "public")
        self.retriever.invalidate()
        self.storage.memory.add("ingest", record)
        return record

    def ingest_file(self, path: str):
        p = Path(path)
        text = p.read_text(encoding="utf-8", errors="ignore")
        record = self.storage.corpus.add(text, str(p), "local")
        self.retriever.invalidate()
        self.storage.memory.add("ingest", record)
        return record

    def crawl(self, seeds=None, max_pages=None, max_depth=None):
        policy = self.storage.load_policy()
        seeds = seeds or self.cfg["web"].get("seed_urls", [])
        pages = self.crawler.crawl(
            seeds=list(seeds),
            max_pages=max_pages or policy.get("max_web_pages_per_cycle", 6),
            max_depth=max_depth if max_depth is not None else self.cfg["web"]["max_depth"],
            same_host=not bool(policy.get("allow_cross_host", False))
        )
        added = 0
        errors = 0
        for page in pages:
            if page.get("text"):
                rec = self.storage.corpus.add(page["text"], page["url"], "public_crawl")
                added += int(rec.get("added", 0))
            if page.get("error"):
                errors += 1
        self.retriever.invalidate()
        state = self.storage.load_state()
        state["web_pages"] = int(state.get("web_pages", 0)) + sum(1 for p in pages if p.get("text"))
        state["web_pages_session"] = sum(1 for p in pages if p.get("text"))
        state["last_web_cycle"] = time.time()
        state["last_error"] = None if errors == 0 else f"{errors} crawl errors; inspect memory log"
        self.storage.save_state(state)
        self.storage.memory.add("web_crawl", {"pages_seen": len(pages), "pages_added": sum(1 for p in pages if p.get("text")), "characters_added": added, "errors": errors})
        return {"pages": pages, "characters_added": added, "errors": errors}

    def learn_web(self):
        return self.crawl()

    def bundle(self, destination=None):
        path = self.storage.make_bundle(destination)
        self.storage.memory.add("bundle", {"path": str(path)})
        return {"bundle": str(path)}

    def set_profile(self, profile: str):
        if profile not in self.cfg["models"]:
            raise ValueError(f"Unknown profile: {profile}")
        self.initialize()
        state = self.storage.load_state()
        base_model, _ = self.storage.load_model()
        target_cfg = self.cfg["models"][profile].copy()
        target = transfer_compatible(base_model, make_model(target_cfg))
        state["profile"] = profile
        state["architecture"] = target_cfg
        state["parameters"] = parameter_count(target)
        gen = int(state["generation"]) + 1
        state["generation"] = gen
        self._save_model_state(target, target_cfg, state, {"event": "profile_upgrade", "profile": profile})
        self.storage.memory.add("profile_upgrade", {"profile": profile, "parameters": parameter_count(target), "generation": gen})
        return state

    def runtime_events(self, limit=60):
        return self.storage.events.recent(limit)

    def status(self):
        self.initialize()
        state = self.storage.load_state()
        corpus_chars = len(self.storage.corpus.text())
        return {
            **state,
            "corpus_characters": corpus_chars,
            "memory_records": len(self.storage.memory.recent(100000)),
            "experiment_records": len(self.storage.experiments.recent(100000)),
            "device": self.trainer.device,
            "checkpoint": str(self.storage.latest_checkpoint()) if self.storage.latest_checkpoint() else None
        }

    def benchmark(self):
        from .benchmarks import report
        model, _ = self.storage.load_model()
        return report(model, self.storage.corpus, self.cfg["training"]["eval_batches"], self.trainer.device)

    def model_for_chat(self):
        state = self.storage.load_state()
        if self._chat_model is None or self._chat_generation != state["generation"]:
            self._chat_model, _ = self.storage.load_model()
            self._chat_generation = state["generation"]
        return self._chat_model

    def chat(self, text: str):
        self.initialize()
        result = chat_answer(self, text)
        self.storage.memory.add("interaction", {
            "user": text,
            "reply": result["reply"],
            "retrieval_hits": len(result["retrieval"]),
            "generation": result["generation"]
        })
        return result

    def develop_once(self):
        action = self.intrinsic_policy.choose()
        before = self.status().get("best_eval_loss")
        train_result = None
        evolution_result = None
        web_result = None
        if action == "train":
            train_result = self.train()
        elif action == "evolve":
            evolution_result = self.evolve()
        elif action == "web":
            web_result = self.learn_web()
            if web_result.get("characters_added", 0) > 0:
                train_result = self.train(max(2, int(self.cfg["training"].get("web_followup_steps", 4))))
        else:
            self.benchmark()
        after = self.status().get("best_eval_loss")
        improved = before is None or after is None or float(after) < float(before)
        self.intrinsic_policy.update(action, improved)
        state = self.storage.load_state()
        plan = {
            "generation": state["generation"],
            "selected_action": action,
            "observations": {
                "training_loss_after": (train_result or {}).get("loss_after"),
                "evolution_action": (evolution_result or {}).get("action"),
                "accepted": (evolution_result or {}).get("accepted"),
                "web_characters_added": (web_result or {}).get("characters_added", 0),
                "intrinsic_improvement": improved
            },
            "next_actions": choose_next_actions(state, evolution_result, self.storage.load_policy().get("web_learning", True)),
            "policy": self.intrinsic_policy.load(),
            "note": "Machine-generated control data, not a claim of consciousness or AGI."
        }
        self.program_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
        self.storage.memory.add("policy_step", {"action": action, "improved": improved})
        return plan

    def serve(self):
        from .server import create_app
        create_app(self).run(host=self.cfg["runtime"]["host"], port=int(self.cfg["runtime"]["port"]), threaded=True)

    def autonomous_loop(self, max_cycles=None):
        self.initialize()
        cycle = 0
        while max_cycles is None or cycle < int(max_cycles):
            cycle += 1
            print(f"=== JARVIS V6 CYCLE {cycle} ===")
            try:
                print("DEVELOP", self.develop_once())
            except Exception as exc:
                self.storage.memory.add("error", {"error": repr(exc), "cycle": cycle})
                state = self.storage.load_state()
                state["last_error"] = repr(exc)
                self.storage.save_state(state)
                print("ERROR", repr(exc))
            time.sleep(float(self.cfg["runtime"]["train_every_seconds"]))
