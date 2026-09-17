from __future__ import annotations
import json
from pathlib import Path


def load_config(path: str = "config.json"):
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8"))
