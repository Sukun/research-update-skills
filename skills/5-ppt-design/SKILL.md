---
name: 5-ppt-design
description: "Create a slide storyboard file (<topic>_<dd-mm-yyyy>.md) from a rough user draft or a research notes subset. This is the content-decision skill: what story to tell, what order, what figure goes on each slide, and what layout to use. Does NOT export PPTX — that is 6-ppt-create's job."
license: MIT
---
# ppt_design — Slide Storyboard Skill

## Purpose

Produce a slide-by-slide storyboard markdown file from either:

- **Mode A**: a rough user draft (free-form bullets, spoken description, or section titles)
- **Mode B**: a pointer to one or more research notes files (reads and proposes a storyboard)

Both modes accepted. The output is a human-readable `.md` storyboard with explicit layout annotations that `6-ppt-create` (skill 6) reads mechanically to produce the final PPTX.

This skill makes **content decisions**. It does NOT touch Pandoc or PPTX formatting — those belong to 6-ppt-create.

---

## How To Invoke

```
/5-ppt-design <path-to-notes-or-draft>
```

---

## Parameters

| # | Parameter      | Default                                                                        | Description                                                  |
| - | -------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------ |
| 1 | `SOURCE`     | User message or current directory, always use absolute paths for files/figures | Free-form draft text OR path to notes file(s)                |
| 2 | `TOPIC`      | Inferred from source                                                           | Short topic slug for output filename (e.g.`amoc_progress`) |
| 3 | `NOTES_DIR`  | Current working directory                                                      | Directory to scan for figure files                           |
| 4 | `MAX_SLIDES` | 25                                                                             | Soft cap on content slides (excluding title + appendix)      |

If parameters are omitted, infer from context. Do not ask — proceed to Phase 1.

---

## Output File

Filename: `<topic>_<dd-mm-yyyy>.md` (e.g. `amoc_progress_22-05-2026.md`)

Written to the user's current working directory (or `NOTES_DIR` if set).

---

## Storyboard Format

The storyboard is near-Pandoc slide format. `6-ppt-create` converts layout annotations to final Pandoc syntax in-place.

### Frontmatter

Use bare double-dashes only — **no `title:` field** (a YAML `title:` creates a duplicate cover slide):

```yaml
---
---
```

### Cover slide (Slide 1)

The cover uses `## Heading` for the title. This heading is kept visible.

```markdown
---

<!-- Slide 1 -->
## Presentation Title

- Sub-bullet or one-sentence overview

::: notes
[Context for the presenter]
:::
```

### Outline / Roadmap slide (first content slide after cover)

The first content slide is always an **outline slide**, not a data-summary slide.
It gives the audience a roadmap of the talk using the section tag labels as bullet points.

```markdown
---

<!-- Slide 2 -->
<!-- section-tag: "Outline" color="steelblue" -->
## Outline

- **OSNAP (~60°N)** — multi-model overturning in the subpolar gyre
- **SAMBA (34.5°S)** — southern boundary transport and climatology
- **RAPID (26.5°N)** — 20-year record, components, and model skill
- **Summary** — cross-section comparison and key findings

::: notes
[Roadmap for the audience. The section tags on subsequent slides match these labels.]
:::
```

Rules for the outline slide:

- Use `<!-- layout: text-only -->` when no map figure is available.
- Use `<!-- layout: figure-dominant -->` when a study-area map exists — place the map as the figure.
- Bullet labels must **exactly match** the `<!-- section-tag: "..." -->` labels used on subsequent slides.
- Max 5 bullets (one per major section + any appendix note).
- Keep bullet text ≤ one line: **section name** (bold) + em-dash + one-phrase description.

### Content slides (Slides 2+)

**Every slide — including content slides — must have a `## Heading`** so Pandoc places all content
(bullets + images) on a single slide. The heading text is the same as the section tag label.
`6-ppt-create` Phase 4 clears the heading text from the title placeholder; the section tag chip at
top-left is the visible slide identifier.

