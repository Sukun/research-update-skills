---
name: 7-ppt-to-5
description: "Read a hand-edited PowerPoint back into the storyboard it was rendered from: text edits are merged into <name>.md, positions/sizes/crops/font sizes go to <name>.layout.json, so the next 6-ppt-create render reproduces the hand layout. Use after a deck from 6-ppt-create was moved, resized, reordered, retitled or rewritten in PowerPoint, or once to import a legacy deck. Never writes a PPTX and never edits scientific reports."
---

# ppt_roundtrip — Revise flow

## Where it sits

```
Create:  /5-ppt-design → <name>.md → /6-ppt-create → <name>.pptx + <name>.layout.json
Revise:  edit <name>.pptx in PowerPoint → /7-ppt-to-5 → <name>.md + <name>.layout.json → /6-ppt-create
```

`<name>.md` holds the words, `<name>.layout.json` holds where every shape sits, the PPTX is the view.
This skill updates both source files in place, so the next render shows what the author left in
PowerPoint. `/5-ppt-design` is not part of the revise loop; use it only to change the story.

Makes **no content decisions** and **no scientific interpretation**. It writes back only what is in
the deck. It never edits `docs/*.md` scientific reports.

Interpreter: the project Python with python-pptx (`/opt/miniconda3/envs/myenv/bin/python` on the Mac,
`/home/users/tg932198/.conda/envs/amoc/bin/python` on the cluster). The scripts import
`../6-ppt-create/layout_record.py`, `render_storyboard.py` and `build_pptx.py`; keep the skills side by side.

---

## Revise (stamped deck from 6-ppt-create)

```bash
$PY $SKILL_DIR/read_deck.py EDITED.pptx --storyboard NAME.md --project-root /abs/project [--dry-run]
```

- **Text** → merged into `NAME.md` (previous copy saved as `NAME.md.bak`). A slide's title, body,
  Notes or figure list is rewritten only where the deck differs from what the storyboard renders, so
  annotations, comments, Markdown emphasis and LaTeX on untouched parts stay. Slides follow the deck
  order; slides deleted in the deck are removed; a duplicated slide copies its original under id
  `<id>-d1`. Bold typed in PowerPoint comes back as `**…**`. Extra lines typed into a title box move
  to the top of the body (a heading is one line).
- **Positions** → `NAME.layout.json`, recorded from the edited deck (see 6-ppt-create, "Layout file").
- **Newer edit wins.** The layout file holds, per slide, the storyboard hash and the deck text
  hash from the last render or read. A slide edited only in PowerPoint takes the deck text; edited
  only in the storyboard keeps the storyboard text; edited in both takes the version from the file
  with the newer modification time, since that is the author's latest intent. Slide order and
  membership follow the same rule. No flag is needed; `--layout-only` keeps all storyboard text.
  Every decision is listed per slide, and `NAME.md.bak` holds the previous storyboard.
- Then re-render with `/6-ppt-create` to the same name and check `layout_record.py diff`.

Unresolved pictures (pasted images with no known source) are extracted to `assets/unresolved/`
beside the storyboard, referenced from the `.md`, and restored by hash on the next render.

## Bootstrap (legacy unstamped deck, once)

```bash
$PY $SKILL_DIR/read_deck.py --bootstrap LEGACY.pptx -o NAME.md --project-root /abs/project
```

The deck is the truth: fresh ids `S001, S002, …`, a new `NAME.md` and `NAME.layout.json`. Do not
match a legacy deck against an old storyboard. Re-render through 6-ppt-create to get a stamped deck.

---

## What survives

| Edit in PowerPoint | Comes back |
|---|---|
| Reorder, delete, duplicate slides | Yes, by stamped `slide_id` |
| Retitle, rewrite bullets or Notes, bold a phrase | Yes, into the `.md` |
| Move / resize a title, body, band, caption or figure; change a font size; crop | Yes, into `.layout.json` |
| Replace a figure, insert one from `plots/` | Yes, resolved by sha256; that slide uses the generic layout once |
| Paste an unknown image | Kept as `unresolved_manual_NN`, extracted, position kept |
| Add a new text box | Its text joins the body if the slide had none; its position is not kept |
| Colours, shadows, animations, italics, charts/SmartArt | No (charts/SmartArt are reported) |

---

## Rules

**Identity.** One authoritative `slide_id` per slide, on the *identity anchor* — the section chip,
else the cover title, else the takeaway band. Figures carry `figure_id`/`source`/`sha256` but
**never a trusted parent slide id**: a picture keeps its old stamp when cut and pasted, so slide
membership is always decided by which slide the picture is currently on.

**Figure resolution order:** stamped `src` (hash-verified) → `figure_registry.json` → `plots/**`
scan → `unresolved_manual_NN`. A stamped source whose hash no longer matches is reported
`refreshed` (the file was re-plotted), not silently trusted.

**Never guess.** If two slides cannot be told apart, leave them unmatched and say so. An unresolved
figure is always extracted and reported, never dropped and never replaced by a plausible substitute.

**Field mapping:** title placeholder → `## ` heading; takeaway band → body bullets (paragraph level
kept); Notes → `::: notes`; pictures → `![]()` lines. The section label is advisory and never
written back; section tags stay as authored in the `.md`.

---

## Sharing check

Merged text stays verbatim. After merging, scan titles, takeaways and notes against the [sharing copy rules](../6-ppt-create/references/sharing-copy.md) and list breaches by slide ID (paths or links, status/to-do labels, "not regenerated from code", titles longer than one line). Do not rewrite them here; the author fixes them in the storyboard or via `/5-ppt-design`.

## Reporting

After running, report: slide count, figure count, how many figures resolved by each route, any
unresolved figures (with the mandatory provenance-unknown line), any slide whose id was positional
rather than stamped, and the per-slide change list (title, body, notes, figures, added, removed,
order). Do not summarise the science.

---

## Safety Constraints

- Read-only against the PPTX — this skill never writes a `.pptx`.
- Never modifies `docs/*.md` scientific reports or source figures. It updates only the storyboard
  it was given and its `.layout.json`, and keeps `NAME.md.bak`.
- Never fabricates a figure source; unresolved stays unresolved.
- Rendering belongs to 6-ppt-create — do not duplicate any of it here.
