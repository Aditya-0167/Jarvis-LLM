from __future__ import annotations
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Trial:
    trial_id: str
    created_at: float
    base_generation: int
    action: str
    config: dict
    score_before: float | None = None
    score_after: float | None = None
    accepted: bool = False
    reason: str = ""


class ExperimentRegistry:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def add(self, trial: Trial):
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(trial), ensure_ascii=False) + "\n")

    def recent(self, limit: int = 20):
        lines = self.path.read_text(encoding="utf-8", errors="ignore").splitlines()
        return [json.loads(x) for x in lines[-int(limit):] if x.strip()]


def choose_next_actions(state: dict, last_result: dict | None, web_enabled: bool):
    actions = ["train", "evaluate"]
    if last_result and last_result.get("accepted"):
        actions.append("continue_with_new_architecture")
    else:
        actions.append("try_alternative_architecture")
    if web_enabled:
        actions.append("refresh_public_web_corpus")
    actions.append("checkpoint")
    return actions
