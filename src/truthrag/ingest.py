"""Corpus → redacted, truth-tagged chunks (.truthrag/chunks.jsonl). Redaction runs on path and text first."""
from __future__ import annotations

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
    max_chars = ch["max_tokens"] * ch["chars_per_token"]

    chunks: list[Chunk] = []
    docs: Counter = Counter()
    for p in sorted(root.glob(cfg["corpus"]["glob"])):
        parts = p.relative_to(root).parts
        if exclude & set(parts[:-1]):
            continue
        doc = classifier.classify_doc(parts, p.read_text(encoding="utf-8", errors="replace"))
        docs[doc.truth] += 1
        path = redactor("/".join(parts))
        is_terms_file = retired_path is not None and p.resolve() == retired_path.resolve()
        for heading_path, lines in sections(redactor(doc.body), set(ch["split_levels"])):
            truth = classifier.classify_section(doc.truth, heading_path)
            for text in pack(lines, max_chars):
                chunks.append(Chunk(
                    id=f"{path}#{len(chunks)}", path=path, heading_path=heading_path, text=text, truth=truth,
                    retired_by=[] if is_terms_file else asserted_retired(text, terms, negation),
                    tokens=len(text) // ch["chars_per_token"]))

    out = index_dir(cfg)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "chunks.jsonl", "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c.to_json(), ensure_ascii=False) + "\n")
    return {"docs": sum(docs.values()), "docs_by_truth": dict(docs), "chunks": len(chunks),
            "chunks_by_truth": dict(Counter(c.truth for c in chunks)),
            "chunks_stating_retired_wording": sum(bool(c.retired_by) for c in chunks),
            "retired_terms": len(terms), "redactions": dict(redactor.counts)}


def load_chunks(cfg: dict) -> list[Chunk]:
    with open(index_dir(cfg) / "chunks.jsonl", encoding="utf-8") as f:
        return [Chunk(**json.loads(line)) for line in f]
