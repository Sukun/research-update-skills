# Plot Style Guide

Last updated: 2026-06-13  
Applies to: all projects under `/storage/research/nceo/sukun/`

---

## Quick reference

```python
import sys
sys.path.insert(0, '/storage/research/nceo/sukun')

from shared_plotting.plot_templates import (
    apply_style, make_figure, save_fig, pad_yaxis,
    line_plot, format_time_axis,
    plot_contourf,
    make_map_ax, plot_map_field,
    add_colorbar, add_shared_colorbar,
)

apply_style('ppt')   # or 'paper'
```

---

## File structure

```
shared_plotting/
├── __init__.py                  # package root + SHARED_ROOT constant
├── AGENTS.md                    # rules for automated coding agents
├── styles/
│   ├── ppt.mplstyle             # PPT-oriented rcParams (18/24/22pt fonts)
│   └── paper.mplstyle           # paper-oriented rcParams (14/16pt fonts)
├── plot_templates/
│   ├── __init__.py              # re-exports all public helpers
│   ├── layout.py                # apply_style, make_figure, save_fig, pad_yaxis
│   ├── line.py                  # line_plot, format_time_axis, add_hline, ...
│   ├── contourf.py              # plot_contourf, plot_pcolormesh
│   ├── global_map.py            # make_map_ax, plot_map_field, make_map_grid
│   └── colorbar.py              # add_colorbar, add_shared_colorbar, ...
└── docs/
    ├── plot_code_inventory.md   # all plotting files catalogued by project
    ├── plot_type_clustering.md  # 8 plot categories with frequency counts
    ├── historical_style_summary.md  # raw convention analysis
    ├── stylia_comparison.md     # where Stylia was and was not adopted
    ├── inferred_style_defaults.md   # canonical default values table
    └── plot_style_guide.md      # this file
```

---

## When to use ppt.mplstyle vs paper.mplstyle

| Use `ppt.mplstyle` when | Use `paper.mplstyle` when |
|------------------------|--------------------------|
| Generating diagnostic slides | Preparing manuscript figures |
| Standalone PNG for internal review | Journal submission (Nature, JGR, etc.) |
| Screen presentation | Printed report |
| Default for any new script | Explicitly requested by task description |

Font size summary:

| Element | PPT | Paper |
|---------|-----|-------|
| Body text | 18pt | 14pt |
| Axes title | 24pt | 16pt |
| Axes labels | 22pt | 16pt |
| Tick labels | 18pt | 14pt |
| Legend | 16pt | 14pt |
| Figure title | 20pt | 16pt |
| Line width | 2.0pt | 1.5pt |

---

## How to apply the shared style

Always call `apply_style()` before any plotting:

```python
from shared_plotting.plot_templates.layout import apply_style
apply_style('ppt')   # applies seaborn-v0_8-paper first, then overlays ppt.mplstyle
```

This replaces the inline `plt.style.use()` + `plt.rcParams.update()` blocks found in older project files. **Do not add inline fontsize overrides** to individual `ax.set_xlabel()`, `ax.set_title()`, etc. calls — let rcParams handle it.

---

## Per-plot-type defaults

### Single-panel line / timeseries

```python
from shared_plotting.plot_templates import apply_style, make_figure, save_fig, pad_yaxis
from shared_plotting.plot_templates import line_plot, format_time_axis

apply_style('ppt')
fig, ax = make_figure(preset='single')   # (14, 6)
line_plot(ax, time, [y1, y2], labels=['Model A', 'Model B'])
format_time_axis(ax, major_years=2)
pad_yaxis(ax)
save_fig(fig, 'output/timeseries.png')
```

- Default figsize: `(14, 6)` PPT / `(10, 5)` paper
- Color cycle: Wong 8-colour (set automatically via mplstyle)
- Legend: `loc='upper right'`, `framealpha=0.8`
- Y padding: use `pad_yaxis(ax)` — do not set `ax.set_ylim()` manually unless domain knowledge requires it

### Multi-line with reference lines

```python
line_plot(ax, time, [y1, y2, y3], labels=['A', 'B', 'C'])
add_hline(ax, 0)                             # zero reference
add_vline(ax, argo_start, label='Argo era')  # event marker
add_shading(ax, 1993, 2003, label='pre-Argo')
```

### Automatic annotation placement

Large-amplitude time series (e.g. seasonal/interannual OHC swings) don't have a single
corner that's reliably empty across every call site — hardcoding `ax.text(0.02, 0.98, ...)`
or a fixed `legend_kwargs={'loc': ...}` risks the annotation landing on top of a curve.
`place_text_auto()` picks whichever of the 4 conventional corners
(`'upper left'/'upper right'/'lower left'/'lower right'`, keys of `CORNER_ANCHORS`) has
the sparsest plotted data, and avoids the legend's own bounding box if one is passed in:

```python
lines = line_plot(ax, time, [y1, y2], labels=['Analysis', 'Smoothed'])
legend = ax.legend(loc='best')          # let matplotlib's own search place the legend
place_text_auto(ax, [(time, y1), (time, y2)],
                 'VarS/VarA=1.12, VN_S/VN_A=0.41',
                 legend=legend, fontsize=18)
```

