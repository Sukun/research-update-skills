"""
Line / time-series plot helpers.

Historical conventions encoded here:
  - figsize (14, 6) for single-panel timeseries
  - linewidth 2.0 (PPT) / 1.5 (paper) from rcParams — do not override inline
  - Wong colorblind-safe color cycle (set via mplstyle)
  - Legend upper-right, framealpha=0.8
  - Date formatting: YearLocator(2), DateFormatter('%Y') for multi-year x-axis
  - Y-axis padding: use pad_yaxis() from layout.py — no black-box heuristic
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def line_plot(ax, x, y_list, labels=None, colors=None,
              linewidths=None, linestyles=None, alphas=None,
              show_legend=True, legend_kw=None):
    """Plot one or more lines on ax using historical conventions.

    Parameters
    ----------
    ax : Axes
        Target axes.
    x : array-like
        Shared x-axis values (time, distance, etc.).
    y_list : list of array-like
        One entry per line. A single array is also accepted.
    labels : list of str, optional
        Legend labels. Must match len(y_list).
    colors : list of str, optional
        Line colors. Defaults to the axes color cycle.
    linewidths : list of float, optional
        Per-line widths. Defaults to rcParams['lines.linewidth'].
    linestyles : list of str, optional
        Per-line styles. Default '-'.
    alphas : list of float, optional
        Per-line alpha. Default 1.0.
    show_legend : bool
        Draw legend if labels are provided. Default True.
    legend_kw : dict, optional
        Extra kwargs passed to ax.legend().

    Returns
    -------
    list of Line2D
    """
    if not isinstance(y_list, (list, tuple)):
        y_list = [y_list]
    n = len(y_list)

    labels = labels or [None] * n
    colors = colors or [None] * n
    linewidths = linewidths or [None] * n
    linestyles = linestyles or ['-'] * n
    alphas = alphas or [1.0] * n

    lines = []
    for i, y in enumerate(y_list):
        kw = dict(linestyle=linestyles[i], alpha=alphas[i])
        if labels[i] is not None:
            kw['label'] = labels[i]
        if colors[i] is not None:
            kw['color'] = colors[i]
        if linewidths[i] is not None:
            kw['linewidth'] = linewidths[i]
        lines.append(ax.plot(x, y, **kw)[0])

    if show_legend and any(l is not None for l in labels):
        kw = {'loc': 'upper right', 'framealpha': 0.8}
        if legend_kw:
            kw.update(legend_kw)
        ax.legend(**kw)

    return lines


def format_time_axis(ax, major_years=2, fmt='%Y', minor_years=None):
    """Apply standard year-based x-axis formatting for timeseries plots.

    Parameters
    ----------
    ax : Axes
    major_years : int
        Tick every N years. Default 2.
    fmt : str
        Date format string. Default '%Y'.
    minor_years : int, optional
        Minor tick interval in years. None = no minor ticks.
    """
    ax.xaxis.set_major_locator(mdates.YearLocator(major_years))
    ax.xaxis.set_major_formatter(mdates.DateFormatter(fmt))
    if minor_years is not None:
        ax.xaxis.set_minor_locator(mdates.YearLocator(minor_years))


def add_hline(ax, y=0, color='k', lw=0.8, ls='--', alpha=0.6, **kwargs):
    """Add a horizontal reference line (e.g. zero line)."""
    ax.axhline(y, color=color, linewidth=lw, linestyle=ls, alpha=alpha, **kwargs)


def add_vline(ax, x, color='k', lw=0.8, ls='--', alpha=0.6, label=None, **kwargs):
    """Add a vertical reference line (e.g. Argo start, event marker)."""
    ax.axvline(x, color=color, linewidth=lw, linestyle=ls, alpha=alpha,
               label=label, **kwargs)


def add_shading(ax, x_start, x_end, color='grey', alpha=0.15, label=None, **kwargs):
    """Add a background shading band (e.g. pre-Argo era)."""
    ax.axvspan(x_start, x_end, color=color, alpha=alpha, label=label, **kwargs)