```markdown
---

<!-- layout: figure-dominant -->
<!-- section-tag: "Section Name" color="colorname" -->
## Section Name

- **Key conclusion** — one line
- **Second conclusion** — one line

![](/absolute/path/to/fig.png)

::: notes
[Speaker notes — methodology, exact statistics, caveats. NOT shown on slide.]
:::
```

### Figure path rule

**Always use absolute paths** for all figure references — in `![]()`, in `<!-- figures: ... -->`, and in `<!-- TODO: ... -->` placeholders.

- ✓ `![](/path/to/project/tests/.../fig.png)`
- ❌ `![](../plots/rapid/straitflux/fig.png)`

Relative paths break when the storyboard is moved or when 6-ppt-create resolves figures from a different working directory. Absolute paths are unambiguous regardless of where the PPTX is generated.

### Section tag spec

- Format: `<!-- section-tag: "Label Text" color="colorname" -->`
- Placement: rendered by 6-ppt-create at top-left, **24 pt bold white** on coloured background
- Available colors: `steelblue`, `darkorange`, `teal`, `purple`, `crimson`
- Use the same section tag for consecutive slides in the same thematic group
- Keep in the `.md` file only; do NOT copy into `::: notes` blocks

### Layout tags (required — select based on figure count and aspect ratio; breakeven A = 2.3 for vstack vs hstack)

These tags are the same set recognised by `/6-ppt-create`. Skill 5 chooses the tag and writes column syntax (equal widths only); skill 6 detects pre-formatted storyboards and skips re-adding column syntax.

| Tag                                  | Meaning                                       | When to use                                                               |
| ------------------------------------ | --------------------------------------------- | ------------------------------------------------------------------------- |
| `<!-- layout: single -->`          | 1 figure, full slide                          | One result — no text bullets needed; use whole slide area                 |
| `<!-- layout: figure-dominant -->` | Bullets top + figure bottom                   | Standard single-figure slide (1–3 bullets)                                |
| `<!-- layout: vstack-2 -->`        | 2 wide figures stacked vertically             | 2 figures with aspect **≥ 2.3**                                          |
| `<!-- layout: vstack-3 -->`        | 3 wide figures stacked                        | 3 figures with aspect **≥ 2.3** only — see aspect threshold rule below   |
| `<!-- layout: hstack-2 -->`        | 2 portrait figures side-by-side               | 2 figures with aspect **< 2.3**                                          |
| `<!-- layout: hstack-3 -->`        | 3 portrait figures on ONE slide (python-pptx) | 3 figures with aspect **< 2.3** — MUST add `<!-- figures: ... -->` line  |
| `<!-- layout: grid-2x2 -->`        | 4 figures in 2×2 grid                        | Multi-model comparison panels                                             |
| `<!-- layout: grid-2x3 -->`        | 6 figures in 2×3 grid                        | 6-ppt-create generates a dedicated python-pptx script                     |
| `<!-- layout: focus-context -->`   | 1 main (65%) + 2 thumbnails (35%)             | Primary result + supporting panels                                        |
| `<!-- layout: text-only -->`       | No figures                                    | Title, summary, or transition slides                                      |

**When layout cannot be determined from the rules above** — if figure aspect ratio is unknown or a slide's content makes the best layout genuinely ambiguous — do not guess. Ask the user before writing Phase 2:
> "Slide N: figure at `[path]` — aspect ratio unknown or layout unclear. Please confirm: vstack-3 / hstack-3 / figure-dominant?"
Proceed to Phase 2 only after the user confirms.

### vstack vs hstack aspect threshold — CRITICAL RULE

**Always choose between vstack and hstack based on figure aspect ratio, not semantics.**

A 16:9 slide is ~13" wide × 7.5" tall (available figure area ≈ 13" × 5.7" after text band + margins). The image area produced by each layout for N=3 figures is:

| Layout | Image area (sq-in) |
|---|---|
| **hstack-3** | ≈ 18.75 / A |
| **vstack-3** | ≈ 3.61 × A |

Breakeven: **A ≈ 2.3**

