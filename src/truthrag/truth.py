"""Truth classification: decide, per document and per section, whether text states what is true now.

The signals are configurable because every corpus carries them differently:
  - a header pattern           <!-- CONTRACT: STATE -->               (header + header_classes)
  - YAML front matter          status: superseded                     (frontmatter_key + frontmatter_classes)
  - folders                    .../archive/...                        (archive_dirs)
  - a log's current section    "## §0 CURRENT STATE" inside a LOG      (log_current_section)
Precedence: archive folder > front matter > header > default. Inside a `log` document, sections under a heading
matching `log_current_section` are `log_current`; the rest stay `log`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import yaml

from .models import ARCHIVE, CLASSES, LOG, LOG_CURRENT

_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@dataclass
class DocTruth:
    truth: str
    body: str          # text with the header / front matter removed


class TruthClassifier:
    def __init__(self, tcfg: dict):
        self.cfg = tcfg
        self.header = re.compile(tcfg["header"], re.DOTALL) if tcfg.get("header") else None
        self.current_section = re.compile(tcfg["log_current_section"]) if tcfg.get("log_current_section") else None
        for cls in list(tcfg.get("header_classes", {}).values()) + list(tcfg.get("frontmatter_classes", {}).values()) \
                + [tcfg["default"]]:
            if cls not in CLASSES:
                raise ValueError(f"unknown truth class {cls!r}; use one of {CLASSES}")

    def classify_doc(self, rel_parts: tuple[str, ...], text: str) -> DocTruth:
        truth, body = self.cfg["default"], text
        if self.header:
            m = self.header.search(text[:2000])
            if m:
                truth = self.cfg["header_classes"].get(m.group(1), truth)
                # Remove the whole HTML comment that carries the header, or just the match if it is not in one.
                start, end = text.rfind("<!--", 0, m.start() + 1), text.find("-->", m.end())
                if start != -1 and end != -1:
                    body = text[:start] + text[end + 3:]
                else:
                    body = text[: m.start()] + text[m.end():]
        fm = _FRONTMATTER.match(text)
        if fm and self.cfg.get("frontmatter_key"):
            try:
                meta = yaml.safe_load(fm.group(1)) or {}
            except yaml.YAMLError:
                meta = {}
            value = str(meta.get(self.cfg["frontmatter_key"], "")).strip().lower()
            if value in self.cfg.get("frontmatter_classes", {}):
                truth = self.cfg["frontmatter_classes"][value]
            body = body.replace(fm.group(0), "", 1)
        if set(self.cfg.get("archive_dirs", [])) & set(rel_parts[:-1]):
            truth = ARCHIVE
        return DocTruth(truth, body)

    def classify_section(self, doc_truth: str, heading_path: list[str]) -> str:
        if doc_truth == LOG and self.current_section and any(self.current_section.search(h) for h in heading_path):
            return LOG_CURRENT
        return doc_truth
