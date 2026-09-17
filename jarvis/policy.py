from __future__ import annotations
import json
import random


class IntrinsicPolicy:
    """Learns which bounded development actions have recently produced progress.

    The policy has no external reward model; it uses validation-loss improvement as
    the scalar research signal and keeps all actions inside explicit safety bounds.
    """
    def __init__(self, storage, seed=1701):
        self.storage = storage
        self.rng = random.Random(seed)
        self.actions = ["train", "evolve", "web", "benchmark"]
        self.path = storage.workspace / "intrinsic_policy.json"
        if not self.path.exists():
            self.save({a: 1.0 for a in self.actions})

    def load(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data):
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def choose(self):
        w = self.load()
        active = [(a, max(0.05, float(w.get(a, 1.0)))) for a in self.actions]
        return self.rng.choices([a for a, _ in active], weights=[v for _, v in active], k=1)[0]

    def update(self, action: str, improved: bool):
        w = self.load()
        current = float(w.get(action, 1.0))
        w[action] = min(8.0, current * (1.12 if improved else 0.94))
        for other in self.actions:
            if other != action:
                w[other] = min(8.0, max(0.05, float(w.get(other, 1.0)) * (1.003 if improved else 1.0)))
        self.save(w)
