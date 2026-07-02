# Inferred Style Defaults

Generated: 2026-06-13  
Derived from: historical style analysis across matplotlib scripts

This document is the canonical reference for the two shared style modes and all per-category plotting defaults. When the shared templates are updated, update this document to match.

---

## Two style modes

| Mode | File | When to use |
|------|------|-------------|
| `ppt` | `styles/ppt.mplstyle` | Presentation slides, standalone diagnostic figures, screen viewing |
| `paper` | `styles/paper.mplstyle` | Manuscript figures, journal submission, printed reports |

---

## rcParams defaults

| Parameter | PPT mode | Paper mode | Source |
|-----------|----------|------------|--------|
| Base style | `seaborn-v0_8-paper` | `seaborn-v0_8-paper` | Universal in codebase |
| `font.size` | 18 | 14 | PPT: global CLAUDE.md; Paper: majority of utility modules |
| `axes.titlesize` | 24 | 16 | As above |
| `axes.labelsize` | 22 | 16 | As above |
| `xtick.labelsize` | 18 | 14 | As above |
| `ytick.labelsize` | 18 | 14 | As above |
| `legend.fontsize` | 16 | 14 | As above |
| `figure.titlesize` | 20 | 16 | As above |
| `savefig.bbox` | `tight` | `tight` | Universal |
| `savefig.pad_inches` | 0.05 | 0.05 | Universal |
| `lines.linewidth` | 2.0 | 1.5 | Historical dominant |
| `legend.frameon` | True | True | Universal |
| `legend.framealpha` | 0.8 | 0.8 | Consistent across files |
| `legend.loc` | `upper right` | `upper right` | Consistent |

---

## Default figure sizes

| Plot type | PPT figsize | Paper figsize | Notes |
|-----------|-------------|---------------|-------|
| Single-panel landscape | `(14, 6)` | `(10, 5)` | Most common shape in codebase |
| Square (regional map, T-S) | `(8, 8)` | `(6, 6)` | Square aspect |
| Global map | `(14, 6)` | `(10, 5)` | Same as single-panel |
| 1×2 side-by-side | `(16, 6)` | `(12, 5)` | Two panels |
| 2×1 stacked | `(14, 8)` | `(10, 7)` | Two stacked |
| 2×3 grid | Use gridspec, no fixed default | As PPT | Too variable |
| 3×4 grid | Use gridspec, no fixed default | As PPT | Too variable |

---

## Default DPI

Always save at `dpi=300`. Never use a lower value for output files.

---

## Color palette

Wong (2011) colorblind-safe 8-colour palette — confirmed in multiple independent plot_utils.py modules:

```python
WONG_COLORS = [
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

Use as the default `axes.prop_cycle` in both style modes.

---

## Colormap defaults

| Data type | Default cmap | Norm | Notes |
|-----------|-------------|------|-------|
| Diverging (anomalies, streamfunction) | `RdBu_r` | `TwoSlopeNorm(vmin, vcenter=0, vmax)` | Dominant (70+ occurrences) |
| Sequential positive | `viridis` | `Normalize(vmin, vmax)` | Default for non-diverging |
| Sequential warm | `Reds` | `Normalize` | For density, magnitude |
| Sequential cool | `Blues` | `Normalize` | Occasionally salinity |

**Diverging default rule:** if vmin < 0 < vmax, use `RdBu_r` with `TwoSlopeNorm`. If vmin and vmax are both positive or both negative, use `viridis`.

---

## Colorbar defaults

```python
# Standard single-panel colorbar
fig.colorbar(im, ax=ax, shrink=0.9, pad=0.02, extend='both')

# Shared colorbar for multi-panel (all axes)
fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.6, pad=0.02, extend='both')
```

| Parameter | Default | Notes |
|-----------|---------|-------|
| `shrink` | 0.9 (single) / 0.6 (shared) | Near-universal |
| `pad` | 0.02 | Tight gap |
| `extend` | `'both'` | Standard when explicit vmin/vmax used |
| `orientation` | vertical | Horizontal only when placed below |
| Label font | Inherits `axes.labelsize` rcParam | Do not override inline |

---

## Cartopy map defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| Global projection | `ccrs.PlateCarree()` | Standard for global fields |
| Regional projection | `ccrs.Mercator()` | Atlantic, North Atlantic |
| Land | `cfeature.LAND`, `facecolor='lightgrey'`, `zorder=3` | Universal |
| Coastline | `cfeature.COASTLINE`, `zorder=4` | Universal |
| Gridlines | `draw_labels=True`, `top_labels=False`, `right_labels=False` | Standard |
| Gridline label size | `gl.xlabel_style = {'size': rcParams['xtick.labelsize']}` | Cartopy ignores rcParams; must be set explicitly (18pt PPT / 14pt paper) |
| Data transform | `transform=ccrs.PlateCarree()` | Always needed for plotted data |

---

## Layout defaults

| Method | Default | When |
|--------|---------|------|
| `fig.tight_layout()` | Default | Single-panel and simple multi-panel |
| `GridSpec(hspace=0.1, wspace=0.1)` | Recommended starting point | Complex multi-panel |
| `constrained_layout` | Not recommended | Inconsistent with tight_layout in historical code |
| `ax.invert_yaxis()` | Required | Depth and density panels |

---

## Line plot defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| `linewidth` | 2.0 (PPT) / 1.5 (paper) | From rcParams |
| Color cycle | Wong palette | See above |
| Legend | `loc='upper right'`, `framealpha=0.8` | From rcParams |
| Y padding | `ax.margins(y=0.05)` | Light explicit helper, not automatic |
| X formatter (time) | `mdates.YearLocator(2)`, `mdates.DateFormatter('%Y')` | For multi-year timeseries |

---

## Uncertain / do-not-standardise parameters

| Parameter | Reason |
|-----------|--------|
| Multi-panel figsize | Too variable across use cases |
| `hspace` exact value | Content-dependent (0.05–0.45 range) |
| `axes.titleweight` | Only one file sets `'bold'`; not universal |
| `legend.fontsize` in paper mode | Ranges 12–18; use 14 as a reasonable default |
| T-S diagram conventions | Too few examples to standardise safely |
