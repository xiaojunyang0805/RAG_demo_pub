# 07 · Responsible answers

**Cite or refuse. Verify every citation after the model answers. Keep confidential names out of the index, not just
out of the output.**

![Two redaction gates around the answer path: gate 1 at ingest replaces confidential names in text and file paths; at question time nothing close means not in the corpus with no model call, otherwise Claude answers with citations or not_in_corpus, and a guard checks every citation and every name; gate 2 at publish replaces names that are internal facts](../figures/guard-and-gates.svg)

## Cite or refuse

The model is told to put a source number after every factual sentence and to answer `not_in_corpus` when the
sources do not answer the question — never from general knowledge. Refusal happens in two places:

1. **Before the model**, when nothing retrieved is close enough ([03](03-pipeline.md)). No tokens spent, no chance
   to improvise.
2. **By the model**, when the retrieved chunks are on topic but do not contain the answer.

The Halyard refusal questions ask about a price, a warranty and an EtherCAT stack — plausible questions about a
motor controller that the documents do not answer.

## Never trust the citations

After the model answers, the guard checks:

| Check | Catches |
|---|---|
| every `[n]` points at a chunk that was actually retrieved | invented or off-by-one citations |
| the answer has at least one inline citation | an answer that drifted into general knowledge |
| no redacted name appears in the answer or the `superseded` note | a name reconstructed from context |

Issues are attached to the answer and counted by the evaluation (citation faithfulness, leak count) — the guard
reports, it does not silently repair.

## Two redaction gates

| Gate | When | What | Why |
|---|---|---|---|
| 1 · ingest | before anything is stored | customer and staff names → `[customer]`, `[engineer]` | the index, logs and caches never hold them |
| 2 · publish | on output that leaves the team | names that are facts internally (a vendor, a product) → `[vendor]` | they help engineers inside, but not in a recording or a report |

Two details that are easy to miss:

- **File paths leak too.** A folder named after a customer ends up in every citation. Redact the path along with the
  text.
- **The redaction list is itself confidential.** It contains exactly the names you are hiding. Keep it out of version
  control; ship an example file instead. (The Halyard `redact.yaml` is committed only because its names are
  invented.)

## Separate what is private from what is shared

The real project behind this repo keeps two repositories: a private one with the corpus path, the real golden set,
per-question results and the redaction list, and this public one with the method, a synthetic corpus and aggregate
numbers. Before every public push, a scan for every name on the redaction list must come back empty.
