#!/usr/bin/env python3
"""fill_datablock.py — fill 6-ppt-create's DATA BLOCK from an index.json.

Does NOT reimplement post-processing: it only substitutes the DATA BLOCK of
6-ppt-create's static postprocess_template.py, which is exactly what that
skill's Phase 4 asks the agent to do by hand. Running it just saves tokens.

  python fill_datablock.py INDEX.json [-o postprocess_slides.py] [--template PATH]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_TEMPLATE = Path.home() / ".agents/skills/6-ppt-create/postprocess_template.py"
START = "# DATA BLOCK — fill in these values, nothing else"
END = "# ============================================================\n\nCOLOR_MAP"


def build(index: dict) -> str:
    tags, layouts, figs, heights = {}, {}, {}, {}
    for s in index["slides"]:
        i = s["idx"]
        tags[i] = tuple(s["tag"])
        layouts.setdefault(s["layout"], []).append(i)
        figs[i] = s["figures"] if len(s["figures"]) > 1 else s["figures"][0]
        if s.get("figure_height"):
            heights[i] = s["figure_height"]

    for key in ("figure-dominant", "vstack-3", "hstack-3", "table"):
        layouts.setdefault(key, [])

    L = [START,
         "# ============================================================",
         f'PPTX_PATH = {index["pptx"]!r}',
         "", "SECTION_TAGS = {"]
    L += [f"    {i}: {t!r}," for i, t in sorted(tags.items())]
    L += ["}", "", "LAYOUT_MAP = {"]
    L += [f"    {k!r}: {sorted(v)!r}," for k, v in sorted(layouts.items())]
    L += ["}", "", "FIGURES = {"]
    L += [f"    {i}: {v!r}," for i, v in sorted(figs.items())]
    L += ["}", "", "FIGURE_HEIGHT_OVERRIDE = {"]
    L += [f"    {i}: {v!r}," for i, v in sorted(heights.items())]
    L += ["}", "",
          f"BULLET_PLACEHOLDERS = {bool(index.get('bullet_placeholders', True))!r}",
          "",
          f"STAMP_IDS = {bool(index.get('stamp_ids', True))!r}",
          "SLIDE_IDS = {"]
    L += [f"    {s['idx']}: {s['slide_id']!r}," for s in index["slides"] if s.get("slide_id")]
    L += ["}",
          f"PROJECT_ROOT = {index.get('project_root')!r}"]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("index")
    ap.add_argument("-o", "--output")
    ap.add_argument("--template", default=str(DEFAULT_TEMPLATE))
    args = ap.parse_args()

    index = json.loads(Path(args.index).read_text())
    tpl = Path(args.template).read_text()
    if START not in tpl or END not in tpl:
        raise SystemExit(f"ERROR: DATA BLOCK markers not found in {args.template} — "
                         "fill it by hand following 6-ppt-create Phase 4.")

    head, rest = tpl.split(START, 1)
    _, tail = rest.split(END, 1)
    out = Path(args.output or Path(index["storyboard"]).with_name("postprocess_slides.py"))
    out.write_text(head + build(index) + END + tail)
    print(out)


if __name__ == "__main__":
    main()
