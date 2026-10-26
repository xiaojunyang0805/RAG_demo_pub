# 08 · Transplant guide

**Most corpora need two lines of configuration and a golden set of 20–40 questions. This page takes you from
"we have a RAG" to "our RAG knows what is current", and shows it on a second, different corpus.**

![Decision tree: if documents change and old versions are kept, use a status header if there is one, else YAML front matter, else archive folders, else add the cheapest signal first; in every case add log_current_section for logs with a summary, record_ids for records cited by ID, a retired-terms table, and a golden set with stale-truth questions](../figures/transplant-decision-tree.svg)

## Where the signal lives in common document sets

| Document set | Signal | `truthrag.yaml` |
|---|---|---|
| Architecture decision records | `status: accepted / superseded / deprecated / proposed` in front matter | `frontmatter_key: status` |
| Wiki (Confluence, Notion, MkDocs) | page status label, an "Archive" space or folder | `frontmatter_key` on an export, or `archive_dirs` |
| Regulated design files (medical, automotive, aerospace) | released vs draft revision; change orders that supersede | `header` on the revision block; superseded revisions to `archive_dirs` |
| Contracts and policies | effective date, amendment chain | `frontmatter_key: status`; expired versions to `archive_dirs` |
| Runbooks and incident notes | runbook = current; incident timeline = history with a summary | runbooks `current`, incidents `log` + `log_current_section: '^Summary'` |
| Datasheets and vendor notes | external, not your design | `reference` class |
| Engineering project notes (this repo's real project) | a status line at the top of every document, `archive/` folders, logs with a §0 | `header` + `archive_dirs` + `log_current_section` |

## Ten steps

1. **Check you need it.** Ask a question whose answer changed. If the top results come from old documents, you do.
2. **Find the signal** (table above). Prefer what already exists; if nothing does, move superseded documents into
   `archive/` — the cheapest signal there is.
3. **Write `truthrag.yaml`.** Start from [`examples/adr/truthrag.yaml`](../examples/adr/truthrag.yaml) (front matter)
   or [`examples/halyard/truthrag.yaml`](../examples/halyard/truthrag.yaml) (header, folders, log sections).
4. **Ingest and read the report.** `docs_by_truth` should look like your project: if everything is `current`, the
   signal did not match. `chunks_over_window` should be 0.
5. **Set `record_ids`** if people ask about records by ID (`ADR-0007`, `D12`, `JIRA-123`) — see below.
6. **Add redaction** for names that must never be indexed (`redact.yaml`, gitignored).
7. **Write 20–40 golden questions**: facts, at least 5 whose answer changed (with the old value as `stale`), at
   least 3 the corpus cannot answer (with an `absent` pattern), a few by ID.
8. **Run `truthrag eval`** and compare *hybrid* with *hybrid + truth*: hit@5, MRR, stale-truth, top-1 is history.
9. **Tune only on evidence.** Change a weight when a golden question shows why, and re-run the whole set.
10. **Pin and re-check.** Record the corpus version with every result; run `truthrag eval --check` after every
    ingest ([06](06-tracking-a-live-corpus.md)).

## Worked example: an ADR repository

[`examples/adr`](../examples/adr) is a fictional order service with eight decision records. Three were superseded:
session cookies by OAuth/JWT, REST between services by gRPC, VMs by Kubernetes. As in real ADR repositories, a
superseded record is kept unchanged — and it states its old decision in plain words.

The whole truth configuration is front matter:

```yaml
truth:
  frontmatter_key: status
  frontmatter_classes: {accepted: current, superseded: archive, deprecated: archive, proposed: log}
  record_ids: 'ADR-\d{4}'
```

For "How do clients authenticate?", plain hybrid retrieval ranks the superseded session-cookie decision 2nd and 3rd;
with truth weights the top three are all the current OAuth decision. On its six questions:

| Retrieval | hit@5 | MRR | stale-truth | top-1 is history |
|---|---|---|---|---|
| hybrid | 1.00 | 0.80 | 0.33 | 0.60 |
| **hybrid + truth** | **1.00** | **1.00** | **1.00** | **0.20** |

The remaining 0.20 is correct: one question asks what ADR-0008 *proposes*, and the proposed record should come first.

## A question about history is still a question

Truth weights halve history. That is right for "what is the value", and wrong for "what did ADR-0008 propose" or
"what fixed CT-O3" — questions about one record, current or not. Without a rule for it, the ADR example's hit@5
**fell from 1.00 to 0.80** with truth weighting: the proposed record lost to unrelated current ones.

`record_ids` is that rule. It is a pattern for the identifiers people use to name records in *your* corpus; when a
question names one, chunks containing it keep full weight whatever their class. Keep the pattern specific: a
generic "letters and digits" pattern would also catch a board revision (`V02`) or, in a hardware project, a
component designator (`D1` the diode, not decision D1).

## What to expect

On both example corpora and on the real project, truth weighting took *top-1 is history* to 0 or near 0 and did
not reduce hit@5. How much stale-truth improves depends on how often an old value outranks the new one in *your*
corpus — measure it; [09](09-results-and-caveats.md) has a case where it did not move.
