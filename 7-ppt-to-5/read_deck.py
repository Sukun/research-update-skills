#!/usr/bin/env python3
"""read_deck.py — hand-edited PPTX -> the storyboard it came from + its layout file.

Revise (stamped deck from 6-ppt-create):
  python read_deck.py EDITED.pptx --storyboard NAME.md [--project-root DIR]
      text edits are merged into NAME.md (old copy kept as NAME.md.bak);
      positions, sizes, crops and font sizes go to NAME.layout.json.
      Newer edit wins: a slide edited only in the deck takes the deck text, edited only in
      the storyboard keeps it, edited in both takes the newer file's version.
  --layout-only keeps NAME.md as it is; --dry-run only reports.

Bootstrap (legacy unstamped deck, once):
  python read_deck.py --bootstrap LEGACY.pptx -o NAME.md [--project-root DIR]
      the deck is the truth; fresh ids S001, S002, ...; writes NAME.md + NAME.layout.json.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

from pptx import Presentation

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "6-ppt-create"))

SCHEMA_VERSION = 1
EMU_IN = 914400
PICTURE, TEXT_BOX, TABLE = 13, 17, 19


# ------------------------------------------------------------------ metadata

def read_meta(shape):
    """Return the stamped payload: descr JSON preferred, shape.name as fallback."""
    try:
        descr = shape._element._nvXxPr.cNvPr.get("descr")
    except Exception:
        descr = None
    if descr:
        try:
            d = json.loads(descr)
            if isinstance(d, dict) and "role" in d:
                return d
        except Exception:
            pass
    name = getattr(shape, "name", "") or ""
    if name.startswith("sb:"):
        out = {}
        for part in name[3:].split("|"):
            if "=" in part:
                k, v = part.split("=", 1)
                out[{"slide": "sid"}.get(k, k)] = v
        if "role" in out:
            return out
    return {}


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


# ---------------------------------------------------------------- extraction

def text_of(shape):
    return shape.text_frame.text.strip() if shape.has_text_frame else ""


def para_markdown(paragraph):
    """Paragraph text with explicitly bold runs written as **bold**."""
    out, bold = [], []

    def flush():
        if bold:
            text = "".join(bold)
            lead, core, trail = text[:len(text) - len(text.lstrip())], text.strip(), text[len(text.rstrip()):]
            out.append(f"{lead}**{core}**{trail}")
            bold.clear()

    for run in paragraph.runs:
        if run.font.bold and run.text.strip():
            bold.append(run.text)
        else:
            flush()
            out.append(run.text)
    flush()
    return "".join(out).strip() or paragraph.text.strip()


def is_chip_like(shape):
    """Bootstrap-only heuristic: the section chip is a filled bold textbox at the top."""
    if shape.shape_type != TEXT_BOX or not text_of(shape):
        return False
    if shape.top is None or shape.top / EMU_IN >= 0.25:
        return False
    try:
        if shape.fill.type is not None and shape.fill.type != 5:  # 5 = background
            return True
    except Exception:
        pass
    return True


def extract_slide(slide, idx, bootstrap):
    chip = title_ph = takeaway = None
    anchor_sid = None
    stamped = False

    for sh in slide.shapes:
        if not sh.has_text_frame or not text_of(sh):
            continue
        meta = read_meta(sh)
        role = meta.get("role")
        if role:
            stamped = True
            if meta.get("sid"):
                anchor_sid = meta["sid"]
            if role == "section":
                chip = sh
            elif role == "title":
                title_ph = sh
            elif role == "takeaway":
                takeaway = sh

    if stamped and takeaway is None:
        # Stamped slide that gained a NEW unstamped text shape in PowerPoint
        # (user inserted a textbox). Adopt the first such shape as the takeaway
        # rather than silently dropping what they typed.
        for sh in slide.shapes:
            if not sh.has_text_frame or not text_of(sh):
                continue
            if sh in (chip, title_ph) or read_meta(sh).get("role"):
                continue
            takeaway = sh
            break

    if not stamped:
        # Unstamped slide: fall back to the coordinate heuristic (bootstrap path).
        for sh in slide.shapes:
            if not sh.has_text_frame or not text_of(sh):
                continue
            if chip is None and is_chip_like(sh):
                chip = sh
            elif sh.is_placeholder and sh.placeholder_format.idx == 0 and title_ph is None:
                title_ph = sh
            elif takeaway is None:
                takeaway = sh

    # Decks from the python-pptx engine keep the title in its placeholder and the
    # section as a small label (chip); legacy decks stored "title · section" in the chip.
    title_shape = title_ph or chip
    title = text_of(title_shape) if title_shape is not None else None
    if title_ph is not None and chip is not None:
        section = text_of(chip)
    else:
        parts = [p.strip() for p in title.split("·")] if title else []
        section = parts[1] if len(parts) >= 2 else None

    figs, opaque = [], []
    for z, sh in enumerate(sh for sh in slide.shapes):
        if sh.shape_type != PICTURE:
            if sh.shape_type in (TABLE,) or (not sh.has_text_frame and sh.shape_type != TEXT_BOX):
                if sh.shape_type != PICTURE and sh is not chip:
                    opaque.append({"shape_type": str(sh.shape_type), "name": sh.name})
            continue
        try:
            sha = sha256_bytes(sh.image.blob)
        except Exception:
            opaque.append({"shape_type": "PICTURE(unreadable)", "name": sh.name})
            continue
        meta = read_meta(sh)
        crop = [round(float(getattr(sh, f"crop_{s}", 0.0) or 0.0), 5)
                for s in ("left", "right", "top", "bottom")]
        fig = {"figure_id": meta.get("fid"), "source": meta.get("src"), "sha256": sha,
               "x": None, "y": None, "w": None, "h": None, "z": len(figs)}
        figs.append((fig, sh, crop))

    notes = ""
    try:
        notes = (slide.notes_slide.notes_text_frame.text or "").strip()
    except Exception:
        pass

    paras = []
    if takeaway is not None:
        paras = [(p.level, para_markdown(p)) for p in takeaway.text_frame.paragraphs if p.text.strip()]
    adopted = takeaway is not None and stamped and not read_meta(takeaway).get("role")
    return {"chip": chip, "anchor_sid": anchor_sid, "stamped": stamped,
            "title": title, "section": section,
            "takeaway": text_of(takeaway) if takeaway is not None else None,
            "takeaway_paras": paras, "adopted_textbox": adopted,
            "notes": notes or None, "figures": figs, "opaque": opaque}


def infer_layout(figs):
    n = len(figs)
    if n == 0:
        return "text-only"
    if n == 1:
        return "single"
    xs = [f["x"] + f["w"] / 2 for f in figs]
    ys = [f["y"] + f["h"] / 2 for f in figs]
    horizontal = (max(xs) - min(xs)) > (max(ys) - min(ys))
    if n in (2, 3):
        return f"{'hstack' if horizontal else 'vstack'}-{n}"
    if n == 4:
        return "grid-2x2"
    if n == 6:
        return "grid-2x3"
    return "custom"


# --------------------------------------------------------------- resolution

def load_registry(deck_dir):
    p = Path(deck_dir) / "figure_registry.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return {}


def scan_plots(root):
    """sha256 -> path, over every image under the project root's plots/ trees."""
    out = {}
    if not root:
        return out
    root = Path(root)
    for pat in ("plots/**/*.png", "plots/**/*.jpg", "*.png"):
        for f in root.glob(pat):
            if f.is_file():
                try:
                    out.setdefault(sha256_bytes(f.read_bytes()), f)
                except Exception:
                    pass
    return out


