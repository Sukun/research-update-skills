# Stylia Comparison

Generated: 2026-06-13  
Stylia version: local install at `/storage/research/nceo/sukun/stylia/`

---

## Overview

Stylia is an Ersilia-branded figure styling package for publication-quality scientific plots. It provides two formats (`print`, `slide`) and two styles (`article`, `ersilia`). This document records where Stylia aligns with historical project conventions and where it conflicts.

**Bottom line:** Stylia is useful as a *structural reference* for file organisation and the print/slide mode concept. Its font sizes and line widths are far too small for this codebase and must not be adopted.

---

## Where Stylia aligns with historical conventions

| Feature | Stylia | Historical | Verdict |
|---------|--------|-----------|---------|
| Two output modes (print/slide) | `set_format('print'/'slide')` | PPT vs paper dialects in rcParams | Concept aligns; adopt the naming convention |
| `savefig.bbox = 'tight'` | Set internally | Universal in all files | Aligned |
| Legend framing | `frameon=True`, `framealpha=0.8`, `loc='upper right'` | Same in most scripts | Aligned |
| Separate colorbar helpers | Conceptually supports it | `plot_utils.py` has `determine_color_mapping()` | Aligned |
| Thin helper functions | Short, explicit functions | Historical preference confirmed | Aligned |
| `ColorPalette` class pattern | `get_named_colors_class()` | Both `plot_utils.py` files define a `ColorPalette` class | Aligned |

---

## Where Stylia conflicts with historical conventions

### Font sizes — major conflict

| Parameter | Stylia print | Stylia slide | Historical PPT | Historical paper |
|-----------|-------------|-------------|---------------|-----------------|
| `font.size` (body) | 5 | 8 | 18 | 14 |
| `axes.titlesize` | 6 | 10 | 24 | 16 |
| `axes.labelsize` | 6 | 10 | 22 | 16 |
| `xtick.labelsize` | 6 | 10 | 18 | 14 |
| `legend.fontsize` | 6 | 10 | 16 | 14 |

**Stylia fonts are 3–4× smaller than historical usage.** Stylia is optimised for Nature two-column print (7.09") at 300dpi where 6pt is readable at final size. The historical codebase targets 14"–16" landscape figures shown in slide presentations; 18pt body text is appropriate there.

**Decision: do not adopt Stylia font sizes. Use historical values.**

### Figure size basis — conflict

| Parameter | Stylia | Historical |
|-----------|--------|-----------|
| Default width basis | 7.09" (print) or 13" (slide) | (14, 6) fixed figsize for single-panel |
| Height determination | `SIZE × height_ratio` (0.5 or 0.3) | Explicit (width, height) tuples |

Stylia uses a proportional width-based system. Historical code uses explicit `(width, height)` tuples. The historical approach is more transparent; retain it.

### Color palettes — partial conflict

| Aspect | Stylia article | Stylia ersilia | Historical |
|--------|---------------|---------------|-----------|
| Primary palette | 10 vivid hues (`#E63946`, `#F4845F`, ...) | 8 Ersilia brand colours | Wong 8-colour palette |
| Foreground colour | Black | Plum `#50285A` | Black |

Stylia's article palette is publication-vivid but unfamiliar. Historical code explicitly encodes the Wong colorblind-safe palette in both major `plot_utils.py` files. **Use the Wong palette.**

### Line widths — conflict

| Parameter | Stylia print | Stylia slide | Historical |
|-----------|-------------|-------------|-----------|
| `lines.linewidth` | 0.5 | 0.75 | 2.0 (dominant) |

Stylia line widths are appropriate for Nature-width figures. At 14" with 18pt fonts, 2pt lines are proportionally correct. **Use historical lw=2.**

### Colormaps — not covered by Stylia

Stylia provides no ocean-science colormap guidance. Historical code has clear dominant choices (`RdBu_r`, `viridis`). No conflict — just a gap in Stylia's scope.

### Cartopy / geospatial — not covered by Stylia

Stylia has no map projection support. Historical code has strong, consistent cartopy conventions. No conflict.

---

## What to borrow from Stylia

1. **File and module structure:** `styles/`, `plot_templates/`, separate `colorbar.py`, `layout.py` — Stylia's modular layout is clean and maps well to this codebase's needs.
2. **The print/slide naming split:** Rename to `paper`/`ppt` to match historical language, but the two-mode concept is correct.
3. **`ColorPalette` class pattern:** Explicit named-color classes are readable and reusable.
4. **Short, explicit helper functions:** Stylia avoids deep inheritance hierarchies; historical code does the same.
5. **`legend.framealpha=0.8`, `legend.loc='upper right'`:** These rcParams align and can be shared.

---

## What NOT to borrow from Stylia

- Font sizes (5–10pt) — too small for PPT use
- Line widths (0.5–0.75pt) — too thin at historical figure sizes
- Figure width basis system — historical explicit (w, h) tuples are clearer
- Ersilia brand palette — not relevant to this scientific codebase
- Custom font files (Arial, Ersilia-Clear) — not needed
