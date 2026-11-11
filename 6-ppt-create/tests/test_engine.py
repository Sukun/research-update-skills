"""Direct python-pptx engine (build_pptx.py), math mapping and the md_to_slides adapter. No Pandoc needed."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image
from pptx import Presentation

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


renderer = load('renderer_e', SKILL / 'render_storyboard.py')
qa = load('qa_e', SKILL / 'qa_slides.py')
adapter = load('adapter_e', SKILL / 'md_to_slides.py')
from latex_text import convert_math  # noqa: E402

STORY = '''---
---

<!-- slide-id: COVER -->
## Cover title

- subtitle line

---

<!-- slide-id: H2 -->
<!-- layout: hstack-2 -->
<!-- section-tag: "Sec" color="teal" -->
## Two side by side

- one
- two

![](land.png)
![](land2.png)

::: notes
note h2
:::

---

<!-- slide-id: V2 -->
<!-- layout: vstack-2 -->
## Two stacked

- one

![](wide.png)
![](wide2.png)

---

<!-- slide-id: T3 -->
<!-- layout: hstack-3 -->
<!-- figures: land.png, land2.png, wide.png -->
<!-- section-tag: "Sec" color="teal" -->
## Three figures

- one

![](land.png)

---

<!-- slide-id: WIDE -->
<!-- layout: figure-dominant -->
## Wide with three bullets

- a
- b
- c

![](wide.png)

---

<!-- slide-id: SQ -->
<!-- layout: figure-right-text-left -->
## Square

- left

![](sq.png)

---

<!-- slide-id: LONG -->
<!-- layout: figure-dominant -->
<!-- section-tag: "Section" color="crimson" -->
## A deliberately long slide title that must wrap onto two lines without hiding anything or colliding

- bullet

![](land.png)

---

<!-- slide-id: MATH -->
<!-- layout: text-only -->
## Math

- $T=-\\Delta D/\\ln\\gamma$ and $\\foo$

::: notes
first note line
second note line
:::
'''
EXPECT = {'COVER': 0, 'H2': 2, 'V2': 2, 'T3': 3, 'WIDE': 1, 'SQ': 1, 'LONG': 1, 'MATH': 0}


@pytest.fixture()
def deck(tmp_path, capfd):
    for i, (name, size) in enumerate([('land', (1600, 1000)), ('land2', (1600, 1000)), ('wide', (2400, 800)),
                                      ('wide2', (2400, 800)), ('sq', (1000, 1000))]):
        Image.new('RGB', size, (120 + 20 * i, 160, 200)).save(tmp_path / (name + '.png'))
    sb = tmp_path / 'sb.md'
    sb.write_text(STORY)
    out = tmp_path / 'out' / 'deck.pptx'
    renderer.render(sb, out, project_root=tmp_path)
    return Presentation(out), tmp_path, capfd.readouterr().out


def test_slide_and_picture_counts_match_storyboard(deck):
    prs, _, _ = deck
    slides = renderer.parse_storyboard(deck[1] / 'sb.md')
    assert len(prs.slides) == len(slides)
    for slide, story in zip(prs.slides, slides):
        assert len([s for s in slide.shapes if s.shape_type == 13]) == EXPECT[story['id']], story['id']


def test_titles_present_even_with_section_tag(deck):
    prs, _, _ = deck
    for slide, story in zip(prs.slides, renderer.parse_storyboard(deck[1] / 'sb.md')):
        assert slide.shapes.title.text_frame.text == story['title']
    tagged = prs.slides[1]
    labels = [s for s in tagged.shapes if qa.metadata(s).get('role') == 'section']
    assert len(labels) == 1 and labels[0].text_frame.text == 'Sec'
    size = labels[0].text_frame.paragraphs[0].runs[0].font.size.pt
    assert 12 <= size <= 14 and labels[0].left > prs.slide_width / 2


def test_no_overlaps_and_qa_clean(deck):
    prs, _, _ = deck
    assert not [x for x in qa.structural_checks(prs) if x['severity'] == 'error']


def test_notes_math_and_warning(deck):
    prs, _, out = deck
    math = prs.slides[7]
    text = '\n'.join(s.text_frame.text for s in math.shapes if s.has_text_frame)
    assert 'T=-ΔD/ln γ' in text and '$' not in text
    assert math.notes_slide.notes_text_frame.text == 'first note line\nsecond note line'
    assert '\\foo' in out and 'not mapped' in out


def test_identity_and_registry_contract(deck):
    prs, root, _ = deck
    ids = [qa.slide_id(s, i) for i, s in enumerate(prs.slides)]
    assert ids == list(EXPECT)
    registry = json.loads((root / 'out' / 'figure_registry.json').read_text())
    assert len(registry) == 5
    pic = next(s for s in prs.slides[1].shapes if s.shape_type == 13)
    assert all(qa.metadata(pic).get(k) for k in ('sha', 'fid', 'src'))


def test_text_band_clear_of_title_and_figures(deck):
    prs, _, _ = deck
    for slide in list(prs.slides)[1:]:
        title = slide.shapes.title
        for s in slide.shapes:
            if s.shape_id != title.shape_id and (s.shape_type == 13 or (s.has_text_frame and s.text_frame.text.strip()
                                                          and qa.metadata(s).get('role') != 'section')):
                assert s.top >= title.top + title.height - 1, (qa.slide_id(slide, 0), s.name)


def test_latex_mapping():
    unmapped = []
    assert convert_math(r'$\sum_i x_i^2 \le \alpha \times \beta$', unmapped) == '∑_i x_i² ≤ α × β'
    assert convert_math(r'$T \approx 95$ d, $e^{-t}$', unmapped) == 'T ≈ 95 d, e^(-t)'
    convert_math(r'$\weird$', unmapped)
    assert unmapped == ['\\weird']


def test_adapter_section_aliases_and_render(tmp_path):
    Image.new('RGB', (800, 500), 'white').save(tmp_path / 'f.png')
    (tmp_path / 'rec.md').write_text('# Topic\n\nSub\n\n# L1 · Summary\n\n## One\n\n- b\n\n![](f.png)\n\n# L2 · Evidence\n\n## Skip\n\n- no\n')
    (tmp_path / 'rec2.md').write_text('# Topic\n\nSub\n\n# Summary\n\n## Only\n\n- b\n\n![](f.png)\n')
    for name, title in [('rec.md', 'One'), ('rec2.md', 'Only')]:
        out = tmp_path / (name + '.story.md')
        result = subprocess.run([sys.executable, str(SKILL.parent / '4-mk_quickview' / 'md_to_slides.py'),
                                 str(tmp_path / name), '--section', 'Summary', '-o', str(out), '--render'],
                                capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        prs = Presentation(out.with_suffix('.pptx'))
        assert [s.shapes.title.text_frame.text for s in prs.slides] == ['Topic', title]


# ---------------------------------------------------------------- figure-full-width

FW_STORY = '''---
---

<!-- slide-id: FW -->
<!-- layout: figure-full-width -->
<!-- section-tag: "Sec" color="teal" -->
## Full width figure

- first bullet
- second bullet
- third bullet
- fourth bullet
- fifth bullet

![](wide25.png)

[ ] caption line

::: notes
authored note
:::
'''


@pytest.fixture()
def fw_deck(tmp_path):
    Image.new('RGB', (2500, 1000), (90, 160, 200)).save(tmp_path / 'wide25.png')
    sb = tmp_path / 'fw.md'
    sb.write_text(FW_STORY)
    out = tmp_path / 'out' / 'fw.pptx'
    renderer.render(sb, out, project_root=tmp_path)
    return Presentation(out).slides[0], Presentation(out)


def test_full_width_bullets_beyond_n_go_to_notes(fw_deck):
    slide, _ = fw_deck
    body = [s for s in slide.shapes if s.has_text_frame and s.text_frame.text.startswith('first')][0]
    kept = [p.text for p in body.text_frame.paragraphs if p.text.strip()]
    assert 1 <= len(kept) <= 3 and kept == ['first bullet', 'second bullet', 'third bullet'][:len(kept)]
    notes = slide.notes_slide.notes_text_frame.text.splitlines()
    assert notes[0] == 'Also on the slide:'
    spilled = ['first bullet', 'second bullet', 'third bullet', 'fourth bullet', 'fifth bullet'][len(kept):]
    assert notes[1:1 + len(spilled)] == spilled and 'authored note' in notes
    caption = [s for s in slide.shapes if qa.metadata(s).get('role') == 'caption']
    assert len(caption) == 1 and caption[0].text_frame.text == '[ ] caption line'
    assert caption[0].text_frame.paragraphs[0].runs[0].font.size.pt <= 12


def test_full_width_wide_image_gets_75_percent_and_keeps_aspect(fw_deck):
    slide, prs = fw_deck
    pic = next(s for s in slide.shapes if s.shape_type == 13)
    content_w = prs.slide_width - 2 * 457200
    assert pic.width >= 0.75 * content_w and pic.width <= content_w + 1
    assert abs(pic.width / pic.height - 2.5) < 0.01
    assert pic.crop_left == pic.crop_right == pic.crop_top == pic.crop_bottom == 0
    assert pic.left >= 457200 - 1 and pic.left + pic.width <= prs.slide_width - 457200 + 1
    assert abs((pic.left + pic.width / 2) - prs.slide_width / 2) < 2
    assert pic.top + pic.height <= prs.slide_height
