"""Heading chunker. Splits on the configured heading levels, keeps tables and code fences whole, and never lets a
chunk outgrow the embedder's window (a model silently drops what it cannot read)."""
from __future__ import annotations

import re

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
TABLE_SEP_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")


def sections(text: str, split_levels: set[int]) -> list[tuple[list[str], list[str]]]:
    """[(heading_path, lines)]. The # title always opens a section; deeper headings stay inside their section."""
    stack: dict[int, str] = {}
    out: list[tuple[list[str], list[str]]] = [([], [])]
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
        m = None if in_fence else HEADING_RE.match(line)
        if m and (len(m.group(1)) == 1 or len(m.group(1)) in split_levels):
            level = len(m.group(1))
            stack = {k: v for k, v in stack.items() if k < level}
            stack[level] = m.group(2)
            out.append(([stack[k] for k in sorted(stack)], []))
        else:
            out[-1][1].append(line)
    return [(h, ls) for h, ls in out if any(l.strip() for l in ls)]


def _blocks(lines: list[str]) -> list[tuple[str, list[str]]]:
    blocks, i = [], 0
    while i < len(lines):
        line = lines[i]
        if FENCE_RE.match(line):
            j = i + 1
            while j < len(lines) and not FENCE_RE.match(lines[j]):
                j += 1
            blocks.append(("code", lines[i: j + 1]))
            i = j + 1
        elif line.lstrip().startswith("|"):
            j = i
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                j += 1
            blocks.append(("table", lines[i:j]))
            i = j
        elif not line.strip():
            i += 1
        else:
            j = i
            while j < len(lines) and lines[j].strip() and not FENCE_RE.match(lines[j]) \
                    and not lines[j].lstrip().startswith("|"):
                j += 1
            blocks.append(("text", lines[i:j]))
            i = j
    return blocks


def _split_block(kind: str, lines: list[str], max_chars: int) -> list[list[str]]:
    """Split one oversized block. A table repeats its header row on every part — only a real header."""
    header = lines[:2] if (kind == "table" and len(lines) > 2 and TABLE_SEP_RE.match(lines[1])
                           and len(lines[0]) < max_chars // 4) else []
    body = []
    for line in lines[len(header):]:
        while len(line) > max_chars:  # one enormous line: cut at a sentence end
            cut = max(line.rfind(s, 0, max_chars) for s in (". ", "; ", ", "))
            cut = cut + 1 if cut > max_chars // 4 else max_chars
            body.append(line[:cut])
            line = line[cut:].lstrip()
        body.append(line)
    parts, cur = [], list(header)
    for line in body:
        if sum(len(l) + 1 for l in cur) + len(line) > max_chars and len(cur) > len(header):
            parts.append(cur)
            cur = list(header)
        cur.append(line)
    if len(cur) > len(header):
        parts.append(cur)
    return parts


def pack(lines: list[str], max_chars: int) -> list[str]:
    pieces = []
    for kind, blk in _blocks(lines):
        pieces.extend(_split_block(kind, blk, max_chars) if sum(len(l) + 1 for l in blk) > max_chars else [blk])
    out, cur, size = [], [], 0
    for p in pieces:
        psize = sum(len(l) + 1 for l in p) + 1
        if cur and size + psize > max_chars:
            out.append("\n".join(cur).strip())
            cur, size = [], 0
        cur.extend(p + [""])
        size += psize
    if cur:
        out.append("\n".join(cur).strip())
    return [t for t in out if t]
