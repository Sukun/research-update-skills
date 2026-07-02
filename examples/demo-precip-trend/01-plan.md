# docs/precip_trend_plan.md (output of 1-plan-task)

```
purpose:
  Determine whether station-observed monthly precipitation shows a statistically
  meaningful upward or downward trend over the last 20 years across the region covered
  by data/stations/, prompted by an informal observation that recent years "look wetter."

background:
  No prior formal trend analysis exists for this station network. The observation is
  anecdotal (from a colleague), so this is an exploratory first pass rather than a
  confirmatory study.

reference work:
  None found in this workspace. If a regional trend study exists elsewhere, link it here
  before starting Stage 3 (enrich).

research scope:
  - All ~40 stations in data/stations/, no sub-regional filtering initially.
  - Last 20 years of available record (trim shorter series; flag stations with >20%
    missing months rather than silently dropping them).

research questions:
  - Is there a significant linear trend in annual precipitation totals, region-wide?
  - Do individual stations disagree in trend direction, or is the signal spatially
    consistent?
  - Is the "wetter recently" impression driven by a genuine trend or by a few recent
    anomalous years?

hypotheses / expected outcomes:
  - Most likely outcome: weak or non-significant trend at the majority of stations,
    with a handful of individually significant stations — this is common for
    station-level precip trends over 20-year windows.
  - The anecdotal impression may be driven by 2-3 recent wet years rather than a trend.

methodology / approach:
  - Aggregate monthly totals to annual totals per station; handle gaps by requiring
    >=10 valid months/year, else mark that year missing.
  - Fit Sen's slope + Mann-Kendall trend test per station (robust to non-normality and
    missing years, standard choice for hydrological trend work).
  - Also compute the region-mean annual series and test that directly.
  - Map per-station trend direction/significance to check spatial consistency.

data sources:
  - data/stations/*.csv — monthly precipitation totals, one file per station.
  - Check header row for units (assume mm unless stated otherwise) and missing-value
    flag before aggregating.

work path:
  ./  (this working directory)

deliverables:
  - Trend map (per-station Sen's slope, significance marked).
  - Region-mean annual timeseries plot with trend line.
  - Short writeup answering the three research questions above.

success criteria:
  - Every station's trend result is reproducible from a single script.
  - The writeup explicitly separates "significant trend" from "recent anomalous years"
    so the Friday presentation doesn't overclaim.

risks / dependencies:
  - Station gap patterns are unknown until explored — may need to drop stations with
    too little coverage, changing the "40 stations" scope.
  - No pre-existing regional baseline to sanity-check results against.

notes:
  - Stage 2 (critical review): flagged that "trending up or down" is ambiguous between
    total precipitation and precipitation intensity/frequency — scope is fixed to
    totals only, extreme-event framing is explicitly out of scope for this pass.
```
