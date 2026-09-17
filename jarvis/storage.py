from __future__ import annotations
import json
from pathlib import Path
import os
import shutil
import tempfile
import torch

from .data import Corpus
from .memory import Memory
from .model import make_model
from .events import EventLog


class Storage:
    def __init__(self, cfg: dict):
        p = cfg["paths"]
        root = Path(os.environ.get("JARVIS_ROOT", ".")).expanduser().resolve()
        self.root = root
        self.data = self._resolve_path(root, p["data"])
        self.checkpoints = self._resolve_path(root, p["checkpoints"])
        self.generations = self._resolve_path(root, p["generations"])
        self.workspace = self._resolve_path(root, p["workspace"])
        self.sandbox = self._resolve_path(root, p["sandbox"])
        self.state_path = self.workspace / "state.json"
        self.policy_path = self.workspace / "policy.json"
        self.corpus = Corpus(self.data, cfg["training"]["block_size"])
        self.memory = Memory(self.data / "memory.jsonl")
        self.events = EventLog(self.workspace / "events.jsonl")

    @staticmethod
    def _resolve_path(root: Path, value: str | Path) -> Path:
        candidate = Path(value).expanduser()
        return candidate if candidate.is_absolute() else root / candidate

    def ensure(self):
        for p in [self.data, self.checkpoints, self.generations, self.workspace, self.sandbox]:
            p.mkdir(parents=True, exist_ok=True)
        if not self.state_path.exists():
            self.save_state({
                "generation": 0,
                "training_steps": 0,
                "accepted_changes": 0,
                "best_eval_loss": None,
                "profile": "local",
                "architecture": None,
                "parameters": 0,
                "lineage": [],
                "web_pages": 0,
                "last_web_cycle": None,
                "last_error": None,
                "runtime": {"running": False, "operation": None, "step": 0, "total": 0, "loss": None}
            })
        if not self.policy_path.exists():
            self.policy_path.write_text(json.dumps({
                "train": True,
                "ingest": True,
                "evolve": True,
                "checkpoint": True,
                "reasoning_depth": 2,
                "web_learning": True,
                "max_web_pages_per_cycle": 6,
                "allow_cross_host": False
            }, indent=2), encoding="utf-8")

    def save_state(self, state: dict):
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.state_path)

    def load_state(self):
        self.ensure()
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def load_policy(self):
        self.ensure()
        return json.loads(self.policy_path.read_text(encoding="utf-8"))

    def save_policy(self, policy: dict):
        tmp = self.policy_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(policy, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.policy_path)

    def latest_checkpoint(self):
        points = sorted(self.checkpoints.glob("generation_*.pt"))
        return points[-1] if points else None

    def save_checkpoint(self, generation: int, model, cfg: dict, optimizer=None, metrics=None):
        payload = {
            "model": model.state_dict(),
            "model_cfg": cfg,
            "generation": int(generation),
            "metrics": metrics or {}
        }
        if optimizer is not None:
            payload["optimizer"] = optimizer.state_dict()
        path = self.checkpoints / f"generation_{generation:06d}.pt"
        # Atomic-ish checkpoint write: finish the file before exposing it as latest.
        fd, tmp_name = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=str(self.checkpoints))
        Path(tmp_name).unlink(missing_ok=True)
        tmp_path = Path(tmp_name)
        try:
            torch.save(payload, tmp_path)
            tmp_path.replace(path)
        finally:
            tmp_path.unlink(missing_ok=True)
        self._write_manifest(path, payload)
        return path

    @staticmethod
    def _manifest_safe(value):
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, dict):
            return {str(k): Storage._manifest_safe(v) for k, v in value.items() if k != "model"}
        if isinstance(value, (list, tuple)):
            return [Storage._manifest_safe(v) for v in value]
        return str(value)

    def _write_manifest(self, path, payload):
        manifest = {
            "checkpoint": path.name,
            "generation": payload.get("generation"),
            "model_cfg": self._manifest_safe(payload.get("model_cfg", {})),
            "metrics": self._manifest_safe(payload.get("metrics", {}))
        }
        tmp = self.checkpoints / "LATEST.json.tmp"
        tmp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.checkpoints / "LATEST.json")

    def load_model(self):
        self.ensure()
        state = self.load_state()
        cfg = state.get("architecture") or self.cfg_local()
        ckpt = self.latest_checkpoint()
        if ckpt is None:
            return make_model(cfg), cfg
        # weights_only=True avoids arbitrary code execution via pickle if a
        # checkpoint/bundle ever comes from an untrusted source (a shared
        # bundle, a forked repo's CI artifact, etc.). Everything this project
        # stores (tensors, dicts, ints, strings) is safe under this mode.
        payload = torch.load(ckpt, map_location="cpu", weights_only=True)
        model_cfg = payload.get("model_cfg", cfg)
        model = make_model(model_cfg)
        model.load_state_dict(payload["model"], strict=False)
        return model, model_cfg

    def make_bundle(self, destination: str | Path | None = None):
        import shutil
        target = Path(destination) if destination else (self.workspace / "jarvis_state_bundle")
        target.parent.mkdir(parents=True, exist_ok=True)
        for old in target.parent.glob(target.name + ".zip"):
            old.unlink(missing_ok=True)
        archive_base = str(target)
        temp_dir = Path(tempfile.mkdtemp(prefix="jarvis_bundle_"))
        try:
            root = temp_dir / "JARVIS_STATE"
            for src in [self.data, self.checkpoints, self.generations, self.workspace]:
                if src.exists():
                    shutil.copytree(src, root / src.name, dirs_exist_ok=True)
            return Path(shutil.make_archive(archive_base, "zip", temp_dir, root.name))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def cfg_local(self):
        raise RuntimeError("Storage.cfg_local is populated by System")
