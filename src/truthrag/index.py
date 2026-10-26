"""Vector index (numpy, content-keyed embedding cache) + BM25 (rebuilt at load; small corpora need no pickle)."""
from __future__ import annotations

import hashlib
import re

import numpy as np

from .config import resolve
from .ingest import index_dir, load_chunks
from .models import Chunk

TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:[-_.][A-Za-z0-9]+)*|[㐀-鿿]")
BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def tokenize(text: str) -> list[str]:
    """Hyphenated tokens yield the whole token and its parts: `CT-O3` stays an exact ID, `full-scale` still
    matches "full scale"."""
    out = []
    for t in TOKEN_RE.findall(text):
        t = t.lower()
        out.append(t)
        if "-" in t:
            out.extend(p for p in t.split("-") if p)
    return out


class Embedder:
    def __init__(self, cfg: dict):
        from fastembed import TextEmbedding
        e = cfg["embedding"]
        self.model_name, self.batch_size = e["model"], e["batch_size"]
        cache = resolve(cfg, e["cache_dir"]) if e.get("cache_dir") else None
        self._model = TextEmbedding(self.model_name, cache_dir=str(cache) if cache else None)
        self._prefix = BGE_QUERY_PREFIX if "bge" in self.model_name.lower() else ""

    def _embed(self, texts: list[str]) -> np.ndarray:
        v = np.array(list(self._model.embed(texts, batch_size=self.batch_size)), dtype=np.float32)
        return v / np.linalg.norm(v, axis=1, keepdims=True).clip(min=1e-12)

    def passages(self, texts: list[str]) -> np.ndarray:
        return self._embed(texts)

    def query(self, text: str) -> np.ndarray:
        return self._embed([self._prefix + text])[0]


def build(cfg: dict) -> dict:
    out = index_dir(cfg)
    chunks = load_chunks(cfg)
    texts = [c.embed_text() for c in chunks]
    keys = [hashlib.sha1(t.encode("utf-8")).hexdigest() for t in texts]
    emb = Embedder(cfg)
    cache: dict[str, np.ndarray] = {}
    cache_file = out / "embed_cache.npz"
    if cache_file.exists():
        z = np.load(cache_file)
        if str(z["model"]) == emb.model_name:
            cache = dict(zip(z["keys"].tolist(), z["vectors"]))
    todo = [i for i, k in enumerate(keys) if k not in cache]
    for i, v in zip(todo, emb.passages([texts[i] for i in todo]) if todo else []):
        cache[keys[i]] = v
    vecs = np.stack([cache[k] for k in keys]).astype(np.float32)
    np.save(out / "vectors.npy", vecs)
    np.savez(cache_file, model=emb.model_name, keys=np.array(keys), vectors=vecs)
    (out / "keys.txt").write_text("\n".join(keys), encoding="utf-8")
    return {"chunks": len(chunks), "embedded": len(todo), "reused": len(chunks) - len(todo)}


class Index:
    def __init__(self, cfg: dict):
        from rank_bm25 import BM25Okapi
        out = index_dir(cfg)
        self.cfg = cfg
        self.chunks: list[Chunk] = load_chunks(cfg)
        keys = [hashlib.sha1(c.embed_text().encode("utf-8")).hexdigest() for c in self.chunks]
        if keys != (out / "keys.txt").read_text(encoding="utf-8").split("\n"):
            raise SystemExit("index is stale: run `truthrag index` after `truthrag ingest`")
        self.vectors = np.load(out / "vectors.npy")
        self.embedder = Embedder(cfg)
        self.bm25 = BM25Okapi([tokenize(c.embed_text()) for c in self.chunks])

    def vector_search(self, query: str, k: int) -> list[tuple[int, float]]:
        sims = self.vectors @ self.embedder.query(query)
        return [(int(i), float(sims[i])) for i in np.argsort(-sims)[:k]]

    def bm25_search(self, query: str, k: int) -> list[tuple[int, float]]:
        scores = self.bm25.get_scores(tokenize(query))
        return [(int(i), float(scores[i])) for i in np.argsort(-scores)[:k] if scores[i] > 0]