def resolve_figure(fig, registry, disk, root, unresolved_map, counter):
    """stamped src (verified) -> registry -> plots scan -> unresolved_manual_NN."""
    sha = fig["sha256"]
    src = fig.get("source")
    if src:
        p = (Path(root) / src) if (root and not Path(src).is_absolute()) else Path(src)
        if p.exists():
            if sha256_bytes(p.read_bytes()) == sha:
                return fig["figure_id"] or p.stem, src, "stamped"
            return fig["figure_id"] or p.stem, src, "refreshed"  # file re-plotted
    ent = registry.get(sha)
    if ent and ent.get("source"):
        return ent.get("figure_id") or Path(ent["source"]).stem, ent["source"], "registry"
    if sha in disk:
        p = disk[sha]
        try:
            rel = str(p.resolve().relative_to(Path(root).resolve())) if root else str(p)
        except Exception:
            rel = str(p)
        return fig["figure_id"] or p.stem, rel, "scan"
    if sha in unresolved_map:
        return unresolved_map[sha], None, "unresolved"
    counter[0] += 1
    name = f"unresolved_manual_{counter[0]:02d}"
    unresolved_map[sha] = name
    return name, None, "unresolved"


# --------------------------------------------------------------------- read

def read(pptx, root=None, bootstrap=False, unresolved_map=None, extract_dir=None):
    """Current state of the deck as a dict (text + figures). Nothing is written except
    unresolved pictures, which are extracted to `extract_dir` when given."""
    pptx = Path(pptx).resolve()
    prs = Presentation(pptx)
    slide_w, slide_h = prs.slide_width, prs.slide_height
    unresolved_map = dict(unresolved_map or {})
    counter = [max([int(v.rsplit("_", 1)[1]) for v in unresolved_map.values()
                    if v.startswith("unresolved_manual_")] or [0])]
    registry = load_registry(pptx.parent)
    disk = scan_plots(root)

    slides, seen_ids, n_unstamped = [], set(), 0
    for idx, slide in enumerate(prs.slides):
        raw = extract_slide(slide, idx, bootstrap)
        if not raw["stamped"]:
            n_unstamped += 1
        figs = []
        for fig, sh, crop in raw["figures"]:
            fig["x"] = round((sh.left or 0) / slide_w, 4)
            fig["y"] = round((sh.top or 0) / slide_h, 4)
            fig["w"] = round((sh.width or 0) / slide_w, 4)
            fig["h"] = round((sh.height or 0) / slide_h, 4)
            fid, src, how = resolve_figure(fig, registry, disk, root, unresolved_map, counter)
            fig["figure_id"], fig["source"], fig["resolved_by"] = fid, src, how
            if any(crop):
                fig["crop"] = crop
            if how == "unresolved" and extract_dir:
                ext = (sh.image.ext or "png").lower()
                target = Path(extract_dir) / f"{fid}.{ext}"
                if not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(sh.image.blob)
                fig["extracted"] = str(target)
            figs.append(fig)

        sid = raw["anchor_sid"]
        if bootstrap or not sid:
            sid = f"S{idx + 1:03d}"
        base, k = sid, 0
        while sid in seen_ids:            # duplicated slide: the stamp was copied verbatim
            k += 1
            sid = f"{base}-d{k}"
        seen_ids.add(sid)

        entry = {"slide_id": sid, "order": idx, "title": raw["title"],
                 "section": raw["section"], "takeaway": raw["takeaway"],
                 "takeaway_paras": raw["takeaway_paras"],
                 "notes": raw["notes"], "layout": infer_layout(figs), "figures": figs,
                 "stamped": raw["stamped"]}
        if k:
            entry["duplicate_of"] = base
        if raw["adopted_textbox"]:
            entry["adopted_textbox"] = True
        if raw["opaque"]:
            entry["opaque_shapes"] = raw["opaque"]
        slides.append(entry)

    return {"schema_version": SCHEMA_VERSION, "deck_id": pptx.stem,
            "generated": _dt.date.today().isoformat(),
            "project_root": str(root) if root else None, "source_pptx": pptx.name,
            "slides": slides, "unresolved": unresolved_map, "n_unstamped": n_unstamped}