- **A ≥ 2.3 → vstack-3**: wide landscape figures (timeseries, 12m-smoothed anomalies). Rows exploit the slide width.
- **A < 2.3 → hstack-3**: portrait, square, or mildly landscape figures (sections, Hovmöllers, profiles). Columns exploit the wider dimension. At A=1 (square), hstack-3 gives **5× more image area** than vstack-3.

Never choose vstack-3 because "stacking feels intuitive for Full/East/West comparison" — use the aspect ratio to decide.

The same threshold applies to 2-figure layouts: vstack-2 (A ≥ 2.3) vs hstack-2 (A < 2.3).

---

## Content Rules

### Slide titles

- **Cover slide only** shows its heading visibly. All other slides use `## Section Tag Text`
  (same text as the section tag label); 6-ppt-create clears it from the title placeholder.
- Keep cover title ≤ 65 characters.
- **No number prefixes.** Slide ordering is tracked via `<!-- Slide N -->` comments only.

### Bullet text — the "one line" rule

- **Target one line per bullet.** If a formula or very long technical term cannot fit one line, allow two — this is the only exception.
- Bullets state **what the audience must conclude**, not what is visually self-evident.
- **Good bullets point to the non-obvious insight:**
  - ✓ "**Geostrophic interior** drives >60% of interannual AMOC variance"
  - ✓ "**Post-Argo spread** halves → data assimilation constrains the interior"
- Max 3 bullet points on `figure-dominant`. Zero on `single`.
- For `vstack-2`: max 2 bullets below figures (space is limited).

### Bullet structure for figure slides (≤4 figures per slide)

**Guideline**: Use **1–3 bullets** before citing figures to frame the key message and highlight findings.

**Bullet 1–2: Frame & details** (concise; one line maximum unless exceeding line exceeds one line, then two lines allowed, if necessary, for formulas or technical terms, if too long, rephrase to be more concise)
- Further introduce **what the figure shows**: e.g. left panel shows *T & S*, right panel shows *velocity*
- Describe **methodology**: e.g. "variables computed by time-mean difference" or "streamfunction from cumulative integration"
- Highlight **content** of each panel or variable

**Bullet 3: Findings & phenomena** (optional; one line)
- Highlight **obvious phenomena or key findings** from the figures
- Use **NO numbers** — quantitative results go to `::: notes`
- Point to visual patterns: e.g. "weak interior stratification" or "maximum poleward in density coords"

**Section tag structure** (last level only):
- Last heading level (`###...`) must mark the **figure key variables/type concisely**, e.g.  
  `### big concept | T,S & Streamfunction | MOC in σ₀-space`  or  `### AMOC Timeseries | Model vs RAPID`
- **Strict rule**: total section-tag text must be **≤ 65 characters** (including brackets, colons, commas)
- from high-level to low-level: general to specific, e.g. `T & S` → `T & S Hovmöllers` → `T & S Hovmöllers | Full Section`


**Examples**:
```markdown
### T & Density | Full Section view

- **Left panel** shows temperature (K, color) and density (σ₀, black contours) across latitude.
- **Right panel** is streamfunction (m² s⁻¹) normalized per density class.

![](/path/to/section_hovmoller.png)

::: notes
Streamfunction computed via cumulative northward velocity integration in density bins.
Mean contour interval = 2 Sv per σ₀ 0.1 kg m⁻³ bin.
:::
```

```markdown
### AMOC | Multi-Model Timeseries

- Multi-model ensemble members in **blue**; ensemble mean in **red** (3-year smoothing).
- RAPID mooring timeseries overlaid in **black** for direct comparison.
- Large ensemble spread post-2008 reflects subpolar gyre variability.

![](/path/to/timeseries.png)

::: notes
Ensemble mean AMOC = 18.2 ± 4.1 Sv.
RAPID mean = 17.0 Sv over same period.
:::
```

### Companion figures — always share one slide

