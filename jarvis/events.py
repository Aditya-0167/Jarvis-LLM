from __future__ import annotations
import json
import time
from pathlib import Path

class EventLog:
    """Append-only runtime events used by the live Studio UI and post-run analysis."""
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def emit(self, kind: str, payload: dict | None = None):
        row = {"time": time.time(), "kind": kind, **(payload or {})}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
        return row

    def recent(self, limit: int = 80):
        lines = self.path.read_text(encoding="utf-8", errors="ignore").splitlines()
        out = []
        for line in lines[-limit:]:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return out
