#!/usr/bin/env python3
"""postprocess_slides.py — fill in DATA BLOCK only; do not edit below the separator."""

import json
import re
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.oxml.ns import qn
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
try:
    from PIL import Image
except ImportError:
    Image = None

# ============================================================
# DATA BLOCK — fill in these values, nothing else
# ============================================================
PPTX_PATH = "output.pptx"          # <-- path to pandoc output

SECTION_TAGS = {
    # slide_index (0-based): ("tag_text", "color_name")
    # e.g.  1: ("z-space", "steelblue"),
}

LAYOUT_MAP = {
    "figure-dominant": [],   # slide indices with figure-dominant layout (annotated normalised in Phase 1)
    "vstack-3":        [],   # slide indices with vstack-3 layout
    "hstack-3":        [],   # slide indices with hstack-3 layout
    "table":           [],   # slide indices containing a stats table
}

FIGURES = {
    # slide_index: "/absolute/path/to/figure.png"
    # hstack-3 / vstack-3 entries: slide_index: ["/abs/fig_a.png", "/abs/fig_b.png", "/abs/fig_c.png"]
}

FIGURE_HEIGHT_OVERRIDE = {
    # optional, from explicit storyboard request
    # slide_index: 10/14,
}

# True (default): a figure slide with no bullets still gets a 1.6" band filled with
# "[Bullet N]" placeholders, so the author can see where text belongs.
# False: intentionally bullet-free decks (e.g. /5a-ppt-quick-assembly figure assembly)
# collapse the empty band instead, freeing its height for the figures.
BULLET_PLACEHOLDERS = True

# --- round-trip identity (consumed by /7-ppt-roundtrip) ---------------------
# STAMP_IDS=False reproduces the pre-round-trip output exactly.
STAMP_IDS = True
# Stable slide ids carried over from a revised storyboard (<!-- slide-id: S004 -->).
# Empty => mint S001, S002, ... by position on this render.
SLIDE_IDS = {
    # slide_index (0-based): "S004",
}
# Absolute project root; figure sources are stamped relative to it when inside.
PROJECT_ROOT = None
# Opt-in geometry, keyed by stable slide ID (or legacy zero-based index).
# margin, gap and content_top are inches; text_fraction is a slide-width fraction.
LAYOUT_OPTIONS = {}
# Keep authored Notes XML unchanged by default.
REFORMAT_NOTES = False
# ============================================================

COLOR_MAP = {
    'steelblue':  (70, 130, 180),
    'darkorange': (255, 140,   0),
    'teal':       (  0, 128, 128),
    'purple':     (128,   0, 128),
    'crimson':    (220,  20,  60),
    'grey':       (112, 112, 112),
}

def get_aspect(path, fallback=1.6):
    if Image is None or path is None:
        return fallback
    try:
        with Image.open(path) as image:
            w, h = image.size
        return w / h
    except Exception:
        return fallback

def shape_role(shape):
    try:
        payload = json.loads(shape._element._nvXxPr.cNvPr.get("descr", "{}"))
        if payload.get("role"):
            return payload["role"]
    except (ValueError, AttributeError, TypeError):
        pass
    match = re.search(r"sb:role=([^|]+)", shape.name or "")
    return match.group(1) if match else None


def body_text_shapes(slide):
    title = slide.shapes.title
    title_id = title.shape_id if title is not None else None
    return [sh for sh in slide.shapes if sh.has_text_frame
            and sh.shape_id != title_id and shape_role(sh) != "section"
            and sh.text_frame.text.strip()]


# Title + section-label geometry (inches). The title always stays in its own
# placeholder; a section tag is only a small label in the top-right corner.
TITLE_PT = 24
TITLE_LEFT, TITLE_TOP, TITLE_H = 0.30, 0.12, 0.85
LABEL_W, LABEL_H, LABEL_PT = 3.0, 0.32, 13
CONTENT_TOP_IN = 1.05          # first content row below a (possibly 2-line) title
LABEL_GREY = (0x70, 0x70, 0x70)


def add_section_tag(slide, tag_text, color_name, slide_w):
    """Small top-right label (13 pt, tag colour). Never touches the title."""
    for shape in slide.shapes:
        if shape_role(shape) == "section":
            if shape.text != tag_text:
                shape.text = tag_text
            return shape
    rgb = COLOR_MAP.get(color_name, LABEL_GREY)
    left = int(slide_w - Inches(LABEL_W + 0.15))
    box = slide.shapes.add_textbox(left, Inches(TITLE_TOP), Inches(LABEL_W), Inches(LABEL_H))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    para = tf.paragraphs[0]
    para.alignment = PP_ALIGN.RIGHT
    run = para.add_run()
    run.text = tag_text
    run.font.size = Pt(LABEL_PT)
    run.font.bold = False
    run.font.color.rgb = RGBColor(*rgb)
    _set_meta(box, "sb:role=section", {"role": "section"})
    return box


def is_cover(slide):
    try:
        return slide.slide_layout.name == "Title Slide"
    except Exception:
        return False


def place_title(slide, slide_w, has_tag):
    """Title stays in its placeholder: 24 pt bold, top-left, up to two lines.
    Width stops before the corner label when a tag exists. Cover slides are untouched."""
    title = slide.shapes.title
    if title is None or not title.has_text_frame or is_cover(slide):
        return
    right_reserved = LABEL_W + 0.3 if has_tag else 0.3
    title.left, title.top = int(Inches(TITLE_LEFT)), int(Inches(TITLE_TOP))
    title.width = int(slide_w - Inches(TITLE_LEFT + right_reserved))
    title.height = int(Inches(TITLE_H))
    tf = title.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    for para in tf.paragraphs:
        para.alignment = PP_ALIGN.LEFT
        for run in para.runs:
            run.font.size = Pt(TITLE_PT)
            run.font.bold = True


