from __future__ import annotations
import math
import re
from collections import Counter, defaultdict

TOKEN_RE = re.compile(r"[A-Za-z0-9_]{2,}")


class LexicalRetriever:
    """Dependency-free BM25-style retrieval over the local corpus."""
    def __init__(self, corpus, chunk_chars: int = 1800):
        self.corpus = corpus
        self.chunk_chars = int(chunk_chars)
        self._chunks = None
        self._df = None
        self._avgdl = 1.0

    def _build(self):
        text = self.corpus.text()
        chunks = []
        for start in range(0, len(text), self.chunk_chars):
            piece = text[start:start + self.chunk_chars].strip()
            if piece:
                chunks.append(piece)
        df = defaultdict(int)
        total = 0
        for piece in chunks:
            toks = set(TOKEN_RE.findall(piece.lower()))
            for tok in toks:
                df[tok] += 1
            total += len(TOKEN_RE.findall(piece.lower()))
        self._chunks = chunks or [text]
        self._df = dict(df)
        self._avgdl = max(1.0, total / max(1, len(self._chunks)))

    def search(self, query: str, limit: int = 6):
        if self._chunks is None:
            self._build()
        q = TOKEN_RE.findall(query.lower())
        if not q:
            return []
        n = len(self._chunks)
        scored = []
        for i, piece in enumerate(self._chunks):
            toks = TOKEN_RE.findall(piece.lower())
            tf = Counter(toks)
            dl = len(toks)
            score = 0.0
            for term in q:
                f = tf.get(term, 0)
                if not f:
                    continue
                df = self._df.get(term, 0)
                idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
                denom = f + 1.5 * (0.25 + 0.75 * dl / self._avgdl)
                score += idf * (f * 2.5) / denom
            if score:
                scored.append((score, i, piece))
        scored.sort(reverse=True)
        return [{"score": round(s, 4), "chunk_id": i, "text": p} for s, i, p in scored[:int(limit)]]

    def invalidate(self):
        self._chunks = None
        self._df = None
