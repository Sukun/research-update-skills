#!/usr/bin/env python3
"""layout_record.py — the coordinate layer between the storyboard and the PPTX.

    <name>.md           text: titles, bullets, notes, which figures (author / 5-ppt-design)
    <name>.layout.json  where every shape sits: box, font size, crop (this module)
    <name>.pptx         the rendered view (6-ppt-create)

6-ppt-create records the layout after every render and restores it on the next one;
7-ppt-to-5 records it from a hand-edited deck. Shapes are matched by stable slide ID
plus a per-slide key: the stamped role for text (title, takeaway, section, caption,
section-band ...) and the image SHA-256 for pictures. Never by position.

CLI:
  python layout_record.py record DECK.pptx -o NAME.layout.json [--storyboard NAME.md]
  python layout_record.py apply  DECK.pptx NAME.layout.json   # restore in place
  python layout_record.py diff   DECK.pptx NAME.layout.json [--tol 0.005]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

SCHEMA_VERSION = 2
PICTURE = 13
TEXT_ROLES_FOR_SIG = ("title", "takeaway", "caption")


# ------------------------------------------------------------------ reading

def meta(shape):
    """Stamped payload: cNvPr@descr JSON first, `sb:` shape name as fallback."""
    try:
        descr = shape._element._nvXxPr.cNvPr.get("descr")
    except Exception:
        descr = None
    if descr:
        try:
            d = json.loads(descr)
            if isinstance(d, dict) and d.get("role"):
                return d
        except (ValueError, TypeError):
            pass
    name = getattr(shape, "name", "") or ""
    if name.startswith("sb:"):
        out = {}
        for part in name[3:].split("|"):
            if "=" in part:
                k, v = part.split("=", 1)
                out[{"slide": "sid"}.get(k, k)] = v
        if out.get("role"):
            return out
    return {}


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    return sha256_bytes(Path(path).read_bytes())


def slide_id(slide):
    for sh in slide.shapes:
        sid = meta(sh).get("sid")
        if sid:
            return sid
    return None


def font_pt(shape):
    """Most common explicit run size in points, or None when every run inherits."""
    if not shape.has_text_frame:
        return None
    sizes = Counter(r.font.size.pt for p in shape.text_frame.paragraphs for r in p.runs
                    if r.text.strip() and r.font.size is not None)
    return round(sizes.most_common(1)[0][0], 1) if sizes else None


def keyed_shapes(slide):
    """[(key, role, shape)] for every stamped text shape and every picture."""
    out, seen = [], Counter()
    for sh in slide.shapes:
        m = meta(sh)
        if sh.shape_type == PICTURE:
            try:
                sha = sha256_bytes(sh.image.blob)
            except Exception:
                continue
            base, role = "figure:" + sha[:16], "figure"
        elif m.get("role") and m["role"] != "figure":
            base = role = m["role"]
        else:
            continue
        seen[base] += 1
        out.append((base if seen[base] == 1 else f"{base}#{seen[base]}", role, sh))
    return out


def unstamped_text(slide):
    """Text boxes the renderer did not make (typed in by hand)."""
    return [sh for sh in slide.shapes
            if sh.has_text_frame and sh.text_frame.text.strip() and not meta(sh).get("role")
            and not (sh.is_placeholder and sh.placeholder_format.idx == 0)]


def text_sig(slide):
    """Short hash of the visible slide text, to tell whether the words changed."""
    parts = []
    for key, role, sh in keyed_shapes(slide):
        if role in TEXT_ROLES_FOR_SIG and sh.has_text_frame:
            parts.append(key + "=" + " ".join(sh.text_frame.text.split()))
    return sha256_bytes("\n".join(sorted(parts)).encode())[:16]


def notes_sig(slide):
    try:
        text = slide.notes_slide.notes_text_frame.text if slide.has_notes_slide else ""
    except Exception:
        text = ""
    return sha256_bytes(" ".join(text.split()).encode())[:16]


def block_sha(block):
    """Hash of one storyboard slide block, ignoring slide markers, separators and spacing."""
    lines = [l.rstrip() for l in block.splitlines()
             if l.strip() and l.strip() != "---" and not re.match(r"^\s*<!--\s*Slide\s+\d+\s*-->\s*$", l)]
    return sha256_bytes("\n".join(lines).encode())[:16]


def capture_slide(slide, sw, sh_):
    shapes, figures = [], []
    for z, (key, role, sh) in enumerate(keyed_shapes(slide)):
        rec = {"key": key, "role": role,
               "x": round((sh.left or 0) / sw, 5), "y": round((sh.top or 0) / sh_, 5),
               "w": round((sh.width or 0) / sw, 5), "h": round((sh.height or 0) / sh_, 5),
               "z": z}
        if role == "figure":
            sha = sha256_bytes(sh.image.blob)
            m = meta(sh)
            rec.update(sha256=sha, figure_id=m.get("fid"), source=m.get("src"))
            crop = [round(float(getattr(sh, "crop_" + s) or 0.0), 5)
                    for s in ("left", "right", "top", "bottom")]
            if any(crop):
                rec["crop"] = crop
            figures.append(sha)
        else:
            pt = font_pt(sh)
            if pt is not None:
                rec["font_pt"] = pt
        shapes.append(rec)
    return {"slide_id": slide_id(slide), "text_sig": text_sig(slide), "notes_sig": notes_sig(slide),
            "figures": sorted(figures), "shapes": shapes}


def record(pptx, storyboard=None, prior=None, blocks=None):
    """Layout dict for a deck. `prior` (a previous layout dict) carries `unresolved` forward.
    `blocks` ({slide_id: storyboard block}) stores a per-slide storyboard hash, so
    7-ppt-to-5 can tell which slides were edited in the storyboard after this point."""
    from pptx import Presentation
    pptx = Path(pptx)
    prs = Presentation(pptx)
    sw, sh = prs.slide_width, prs.slide_height
    slides = []
    for order, slide in enumerate(prs.slides):
        entry = capture_slide(slide, sw, sh)
        entry["order"] = order
        if entry["slide_id"] is None:
            entry["slide_id"] = f"S{order + 1:03d}"
            entry["positional_id"] = True
        if blocks and entry["slide_id"] in blocks:
            entry["md_sha"] = block_sha(blocks[entry["slide_id"]])
        slides.append(entry)
    return {"schema_version": SCHEMA_VERSION,
            "recorded": _dt.datetime.now().isoformat(timespec="seconds"),
            "source_pptx": pptx.name,
            "pptx_sha256": sha256_file(pptx),
            "storyboard": Path(storyboard).name if storyboard else None,
            "storyboard_sha256": sha256_file(storyboard) if storyboard else None,
            "slide_w_emu": int(sw), "slide_h_emu": int(sh),
            "slides": slides,
            "unresolved": dict((prior or {}).get("unresolved", {}))}


def write(layout, path):
    Path(path).write_text(json.dumps(layout, indent=1, ensure_ascii=False) + "\n")


def load(path):
    """Read a layout file. Schema 1 (old 7-ppt-to-5 deck.json) is converted: figures only."""
    data = json.loads(Path(path).read_text())
    if not isinstance(data, dict) or not isinstance(data.get("slides"), list):
        raise ValueError(f"{path}: not a layout file")
    version = data.get("schema_version")
    if version == SCHEMA_VERSION:
        out = data
    elif version == 1:
        out = {"schema_version": SCHEMA_VERSION, "converted_from": 1, "slides": [],
               "unresolved": data.get("unresolved", {})}
        for s in data["slides"]:
            shapes, seen = [], Counter()
            for f in s.get("figures", []):
                base = "figure:" + (f.get("sha256") or "")[:16]
                seen[base] += 1
                rec = {"key": base if seen[base] == 1 else f"{base}#{seen[base]}", "role": "figure",
                       **{k: f.get(k) for k in ("x", "y", "w", "h", "sha256", "figure_id", "source")}}
                if f.get("crop"):
                    rec["crop"] = f["crop"]
                shapes.append(rec)
            out["slides"].append({"slide_id": s.get("slide_id"), "text_sig": None,
                                  "figures": sorted(r["sha256"] for r in shapes),
                                  "shapes": shapes, "figures_only": True})
    else:
        raise ValueError(f"{path}: unsupported layout schema {version!r}")
    ids = [s.get("slide_id") for s in out["slides"]]
    if any(not i for i in ids) or len(ids) != len(set(ids)):
        raise ValueError(f"{path}: missing or duplicate slide IDs")
    for s in out["slides"]:
        for r in s["shapes"]:
            _check_box(r, s["slide_id"])
    return out


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _check_box(r, sid):
    vals = [r.get(k) for k in ("x", "y", "w", "h")]
    if not all(_num(v) for v in vals) or vals[2] <= 0 or vals[3] <= 0:
        raise ValueError(f"Invalid recorded geometry for {sid} {r.get('key')}")
    crop = r.get("crop", [0, 0, 0, 0])
    if (not isinstance(crop, list) or len(crop) != 4 or not all(_num(v) and 0 <= v < 1 for v in crop)
            or crop[0] + crop[1] >= 1 or crop[2] + crop[3] >= 1):
        raise ValueError(f"Invalid recorded crop for {sid} {r.get('key')}")


# ---------------------------------------------------------------- restoring

def estimated_overflow(shape, pt=None):
    """True when the text likely needs more height than its box (rough, 0.5 em glyphs)."""
    if not shape.has_text_frame or not shape.width or not shape.height:
        return False
    size = pt or font_pt(shape) or 18
    width_in = max(shape.width / 914400 - 0.2, 0.5)
    chars = max(1, int(width_in * 72 / (0.5 * size)))
    lines = sum(max(1, math.ceil(len(p.text) / chars)) for p in shape.text_frame.paragraphs)
    need_in = lines * size * 1.25 / 72 + 0.1
    return need_in > shape.height / 914400 * 1.05


def apply(pptx, layout, skip_ids=(), log=print):
    """Restore recorded boxes in place. Returns counts. A slide whose figure set changed
    keeps the generic layout (mixing recorded text with new figures would overlap)."""
    from pptx import Presentation
    from pptx.util import Pt
    if not isinstance(layout, dict):
        layout = load(layout)
    by_id = {s["slide_id"]: s for s in layout["slides"]}
    prs = Presentation(pptx)
    sw, sh = prs.slide_width, prs.slide_height
    counts = Counter()
    for slide in prs.slides:
        sid = slide_id(slide)
        entry = by_id.get(sid)
        if sid is None or sid in skip_ids:
            counts["generic"] += 1
            continue
        if entry is None:
            counts["new"] += 1
            log(f"layout {sid}: new slide, generic layout")
            continue
        cur = capture_slide(slide, sw, sh)
        if cur["figures"] != entry.get("figures", []):
            counts["figures_changed"] += 1
            log(f"layout {sid}: figures changed since the layout was recorded; generic layout kept")
            continue
        rec = {r["key"]: r for r in entry["shapes"]}
        moved = 0
        for key, role, shape in keyed_shapes(slide):
            r = rec.get(key)
            if r is None:
                log(f"layout {sid}: no recorded position for {key}; generic position kept")
                continue
            shape.left, shape.top = round(r["x"] * sw), round(r["y"] * sh)
            shape.width, shape.height = round(r["w"] * sw), round(r["h"] * sh)
            if role == "figure":
                shape.crop_left, shape.crop_right, shape.crop_top, shape.crop_bottom = r.get("crop", [0, 0, 0, 0])
            elif r.get("font_pt") and shape.has_text_frame:
                for p in shape.text_frame.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(r["font_pt"])
            moved += 1
        counts["shapes"] += moved
        counts["slides"] += 1
        if entry.get("figures_only"):
            log(f"layout {sid}: old deck.json records figures only; text boxes use the generic layout")
        elif entry.get("text_sig") and cur["text_sig"] != entry["text_sig"]:
            tight = [k for k, role, s in keyed_shapes(slide)
                     if role in TEXT_ROLES_FOR_SIG and estimated_overflow(s)]
            log(f"layout {sid}: text changed since the layout was recorded"
                + (f"; may overflow: {', '.join(tight)}" if tight else "; boxes kept"))
    prs.save(pptx)
    log("layout: restored {} shapes on {} slides; {} new, {} with changed figures".format(
        counts["shapes"], counts["slides"], counts["new"], counts["figures_changed"]))
    return counts


def diff(pptx, layout, tol=0.005):
    """[(sid, key, what)] for shapes that moved, appeared or vanished relative to `layout`."""
    from pptx import Presentation
    if not isinstance(layout, dict):
        layout = load(layout)
    prs = Presentation(pptx)
    sw, sh = prs.slide_width, prs.slide_height
    by_id = {s["slide_id"]: s for s in layout["slides"]}
    out = []
    for slide in prs.slides:
        cur = capture_slide(slide, sw, sh)
        entry = by_id.get(cur["slide_id"])
        if entry is None:
            out.append((cur["slide_id"], "*", "slide not in layout"))
            continue
        rec = {r["key"]: r for r in entry["shapes"]}
        now = {r["key"]: r for r in cur["shapes"]}
        for key in sorted(set(rec) | set(now)):
            a, b = rec.get(key), now.get(key)
            if a is None:
                out.append((cur["slide_id"], key, "not recorded"))
            elif b is None:
                out.append((cur["slide_id"], key, "missing from deck"))
            else:
                d = max(abs(a[k] - b[k]) for k in ("x", "y", "w", "h"))
                if d > tol:
                    out.append((cur["slide_id"], key, f"moved {d:.3f} of slide"))
    return out


# --------------------------------------------------------------------- CLI

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record")
    r.add_argument("pptx")
    r.add_argument("-o", "--output", required=True)
    r.add_argument("--storyboard")
    a = sub.add_parser("apply")
    a.add_argument("pptx")
    a.add_argument("layout")
    d = sub.add_parser("diff")
    d.add_argument("pptx")
    d.add_argument("layout")
    d.add_argument("--tol", type=float, default=0.005)
    args = ap.parse_args(argv)
    if args.cmd == "record":
        prior = load(args.output) if Path(args.output).is_file() else None
        write(record(args.pptx, args.storyboard, prior), args.output)
        print(f"wrote {args.output}")
    elif args.cmd == "apply":
        apply(args.pptx, args.layout)
    else:
        rows = diff(args.pptx, args.layout, args.tol)
        for row in rows:
            print("{}\t{}\t{}".format(*row))
        print(f"{len(rows)} difference(s)")
        return 1 if rows else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
