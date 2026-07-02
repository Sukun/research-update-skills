# Historical Style Summary

Generated: 2026-06-13  
Source: statistical analysis of ~189 Python plotting files across project-ocean, project-carbon, project-ml

---

## Method

Each major plotting utility module was read and its rcParams, figsize, colormap, colorbar, and layout settings extracted. Where multiple files disagree, the dominant value (by file count) is reported. Conflicts are flagged explicitly.

---

## 1. Style base

**Dominant (universal):** `plt.style.use('seaborn-v0_8-paper')`

Every primary plotting utility module uses this exact style. No other base style is dominant. One outlier (`cgr-tws_monthly_analysis/functions_plot.py`) uses `'seaborn-v0_8-talk'` — treated as an anomaly.

The user's global `CLAUDE.md` also specifies `seaborn-v0_8-paper`, confirming this as the canonical choice.

---

## 2. Font sizes — the PPT vs paper split

Two distinct font-size dialects exist in the codebase.

### PPT dialect — large fonts
Used in: `project-ocean/tests/visualization_cdftools_straitflux/code/plotting.py`  
Also specified in the user's global `CLAUDE.md` as the preferred default.

```python
'font.size': 18,
'axes.titlesize': 24,
'axes.labelsize': 22,
'xtick.labelsize': 18,
'ytick.labelsize': 18,
'legend.fontsize': 16,
'figure.titlesize': 20,
```

### Paper dialect — smaller fonts
Used in: `project-carbon/plot_utils.py`, `project-ml/plot_utils.py`,
`project-ocean/tests/MOC_decomposition_METRIC/functions_plotting.py`,
`project-ocean/tests/section_analysis/functions_plotting.py`,
`project-carbon/CGR_inversion_202504/functions_plot.py`

```python
'font.size': 14,
'axes.titlesize': 14–16,
'axes.labelsize': 12–16,
'xtick.labelsize': 12–16,
'ytick.labelsize': 12–16,
'legend.fontsize': 12–18,
'figure.titlesize': 14–16,
```

**Verdict:** two legitimate use modes. PPT dialect → `ppt.mplstyle`. Paper dialect → `paper.mplstyle`.  
Paper dialect centred on 14pt body / 16pt titles / 16pt labels.

---

## 3. Save settings (universal)

| Parameter | Dominant value | Consistency |
|-----------|---------------|-------------|
| `savefig.bbox` | `'tight'` | Universal |
| `savefig.pad_inches` | `0.05` | Universal |
| `dpi` (in `savefig` call) | `300` | Universal |

Pattern: all utility modules define a `save_fig(fig, path)` function that calls `plt.savefig(path, dpi=300, bbox_inches='tight')` then `plt.close(fig)`.

---

## 4. Figure sizes

| Plot category | Dominant figsize | Notes |
|---------------|-----------------|-------|
| Single-panel landscape (line, contourf) | `(14, 6)` | Most common across all projects |
| Square map | `(7, 7)` | Regional Cartopy maps |
| Wide single-panel | `(16, 5)` or `(20, 5)` | Some AMOC timeseries |
| Multi-panel (2×1) | `(14, 6)` or `(14, 8)` | Two stacked panels |
| Multi-panel (1×2) | `(16, 6)` or `(18, 6)` | Side-by-side |
| Global map | `(14, 6)` or `(16, 7)` | PlateCarree maps |

**Uncertain:** 2×3 and 3×4 figsize varies too widely to standardise safely.

---

## 5. Line widths

| Context | Dominant lw | Notes |
|---------|------------|-------|
| Primary data lines | `2.0–2.5` | Most diagnostic scripts |
| Secondary / overlay lines | `1.0–1.5` | Reference lines, baselines |
| Contour overlay (black) | `0.1–0.5` | Thin black contour on filled contourf |
| Shading / fill_between alpha | `0.2–0.4` | Ensemble spread |

**Conflict:** line width is inconsistent across scripts. `lw=2` is the single most common value for primary lines; encode this as the default.

---

## 6. Color cycle

**Dominant (used in multiple internal plot_utils.py modules):**
```python
COLORS = [
    '#000000',  # black
    '#E69F00',  # orange
    '#009E73',  # bluish green
    '#D55E00',  # vermillion
    '#F0E442',  # yellow
    '#56B4E9',  # sky blue
    '#0072B2',  # dark blue
    '#CC79A7',  # reddish purple
]
```
This is the Wong (2011) colorblind-safe palette. It appears explicitly defined in two independent utility modules, confirming it as the standard.

---

## 7. Colormaps

