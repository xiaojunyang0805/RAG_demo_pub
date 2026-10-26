"""Evaluation against a golden set (fields: see the header of examples/halyard/golden.yaml).

Retrieval metrics need no API key: hit@5, MRR and stale-truth ranking for every mode (the ablation).
Answer metrics call Claude: correctness, citation faithfulness, stale-truth in the answer, refusal, leaks.
Relevance is marked by text pattern, not file path, so the set survives re-chunking. Patterns are matched against
what retrieval sees: the path, the heading trail and the chunk text.
"""
from __future__ import annotations

import json
import re

import yaml

from .config import resolve
from .models import ARCHIVE, LOG, REFERENCE
from .retired import negation_re, states

CURRENT_CLASSES = {"current", "log_current", REFERENCE}
ABLATION = [("BM25", "bm25", False), ("vector", "vector", False), ("hybrid", "hybrid", False),
            ("hybrid + truth", "hybrid+truth", False), ("hybrid + truth + rerank", "hybrid+truth", True)]


def load_golden(cfg: dict) -> list[dict]:
    qs = yaml.safe_load(resolve(cfg, cfg["golden"]).read_text(encoding="utf-8"))["questions"]
    for q in qs:
        for key in ("evidence", "stale", "absent"):
            if q.get(key):
                q[f"_{key}"] = re.compile(q[key])
        q["_must"] = [re.compile(p) for p in q.get("must", [])]
        q["_all"] = [re.compile(p) for p in q.get("evidence_all", [])]
    return qs


def check_golden(qs: list[dict], chunks, cfg: dict) -> list[tuple[str, str, str]]:
    """(id, FAIL|WARN, message): is every question still valid for the corpus as ingested?"""
    neg = negation_re(cfg["truth"]["negation_markers"])
    cur = [c for c in chunks if c.truth in CURRENT_CLASSES]
    out = []
    for q in qs:
        if q.get("_absent"):
            n = sum(bool(q["_absent"].search(c.embed_text())) for c in chunks)
            if n:
                out.append((q["id"], "FAIL", f"refusal question is answerable: `absent` matches {n} chunks"))
            continue
        pool = chunks if q.get("evidence_truth") == "any" else cur
        if q.get("_evidence") and not any(q["_evidence"].search(c.embed_text()) for c in pool):
            out.append((q["id"], "FAIL", "no chunk matches `evidence`"))
        for p in q["_all"]:
            if not any(p.search(c.embed_text()) for c in chunks):
                out.append((q["id"], "FAIL", f"no chunk matches `{p.pattern}`"))
        if q.get("_stale") and q.get("_evidence"):
            for c in cur:
                if c.truth != REFERENCE and states(q["_stale"], c.text, neg) and not q["_evidence"].search(c.embed_text()):
                    out.append((q["id"], "WARN", f"current doc states the superseded value: {c.citation[:80]}"))
    return out


def _relevant(q: dict, chunk) -> bool:
    return bool(q.get("_evidence") and q["_evidence"].search(chunk.embed_text())
                and (q.get("evidence_truth") == "any" or chunk.truth in CURRENT_CLASSES))


