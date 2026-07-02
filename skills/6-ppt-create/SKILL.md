---
name: 6-ppt-create
description: "Pure mechanical renderer: reads a ppt_design storyboard file (<topic>_<dd-mm-yyyy>.md) and produces a .pptx via Pandoc + python-pptx post-processing. Validates titles, detects figure aspect ratios, applies layout rules. No content decisions — all story/layout intent comes from the storyboard."
license: MIT
model: haiku
---

# ppt_create — Slide Renderer Skill

## Purpose

Convert a `ppt_design` storyboard file (output of skill 5) into a `.pptx` presentation via Pandoc,
followed by python-pptx post-processing for section tags, title clearing, font sizes, table styling,
figure layout adjustments, and 3-column layouts.
This skill makes **no content decisions** — everything is specified by the storyboard's layout annotations.

Four-phase workflow:
1. **Validate** — check titles, figure paths, layout tags
2. **Format** — apply layout rules in-place to the storyboard file
3. **Export** — run pandoc → `.pptx`
4. **Post-process** — python-pptx: section tag chips, title clearing, font sizes, table styling, figure layout, 3-column slides

---

## How To Invoke

```
/6-ppt-create <path-to-storyboard.md>
```

---

## Parameters

| # | Parameter | Default | Description |
|---|-----------|---------|-------------|
| 1 | `STORYBOARD` | Auto-detect: most recent `*_<dd-mm-yyyy>.md` in current dir | Path to ppt_design storyboard file |
| 2 | `REFERENCE_PPTX` | `reference.pptx` in storyboard directory if exists, else Pandoc default | Custom PowerPoint template |
| 3 | `OUTPUT` | Same name as storyboard, `.pptx` extension | Output PPTX filename |

If parameters are omitted, apply defaults. Do not ask — proceed to Phase 1.

---

## Slide Title Rules

### Pandoc requires a `## Heading` on every slide

Pandoc PPTX output places all content (bullets, images) on a new slide only when anchored by a `## Heading`.
Without a heading, each block element goes on a separate continuation slide.

**All slides — including content slides — must have a `## Heading`.**

- **Cover slide**: the heading is the presentation title (kept visible).
- **Content slides** with a section tag: the heading text equals the section tag label.
  Phase 4 (step 4T) clears this text from the title placeholder so it is invisible;
  the section tag chip acts as the visual slide identifier.

Title length: ≤ 65 chars.
If > limit, shorten and preserve the original in an HTML comment:
```markdown
<!-- original-title: "Full meridional overturning transport at the OSNAP array" -->
## OSNAP Full MOT
```

---

## Figure Layout Rules

### Aspect Ratio Detection (batched)

After collecting all figure paths in Phase 1, detect every aspect ratio in a **single batch script** — do NOT run per-figure subprocesses. Generate and run this script once (fill the `figures` dict from the storyboard parse):

```python
# detect_aspects.py — auto-generated, run once in Phase 1
import json
try:
    from PIL import Image
    figures = {
        # "label": "/abs/path/to/fig.png"  — one entry per unique figure path
    }
    result = {}
    for label, path in figures.items():
        try:
            w, h = Image.open(path).size
            result[label] = round(w / h, 3)
        except Exception:
            result[label] = 1.6  # fallback
    print(json.dumps(result, indent=2))
except ImportError:
    print(json.dumps({}))
```

Capture the JSON output; use it to populate `FIGURES` in the Phase 4 DATA BLOCK and to assign widths from the table below. If detection fails entirely, default aspect = 1.6.

---

### Width Assignment by Aspect Ratio (Pandoc storyboard)

