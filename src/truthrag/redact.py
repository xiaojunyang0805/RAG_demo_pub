"""Name redaction in two gates.

  ingest:  names replaced before anything is stored — the index never holds them.
  public:  names kept in the private index (they are facts there) and replaced in anything published.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import yaml

_CJK = re.compile(r"[㐀-鿿]")


class Redactor:
    def __init__(self, mapping: dict[str, list[str]] | None = None):
        pairs = sorted(((n, tag) for tag, names in (mapping or {}).items() for n in names or [] if n),
                       key=lambda p: -len(p[0]))
        self.names = [n for n, _ in pairs]
        self._rules = [(self._pattern(n), tag) for n, tag in pairs]
        self.counts: Counter[str] = Counter()

    @staticmethod
    def _pattern(name: str) -> re.Pattern:
        esc = re.escape(name)
        if _CJK.search(name):
            return re.compile(esc)
        return re.compile(rf"(?<![A-Za-z0-9]){esc}(?![A-Za-z0-9])", re.IGNORECASE)

    @property
    def empty(self) -> bool:
        return not self._rules

    def __call__(self, text: str) -> str:
        for pat, tag in self._rules:
            text, n = pat.subn(tag, text)
            self.counts[tag] += n
        return text

    def leaks(self, text: str) -> list[str]:
        return [tag for pat, tag in self._rules if pat.search(text)]


def load_redactors(path: Path | None) -> tuple[Redactor, Redactor]:
    if not path or not path.exists():
        return Redactor(), Redactor()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return Redactor(data.get("ingest")), Redactor(data.get("public"))
