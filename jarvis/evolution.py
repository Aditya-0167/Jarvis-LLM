from __future__ import annotations
import copy
import json
import random
import uuid
from .model import make_model, parameter_count, transfer_compatible
from .autonomy import Trial


class Evolution:
    """Bounded architecture evolution with measurement, acceptance and lineage."""
    def __init__(self, cfg, storage, trainer):
        self.cfg = cfg
        self.storage = storage
        self.trainer = trainer

    def candidates(self, base_cfg, profile):
        evo = self.cfg["evolution"]
        state = self.storage.load_state()
        rng = random.Random(int(self.cfg["seed"]) + int(state["generation"]) * 9973)
        max_layers = evo["max_layers_local"] if profile == "local" else evo["max_layers_colab"] if profile == "colab" else evo["max_layers_cloud"]
        out, seen = [], set()
        actions = ["add_layer", "add_expert", "widen", "narrow_dropout", "widen_context", "increase_top_k"]
        attempts = 0
        max_attempts = max(20, int(evo["architecture_candidates"]) * 20)
        while len(out) < int(evo["architecture_candidates"]) and attempts < max_attempts:
            attempts += 1
            c = copy.deepcopy(base_cfg)
            action = rng.choice(actions)
            if action == "add_layer":
                c["n_layers"] = min(max_layers, int(c["n_layers"]) + 1)
            elif action == "add_expert":
                c["experts"] = min(int(evo["max_experts"]), int(c["experts"]) + 1)
            elif action == "widen":
                d = min(int(evo["max_d_model"]), int(c["d_model"]) + int(evo.get("width_step", 64)))
                d -= d % int(c["n_heads"])
                c["d_model"] = max(int(c["n_heads"]), d)
            elif action == "narrow_dropout":
                c["dropout"] = round(max(0.0, float(c["dropout"]) - 0.025), 3)
            elif action == "widen_context":
                c["block_size"] = min(int(evo["max_block_size"]), int(c["block_size"]) + 128)
            else:
                c["top_k_experts"] = min(int(c["experts"]), int(c.get("top_k_experts", 2)) + 1)
            key = json.dumps(c, sort_keys=True)
            if key not in seen and c != base_cfg:
                seen.add(key)
                out.append((action, c))
        return out

    def run_once(self, base_model, base_cfg, profile):
        base_loss = self.trainer.evaluate(base_model)
        candidates = []
        candidate_specs = self.candidates(base_cfg, profile)
        for action, cfg in candidate_specs:
            candidate = transfer_compatible(base_model, make_model(cfg))
            steps = int(self.cfg["evolution"].get("steps_by_profile", {}).get(profile, self.cfg["evolution"]["architecture_steps"]))
            result = self.trainer.train_model(candidate, cfg, steps)
            candidates.append({"action": action, "cfg": cfg, "train": result, "loss": result["loss_after"], "model": candidate})
        candidates.append({"action": "keep", "cfg": base_cfg, "train": None, "loss": base_loss, "model": base_model})
        candidates.sort(key=lambda row: row["loss"])
        best = candidates[0]
        accepted = best["action"] != "keep" and best["loss"] + float(self.cfg["evolution"]["accept_margin"]) < base_loss
        trial_id = uuid.uuid4().hex[:12]
        self.storage.experiments.add(Trial(
            trial_id=trial_id,
            created_at=__import__("time").time(),
            base_generation=int(self.storage.load_state()["generation"]),
            action=best["action"] if accepted else "keep",
            config=best["cfg"] if accepted else base_cfg,
            score_before=base_loss,
            score_after=best["loss"],
            accepted=accepted,
            reason="candidate improved held-out validation beyond acceptance margin" if accepted else "no candidate met acceptance margin"
        ))
        return {
            "accepted": accepted,
            "trial_id": trial_id,
            "base_loss": base_loss,
            "best_loss": best["loss"],
            "action": best["action"] if accepted else "keep",
            "model": best["model"] if accepted else base_model,
            "model_cfg": best["cfg"] if accepted else base_cfg,
            "candidate_losses": [
                {"action": x["action"], "loss": x["loss"], "parameters": parameter_count(x["model"])} for x in candidates
            ]
        }
