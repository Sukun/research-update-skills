#!/usr/bin/env python3
"""read_deck.py — edited PPTX -> deck.json (pure current state, no diff).

Normal path reads the roles stamped by 6-ppt-create. `--bootstrap` imports a
legacy unstamped deck once, using the coordinate heuristic and minting fresh ids;
the deck itself is treated as the truth, with no matching against any storyboard.

  python read_deck.py DECK.pptx -o deck.json [--project-root DIR] [--bootstrap]
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import sys
from pathlib import Path

from pptx import Presentation

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

    title_shape = chip or title_ph
    title = text_of(title_shape) if title_shape is not None else None
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

    return {"chip": chip, "anchor_sid": anchor_sid, "stamped": stamped,
            "title": title, "section": section,
            "takeaway": text_of(takeaway) if takeaway is not None else None,
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


# --------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--project-root")
    ap.add_argument("--bootstrap", action="store_true",
                    help="import a legacy unstamped deck: mint fresh ids, deck is the truth")
    ap.add_argument("--prior", help="prior deck.json (carries unresolved_manual_NN numbering)")
    args = ap.parse_args()

    pptx = Path(args.pptx).resolve()
    root = Path(args.project_root).resolve() if args.project_root else None
    prs = Presentation(pptx)
    slide_w, slide_h = prs.slide_width, prs.slide_height

    prior = {}
    if args.prior and Path(args.prior).exists():
        prior = json.loads(Path(args.prior).read_text())
    unresolved_map = dict(prior.get("unresolved", {}))
    counter = [max([int(v.rsplit("_", 1)[1]) for v in unresolved_map.values()
                    if v.startswith("unresolved_manual_")] or [0])]

    registry = load_registry(pptx.parent)
    disk = scan_plots(root)

    slides, seen_ids, n_unstamped = [], set(), 0
    for idx, slide in enumerate(prs.slides):
        raw = extract_slide(slide, idx, args.bootstrap)
        if not raw["stamped"]:
            n_unstamped += 1

        figs = []
        for fig, sh, crop in raw["figures"]:
            fig["x"] = round((sh.left or 0) / slide_w, 4)
            fig["y"] = round((sh.top or 0) / slide_h, 4)
            fig["w"] = round((sh.width or 0) / slide_w, 4)
            fig["h"] = round((sh.height or 0) / slide_h, 4)
            fid, src, how = resolve_figure(fig, registry, disk, root,
                                           unresolved_map, counter)
            fig["figure_id"], fig["source"], fig["resolved_by"] = fid, src, how
            if any(crop):
                fig["crop"] = crop
            figs.append(fig)

        sid = raw["anchor_sid"]
        if args.bootstrap or not sid:
            sid = f"S{idx + 1:03d}"
        while sid in seen_ids:            # duplicated slide: id was copied verbatim
            n = int(re.sub(r"\D", "", sid) or 0)
            sid = f"S{n:03d}d{sum(1 for s in seen_ids if s.startswith(f'S{n:03d}d')) + 1}"
        seen_ids.add(sid)

        entry = {"slide_id": sid, "order": idx, "title": raw["title"],
                 "section": raw["section"], "takeaway": raw["takeaway"],
                 "notes": raw["notes"], "layout": infer_layout(figs), "figures": figs}
        if raw["opaque"]:
            entry["opaque_shapes"] = raw["opaque"]
        slides.append(entry)

    deck = {"schema_version": SCHEMA_VERSION,
            "deck_id": pptx.stem,
            "revision": int(prior.get("revision", 0)) + 1,
            "generated": _dt.date.today().isoformat(),
            "project_root": str(root) if root else None,
            "source_pptx": pptx.name,
            "slides": slides,
            "unresolved": unresolved_map}

    Path(args.output).write_text(json.dumps(deck, indent=2, ensure_ascii=False) + "\n")

    n_fig = sum(len(s["figures"]) for s in slides)
    n_unres = sum(1 for s in slides for f in s["figures"] if f["resolved_by"] == "unresolved")
    print(f"slides: {len(slides)}   figures: {n_fig}   unresolved: {n_unres}")
    if n_unstamped:
        mode = "bootstrap" if args.bootstrap else "WARNING: unstamped, ids are positional"
        print(f"unstamped slides: {n_unstamped}  ({mode})")
    if n_unres:
        print(f"{n_unres} figures had no resolvable source — provenance unknown.")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
