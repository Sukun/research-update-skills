#!/usr/bin/env python3
"""write_storyboard.py — deck.json -> storyboard .md that 6-ppt-create can render.

Writes the STORY only: order, title, takeaway, figures, layout, notes.
Geometry/crop stay in deck.json and are NOT reproduced by the standard renderer.

  python write_storyboard.py deck.json -o deck_revised.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

COLORS = ["steelblue", "darkorange", "teal", "purple", "crimson"]


def abs_source(fig, root, deck_dir):
    src = fig.get("source")
    if not src:
        name = fig.get("figure_id") or "unresolved"
        return str(Path(deck_dir) / "assets" / "unresolved" / f"{name}.png")
    p = Path(src)
    if not p.is_absolute() and root:
        p = Path(root) / p
    return str(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck_json")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    deck = json.loads(Path(args.deck_json).read_text())
    out = Path(args.output).resolve()
    root = deck.get("project_root")
    deck_dir = out.parent

    # One colour per section, stable across the deck.
    sections, colors = [], {}
    for s in deck["slides"]:
        key = s.get("section") or s.get("title") or s["slide_id"]
        if key not in colors:
            colors[key] = COLORS[len(sections) % len(COLORS)]
            sections.append(key)

    lines = ["---", "---", ""]
    for i, s in enumerate(deck["slides"]):
        title = (s.get("title") or s["slide_id"]).strip()
        figs = s.get("figures", [])
        layout = s.get("layout") or ("text-only" if not figs else "single")
        paths = [abs_source(f, root, deck_dir) for f in figs]

        lines.append(f"<!-- Slide {i + 1} -->")
        lines.append(f"<!-- slide-id: {s['slide_id']} -->")
        lines.append(f"<!-- layout: {layout} -->")
        if layout == "hstack-3" and len(paths) == 3:
            lines.append("<!-- figures: " + ", ".join(paths) + " -->")
        key = s.get("section") or s.get("title") or s["slide_id"]
        lines.append(f'<!-- section-tag: "{title}" color="{colors[key]}" -->')
        lines.append(f"## {title}")
        lines.append("")

        if s.get("takeaway"):
            for para in str(s["takeaway"]).splitlines():
                if para.strip():
                    lines.append(f"- {para.strip().lstrip('- ')}")
            lines.append("")

        for f, p in zip(figs, paths):
            if layout == "hstack-3" and f is not figs[0]:
                continue
            if f.get("resolved_by") == "unresolved":
                lines.append(f"<!-- unresolved-figure: {f['figure_id']} "
                             f"sha256={f['sha256'][:16]}… origin=manual-insert -->")
            lines.append(f"![]({p})")
        if figs:
            lines.append("")

        for op in s.get("opaque_shapes", []):
            lines.append(f"<!-- TODO: unsupported shape ({op['shape_type']}) — "
                         "not round-tripped -->")

        if s.get("notes"):
            lines += ["::: notes"] + str(s["notes"]).splitlines() + [":::", ""]

        lines += ["---", ""]

    out.write_text("\n".join(lines).rstrip() + "\n")

    n_unres = sum(1 for s in deck["slides"] for f in s.get("figures", [])
                  if f.get("resolved_by") == "unresolved")
    print(f"wrote {out}  ({len(deck['slides'])} slides)")
    if n_unres:
        print(f"{n_unres} unresolved figure(s) referenced from assets/unresolved/")
    print("NOTE: story only — hand-adjusted geometry/crop stay in deck.json and are "
          "not reproduced by the standard renderer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
