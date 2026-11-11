#!/usr/bin/env python3
"""md_to_slides.py - Markdown input adapter for 6-ppt-create.

Turns a figure-first markdown (quickview, or a topic record's Summary) into a
6-ppt-create storyboard and, with --render, hands it to render_storyboard.py's
documented path (build_pptx.py -> postprocess_template.py -> identity stamping).
It makes NO content decisions: every `## ` block of the source becomes one slide,
in source order, with the figures, caption and bullets it already has. It owns no
render chain of its own (no Pandoc call, no DATA BLOCK filling).

  python md_to_slides.py SOURCE.md [-o OUT.md] [--section Summary] [--layout auto]
                         [--tag-prefix OSNAP] [--no-cover] [--render] [--engine pptx|pandoc]
  python md_to_slides.py STORYBOARD.md --render-only   # render an existing storyboard

Mapping (source -> slide):
  `# Title` + first paragraph      -> cover slide (unless --no-cover)
  `## Heading`                     -> one slide; the heading is the slide TITLE (never hidden)
  --tag-prefix P                   -> small top-right section label "P" on every content slide
  `![](fig)`                       -> figures (relative paths resolved from SOURCE's directory)
  `**Figure N.** caption`          -> first bullet (bold lead-in kept)
  `- bullet`                       -> bullets (max 3 on the slide; extras -> speaker notes)
  other paragraphs / links         -> speaker notes
  `<!-- layout: X -->` in a block  -> explicit layout for that slide (beats --layout and auto)
  `## Technical details` block     -> speaker notes of the cover (or last slide)
  --section X                      -> only the level-1 section starting with X; `Summary` and the
                                      legacy `L1` match either spelling (`# Summary`, `# L1 - Summary`)

Exit codes: 0 ok, 2 unresolved figure path or unsupported figure count (nothing written).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

SKILL = Path(__file__).resolve().parent
sys.path.insert(0, str(SKILL))
import render_storyboard  # noqa: E402

COLORS = ["steelblue", "darkorange", "teal", "purple", "crimson"]
ASPECT_BREAKEVEN = 2.3           # same threshold as 5-ppt-design / 6-ppt-create
ASPECT_FALLBACK = 1.6
MAX_BULLETS = 3
KNOWN_LAYOUTS = set(render_storyboard.LAYOUTS) - {"custom", "cover"}
TECH_RE = re.compile(r"^technical details\b", re.I)
IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)(\{[^}]*\})?")
CAPTION_RE = re.compile(r"^\*\*Figure\s+\d+[a-z]?\.\*\*\s*", re.I)
LAYOUT_RE = re.compile(r"<!--\s*layout:\s*([\w-]+)\s*-->")
SECTION_ALIASES = {"summary": ("summary", "l1"), "l1": ("summary", "l1")}


def aspect_of(p: Path) -> float:
    if Image is None:
        return ASPECT_FALLBACK
    try:
        w, h = Image.open(p).size
        return w / h
    except Exception:
        return ASPECT_FALLBACK


# ------------------------------------------------------------------ parsing

def restrict_section(lines, section):
    """Keep only lines under the level-1 heading that starts with `section`.
    `Summary` and legacy `L1` accept either spelling (e.g. `# L1 · Summary`)."""
    wanted = SECTION_ALIASES.get(section.lower(), (section.lower(),))
    out, inside = [], False
    for ln in lines:
        if re.match(r"^# (?!#)", ln):
            inside = ln[2:].strip().lower().startswith(wanted)
            continue
        if inside:
            out.append(ln)
    if not out:
        raise SystemExit(f"ERROR: no '# {section}...' section found")
    return out


def parse(src: Path, section: str | None):
    raw = src.read_text().splitlines()
    title = next((l[2:].strip() for l in raw if re.match(r"^# (?!#)", l)), src.stem)
    # subtitle = first non-empty, non-heading line after the first H1
    subtitle = ""
    seen_h1 = False
    for l in raw:
        if re.match(r"^# (?!#)", l):
            if seen_h1:
                break
            seen_h1 = True
            continue
        if seen_h1 and l.strip() and not l.startswith("#") and l.strip() != "---":
            subtitle = l.strip()
            break
    lines = restrict_section(raw, section) if section else raw

    blocks, cur = [], None
    for ln in lines:
        if ln.startswith("## "):
            cur = {"heading": ln[3:].strip(), "body": []}
            blocks.append(cur)
        elif re.match(r"^# (?!#)", ln):
            cur = None                     # level-1 headings are never slides
        elif cur is not None:
            cur["body"].append(ln)
    return title, subtitle, blocks


def split_block(block, base: Path):
    figs, bullets, notes, layout, missing = [], [], [], None, []
    captions = []      # `**Figure N.**` lines, kept in document order and placed before the bullets
    para = []

    def flush_para():
        if para:
            notes.append(" ".join(s.strip() for s in para))
            para.clear()

    body = block["body"]
    i = 0
    while i < len(body):
        ln = body[i]
        s = ln.strip()
        m = LAYOUT_RE.search(s)
        if m:
            layout = m.group(1)
        elif not s or s == "---" or s.startswith("<!--"):
            flush_para()
        elif IMG_RE.search(s) and IMG_RE.sub("", s).strip() == "":
            flush_para()
            for m2 in IMG_RE.finditer(s):
                p = Path(m2.group(1))
                p = p if p.is_absolute() else (base / p)
                p = p.resolve()
                (figs if p.exists() else missing).append(p)
        elif s.startswith("- ") or s.startswith("* "):
            flush_para()
            item = s[2:].strip()
            while i + 1 < len(body) and body[i + 1].startswith("  ") and body[i + 1].strip() \
                    and not body[i + 1].strip().startswith(("- ", "* ")):
                i += 1
                item += " " + body[i].strip()
            bullets.append(item)
        elif CAPTION_RE.match(s):
            flush_para()
            cap = s          # keep the bold "Figure N." lead-in so the slide is citable like a paper figure
            while i + 1 < len(body) and body[i + 1].strip() and not body[i + 1].strip().startswith(("- ", "![", "<!--")):
                i += 1
                cap += " " + body[i].strip()
            captions.append(cap)
        else:
            para.append(s)
        i += 1
    flush_para()
    return figs, captions + bullets, notes, layout, missing


def pick_layout(n_fig, n_bul, figs, explicit):
    if explicit and explicit != "auto":
        return explicit
    if n_fig == 0:
        return "text-only"
    if n_fig == 1:
        return "figure-dominant" if n_bul else "single"
    if n_fig in (2, 3):
        amin = min(aspect_of(p) for p in figs)
        return f"{'vstack' if amin >= ASPECT_BREAKEVEN else 'hstack'}-{n_fig}"
    if n_fig == 4:
        return "grid-2x2"
    return None


# ---------------------------------------------------------------- emitting

def emit_slide(slide_id, layout, tag, color, title, figs, bullets, notes):
    L = [f"<!-- slide-id: {slide_id} -->", f"<!-- layout: {layout} -->"]
    if layout == "hstack-3":
        L.append("<!-- figures: " + ", ".join(map(str, figs)) + " -->")
    if tag:
        L.append(f'<!-- section-tag: "{tag}" color="{color}" -->')
    L += [f"## {title}", ""]
    L += [f"- {b}" for b in bullets]
    if bullets and figs:
        L.append("")
    shown = figs[:1] if layout == "hstack-3" else figs
    L += [f"![]({p})" for p in shown]
    if notes:
        L += ["", "::: notes", *notes, ":::"]
    return L


def build(src: Path, out: Path, section, layout_all, prefix, cover):
    title, subtitle, blocks = parse(src, section)
    base = src.parent
    lines = ["---", "---", ""]
    tech_notes, problems, slides = [], [], []

    for b in blocks:
        if TECH_RE.match(b["heading"]):
            tech_notes += [l.strip() for l in b["body"] if l.strip() and l.strip() != "---"]
            continue
        figs, bullets, notes, lay, missing = split_block(b, base)
        for m in missing:
            problems.append(f"MISSING figure in '{b['heading']}': {m}")
        if len(bullets) > MAX_BULLETS:
            notes = [f"- {x}" for x in bullets[MAX_BULLETS:]] + notes
            bullets = bullets[:MAX_BULLETS]
        explicit = lay or (layout_all if layout_all != "auto" else None)
        layout = pick_layout(len(figs), len(bullets), figs, explicit)
        if layout is None or layout not in KNOWN_LAYOUTS:
            problems.append(f"UNSUPPORTED layout/figure count in '{b['heading']}': "
                            f"{len(figs)} figures, layout={layout!r} - split the block or set "
                            f"<!-- layout: X --> ({', '.join(sorted(KNOWN_LAYOUTS))})")
            continue
        slides.append((b["heading"], layout, figs, bullets, notes))

    if problems:
        print("\n".join(problems), file=sys.stderr)
        print("Nothing written.", file=sys.stderr)
        return 2

    if cover:
        lines += ["<!-- slide-id: COVER -->", "<!-- layout: cover -->", f"## {title}", ""]
        if subtitle:
            lines.append(subtitle)
        if tech_notes:
            lines += ["", "::: notes", *tech_notes, ":::"]
        lines += ["", "---", ""]
    elif tech_notes and slides:
        h, lay, f, bu, no = slides[-1]
        slides[-1] = (h, lay, f, bu, no + tech_notes)

    index = []
    for k, (heading, layout, figs, bullets, notes) in enumerate(slides):
        color = COLORS[k % len(COLORS)]
        lines += emit_slide(f"S{k + 1:02d}", layout, prefix or None, color, heading, figs, bullets, notes)
        lines += ["", "---", ""]
        index.append({"title": heading, "layout": layout, "bullets": bullets,
                      "paths": [str(f) for f in figs]})

    while lines and lines[-1] in ("", "---"):
        lines.pop()
    out.write_text("\n".join(lines) + "\n")
    out.with_suffix(".index.json").write_text(json.dumps(index, indent=2) + "\n")
    print(f"storyboard: {out}\nindex:      {out.with_suffix('.index.json')}\n"
          f"slides:     {len(slides) + bool(cover)} ({'cover + ' if cover else ''}{len(slides)} content)")
    for s in index:
        print(f"  {s['layout']:<15} figs={len(s['paths'])} bullets={len(s['bullets'])}  {s['title'][:60]}")
    return 0


# ---------------------------------------------------------------- render

def render(storyboard: Path, engine: str = "pptx", pandoc: str | None = None):
    """Hand the storyboard to render_storyboard.py (the documented render path)."""
    pptx = storyboard.with_suffix(".pptx")
    outputs, slides = render_storyboard.render(storyboard, pptx, pandoc=pandoc,
                                               project_root=storyboard.parent, engine=engine)
    print(f"pptx:       {outputs[0]}  ({len(slides)} slides)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("-o", "--output", help="storyboard path (default: <source-stem>_slides_<dd-mm-yyyy>.md beside source)")
    ap.add_argument("--section", help="only convert this level-1 section, e.g. 'Summary' (legacy 'L1' also accepted)")
    ap.add_argument("--layout", default="auto", help="layout for every slide unless a block sets its own")
    ap.add_argument("--tag-prefix", default="", help="small top-right section label on every content slide, e.g. 'OSNAP'")
    ap.add_argument("--no-cover", action="store_true")
    ap.add_argument("--render", action="store_true", help="also render with render_storyboard.py")
    ap.add_argument("--engine", choices=["pptx", "pandoc"], default="pptx")
    ap.add_argument("--pandoc", help="only for --engine pandoc")
    ap.add_argument("--render-only", action="store_true",
                    help="SOURCE is already a storyboard (e.g. from assemble_figures.py --write): render it, convert nothing")
    a = ap.parse_args()
    if a.render_only:
        render(Path(a.source).expanduser().resolve(), a.engine, a.pandoc)
        return 0

    src = Path(a.source).expanduser().resolve()
    default = src.with_name(f"{src.stem}_slides_{_dt.date.today():%d-%m-%Y}.md")
    out = Path(a.output).expanduser().resolve() if a.output else default
    rc = build(src, out, a.section, a.layout, a.tag_prefix, not a.no_cover)
    if rc == 0 and a.render:
        render(out, a.engine, a.pandoc)
    return rc


if __name__ == "__main__":
    sys.exit(main())
