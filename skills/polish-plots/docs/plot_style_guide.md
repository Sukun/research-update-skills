# Plot Style Guide

Use this guide with the bundled `polish-plots` skill. It is portable: set
`<plot-skill-root>` to the installed skill directory rather than hardcoding a
machine-specific location.

## Quick start

```python
import sys
sys.path.insert(0, "<plot-skill-root>")

from plot_templates import (
    apply_style, make_figure, save_fig, pad_yaxis,
    line_plot, format_time_axis, place_text_auto,
    plot_contourf, plot_map_field, add_shared_colorbar,
)

apply_style("ppt")
fig, ax = make_figure()
# plot data
save_fig(fig, "output/figure.png")
```

## Style modes

- `ppt`: presentation and diagnostic figures; larger type and line widths.
- `paper`: manuscript and print figures; more compact type.

Choose the output context explicitly. Do not override font sizes inline unless an annotation needs a deliberate layout exception.

## Time series

```python
lines = line_plot(ax, time, [series_a, series_b], labels=["A", "B"])
ax.legend(loc="best")
format_time_axis(ax)
pad_yaxis(ax)
```

For free text annotations, let the helper select the sparsest conventional corner:

```python
place_text_auto(
    ax,
    [(time, series_a), (time, series_b)],
    "ratio = 1.12",
    legend=ax.get_legend(),
    fontsize=12,
)
```

Use `exclude={"upper left"}` when a panel label already occupies a corner. For a
manual placement, use `CORNER_ANCHORS[location]`.

## Gridded fields and maps

Use `plot_contourf` or `plot_map_field` where their defaults match the requested
plot. For geographic data plotted on Cartopy axes, always provide the source-coordinate
transform. Use a shared colorbar for comparable panels.

## Output

Use `save_fig(fig, path)` for normal exports. It sets `dpi=300` and a tight bounding
box. Confirm before overwriting an existing figure.
