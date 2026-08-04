# Plot Code Inventory

Generated: 2026-06-13  
Source scanned: `/storage/research/nceo/sukun/`  
Total Python files with plotting code: ~189 across 3 major projects

---

## AMOC_CALC

| File | Plot types | Notes |
|------|-----------|-------|
| `AMOC_CALC/tests/visualization_cdftools_straitflux/code/plotting.py` | contourf (Hovmöller), streamfunction map | Primary utility module; PPT-large fonts (18/24/22). Dense: 360 pattern matches. Uses `TwoSlopeNorm`, `RdBu_r`. |
| `AMOC_CALC/tests/visualization_cdftools_straitflux/code/2b_plot_maps_ecco.py` | global map | Imports `plot_streamfunction_map` from local module |
| `AMOC_CALC/tests/visualization_cdftools_straitflux/code/2c_plot_maps_ecco_all.py` | multi-panel global map | Multi-model comparison layout |
| `AMOC_CALC/tests/visualization_cdftools_straitflux/code/2d_compare_mooring_model.py` | multi-line time-series | Mooring vs model comparison |
| `AMOC_CALC/tests/visualization_cdftools_straitflux/code/2e_compare_sf_model.py` | multi-line, contourf | Streamfunction comparison |
| `AMOC_CALC/tests/visualization_cdftools_straitflux/code/3_analyse_transport.py` | line, bar | Transport analysis |
| `AMOC_CALC/tests/visualization_cdftools_straitflux/code/4_timeseries_comparison.py` | multi-line time-series | Multi-model AMOC timeseries |
| `AMOC_CALC/tests/visualization_cdftools_straitflux/code/5_spectral_analysis.py` | line (spectra) | Power spectral density |
| `AMOC_CALC/tests/MOC_decomposition_METRIC/functions_plotting.py` | multi-line time-series, contourf | Paper-small fonts (14/16/16). Complex GridSpec layouts. |
| `AMOC_CALC/tests/MOC_decomposition_METRIC/plot_fig1.py` | multi-line, multi-panel | Fig 1 for manuscript |
| `AMOC_CALC/tests/MOC_decomposition_METRIC/plot_fig2.py` | multi-panel contourf | Fig 2 for manuscript |
| `AMOC_CALC/tests/MOC_decomposition_METRIC/plot_fig3.py` | multi-panel line | Fig 3 for manuscript |
| `AMOC_CALC/tests/MOC_decomposition_METRIC/plot_fig4.py` | multi-panel contourf | Fig 4 |
| `AMOC_CALC/tests/osnap_amoc_analysis/functions_plotting.py` | regional map (Cartopy), contourf | Density-streamfunction; `ccrs.Mercator` |
| `AMOC_CALC/tests/osnap_amoc_analysis/plot_osnap_sections.py` | contourf, regional map | OSNAP section analysis |
| `AMOC_CALC/tests/osnap_amoc_analysis/plot_transports.py` | multi-line time-series | Transport time-series |
| `AMOC_CALC/tests/osnap_amoc_analysis/plot_density.py` | contourf (density) | Density-space Hovmöller |
| `AMOC_CALC/tests/native_grid_amoc_analysis/plot_native_grid.py` | global map, contourf | Native grid visualization |
| `AMOC_CALC/tests/section_analysis/functions_plotting.py` | regional map (Cartopy Mercator), contourf, scatter | Paper-small fonts (14/16/16). GridSpec. Velocity cross-sections. |
| `AMOC_CALC/tests/section_analysis/plot_velocity.py` | contourf | Velocity cross-section |
| `AMOC_CALC/tests/section_analysis/plot_section_map.py` | regional map | Section path on map |

---

## CPEO_data_analysis

