"""Corpus → redacted, truth-tagged chunks (.truthrag/chunks.jsonl). Redaction runs on path and text first.

Chunk size is measured, not guessed: the embedder's own tokenizer gives this corpus's characters per token, and
chunks are sized to fit the model's window (an embedder silently drops what it cannot read). The report says how
many chunks still exceed it.
"""
from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path

from .chunker import pack, sections
from .config import resolve
from .models import Chunk
from .redact import load_redactors
from .retired import asserted_retired, load_retired_terms, negation_re
from .truth import TruthClassifier


def index_dir(cfg: dict) -> Path:
    return resolve(cfg, cfg["index"]["dir"])


def embedder_tokenizer(cfg: dict):
    """(untruncated tokenizer copy, model window) for the configured embedder, or (None, None)."""
    try:
        from fastembed import TextEmbedding
        cache = cfg["embedding"].get("cache_dir")
        tk = TextEmbedding(cfg["embedding"]["model"], cache_dir=str(resolve(cfg, cache)) if cache else None).model.tokenizer
    except Exception:  # no model available: fall back to the configured chars_per_token
        return None, None
    window = (tk.truncation or {}).get("max_length")
    counter = copy.deepcopy(tk)
    counter.no_truncation()
    counter.no_padding()
    return counter, window


def ingest(cfg: dict) -> dict:
    root = resolve(cfg, cfg["corpus"]["root"])
    exclude = set(cfg["corpus"]["exclude_dirs"])
    redactor, public = load_redactors(resolve(cfg, cfg.get("redact")))
    classifier = TruthClassifier(cfg["truth"])
    retired_path = resolve(cfg, cfg["truth"].get("retired_terms")) if cfg["truth"].get("retired_terms") else None
    if retired_path and not retired_path.is_absolute():
        retired_path = root / retired_path
    terms = load_retired_terms(retired_path)
    negation = negation_re(cfg["truth"]["negation_markers"], public.names)
    ch = cfg["chunking"]

    docs = []
    for p in sorted(root.glob(cfg["corpus"]["glob"])):
        parts = p.relative_to(root).parts
        if exclude & set(parts[:-1]):
            continue
        doc = classifier.classify_doc(parts, p.read_text(encoding="utf-8", errors="replace"))
        docs.append((p, redactor("/".join(parts)), doc.truth, redactor(doc.body)))

    tokenizer, window = embedder_tokenizer(cfg) if ch.get("chars_per_token") == "auto" else (None, None)
    if tokenizer:
        sample = "\n".join(body for *_, body in docs)[:400_000]
        cpt = len(sample) / max(1, len(tokenizer.encode(sample).ids))
    else:
        cpt = float(ch["chars_per_token"]) if ch.get("chars_per_token") != "auto" else 2.5
    max_chars = int(ch["max_tokens"] * cpt)

    chunks: list[Chunk] = []
    for p, path, doc_truth, body in docs:
        is_terms_file = retired_path is not None and p.resolve() == retired_path.resolve()
        for heading_path, lines in sections(body, set(ch["split_levels"])):
            truth = classifier.classify_section(doc_truth, heading_path)
            for text in pack(lines, max_chars):
                chunks.append(Chunk(
                    id=f"{path}#{len(chunks)}", path=path, heading_path=heading_path, text=text, truth=truth,
                    retired_by=[] if is_terms_file else asserted_retired(text, terms, negation),
                    tokens=len(tokenizer.encode(text).ids) if tokenizer else int(len(text) / cpt)))

    out = index_dir(cfg)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "chunks.jsonl", "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c.to_json(), ensure_ascii=False) + "\n")
    report = {"docs": len(docs), "docs_by_truth": dict(Counter(t for _, _, t, _ in docs)), "chunks": len(chunks),
              "chunks_by_truth": dict(Counter(c.truth for c in chunks)),
              "chunks_stating_retired_wording": sum(bool(c.retired_by) for c in chunks),
              "retired_terms": len(terms), "redactions": dict(redactor.counts),
              "chars_per_token": round(cpt, 2), "max_chunk_chars": max_chars}
    if tokenizer and window:
        over = sum(len(tokenizer.encode(c.embed_text()).ids) > window for c in chunks)
        report.update(embedder_window=window, chunks_over_window=over)
    return report


def load_chunks(cfg: dict) -> list[Chunk]:
    with open(index_dir(cfg) / "chunks.jsonl", encoding="utf-8") as f:
        return [Chunk(**json.loads(line)) for line in f]
