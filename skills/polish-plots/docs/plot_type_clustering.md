# Plot Type Clustering

Generated: 2026-06-13  
Method: frequency analysis of 189 Python plotting files across 3 projects

---

## Cluster taxonomy

Eight practical categories cover >95% of the codebase. Scripts are classified by their dominant figure-producing pattern; a single file may span multiple categories.

---

### Category 1 — Single-panel line / time-series
**Frequency: very high (~60+ scripts)**

Simple `ax.plot()` or `ax.fill_between()` on a shared axis. Usually time on x-axis (years or datetime), transport/flux/index on y.

Typical usage:
- AMOC transport timeseries (Sv vs year)
- AI smoother diagnostics (loss curves, metric traces)
- CGR inversion timeseries
- Spectral density plots

Representative files:
- `project-ocean/tests/visualization_cdftools_straitflux/code/4_timeseries_comparison.py`
- `project-ocean/tests/osnap_amoc_analysis/plot_transports.py`
- `project-carbon/CGR_inversion_202504/plot_timeseries.py`

Key parameters:
- `figsize = (14, 6)` — dominant
- `linewidth = 2–2.5`
- Wong color cycle
- `tight_layout()`
- Legend upper-right by default

---

### Category 2 — Multi-line plot (2–6 lines)
**Frequency: high (~40 scripts)**

Multiple `ax.plot()` calls on one panel, typically comparing models, ensemble members, or decomposition components. Distinguished from Cat 1 by the presence of a multi-entry legend.

Representative files:
- `project-ocean/tests/visualization_cdftools_straitflux/code/2d_compare_mooring_model.py`
- `project-ocean/tests/MOC_decomposition_METRIC/plot_fig1.py`
- `project-ml/ai_smoother/code/1_diagnostics_increment.py`

Key parameters:
- `figsize = (14, 6)` or `(16, 5)` for side-by-side
- legend with `framealpha=0.8`, `loc='upper right'`
- Shared x-axis with datetime formatter

---

### Category 3 — Single-panel contourf (Hovmöller / depth-time / density-lat)
**Frequency: high (~50 scripts)**

One `ax.contourf()` filling a 2D panel. Common forms: time × depth, latitude × density, time × latitude.

Representative files:
- `project-ocean/tests/visualization_cdftools_straitflux/code/plotting.py` → `plot_heatmap`
- `project-ocean/tests/visualization_cdftools_straitflux/code/plotting.py` → `plot_streamfunction_map`
- `project-ml/plot_utils.py` (multiple functions)

Key parameters:
- `figsize = (14, 6)` for landscape panels
- `cmap = 'RdBu_r'` for diverging, `viridis` for sequential
- `TwoSlopeNorm(vmin, vcenter=0, vmax)` for diverging
- `colorbar(shrink=0.9, pad=0.02)`
- `extend='both'`
- `invert_yaxis()` for depth/density panels

---

### Category 4 — Multi-panel contourf (2×1, 2×3, 3×4)
**Frequency: high (~40 scripts)**

Multiple `contourf` subplots in a grid, often with a shared colorbar for all panels or individual colorbars per panel.

Representative files:
- `project-ocean/tests/MOC_decomposition_METRIC/plot_fig2.py`
- `project-carbon/CGR_inversion_202504/plot_inversion_results.py`
- `project-ml/ai_smoother/code/diagnostic_D07_pulse_spatiotemporal.py`

Key parameters:
- `GridSpec` with `hspace=0.05–0.3`, `wspace=0.1–0.2`
- Shared colorbar placed below or to the right via `fig.colorbar(... ax=axes.ravel())`
- `sharex=True`, `sharey=True` common
- Individual colorbars when ranges differ between panels

---

### Category 5 — Global map (PlateCarree)
**Frequency: high (~45 scripts)**

Cartopy `PlateCarree` projection covering ±90°N/S and ±180°E/W. Filled contourf or pcolormesh of a gridded 2D field.

Representative files:
- `project-carbon/grace_TWS/grace_data_map_view.py`
- `project-carbon/LandSurfaceTemperature/ERA5_LST/main.py`
- `project-ml/cigar_/observations_statistics_gif/main1_obs_summary.py`

Key parameters:
- `projection = ccrs.PlateCarree()`
- `transform = ccrs.PlateCarree()` on all `contourf`/`pcolormesh`
- `cfeature.LAND` (lightgrey), `cfeature.COASTLINE`
- Gridlines with `draw_labels=True`, top/right labels off
- `figsize = (14, 6)` or `(16, 7)`

---

### Category 6 — Regional map (Mercator / limited extent)
**Frequency: moderate (~20 scripts)**

Cartopy with a non-global projection or explicit extent set via `ax.set_extent()`. Used for Atlantic sections, OSNAP, North Atlantic basin.

Representative files:
- `project-ocean/tests/section_analysis/functions_plotting.py` → `plot_section_map_cartopy`
- `project-ocean/tests/osnap_amoc_analysis/functions_plotting.py`
- `project-carbon/CGR_inversion_202504/plot_flux_maps.py`

Key parameters:
- `projection = ccrs.Mercator()` or `ccrs.NorthPolarStereo()`
- `ax.set_extent([lon_min, lon_max, lat_min, lat_max])`
- `figsize = (7, 7)` for square regional maps
- `cfeature.LAND`, `cfeature.COASTLINE`, `cfeature.RIVERS` (occasionally)

---

### Category 7 — T-S diagram / scatter
**Frequency: low–moderate (~10 scripts)**

Scatter or density plot in temperature × salinity space, often with seawater isopycnal overlays. Found in AMOC section analysis.

Representative files:
- `project-ocean/tests/visualization_cdftools_straitflux/code/plotting.py` (TS functions)
- `project-ocean/tests/osnap_amoc_analysis/functions_plotting.py`

Key parameters:
- `figsize = (8, 8)` near-square
- `seawater` or `gsw` for isopycnal contours
- Color-coded by depth or time

---

### Category 8 — Bar / histogram diagnostic and image composite
**Frequency: low (~8 scripts) — outlier category**

Includes bar charts in ML hyperparameter sweeps, histogram diagnostics, and the image-composite viewer (`python_tools/view_exps_2x2_panel.py`).

Representative files:
- `project-ml/ai_smoother/exps/D1/experiment_D1b_hyperp_diagnosis.py`
- `project-ml/cigar_/observations_statistics_gif/main1_obs_summary.py`
- `python_tools/view_exps_2x2_panel.py`

Notes:
- `view_exps_2x2_panel.py` assembles PNG files with `matplotlib.image.imread`; not a data plot.
- These scripts do not need standardised contourf/map helpers.

---

## Frequency summary

| Category | Approx. scripts | Priority for shared templates |
|----------|----------------|-------------------------------|
| 1. Single-panel line/timeseries | 60+ | High |
| 2. Multi-line | 40 | High |
| 3. Single-panel contourf | 50 | High |
| 4. Multi-panel contourf | 40 | High |
| 5. Global map (PlateCarree) | 45 | High |
| 6. Regional map (Mercator) | 20 | Medium |
| 7. T-S diagram / scatter | 10 | Low |
| 8. Bar / image composite | 8 | Low / outlier |

Categories 1–5 account for ~85% of all plotting code and drive the shared template priorities.