**Never split companion figures across multiple slides.** Companion figures are a set that share the same variable type, time period, or method across sub-regions (e.g. T, S, σ₀ Hovmöllers for the same section), or the same diagnostic across sub-arrays (Full, East, West).

- T + S + σ₀ Hovmöllers → one `hstack-3` slide, NOT separate `single` + `hstack-2`
- Full + East + West timeseries → one `vstack-3` or `hstack-3` slide (per aspect threshold)
- Two complementary diagnostics (e.g. MOC vs MLD) → one `hstack-2` slide

If the figure aspect makes a combined layout too cramped, prefer `hstack-3` (python-pptx rebuild handles sizing automatically) over splitting into separate slides. Splitting companion figures wastes slides and breaks visual comparison.

### Column syntax — preview-friendly format

Write storyboards **with Pandoc column syntax** so figures are visible as inline previews in VSCode Markdown Preview. Use **equal-width columns only** — never `{.column width="70%"}` or other asymmetric widths. Omit the width attribute entirely: Pandoc defaults to 50/50.

**`figure-dominant`** (bullets left, figure right):
```markdown
<!-- layout: figure-dominant -->
<!-- section-tag: "Section" color="steelblue" -->
## Section

:::: {.columns}
::: {.column}
- **Key finding 1**
- **Key finding 2**
:::
::: {.column}
![](/absolute/path/to/fig.png){width="100%"}
:::
::::

::: notes
[Speaker notes only]
:::
```

**`hstack-2`** (two figures side by side):
```markdown
<!-- layout: hstack-2 -->
<!-- section-tag: "Section" color="darkorange" -->
## Section

:::: {.columns}
::: {.column}
![](/absolute/path/to/fig_a.png){width="100%"}
:::
::: {.column}
![](/absolute/path/to/fig_b.png){width="100%"}
:::
::::

::: notes
[Speaker notes only]
:::
```

**Exception — `hstack-3`**: Pandoc cannot render 3-column natively. Write only the first figure as `![]()` and add a `<!-- figures: a, b, c -->` comment; 6-ppt-create's Phase 4D handles it via python-pptx. Do NOT write column syntax for hstack-3.

6-ppt-create Phase 2 detects pre-formatted storyboards (column syntax already present) and skips re-adding it.

### Note: blocks

- **Only write content explicitly stated in the source notes or documentation.** only write what you actually know from the source. Do not infer, embellish, or reconstruct from general domain knowledge.

- `::: notes` text goes to the **PowerPoint speaker Notes pane** — NOT shown on slide.
- Put here: exact numbers (r, RMSE, bias), methodology details, caveats, references.
- **Do NOT** include: section tag color/placement info, aspect ratios, pixel dimensions, or 6-ppt-create mechanism descriptions (e.g. ❌ "HSTACK-3 SLIDE — Phase 4D handles this").
- Do **not** repeat bullet content in `::: notes`.
- **Format**: one sentence per line. No run-on paragraphs.
  - ✓ `Multi-model mean AMOC = 18.2 Sv.`  `Spread = 4.1 Sv (1σ).`  `RAPID obs = 17.0 Sv.`
  - ❌ `The multi-model mean AMOC strength is 18.2 Sv with a spread of 4.1 Sv and the RAPID observation gives 17.0 Sv.`

- **Algorithm:** — For slides whose figure shows a derived quantity (transport, stream
  function, anomaly, METRIC component, skill score), add an **Algorithm:** subsection at
  the end of the `::: notes` block. 
  - If the algorithm is not documented, write: `**Algorithm:**`
  - **Never infer, reconstruct, or embellish** from general domain knowledge.
  - Example (only when the source states this): `**Algorithm:** MOC in σ₀-space: integrate northward velocity across section per density class; cumulative sum gives stream function; maximum = AMOC strength. StraitFlux: indices.py → moc_sigma0().`

  Omit the Algorithm section for slides that show only raw observational time series
  (no model computation involved), or for slides that show skill scores without documenting the underlying algorithm.

### Coordinate-space grouping rule *(domain rule — ocean/AMOC projects)*

