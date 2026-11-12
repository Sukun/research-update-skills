#!/usr/bin/env python3
"""merge_storyboard.py — fold a hand-edited deck's text back into its storyboard.

The storyboard keeps everything the deck does not show (annotations, comments, Markdown
emphasis, LaTeX). A slide's title, body, notes or figure list is rewritten only when the
deck's version differs from what the storyboard would render. Slides follow the deck's
order; slides deleted in the deck are dropped; duplicated slides copy their original.
Positions are not written here; they go to <name>.layout.json (layout_record.py).
"""
from __future__ import annotations

import hashlib
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "6-ppt-create"))
import build_pptx  # noqa: E402
import render_storyboard  # noqa: E402
from latex_text import convert_math  # noqa: E402

COLORS = ["steelblue", "darkorange", "teal", "purple", "crimson"]
FW_NOTES_PREFIX = "Also on the slide:"
IMG_LINE = re.compile(r"^\s*!\[[^\]]*\]\((?:<[^>]+>|[^\s)]+)\)(?:\{[^}]*\})?\s*$")
FIG_COMMENT = re.compile(r"^\s*<!--\s*(figures|unresolved-figure)\b.*-->\s*$")
NOTES_OPEN = re.compile(r"^::: ?(?:notes|\{\.notes\})\s*$")
LAYOUTS = render_storyboard.LAYOUTS


# ------------------------------------------------------------ normalising

def plain(text):
    """What the renderer puts on the slide for a line of storyboard text."""
    text = text.replace("**", "")
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"(?<![\w*])\*([^*\s][^*]*)\*(?![\w*])", r"\1", text)
    return " ".join(convert_math(text, []).split())


def squash(text):
    return " ".join((text or "").split())


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def split_spill(notes):
    """figure-full-width moves extra bullets to the top of Notes; separate them again."""
    lines = (notes or "").splitlines()
    if not lines or lines[0].strip() != FW_NOTES_PREFIX:
        return [], notes or ""
    spill, i = [], 1
    while i < len(lines) and lines[i].strip():
        spill.append(lines[i].strip())
        i += 1
    return spill, "\n".join(lines[i + 1:])


def fig_ref(path, md_dir, root):
    path = Path(path).resolve()
    for base in (md_dir, root):
        if base:
            try:
                return str(path.relative_to(Path(base).resolve()))
            except ValueError:
                pass
    try:
        rel = os.path.relpath(path, md_dir)
        if not rel.startswith(".." + os.sep + ".." + os.sep):
            return rel
    except ValueError:
        pass
    return str(path)


def deck_fig_path(fig, root):
    if fig.get("extracted"):
        return Path(fig["extracted"])
    src = fig.get("source")
    if not src:
        return None
    p = Path(src)
    return p if p.is_absolute() or not root else Path(root) / p


# ------------------------------------------------------------ block surgery

def _regions(lines):
    """Index sets: lines inside ::: notes (incl. fences) and inside HTML comments."""
    notes, comments, in_notes, in_comment = set(), set(), False, False
    for i, line in enumerate(lines):
        s = line.strip()
        if in_comment:
            comments.add(i)
            in_comment = "-->" not in line
            continue
        if in_notes:
            notes.add(i)
            if re.fullmatch(r":{3,}", s):
                in_notes = False
            continue
        if NOTES_OPEN.match(s):
            notes.add(i)
            in_notes = True
            continue
        if s.startswith("<!--"):
            comments.add(i)
            in_comment = "-->" not in line
    return notes, comments


def _heading_index(lines):
    return next(i for i, line in enumerate(lines) if line.startswith("## "))


def set_title(lines, title):
    lines[_heading_index(lines)] = "## " + title


def set_annotation(lines, name, value):
    pat = re.compile(r"^\s*<!--\s*" + re.escape(name) + r":.*-->\s*$")
    for i, line in enumerate(lines):
        if pat.match(line):
            lines[i] = f"<!-- {name}: {value} -->"
            return
    lines.insert(_heading_index(lines), f"<!-- {name}: {value} -->")


