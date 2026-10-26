"""truthrag command line:  ingest | index | search | ask | eval"""
from __future__ import annotations

import argparse
import json
import sys

from .config import load_config, resolve


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(prog="truthrag")
    p.add_argument("-c", "--config", default="truthrag.yaml", help="path to truthrag.yaml")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ingest", help="read the corpus, classify truth, redact, chunk")
    sub.add_parser("index", help="embed chunks (cached) and build the indexes")
    for name in ("search", "ask"):
        sp = sub.add_parser(name, help="retrieval only" if name == "search" else "answer with citations (Claude)")
        sp.add_argument("question")
        sp.add_argument("--mode", default="hybrid+truth")
        sp.add_argument("-k", type=int, default=None)
        if name == "ask":
            sp.add_argument("--model", default=None)
            sp.add_argument("--public", action="store_true", help="also apply public redaction")
    pe = sub.add_parser("eval", help="score against the golden set")
    pe.add_argument("--answers", action="store_true", help="also score answers (calls Claude)")
    pe.add_argument("--rerank", action="store_true", help="include the cross-encoder row in the ablation")
    pe.add_argument("--check", action="store_true", help="only validate the golden set against the corpus")
    pe.add_argument("--json", default=None, help="write the ablation rows to this JSON file")
    args = p.parse_args(argv)
    cfg = load_config(args.config)

    if args.cmd == "ingest":
        from .ingest import ingest
        print(json.dumps(ingest(cfg), indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "index":
        from .index import build
        print(json.dumps(build(cfg), indent=2))
        return 0

    from .index import Index
    index = Index(cfg)
    if args.cmd == "search":
        from .retrieve import in_corpus, retrieve
        hits = retrieve(index, args.question, cfg, args.mode, args.k)
        print(f"in corpus: {in_corpus(hits, args.question, cfg)}")
        for n, h in enumerate(hits, 1):
            print(f"[{n}] {h.score:.4f}  w={h.weight:.2f}  {h.chunk.truth:<11} {h.chunk.citation[:100]}")
    elif args.cmd == "ask":
        from .answer import answer, render
        from .guard import check
        from .redact import load_redactors
        from .retrieve import retrieve
        ingest_r, public_r = load_redactors(resolve(cfg, cfg.get("redact")))
        hits = retrieve(index, args.question, cfg, args.mode, args.k)
        try:
            ans = answer(args.question, hits, cfg, args.model)
        except TypeError as e:  # the SDK raises this when no credential is configured
            if "authentication" not in str(e).lower():
                raise
            print("No Anthropic credentials found: set ANTHROPIC_API_KEY (or run `ant auth login`). "
                  "`truthrag search` works without them.", file=sys.stderr)
            return 2
        print(render(check(ans, ingest_r, public_r if args.public else None)))
    elif args.cmd == "eval":
        from . import evaluate as ev
        qs = ev.load_golden(cfg)
        problems = ev.check_golden(qs, index.chunks, cfg)
        for qid, level, msg in problems:
            print(f"{level} {qid}: {msg}")
        if args.check:
            return 1 if any(lvl == "FAIL" for _, lvl, _ in problems) else 0
        rows = ev.ablation(index, qs, cfg, args.rerank)
        print(ev.markdown_table(rows))
        if args.json:
            with open(args.json, "w", encoding="utf-8") as f:
                json.dump(rows, f, indent=2)
        if args.answers:
            print(json.dumps(ev.aggregate(ev.run_answers(index, qs, cfg, cfg["llm"]["eval_model"])), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
