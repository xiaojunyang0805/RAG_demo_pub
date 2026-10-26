# 04 · Chunking lessons

**Three silent failures, each found by a failing evaluation question. None raised an error.**

## 1. The embedder only reads its window

`bge-small-en-v1.5`, like most small embedding models, reads 512 tokens and drops the rest without a warning. The
vector is computed; it just describes the first part of the chunk.

![Three bars against a 512-token window: a chunk sized by guessing 800 tokens at 4 characters is about 1,200 model tokens, 57 percent never read; a second guess at 3 characters per token still cut 10.7 percent of chunks; sizing with the embedder's own tokenizer leaves none over](../figures/embedder-window.svg)

The guesses failed because **technical text tokenizes densely**. Part numbers, units, IDs, table pipes and
backticks break into many tokens. Measured with the embedder's own tokenizer:

| Corpus | Characters per token |
|---|---|
| Real hardware project | 2.66 |
| Halyard example | 2.98 |
| Typical English prose (rule of thumb) | ≈ 4 |

How it showed up: a question about a voltage that ten chunks state missed the top 5 entirely. The value
sat in the second half of long sections. After re-chunking, the same question found it at ranks 1 and 2.

**What `truthrag` does:** with `chars_per_token: auto` (the default) it measures this ratio on your corpus with the
embedder's tokenizer, sizes chunks to fit, and reports `chunks_over_window` after every ingest. On Halyard: 2.98
characters per token, 0 chunks over.

## 2. Tokenizers that keep IDs whole can break ordinary words

BM25 is there to catch exact identifiers, so its tokenizer should keep `CT-O3` as one token rather than `ct` + `o3`.
The first version did exactly that — and turned the question's `full-scale` into one token that never matched the
corpus's "full scale".

**Fix:** emit the whole hyphenated token *and* its parts. `CT-O3` → `ct-o3`, `ct`, `o3`. The exact match still
scores highest; ordinary hyphenated words still match their spaced form.

## 3. Splitting a table: repeat the header — but only a real one

Tables are the densest source of current values (parameter tables, pin maps, status tables), so the chunker keeps
them whole and, when one is too long, splits it by rows with the header row repeated on every part.

The first version repeated the first two lines of *any* table block. A table that continued after a heading had no
header, so it repeated two data rows on every part — producing chunks of 2,700 tokens. **Fix:** repeat only when
line two is a `|---|` separator and the header is short.

## Defaults that held up

| Setting | Value | Why |
|---|---|---|
| Split on | `##` and `###` | engineering docs are heading-structured; deeper headings stay inside their section |
| Max chunk | 400 tokens + heading trail | fits a 512-token window with room for the path and headings |
| Heading trail | `path > title > section` prepended to the embedded text | gives a 3-line table cell its context |
| Code fences, tables | never split mid-block | a half table is worse than a long chunk |