def remove_empty_placeholders(slide):
    """Delete placeholder shapes whose text content is entirely empty."""
    sp_tree = slide.shapes._spTree
    for shape in list(slide.placeholders):
        if not shape.has_text_frame:
            continue
        all_text = ''.join(
            run.text for para in shape.text_frame.paragraphs for run in para.runs
        )
        if not all_text.strip():
            sp_tree.remove(shape._element)

def enforce_content_placeholder_geometry(slide, slide_w, slide_h, has_tag, n_pics):
    """Widen/reposition the body content placeholder on section-tagged, picture-less
    slides (Outline, Method, Summary) to 90% width, centred, starting just below the chip.

    Picture slides are skipped here — ensure_bullet_placeholder() (called from the
    figure-fitting paths) already sets the correct compact top-band geometry for them.
    Cover slides / untagged slides are skipped entirely: touching a layout-inherited
    placeholder's geometry without setting all four xfrm fields can zero out height.
    """
    if not has_tag or n_pics > 0:   # has_tag: "slide is not a cover"
        return
    for ph in slide.placeholders:
        if ph.placeholder_format.idx == 0:
            continue
        if not ph.has_text_frame:
            continue
        ph.left = int(slide_w * 0.05)
        ph.width = int(slide_w * 0.90)
        ph.top = int(Inches(CONTENT_TOP_IN))
        ph.height = int(slide_h - Inches(CONTENT_TOP_IN + 0.30))
        break

def format_notes_one_sentence_per_line(slide):
    """Reformat speaker notes so each sentence occupies its own paragraph."""
    import re
    try:
        ntf = slide.notes_slide.notes_text_frame
    except Exception:
        return
    from pptx.oxml.ns import qn
    txBody = ntf._txBody
    paras  = txBody.findall(qn('a:p'))
    blocks = [''.join(r.text or '' for r in p.iter(qn('a:t'))) for p in paras]
    full = '\n\n'.join(b for b in blocks if b.strip())
    if not full.strip():
        return
    sentences = []
    for chunk in re.split(r'\n\n+', full):
        chunk = chunk.strip()
        if not chunk:
            continue
        sents = re.split(r'(?<=[.!?])\s+', chunk)
        sentences.extend(s.strip() for s in sents if s.strip())
    for p in paras[1:]:
        txBody.remove(p)
    first = paras[0]
    for r in list(first.findall(qn('a:r'))):
        first.remove(r)
    if sentences:
        ntf.paragraphs[0].text = sentences[0]
        for sent in sentences[1:]:
            ntf.add_paragraph().text = sent

def set_body_font(slide):
    title_id = slide.shapes.title.shape_id if slide.shapes.title else -1
    for shape in slide.shapes:
        if shape.shape_id == title_id or shape_role(shape) == "section":
            continue
        _set_text_shape_font(shape, 20)

def _set_text_shape_font(shape, font_pt):
    if not hasattr(shape, 'text_frame'):
        return
    for para in shape.text_frame.paragraphs:
        if para.runs:
            for run in para.runs:
                run.font.size = Pt(font_pt)
        else:
            para.font.size = Pt(font_pt)

def _boxes_overlap(a, b):
    ax1, ay1 = int(a.left), int(a.top)
    ax2, ay2 = ax1 + int(a.width), ay1 + int(a.height)
    bx1, by1 = int(b.left), int(b.top)
    bx2, by2 = bx1 + int(b.width), by1 + int(b.height)
    return (ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1)

def _resolve_text_picture_overlap(slide, text_shape):
    if text_shape is None:
        return
    pics = [s for s in slide.shapes if s.shape_type == 13]
    if not pics:
        return
    for font_pt in (20, 18, 16):
        _set_text_shape_font(text_shape, font_pt)
        if not any(_boxes_overlap(text_shape, pic) for pic in pics):
            return

def ensure_bullet_placeholder(slide, slide_w):
    """Ensure a top-half bullet band (1-3 bullets) below the section tag."""
    band_left = int(Inches(0.5))
    band_top = int(Inches(CONTENT_TOP_IN))
    band_width = int(slide_w - 2 * Inches(0.5))
    band_height = int(Inches(1.6))

    bullet_shape = None
    for ph in slide.placeholders:
        if ph.placeholder_format.idx != 0 and ph.has_text_frame:
            bullet_shape = ph
            break

    if bullet_shape is None:
        authored = body_text_shapes(slide)
        if authored:
            bullet_shape = authored[0]
            bullet_shape.left, bullet_shape.top = band_left, band_top
            bullet_shape.width, bullet_shape.height = band_width, band_height
    if bullet_shape is None:
        bullet_shape = slide.shapes.add_textbox(band_left, band_top, band_width, band_height)
    else:
        bullet_shape.left = band_left
        bullet_shape.top = band_top
        bullet_shape.width = band_width
        bullet_shape.height = band_height

    tf = bullet_shape.text_frame
    tf.word_wrap = True

    has_user_text = bool(tf.text.strip())
    if has_user_text:
        # Band height follows the text (0.7"-1.6") so short text frees height for figures.
        est = _estimated_text_height(bullet_shape, band_width, 20)
        bullet_shape.height = int(max(Inches(0.7), min(est + Inches(0.1), Inches(1.6))))
    if not has_user_text and not BULLET_PLACEHOLDERS:
        tf.clear()
        bullet_shape.top = int(Inches(CONTENT_TOP_IN - 0.02))
        bullet_shape.height = int(Inches(0.06))
        return bullet_shape

    if not has_user_text:
        tf.clear()
        p0 = tf.paragraphs[0]
        p0.text = "- [Bullet 1]"
        p1 = tf.add_paragraph()
        p1.text = "- [Bullet 2]"
        p2 = tf.add_paragraph()
        p2.text = "- [Bullet 3]"

    _set_text_shape_font(bullet_shape, 20)
    return bullet_shape

