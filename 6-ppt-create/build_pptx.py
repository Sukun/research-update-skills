#!/usr/bin/env python3
"""Direct python-pptx builder: storyboard -> raw deck (replaces Pandoc).

Pandoc's PPTX writer drops or splits content whenever a slide holds text plus
several pictures, so this engine places the shapes itself. It produces the same
*kind* of raw deck Pandoc did (title placeholder, one body placeholder with the
authored text, loose pictures in their intended arrangement, Notes), and
render_storyboard.py then runs the unchanged static postprocess_template.py,
which owns all layout geometry, tags, identity stamping and the figure registry.

No reference template by default: a blank 16:9 python-pptx presentation. A
template is used only when --reference is given explicitly.
"""
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from latex_text import convert_math  # noqa: E402

SLIDE_W, SLIDE_H = Inches(13.333), Inches(7.5)
IMG_RE = re.compile(r'!\[[^\]]*\]\((?:<[^>]+>|[^\s)]+)\)(?:\{[^}]*\})?')
BULLET_RE = re.compile(r'^(\s*)[-*+]\s+(.*)$')
TABLE_SEP_RE = re.compile(r'^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$')
NOTES_OPEN = re.compile(r'^::: ?(?:notes|\{\.notes\})\s*$')


# ------------------------------------------------------------------ parsing

def _strip_comments(text):
    return re.sub(r'<!--.*?-->', '', text, flags=re.S)


def split_block(block, math_warnings):
    """Return dict(paragraphs, notes, table) from one slide block (text outside the title)."""
    notes, body, in_notes, legacy_note = [], [], False, False
    # Drop comments (metadata) first; they may span lines.
    lines = _strip_comments(block).splitlines()
    for line in lines:
        s = line.strip()
        if in_notes:
            if re.fullmatch(r':{3,}', s):
                in_notes = False
            else:
                notes.append(line.rstrip())
            continue
        if NOTES_OPEN.match(s):
            in_notes = True
            continue
        if legacy_note:
            if s == '---':
                legacy_note = False
            else:
                notes.append(line.rstrip())
                continue
        if s == 'Note:':
            legacy_note = True
            continue
        if s == '---' or line.startswith('## ') or re.match(r'^:{3,}', s):
            continue
        body.append(line.rstrip())

    paragraphs, table, cur = [], None, None
    i = 0
    while i < len(body):
        line = body[i]
        s = line.strip()
        if not s:
            cur = None
            i += 1
            continue
        if s.startswith('|') and i + 1 < len(body) and TABLE_SEP_RE.match(body[i + 1]):
            rows = [[c.strip() for c in s.strip('|').split('|')]]
            i += 2
            while i < len(body) and body[i].strip().startswith('|'):
                rows.append([c.strip() for c in body[i].strip().strip('|').split('|')])
                i += 1
            table = rows
            cur = None
            continue
        text = IMG_RE.sub('', s).strip()
        if not text:
            cur = None
            i += 1
            continue
        m = BULLET_RE.match(line)
        if m:
            level = 1 if len(m.group(1).replace('\t', '    ')) >= 2 else 0
            cur = dict(text=m.group(2).strip(), bullet=True, level=level)
            paragraphs.append(cur)
        elif cur is not None:
            cur['text'] += ' ' + text
        else:
            cur = dict(text=text, bullet=False, level=0)
            paragraphs.append(cur)
        i += 1
    for p in paragraphs:
        p['text'] = convert_math(p['text'], math_warnings)
    notes = [convert_math(n, math_warnings) for n in notes]
    while notes and not notes[-1].strip():
        notes.pop()
    return dict(paragraphs=paragraphs, notes=notes, table=table)


INLINE_RE = re.compile(r'(\*\*[^*]+\*\*|\*[^*\s][^*]*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))')


def add_inline_runs(paragraph, text):
    """Add runs for **bold**, *italic*, `code` and [text](url)."""
    for part in INLINE_RE.split(text):
        if not part:
            continue
        run = None
        if part.startswith('**') and part.endswith('**') and len(part) > 4:
            run = paragraph.add_run()
            run.text = part[2:-2]
            run.font.bold = True
        elif part.startswith('*') and part.endswith('*') and len(part) > 2:
            run = paragraph.add_run()
            run.text = part[1:-1]
            run.font.italic = True
        elif part.startswith('`') and part.endswith('`'):
            run = paragraph.add_run()
            run.text = part[1:-1]
            run.font.name = 'Courier New'
        else:
            m = re.fullmatch(r'\[([^\]]+)\]\(([^)]+)\)', part)
            run = paragraph.add_run()
            run.text = m.group(1) if m else part
            if m and re.match(r'\w+://', m.group(2)):
                run.hyperlink.address = m.group(2)
    return paragraph


def plain_title(text, math_warnings):
    return convert_math(text.replace('**', '').replace('`', ''), math_warnings)


# ----------------------------------------------------------------- shapes

def _no_bullet(paragraph):
    pPr = paragraph._p.get_or_add_pPr()
    pPr.set('marL', '0')
    pPr.set('indent', '0')
    for tag in ('a:buNone', 'a:buChar', 'a:buAutoNum'):
        for el in pPr.findall(qn(tag)):
            pPr.remove(el)
    pPr.insert(0, etree.SubElement(pPr, qn('a:buNone')))


