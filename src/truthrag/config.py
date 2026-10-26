"""Load a truthrag.yaml. Relative paths in it resolve against the file's own directory."""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

DEFAULTS: dict[str, Any] = {
    "corpus": {"root": ".", "glob": "**/*.md", "exclude_dirs": [".git", ".truthrag", "node_modules"]},
    "truth": {
        "header": None,               # regex with one group, e.g. '<!--\s*CONTRACT:\s*(STATE|REFERENCE|LOG)\b'
        "header_classes": {},         # group value -> truth class
        "frontmatter_key": None,      # e.g. 'status' in YAML front matter
        "frontmatter_classes": {},    # value -> truth class, e.g. {superseded: archive}
        "archive_dirs": ["archive"],
        "log_current_section": None,  # heading regex marking a log's current section, e.g. '§\s*0\b'
        "default": "current",
        "retired_terms": None,        # optional table of retired wording (see docs)
        "negation_markers": ["~~", r"\bwas\b", r"\bnot\b", r"\bno longer\b", r"\bsuperseded\b", r"\breplaced\b",
                             r"\bformerly\b", r"\bretired\b", r"\binstead\b"],
    },
    "weights": {"current": 1.0, "log_current": 1.0, "reference": 0.9, "log": 0.5, "archive": 0.2,
                "retired_penalty": 0.5},
    "chunking": {"split_levels": [2, 3], "max_tokens": 400, "chars_per_token": "auto"},  # auto = measured
    "embedding": {"model": "BAAI/bge-small-en-v1.5", "batch_size": 64, "cache_dir": None},
    "index": {"dir": ".truthrag"},
    "retrieval": {"top_k": 8, "candidates": 40, "rrf_k": 60, "min_vector_sim": 0.6, "cross_encoder": None,
                  "rerank_candidates": 30},
    "llm": {"model": "claude-sonnet-5-5", "eval_model": "claude-haiku-5-5", "max_tokens": 16000,
            "effort": "medium"},
    "redact": None,
    "golden": None,
}


def _merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_config(path: str | Path) -> dict[str, Any]:
    path = Path(path).resolve()
    cfg = _merge(DEFAULTS, yaml.safe_load(path.read_text(encoding="utf-8")) or {})
    cfg["_dir"] = path.parent
    return cfg


def resolve(cfg: dict, rel: str | None) -> Path | None:
    """A config path, relative to the config file."""
    if rel is None:
        return None
    p = Path(rel).expanduser()
    return p if p.is_absolute() else cfg["_dir"] / p
