---
name: 5a-ppt-quick-assembly
description: "DEPRECATED 2026-09-29 — merged into 4-mk_quickview (Share step, Mode B; same assemble_figures.py). Kept only for reference; do not trigger. Formerly: Assemble existing local figures into PowerPoint slides exactly as the user described them, with no story design. Use for requests like 'make 3 slides: Full, West, East, each with raw / deseasonalized / 12m-smoothed stacked vertically, figures from <dir>'. Resolves filenames deterministically, writes a minimal storyboard, then hands it to 6-ppt-create for rendering. Use 5-ppt-design instead when the slide story, order, or grouping must be decided."
---

# ppt_quick_assembly — Fast Figure-to-Slides Skill

> **Deprecated 2026-09-29.** Use `4-mk_quickview` → *Share step, Mode B*. It runs the same
> `assemble_figures.py`, then `md_to_slides.py --render-only` (regression-tested on the
> Full/West/East × raw/deseasonalized/12m example: identical 3-slide vstack-3 output).

## Purpose

Turn a compact natural-language request into a PPTX of **existing** local figures, preserving the
user's slide count, grouping, ordering and layout verbatim.

```
user request → parse intent → resolve files (script) → minimal storyboard → 6-ppt-create → PPTX
```

This skill makes **no content decisions and no scientific interpretation**. It is the cheap path.

**Use `5-ppt-design` instead** when the user wants the model to decide the story, slide order,
figure grouping, bullets or conclusions. This skill only executes an explicit arrangement.

---

## Authority Rule (overrides all layout heuristics)

**Explicit user instructions beat every generic heuristic, including those in `5-ppt-design`.**

- User says `Full / West / East = separate slides` → three slides. Never merge them, even though
  the companion-figure rule in `5-ppt-design` would normally put them on one slide.
- User says `vertical stacked` → `vstack-2` / `vstack-3`, even if the aspect-ratio breakeven
  (A = 2.3) would suggest `hstack-*`. Note the mismatch in one line; do not override it.
- Only when the user gave **no** layout instruction does the aspect rule decide (`"layout": "auto"`).

**Never add unrequested slides or content.** No cover slide, no outline slide, no summary slide,
no bullets, no speaker notes, no extra figures, no interpretation — unless the user asks for them.

---

## Files

| File | Role |
|---|---|
| `assemble_figures.py` | Resolves the (slide × role) figure matrix, writes storyboard + `*.index.json` |
| `fill_datablock.py` | Fills 6-ppt-create's DATA BLOCK from `*.index.json` (token-saving convenience only) |

Interpreter: `/home/users/tg932198/.conda/envs/amoc/bin/python` (has PIL and python-pptx).
Skill directory works from both `~/.claude/skills/` (Claude Code) and `~/.agents/skills/` (Codex) —
they are the same directory via symlink. Refer to it as `$SKILL_DIR` below.

---

## Step 1 — Parse intent (LLM, keep it short)

Extract only:

- **figure directory** (absolute)
- **slide groups** — one slide per group, in the user's order (e.g. Full, West, East)
- **figure roles** — the rows/columns within each slide, in the user's order (e.g. raw,
  deseasonalized, 12m smooth)
- **layout** if stated (`vertical stacked` → `vstack-N`, `side by side` → `hstack-N`)
- **example filenames** the user supplied — these are the matching key, use them
- optional: presentation title / section-tag prefix, output filename

Do not build a plan document, do not enumerate the directory by hand, do not ask questions that
`assemble_figures.py` can answer.

## Step 2 — Write the spec JSON

Write `spec.json` to the scratchpad (or storyboard directory):

```json
{
  "dir": "/absolute/figure/directory",
  "topic": "osnap_amoc_sections",
  "title": "OSNAP",
  "layout": "vstack-3",
  "figure_height": "13/14",
  "groups": [
    {"name": "Full", "tokens": ["full"]},
    {"name": "West", "tokens": ["west"]},
    {"name": "East", "tokens": ["east"]}
  ],
  "roles": [
    {"name": "raw",            "example": "amoc_timeseries_east_moc_sigma0_full_range.png"},
    {"name": "deseasonalized", "example": "amoc_anomalies_east_moc_sigma0_12m_smooth_obs_range.png"},
    {"name": "12m-smooth",     "example": "amoc_density_east_moc_sigma0_full_range_12m_smooth.png"}
  ]
}
```

Field reference:

