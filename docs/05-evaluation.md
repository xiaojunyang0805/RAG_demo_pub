# 05 · Evaluation

**Ordinary RAG metrics cannot see stale answers: the stale chunk *is* relevant to the question. You need questions
whose answer changed, and a metric that asks which value ranked first.**

![An annotated golden-set question: category stale; evidence '32 ?A' drives hit@5 and MRR; must '32 ?A' drives answer correctness; stale '25 ?A' drives the stale-truth metric; refusal questions add an absent pattern that must match no chunk](../figures/golden-anatomy.svg)

## Categories

| Category | Halyard | Real project | Tests |
|---|---|---|---|
| Fact lookup | 6 | 10 | the value is found and stated |
| Exact ID | 4 | 6 | BM25 catches `D12`, `CT-O3` |
| **Stale truth** | 8 | 8 | the current value outranks the superseded one, and the answer gives it |
| Multi-hop | 3 | 5 | two sources are both retrieved and both cited |
| **Refusal** | 3 | 5 | "not in the corpus", no guessing |
| **Redaction** | 2 | 3 | no confidential name appears |

Categories turn a score into a diagnosis. On the real project every remaining retrieval miss was a stale-truth
question — that told us where to work.

## Mark relevance by text, not by file

A golden set that lists the "right" file and section breaks the first time you re-chunk. `truthrag` marks relevance
with a regular expression the relevant chunk must contain (`evidence`). For fact and stale questions the matching
chunk must also be **current** — a history chunk that happens to contain "32 A" is not where an engineer should be
sent. Exact-ID and multi-hop questions accept any chunk (`evidence_truth: any`).

Be honest about what that means: part of the truth-weighting gain comes from this definition. That is the intent —
the question asks for what is true now — but say so when you report it.

## Metrics

| Metric | Definition |
|---|---|
| hit@5 | a relevant chunk in the top 5 (multi-hop: every `evidence_all` pattern matched in the top 5) |
| MRR | 1 / rank of the first relevant chunk, top 10 |
| stale-truth (retrieval) | among the top 5, the first chunk that states *either* value states the current one |
| top-1 is history | the first-ranked chunk is a log or archive chunk |
| correctness | every `must` pattern appears in the answer (optionally confirmed by an LLM judge) |
| citation faithfulness | every citation points at a retrieved chunk, and at least one cited chunk is relevant |
| stale-truth (answer) | the answer gives the current value and does not state the old one (the `superseded` field may) |
| refusal / leaks | refusal questions answered "not in the corpus"; redacted names found in any answer (target 0) |

"States" uses the same rule as retired wording: *"was 25 A"* does not state 25 A.

## Make sure refusal questions stay unanswerable

A refusal question is only valid while the corpus truly lacks the answer. Each carries an `absent` pattern that
must match no chunk, checked on every run:

```yaml
- {id: R02, category: refusal, question: "How long is the warranty on a Halyard drive?", absent: '(?i)warranty'}
```

This caught a real mistake: a refusal question about telemetry was answerable all along — 35 chunks mentioned
telemetry — and the question was rewritten.

## Running it

```bash
truthrag eval                  # retrieval metrics for every mode — no API key needed
truthrag eval --rerank         # add the cross-encoder row
truthrag eval --answers        # answer metrics (calls Claude)
truthrag eval --check          # only validate the golden set against the corpus — see 06
```
