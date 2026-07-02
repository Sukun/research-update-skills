"""
plot_templates — thin, explicit plotting helpers for all shared projects.

Public API
----------
Layout and style:
    apply_style(mode)           — apply 'ppt' or 'paper' rcParams
    make_figure(...)            — create figure + subplots with size presets
    make_gridspec_figure(...)   — figure + GridSpec for fine-grained control
    save_fig(fig, path)         — save at 300 DPI and close
    pad_yaxis(ax)               — trim excessive top/bottom whitespace

Line plots:
    line_plot(ax, x, y_list, ...)
    format_time_axis(ax, ...)
    add_hline(ax, y)
    add_vline(ax, x)
    add_shading(ax, x_start, x_end)

Filled contour / pcolormesh:
    plot_contourf(ax, x, y, z, ...)
    plot_pcolormesh(ax, x, y, z, ...)

Cartopy maps:
    make_map_ax(fig, ...)
    plot_map_field(ax, lon, lat, data, ...)
    make_map_grid(fig, nrows, ncols, ...)

Colorbars:
    add_colorbar(mappable, ax, ...)
    add_shared_colorbar(mappable, axes, ...)
    add_bottom_colorbar(mappable, ax, ...)
"""

from .layout import (
    apply_style,
    make_figure,
    make_gridspec_figure,
    save_fig,
    pad_yaxis,
)

from .line import (
    line_plot,
    format_time_axis,
    add_hline,
    add_vline,
    add_shading,
)

from .contourf import (
    plot_contourf,
    plot_pcolormesh,
)

from .global_map import (
    make_map_ax,
    plot_map_field,
    make_map_grid,
)

from .colorbar import (
    add_colorbar,
    add_shared_colorbar,
    add_bottom_colorbar,
)

__all__ = [
    'apply_style', 'make_figure', 'make_gridspec_figure', 'save_fig', 'pad_yaxis',
    'line_plot', 'format_time_axis', 'add_hline', 'add_vline', 'add_shading',
    'plot_contourf', 'plot_pcolormesh',
    'make_map_ax', 'plot_map_field', 'make_map_grid',
    'add_colorbar', 'add_shared_colorbar', 'add_bottom_colorbar',
]
