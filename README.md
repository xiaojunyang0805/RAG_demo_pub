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

![Grouped bars of hit@5 and top-1-is-current: on the example corpus top-1-is-current rises from 0.62 to 1.00 with truth weighting; on the real project from 0.34 to 0.97, with hit@5 from 0.69 to 0.90](figures/ablation.svg)

| Corpus | Retrieval | hit@5 | MRR | top-1 is history | stale-truth |
|---|---|---|---|---|---|
| Example (Halyard, synthetic) | hybrid | 0.86 | 0.65 | 0.38 | 0.12 |
| | **hybrid + truth** | **0.90** | **0.85** | **0.00** | **1.00** |
| Real hardware project (121 docs, private) | hybrid | 0.69 | 0.46 | 0.66 | 0.78 |
| | **hybrid + truth** | **0.90** | **0.76** | **0.03** | 0.78 |

*top-1 is history*: share of questions whose best-ranked chunk is a log or archive chunk. *stale-truth*: for
questions whose answer changed, the first top-5 chunk stating either value states the current one.

**Read with care.**

- The example corpus is synthetic and was written to contain the failure; its numbers show the mechanism, not a
  typical gain.
- The real-project numbers come from 29 questions on a live engineering project, 9 of them about values that
  changed. Its corpus is private; only aggregates are published.
- On the real project, stale-truth does not move (0.78 in both modes). After its chunking was fixed (see
  [04](docs/04-chunking-lessons.md)), no superseded value reached the top 5 in either mode; the misses that remain
  are recall misses, where neither value was retrieved. An earlier measurement on broken chunking showed 0.78 → 0.89;
  it is superseded by this one.
- For fact and stale-truth questions a chunk counts as relevant only if it is current — the point of the method,
  and part of why hit@5 rises.
- A cross-encoder reranker on top adds a little on the real project (hit@5 0.93, MRR 0.78).

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
comes from, the pipeline, chunking lessons, evaluation, tracking a live corpus, responsible answers — and ends with
a [transplant guide](docs/08-transplant-guide.md) for ADR repositories, wikis, regulated design files and runbooks.

## What is in the repo

| Path | What |
|---|---|
| `docs/` | The guide: nine pages, each with a figure |
| `src/truthrag/` | The package: truth classifier, chunker, redaction, hybrid index, truth-weighted retrieval, Claude answer + guard, evaluation |
| `examples/adr/` | A second synthetic corpus — eight architecture decision records — where truth comes only from front matter |
| `examples/halyard/` | A synthetic 20-document project (a 48 V motor-controller board) with planted superseded values, a golden set, and a config |
| `figures/` | Every figure as SVG; `scripts/plot_ablation.py` regenerates the chart from `truthrag eval --json` |
| `tests/` | Unit tests; no network, no API key |

## Licence

Code: MIT. Documentation and figures: CC BY 4.0.
