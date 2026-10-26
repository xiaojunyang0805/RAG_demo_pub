"""Retired wording: a table of patterns that a decision made wrong, used as a stale-statement detector.

Table rows look like  | `regex` | retired by | use instead |  (pipes inside the regex escaped as \\|).
A line that matches is NOT stale when it marks itself as history (negation markers, or the retiring ID).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_ID = re.compile(r"`([^`]+)`")


@dataclass
class RetiredTerm:
    pattern: re.Pattern
    retired_by: str
    use_instead: str
    ids: list[str]


def negation_re(markers: list[str], extra_literals: list[str] = ()) -> re.Pattern:
    parts = list(markers) + [re.escape(x) for x in extra_literals if x]
    return re.compile("|".join(parts), re.IGNORECASE)


def load_retired_terms(path: Path | None) -> list[RetiredTerm]:
    if not path or not path.exists():
        return []
    terms = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        if len(cells) < 3:
            continue
        try:
            pat = re.compile(cells[0].strip("`").replace("\\|", "|"), re.IGNORECASE)
        except re.error:
            continue
        terms.append(RetiredTerm(pat, cells[1].replace("`", ""), cells[2], _ID.findall(cells[1])))
    return terms


def states(pattern: re.Pattern, text: str, negation: re.Pattern, ids: list[str] = ()) -> bool:
    """True if some line matches `pattern` without marking itself as history."""
    return any(pattern.search(line) and not negation.search(line) and not any(i in line for i in ids)
               for line in text.splitlines())


def asserted_retired(text: str, terms: list[RetiredTerm], negation: re.Pattern) -> list[str]:
    return sorted({t.retired_by for t in terms if states(t.pattern, text, negation, t.ids)})
