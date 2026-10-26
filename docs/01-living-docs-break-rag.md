# 01 · Living documents break RAG

**A retrieval system that ranks by similarity alone will hand the model a superseded value whenever the history
describes it more plainly than the current documents do — and in engineering projects it usually does.**

## How a value goes stale

A parameter starts as an estimate, is measured, and is decided. Each step leaves documents behind, and none of them
is wrong on the day it was written:

![Timeline of the Halyard phase current limit: four documents state 25 A in January and February; on 14 May a stall test measures 31.2 A and decision D8 sets 32 A; the spec documents and logs' current sections state 32 A. Afterwards 11 chunks still state 25 A, all history, and 18 state 32 A](../figures/stale-value-timeline.svg)

The history is right to keep the old value: a worknote that recorded "limit set at 25 A" on 18 February is an
accurate record of 18 February. Rewriting history to match today destroys the reasoning trail. The problem is not
the documents. It is retrieval treating them as equals.

## Why similarity prefers the old value

Count alone does not explain it. In the Halyard example, across its eight values that changed, 91 chunks mention a
current value and 62 still state an old one. The current value is not outnumbered. It is **out-phrased**:

| | Old value (history) | New value (current) |
|---|---|---|
| Where it lives | concept notes, early proposals, bring-up diaries | parameter tables, design notes, guides |
| How it is written | a sentence: "*The phase current limit of the Halyard drive is 25 A.*" | a table cell: `P-02 · Phase current limit · 32 A` |
| Match to the question "What is the phase current limit?" | almost word for word | a few shared tokens |

Early documents explain things in full sentences because nothing has been decided yet. Mature documents are terse
because the reader is assumed to know the context. A question phrased in natural language looks like the early
document.

On Halyard, plain hybrid retrieval (BM25 + vectors) puts a history chunk first for **38 %** of the questions, and
for the question above its top three are all history, all saying 25 A — see the [README](../README.md) figure. On
the real project it is **66 %** of the questions, and 70 % of everything in the top 5.

## How big the history is in a real project

In the real project behind this repo — a 121-document hardware design corpus — **61 % of all chunks** came from
archived documents, and logs added another 15 %. That is not neglect; it is a project that writes things down. The more
diligent the team, the more history the index holds.

## What does not fix it

- **A bigger or newer embedding model.** It matches the history *better*, because the history is the better text
  match.
- **A reranker alone.** A cross-encoder judges relevance, not currency: an archived note that states the old value
  in plain words is highly relevant. On top of truth weighting it helps a little ([09](09-results-and-caveats.md)); instead of it,
  it does not address the problem.
- **Deleting the archive.** You lose the reasoning trail, and history keeps accruing in logs anyway.
- **Asking the model to prefer recent sources.** It can only weigh what it is handed. If the top 8 chunks are history,
  the current value is not in the prompt.

What does fix it: tell retrieval what is current. → [02 · Truth metadata](02-truth-metadata.md)
