# 02 · Truth metadata

**Most document sets already say how current each document is. Map that signal to five truth classes and a weight
per class; no hand labelling.**

![Signals in documents (status header, ADR front matter, a log's current-state section, reference header, log or proposed status, archive folder, superseded status) mapped to five truth classes (current, log current section, external reference, history, archive) with weights 1.0, 1.0, 0.9, 0.5, 0.2; retired wording multiplies by 0.5](../figures/truth-signals.svg)

## The five classes

| Class | Meaning | Default weight | Status tag in answers |
|---|---|---|---|
| `current` | must be true now | 1.0 | current |
| `log_current` | the "current state" section of a log | 1.0 | current |
| `reference` | what an external source says (a datasheet, a vendor note) — true *about that source* | 0.9 | vendor claim |
| `log` | history: diaries, test logs, proposals, drafts | 0.5 | history |
| `archive` | superseded documents kept for the record | 0.2 | history |

`reference` sits just below `current` on purpose. A datasheet is authoritative about the part, but it is not your
design: a vendor's reference design switching at 20 kHz does not mean your board does.

Weights are not penalties for being wrong — history is accurate history. They express *how likely a chunk is to be
the right answer to a question about now*. The defaults worked on both corpora in this repo; tune them on your
golden set, not by intuition.

## Where the signal comes from

`truthrag` reads five kinds of signal, all from configuration:

```yaml
truth:
  header: '<!--\s*CONTRACT:\s*(STATE|REFERENCE|LOG)\b'      # a status line near the top
  header_classes: {STATE: current, REFERENCE: reference, LOG: log}
  frontmatter_key: status                                   # YAML front matter
  frontmatter_classes: {accepted: current, superseded: archive, deprecated: archive, proposed: log}
  archive_dirs: [archive, old]                              # folders
  log_current_section: '§\s*0\b'                            # the current section inside a log
  retired_terms: docs/RetiredTerms.md                       # wording a decision made wrong
```

Precedence: **archive folder › front matter › header › default**. A document in `archive/` is history whatever its
header claims — it was written as current, then retired.

### A log's current section

Logs are append-only, so most of a log is history. Many teams keep a summary at the top ("Current state",
"Status", "§0"). `log_current_section` marks the sections under such a heading as `log_current`, so a log can be
both the best history *and* a current source.

### Retired wording

A decision often makes a phrase wrong everywhere at once ("PWM at 20 kHz", "the C4-120 MCU"). A retired-terms
table lists the pattern, the decision that retired it and what to say instead:

| Pattern | Retired by | Use instead |
|---|---|---|
| `20 ?kHz PWM\|PWM (at\|of) 20 ?kHz` | `D7` | PWM 24 kHz |

Any chunk that *states* a retired pattern gets a further ×0.5. "States" excludes lines that mark themselves as
history — *was*, *not*, *no longer*, *superseded*, *replaced*, `~~strikethrough~~`, or the retiring decision's ID.
"PWM was 20 kHz until D7" does not count; "PWM at 20 kHz" does.

## If your documents carry no signal

Start with the cheapest one: move superseded documents into an `archive/` folder. Then add a one-line status
header to the ten documents people ask about most. The transplant guide ([08](08-transplant-guide.md))
covers ADR repositories, wikis, regulated design files and runbooks.
