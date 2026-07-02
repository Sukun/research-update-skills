---
name: polish-plots
description: "Apply the bundled shared-plotting style conventions to any Python matplotlib script. Replaces raw plt.rcParams blocks, plt.savefig(), and inline fontsize overrides with calls to the plot_templates helpers bundled in this skill. Invoke directly: /polish-plots <path-to-script>."
license: MIT
---

# Plot Polish Skill

## Purpose

Refactor any Python plotting script to use the shared plotting helpers bundled
with this skill (`~/.claude/skills/polish-plots/plot_templates/`, `styles/`,
`docs/`), enforcing consistent style across all projects.

This skill is **fully self-contained** — the helper code, mplstyle files, and
analysis docs all live directly inside this skill folder. Don't point new code
at an external shared-plotting package; the install root is
`~/.claude/skills/polish-plots` (or wherever you've installed this skill).

---

## How To Invoke

```
/polish-plots <path-to-script.py>
```

---

## The 12 Rules

### Rule 1 — Look for the bundled helpers first

Before writing any matplotlib code, check whether a helper already exists:

```
~/.claude/skills/polish-plots/plot_templates/
```

The following helpers are available:
- `layout.py` — `apply_style`, `make_figure`, `make_gridspec_figure`, `save_fig`, `pad_yaxis`
- `line.py` — `line_plot`, `format_time_axis`, `add_hline`, `add_vline`, `add_shading`
- `contourf.py` — `plot_contourf`, `plot_pcolormesh`
- `global_map.py` — `make_map_ax`, `plot_map_field`, `make_map_grid`
- `colorbar.py` — `add_colorbar`, `add_shared_colorbar`, `add_bottom_colorbar`

Import from the package root:
```python
import sys, os
sys.path.insert(0, os.path.expanduser('~/.claude/skills/polish-plots'))
from plot_templates import apply_style, make_figure, save_fig
```

### Rule 2 — Always call apply_style() before plotting

```python
from plot_templates.layout import apply_style
apply_style('ppt')    # for presentations and diagnostics (default)
apply_style('paper')  # for manuscript figures only
```

This applies `seaborn-v0_8-paper` as the base and overlays the correct font sizes. Never write a raw `plt.rcParams.update(...)` block in new scripts — update the shared mplstyle files instead.

### Rule 3 — Default to PPT style

Use `apply_style('ppt')` for all new plotting code unless the task description
explicitly requests paper or publication output. The ppt mode uses:
- 18pt body, 24pt titles, 22pt axis labels — readable on slides
- linewidth 2.0 — visible at presentation size

### Rule 4 — Do not add inline font size overrides

Never write:
```python
ax.set_xlabel('Time', fontsize=20)  # WRONG — defeats shared style
ax.set_title('My Plot', fontsize=18)  # WRONG
ax.legend(fontsize=14)  # WRONG
```

Write instead:
```python
ax.set_xlabel('Time')
ax.set_title('My Plot')
ax.legend()
```

Font sizes are governed by the mplstyle files. The only permitted `fontsize`
argument is in text annotations where layout requires it (`ax.text(..., fontsize=...)`).

### Rule 5 — Use the shared save_fig() function

```python
from plot_templates.layout import save_fig
save_fig(fig, 'output/myplot.png')   # always dpi=300, bbox_inches='tight'
```

Never call `plt.savefig()` directly in new scripts — it bypasses the shared DPI and tight-bbox settings.

### Rule 6 — Use historical colormaps

| Data type | Colormap | Norm |
|-----------|----------|------|
| Diverging (crosses zero) | `RdBu_r` | `TwoSlopeNorm(vmin, vcenter=0, vmax)` |
| Sequential positive | `viridis` | `Normalize(vmin, vmax)` |
| Sequential warm | `Reds` | `Normalize` |

The `plot_contourf()` and `plot_map_field()` helpers auto-select these. Do not
introduce cmocean, cmcrameri, or other colormap packages as required imports.

### Rule 7 — Use the Wong color palette for line plots

The shared mplstyle files set the `axes.prop_cycle` to the Wong (2011)
colorblind-safe palette. Do not override it with `plt.rcParams['axes.prop_cycle']`
in project scripts. The 8 colours in order are:
`black, orange, bluish-green, vermillion, yellow, sky-blue, dark-blue, reddish-purple`.

### Rule 8 — Use shared colorbar helpers

```python
from plot_templates.colorbar import add_colorbar, add_shared_colorbar

# Single panel
add_colorbar(im, ax, label='Streamfunction (Sv)')

# Multiple panels sharing one colorbar
add_shared_colorbar(im, axes, label='Anomaly (°C)', shrink=0.6)
```

Default: `shrink=0.9`, `pad=0.02`, `extend='both'`. Do not call
`plt.colorbar(im, ...)` with non-standard shrink/pad values in new scripts.

### Rule 9 — Do not invent new styles for a single project

If the existing mplstyle or template does not cover a need:
1. Check `docs/plot_style_guide.md` (in this skill folder) for the correct approach.
2. If genuinely missing, add a helper to the shared `plot_templates/` module.
3. Update `plot_templates/__init__.py` and `docs/plot_style_guide.md`.
4. Do not patch a single project script with a one-off style block.

### Rule 10 — Do not require cmocean

cmocean is not installed in all environments. Use matplotlib built-in colormaps
(`RdBu_r`, `viridis`, `Reds`, `Blues`) as defaults. If a project-specific script
already uses cmcrameri, that is acceptable for that script only — do not propagate
it to new shared code.

### Rule 11 — Cartopy maps: always set transform and gridline label sizes

Any `contourf`, `pcolormesh`, or `scatter` call on a Cartopy axes must include:
```python
transform=ccrs.PlateCarree()
```
Omitting this is a common bug that produces blank maps.

Cartopy gridline labels ignore matplotlib rcParams. When setting up gridlines,
always apply label sizes explicitly so they match the active style:
```python
gl = ax.gridlines(draw_labels=True, ...)
gl.top_labels = False
gl.right_labels = False
label_size = plt.rcParams.get('xtick.labelsize', 14)
gl.xlabel_style = {'size': label_size}
gl.ylabel_style = {'size': label_size}
```
`make_map_ax()` in `global_map.py` does this automatically. In scripts that
build Cartopy axes manually (e.g. `plot_multiple_maps` in `plot_utils.py`),
the same lines must be added after `ax.gridlines()`.

### Rule 12 — Save at dpi=300

All figures saved to disk must use `dpi=300`. Lower values are only acceptable
when explicitly requested (e.g. "save a small preview"). Use `save_fig()` to
enforce this automatically.

---

## Workflow

### Step 1 — Read the target script(s)

If the user specifies a file, read it. If not, read the file currently open in
the IDE or the most recently mentioned `.py` file.

### Step 2 — Audit the script against all 12 rules

Check each rule in order:

| # | Rule | What to fix |
|---|------|-------------|
| 1 | Use shared helpers | Replace hand-rolled plot code with helpers from `plot_templates/` where a matching helper exists |
| 2 | Call `apply_style()` | Remove any raw `plt.rcParams.update({...})` block; add `apply_style('ppt')` (or `'paper'` if explicitly requested) after imports |
| 3 | Default to PPT style | Use `'ppt'` unless the task description says "paper" or "publication" |
| 4 | No inline font sizes | Remove `fontsize=` kwargs from `set_xlabel`, `set_ylabel`, `set_title`, `legend()`, `suptitle()`. Font hierarchy: `figure.titlesize` (24pt, suptitle) > `axes.titlesize` (20pt, panel titles) — enforced by the mplstyle, never override inline |
| 5 | Use `save_fig()` | Replace `plt.savefig(...)` with `save_fig(fig, path)` |
| 6 | Standard colormaps | Use `RdBu_r` / `viridis` / `Reds`; no cmocean or cmcrameri in new shared code |
| 7 | Wong colour cycle | Remove any `axes.prop_cycle` override |
| 8 | Shared colorbar helpers | Replace `plt.colorbar(...)` with `add_colorbar(im, ax, label=...)` or `add_shared_colorbar(...)` |
| 9 | No one-off style blocks | If a style need is genuinely missing, add it to the shared module; do not patch the local script |
| 10 | No cmocean requirement | Do not add cmocean imports |
| 11 | Cartopy transform | Ensure every `contourf`/`pcolormesh`/`scatter` on a Cartopy axes includes `transform=ccrs.PlateCarree()` |
| 12 | Save at dpi=300 | Enforce via `save_fig()`, which sets dpi=300 automatically |

### Step 3 — Add the import block

Place this block immediately after the existing `import matplotlib` /
`import matplotlib.pyplot as plt` line (before any `plt.style.use` calls,
which `apply_style` replaces):

```python
import sys, os
sys.path.insert(0, os.path.expanduser('~/.claude/skills/polish-plots'))
from plot_templates.layout import apply_style, make_figure, save_fig
```

Import additional helpers only as needed:

```python
from plot_templates.line import line_plot, format_time_axis, add_hline
from plot_templates.contourf import plot_contourf, plot_pcolormesh
from plot_templates.global_map import make_map_ax, plot_map_field
from plot_templates.colorbar import add_colorbar, add_shared_colorbar
```

### Step 4 — Apply the style call

Add `apply_style('ppt')` as the first statement after the import block and
before any figure creation call. Remove the old `plt.style.use(...)` or
`plt.rcParams.update({...})` block entirely.

### Step 5 — Edit the file

Apply all changes identified in Step 2 using the Edit tool. Prefer targeted
edits over full rewrites. Do not alter any non-plotting logic.

### Step 6 — Report

After editing, summarise:
- Which rules required changes (list by number)
- Which rules were already compliant (one line)
- Whether any rules could not be applied (explain why)

Do not run the script unless the user asks.

---

## Reference: available helpers

Read `plot_templates/__init__.py` (in this skill folder) to see the current
export list. Key helpers at time of writing:

**layout.py**: `apply_style`, `make_figure`, `make_gridspec_figure`, `save_fig`, `pad_yaxis`

**line.py**: `line_plot`, `format_time_axis`, `add_hline`, `add_vline`, `add_shading`

**contourf.py**: `plot_contourf`, `plot_pcolormesh`

**global_map.py**: `make_map_ax`, `plot_map_field`, `make_map_grid`

**colorbar.py**: `add_colorbar`, `add_shared_colorbar`, `add_bottom_colorbar`

Style files: `styles/ppt.mplstyle`, `styles/paper.mplstyle` (in this skill folder)

## Where to find information

All paths below are relative to this skill folder (`~/.claude/skills/polish-plots/`):

| Question | Where to look |
|----------|--------------|
| What plot helpers exist? | `plot_templates/__init__.py` |
| What style values are used? | `docs/inferred_style_defaults.md` |
| When to use PPT vs paper? | `docs/plot_style_guide.md` |
| What plot types exist? | `docs/plot_type_clustering.md` |
| Historical code analysis | `docs/historical_style_summary.md` |
