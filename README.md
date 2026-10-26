# Truth-aware RAG

**Retrieval that knows current facts from superseded ones.**

Engineering documents change. A parameter starts as an estimate, gets measured, gets decided — and the old value
lives on in worknotes, test logs, archived plans and early proposals. Those documents state it plainly, often in
exactly the words people ask with ("the phase current limit is 25 A"), while the current value sits in a parameter
table. A retrieval system that ranks by similarity alone will happily hand the old value to the model, and the
model will state it with full confidence and a citation.

![Same question, two retrievals: plain hybrid retrieval returns three history chunks that say 25 A; truth-aware retrieval returns three current chunks that say 32 A](figures/hero-two-answers.svg)

This repo shows a small, transplantable fix — and how to measure it.

## The idea in three lines

1. **Most document sets already say what is current.** Status headers, `archive/` folders, ADR status fields,
   revision tables, "current state" sections in logs. You rarely need to label anything by hand.
2. **Turn that signal into a truth class per chunk** — *current*, *external reference*, *history*, *archive* — and
   **multiply the retrieval score by a weight** for that class. One line in the ranking; nothing else changes.
3. **Measure it with questions whose answer changed.** A golden set with a *stale-truth* category tells you whether
   the current value outranks the superseded one — the failure that ordinary RAG metrics never see.

![Pipeline: ingest (documents, truth classifier, chunker, redaction, BM25 + vector index) and query (hybrid search, truth weight, optional cross-encoder, Claude with citations or refusal, guard)](figures/pipeline.svg)

## Results

![Grouped bars: on the example corpus stale-truth rises from 0.12 to 1.00 with truth weighting; on the real project from 0.78 to 0.89, with hit@5 from 0.62 to 0.93](figures/ablation.svg)

| Corpus | Retrieval | hit@5 | MRR | stale-truth |
|---|---|---|---|---|
| Example (Halyard, synthetic) | hybrid | 0.81 | 0.64 | 0.12 |
| | **hybrid + truth** | **0.90** | **0.84** | **1.00** |
| Real hardware project (121 docs, private) | hybrid | 0.62 | 0.44 | 0.78 |
| | **hybrid + truth** | **0.93** | **0.72** | **0.89** |

**Read with care.** The example corpus is synthetic and was written to contain the failure, so its numbers show the
mechanism, not a typical gain. The real-project numbers come from 29 questions (9 with a superseded value) on a
live engineering project; its corpus is private, so only aggregates are published. For fact and stale-truth
questions a chunk counts as relevant only if it is current — that is the point of the method, and it also means part
of the gain comes from the definition. A cross-encoder reranker added nothing on the real project.

## Try it

```bash
pip install -e .
cd examples/halyard
truthrag ingest                                         # classify, redact, chunk  (20 docs → 91 chunks)
truthrag index                                          # embed on CPU, ~15 s the first time
truthrag search "What is the phase current limit?" --mode hybrid
truthrag search "What is the phase current limit?"      # truth-aware (default)
truthrag eval                                           # golden set → the ablation table above
truthrag ask "What PWM frequency does Halyard use?"     # needs ANTHROPIC_API_KEY
```

`ask` hands the top chunks to Claude labelled CURRENT / HISTORY / EXTERNAL SOURCE, requires a citation for every
claim, answers "not in the corpus" when retrieval finds nothing close, and runs a guard that rejects citations to
chunks that were never retrieved and catches redacted names.

## Use it on your own documents

Write a `truthrag.yaml` that maps the signals your documents already carry to truth classes:

```yaml
truth:
  header: '<!--\s*CONTRACT:\s*(STATE|REFERENCE|LOG)\b'   # a status header, if you have one
  header_classes: {STATE: current, REFERENCE: reference, LOG: log}
  frontmatter_key: status                                # or ADR-style front matter
  frontmatter_classes: {accepted: current, superseded: archive, deprecated: archive, proposed: log}
  archive_dirs: [archive, old, deprecated]               # folders that hold history
  log_current_section: 'Current state'                   # a log's "current" section, if it has one
  retired_terms: docs/RetiredTerms.md                    # optional: wording a decision made wrong
```

**The guide, [`docs/`](docs/README.md)**, explains each part — why living documents break RAG, where truth metadata
comes from, the pipeline, chunking lessons, evaluation, tracking a live corpus, responsible answers. A transplant
guide for ADR repositories, wikis, regulated design files and runbooks is next.

## What is in the repo

| Path | What |
|---|---|
| `docs/` | The guide: seven pages, each with a figure |
| `src/truthrag/` | The package: truth classifier, chunker, redaction, hybrid index, truth-weighted retrieval, Claude answer + guard, evaluation |
| `examples/halyard/` | A synthetic 20-document project (a 48 V motor-controller board) with planted superseded values, a golden set, and a config |
| `figures/` | Every figure as SVG; `scripts/plot_ablation.py` regenerates the chart from `truthrag eval --json` |
| `tests/` | Unit tests; no network, no API key |

## Licence

Code: MIT. Documentation and figures: CC BY 4.0.
