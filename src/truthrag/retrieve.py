"""Hybrid retrieval with truth weighting.

    final = RRF(bm25 rank, vector rank [, cross-encoder rank]) × weight[truth] × (retired_penalty if stale wording)

RRF is rank-only, so refusal uses absolute signals instead (best cosine, or an exact ID from the query).
`mode` exists for the ablation: bm25 | vector | hybrid | hybrid+truth.
"""
from __future__ import annotations

import math
import re

from .config import resolve
from .models import Chunk, Hit

MODES = ("bm25", "vector", "hybrid", "hybrid+truth")
ID_RE = re.compile(r"(?<![\w-])(?:[A-Z]{1,3}-O\d+|[A-Z]{1,3}-\d{1,3}|[A-Z]\d{1,3}|[A-Z0-9]{2,}-[A-Z0-9]{2,})(?![\w-])")


def weight(chunk: Chunk, cfg: dict) -> float:
    w = cfg["weights"][chunk.truth]
    return w * cfg["weights"]["retired_penalty"] if chunk.retired_by else w


def rrf(ranks: list[int | None], k: int) -> float:
    return sum(1.0 / (k + r) for r in ranks if r is not None)


_CROSS: dict = {}


def _cross_scores(query: str, hits: list[Hit], cfg: dict) -> list[float]:
    from fastembed.rerank.cross_encoder import TextCrossEncoder
    name = cfg["retrieval"]["cross_encoder"]
    if name not in _CROSS:
        cache = cfg["embedding"].get("cache_dir")
        _CROSS[name] = TextCrossEncoder(name, cache_dir=str(resolve(cfg, cache)) if cache else None)
    return [1 / (1 + math.exp(-s)) for s in _CROSS[name].rerank(query, [h.chunk.embed_text() for h in hits])]


def retrieve(index, query: str, cfg: dict, mode: str = "hybrid+truth", top_k: int | None = None,
             rerank: bool | None = None) -> list[Hit]:
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    r = cfg["retrieval"]
    hits: dict[int, Hit] = {}
    if mode != "vector":
        for rank, (i, _) in enumerate(index.bm25_search(query, r["candidates"]), 1):
            hits.setdefault(i, Hit(index.chunks[i])).bm25_rank = rank
    if mode != "bm25":
        for rank, (i, sim) in enumerate(index.vector_search(query, r["candidates"]), 1):
            h = hits.setdefault(i, Hit(index.chunks[i]))
            h.vector_rank, h.vector_sim = rank, sim
    use_truth = mode == "hybrid+truth"
    for h in hits.values():
        h.fused = rrf([h.bm25_rank, h.vector_rank], r["rrf_k"])
        h.weight = weight(h.chunk, cfg) if use_truth else 1.0
        h.score = h.fused * h.weight
    ranked = sorted(hits.values(), key=lambda h: -h.fused)
    if (r.get("cross_encoder") if rerank is None else rerank) and mode.startswith("hybrid"):
        ranked = ranked[: r["rerank_candidates"]]
        order = sorted(zip(_cross_scores(query, ranked, cfg), ranked), key=lambda p: -p[0])
        for rank, (_, h) in enumerate(order, 1):
            h.fused = rrf([h.bm25_rank, h.vector_rank, rank], r["rrf_k"])
            h.score = h.fused * h.weight
    return sorted(ranked, key=lambda h: -h.score)[: top_k or r["top_k"]]


def in_corpus(hits: list[Hit], query: str, cfg: dict) -> bool:
    """False -> answer "not in the corpus" without calling the LLM."""
    if not hits:
        return False
    ids = set(ID_RE.findall(query))
    if ids and any(any(i in h.chunk.text for i in ids) for h in hits):
        return True
    return max(h.vector_sim or 0.0 for h in hits) >= cfg["retrieval"]["min_vector_sim"]
