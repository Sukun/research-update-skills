# Legacy layout rules

Note: these were written for the Pandoc writer. The default `pptx` engine (build_pptx.py) accepts text plus several figures on one slide for every layout; the `{width=...}` / columns syntax is accepted but ignored, and the Pandoc-specific notes below only matter with `--engine pandoc`.

These remain available for existing storyboards. The main skill lists the new opt-in layouts. Geometry-only previews are not office renders.

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

**Blank line before every closing `:::`/`::::` fence, when it follows a bullet list.** A bare `:::` immediately under a `- bullet` line reads as a list-continuation to markdown auto-formatters (VSCode's built-in formatter, prettier, format-on-save), which indent it — an indented fence closer is no longer at column 1, so Pandoc fails to close the div and silently drops the slide's content (symptom: a near-empty `.pptx`, far smaller than expected, with `[WARNING] Div ... unclosed` from Pandoc). Phase 2 Step D must enforce this when formatting/detecting column syntax.

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

**Three-figure processing**: Reads the three paths from `<!-- figures: ... -->`, replaces only pictures, preserves authored text and Notes, places figures equally spaced with proportional W+H sizing, adds section tag chip.

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
- **Width**: expand the table to fill the slide width — cap at `1.00 × slide_w`. Column widths scaled proportionally from content; minimum column width preserved.
- **Position with bullets** (figure-dominant analogue): text band at top (~1.6" tall for 1-3 bullets at 20 pt); table centred horizontally **below** the text band; vertically centred in the remaining slide height.
- **Position without bullets** (single analogue): table centred horizontally; top edge just below the section tag band (~0.55" from slide top); vertically centred in remaining slide height.
- All cell text 16 pt; header row bold with light-grey fill (`RGB(220,220,220)`); existing solid/gradient fills cleared before re-applying header colour.
- See `style_table()` in the template — it now computes both width and position.

---

## Speaker Notes

In Pandoc PPTX output, speaker notes use `::: notes` fenced div syntax — **not** the bare `Note:` label.
The render command converts legacy `Note:` blocks in its formatted copy before running Pandoc. Existing Notes XML is preserved by post-processing.

---