- When results exist in both z-space and σ₀/density-space, **group them**: all z-space slides first,
  then all density-space slides.
- Never interleave z-space and density-space slides within the same section.

### General content filtering

- **KEEP on slides**: key findings, the single most important statistic per panel
- **MOVE TO notes**: exact numbers, caveats, method details, formulas, grid indices
- **OMIT entirely**: code names, script paths, variable names, internal file references

---

## Execution Workflow

### PHASE 1 — Explore & Outline (Plan Mode preferred, read-only)

**If Mode A (user draft provided):**

1. Parse the user's draft to extract intended slide order, section groupings, and figure references.
2. Scan `NOTES_DIR` for available figure files.
3. Identify gaps (figures mentioned but not found).

**If Mode B (notes file provided):**

1. Check line count: `wc -l <notes_file>`. If > 150 lines, ask the user: "Notes file is ~N lines — read in full to construct the storyboard? (yes / no — paste a summary instead)". Proceed only on yes.
2. Read the specified notes file(s).
3. Identify key findings, figure references, and thematic groupings.
4. Ask: "Full narrative arc + slide table (thorough) or slide-by-slide table only (fast)? (arc / table)" — construct accordingly.
5. Apply coordinate-space grouping.

**Present proposed outline:**

```
# STORYBOARD — Proposed Outline

## Narrative arc
[The story in plain language]

## Proposed slide sequence
| # | Section tag | Layout | Figures |
|---|-------------|--------|---------|
| 1 | (cover) | text-only | — |
| 2 | z-space | figure-dominant | timeseries.png |
...

## Figures found vs. missing
- ✓ fig1_amoc_total_timeseries.png
- ✗ rapid_overview_map.png — [TODO]
```

**Risk-awareness check (required before presenting outline):**
- For each figure path in the proposed outline, verify it exists: `ls <path>`. Mark missing paths `✗ [missing]` in the figures table.
- If ≥ 2 figures are missing, warn: "N figure paths could not be verified — storyboard will include `<!-- TODO: confirm path -->` placeholders. Proceed anyway?"
- If a figure exists but its aspect ratio cannot be determined (binary file unreadable), flag with `[aspect unknown]` and ask the user before choosing a layout.
- If `MAX_SLIDES` would be exceeded, warn and propose a merged or abbreviated deck.

**Proceed decision**: if the proposed deck is ≤ 3 slides, proceed to Phase 2 immediately. Otherwise present the outline and ask: "Proceed to write the storyboard? (yes / adjust)"

### PHASE 2 — Write Storyboard (only after approval)

1. Write `<topic>_<dd-mm-yyyy>.md` in `NOTES_DIR`.
2. Apply all format rules and layout tags above.
3. Cover slide: use `## Heading` (kept visible).
4. Slide 2 (first content slide after cover): generate the outline/roadmap slide — section tag labels
   as bullets, use `figure-dominant` when a study-area map is available, otherwise `text-only`.
5. All other slides: use `---` + `<!-- section-tag: ... -->` + `## Section Tag Text` (same text).
6. Mark uncertain figure paths: `![](PLACEHOLDER_figure_name.png)` with `<!-- TODO: confirm path -->`. This is the only permitted exception to the absolute path rule — the placeholder name makes the intent explicit.
7. Report the output file path and prompt: "Storyboard ready. To export to PPTX, run `/6-ppt-create <path>`."

### PHASE 3 — Iterate (on user request)

When the user edits the storyboard and asks for refinement of specific slides:

1. Read the current storyboard file.
2. Apply requested changes to the specified slides only.
3. Do not touch slides the user did not mention.
4. Report what changed.

---

## Safety Constraints

- Phase 1 is strictly read-only — no files written.
- Phase 2 activates only after explicit user approval.
- Never modify or delete source notes files.
- Never fabricate results or figures — mark unknowns with `[TODO]`.
- Never use paper-style section headings (Abstract, Introduction, etc.) as slide titles.
- 6-ppt-create handles all PPTX formatting — do not add Pandoc column syntax here.
