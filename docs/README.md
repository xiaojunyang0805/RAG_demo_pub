# Truth-aware RAG — the guide

Read in order, or jump to what you need.

| # | Page | One-line answer |
|---|---|---|
| 01 | [Living documents break RAG](01-living-docs-break-rag.md) | Old values stay in history documents, phrased the way people ask; similarity search prefers them |
| 02 | [Truth metadata](02-truth-metadata.md) | Your documents already say how current they are — map that to five classes and a weight |
| 03 | [The pipeline](03-pipeline.md) | Standard hybrid RAG plus one multiplicative weight; refusal decided before the model is called |
| 04 | [Chunking lessons](04-chunking-lessons.md) | The embedder silently drops what does not fit its window — measure chunk size with its tokenizer |
| 05 | [Evaluation](05-evaluation.md) | A golden set with a stale-truth category, relevance marked by text pattern, not file path |
| 06 | [Tracking a live corpus](06-tracking-a-live-corpus.md) | Pin every result to a corpus commit; the golden-set check also finds stale statements in your docs |
| 07 | [Responsible answers](07-responsible-answers.md) | Cite or refuse, verify every citation, redact before indexing |
| 08 | Transplant guide | *coming* |
| 09 | Results and caveats | *coming* |

All examples run on the synthetic corpus in [`examples/halyard`](../examples/halyard). Numbers from the real
project are aggregates; its corpus is private.