def _is_body(line):
    s = line.strip()
    return bool(s) and s != "---" and not line.startswith("## ") and not IMG_LINE.match(line) \
        and not s.startswith("|") and not re.match(r"^:{3,}", s)


def set_body(lines, paras):
    notes, comments = _regions(lines)
    h = _heading_index(lines)
    keep = [line for i, line in enumerate(lines)
            if i <= h or i in notes or i in comments or not _is_body(line)]
    new = [("  " if level else "") + "- " + text for level, text in paras]
    h = _heading_index(keep)
    j = h + 1
    while j < len(keep) and not keep[j].strip():
        j += 1
    block = [""] + new + ([""] if new else [])
    lines[:] = keep[:h + 1] + block + keep[j:]


def set_notes(lines, notes_text):
    region, _ = _regions(lines)
    if region:
        start, end = min(region), max(region)
        del lines[start:end + 1]
        at = start
    else:
        at = len(lines)
        while at > 0 and (not lines[at - 1].strip() or lines[at - 1].strip() == "---"):
            at -= 1
    if notes_text.strip():
        lines[at:at] = ["", "::: notes"] + notes_text.strip().splitlines() + [":::"]


def set_figures(lines, refs, layout):
    notes, comments = _regions(lines)
    kept = [line for i, line in enumerate(lines)
            if i in notes or not (IMG_LINE.match(line) or FIG_COMMENT.match(line))]
    lines[:] = kept
    notes, _ = _regions(lines)
    at = min(notes) if notes else len(lines)
    while at > 0 and not lines[at - 1].strip():
        at -= 1
    new = []
    if layout in ("hstack-3", "vstack-3") and len(refs) == 3:
        new.append("<!-- figures: " + ", ".join(refs) + " -->")
        refs = refs[:1]
    new += [f"![]({r})" for r in refs]
    lines[at:at] = [""] + new if new else []
    set_annotation(lines, "layout", layout)


def tidy(lines):
    """Strip the slide separator and surplus blank lines at either end."""
    while lines and (not lines[-1].strip() or lines[-1].strip() == "---"):
        lines.pop()
    while lines and not lines[0].strip():
        lines.pop(0)
    out = []
    for line in lines:
        if not line.strip() and out and not out[-1].strip():
            continue
        out.append(line)
    return out


# ------------------------------------------------------------ new slides

def new_block(s, md_dir, root, color="grey"):
    figs = s.get("figures", [])
    layout = s.get("layout") if s.get("layout") in LAYOUTS else ("text-only" if not figs else "custom")
    tparts = [t.strip() for t in (s.get("title") or s["slide_id"]).splitlines() if t.strip()]
    title = tparts[0]
    lines = [f"<!-- slide-id: {s['slide_id']} -->", f"<!-- layout: {layout} -->"]
    if s.get("section"):
        lines.append(f'<!-- section-tag: "{s["section"]}" color="{color}" -->')
    lines += [f"## {title}", ""]
    lines += [("  " if lv else "") + "- " + t for lv, t in [(0, x) for x in tparts[1:]] + list(s.get("takeaway_paras") or [])]
    refs = []
    for f in figs:
        p = deck_fig_path(f, root)
        if p is None:
            continue
        if f.get("resolved_by") == "unresolved":
            lines.append(f"<!-- unresolved-figure: {f['figure_id']} sha256={f['sha256'][:16]} origin=manual-insert -->")
        refs.append(fig_ref(p, md_dir, root))
    if refs:
        tmp = list(lines)
        set_figures(tmp, refs, layout)
        lines = tmp
    if s.get("notes"):
        lines += ["", "::: notes"] + s["notes"].splitlines() + [":::"]
    return lines


def assemble(preamble, blocks):
    out = []
    for n, block in enumerate(blocks, 1):
        block = [line for line in block if not re.match(r"^\s*<!--\s*Slide\s+\d+\s*-->\s*$", line)]
        out.append("\n".join([f"<!-- Slide {n} -->"] + block))
    pre = preamble.rstrip()
    return (pre + "\n\n" if pre else "") + "\n\n---\n\n".join(out) + "\n"