| File | Plot types | Notes |
|------|-----------|-------|
| `CPEO_data_analysis/plot_utils.py` | multi-panel contourf, global map, line | Main utility; paper-small fonts (14/14/12). 246 pattern matches. Extensive norm helpers (`TwoSlopeNorm`, `LogNorm`, `SymLogNorm`). |
| `CPEO_data_analysis/CGR_inversion_202504/functions_plot.py` | line (GCV), global map, multi-panel contourf | Paper-small fonts (14/14/12). Uses `cmcrameri` (optional). |
| `CPEO_data_analysis/CGR_inversion_202504/plot_inversion_results.py` | multi-panel contourf, line | Inversion result maps |
| `CPEO_data_analysis/CGR_inversion_202504/plot_flux_maps.py` | global map, multi-panel | Flux maps |
| `CPEO_data_analysis/CGR_inversion_202504/plot_timeseries.py` | multi-line time-series | CGR timeseries |
| `CPEO_data_analysis/cgr-tws_monthly_analysis/functions_plot.py` | line, contourf, global map | Uses `seaborn-v0_8-talk` style (outlier) |
| `CPEO_data_analysis/cgr-tws_humphrey_fig1_072025/plot_fig1.py` | multi-panel global map | Humphrey comparison |
| `CPEO_data_analysis/grace_TWS/grace_data_map_view.py` | global map | GRACE TWS fields; `netCDF4` + Cartopy |
| `CPEO_data_analysis/LandSurfaceTemperature/ERA5_LST/main.py` | global map, line | ERA5 LST; uses xarray coarsen |
| `CPEO_data_analysis/OCS_CO2_study/3_ocs_analysis_preliminary_archieved/core/plotter.py` | multi-line, scatter, global map | Class-based `OCSVisualizer`; `seaborn`, `gridspec` |
| `CPEO_data_analysis/OCS_CO2_study/*/plot_*.py` (×10) | line, global map, scatter | OCS CO₂ analysis scripts |

---

## ORACS_data_analysis

| File | Plot types | Notes |
|------|-----------|-------|
| `ORACS_data_analysis/plot_utils.py` | multi-panel contourf, global map, Hovmöller, GIF frames | Primary utility; paper-small fonts (18/18/12). 324 pattern matches. |
| `ORACS_data_analysis/salinity_test_cigar/plot_utils.py` | contourf, Hovmöller, global map | Near-duplicate of main plot_utils; 280 matches |
| `ORACS_data_analysis/ai_smoother/code/diagnostic_D07_pulse_spatiotemporal.py` | global map, multi-panel contourf, Hovmöller | Cartopy + xarray; pulse detection plots |
| `ORACS_data_analysis/ai_smoother/code/1_diagnostics_increment.py` | multi-panel contourf, global map | Increment diagnostics |
| `ORACS_data_analysis/ai_smoother/code/diagnostic_*.py` (×10) | multi-panel contourf, line, global map | AI smoother diagnostics |
| `ORACS_data_analysis/ai_smoother/exps/D1/experiment_D1b_hyperp_diagnosis.py` | line, scatter | Hyperparameter sweep |
| `ORACS_data_analysis/cigar_/optimize_gamma/data_analyse.py` | multi-line, contourf | CIGAR gamma optimization; 139 matches |
| `ORACS_data_analysis/cigar_/observations_statistics_gif/main1_obs_summary.py` | scatter, global map, bar | Class-based `ObservationAnalyzer`; type-color-marker mappings |
| `ORACS_data_analysis/cigar_/regional_study/*.py` (×15) | contourf, global map, line | Regional CIGAR analysis |

---

## python_tools

| File | Plot types | Notes |
|------|-----------|-------|
| `python_tools/view_exps_2x2_panel.py` | composite image grid | Assembles 2×2 PNG panels; uses `matplotlib.image`. Outlier — no scientific data |

---

## Summary statistics

| Project | Python plotting files (approx) | Dominant plot types |
|---------|-------------------------------|---------------------|
| AMOC_CALC | ~32 | contourf, multi-line, regional map |
| CPEO_data_analysis | ~80 | global map, multi-panel contourf, line |
| ORACS_data_analysis | ~76 | contourf, global map, Hovmöller, multi-panel |
| python_tools | 1 | image composite (outlier) |
| **Total** | **~189** | |
