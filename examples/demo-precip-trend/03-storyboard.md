# precip_trend_02-07-2026.md (output of 5-ppt-design, ready for 6-ppt-create)

Storyboard built from `notes/precip_trend.md`. Layout tags and figure widths follow
`5-ppt-design`'s rules; `6-ppt-create` would resolve these into a `.pptx`.

```markdown
<!-- Slide 1 -->
## Is regional precipitation trending wetter?

<!-- layout: text-only -->
- 40-station monthly network, 20-year record, checked against an informal "wetter
  recently" observation from the group.

---

<!-- Slide 2 -->
<!-- layout: figure-dominant -->
### Region Trend | Sen's Slope by Station

- No significant region-wide trend (Mann-Kendall p=0.31 on the region-mean series).
- 6 of 36 usable stations individually significant — scattered, not clustered.

![](/path/to/project/fig_trend_map.png){width="100%"}

::: notes
36 of 40 stations retained after dropping 4 for >20% missing months.
Significant stations show no spatial pattern consistent with a shared driver.
:::

---

<!-- Slide 3 -->
<!-- layout: single -->
### Regional Series | Annual Totals, 2006–2026

![](/path/to/project/fig_regional_series.png){width="80%"}

::: notes
2023 and 2024 are the two wettest years in the 20-year window at 28 of 40 stations —
this is the likely source of the "wetter recently" impression, not a trend.
:::

---

<!-- Slide 4 -->
## Bottom line

<!-- layout: text-only -->
- **No sustained trend** — the recent wet years are an anomaly, not a signal.
- Worth re-checking in a few years once 2023–2024 are no longer the tail of the record.
```