def new_storyboard(deck, md, root):
    md = Path(md).resolve()
    colors = {}
    blocks = []
    for s in deck["slides"]:
        key = s.get("section") or s["slide_id"]
        colors.setdefault(key, COLORS[len(colors) % len(COLORS)])
        blocks.append(new_block(s, md.parent, root, colors[key]))
    return assemble("---\n---", blocks)


# ------------------------------------------------------------ merge

def merge(md, deck, root=None):
    """Return (new storyboard text, [change lines])."""
    md = Path(md).resolve()
    text = md.read_text()
    slides = render_storyboard.parse_storyboard(md, root)
    first = text.find(slides[0]["block"])
    preamble = text[:first] if first > 0 else ""
    by_id = {s["id"]: s for s in slides}
    changes, blocks = [], []

    for d in deck["slides"]:
        sid = d["slide_id"]
        story = by_id.get(sid) or by_id.get(d.get("duplicate_of"))
        if story is None:
            blocks.append(new_block(d, md.parent, root))
            changes.append(f"{sid}: new slide in the deck, added")
            continue
        lines = story["block"].rstrip("\n").splitlines()
        what = []
        if story is not by_id.get(sid):
            set_annotation(lines, "slide-id", sid)
            what.append(f"duplicate of {story['id']}")
        elif story.get("generated_id"):
            set_annotation(lines, "slide-id", sid)

        # title (a heading is one line: extra lines typed into the title box join the body)
        tparts = [t.strip() for t in (d.get("title") or "").splitlines() if t.strip()]
        extra = [(0, t) for t in tparts[1:]]
        if tparts and squash(tparts[0]) != plain(story["title"]):
            set_title(lines, tparts[0])
            what.append("title")
        if extra:
            what.append(f"{len(extra)} extra title line(s) kept as body text")

        # body (+ bullets that figure-full-width moved to Notes, + caption)
        content = build_pptx.split_block(story["block"], [])
        md_body = [plain(p["text"]) for p in content["paragraphs"]]
        spill, deck_notes = split_spill(d.get("notes"))
        deck_paras = extra + list(d.get("takeaway_paras") or []) + [(0, t) for t in spill]
        deck_body = [plain(t) for _, t in deck_paras]
        if sorted(md_body) != sorted(deck_body) and " ".join(md_body) != " ".join(deck_body):
            set_body(lines, deck_paras)
            what.append("body")

        # notes
        md_notes = squash(convert_math("\n".join(content["notes"]), []))
        if squash(deck_notes) != md_notes:
            set_notes(lines, deck_notes)
            what.append("notes")

        # figures
        md_sha = sorted(sha_file(p) for p in story["paths"])
        deck_sha = sorted(f["sha256"] for f in d.get("figures", []))
        if md_sha != deck_sha:
            refs, missing = [], []
            for f in sorted(d.get("figures", []), key=lambda f: f["z"]):
                p = deck_fig_path(f, root)
                if p is None or not Path(p).is_file():
                    missing.append(f["figure_id"])
                    continue
                refs.append(fig_ref(p, md.parent, root))
                if f.get("resolved_by") == "unresolved":
                    lines.insert(_heading_index(lines) + 1,
                                 f"<!-- unresolved-figure: {f['figure_id']} sha256={f['sha256'][:16]} origin=manual-insert -->")
            layout = story["layout"]
            if len(refs) != len(story["paths"]):
                layout = d.get("layout") if d.get("layout") in LAYOUTS else "custom"
            set_figures(lines, refs, layout)
            what.append("figures" + (f" (no file for {', '.join(missing)})" if missing else ""))

        blocks.append(tidy(lines))
        if what:
            changes.append(f"{sid}: " + ", ".join(what))

    kept = {d["slide_id"] for d in deck["slides"]} | {d.get("duplicate_of") for d in deck["slides"]}
    for s in slides:
        if s["id"] not in kept:
            changes.append(f"{s['id']}: deleted in the deck, removed")
    order_md = [s["id"] for s in slides if s["id"] in kept]
    order_deck = [d["slide_id"] for d in deck["slides"] if d["slide_id"] in by_id]
    if order_md != order_deck:
        changes.append("slide order changed")
    return assemble(preamble, blocks), changes
