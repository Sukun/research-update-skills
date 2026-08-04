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


# Single source of truth for the 4 conventional corner anchors, shared by both manual
# overrides (caller passes one of these keys directly) and place_text_auto() below.
CORNER_ANCHORS = {
    'upper left':  dict(x=0.02, y=0.98, ha='left',  va='top'),
    'upper right': dict(x=0.98, y=0.98, ha='right', va='top'),
    'lower left':  dict(x=0.02, y=0.02, ha='left',  va='bottom'),
    'lower right': dict(x=0.98, y=0.02, ha='right', va='bottom'),
}

# Deterministic tie-break order when several corners score equally (e.g. uniform-density
# data) — keeps output reproducible instead of dict/insertion-order dependent.
_CORNER_TIE_BREAK = ['upper right', 'lower right', 'lower left', 'upper left']


def _corner_box_axes_frac(corner, box_frac):
    """Axes-fraction (x0, y0, x1, y1) rectangle for a corner probe box."""
    wx, wy = box_frac
    if corner == 'upper left':
        return (0.0, 1.0 - wy, wx, 1.0)
    if corner == 'upper right':
        return (1.0 - wx, 1.0 - wy, 1.0, 1.0)
    if corner == 'lower left':
        return (0.0, 0.0, wx, wy)
    if corner == 'lower right':
        return (1.0 - wx, 0.0, 1.0, wy)
    raise ValueError(f"unknown corner {corner!r}")


def _rects_overlap(a, b):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1


def place_text_auto(ax, xy_data, text, candidates=None, exclude=None,
                     legend=None, box_frac=(0.35, 0.25), **text_kwargs):
    """Place `text` in whichever corner of `ax` has the sparsest plotted data.

    Scores the 4 conventional corners (`CORNER_ANCHORS` keys) by how many of the
    already-plotted (x, y) points fall inside a small probe box in that corner, and
    picks the sparsest one — so an annotation doesn't end up sitting on top of a curve.
    If `legend` (the Legend artist already drawn on `ax`) is given, corners whose probe
    box overlaps the legend's rendered bounding box are penalized so the annotation
    doesn't collide with the legend either.

    Does not attempt to place the legend itself — matplotlib's own `loc='best'` already
    solves that well; this only handles the free-floating text case matplotlib has no
    equivalent for.

    Parameters
    ----------
    ax : Axes
    xy_data : list of (x_array, y_array)
        The already-plotted series (e.g. collected during the plotting loop). x may be
        datetime-like (converted via matplotlib.dates.date2num) or plain numeric.
    text : str
        Annotation text. No-op (returns None) if falsy.
    candidates : list of str, optional
        Corner names to consider. Defaults to all of `CORNER_ANCHORS`.
    exclude : iterable of str, optional
        Corner names to remove from consideration (e.g. wherever a panel_label already
        sits).
    legend : Legend, optional
        Legend artist already drawn on `ax`, used for the overlap penalty.
    box_frac : (float, float)
        (width, height) of each corner's probe box, as a fraction of the current
        x/y data range. Default (0.35, 0.25).
    **text_kwargs
        Forwarded to ax.text() (e.g. fontsize=18). `ha`/`va`/`transform` are always set
        from the chosen corner and must not be passed here.

    Returns
    -------
    str or None
        The corner name used, or None if `text` is falsy or no candidates remain.
    """
    if not text:
        return None

    candidates = list(candidates) if candidates is not None else list(CORNER_ANCHORS)
    if exclude:
        exclude = set(exclude)
        candidates = [c for c in candidates if c not in exclude]
    if not candidates:
        return None

    # Concatenate all plotted points, converting datetime-like x to numeric (date
    # ordinals) to match ax.get_xlim()'s numeric representation on a date axis.
    xs, ys = [], []
    for x_arr, y_arr in xy_data:
        try:
            x_num = np.asarray(mdates.date2num(x_arr), dtype=float)
        except (TypeError, ValueError):
            x_num = np.asarray(x_arr, dtype=float)
        y_num = np.asarray(y_arr, dtype=float)
        xs.append(x_num)
        ys.append(y_num)
    x_all = np.concatenate(xs) if xs else np.array([])
    y_all = np.concatenate(ys) if ys else np.array([])
    finite = np.isfinite(x_all) & np.isfinite(y_all)
    x_all, y_all = x_all[finite], y_all[finite]

    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    wx, wy = box_frac

    legend_bbox_frac = None
    if legend is not None:
        try:
            ax.figure.canvas.draw()
            renderer = ax.figure.canvas.get_renderer()
            bbox = legend.get_window_extent(renderer).transformed(ax.transAxes.inverted())
            legend_bbox_frac = (bbox.x0, bbox.y0, bbox.x1, bbox.y1)
        except Exception:
            legend_bbox_frac = None  # renderer unavailable on this backend — skip penalty

    scores = {}
    for corner in candidates:
        anchor = CORNER_ANCHORS[corner]
        bx0 = x0 + (0.0 if 'left' in corner else (1 - wx)) * (x1 - x0)
        bx1 = bx0 + wx * (x1 - x0)
        by0 = y0 + (0.0 if 'lower' in corner else (1 - wy)) * (y1 - y0)
        by1 = by0 + wy * (y1 - y0)
        if x_all.size:
            score = float(np.count_nonzero(
                (x_all >= bx0) & (x_all <= bx1) & (y_all >= by0) & (y_all <= by1)))
        else:
            score = 0.0
        if legend_bbox_frac is not None:
            box_frac_rect = _corner_box_axes_frac(corner, box_frac)
            if _rects_overlap(box_frac_rect, legend_bbox_frac):
                score += 1e6
        scores[corner] = score

    min_score = min(scores.values())
    best = [c for c in candidates if scores[c] == min_score]
    chosen = next((c for c in _CORNER_TIE_BREAK if c in best), best[0])

    anchor = CORNER_ANCHORS[chosen]
    for k in ('ha', 'va', 'transform'):
        text_kwargs.pop(k, None)
    ax.text(anchor['x'], anchor['y'], text, transform=ax.transAxes,
            ha=anchor['ha'], va=anchor['va'], **text_kwargs)
    return chosen