def score_retrieval(q: dict, hits, neg) -> dict:
    r: dict = {}
    if q.get("_all"):
        ranks = [next((n for n, h in enumerate(hits, 1) if p.search(h.chunk.embed_text())), None) for p in q["_all"]]
        worst = None if None in ranks else max(ranks)
        r.update(rank=worst, hit5=worst is not None and worst <= 5)
    elif q.get("_evidence"):
        rank = next((n for n, h in enumerate(hits, 1) if _relevant(q, h.chunk)), None)
        r.update(rank=rank, hit5=rank is not None and rank <= 5)
    if q.get("_stale") and q.get("_evidence"):
        first = next((h.chunk for h in hits[:5] if q["_evidence"].search(h.chunk.embed_text())
                      or states(q["_stale"], h.chunk.text, neg)), None)
        r["stale_ret"] = bool(first and q["_evidence"].search(first.embed_text()))
    r["top1_truth"] = hits[0].chunk.truth if hits else None
    return r


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def aggregate(rows: list[dict]) -> dict:
    ranked = [r for r in rows if "hit5" in r]
    agg = {"n": len(ranked),
           "hit5": _mean([float(r["hit5"]) for r in ranked]),
           "mrr": _mean([1.0 / r["rank"] if r["rank"] else 0.0 for r in ranked]),
           "stale_ret": _mean([float(r["stale_ret"]) for r in rows if "stale_ret" in r]),
           "top1_history": _mean([float(r["top1_truth"] in (LOG, ARCHIVE)) for r in ranked])}
    answered = [r for r in rows if "correct" in r]
    if answered or any("refusal_ok" in r for r in rows):
        agg.update(
            correct=_mean([float(r["correct"]) for r in answered]),
            faithful=_mean([float(r["faithful"]) for r in answered if not r["refused"]]),
            stale_ans=_mean([float(r["stale_ans"]) for r in rows if "stale_ans" in r]),
            refusal=_mean([float(r["refusal_ok"]) for r in rows if "refusal_ok" in r]),
            leaks=sum(r.get("leaks", 0) for r in rows))
    return agg


def run_retrieval(index, qs: list[dict], cfg: dict, mode: str, rerank: bool) -> list[dict]:
    from .retrieve import retrieve
    neg = negation_re(cfg["truth"]["negation_markers"])
    return [{"id": q["id"], **score_retrieval(q, retrieve(index, q["question"], cfg, mode, 10, rerank), neg)}
            for q in qs if q["category"] not in ("refusal", "redaction")]


def ablation(index, qs: list[dict], cfg: dict, with_rerank: bool) -> list[dict]:
    rows = []
    for label, mode, rr in ABLATION:
        if rr and not with_rerank:
            continue
        rows.append({"mode": label, **aggregate(run_retrieval(index, qs, cfg, mode, rr))})
    return rows


def run_answers(index, qs: list[dict], cfg: dict, model: str | None) -> list[dict]:
    from .answer import answer
    from .guard import check
    from .redact import load_redactors
    from .retrieve import retrieve
    neg = negation_re(cfg["truth"]["negation_markers"])
    ingest_r, _ = load_redactors(resolve(cfg, cfg.get("redact")))
    rows = []
    for q in qs:
        hits = retrieve(index, q["question"], cfg, "hybrid+truth", 10)
        row = {"id": q["id"], "category": q["category"]}
        if q["category"] not in ("refusal", "redaction"):
            row.update(score_retrieval(q, hits, neg))
        ans = check(answer(q["question"], hits[: cfg["retrieval"]["top_k"]], cfg, model), ingest_r)
        row.update(refused=ans.refused, leaks=sum(i.startswith("leak:") for i in ans.guard_issues), answer=ans.text)
        if q["category"] == "refusal":
            row["refusal_ok"] = ans.refused
        elif q["category"] != "redaction":
            row["correct"] = not ans.refused and all(p.search(ans.text) for p in q["_must"])
            cited = [ans.hits[n - 1].chunk for n in ans.citations if 1 <= n <= len(ans.hits)]
            pats = [q["_evidence"]] if q.get("_evidence") else q["_all"] or q["_must"]
            row["faithful"] = not any(i.startswith("citation") for i in ans.guard_issues) and \
                any(p.search(c.embed_text()) for c in cited for p in pats)
            if q.get("_stale"):
                row["stale_ans"] = row["correct"] and not states(q["_stale"], ans.text, neg)
        rows.append(row)
        print(f"  {q['id']:<4} {json.dumps({k: row[k] for k in row if k in ('correct', 'refusal_ok', 'leaks')})}")
    return rows


def markdown_table(rows: list[dict]) -> str:
    f = lambda x: "–" if x is None else f"{x:.2f}"
    out = ["| Retrieval | hit@5 | MRR | stale-truth | top-1 is history |", "|---|---|---|---|---|"]
    out += [f"| {r['mode']} | {f(r['hit5'])} | {f(r['mrr'])} | {f(r['stale_ret'])} | {f(r['top1_history'])} |"
            for r in rows]
    return "\n".join(out)
