from __future__ import annotations
import hashlib
import json
import random
from pathlib import Path
import torch


class Corpus:
    def __init__(self, data_dir: str | Path, block_size: int):
        self.root = Path(data_dir)
        self.root.mkdir(parents=True, exist_ok=True)
        self.sources = self.root / "sources.jsonl"
        self.text_file = self.root / "corpus.txt"
        self.block_size = int(block_size)
        if not self.text_file.exists():
            self.text_file.write_text(self.default_seed(), encoding="utf-8")

    @staticmethod
    def default_seed() -> str:
        return (
            "JARVIS research seed.\n"
            "This system starts from random neural weights and learns from permitted public or user-provided text.\n"
            "Every change is logged as an experiment.\n"
            "Knowledge is treated as evidence with provenance rather than as a command.\n"
        )

    def add(self, text: str, source: str, kind: str = "public"):
        text = text.strip()
        if not text:
            return {"added": 0}
        digest = hashlib.sha256((source + "\n" + text[:10000]).encode("utf-8", errors="ignore")).hexdigest()
        # De-duplicate exact source/content fingerprints.
        if self.sources.exists() and any(digest in line for line in self.sources.read_text(encoding="utf-8", errors="ignore").splitlines()[-5000:]):
            return {"added": 0, "duplicate": True, "id": digest, "source": source}
        record = {"id": digest, "source": source, "kind": kind, "chars": len(text)}
        with self.sources.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        with self.text_file.open("a", encoding="utf-8") as f:
            f.write(f"\n\n===== {kind.upper()}: {source} =====\n{text}\n")
        return {**record, "added": len(text)}

    def text(self) -> str:
        return self.text_file.read_text(encoding="utf-8", errors="ignore")

    def bytes(self):
        raw = self.text().encode("utf-8", errors="replace")
        minimum = self.block_size + 4
        if len(raw) < minimum:
            raw += b" " * (minimum - len(raw))
        return torch.tensor(list(raw), dtype=torch.long)

    def batch(self, batch_size: int, holdout: str = "train"):
        data = self.bytes()
        n = len(data)
        train_end = max(self.block_size + 2, int(n * 0.80))
        val_end = max(train_end + self.block_size + 2, int(n * 0.90))
        if holdout == "train":
            source = data[:train_end]
        elif holdout == "val":
            source = data[train_end:val_end]
        else:
            source = data[val_end:]
        if len(source) < self.block_size + 2:
            source = data
        max_start = len(source) - self.block_size - 1
        starts = torch.randint(0, max_start + 1, (int(batch_size),))
        xs = [source[int(i):int(i) + self.block_size] for i in starts]
        ys = [source[int(i) + 1:int(i) + self.block_size + 1] for i in starts]
        return torch.stack(xs), torch.stack(ys)


class Curriculum:
    """Synthetic self-supervision: no external model or labels."""
    def __init__(self, seed: int = 1701):
        self.rng = random.Random(seed)

    def sample(self, batch_size: int, length: int = 32):
        rows = []
        for _ in range(batch_size):
            raw = [self.rng.randrange(32, 127) for _ in range(length)]
            rows.append(b"<COPY>" + bytes(raw) + b"</COPY>")
        return rows
