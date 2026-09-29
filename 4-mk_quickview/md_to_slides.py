#!/usr/bin/env python3
"""md_to_slides.py — figure-first markdown (quickview or topic-record L1) -> 6-ppt-create storyboard.

Part of the 4-mk_quickview skill ("share" step). Makes NO content decisions:
every `## ` block of the source becomes one slide, in source order, with the
figures, caption and bullets it already has. Rendering is 6-ppt-create's job;
`--render` only chains its documented steps (pandoc -> slide-count check ->
DATA BLOCK fill -> postprocess template).

  python md_to_slides.py SOURCE.md [-o OUT.md] [--section "L1"] [--layout auto]
                         [--tag-prefix OSNAP] [--no-cover] [--render]

Mapping (source -> slide):
  `# Title` + first paragraph      -> cover slide (unless --no-cover)
  `## Heading`                     -> one slide; heading -> section tag (Figure N / 2. prefixes kept)
  `![](fig)`                       -> figures (relative paths resolved from SOURCE's directory)
  `**Figure N.** caption`          -> first bullet (prefix stripped)
  `- bullet`                       -> bullets (max 3 on the slide; extras -> speaker notes)
  other paragraphs / links         -> speaker notes
  `<!-- layout: X -->` in a block  -> explicit layout for that slide (beats --layout and auto)
  `## Technical details` block     -> speaker notes of the cover (or last slide)

Exit codes: 0 ok, 2 unresolved figure path or unsupported figure count (nothing written).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

SKILLS = Path(__file__).resolve().parent.parent
TEMPLATE = SKILLS / "6-ppt-create" / "postprocess_template.py"
PANDOC = Path.home() / ".conda/envs/amoc/bin/pandoc"
COLORS = ["steelblue", "darkorange", "teal", "purple", "crimson"]
ASPECT_BREAKEVEN = 2.3           # same threshold as 5-ppt-design / 6-ppt-create
ASPECT_FALLBACK = 1.6
TITLE_MAX = 65
MAX_BULLETS = 3
KNOWN_LAYOUTS = {"text-only", "single", "figure-dominant", "vstack-2", "vstack-3",
                 "hstack-2", "hstack-3", "grid-2x2"}
TECH_RE = re.compile(r"^technical details\b", re.I)
IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)(\{[^}]*\})?")
CAPTION_RE = re.compile(r"^\*\*Figure\s+\d+[a-z]?\.\*\*\s*", re.I)
LAYOUT_RE = re.compile(r"<!--\s*layout:\s*([\w-]+)\s*-->")


GREEK = {r"\\sigma": "σ", r"\\Psi": "Ψ", r"\\psi": "ψ", r"\\alpha": "α", r"\\beta": "β",
         r"\\rho": "ρ", r"\\Delta": "Δ", r"\\ge": "≥", r"\\le": "≤", r"\\gtrsim": "≳",
         r"\\approx": "≈", r"\\pm": "±", r"\\times": "×", r"\\to": "→",
         r"\\lesssim": "≲", r"\\sim": "~", r"\\gamma": "γ", r"\\tau": "τ", r"\\mu": "μ",
         r"\\partial": "∂", r"\\infty": "∞", r"\\cdot": "·", r"\\leftrightarrow": "↔"}


def plain(s: str, strip_md: bool = True) -> str:
    """Inline TeX -> Unicode text.

    Used for section tags (truncated and matched against pptx titles) and for slide
    bullets/notes: pandoc wraps any text shape holding OMML math in mc:AlternateContent,
    which python-pptx cannot see, so 6-ppt-create's post-processing cannot place that
    text band. The markdown source keeps its TeX; only the slide copy is flattened.
    """
    def conv(m):
        t = m.group(1)
        t = re.sub(r"\{\\rm\s+([^}]*)\}", r"\1", t)
        t = re.sub(r"\\math(?:rm|bf|it)\{([^}]*)\}", r"\1", t)
        for k, v in GREEK.items():
            t = re.sub(k + r"(?![A-Za-z])", v, t)
        t = re.sub(r"_\{([^}]*)\}", r"_\1", t)
        t = re.sub(r"\^\{([^}]*)\}", r"^\1", t)
        t = re.sub(r"\\(?:bar|hat|tilde|overline|left|right|,|;|!|quad)\s*", "", t)
        t = re.sub(r"\\(?:text|operatorname)\{([^}]*)\}", r"\1", t)
        return t.replace("{", "").replace("}", "").replace("\\", "")
    s = re.sub(r"\$([^$]+)\$", conv, s)
    return s.replace("**", "").replace("`", "") if strip_md else s


def truncate(s: str, n: int = TITLE_MAX) -> str:
    if len(s) <= n:
        return s
    cut = s[:n - 1].rsplit(" ", 1)[0].rstrip(" ·—-,;:")
    return cut + "…"


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
    """Keep only lines under the level-1 heading that starts with `section` (e.g. 'L1')."""
    out, inside = [], False
    for ln in lines:
        if re.match(r"^# (?!#)", ln):
            inside = ln[2:].strip().lower().startswith(section.lower())
            continue
        if inside:
            out.append(ln)
    if not out:
        raise SystemExit(f"ERROR: no '# {section}…' section found")
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

def img(p, width=None):
    return f"![]({p})" + (f'{{width="{width}"}}' if width else "")


def emit_slide(layout, tag, color, figs, bullets, notes, fig_height):
    L = [f"<!-- layout: {layout} -->"]
    if layout == "hstack-3":
        L.append("<!-- figures: " + ", ".join(map(str, figs)) + " -->")
    if fig_height:
        L.append(f"<!-- figure-height: {fig_height} -->")
    L += [f'<!-- section-tag: "{tag}" color="{color}" -->', f"## {tag}", ""]
    bl = [f"- {b}" for b in bullets]
    if layout == "text-only":
        L += bl
    elif layout == "single":
        a = aspect_of(figs[0])
        L += [img(figs[0], "80%" if a > 1.5 else "70%")]
    elif layout == "figure-dominant":
        L += [":::: {.columns}", '::: {.column width="30%"}', *bl, "", ":::",
              '::: {.column width="70%"}', img(figs[0], "100%"), "", ":::", "::::"]
    elif layout in ("vstack-2", "vstack-3"):
        L += [img(f, "80%") for f in figs]
    elif layout == "hstack-2":
        L += [":::: {.columns}"]
        for f in figs:
            L += ['::: {.column width="50%"}', img(f, "100%"), ":::"]
        L += ["::::"]
    elif layout == "hstack-3":
        L += [img(figs[0], "30%")]
    elif layout == "grid-2x2":
        L += [":::: {.columns}"]
        for col in (figs[:2], figs[2:]):
            L += ['::: {.column width="50%"}', *[img(f, "100%") for f in col], ":::"]
        L += ["::::"]
    if notes:
        L += ["", "::: notes", *notes, ":::"]
    return L


def build(src: Path, out: Path, section, layout_all, prefix, cover):
    title, subtitle, blocks = parse(src, section)
    base = src.parent
    lines = ["---", "---", ""]
    index = {"storyboard": str(out), "pptx": str(out.with_suffix(".pptx")),
             "bullet_placeholders": False, "source": str(src), "slides": []}
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
        if len(figs) > 1 and bullets:
            # pandoc's pptx writer keeps only ONE picture when text and several pictures share a
            # slide, so a multi-figure slide can carry no visible text.
            caps = [x for x in bullets if CAPTION_RE.match(x)]
            rest = [x for x in bullets if not CAPTION_RE.match(x)]
            if explicit is None:
                # companion figures: one slide per figure, each with its own `**Figure N.**` caption;
                # shared bullets stay on the first of them
                n = len(figs)
                per = caps if len(caps) == n else [None] * n
                for i, f in enumerate(figs):
                    bl = ([per[i]] if per[i] else []) + (rest if i == 0 else [])
                    if i == 0 and len(caps) != n:
                        bl = caps + rest
                    head = b["heading"] if i == 0 else f"{b['heading']} (cont. {i + 1}/{n})"
                    lay1 = pick_layout(1, len(bl[:MAX_BULLETS]), [f], None)
                    slides.append((head, lay1, [f], bl[:MAX_BULLETS],
                                   (notes if i == 0 else []) + ([f"- {x}" for x in bl[MAX_BULLETS:]])))
                continue
            print(f"WARNING: '{b['heading']}': {len(figs)} figures with explicit layout {explicit}; "
                  f"captions/bullets moved to speaker notes (pandoc keeps one picture per text slide)",
                  file=sys.stderr)
            notes = [f"- {x}" for x in bullets] + notes
            bullets = []
        layout = pick_layout(len(figs), len(bullets), figs, explicit)
        if layout is None or layout not in KNOWN_LAYOUTS:
            problems.append(f"UNSUPPORTED layout/figure count in '{b['heading']}': "
                            f"{len(figs)} figures, layout={layout!r} — split the block or set "
                            f"<!-- layout: X --> ({', '.join(sorted(KNOWN_LAYOUTS))})")
            continue
        slides.append((b["heading"], layout, figs, bullets, notes))

    if problems:
        print("\n".join(problems), file=sys.stderr)
        print("Nothing written.", file=sys.stderr)
        return 2

    idx0 = 0
    if cover:
        lines += ["<!-- Slide 1 (cover) -->", f"## {truncate(plain(title))}", ""]
        if subtitle:
            lines.append(plain(subtitle, False))
        if tech_notes:
            lines += ["", "::: notes", *[plain(x, False) for x in tech_notes], ":::"]
        lines += ["", "---", ""]
        idx0 = 1
    elif tech_notes and slides:
        h, lay, f, bu, no = slides[-1]
        slides[-1] = (h, lay, f, bu, no + tech_notes)

    for k, (heading, layout, figs, bullets, notes) in enumerate(slides):
        tag = truncate(plain(f"{prefix} · {heading}" if prefix else heading))
        color = COLORS[k % len(COLORS)]
        fh = "13/14" if (figs and not bullets) else None
        lines += [f"<!-- Slide {idx0 + k + 1} -->"]
        lines += emit_slide(layout, tag, color, figs, [plain(x, False) for x in bullets],
                            [plain(x, False) for x in notes], fh)
        lines += ["", "---", ""]
        num, den = (fh.split("/") if fh else (None, None))
        index["slides"].append({
            "idx": idx0 + k, "name": heading, "tag": [tag, color], "layout": layout,
            "figures": [str(f) for f in figs] or [None],
            "aspects": [round(aspect_of(f), 3) for f in figs],
            "n_bullets": len(bullets),
            **({"figure_height": round(int(num) / int(den), 4)} if fh else {}),
        })

    # drop the trailing separator
    while lines and lines[-1] in ("", "---"):
        lines.pop()
    out.write_text("\n".join(lines) + "\n")
    index["n_slides"] = idx0 + len(slides)
    out.with_suffix(".index.json").write_text(json.dumps(index, indent=2) + "\n")
    print(f"storyboard: {out}\nindex:      {out.with_suffix('.index.json')}\n"
          f"slides:     {index['n_slides']} ({'cover + ' if cover else ''}{len(slides)} content)")
    for s in index["slides"]:
        print(f"  [{s['idx']}] {s['layout']:<15} figs={len([f for f in s['figures'] if f])} "
              f"bullets={s['n_bullets']}  {s['tag'][0]}")
    return 0


# ---------------------------------------------------------------- render

def fill_datablock(index: dict) -> str:
    tags, layouts, figs, heights = {}, {}, {}, {}
    for s in index["slides"]:
        i = s["idx"]
        tags[i] = tuple(s["tag"])
        layouts.setdefault(s["layout"], []).append(i)
        f = [x for x in s["figures"] if x]
        if f:
            figs[i] = f if len(f) > 1 else f[0]
        if s.get("figure_height"):
            heights[i] = s["figure_height"]
    for key in ("figure-dominant", "vstack-3", "hstack-3", "table"):
        layouts.setdefault(key, [])
    start = "# DATA BLOCK — fill in these values, nothing else"
    end = "# ============================================================\n\nCOLOR_MAP"
    tpl = TEMPLATE.read_text()
    if start not in tpl or end not in tpl:
        raise SystemExit(f"ERROR: DATA BLOCK markers not found in {TEMPLATE}")
    L = [start, "# ============================================================",
         f"PPTX_PATH = {index['pptx']!r}", "", "SECTION_TAGS = {"]
    L += [f"    {i}: {t!r}," for i, t in sorted(tags.items())]
    L += ["}", "", "LAYOUT_MAP = {"]
    L += [f"    {k!r}: {sorted(v)!r}," for k, v in sorted(layouts.items())]
    L += ["}", "", "FIGURES = {"]
    L += [f"    {i}: {v!r}," for i, v in sorted(figs.items())]
    L += ["}", "", "FIGURE_HEIGHT_OVERRIDE = {"]
    L += [f"    {i}: {v!r}," for i, v in sorted(heights.items())]
    L += ["}", "", f"BULLET_PLACEHOLDERS = {bool(index.get('bullet_placeholders', False))!r}", "",
          "STAMP_IDS = True", "SLIDE_IDS = {", "}",
          f"PROJECT_ROOT = {index.get('project_root')!r}"]
    head, rest = tpl.split(start, 1)
    _, tail = rest.split(end, 1)
    return head + "\n".join(L) + "\n" + end + tail


def render(out: Path):
    index = json.loads(out.with_suffix(".index.json").read_text())
    pptx = Path(index["pptx"])
    pandoc = str(PANDOC) if PANDOC.exists() else "pandoc"
    subprocess.run([pandoc, str(out), f"--resource-path={out.parent}", "-o", str(pptx)], check=True)
    from pptx import Presentation
    prs = Presentation(str(pptx))
    titles = [(s.shapes.title.text_frame.text if s.shapes.title is not None else None) for s in prs.slides]
    n_expected = index.get("n_slides", len(index["slides"]))
    if len(titles) != n_expected:
        for i, t in enumerate(titles):
            print(f"  pptx[{i}] {t}", file=sys.stderr)
        raise SystemExit(f"ERROR: pandoc produced {len(titles)} slides, storyboard has "
                         f"{n_expected} — stop, do not post-process (see 6-ppt-create Phase 1.3)")
    for s in index["slides"]:
        if titles[s["idx"]] != s["tag"][0]:
            raise SystemExit(f"ERROR: slide {s['idx']} title {titles[s['idx']]!r} != tag {s['tag'][0]!r}")
    pp = out.with_name(out.stem + "_postprocess.py")
    pp.write_text(fill_datablock(index))
    subprocess.run([sys.executable, str(pp)], check=True, cwd=str(out.parent))
    print(f"pptx:       {pptx}  ({len(titles)} slides, titles verified)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("-o", "--output", help="storyboard path (default: <source-stem>_slides_<dd-mm-yyyy>.md beside source)")
    ap.add_argument("--section", help="only convert this level-1 section, e.g. 'L1' of a topic record")
    ap.add_argument("--layout", default="auto", help="layout for every slide unless a block sets its own")
    ap.add_argument("--tag-prefix", default="", help="section-tag prefix, e.g. 'OSNAP'")
    ap.add_argument("--no-cover", action="store_true")
    ap.add_argument("--render", action="store_true", help="also run pandoc + 6-ppt-create post-processing")
    ap.add_argument("--render-only", action="store_true",
                    help="SOURCE is already a storyboard with a sibling .index.json "
                         "(e.g. from assemble_figures.py --write): render it, convert nothing")
    a = ap.parse_args()
    if a.render_only:
        render(Path(a.source).expanduser().resolve())
        return 0

    src = Path(a.source).expanduser().resolve()
    default = src.with_name(f"{src.stem}_slides_{_dt.date.today():%d-%m-%Y}.md")
    out = Path(a.output).expanduser().resolve() if a.output else default
    rc = build(src, out, a.section, a.layout, a.tag_prefix, not a.no_cover)
    if rc == 0 and a.render:
        render(out)
    return rc


if __name__ == "__main__":
    sys.exit(main())
