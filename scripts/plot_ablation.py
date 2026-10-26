"""Render figures/ablation.svg from the example's ablation JSON and the real project's aggregates.

    truthrag -c examples/halyard/truthrag.yaml eval --json examples/halyard/.truthrag/ablation.json
    python scripts/plot_ablation.py examples/halyard/.truthrag/ablation.json figures/data/real_project_ablation.json

Palette: categorical slots 1-2 of the dataviz reference palette, validated for light and dark surfaces.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

MODES = ["BM25", "vector", "hybrid", "hybrid + truth"]
SERIES = [("hit5", "hit@5", "s1"), ("top1_current", "top-1 is current", "s2")]
W, H = 960, 450
PANEL_W, TOP, PLOT_H, LEFT = 430, 138, 220, 52
BAR, GAP = 22, 2

STYLE = """
  .root { --surface:#fcfcfb; --t1:#0b0b0b; --t2:#52514e; --grid:#e3e2de; --band:#f1f0ec; --s1:#2a78d6; --s2:#eb6834; }
  @media (prefers-color-scheme: dark) {
    .root { --surface:#1a1a19; --t1:#f0efec; --t2:#c3c2b7; --grid:#33332f; --band:#242422; --s1:#3987e5; --s2:#d95926; }
  }
  text { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; fill: var(--t1); }
  .t2 { fill: var(--t2); } .s1 { fill: var(--s1); } .s2 { fill: var(--s2); }
  .grid { stroke: var(--grid); stroke-width: 1; } .base { stroke: var(--t2); stroke-width: 1; }
"""


def bar(x: float, y0: float, h: float, cls: str, tip: str) -> str:
    """Column with a 4px rounded data-end, square at the baseline."""
    r = min(4, h)
    top = y0 - h
    d = (f"M{x},{y0} V{top + r} Q{x},{top} {x + r},{top} H{x + BAR - r} Q{x + BAR},{top} {x + BAR},{top + r} "
         f"V{y0} Z")
    return f'<path class="{cls}" d="{d}"><title>{escape(tip)}</title></path>'


def panel(ox: float, data: dict) -> list[str]:
    rows = {r["mode"]: dict(r, top1_current=1 - r["top1_history"]) for r in data["rows"]}
    out = [f'<text x="{ox}" y="{TOP - 46}" font-size="15" font-weight="600">{escape(data["label"])}</text>',
           f'<text x="{ox}" y="{TOP - 28}" font-size="12" class="t2">{escape(data["subtitle"])}</text>']
    y0, plot_w = TOP + PLOT_H, PANEL_W - LEFT
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        y = y0 - v * PLOT_H
        out.append(f'<line class="{"base" if v == 0 else "grid"}" x1="{ox + LEFT}" x2="{ox + PANEL_W}" y1="{y}" y2="{y}"/>')
        out.append(f'<text x="{ox + LEFT - 8}" y="{y + 4}" font-size="11" class="t2" text-anchor="end">{v:.2f}</text>')
    slot = plot_w / len(MODES)
    for i, mode in enumerate(MODES):
        cx = ox + LEFT + slot * (i + 0.5)
        if mode == "hybrid + truth":
            out.insert(2, f'<rect x="{cx - slot / 2 + 4}" y="{TOP - 8}" width="{slot - 8}" height="{PLOT_H + 8}" '
                          f'rx="6" fill="var(--band)"/>')
        x = cx - BAR - GAP / 2
        for key, label, cls in SERIES:
            v = rows[mode][key]
            out.append(bar(x, y0, v * PLOT_H, cls, f"{data['label']} · {mode} · {label}: {v:.2f}"))
            if mode in ("hybrid", "hybrid + truth"):  # selective direct labels: the comparison that matters
                weight = ' font-weight="600"' if mode == "hybrid + truth" else ""
                out.append(f'<text x="{x + BAR / 2}" y="{y0 - v * PLOT_H - 6}" font-size="11" text-anchor="middle"'
                           f'{weight}>{v:.2f}</text>')
            x += BAR + GAP
        out.append(f'<text x="{cx}" y="{y0 + 20}" font-size="12" text-anchor="middle"'
                   f'{" font-weight=\"600\"" if mode == "hybrid + truth" else " class=\"t2\""}>{escape(mode)}</text>')
    return out


def main(halyard_json: str, real_json: str, out: str = "figures/ablation.svg") -> None:
    halyard = {"label": "Example corpus (Halyard)",
               "subtitle": "20 documents · 21 questions · synthetic, built to show the effect",
               "rows": json.loads(Path(halyard_json).read_text(encoding="utf-8"))}
    real = json.loads(Path(real_json).read_text(encoding="utf-8"))
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
             f'aria-labelledby="title desc" class="root">',
             '<title id="title">Retrieval ablation: truth weighting</title>',
             '<desc id="desc">Grouped bars of hit@5 and stale-truth for BM25, vector, hybrid and hybrid with truth '
             'weighting, on the example corpus and on a real project. Values are listed in the README table.</desc>',
             f"<style>{STYLE}</style>",
             f'<rect width="{W}" height="{H}" rx="10" fill="var(--surface)"/>',
             '<text x="28" y="36" font-size="18" font-weight="600">Truth weighting puts current sources first'
             '</text>',
             # legend
             '<rect x="28" y="52" width="12" height="12" rx="2" class="s1"/>'
             '<text x="46" y="62" font-size="12">hit@5 — a relevant chunk in the top 5</text>',
             '<rect x="300" y="52" width="12" height="12" rx="2" class="s2"/>'
             '<text x="318" y="62" font-size="12">top-1 is current — the best-ranked chunk is not history</text>']
    parts += panel(28, halyard) + panel(28 + PANEL_W + 40, real)
    parts.append(f'<text x="28" y="{H - 18}" font-size="11" class="t2">Same 0–1 scale in both panels. Real-project '
                 f'numbers are aggregates; its corpus and questions are private.</text>')
    parts.append("</svg>")
    Path(out).write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main(*sys.argv[1:])