| Field | Meaning |
|---|---|
| `groups` | One slide each, in order. `tokens` = filename aliases for that group (e.g. `["west","w"]`) |
| `roles` | Figures within each slide, in order |
| `roles[].example` | **Preferred.** One real filename; the script substitutes the group token to build the other slides |
| `roles[].include` / `exclude` | Fallback when no example exists: required / forbidden filename tokens |
| `roles[].shared` | `true` = the same file appears on every slide (only for examples with no group token) |
| `layout` | Explicit layout tag, or `"auto"` (aspect ≥ 2.3 → vstack, else hstack) |
| `figure_height` | Figure region fraction, default `13/14` — correct for bullet-free slides |
| `overrides` | `{"Full|raw": "filename.png"}` — set **only** after the user picks from an ambiguity list |
| `title` | Section-tag prefix: tag becomes `"<title> · <group>"` |

## Step 3 — Resolve (deterministic, no LLM reasoning)

```bash
$PY $SKILL_DIR/assemble_figures.py spec.json          # dry run: prints the matrix
```

The script tokenizes filenames on `_`/`-`, tests every group-token position in the example, and
keeps the substitution hypothesis that resolves the most groups. Files carrying another group's
alias are excluded from a group's candidates.

Handle the outcome:

- **all cells resolved** → go to Step 4.
- **`[MISSING]`** → report the missing slide × role plainly. Do not substitute a different figure.
- **`[AMBIGUOUS]`** → show the (small) candidate list and ask the user to choose; then add
  `"overrides"` and re-run. Never pick silently.

Exit code 2 means unresolved — nothing is written.

## Step 4 — Write the storyboard

```bash
$PY $SKILL_DIR/assemble_figures.py spec.json --write -o <topic>_<dd-mm-yyyy>.md
```

Produces, next to each other:

- `<topic>_<dd-mm-yyyy>.md` — minimal storyboard, absolute figure paths, one `## ` heading per
  slide, `<!-- layout: -->` / `<!-- figure-height: -->` / `<!-- section-tag: -->` annotations, and
  the `<!-- figures: a, b, c -->` line when the layout is `hstack-3`. No cover, no outline, no bullets.
- `<topic>_<dd-mm-yyyy>.index.json` — slide index → tag, layout, figure paths, aspects. This is
  6-ppt-create's DATA BLOCK, precomputed.

Show the matrix and the storyboard path to the user.

## Step 5 — Render with 6-ppt-create (do not reimplement)

Continue immediately by following `$SKILL_DIR/../6-ppt-create/SKILL.md` against the generated
storyboard. In Claude Code that is `/6-ppt-create <storyboard>`; in Codex, read that SKILL.md and
execute its phases. Two shortcuts apply because the storyboard was machine-generated:

- **Phase 1** — aspect detection and slide indexing are already in `*.index.json`; still run the
  `prs.slides` title check after export.
- **Phase 4** — instead of filling the DATA BLOCK by hand:
  ```bash
  $PY $SKILL_DIR/fill_datablock.py <topic>_<dd-mm-yyyy>.index.json
  $PY postprocess_slides.py
  ```
  This sets `BULLET_PLACEHOLDERS = False`, which collapses the empty bullet band so the figures use
  the full slide height. Without it, bullet-free slides render literal `[Bullet 1]` placeholders.

Phases 2 and 3 (format + pandoc export) run unchanged.

---

## Worked example

Request:

> create 3 slides covering section: full, west, east, respectively. 3 rows: raw amoc strength,
> deseasonalized, 12-month smoothed. vertical stacked. figure path: `.../osnap/straitflux`

Spec: the JSON above. Result: exactly 3 slides, `vstack-3`, section tags `OSNAP · Full`,
`OSNAP · West`, `OSNAP · East`. Resolved matrix:

| slide | raw | deseasonalized | 12m-smooth |
|---|---|---|---|
| Full | `amoc_timeseries_full_moc_sigma0_full_range.png` | `amoc_anomalies_full_..._12m_smooth_obs_range.png` | `amoc_density_full_..._full_range_12m_smooth.png` |
| West | `amoc_timeseries_west_...` | `amoc_anomalies_west_...` | `amoc_density_west_...` |
| East | `amoc_timeseries_east_...` | `amoc_anomalies_east_...` | `amoc_density_east_...` |

Note the trap the substitution logic handles: the example `amoc_timeseries_east_moc_sigma0_full_range.png`
contains the token `full` inside `full_range`, but only the `east` position is the group token.

---

## Safety Constraints

- Steps 1–3 write nothing except the spec file; the storyboard appears only in Step 4.
- Never invent a filename — every path is verified to exist on disk before it is written.
- Never resolve an ambiguity by picking the first candidate.
- Never add cover / outline / summary slides, bullets, notes or interpretation unless asked.
- Never modify source figures, notes, or an existing storyboard; write a new dated file.
- Do not duplicate any of 6-ppt-create's rendering logic here.
