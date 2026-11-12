"""Revise loop: render -> edit in PowerPoint -> read_deck -> render again.

Run: python -m pytest tests  (python-pptx and Pillow required)."""
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image
from pptx import Presentation
from pptx.util import Inches

HERE = Path(__file__).resolve().parents[1]
SKILL6 = HERE.parent / "6-ppt-create"
sys.path.insert(0, str(SKILL6))
import layout_record  # noqa: E402
import render_storyboard  # noqa: E402

STORY = """---
---

<!-- slide-id: A -->
<!-- layout: text-only -->
<!-- section-tag: "1 Intro" color="teal" -->
## First finding is $\\alpha$-stable

- One **bold** point.
- Two.

::: notes
Notes for A.
:::

---

<!-- slide-id: B -->
<!-- layout: figure-dominant -->
<!-- section-tag: "2 Data" color="purple" -->
## Second slide

- Figure point.

![](fig.png)

---

<!-- slide-id: C -->
<!-- layout: text-only -->
## Third slide

- Gone soon.
"""


def run_read(*args):
    return subprocess.run([sys.executable, str(HERE / "read_deck.py"), *map(str, args)],
                          capture_output=True, text=True)


def keyed(slide):
    return {k: sh for k, _, sh in layout_record.keyed_shapes(slide)}


@pytest.fixture
def rendered(tmp_path):
    Image.new("RGB", (800, 400), (90, 120, 160)).save(tmp_path / "fig.png")
    md = tmp_path / "talk.md"
    md.write_text(STORY)
    out = tmp_path / "talk.pptx"
    render_storyboard.render(md, out, project_root=tmp_path)
    return md, out


def test_render_records_layout_beside_storyboard(rendered):
    md, out = rendered
    lay = layout_record.load(md.with_suffix(".layout.json"))
    assert [s["slide_id"] for s in lay["slides"]] == ["A", "B", "C"]
    assert lay["storyboard_sha256"] == layout_record.sha256_file(md)
    assert layout_record.diff(out, lay) == []


def test_edit_read_render_keeps_text_and_positions(rendered, tmp_path):
    md, out = rendered
    prs = Presentation(out)
    a, b, c = prs.slides
    keyed(a)["title"].text_frame.text = "First finding holds"
    pic = next(sh for k, sh in keyed(b).items() if k.startswith("figure:"))
    pic.left, pic.top, pic.width = Inches(6), Inches(3), Inches(5)
    keyed(b)["takeaway"].left = Inches(0.4)
    b.notes_slide.notes_text_frame.text = "New notes for B."
    lst = prs.slides._sldIdLst                      # delete C, move B first
    prs.part.drop_rel(lst[2].rId)
    lst.remove(lst[2])
    lst.insert(0, lst[1])
    prs.save(out)
    edited = layout_record.record(out)

    res = run_read(out, "--storyboard", md, "--project-root", tmp_path)
    assert res.returncode == 0, res.stderr
    text = md.read_text()
    assert "## First finding holds" in text
    assert "One **bold** point." in text            # untouched slide body keeps its markup
    assert "New notes for B." in text and "Gone soon" not in text
    assert text.index("slide-id: B") < text.index("slide-id: A")
    assert (md.with_name("talk.md.bak")).read_text() == STORY

    again = tmp_path / "again.pptx"
    render_storyboard.render(md, again, project_root=tmp_path)
    assert layout_record.diff(again, edited) == []

    # second read of an unchanged deck changes nothing
    res = run_read(again, "--storyboard", md, "--project-root", tmp_path)
    assert "storyboard text unchanged" in res.stdout


def _touch(path, t):
    import os
    os.utime(path, (t, t))


def test_newer_edit_wins_per_slide(rendered, tmp_path):
    md, out = rendered
    # storyboard edit on A, deck edit on B: both kept whatever the file times
    md.write_text(md.read_text().replace("- Two.", "- Two, edited in the storyboard."))
    prs = Presentation(out)
    keyed(prs.slides[1])["title"].text_frame.text = "Second slide, retitled in PowerPoint"
    prs.save(out)
    _touch(md, 2_000_000_000)
    _touch(out, 1_000_000_000)
    res = run_read(out, "--storyboard", md, "--project-root", tmp_path)
    assert res.returncode == 0, res.stderr
    text = md.read_text()
    assert "edited in the storyboard" in text and "retitled in PowerPoint" in text


def test_slide_edited_in_both_takes_newer_file(rendered, tmp_path):
    md, out = rendered
    story = md.read_text()
    md.write_text(story.replace("## Second slide", "## Second slide from the storyboard"))
    prs = Presentation(out)
    keyed(prs.slides[1])["title"].text_frame.text = "Second slide from PowerPoint"
    prs.save(out)
    _touch(md, 1_000_000_000)
    _touch(out, 2_000_000_000)                     # deck newer -> deck wins
    res = run_read(out, "--storyboard", md, "--project-root", tmp_path, "--dry-run")
    assert "the deck is newer" in res.stdout
    _touch(md, 3_000_000_000)                      # storyboard newer -> storyboard wins
    res = run_read(out, "--storyboard", md, "--project-root", tmp_path)
    assert res.returncode == 0, res.stderr
    assert "## Second slide from the storyboard" in md.read_text()
    assert "the storyboard is newer" in res.stdout


def test_layout_only_keeps_storyboard_text(rendered, tmp_path):
    md, out = rendered
    md.write_text(md.read_text().replace("Two.", "Two, edited in the storyboard."))
    res = run_read(out, "--storyboard", md, "--project-root", tmp_path, "--layout-only")
    assert res.returncode == 0
    assert "edited in the storyboard" in md.read_text()
