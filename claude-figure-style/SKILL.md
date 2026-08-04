---
name: figure-style
description: This skill should be used when the user is preparing a final scientific figure for a paper, thesis, poster, or report submission — polishing a plot to meet publication requirements, checking DPI/font/color-accessibility/label conventions, or reviewing a figure against journal figure guidelines. Use when the user says "polish this figure", "make this publication-ready", "check my figure for journal submission", "fix the fonts/DPI/colors on this plot", or asks for a pre-submission figure checklist. Not for exploratory/EDA plots — only for figures that will ship.
---

# Publication-Grade Figure Rules

A checklist for correct, legible, internally-consistent scientific figures,
plus matplotlib helper functions that implement the mechanical parts. This is
not a fixed visual house style — frame, font, and palette stay parameters;
what's fixed is correctness (data fidelity, label floor/ceiling, color-vision
safety, chart choice matched to data shape) and a render-then-verify QA pass.

**Scope**: use this for a **final-deliverable figure** — one going into a
paper, thesis chapter, poster, or kept export. For a quick look or an
in-progress analysis plot (EDA scatter, sanity-check histogram), skip this and
plot plainly — reach for this skill when you're about to ship the figure.

## Setup

The helpers are plain matplotlib/numpy/scipy — no special SDK. Load them once
per script/session:

```python
import sys
sys.path.insert(0, "<this-skill-dir>/scripts")   # replace with the skill's own path
from figure_style import (
    apply_figure_style, set_frame, panel_letter, focal_palette,
    bar_with_points, strip_with_median, goodness_arrow, end_of_line_labels,
    panel_crops,
)

apply_figure_style()   # call once, before any plotting — sets rcParams
```

`apply_figure_style()` sets a role-mapped font-size ladder (titles/axis labels
→ legend/annotation → tick labels, in that order), outward ticks, frameless
legends, 300-dpi save with Type-42 embedded fonts, and open (not boxed)
spines by default. All of these are parameters (`frame=`, `font=`, `sizes=`) —
override them, don't fight them.

## Workflow

1. **Before plotting**, read `reference/RULES.md` §1–§3 (data fidelity, label
   floor/ceiling, axes) and skim §4–§7 (color, typography, chart-family
   guidance, layout) for the chart type you're building.
2. Call `apply_figure_style()`, then build the figure using the helpers where
   they fit (`bar_with_points`, `strip_with_median`, `focal_palette` for a
   dominant/comparator color scheme, `end_of_line_labels` instead of a legend
   box, `panel_letter` for multi-panel figures).
3. **After `fig.savefig(...)`, before calling the figure done**, run the two
   checks in `reference/RULES.md` §9:
   - a geometric bbox-collision check over all text/spine objects in the
     figure (catches overlapping labels, text overrunning the canvas);
   - a perceptual check — crop the saved PNG to each panel via
     `panel_crops(fig)` and actually look at each crop (legibility, leader
     lines, color confusability, contrast). This step catches defects the
     bbox check cannot.
4. Walk `reference/RULES.md` §8 (anti-patterns) as a final pre-submission
   scan — these are correctness failures a reviewer will flag, not style
   nitpicks (red/green as opposing categories, filled bars on log axes,
   diverging colormaps not centered at the semantic zero, excluded data
   entering a plotted summary, etc.).

## Reference

- `reference/RULES.md` — the full §0–§9 checklist (data fidelity, label
  economy, axes/scales, color, typography, chart-family guidance by data
  shape, layout/narrative, anti-patterns, render-then-verify).
- `scripts/figure_style.py` — the helper functions themselves, each
  docstring-tagged with the rule section it implements.
