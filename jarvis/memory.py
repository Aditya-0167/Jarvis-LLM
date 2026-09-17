from __future__ import annotations
import json
import math
import re
import time
from collections import Counter
from pathlib import Path

TOKEN_RE = re.compile(r"[A-Za-z0-9_]{2,}")


class Memory:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def add(self, kind: str, payload: dict):
        record = {"time": time.time(), "kind": kind, **payload}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def recent(self, limit: int = 20):
        lines = self.path.read_text(encoding="utf-8", errors="ignore").splitlines()
        return [json.loads(x) for x in lines[-limit:] if x.strip()]

    def search(self, query: str, limit: int = 5):
        q = Counter(TOKEN_RE.findall(query.lower()))
        rows = []
        for line in self.path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            text = json.dumps(row, ensure_ascii=False).lower()
            tokens = Counter(TOKEN_RE.findall(text))
            score = 0.0
            for token, count in q.items():
                score += min(count, tokens.get(token, 0)) * math.log1p(tokens.get(token, 0))
            if score > 0:
                rows.append((score, row))
        rows.sort(key=lambda x: x[0], reverse=True)
        return [x[1] for x in rows[:limit]]
