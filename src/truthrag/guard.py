"""Never trust the model's citations: every [n] must point at a retrieved chunk, and no redacted name may appear."""
from __future__ import annotations

import re

from .models import Answer
from .redact import Redactor

CITE_RE = re.compile(r"\[(\d+)\]")


def check(ans: Answer, ingest_redactor: Redactor, public_redactor: Redactor | None = None) -> Answer:
    issues = []
    if not ans.refused:
        inline = {int(x) for x in CITE_RE.findall(ans.text)}
        for ref in sorted(inline | set(ans.citations)):
            if not 1 <= ref <= len(ans.hits):
                issues.append(f"citation [{ref}] does not match a retrieved chunk")
        if not inline:
            issues.append("answer has no inline citation")
        ans.citations = sorted(set(ans.citations) | inline)
    for field in ("text", "superseded"):
        value = getattr(ans, field)
        issues += [f"leak: {tag}" for tag in ingest_redactor.leaks(value)]
        value = ingest_redactor(value)
        setattr(ans, field, public_redactor(value) if public_redactor else value)
    ans.guard_issues.extend(issues)
    return ans