def _count_bullets(text_shape):
    if text_shape is None or not hasattr(text_shape, 'text_frame'):
        return 0
    count = 0
    for para in text_shape.text_frame.paragraphs:
        if para.text.strip():
            count += 1
    return count

def _default_figure_fraction_from_bullets(bullet_count):
    if bullet_count <= 1:
        return 11 / 14
    if bullet_count == 2:
        return 10 / 14
    return 9 / 14

FIG_BOTTOM_MARGIN_IN = 0.15


def _figure_region_geometry(slide_idx, slide_h, text_shape):
    """(top, height) of the figure region. Without an explicit figure-height the region
    starts right below the text band (or the title when there is no text) and runs to the
    bottom margin; an explicit override keeps the legacy fraction-from-bottom rule."""
    frac = FIGURE_HEIGHT_OVERRIDE.get(slide_idx)
    bottom = int(slide_h) - int(Inches(FIG_BOTTOM_MARGIN_IN))
    min_top = (int(text_shape.top + text_shape.height + Inches(0.08)) if text_shape is not None
               else int(Inches(CONTENT_TOP_IN)))
    if frac is None:
        fig_top = min_top
    else:
        frac = max(1e-3, min(float(frac), 1.0))
        fig_top = max(int(slide_h) - int(slide_h * frac), min_top)
    return fig_top, bottom - fig_top