| Usage | Dominant cmap | Frequency | Notes |
|-------|--------------|-----------|-------|
| Diverging (anomalies, streamfunction, velocity) | `RdBu_r` | ~70 occurrences | Clear dominant |
| Diverging alternative | `bwr` | ~34 | Secondary |
| Diverging (T anomaly, multivar) | `RdYlBu` | ~23 | Occasional |
| Sequential (general) | `viridis` | ~66 | Default sequential |
| Sequential (positive) | `Reds` | ~19 | Density, magnitude |
| Sequential (cool) | `Blues` | ~8 | Salinity occasionally |

**No cmocean.** Some scripts import `cmcrameri.cm` (vik, roma, etc.) but this is project-specific and must not be a shared dependency.

---

## 8. Color normalisation

| Norm type | Usage | Notes |
|-----------|-------|-------|
| `TwoSlopeNorm(vmin, vcenter=0, vmax)` | Dominant for diverging | Standard for asymmetric ranges |
| `BoundaryNorm(levels, ncolors=256)` | Occasional | Discrete colorbars |
| `LogNorm` | Rare | Only in positive scalar fields |
| `SymLogNorm` | Very rare | Signed fields spanning orders of magnitude |
| `Normalize(vmin, vmax)` | Sequential | Standard linear for positive fields |

---

## 9. Colorbar

**Near-universal pattern:**
```python
plt.colorbar(im, shrink=0.9, label='...', pad=0.02)
```

| Parameter | Dominant value | Notes |
|-----------|---------------|-------|
| `shrink` | `0.9` | Slightly smaller than axes height |
| `pad` | `0.02` | Tight gap from axes edge |
| `orientation` | vertical (default) | Horizontal used occasionally for bottom colorbars |
| `extend` | `'both'` | Standard for contourf with explicit vmin/vmax |
| Font size for label | Not set explicitly — inherits rcParams | Consistent with global font settings |

**Shared colorbar for multi-panel:** `fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.6, pad=0.02)` — observed in multiple diagnostic scripts.

---

## 10. Cartopy map conventions

| Parameter | Dominant value |
|-----------|---------------|
| Global projection | `ccrs.PlateCarree()` |
| Regional projection | `ccrs.Mercator()` |
| Land feature | `cfeature.LAND` with `facecolor='lightgrey'`, `zorder=3` |
| Coastline | `cfeature.COASTLINE`, `zorder=4` |
| Gridlines | `draw_labels=True`, `top_labels=False`, `right_labels=False` |
| Transform for data | `transform=ccrs.PlateCarree()` |
| Gridline formatters | `LONGITUDE_FORMATTER`, `LATITUDE_FORMATTER` |

---

## 11. Layout spacing

| Method | Frequency | Notes |
|--------|-----------|-------|
| `fig.tight_layout()` | Very high (311) | Default choice |
| `gridspec` with manual `hspace`/`wspace` | High | Used when tight_layout doesn't give enough control |
| `constrained_layout` | Rare | Not dominant |

Typical `hspace`: 0.05 (tightly stacked panels) to 0.45 (panels with titles).  
Typical `wspace`: 0.1 (tightly packed) to 0.3 (with individual colorbars).

---

## 12. Axis limits and padding

- **Y-axis:** Explicit `ax.set_ylim()` is common in timeseries scripts. No consistent formula for automatic padding. Some scripts use `ax.margins(y=0.05)` to reduce whitespace.
- **X-axis:** Usually left at matplotlib default or set via `ax.set_xlim()` for section plots.
- **Depth/density panels:** `ax.invert_yaxis()` is standard.

**Uncertain:** y-axis padding rule is too inconsistent to standardise safely. Implement a light explicit helper rather than an automatic rule.

---

## 13. Legend

| Parameter | Dominant value |
|-----------|---------------|
| `loc` | `'upper right'` (most common) |
| `framealpha` | `0.8` |
| `fontsize` | Inherits `legend.fontsize` from rcParams |
| Frame | On (`frameon=True`) |

---

## 14. Confirmed inconsistencies (do not force uniformity)

| Parameter | Issue |
|-----------|-------|
| `axes.titlesize` in paper mode | Ranges 14–16 across files — encode 16 as a reasonable centre |
| `legend.fontsize` in paper mode | Ranges 12–18 — encode 14 as default |
| Multi-panel figsize | Too variable; do not encode a single default |
| `hspace` | Highly content-dependent; provide a common starting value, not a fixed rule |
| Some scripts use `axes.titleweight='bold'` | Not universal; do not make it a shared default |