- Do not hand-roll legend placement — `loc='best'` already solves that with a
  well-tested search; `place_text_auto()` only handles the free-floating text case
  matplotlib has no equivalent for.
- Pass `exclude={'upper left'}` (etc.) if another fixed-position artist (e.g. a panel
  label at the same corner) already occupies a corner.
- `xy_data` should be the already-plotted series (datetime-like x is handled internally
  via `matplotlib.dates.date2num`).
- For a manual override, skip `place_text_auto()` and look up `CORNER_ANCHORS[loc]`
  directly — this is the same table the automatic placement uses, so manual and
  automatic annotations stay visually consistent.

### Single-panel contourf

```python
from shared_plotting.plot_templates import plot_contourf, make_figure, save_fig

apply_style('ppt')
fig, ax = make_figure(preset='single')
im, cb = plot_contourf(ax, time, depth, sf, vmin=-10, vmax=25,
                        cb_label='Streamfunction (Sv)', invert_y=True)
ax.set_xlabel('Year'); ax.set_ylabel('Depth (m)')
save_fig(fig, 'output/hovmoller.png')
```

- Auto-selects `RdBu_r` + `TwoSlopeNorm` when vmin < 0 < vmax
- Auto-selects `viridis` + `Normalize` for all-positive data
- Default colorbar: `shrink=0.9`, `pad=0.02`, `extend='both'`

### Multi-panel contourf with shared colorbar

```python
from shared_plotting.plot_templates import make_figure, plot_contourf, add_shared_colorbar

apply_style('ppt')
fig, axes = make_figure(nrows=2, ncols=3, preset='2x3', hspace=0.2, wspace=0.1)
last_im = None
for ax, data in zip(axes.flat, data_list):
    im, _ = plot_contourf(ax, lon, lat, data, vmin=-1, vmax=1, add_cb=False)
    last_im = im
add_shared_colorbar(last_im, axes, label='Anomaly', shrink=0.6)
save_fig(fig, 'output/multi_panel.png')
```

### Global map (PlateCarree)

```python
from shared_plotting.plot_templates import make_map_ax, plot_map_field, save_fig
import matplotlib.pyplot as plt

apply_style('ppt')
fig = plt.figure(figsize=(14, 6))
ax = make_map_ax(fig, 111, projection='platecarree')
im, cb = plot_map_field(ax, lon, lat, data, vmin=-1, vmax=1, cb_label='TWS (cm)')
save_fig(fig, 'output/global_map.png')
```

> **Note:** Cartopy gridline labels ignore matplotlib rcParams — `make_map_ax()`
> sets `gl.xlabel_style` / `gl.ylabel_style` from `rcParams['xtick.labelsize']`
> automatically. If you build Cartopy axes manually (without `make_map_ax`), add:
> ```python
> label_size = plt.rcParams.get('xtick.labelsize', 14)
> gl.xlabel_style = {'size': label_size}
> gl.ylabel_style = {'size': label_size}
> ```
> This gives 18 pt under `ppt` style and 14 pt under `paper`.

### Regional map grid (Mercator)

```python
fig = plt.figure(figsize=(16, 6))
axes = make_map_grid(fig, 1, 2, projection='mercator',
                     extent=[-80, 20, 40, 75])
for ax, data in zip(axes, data_list):
    plot_map_field(ax, lon, lat, data, add_cb=False)
add_shared_colorbar(last_im, axes, label='...')
```

---

## Save figures

Always use `save_fig()` from `layout.py`:

```python
save_fig(fig, 'output/myplot.png')       # dpi=300 by default
save_fig(fig, 'output/myplot.png', dpi=150, close=False)  # keep figure open
```

This replaces the `plt.savefig(path, dpi=300, bbox_inches='tight'); plt.close(fig)` pattern in older scripts.

---

## What must not be changed casually

1. **Do not add inline `fontsize=` to `ax.set_xlabel()`, `ax.set_title()`, `ax.legend()`** — the mplstyle handles these. Inline overrides defeat the shared style system.

2. **Do not change the Wong color palette** in the mplstyle files without updating this guide and the `inferred_style_defaults.md`.

3. **Do not set `dpi` lower than 300** in any `save_fig()` call unless the file size is explicitly a requirement.

4. **Do not add cmocean as a required import** — it is not installed in all environments.

5. **Do not replace `apply_style()` with a manual `plt.rcParams.update()` block** in new scripts — updating the shared mplstyle files is the correct path.

6. **Do not introduce `constrained_layout=True`** by default — it conflicts with the historical `tight_layout()` pattern and creates inconsistencies.

---

## Adding a new plot type

1. Identify if the new type fits an existing category (see `plot_type_clustering.md`).
2. If truly new, add a helper function to an existing template module (or a new `plot_templates/scatter.py` etc.).
3. Update `plot_templates/__init__.py` to re-export the new function.
4. Document the new type in this guide.
5. Do not add it to a single project script — the shared layer is the right place.
