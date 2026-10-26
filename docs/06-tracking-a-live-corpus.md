# 06 · Tracking a live corpus

**A live project changes every day. Pin every score to the corpus version it measured, re-validate the golden set
on every ingest — and use the same check to find stale statements in the documents themselves.**

![A loop: the corpus changes and gets a new commit; ingest records it; the golden-set check runs; FAIL means a question is invalid, fix the question; WARN means a current document still states a superseded value, fix the document and add the wording to the retired-terms table; then re-ingest](../figures/live-corpus-loop.svg)

## Pin results to a corpus version

If the documents live in git, record the commit at ingest and print it in every result row. A score without a
corpus version cannot be compared with anything: the answer to "did the change help?" depends on whether the
documents moved too.

## Re-validate the golden set

Every question can go stale as well. `truthrag eval --check` verifies, for the corpus as ingested:

| Check | Level | Meaning |
|---|---|---|
| `evidence` still matches a current chunk | FAIL | the fact moved or changed; fix the question |
| every `evidence_all` pattern still matches | FAIL | a multi-hop source disappeared |
| `absent` still matches nothing | FAIL | a refusal question became answerable |
| no *current* chunk states the `stale` value | WARN | a current document contradicts the decision |

## The WARN that matters

The last check turns the evaluation into a **document linter**. If a document marked current still states the
superseded value as fact, either the document is wrong or the golden answer is.

On the real project, the first run flagged three places in two current documents that still quoted a superseded peak
current — and one analysis section whose numbers were all derived from a superseded load value. The project's own
consistency checker could not see them, because no retired-terms pattern covered that wording. The fix was the
project's usual one: correct the documents, re-derive the dependent numbers, and add the wording to the
retired-terms table so it cannot come back.

The same run caught weak golden-set patterns. A stale pattern of just `2\.54` matched every unrelated 2.54 mm
connector; tightened to its context, the check went quiet where it should.

## Keep it cheap

Re-embedding a few thousand chunks on a CPU takes about 20 minutes. `truthrag` caches embeddings by the hash of
each chunk's text, so a re-ingest after a document edit re-embeds only the chunks that changed — typically a
handful, in seconds.