def _fix_layout_geometry(prs):
    """The python-pptx default template is 4:3 (10 in wide); stretch its layouts to 16:9."""
    factor = SLIDE_W / Emu(9144000)
    parents = [prs.slide_master] + list(prs.slide_layouts)
    for parent in parents:
        for shape in parent.shapes:
            try:
                if shape.left is not None:
                    shape.left, shape.width = int(shape.left * factor), int(shape.width * factor)
            except Exception:
                pass


def _layout(prs, name, fallback_index):
    for layout in prs.slide_layouts:
        if layout.name == name:
            return layout
    return prs.slide_layouts[fallback_index]


def arrangement(layout, aspects):
    """Relative picture boxes (x, y, w, h) in arbitrary units, matching the layout's
    intended arrangement. postprocess_template scales/centres the group to its region."""
    n, gap = len(aspects), 0.04
    if n == 1:
        return [(0, 0, aspects[0], 1)]
    if layout in ('vstack-2', 'vstack-3'):
        boxes, y = [], 0
        for a in aspects:
            h = 1 / a
            boxes.append((0, y, 1, h))
            y += h + gap
        return boxes
    if layout == 'grid-2x2' and n == 4:
        cw = max(aspects)
        return [((i % 2) * (cw + gap), (i // 2) * (1 + gap), aspects[i], 1) for i in range(4)]
    if layout == 'focus-context' and n == 3:
        h = (1 - gap) / 2
        return [(0, 0, aspects[0], 1),
                (aspects[0] + gap, 0, aspects[1] * h, h),
                (aspects[0] + gap, h + gap, aspects[2] * h, h)]
    boxes, x = [], 0
    for a in aspects:
        boxes.append((x, 0, a, 1))
        x += a + gap
    return boxes


def _aspect(path):
    with Image.open(path) as im:
        w, h = im.size
    return w / h


def build(slides, output, reference=None):
    """Write the raw deck for `slides` (parse_storyboard output). Returns math warnings."""
    prs = Presentation(str(reference)) if reference else Presentation()
    if not reference:
        prs.slide_width, prs.slide_height = SLIDE_W, SLIDE_H
        _fix_layout_geometry(prs)
    slide_w, slide_h = prs.slide_width, prs.slide_height
    unmapped = []
    for story in slides:
        content = split_block(story['block'], unmapped)
        cover = story['layout'] == 'cover' or story['id'].upper() == 'COVER'
        title = plain_title(story['title'], unmapped)
        if cover:
            slide = prs.slides.add_slide(_layout(prs, 'Title Slide', 0))
            slide.shapes.title.text = title
            sub = slide.placeholders[1] if len(slide.placeholders) > 1 else None
            if not reference:
                t = slide.shapes.title
                t.left, t.top, t.width, t.height = Inches(0.8), Inches(2.2), slide_w - Inches(1.6), Inches(1.6)
                t.text_frame.word_wrap = True
                for para in t.text_frame.paragraphs:
                    para.alignment = PP_ALIGN.CENTER
                    for run in para.runs:
                        run.font.size, run.font.bold = Pt(36), True
            if sub is not None:
                tf = sub.text_frame
                tf.clear()
                first = True
                for p in content['paragraphs']:
                    para = tf.paragraphs[0] if first else tf.add_paragraph()
                    first = False
                    add_inline_runs(para, p['text'])
                    para.alignment = PP_ALIGN.CENTER
                    _no_bullet(para)
                if not reference:
                    sub.left, sub.top, sub.width, sub.height = Inches(0.8), Inches(4.0), slide_w - Inches(1.6), Inches(1.4)
        else:
            slide = prs.slides.add_slide(_layout(prs, 'Title and Content', 1))
            slide.shapes.title.text = title
            body = next((ph for ph in slide.placeholders if ph.placeholder_format.idx != 0), None)
            if body is not None:
                tf = body.text_frame
                tf.clear()
                first = True
                for p in content['paragraphs']:
                    para = tf.paragraphs[0] if first else tf.add_paragraph()
                    first = False
                    add_inline_runs(para, p['text'])
                    if p['level']:
                        para.level = 1
                    if not p['bullet']:
                        _no_bullet(para)
            if content['table']:
                rows = content['table']
                cols = max(len(r) for r in rows)
                shape = slide.shapes.add_table(len(rows), cols, Inches(0.5), Inches(2.5),
                                               slide_w - Inches(1.0), Inches(0.4) * len(rows))
                for r, row in enumerate(rows):
                    for c in range(cols):
                        cell = shape.table.cell(r, c)
                        cell.text = convert_math(row[c], unmapped) if c < len(row) else ''
            paths = story['paths']
            if paths:
                aspects = [_aspect(p) for p in paths]
                scale = Inches(3.0)
                for path, (x, y, w, h) in zip(paths, arrangement(story['layout'], aspects)):
                    slide.shapes.add_picture(path, int(Inches(0.3) + x * scale), int(Inches(2.0) + y * scale),
                                             width=max(int(w * scale), 1), height=max(int(h * scale), 1))
        if content['notes']:
            slide.notes_slide.notes_text_frame.text = '\n'.join(content['notes'])
    prs.save(str(output))
    return sorted(set(unmapped))