def _fit_pictures_to_bottom_region(slide, slide_idx, slide_w, slide_h, text_shape):
    """Fit 1-4 pictures into the target bottom figure region while preserving arrangement."""
    pics = [s for s in slide.shapes if s.shape_type == 13]
    if not (1 <= len(pics) <= 4):
        return
    fig_top, fig_h = _figure_region_geometry(slide_idx, slide_h, text_shape)
    region_left = int(Inches(0.15))
    region_w = int(slide_w - 2 * Inches(0.15))

    box_left = min(int(s.left) for s in pics)
    box_top = min(int(s.top) for s in pics)
    box_right = max(int(s.left + s.width) for s in pics)
    box_bottom = max(int(s.top + s.height) for s in pics)
    box_w = max(box_right - box_left, 1)
    box_h = max(box_bottom - box_top, 1)

    scale = min(region_w / box_w, fig_h / box_h)
    out_w = int(box_w * scale)
    out_h = int(box_h * scale)
    target_left = region_left + max((region_w - out_w) // 2, 0)
    target_top = fig_top + max((fig_h - out_h) // 2, 0)

    for shp in pics:
        rel_x = int(shp.left) - box_left
        rel_y = int(shp.top) - box_top
        shp.left = int(target_left + rel_x * scale)
        shp.top = int(target_top + rel_y * scale)
        shp.width = int(max(int(shp.width * scale), 1))
        shp.height = int(max(int(shp.height * scale), 1))
        # Pandoc may round each dimension independently; restore source proportion.
        fit_picture(shp, shp.left, shp.top, shp.width, shp.height)

def style_table(slide, shape, slide_idx, slide_w, slide_h, has_bullets):
    tbl    = shape.table
    n_cols = len(tbl.columns)
    max_chars = [0] * n_cols
    for row in tbl.rows:
        for j, cell in enumerate(row.cells):
            max_chars[j] = max(max_chars[j], len(cell.text_frame.text))
    char_emu = int(Inches(0.12))
    min_emu  = 6 * char_emu
    widths   = [max(max_chars[j] * char_emu, min_emu) for j in range(n_cols)]
    total    = sum(widths)
    cap      = int(slide_w * 1.00)
    if total > cap:
        scale  = cap / total
        widths = [max(int(w * scale), min_emu) for w in widths]
        widths[-1] = max(cap - sum(widths[:-1]), min_emu)
        total = sum(widths)
    for j, col in enumerate(tbl.columns):
        col.width = widths[j]
    shape.width = total
    shape.left  = int((slide_w - total) / 2)

    text_shape = ensure_bullet_placeholder(slide, slide_w) if has_bullets else None
    top_min, avail_h = _figure_region_geometry(slide_idx, slide_h, text_shape)
    tbl_h   = sum(row.height for row in tbl.rows)
    shape.top = top_min + max((avail_h - tbl_h) // 2, 0)

    for row_idx, row in enumerate(tbl.rows):
        for cell in row.cells:
            tc = cell._tc
            for tag in ('{http://schemas.openxmlformats.org/drawingml/2006/main}solidFill',
                        '{http://schemas.openxmlformats.org/drawingml/2006/main}gradFill'):
                for el in tc.findall('.//' + tag):
                    el.getparent().remove(el)
            if row_idx == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(220, 220, 220)
            for para in cell.text_frame.paragraphs:
                para.font.size = Pt(16)
                for run in para.runs:
                    run.font.size = Pt(16)
                    run.font.bold = (row_idx == 0)

def _prepare_rebuild_pictures(slide, paths):
    """Reuse matching pictures to retain crops/metadata; replace only unmatched pictures."""
    if len(paths) != 3 or any(not path or not Path(path).is_file() for path in paths):
        raise ValueError("Three-picture layouts require three existing local figures")
    existing = [shape for shape in slide.shapes if shape.shape_type == 13]
    unused = list(existing)
    selected = []
    for path in paths:
        sha = _sha256_file(path)
        picture = next((pic for pic in unused if _sha256_bytes(pic.image.blob) == sha), None)
        if picture is not None:
            unused.remove(picture)
        else:
            picture = slide.shapes.add_picture(str(path), 0, 0)
        selected.append(picture)
    for pic in unused:
        pic._element.getparent().remove(pic._element)
    return selected


def rebuild_vstack3(slide, fig_paths, tag_info, slide_w, slide_h, slide_idx):
    pictures = _prepare_rebuild_pictures(slide, fig_paths)
    place_title(slide, slide_w, bool(tag_info))
    if tag_info:
        add_section_tag(slide, tag_info[0], tag_info[1], slide_w)
    text_shape = ensure_bullet_placeholder(slide, slide_w)
    top, height = _figure_region_geometry(slide_idx, slide_h, text_shape)
    margin = int(Inches(0.15))
    for i, pic in enumerate(pictures):
        fit_picture(pic, margin, top+i*height/3, slide_w-2*margin, height/3)
    _resolve_text_picture_overlap(slide, text_shape)


def rebuild_hstack3(slide, fig_paths, tag_info, slide_w, slide_h, slide_idx):
    pictures = _prepare_rebuild_pictures(slide, fig_paths)
    place_title(slide, slide_w, bool(tag_info))
    if tag_info:
        add_section_tag(slide, tag_info[0], tag_info[1], slide_w)
    text_shape = ensure_bullet_placeholder(slide, slide_w)
    top, height = _figure_region_geometry(slide_idx, slide_h, text_shape)
    margin = int(Inches(0.08))
    width = (slide_w-2*margin)/3
    for i, pic in enumerate(pictures):
        fit_picture(pic, margin+i*width, top, width, height)
    _resolve_text_picture_overlap(slide, text_shape)

def reposition_figure_dominant(slide, fig_path, slide_w, slide_h, slide_idx):
    aspect      = get_aspect(fig_path)
    text_shape  = ensure_bullet_placeholder(slide, slide_w)
    fig_top_min, max_h = _figure_region_geometry(slide_idx, slide_h, text_shape)
    img_w       = int(slide_w - 2 * Inches(0.3))
    img_h       = min(int(img_w / aspect), max_h)
    if img_h == max_h:
        img_w = int(img_h * aspect)
    fig_top  = fig_top_min + max((max_h - img_h) // 2, 0)
    fig_left = int((slide_w - img_w) / 2)
    for shape in slide.shapes:
        if shape.shape_type == 13:
            shape.left   = fig_left
            shape.top    = fig_top
            shape.width  = img_w
            shape.height = img_h
            fit_picture(shape, shape.left, shape.top, shape.width, shape.height)
            break
    _resolve_text_picture_overlap(slide, text_shape)

# ============================================================
# Round-trip identity stamping (additive; no geometry/font/shape-count change)
# ============================================================

def _sha256_bytes(b):
    import hashlib
    return hashlib.sha256(b).hexdigest()


def _sha256_file(path):
    import hashlib
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except Exception:
        return None


def _rel_source(path):
    """Project-relative when inside PROJECT_ROOT, else absolute."""
    p = Path(str(path)).resolve()
    if PROJECT_ROOT:
        try:
            return str(p.relative_to(Path(PROJECT_ROOT).resolve()))
        except ValueError:
            pass
    return str(p)


def _figure_id(source, taken):
    stem = re.sub(r"[^0-9A-Za-z_.-]+", "_", Path(str(source)).stem)[:60] or "fig"
    fid, n = stem, 1
    while fid in taken:
        n += 1
        fid = f"{stem}_{n}"
    taken.add(fid)
    return fid


def _set_meta(shape, name, payload):
    """Write the two stamped copies: shape.name (invisible) + cNvPr@descr (alt text)."""
    try:
        shape.name = name
    except Exception:
        pass
    try:
        cNvPr = shape._element._nvXxPr.cNvPr
        cNvPr.set("descr", json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    except Exception:
        pass


def _slide_text_shapes(slide):
    """All text-bearing shapes, INCLUDING empty ones.

    The takeaway band is empty on a bullet-free deck, but it must still be
    stamped: the user may type into it in PowerPoint, and an unstamped shape
    would make that edit invisible to /7-ppt-roundtrip.
    """
    return [sh for sh in slide.shapes if sh.has_text_frame]


def stamp_identity(slide, idx, registry):
    """Stamp roles on semantic shapes, the slide id on the identity anchor, and
    fid/src/sha on every picture. Returns nothing; mutates metadata only."""
    tag_info = SECTION_TAGS.get(idx)
    prior_ids = []
    for shape in slide.shapes:
        try:
            prior = json.loads(shape._element._nvXxPr.cNvPr.get("descr", "{}"))
            if prior.get("sid"):
                prior_ids.append(prior["sid"])
        except (ValueError, TypeError, AttributeError):
            pass
    sid = SLIDE_IDS.get(idx) or (prior_ids[0] if prior_ids else f"S{idx + 1:03d}")

    # --- roles on text shapes -------------------------------------------------
    chip = title_ph = takeaway = None
    tag_text = tag_info[0].strip() if tag_info else None
    for sh in _slide_text_shapes(slide):
        txt = sh.text_frame.text.strip()
        is_title = sh.is_placeholder and sh.placeholder_format.idx == 0
        if chip is None and tag_text and ((shape_role(sh) == "section") or (txt == tag_text and not is_title)):
            chip = sh
        elif sh.is_placeholder and sh.placeholder_format.idx == 0 and txt and title_ph is None:
            title_ph = sh
        elif takeaway is None:
            takeaway = sh          # may be empty — stamped anyway, see above
    if chip is None and title_ph is None and takeaway is None:
        # cover-style slide whose title was already consumed above
        t = slide.shapes.title
        if t is not None and t.has_text_frame:
            title_ph = t

    # Identity anchor precedence: section chip -> cover title -> takeaway band.
    anchor = chip or title_ph or takeaway
    for sh, role in ((chip, "section"), (title_ph, "title"), (takeaway, "takeaway")):
        if sh is None:
            continue
        payload = {"role": role}
        name = f"sb:role={role}"
        if sh is anchor:
            payload["sid"] = sid
            name += f"|slide={sid}"
        _set_meta(sh, name, payload)

    # --- figures --------------------------------------------------------------
    declared = FIGURES.get(idx)
    declared = declared if isinstance(declared, list) else ([declared] if declared else [])
    by_sha = {}
    for src in declared:
        h = _sha256_file(src)
        if h:
            by_sha.setdefault(h, src)

    taken = {e["figure_id"] for e in registry.values()}
    for pic in [sh for sh in slide.shapes if sh.shape_type == 13]:
        try:
            sha = _sha256_bytes(pic.image.blob)
        except Exception:
            continue
        payload = {"role": "figure", "sha": sha}
        entry = registry.get(sha)
        if entry is not None:
            fid, src_rel = entry["figure_id"], entry["source"]
        else:
            src = by_sha.get(sha)
            prior = {}
            try:
                prior = json.loads(pic._element._nvXxPr.cNvPr.get("descr", "{}"))
            except (ValueError, TypeError, AttributeError):
                pass
            src_rel = _rel_source(src) if src else (prior.get("src") if prior.get("sha") == sha else None)
            fid = _figure_id(src_rel or f"unknown_{sha[:8]}", taken)
            registry[sha] = {"figure_id": fid, "source": src_rel,
                             "width": None, "height": None}
            try:
                registry[sha]["width"], registry[sha]["height"] = pic.image.size
            except Exception:
                pass
        payload["fid"] = fid
        if src_rel:
            payload["src"] = src_rel
        _set_meta(pic, f"sb:role=figure|fid={fid}", payload)


def write_figure_registry(registry, pptx_path):
    """Append-only, project-scoped, keyed by sha256. Fallback resolver only."""
    out = Path(pptx_path).parent / "figure_registry.json"
    existing = {}
    if out.exists():
        try:
            existing = json.loads(out.read_text())
        except Exception:
            existing = {}
    existing.update({k: v for k, v in registry.items() if k not in existing})
    out.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n")
    return out, len(existing)


BALANCED_LAYOUTS = ("figure-right-text-left", "figure-pair-right-text-left",
                    "figure-left-text-right", "figure-pair-left-text-right",
                    "vertical-balanced-text", "large-text-summary", "figure-full-width")
# layout -> (picture count, text on the right?). Side layouts: 18 pt bullets,
# text box and its text both vertically centred against the figure region.
SIDE_LAYOUTS = {
    "figure-right-text-left": (1, False), "figure-pair-right-text-left": (2, False),
    "figure-left-text-right": (1, True), "figure-pair-left-text-right": (2, True),
}
SIDE_FONT_PT = 18


def _ensure_bullets(shape):
    """Give every non-empty paragraph an explicit bullet, keeping existing ones."""
    from pptx.oxml.ns import qn
    from lxml import etree
    for para in shape.text_frame.paragraphs:
        if not para.text.strip():
            continue
        pPr = para._p.get_or_add_pPr()
        if any(pPr.find(qn(tag)) is not None for tag in ("a:buNone", "a:buChar", "a:buAutoNum", "a:buBlip")):
            continue
        pPr.set("marL", "285750")
        pPr.set("indent", "-285750")
        bullet = etree.SubElement(pPr, qn("a:buChar"))
        bullet.set("char", "•")
        # Schema order: bullet elements precede tabLst/defRPr/extLst.
        for tag in ("a:tabLst", "a:defRPr", "a:extLst"):
            later = pPr.find(qn(tag))
            if later is not None:
                later.addprevious(bullet)
                break


def _options(idx):
    return LAYOUT_OPTIONS.get(SLIDE_IDS.get(idx), LAYOUT_OPTIONS.get(idx, {}))


def validate_layout_options(prs):
    import math
    allowed = {"margin", "gap", "content_top", "text_fraction", "font_pt"}
    valid_keys = set(range(len(prs.slides))) | set(SLIDE_IDS.values())
    for key, options in LAYOUT_OPTIONS.items():
        if key not in valid_keys:
            raise ValueError("Unknown slide for layout options: " + str(key))
        if set(options) - allowed:
            raise ValueError("Unknown layout options: " + str(set(options) - allowed))
        for name, value in options.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError("Layout option must be finite: " + name)
            low, high = ((0.25, 0.35) if name == "text_fraction" else
                         (16, 44) if name == "font_pt" else
                         (0, 1.5) if name == "margin" else
                         (0.02, 1) if name == "gap" else (0.48, 3))
            if not low <= value <= high:
                raise ValueError("Layout option out of range: " + name)
    for idx, value in FIGURE_HEIGHT_OVERRIDE.items():
        if idx not in range(len(prs.slides)) or not math.isfinite(float(value)) or not 0 < value <= 1:
            raise ValueError("Invalid figure-height override")


def _set_box(shape, left, top, width, height):
    if width <= 0 or height <= 0:
        raise ValueError("No space for slide content")
    shape.left, shape.top = int(left), int(top)
    shape.width, shape.height = int(width), int(height)


def fit_picture(pic, left, top, width, height):
    # Existing crops are preserved. New crops are never inferred.
    w, h = pic.image.size
    aspect = (w * (1 - pic.crop_left - pic.crop_right) /
              (h * (1 - pic.crop_top - pic.crop_bottom)))
    out_w = min(width, height * aspect)
    out_h = out_w / aspect
    _set_box(pic, left + (width - out_w) / 2, top + (height - out_h) / 2, out_w, out_h)


def _estimated_text_height(shape, width, font_pt=20):
    # Conservative geometry heuristic, not a substitute for office rendering.
    import math
    chars_per_line = max((width / 914400 * 72 / font_pt) / 0.55, 1)
    lines = 0
    for para in shape.text_frame.paragraphs:
        if para.text.strip():
            sizes = [r.font.size.pt for r in para.runs if r.font.size]
            factor = max(sizes + [font_pt]) / font_pt
            lines += max(1, math.ceil(len(para.text) * factor / chars_per_line))
    return int(Pt(lines * font_pt * 1.35) + shape.text_frame.margin_top + shape.text_frame.margin_bottom)


def _place_text_group(shapes, left, top, width, height, font_pt, sid):
    if not shapes:
        return
    heights = [_estimated_text_height(sh, width, font_pt) for sh in shapes]
    gap = int(Inches(0.10))
    total = sum(heights) + gap * (len(shapes) - 1)
    if total > height:
        print("QA WARNING {}: text may overflow; enlarge the region or revise the storyboard.".format(sid))
        # Keep boxes inside the text region; do not move them over figures.
        heights = [max(1, int(h * max(height - gap * (len(shapes)-1), 1) / sum(heights))) for h in heights]
        total = sum(heights) + gap * (len(shapes)-1)
    cursor = top + max((height - total) / 2, 0)
    for sh, h in zip(shapes, heights):
        _set_box(sh, left, cursor, width, h)
        sh.text_frame.word_wrap = True
        cursor += h + gap


# --- figure-full-width: shared geometry (inches) ---------------------------
FW_MARGIN_IN = 0.5          # left/right margin; content width = slide width - 2 * this
FW_FONT_PT = 16
FW_LINE_IN = 0.32           # height of one 16 pt text line
FW_TEXT_PAD_IN = 0.10       # box padding above/below the bullets
FW_GAP_IN = 0.08
FW_CAPTION_PT = 11
FW_CAPTION_H_IN = 0.30
FW_BOTTOM_IN = 0.12
FW_MAX_BULLETS = 3
FW_MIN_WIDTH_FRACTION = 0.75
FW_NOTES_PREFIX = "Also on the slide:"


def fw_line_count(text, width_in, font_pt=FW_FONT_PT):
    """Estimated wrapped line count of one paragraph (0.5 em average glyph width)."""
    import math
    chars = max((width_in - 0.2) * 72 / font_pt / 0.5, 1)
    return max(1, math.ceil(len(text) / chars))


def fw_figure_box(aspect, text_h_in, slide_w_in, slide_h_in, top_in=None):
    """Figure box (left, top, w, h) in inches below `text_h_in` of top text: full content
    width if the aspect allows, otherwise scaled down and centred. Never stretched."""
    top_in = CONTENT_TOP_IN if top_in is None else top_in
    content_w = slide_w_in - 2 * FW_MARGIN_IN
    fig_top = top_in + (text_h_in + FW_GAP_IN if text_h_in > 0 else 0)
    fig_bottom = slide_h_in - FW_BOTTOM_IN - FW_CAPTION_H_IN - FW_GAP_IN
    avail_h = fig_bottom - fig_top
    w = min(content_w, avail_h * aspect)
    h = w / aspect
    return (slide_w_in - w) / 2, fig_top, w, h


def fw_choose_n(line_counts, aspect, slide_w_in, slide_h_in):
    """Largest N <= 3 (and <= len(line_counts)) whose top text still leaves the figure at
    least 75% of the content width. Falls back to 1 (0 if there is no text)."""
    content_w = slide_w_in - 2 * FW_MARGIN_IN
    best = min(1, len(line_counts))
    for n in range(min(FW_MAX_BULLETS, len(line_counts)), 0, -1):
        text_h = sum(line_counts[:n]) * FW_LINE_IN + FW_TEXT_PAD_IN
        _, _, w, _ = fw_figure_box(aspect, text_h, slide_w_in, slide_h_in)
        if w >= FW_MIN_WIDTH_FRACTION * content_w - 1e-9:
            return n
    return best


def apply_full_width_layout(slide, idx, slide_w, slide_h):
    """Title and tag as usual; top bullets (N chosen by fw_choose_n) under the title; one
    picture across the full content width; small grey caption; remaining bullets -> notes."""
    sid = SLIDE_IDS.get(idx, "slide-{}".format(idx + 1))
    pics = [sh for sh in slide.shapes if sh.shape_type == 13]
    if len(pics) != 1:
        raise ValueError("figure-full-width requires one picture; got {}".format(len(pics)))
    texts = body_text_shapes(slide)
    if len(texts) > 1:
        raise ValueError("figure-full-width expects one body text frame")
    pic = pics[0]
    w_px, h_px = pic.image.size
    aspect = (w_px * (1 - pic.crop_left - pic.crop_right) /
              (h_px * (1 - pic.crop_top - pic.crop_bottom)))
    sw_in, sh_in = slide_w / 914400, slide_h / 914400
    content_w = sw_in - 2 * FW_MARGIN_IN

    body = texts[0] if texts else None
    bullets, captions = [], []
    if body is not None:
        for para in body.text_frame.paragraphs:
            t = para.text.strip()
            if not t:
                continue
            pPr = para._p.pPr
            is_bullet = pPr is None or pPr.find(qn("a:buNone")) is None
            (captions if (t.startswith("[") and not is_bullet) else bullets).append(para)
    lines = [fw_line_count(p.text, content_w) for p in bullets]
    n = fw_choose_n(lines, aspect, sw_in, sh_in)
    keep, spill = bullets[:n], bullets[n:]
    text_h = (sum(lines[:n]) * FW_LINE_IN + FW_TEXT_PAD_IN) if n else 0

    if body is not None:
        from copy import deepcopy
        cap_elems = [deepcopy(p._p) for p in captions]
        spill_text = [p.text for p in spill]
        for p in spill + captions:
            p._p.getparent().remove(p._p)
        if n:
            _set_box(body, Inches(FW_MARGIN_IN), Inches(CONTENT_TOP_IN), Inches(content_w), Inches(text_h))
            tf = body.text_frame
            tf.word_wrap = True
            tf.vertical_anchor = MSO_ANCHOR.TOP
            tf.margin_top = tf.margin_bottom = Inches(0.03)
            _set_text_shape_font(body, FW_FONT_PT)
            _ensure_bullets(body)
        else:
            body._element.getparent().remove(body._element)
    else:
        cap_elems, spill_text = [], []

    left, top, w, h = fw_figure_box(aspect, text_h, sw_in, sh_in)
    _set_box(pic, Inches(left), Inches(top), Inches(w), Inches(h))

    if cap_elems:
        cap_top = max(top + h + FW_GAP_IN, 0)
        box = slide.shapes.add_textbox(Inches(FW_MARGIN_IN), Inches(cap_top),
                                       Inches(content_w), Inches(FW_CAPTION_H_IN))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = Inches(0.02)
        for element in list(tf._txBody.findall(qn("a:p"))):
            tf._txBody.remove(element)
        for element in cap_elems:
            tf._txBody.append(element)
        for para in tf.paragraphs:
            para.alignment = PP_ALIGN.CENTER
            pPr = para._p.get_or_add_pPr()
            pPr.set("marL", "0")
            pPr.set("indent", "0")
            for run in para.runs:
                run.font.size = Pt(FW_CAPTION_PT)
                run.font.color.rgb = RGBColor(*LABEL_GREY)
        if len(cap_elems) > 1 or fw_line_count(box.text_frame.text, content_w, FW_CAPTION_PT) > 1:
            print("QA WARNING {}: caption may wrap beyond one line.".format(sid))
        _set_meta(box, "sb:role=caption", {"role": "caption"})

    if spill_text:
        ntf = slide.notes_slide.notes_text_frame
        existing = ntf.text.strip()
        block = [FW_NOTES_PREFIX] + spill_text
        ntf.text = "\n".join(block + ([""] + existing.splitlines() if existing else []))
    print("figure-full-width {}: N={} top bullets kept, {} moved to notes; figure {:.2f} in wide ({:.0f}% of content width)"
          .format(sid, n, len(spill_text), w, 100 * w / content_w))
    return n


def apply_balanced_layout(slide, idx, layout, slide_w, slide_h):
    from pptx.enum.text import MSO_ANCHOR
    if layout == "figure-full-width":
        return apply_full_width_layout(slide, idx, slide_w, slide_h)
    options = _options(idx)
    margin = int(Inches(options.get("margin", 0.30)))
    gap = int(Inches(options.get("gap", 0.18)))
    top = int(Inches(options.get("content_top", CONTENT_TOP_IN)))
    width, height = slide_w - 2*margin, slide_h - top - margin
    if width <= gap or height <= gap:
        raise ValueError("Margins leave no content region")
    pics = [sh for sh in slide.shapes if sh.shape_type == 13]
    texts = body_text_shapes(slide)
    sid = SLIDE_IDS.get(idx, "slide-{}".format(idx + 1))
    default_font = (28 if layout == "large-text-summary" else
                    SIDE_FONT_PT if layout in SIDE_LAYOUTS else 20)
    font = options.get("font_pt", default_font)
    for sh in texts:
        _set_text_shape_font(sh, font)
    if layout in SIDE_LAYOUTS:
        expected, text_right = SIDE_LAYOUTS[layout]
        if len(pics) != expected:
            raise ValueError("{} requires {} pictures; got {}".format(layout, expected, len(pics)))
        text_w = int(width * options.get("text_fraction", 0.30))
        text_left = slide_w - margin - text_w if text_right else margin
        if len(texts) == 1:
            # One box spans the figure region, so the box and its anchored text
            # are both exactly centred whatever the real rendered text height is.
            if _estimated_text_height(texts[0], text_w, font) > height:
                print("QA WARNING {}: text may overflow; enlarge the region or revise the storyboard.".format(sid))
            _set_box(texts[0], text_left, top, text_w, height)
        else:
            _place_text_group(texts, text_left, top, text_w, height, font, sid)
        for sh in texts:
            tf = sh.text_frame
            tf.word_wrap = True
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            _ensure_bullets(sh)
        if text_right:
            fig_left, fig_right = margin, text_left - gap
        else:
            fig_left, fig_right = text_left + text_w + gap, slide_w - margin
        cell_w = (fig_right - fig_left - gap * (len(pics)-1)) / len(pics)
        for i, pic in enumerate(pics):
            fit_picture(pic, fig_left + i * (cell_w + gap), top, cell_w, height)
    elif layout == "vertical-balanced-text":
        if len(pics) != 1:
            raise ValueError("vertical-balanced-text requires one picture")
        text_h = sum(_estimated_text_height(sh, width, font) for sh in texts) + gap * max(len(texts)-1, 0)
        frac = FIGURE_HEIGHT_OVERRIDE.get(idx)
        # Without an explicit figure-height the figure starts right below the measured text.
        fig_top = top + text_h + gap if frac is None else max(top + text_h + gap, int(slide_h * (1-frac)))
        if fig_top >= slide_h - margin:
            raise ValueError("Text leaves no figure region on " + sid)
        fit_picture(pics[0], margin, fig_top, width, slide_h-margin-fig_top)
        _place_text_group(texts, margin, top, width, pics[0].top-top-gap, font, sid)
    else:
        if pics:
            raise ValueError("large-text-summary requires a text-only slide")
        paragraphs = [(sh, para) for sh in texts for para in sh.text_frame.paragraphs if para.text.strip()]
        if not 3 <= len(paragraphs) <= 4:
            raise ValueError("large-text-summary requires three or four statements")
        # Keep one takeaway text frame so /7-ppt-to-5 recovers every statement.
        # Preserve paragraph XML (runs, emphasis and links), then spread paragraphs.
        from copy import deepcopy
        from pptx.oxml.ns import qn
        import math
        copies = [deepcopy(para._p) for _, para in paragraphs]
        box = texts[0]
        for sh in texts[1:]:
            sh._element.getparent().remove(sh._element)
        tf = box.text_frame
        for element in list(tf._txBody.findall(qn("a:p"))):
            tf._txBody.remove(element)
        for element in copies:
            tf._txBody.append(element)
        _set_box(box, margin, top, width, height)
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_top = tf.margin_bottom = 0
        _set_text_shape_font(box, font)
        slot_pt = height / 12700 / len(copies)
        chars = max(width / 914400 * 72 / font / 0.55, 1)
        for para in tf.paragraphs:
            text_pt = max(1, math.ceil(len(para.text) / chars)) * font * 1.35
            para.space_before = Pt(max((slot_pt-text_pt)/2, 0))
            para.space_after = Pt(max((slot_pt-text_pt)/2, 0))
            if text_pt > slot_pt:
                print("QA WARNING {}: summary statement may overflow.".format(sid))



def main():
    prs     = Presentation(PPTX_PATH)
    slide_w = prs.slide_width
    slide_h = prs.slide_height

    validate_layout_options(prs)
    for idx, slide in enumerate(prs.slides):
        tag_info = SECTION_TAGS.get(idx)
        fig_path = FIGURES.get(idx)
        layout = next((name for name in BALANCED_LAYOUTS if idx in LAYOUT_MAP.get(name, [])), None)
        if not (idx in LAYOUT_MAP.get("vstack-3", []) or idx in LAYOUT_MAP.get("hstack-3", [])):
            place_title(slide, slide_w, bool(tag_info))
        if layout:
            if layout in ("figure-pair-right-text-left", "figure-pair-left-text-right"):
                from collections import Counter
                existing = Counter(_sha256_bytes(pic.image.blob) for pic in slide.shapes if pic.shape_type == 13)
                for source in (fig_path if isinstance(fig_path, list) else []):
                    sha = _sha256_file(source)
                    if existing[sha]:
                        existing[sha] -= 1
                    else:
                        slide.shapes.add_picture(str(source), 0, 0)
            if tag_info:
                add_section_tag(slide, tag_info[0], tag_info[1], slide_w)
            remove_empty_placeholders(slide)
            set_body_font(slide)
            apply_balanced_layout(slide, idx, layout, slide_w, slide_h)
            if REFORMAT_NOTES:
                format_notes_one_sentence_per_line(slide)
            continue

        if idx in LAYOUT_MAP.get("vstack-3", []):
            paths = fig_path if isinstance(fig_path, list) else [fig_path]
            rebuild_vstack3(slide, paths, tag_info, slide_w, slide_h, idx)
            if REFORMAT_NOTES:
                format_notes_one_sentence_per_line(slide)
            continue

        if idx in LAYOUT_MAP.get("hstack-3", []):
            paths = fig_path if isinstance(fig_path, list) else [fig_path]
            rebuild_hstack3(slide, paths, tag_info, slide_w, slide_h, idx)
            if REFORMAT_NOTES:
                format_notes_one_sentence_per_line(slide)
            continue

        if tag_info:
            add_section_tag(slide, tag_info[0], tag_info[1], slide_w)

        remove_empty_placeholders(slide)

        n_pics_now = len([s for s in slide.shapes if s.shape_type == 13])
        enforce_content_placeholder_geometry(slide, slide_w, slide_h, not is_cover(slide), n_pics_now)

        set_body_font(slide)

        has_bullets = False
        bullet_shape = None
        for ph in slide.placeholders:
            if ph.placeholder_format.idx == 0:
                continue
            if ph.has_text_frame and any(
                run.text.strip()
                for para in ph.text_frame.paragraphs
                for run in para.runs
            ):
                has_bullets = True
                bullet_shape = ph
                break

        for shape in slide.shapes:
            if shape.shape_type == 19:
                style_table(slide, shape, idx, slide_w, slide_h, has_bullets)

        if idx in LAYOUT_MAP.get("figure-dominant", []) and fig_path:
            reposition_figure_dominant(slide, fig_path, slide_w, slide_h, idx)
        elif 1 <= len([s for s in slide.shapes if s.shape_type == 13]) <= 4:
            # Always re-normalize geometry here, even if a bullet placeholder was
            # already found above — that placeholder still has Pandoc's raw
            # two-column geometry (narrow width, near-full-slide height). Without
            # this call the figure-region math treats that raw placeholder as
            # final, leaving only a sliver of vertical space for the picture.
            # This branch is the safety net for any slide missing from
            # LAYOUT_MAP["figure-dominant"] (e.g. an off-by-one in slide_idx),
            # so it must produce the same compact top band as the explicit path.
            if has_bullets:
                bullet_shape = ensure_bullet_placeholder(slide, slide_w)
            _fit_pictures_to_bottom_region(slide, idx, slide_w, slide_h, bullet_shape)
            _resolve_text_picture_overlap(slide, bullet_shape)

        if REFORMAT_NOTES:
            format_notes_one_sentence_per_line(slide)

    if STAMP_IDS:
        registry = {}
        for idx, slide in enumerate(prs.slides):
            stamp_identity(slide, idx, registry)
        reg_path, n_reg = write_figure_registry(registry, PPTX_PATH)
        print(f"Stamped {len(prs.slides)} slides; registry: {reg_path} ({n_reg} figures)")

    prs.save(PPTX_PATH)
    print(f"Saved: {PPTX_PATH}")

if __name__ == "__main__":
    main()
