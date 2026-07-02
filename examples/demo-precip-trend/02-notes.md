# Notes accumulated while conducting the plan

Two layers, matching how `noteit` and `organize-notes` split the work: quick dated log
entries as you go, compiled into a per-topic note once the task settles.

## docs/precip_trend_notes.md (noteit — quick log, most recent first)

```
## [2026-06-28] [[precip_trend]] Region-mean trend is not significant (p=0.31, Mann-Kendall)
## [2026-06-27] [[precip_trend]] 6 of 40 stations individually significant, no spatial clustering
## [2026-06-26] [[precip_trend]] 2023-2024 are the two wettest years in the 20-year window
   at 28 of 40 stations — likely source of the "wetter recently" impression
## [2026-06-25] [[precip_trend]] Dropped 4 stations for >20% missing months (per plan
   success criteria); 36 stations carried forward
## [2026-06-24] [[precip_trend]] Sen's slope + Mann-Kendall implemented per station;
   region-mean series aggregated
```

## notes/precip_trend.md (organize-notes — compiled detail)

```markdown
# Precipitation Trend — Regional Station Network

**Status:** analysis complete, writeup pending
**Plan:** docs/precip_trend_plan.md

## Summary

No significant region-wide trend in annual precipitation totals over the last 20 years
(Mann-Kendall p=0.31 on the region-mean series). 6 of 36 usable stations show an
individually significant trend, but they don't cluster spatially — consistent with
noise rather than a regional signal.

The "wetter recently" impression traces to 2023–2024 being the two wettest years in the
window at the majority of stations (28/40), not a sustained trend.

## Method

- 40 candidate stations, 36 retained after dropping 4 for >20% missing months.
- Annual totals from monthly data, requiring ≥10 valid months/year.
- Sen's slope + Mann-Kendall per station; same test on the region-mean series.

## Key figures

- `fig_trend_map.png` — per-station Sen's slope, non-significant stations shown as
  hollow markers.
- `fig_regional_series.png` — region-mean annual series with 2023–2024 highlighted.

## Answers to the plan's research questions

1. **Significant trend?** No, region-wide.
2. **Spatially consistent?** No — the 6 significant stations are scattered, not clustered.
3. **Trend or recent anomaly?** Recent anomaly (2023–2024), not a trend.
```