def report(deck, bootstrap):
    slides = deck["slides"]
    n_fig = sum(len(s["figures"]) for s in slides)
    routes = Counter(f["resolved_by"] for s in slides for f in s["figures"])
    print(f"slides: {len(slides)}   figures: {n_fig}   resolved: "
          + ", ".join(f"{k} {v}" for k, v in sorted(routes.items())))
    if deck["n_unstamped"]:
        mode = "bootstrap" if bootstrap else "WARNING: unstamped, ids are positional"
        print(f"unstamped slides: {deck['n_unstamped']}  ({mode})")
    for s in slides:
        for f in s["figures"]:
            if f["resolved_by"] == "unresolved":
                print(f"{s['slide_id']}: {f['figure_id']} has no resolvable source — provenance unknown"
                      + (f" (extracted to {f['extracted']})" if f.get("extracted") else ""))
        if s.get("adopted_textbox"):
            print(f"{s['slide_id']}: a hand-added text box was read as the body; its position is not recorded")
        for op in s.get("opaque_shapes", []):
            print(f"{s['slide_id']}: unsupported shape {op['shape_type']} is not round-tripped")


# --------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pptx")
    ap.add_argument("--storyboard", help="revise: the storyboard this deck was rendered from (updated in place)")
    ap.add_argument("-o", "--output", help="bootstrap: the new storyboard .md to write")
    ap.add_argument("--project-root")
    ap.add_argument("--bootstrap", action="store_true",
                    help="import a legacy unstamped deck: mint fresh ids, deck is the truth")
    ap.add_argument("--layout-only", action="store_true",
                    help="record positions only; leave the storyboard text untouched")
    ap.add_argument("--dry-run", action="store_true", help="report what would change; write nothing")
    ap.add_argument("--json", help="also dump the deck state (text + figures) to this file, for debugging")
    args = ap.parse_args()

    import layout_record
    import merge_storyboard
    pptx = Path(args.pptx).resolve()
    root = Path(args.project_root).resolve() if args.project_root else None

    if args.bootstrap:
        if not args.output:
            ap.error("--bootstrap needs -o NAME.md")
        md = Path(args.output).resolve()
        if md.exists():
            ap.error(f"{md} exists; bootstrap writes a new storyboard only")
        deck = read(pptx, root, True, None, md.parent / "assets" / "unresolved")
        report(deck, True)
        if args.dry_run:
            return 0
        md.write_text(merge_storyboard.new_storyboard(deck, md, root))
        layout = layout_record.record(pptx, md)
        layout["unresolved"] = deck["unresolved"]
        layout_record.write(layout, md.with_suffix(".layout.json"))
        print(f"wrote {md} and {md.with_suffix('.layout.json').name}")
        return 0

    if not args.storyboard:
        ap.error("pass --storyboard NAME.md (revise) or --bootstrap -o NAME.md (legacy import)")
    md = Path(args.storyboard).resolve()
    layout_path = md.with_suffix(".layout.json")
    prior = layout_record.load(layout_path) if layout_path.is_file() else None
    md_newer = md.stat().st_mtime > pptx.stat().st_mtime
    if prior is None:
        print("NOTE: no layout record yet; every deck slide counts as edited in the deck")
    elif prior.get("pptx_sha256") == layout_record.sha256_file(pptx):
        print("NOTE: the deck is unchanged since its layout was last recorded")
    print("newer file: " + ("storyboard" if md_newer else "deck")
          + " (wins for slides edited in both places)")

    deck = read(pptx, root, False, (prior or {}).get("unresolved"), md.parent / "assets" / "unresolved")
    report(deck, False)
    if args.json and not args.dry_run:
        Path(args.json).write_text(json.dumps(deck, indent=2, ensure_ascii=False) + "\n")

    if not args.layout_only:
        current = layout_record.record(pptx)
        for entry, s in zip(current["slides"], deck["slides"]):
            entry["slide_id"] = s["slide_id"]
        text, changes = merge_storyboard.merge(md, deck, root, prior, current, md_newer)
        for line in changes:
            print(line)
        if not args.dry_run and text != md.read_text():
            backup = md.with_name(md.name + ".bak")
            backup.write_text(md.read_text())
            md.write_text(text)
            print(f"updated {md.name} (previous version: {backup.name})")
        elif text == md.read_text():
            print("storyboard text unchanged")
    if args.dry_run:
        return 0
    import render_storyboard
    blocks = {s["id"]: s["block"] for s in render_storyboard.parse_storyboard(md, root)}
    layout = layout_record.record(pptx, md, prior, blocks)
    layout["unresolved"] = deck["unresolved"]
    # Read slide ids the same way as above, so duplicates and positional slides line up.
    for entry, s in zip(layout["slides"], deck["slides"]):
        entry["slide_id"] = s["slide_id"]
    layout_record.write(layout, layout_path)
    print(f"wrote {layout_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
