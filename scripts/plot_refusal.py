"""Render figures/refusal-signal.svg: best cosine and best cross-encoder score per question, answerable vs
unanswerable — two panels with their own x-axis (different scales; never one dual axis).

    python scripts/plot_refusal.py figures/data/real_project_refusal_signal.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

W, H = 960, 400
STYLE = """
  .root { --surface:#fcfcfb; --t1:#0b0b0b; --t2:#52514e; --grid:#e3e2de; --s1:#2a78d6; --s2:#eb6834; --thr:#0b0b0b; }
  @media (prefers-color-scheme: dark) {
    .root { --surface:#1a1a19; --t1:#f0efec; --t2:#c3c2b7; --grid:#33332f; --s1:#3987e5; --s2:#d95926; --thr:#f0efec; }
  }
  text { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; fill: var(--t1); }
  .t2 { fill: var(--t2); } .grid { stroke: var(--grid); } .thr { stroke: var(--thr); stroke-width: 1.5; stroke-dasharray: 4 3; }
  .ans { fill: var(--s1); stroke: var(--surface); stroke-width: 2; } .ref { fill: var(--s2); stroke: var(--surface); stroke-width: 2; }
"""


def panel(y0: int, title: str, sub: str, key: str, lo: float, hi: float, thr: float, thr_label: str,
          rows: list[dict]) -> list[str]:
    x0, x1 = 210, 920
    sx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    out = [f'<text x="28" y="{y0}" font-size="14" font-weight="600">{escape(title)}</text>',
           f'<text x="28" y="{y0 + 18}" font-size="11" class="t2">{escape(sub)}</text>']
    for i in range(6):
        v = lo + (hi - lo) * i / 5
        out.append(f'<line class="grid" x1="{sx(v):.1f}" x2="{sx(v):.1f}" y1="{y0 + 30}" y2="{y0 + 112}"/>')
        out.append(f'<text x="{sx(v):.1f}" y="{y0 + 128}" font-size="11" class="t2" text-anchor="middle">{v:.2f}</text>')
    lanes = [("answerable", "ans", y0 + 52, [r for r in rows if r["cat"] not in ("refusal", "redaction")]),
             ("not in corpus", "ref", y0 + 92, [r for r in rows if r["cat"] == "refusal"])]
    for label, cls, y, pts in lanes:
        out.append(f'<text x="196" y="{y + 4}" font-size="12" text-anchor="end">{label} (n={len(pts)})</text>')
        for j, r in enumerate(sorted(pts, key=lambda r: r[key])):
            jitter = ((j % 3) - 1) * 6
            out.append(f'<circle class="{cls}" cx="{sx(r[key]):.1f}" cy="{y + jitter}" r="5">'
                       f'<title>{label}: {r[key]:.2f}</title></circle>')
    tx = sx(thr)
    out.append(f'<line class="thr" x1="{tx:.1f}" x2="{tx:.1f}" y1="{y0 + 30}" y2="{y0 + 112}"/>')
    out.append(f'<text x="{tx + 6:.1f}" y="{y0 + 40}" font-size="11">{escape(thr_label)}</text>')
    return out


def main(data_json: str, out: str = "figures/refusal-signal.svg") -> None:
    rows = json.loads(Path(data_json).read_text(encoding="utf-8"))["rows"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
             f'aria-labelledby="title desc" class="root">',
             '<title id="title">How well retrieval scores separate answerable from unanswerable questions</title>',
             '<desc id="desc">Real project. Best cosine similarity per question overlaps almost completely between '
             'answerable and unanswerable questions. The best cross-encoder score separates them better but still '
             'overlaps.</desc>', f"<style>{STYLE}</style>",
             f'<rect width="{W}" height="{H}" rx="10" fill="var(--surface)"/>',
             '<text x="28" y="36" font-size="18" font-weight="600">Retrieval scores are a weak refusal signal</text>',
             '<text x="28" y="56" font-size="12" class="t2">Real project, one dot per golden-set question; best score '
             'among the 8 retrieved chunks.</text>']
    parts += panel(92, "Best cosine similarity (bge-small)", "the built-in pre-LLM gate", "cos", 0.5, 0.9, 0.6,
                   "default gate 0.60", rows)
    parts += panel(252, "Best cross-encoder score", "optional reranker, sigmoid of the logit", "rr", 0.0, 1.0, 0.2,
                   "0.20 for reference", rows)
    parts.append("</svg>")
    Path(out).write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main(*sys.argv[1:])
