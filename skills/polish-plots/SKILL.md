---
name: polish-plots
description: Apply the bundled matplotlib plotting helpers and style files to a Python plotting script. Use when asked to polish plots, apply the shared style, or replace raw rcParams/savefig/font-size code with the helpers bundled in this skill.
---

# Polish Matplotlib Plots

Use the helpers bundled in this skill. Follow the host's global response style and make only the requested plotting changes.

## Setup

Let `<plot-skill-root>` mean the installed `polish-plots` folder. Add it to the target script's import path only when the project has no package-based installation:

```python
import sys
sys.path.insert(0, "<plot-skill-root>")
from plot_templates import apply_style, make_figure, save_fig
```

The available helpers are in relative paths:

- `plot_templates/layout.py`: style, figure creation, saving, axis padding;
- `plot_templates/line.py`: line plots, time axes, reference lines, annotation placement;
- `plot_templates/contourf.py`: gridded fields;
- `plot_templates/global_map.py`: Cartopy maps;
- `plot_templates/colorbar.py`: single and shared colorbars;
- `styles/ppt.mplstyle` and `styles/paper.mplstyle`: slide and manuscript modes.

## Rules

1. Call `apply_style('ppt')` for presentation/diagnostic plots and `apply_style('paper')` only for manuscript output.
2. Replace raw `plt.rcParams.update(...)` blocks with the shared style; do not add inline title, label, or legend font sizes.
3. Use `save_fig(fig, path)` for normal exports (300 DPI and tight bounding box).
4. Use `RdBu_r` with a centered normalization for diverging data; use built-in sequential maps for one-sided data. Do not add a colormap dependency without approval.
5. Reuse `add_colorbar` or `add_shared_colorbar` when applicable.
6. On Cartopy axes, give plotted geographic data an explicit `ccrs.PlateCarree()` transform; use the bundled map helper where suitable.
7. Use `place_text_auto()` for free text annotations that could overlap data; let Matplotlib choose legend placement with `loc='best'` where appropriate.
8. Preserve non-plotting logic, numerical methods, inputs, outputs, and scientific claims.

Read [the plot style guide](./docs/plot_style_guide.md) for imports and common layouts. Read [the default values](./docs/inferred_style_defaults.md) only when exact values matter.

## Workflow

1. Inspect the requested script and identify only relevant style violations.
2. State the intended plotting-only edits and any limitation.
3. Apply targeted edits. Do not refactor unrelated code or run the script unless asked.
4. Report changed helpers, verification performed, and any remaining limitation.

Do not infer scientific meaning, create extra figures, or modify shared helpers unless the user explicitly requests that scope.
