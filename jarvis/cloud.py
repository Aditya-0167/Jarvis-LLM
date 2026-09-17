from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path


def make_manifest(root="."):
    root = Path(root)
    rows = []
    for p in sorted((root / "checkpoints").glob("generation_*.pt")):
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        rows.append({"file": str(p), "bytes": p.stat().st_size, "sha256": h})
    manifest = {"created": time.time(), "checkpoints": rows}
    out = root / "workspace" / "checkpoint_manifest.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
