# 09 · Results and caveats

**Truth weighting moved the best-ranked chunk from history to current on all three corpora without costing recall.
Whether it improves *stale-truth* depends on how often an old value outranks the new one in your corpus — on the
real project, after its chunking was fixed, it did not. Answer quality is not measured yet.**

*All numbers: 2026-10-26, retrieval only, no LLM calls. Re-run with `truthrag eval`.*

## Retrieval, all modes

| Corpus | Retrieval | hit@5 | MRR | stale-truth | top-1 is history |
|---|---|---|---|---|---|
| **Halyard** — 20 engineering notes, 21 questions (8 stale) | BM25 | 0.67 | 0.49 | 0.12 | 0.52 |
| | vector | 0.90 | 0.58 | 0.12 | 0.48 |
| | hybrid | 0.86 | 0.65 | 0.12 | 0.38 |
| | **hybrid + truth** | **0.90** | **0.85** | **1.00** | **0.00** |
| **ADR** — 8 decision records, 5 questions (3 stale) | BM25 | 1.00 | 0.80 | 0.33 | 0.60 |
| | vector | 1.00 | 0.90 | 0.67 | 0.40 |
| | hybrid | 1.00 | 0.80 | 0.33 | 0.60 |
| | **hybrid + truth** | **1.00** | **1.00** | **1.00** | **0.20** |
| **Real project** — 121 hardware docs, 29 questions (9 stale), private | BM25 | 0.66 | 0.40 | 0.67 | 0.69 |
| | vector | 0.45 | 0.34 | 0.67 | 0.52 |
| | hybrid | 0.69 | 0.46 | 0.78 | 0.66 |
| | **hybrid + truth** | **0.90** | **0.76** | 0.78 | **0.03** |
| | hybrid + truth + cross-encoder | 0.93 | 0.78 | 0.78 | – |

Metric definitions are in [05](05-evaluation.md). In the ADR corpus the remaining 0.20 is correct: one question
asks what a *proposed* record says.

## What helped

| Change | Evidence |
|---|---|
| **Truth weighting** | top-1 is history: 0.38 → 0.00 (Halyard), 0.60 → 0.20 (ADR), 0.66 → 0.03 (real); hit@5 never fell; MRR +0.20 to +0.30 |
| **Hybrid over a single retriever** | real project hit@5: BM25 0.66, vector 0.45, hybrid 0.69. BM25 carries IDs and part numbers; vectors carry paraphrase |
| **Chunks sized with the embedder's tokenizer** | real project: 10.7 % of chunks had been cut off silently; a voltage stated in ten chunks went from missing to ranks 1–2 ([04](04-chunking-lessons.md)) |
| **A tokenizer that keeps IDs whole and adds their parts** | exact-ID questions match `CT-O3`; `full-scale` still matches "full scale" |
| **`record_ids`** | ADR hit@5 with truth weighting: 0.80 without it, 1.00 with it — questions about one record find it whatever its status |
| **The golden-set check as a document linter** | found four places in the real project's current documents still stating superseded values, plus a refusal question that was answerable all along ([06](06-tracking-a-live-corpus.md)) |

## What did not, or only a little

| Change | Evidence |
|---|---|
| **A cross-encoder reranker** | real project: hit@5 +0.03, MRR +0.02, stale-truth unchanged; ~80 MB model, ~3–4 s per question on a CPU. A first integration (its score × the truth weight) let reranker confidence override the weights; it now joins the rank fusion instead |
| **A similarity threshold as the refusal gate** | the default cosine gate (0.60) refused **0 of 5** unanswerable real-project questions; see the figure below |
| **Stale-truth as the headline metric** | on the real project it reads 0.78 with or without truth weighting: after the chunking fix, no superseded value reached the top 5 in either mode, so its misses are recall misses. *Top-1 is history* shows the mechanism instead |

![Two strip plots for the real project: best cosine similarity overlaps almost completely between answerable and unanswerable questions (unanswerable 0.64 to 0.74, answerable 0.60 to 0.83); the best cross-encoder score separates them better (unanswerable 0.01 to 0.29) but one answerable question scores 0.02](../figures/refusal-signal.svg)

Small embedding models compress similarities into a narrow band, so a cosine threshold cannot tell "on topic" from
"answered". The cross-encoder separates better — a 0.20 cut would refuse 4 of 5 unanswerable questions and 1 of 29
answerable ones — but not cleanly. In practice the refusal falls to the model's `not_in_corpus` answer, which is
**not yet measured**.

## Corrections made along the way

Published numbers that turned out wrong, and what replaced them:

| Claim | Status |
|---|---|
| Real project stale-truth 0.78 → 0.89 with truth weighting | **Withdrawn.** Measured on chunks that overflowed the embedder window; with correct chunks it is 0.78 → 0.78 |
| "There are usually more copies of the old value than the new one" | **Wrong** on our own example (91 chunks mention current values, 62 state old ones). History out-*phrases* the current value; see [01](01-living-docs-break-rag.md) |
| All refusal questions verified unanswerable | One was answerable (35 chunks); an output filter had hidden the warning. Rewritten, and the check now runs on every ingest |
| ≈ 3 characters per token | Measured 2.70 on the real project; a first "measured" version sampled a prefix and was worse than the guess ([04](04-chunking-lessons.md)) |

## Costs

| | |
|---|---|
| Embedding model | bge-small-en-v1.5, ≈ 67 MB, CPU |
| First index | Halyard (91 chunks) ≈ 15 s; real project ≈ 20 min for ≈ 6,500 chunks on a laptop CPU; later re-indexes embed only changed chunks |
| Query, retrieval only | well under a second without the cross-encoder |
| Answer step | not yet measured (needs an API key); about 4–6 k input tokens per question with 8 chunks |

## Not measured yet, and other limits

- **Answer quality**: correctness, citation faithfulness, refusal by the model and leak count need Claude calls;
  `truthrag eval --answers` is built and tested offline but has not run against the API.
- **Small n.** 21, 5 and 29 retrieval questions; one question moves stale-truth by 0.11–0.33.
- **Two of three corpora are synthetic** and were written to contain the failure; they demonstrate the mechanism,
  not a typical gain. The real project's golden set was drafted by the builder and approved by the project owner —
  one reviewer.
- **One embedding model, one language.** Multilingual corpora and larger embedders are untested.
- **Relevance for fact and stale questions requires a current chunk** ([05](05-evaluation.md)) — part of why hit@5
  rises with truth weighting.
