---
name: 7-ppt-to-5
description: "Recover a hand-edited PowerPoint back into a storyboard Markdown file and a machine-readable deck.json. Use after a deck rendered by 6-ppt-create has been manually reordered, retitled, re-figured, or rewritten in PowerPoint, or to import a legacy deck as a baseline. Reads only — never renders PPTX and never edits scientific reports."
---

# ppt_roundtrip — Reverse Slide Reader

## Purpose

Close the loop. `5/5a → 6-ppt-create` goes Markdown → PPTX; this skill goes **edited PPTX →
storyboard Markdown + JSON**, so the reorganisation done by hand in PowerPoint is not lost.

```
storyboard .md → 6-ppt-create → PPTX → MANUAL EDITING → 7-ppt-to-5 → deck.json + deck_revised.md
```

Makes **no content decisions** and **no scientific interpretation**. It writes back only what is in
the deck: order, title, takeaway, figures, notes. It never edits `docs/*.md` scientific reports —
those stay canonical; promoting a presentation interpretation into them is a separate, explicit step.

Interpreter: `/home/users/tg932198/.conda/envs/amoc/bin/python`. `$SKILL_DIR` works from both
`~/.claude/skills/` and `~/.agents/skills/` (same directory via symlink), so Codex uses it unchanged.

---

## Two entry paths

**Normal (stamped deck)** — rendered by 6-ppt-create with `STAMP_IDS = True`, so every slide carries
a stable `slide_id` and every picture a `figure_id` + source + sha256. Identity is exact.

```bash
$PY $SKILL_DIR/read_deck.py edited.pptx -o deck.json \
      --project-root /abs/project --prior previous_deck.json
$PY $SKILL_DIR/write_storyboard.py deck.json -o deck_revised.md
```

**Bootstrap (legacy unstamped deck)** — a deck made before stamping existed. Do **not** try to match
it against an old storyboard: import it once, treat the deck as the truth, mint fresh ids
`S001, S002, …`, then re-render through 6-ppt-create to get a stamped deck.

```bash
$PY $SKILL_DIR/read_deck.py --bootstrap legacy.pptx -o baseline.json --project-root /abs/project
$PY $SKILL_DIR/write_storyboard.py baseline.json -o baseline.md
```

`--prior` carries `unresolved_manual_NN` numbering and the revision counter forward. Always pass it
when a previous `deck.json` exists.

---

## What survives, and what does not

| Edit | Recovered |
|---|---|
| Reorder, delete, duplicate slides | Yes — ids preserved; a duplicate gets `S00Nd1` |
| Retitle a slide, rewrite a takeaway | Yes, verbatim |
| Move / resize / **crop** a figure | Figure identity survives; geometry recorded in JSON |
| Replace a figure, insert one from `plots/` | Yes, resolved by sha256 |
| Paste an unknown image | Kept as `unresolved_manual_NN`, extracted to `assets/unresolved/` |
| Cut a figure from one slide onto another | Yes — membership follows the slide it is **on now** |
| Fonts, colours, shadows, animations, charts/SmartArt | No — charts/SmartArt emit a `<!-- TODO -->` marker |

> **Round-trip preserves the presentation *story*. Exact visual geometry is recorded in `deck.json`
> but is not necessarily reproduced by the standard renderer.** Re-rendering `deck_revised.md`
> reapplies the standard layout rules, so a figure hand-pulled from 80% to 92% width will not come
> back at 92%.

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

**Field mapping** (frozen — chip depth varies from 1 to 4 `·`-separated parts):
- `title` = the **full chip text, verbatim** → round-trips to the `## ` heading
- `section` = part 2 when ≥2 parts — **derived and advisory only**, never written back
- `takeaway` = the bullet-band text, `null` when absent

---

## Reporting

After running, report: slide count, figure count, how many figures resolved by each route, any
unresolved figures (with the mandatory provenance-unknown line), and any slide whose id was
positional rather than stamped. Do not summarise the science.

---

## Safety Constraints

- Read-only against the PPTX — this skill never writes a `.pptx`.
- Never modifies `docs/*.md` scientific reports, source figures, or an existing storyboard; output
  goes to new files.
- Never fabricates a figure source; unresolved stays unresolved.
- Rendering belongs to 6-ppt-create — do not duplicate any of it here.
