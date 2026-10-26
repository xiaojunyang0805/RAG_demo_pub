# 03 · The pipeline

**A standard hybrid RAG with one extra multiplication. Truth is decided at ingest and used at ranking; refusal is
decided before the model is called.**

![Pipeline: ingest (documents, truth classifier, chunker, redaction, BM25 + vector index) and query (hybrid search, truth weight, optional cross-encoder, Claude with citations or refusal, guard)](../figures/pipeline.svg)

## Ranking

```
score = RRF(bm25_rank, vector_rank) × weight[truth class] × (0.5 if the chunk states retired wording)
```

- **BM25** catches exact identifiers that embeddings blur: decision IDs (`D12`), item IDs (`CT-O3`), part numbers
  (`GD-22`). Its tokenizer keeps hyphenated tokens whole *and* adds their parts, so `CT-O3` is an exact match while
  `full-scale` still matches "full scale".
- **Vectors** catch paraphrase: "how hot can the heat sink get" finds "thermal shutdown".
- **Reciprocal-rank fusion** (RRF, k = 60) combines the two by rank, so neither score scale dominates.
- **The truth weight** multiplies the fused score. That is the whole method.

Here is what it does to the top 8 for one question:

![Rank changes for "What is the phase current limit?": in plain hybrid, ranks 1 to 3 and 6 are history chunks stating 25 A; with truth weights the four current chunks move to ranks 1 to 4, the history chunks leave the top 8, and four more current sources enter. Every chunk in the new top 8 states 32 A](../figures/rerank-bump.svg)

Note what it does *not* do: it does not filter history out. A history chunk that is the only match still comes back
— with weight 0.5 it needs to be twice as relevant as a current chunk to outrank it. Questions *about* history
("why was the connector changed?") still find the logs, because only the logs contain the reasoning.

## An optional cross-encoder

A cross-encoder rescores the top candidates by reading question and chunk together. In `truthrag` it joins RRF as a
third ranked list, *then* the truth weight applies. An earlier version multiplied the cross-encoder's score by the
weight directly; its confidence swamped the weights and history climbed back to the top. Keep currency and relevance
as separate factors.

## Refusal before the model

RRF scores are rank-based, so they cannot say "nothing here is relevant". `truthrag` decides refusal from absolute
signals instead:

- the best cosine similarity of any retrieved chunk is above a threshold (`min_vector_sim`, default 0.6), **or**
- an identifier from the question (`CT-O3`, `D12`) appears verbatim in a retrieved chunk.

If neither holds, the answer is "not in the corpus" and no model call is made. When the model *is* called, it can
still answer `not_in_corpus` — see [07](07-responsible-answers.md). Small embedding models compress similarities
into a narrow band, so treat the threshold as a first gate and tune it on your refusal questions.

## The answer step

The top chunks go to Claude as numbered sources, each labelled `CURRENT`, `HISTORY` or `EXTERNAL SOURCE`, with a
note when a chunk states retired wording. A JSON schema forces the reply into fields: `answer` (with `[n]` markers),
`citations`, `status`, `superseded` (the old value and what replaced it) and `not_in_corpus`.

The `superseded` field is the user-facing payoff: *"32 A peak per phase — superseded: 25 A, an estimate replaced by
the measured stall current (D8)."* The reader learns the current value and why an old document says otherwise.