| Figure context | Aspect ratio | Width to apply |
|---|---|---|
| Single figure, no columns (landscape) | > 1.5 | `{width="80%"}` |
| Single figure, no columns (portrait) | 0.65–1.5 | `{width="70%"}` |
| Single figure, ultra-tall portrait | < 0.65 | `{width="INT(48.8×A)%"}` — height-derived: max fig height ≈ 6.5", img_w = 6.5×A, pct = img_w/13.33. Example: A=0.49 → `{width="23%"}` |
| Figure inside a 70% column (`figure-dominant`) | any | `{width="100%"}` |
| Stacked figures `vstack-2/3` | any | `{width="80%"}` |
| Side-by-side `hstack-2`, portrait | 0.65–1.5 | `{width="100%"}` |
| Side-by-side `hstack-2`, ultra-tall portrait | < 0.65 | `{width="INT(100×A)%"}` — height-derived per column (col ≈ 6.5"): pct = 6.5×A/6.5×100. Example: A=0.51 → `{width="50%"}` |
| 3-column `hstack-3` (per column) | any | no width needed — Phase 4D handles in python-pptx |

Note: For `figure-dominant` slides, the `{width="100%"}` storyboard value is only used for initial Pandoc placement.
The postprocess script always overrides figure and text positions to the top-bottom layout (see Layout 3).

### Default Figure-Height Allocation (<= 4 figures)

For layouts with figure count <= 4, unless the storyboard explicitly requests otherwise, Phase 4 sets the figure region from the bottom using the bullet count in the top text band:

| Bullet count in top band | Figure region height (from slide bottom) |
|---|---|
| 1 bullet (or fewer) | `11/14` of slide height |
| 2 bullets | `10/14` of slide height |
| 3 bullets (or more) | `9/14` of slide height |

This rule applies inversely: more bullets -> less figure height.
An explicit storyboard request may override this per slide (see `FIGURE_HEIGHT_OVERRIDE` in Phase 4 DATA BLOCK).
Phase 4 enforces this for all slides with 1-4 pictures, including generic Pandoc picture layouts (e.g. `single`, `hstack-2`, `grid-2x2`) and table-as-figure positioning.

Suggested explicit override syntax in storyboard comments:
`<!-- figure-height: 10/14 -->` (or any fraction in `(0, 1]`), placed inside the target slide block.

---

### Layout 1 — Text only (0 figures)
**Tag**: `<!-- layout: text-only -->`
**Rule**: No figure modifications needed. Bullets at max width.

---

### Layout 2 — Single figure, no bullets (1 figure)
**Tag**: `<!-- layout: single -->`
**Rule**: One figure. Landscape (aspect > 1.5): `{width="80%"}`. Portrait (aspect ≤ 1.5): `{width="70%"}`.

```markdown
![](fig_a.png){width="80%"}
```

---

### Layout 3 — Figure-dominant: text top, figure bottom (1 figure + bullets)
**Tag**: `<!-- layout: figure-dominant -->`
**Visual output**: 1-3 bullet placeholder band in the top half (below section tag), figure fills remaining slide height below.

**Storyboard syntax** (Pandoc input — python-pptx overrides position/size in postprocess):
```markdown
:::: {.columns}
::: {.column width="30%"}
- **Key finding one**
- **Key finding two**
- **Key finding three**
:::
::: {.column width="70%"}
![](fig.png){width="100%"}
:::
::::
```

**Post-processing logic** (runs for all figure-dominant slides regardless of aspect ratio):
- Text band: top half of slide, below section tag, sized for 1-3 bullets (~1.6").
- Figure: centred horizontally below text, both W and H scaled proportionally from detected aspect ratio.
- Overlap fallback: if Phase 4 detects text-band overlap with any picture, reduce body text size stepwise (20 pt -> 18 pt -> 16 pt) until overlap clears.
- Aspect fallback if detection fails: `1.6`. See `reposition_figure_dominant()` in the template.

---

### Layout 5 — Vertical stack (2 figures)
**Tag**: `<!-- layout: vstack-2 -->`
**Trigger**: 2 figures with aspect ratio ≥ 2.0 (e.g. timeseries panels)
**Rule**: Stack vertically. Each figure at `{width="80%"}` to leave side margins.

```markdown
![](fig_a.png){width="80%"}
![](fig_b.png){width="80%"}
```

---

### Layout 6 — Horizontal side-by-side (2 figures)
**Tag**: `<!-- layout: hstack-2 -->`
**Trigger**: 2 figures with aspect ratio ≤ 1.5
**Rule**: Pandoc 2-column, equal width. Each figure at `{width="100%"}`.

```markdown
:::: {.columns}
::: {.column width="50%"}
![](fig_a.png){width="100%"}
:::
::: {.column width="50%"}
![](fig_b.png){width="100%"}
:::
::::
```

---

### Layout 7 — Vertical stack (3 figures)
**Tag**: `<!-- layout: vstack-3 -->`
**Rule**: 3 landscape figures stacked vertically. Each at `{width="80%"}`. Reserve a top bullet placeholder band (1-3 bullets) below section tag.

---

### Layout 8 — 3 portrait figures (3 figures, python-pptx)
**Tag**: `<!-- layout: hstack-3 -->`
**Rule**: Pandoc cannot render 3-column PPTX natively. All three figures go on ONE slide via python-pptx.

**Storyboard format**: list only the first figure as `![]()` (Pandoc anchor). All three paths go in the required `<!-- figures: ... -->` comment on the line immediately after the layout tag (see skill 5 layout tags for the full example):
```markdown
<!-- layout: hstack-3 -->
<!-- figures: path/fig_a.png, path/fig_b.png, path/fig_c.png -->
## Section Tag Label
![](path/fig_a.png){width="30%"}
```

**Phase 4D**: Reads the three paths from `<!-- figures: ... -->`, removes all shapes, places figures equally spaced with proportional W+H sizing, adds section tag chip.

---

### Layout 9 — Focus + context (3 figures: 1 main + 2 thumbnails)
**Tag**: `<!-- layout: focus-context -->`
**Rule**: Left 65% main figure, right 35% two thumbnails stacked.

---

### Layout 10 — 2×2 grid (4 figures)
**Tag**: `<!-- layout: grid-2x2 -->`
**Rule**: Pandoc 2-column, 2 figures per column. Each figure at `{width="100%"}`.

---

### Layout 11 — 2×3 grid (6 figures)
**Tag**: `<!-- layout: grid-2x3 -->`
**Rule**: Generate `build_6grid_slide.py` (python-pptx) and notify user.

**Geometry — maximum slide width:**
- Use **minimal horizontal margins** (≤ 0.08") so the grid spans the **full slide width**.
- Inter-column gap ≤ 0.08"; inter-row gap ≤ 0.12".
- Cell width = `(slide_w - 2*margin_x - 2*gap_x) / 3`, taken as wide as the slide allows.
- Cell height computed from remaining vertical space after the section tag band (~0.50" top reserve) and a small bottom margin (≤ 0.12").
- **Uniform panel size:** all six tiles rendered at identical W×H. Compute image dimensions from a single target aspect (use the minimum aspect among the six figures so the most square one still fits the cell). Width-constrained: `img_w = cell_w_inner`, `img_h = img_w / aspect_target`; clamp to cell height if needed.
- If a panel is missing (e.g. only 5 figures supplied + a placeholder name like `oras`), draw a light-grey rectangle of the same W×H labelled with the placeholder name in 18 pt dark-grey italic.
- Optional per-panel label (model name etc.) goes above the image in a 0.28" band, 20 pt bold, centred.

---

### Layout 12 — Table slide
**Tag**: `<!-- layout: table -->` (or any slide containing a Markdown `| col |` table)
**Rule**: Treat the table as the slide's "figure" and apply the same positioning logic as Layout 2 (`single`) when no bullets are present, or Layout 3 (`figure-dominant`) when bullets are present.

**Geometry — same as figure / figure-dominant:**
- **Width**: expand the table to fill the slide width — cap at `100 × slide_w` (not 0.75). Column widths scaled proportionally from content; minimum column width preserved.
- **Position with bullets** (figure-dominant analogue): text band at top (~1.6" tall for 1-3 bullets at 20 pt); table centred horizontally **below** the text band; vertically centred in the remaining slide height.
- **Position without bullets** (single analogue): table centred horizontally; top edge just below the section tag band (~0.55" from slide top); vertically centred in remaining slide height.
- All cell text 16 pt; header row bold with light-grey fill (`RGB(220,220,220)`); existing solid/gradient fills cleared before re-applying header colour.
- See `style_table()` in the template — it now computes both width and position.

---

## Speaker Notes

In Pandoc PPTX output, speaker notes use `::: notes` fenced div syntax — **not** the bare `Note:` label.
**Phase 2 MUST convert all `Note:` blocks to `::: notes` syntax before running pandoc.**

---

## Execution Workflow

### PHASE 1 — Validate (read-only)

1. Read the storyboard file. Collect all figure paths, `<!-- section-tag: ... -->`, `<!-- layout: ... -->`, and `<!-- figures: ... -->` annotations.
2. Run batched aspect detection script (see Aspect Ratio Detection section). Detection auto-proceeds — both W and H are scaled proportionally in the template.
3. Parse all slides. For each slide, check:
   - **Title presence** — every slide must have a `## Heading` (required for Pandoc).
   - **Title length** ≤ 65 chars. Collect overlong titles.
   - **Figure paths** — verify each `![]()` path exists relative to storyboard directory. If not, ask user to fix or confirm ignoring.
   - **Layout tags** — verify tag is one of the known layouts; warn on unknown.
     Normalize the deprecated `<!-- layout: annotated -->` to `<!-- layout: figure-dominant -->` (they post-process identically). Phase 2 rewrites the tag in-place.
   - **vstack-3/hstack-3 aspect mismatch** — for each vstack-3 slide, check all figure aspects. If any aspect < 2.3, warn: "vstack-3 on slide N has figures with aspect {A:.2f} < 2.3 — hstack-3 gives {18.75/A:.0f} sq-in vs {3.61*A:.0f} sq-in image area. Consider switching to hstack-3." Do the same check in reverse for hstack-3 with aspect ≥ 2.3.
   - **Pandoc column syntax** — if the storyboard contains `:::: {.columns}`, `{width="…"}` on images, or `::: {.column`, warn: "Pandoc formatting found in storyboard (violates /5-ppt-design rule). Phase 2 will overwrite these."
   - **section-tag comments** — collect `<!-- section-tag: "X" color="Y" -->` per slide for Phase 4.
    - **figure-height override comments** — collect `<!-- figure-height: A/B -->` (or decimal) per slide and populate `FIGURE_HEIGHT_OVERRIDE`.
   - **Note: blocks** — flag any `Note:` blocks (convert to `::: notes` in Phase 2).
4. Report validation summary. If any titles exceed the limit, show a list with shortened suggestions and ask: "Approve shortened titles, or proceed with originals? (approve / keep originals)"
5. Proceed to Phase 2 unless blocking issues exist (missing figure paths, missing headings).

### PHASE 2 — Format (in-place edits to storyboard file)

**Backup first**: `cp <STORYBOARD> <STORYBOARD>.bak`

**Step A** — Convert `Note:` blocks to `::: notes` syntax.

**Step B** — Add `{width="X%"}` to all image links per the width assignment table above.

**Step C** — Apply column syntax for multi-column layouts **only if not already present**.
Before adding column syntax to a slide, check whether that slide's block already contains `:::: {.columns}`. If yes, skip Step C for that slide — the storyboard was written in preview-friendly format (by /5-ppt-design) and already contains the correct column structure. Only apply Step C to slides using the legacy flat format (layout tag + flat image list, no `:::: {.columns}`).

**Step D** — Structural fixes:
- Ensure `---` separators between every slide block.
- Ensure `<!-- Slide N -->` comment above each slide.
- Remove processed `<!-- layout: X -->` tags (keep `<!-- section-tag: ... -->` — needed for Phase 4).

### PHASE 3 — Export

1. Locate pandoc — prefer a conda environment if you keep one for this:
   ```bash
   PANDOC=$(command -v pandoc)
   $PANDOC --version 2>/dev/null | head -1 || { echo "pandoc not found on PATH"; exit 1; }
   echo "Using pandoc: $PANDOC"
   ```
2. If no `reference.pptx` is present in the storyboard directory, use the Pandoc default template (omit `--reference-doc`).
3. Run pandoc:
   ```bash
   $PANDOC <STORYBOARD> \
     --resource-path=<storyboard_dir>/.. \
     --reference-doc=<REFERENCE_PPTX> \
     -o <OUTPUT>.pptx
   ```
4. Proceed to Phase 4 immediately.

### PHASE 4 — Post-process (python-pptx)

**Do NOT regenerate the full processing script.** The static template lives at:
`~/.claude/skills/6-ppt-create/postprocess_template.py`

Read that file, fill in **only the DATA BLOCK** at the top (PPTX_PATH, SECTION_TAGS, LAYOUT_MAP, FIGURES) from the storyboard parse — roughly 15–20 lines. Write the filled script to `postprocess_slides.py` in the storyboard directory and run it.

#### DATA BLOCK reference

**`SECTION_TAGS`** — from `<!-- section-tag: "X" color="Y" -->` annotations:
- Key: slide index (0-based). Value: `("tag_text", "color_name")`.
- Cover slide (index 0) normally has no entry.

**`LAYOUT_MAP`** keys (hyphenated to match `<!-- layout: ... -->` tags from /5-ppt-design):
- `"vstack-3"`: slide indices tagged `vstack-3`
- `"figure-dominant"`: slide indices tagged `figure-dominant` (the deprecated `annotated` tag is normalized to this in Phase 1)
- `"hstack-3"`: slide indices tagged `hstack-3`
- `"table"`: slide indices containing a `| col |` table

**`FIGURES`** — from batched aspect detection (Phase 1):
- Key: slide index. Value: absolute path string (single figure) OR list of 3 paths (hstack-3 / vstack-3).

**`FIGURE_HEIGHT_OVERRIDE`** — optional per-slide override from storyboard explicit request:
- Key: slide index (0-based). Value: float in `(0, 1]` representing figure region fraction from bottom.
- If present for a slide, it overrides the default bullet-driven `9/14` to `11/14` rule.

#### Static template

The full template lives at:
`~/.claude/skills/6-ppt-create/postprocess_template.py`

**Phase 4 procedure:**
1. Read the template file.
2. Replace only the DATA BLOCK section (PPTX_PATH, SECTION_TAGS, LAYOUT_MAP, FIGURES, FIGURE_HEIGHT_OVERRIDE) with values parsed from the storyboard.
3. Write the result to `postprocess_slides.py` in the storyboard directory.
4. Run it.

Template execution order: **4D** (rebuild hstack-3 slides) → **4A** (add section tag chips) → **4T** (clear title text) → **4P** (remove empty placeholder shapes) → **4G** (enforce content placeholder geometry — 90% width, centred; text-only section slides also reposition to fill below chip) → **4B** (set body font 20 pt, skipping TEXT_BOX shapes so chip font is preserved) → **4C** (style + reposition tables — figure-dominant if bullets present, else single-figure positioning) → **4E** (reposition figures using bullet-driven 9/14 to 11/14 bottom-region rule unless overridden) → **4F** (if text band overlaps figures, shrink body text 20 -> 18 -> 16 pt) → **4N** (reformat notes: one sentence per line). See template functions for implementation.

## Font Size and Section Tag Rule

**Default font sizes across slides:**

| Element | Size |
|---|---|
| Section tag chip text | 24 pt bold white |
| Body text / bullets | 20 pt default |
| Overlap fallback (Phase 4F only) | 18 pt, then 16 pt |

Use 20 pt for non-title text by default. If text-band overlap with figures is detected, Phase 4 may reduce to 18 pt then 16 pt for that text band only.

**`set_body_font()` MUST skip `TEXT_BOX` shapes (shape_type == 17).** Section tag chips are TextBoxes created by `add_section_tag()` at 24 pt bold. If `set_body_font()` iterates them, it overwrites the chip font from 24 pt → 20 pt. Guard with `if shape.shape_type == 17: continue`.

## Content Placeholder Geometry Rule

**Step 4G** — call `enforce_content_placeholder_geometry()` after 4P (remove empty placeholders), before 4B (set body font). Rules:

- **Cover slide / any slide without a section tag**: skip entirely. Pandoc's layout-inherited geometry must not be touched — setting any python-pptx geometry attribute on a layout-inherited placeholder creates a fresh `<a:xfrm>` element that zeroes the fields not explicitly set (y=0, cy=0).
- **Section-tagged text-only slides** (Outline, Method, Summary — n_pics=0): set all four values:
  - `left = int(slide_w × 0.05)` — 5% left margin
  - `width = int(slide_w × 0.90)` — 90% of slide width, centred
  - `top = int(Inches(0.52))` — starts just below the chip (chip is ~0.05"–0.41")
  - `height = int(slide_h − Inches(0.60))` — fills to 0.10" from slide bottom
  - Without this, Pandoc leaves `top=1.31"` (space for the cleared title), wasting ~0.9" and shortening the usable text area.
- **Section-tagged picture slides** (n_pics ≥ 1): skip. `_compact_text_placeholder()` inside `fit_pictures_bottom()` sets all four values to the correct compact band.

Always set all four geometry attributes together when touching any of them. Setting only `left` or `width` on a shape without an explicit `<a:xfrm>` in the slide XML causes python-pptx to emit a new `<a:xfrm>` with `cx` set but `cy=0`, making the placeholder invisible.

**Section tag width:** Always 70% of slide width (`int(slide_w * 0.70)`). Never use a fixed inch value.

**Section tag text format:** Use a comprehensive hierarchical label: `"[Presentation] · [Section] · [Slide topic]"`. Examples: `"OSNAP · σ₀ space · time series"`, `"OSNAP · west · T-S & MOC vs MLD"`. Short sections may omit the third level: `"OSNAP · Outline"`. Tags must be specific enough that a reader knows exactly where in the presentation they are.

---

## Pandoc → PPTX Mapping Reference

| Markdown element | PowerPoint result |
|---|---|
| `## Title` (level-2 heading) | New slide with title (cleared in Phase 4T for section-tagged slides) |
| `---` alone (no heading) | New untitled slide — avoid; Pandoc overflows content to extra slides |
| Body text / bullets | Content placeholder |
| `![](fig.png){width="X%"}` | Picture embedded in content area |
| `:::: {.columns}` + two `:::` blocks | "Two Content" layout (left text + right picture) |
| `::: notes` … `:::` | Speaker notes pane |
| `<!-- section-tag: ... -->` | Parsed by Phase 4 only; ignored by Pandoc |

---

## Safety Constraints
- Phase 1 reads only — no files written (except cosmetic title fixes).
- Phase 2 edits the storyboard in-place for formatting only — never changes bullet content or figure selection.
- Phase 4 fills only the DATA BLOCK of the static template, writes `postprocess_slides.py` to disk, and runs it.
- Never modify or delete source notes files.
- Never fabricate statistics — `[TODO]` marks unknown values.
- Do not use paper-style section headings as slide titles.
