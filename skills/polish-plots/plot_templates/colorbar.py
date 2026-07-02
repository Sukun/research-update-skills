"""
Colorbar helpers.

Historical conventions encoded here:
  - shrink=0.9, pad=0.02 for single-panel colorbars
  - shrink=0.6, pad=0.02 for shared colorbars across multiple axes
  - extend='both' is the default (explicit vmin/vmax almost always used)
  - Vertical orientation default; horizontal available for bottom placement
"""

import matplotlib.pyplot as plt


def add_colorbar(mappable, ax, label='', shrink=0.9, pad=0.02,
                 extend='both', orientation='vertical', labelpad=4, **kwargs):
    """Add a standard vertical colorbar next to a single axes.

    Parameters
    ----------
    mappable : ScalarMappable
        Return value of contourf, pcolormesh, etc.
    ax : Axes
        The axes the colorbar belongs to.
    label : str
        Colorbar label (units or variable name).
    shrink : float
        Fraction of axes height. Historical default 0.9.
    pad : float
        Gap between axes and colorbar. Historical default 0.02.
    extend : str
        'both', 'min', 'max', or 'neither'. Default 'both'.
    orientation : str
        'vertical' (default) or 'horizontal'.
    labelpad : float
        Distance in points between tick labels and colorbar label. Default 4.

    Returns
    -------
    Colorbar
    """
    fig = ax.get_figure()
    cb = fig.colorbar(
        mappable, ax=ax,
        shrink=shrink, pad=pad,
        extend=extend, orientation=orientation,
        **kwargs,
    )
    if label:
        cb.set_label(label, labelpad=labelpad)
    return cb


def add_shared_colorbar(mappable, axes, fig=None, label='', shrink=0.6,
                        pad=0.02, extend='both', orientation='vertical',
                        labelpad=4, **kwargs):
    """Add a shared colorbar spanning all axes in a multi-panel figure.

    Parameters
    ----------
    mappable : ScalarMappable
        The reference contourf/pcolormesh return value (usually the last panel).
    axes : array-like of Axes
        All axes to be spanned by the colorbar.
    fig : Figure, optional
        Figure object. Inferred from axes if not given.
    label : str
        Colorbar label.
    shrink : float
        Fraction of total axes span. Historical default 0.6.
    pad : float
        Gap from axes edge. Historical default 0.02.
    extend : str
        'both', 'min', 'max', or 'neither'.
    orientation : str
        'vertical' (default) or 'horizontal'.
    labelpad : float
        Distance in points between tick labels and colorbar label. Default 4.

    Returns
    -------
    Colorbar
    """
    import numpy as np
    if fig is None:
        fig = axes.flat[0].get_figure() if hasattr(axes, 'flat') else axes[0].get_figure()
    ax_list = np.asarray(axes).ravel().tolist()
    cb = fig.colorbar(
        mappable, ax=ax_list,
        shrink=shrink, pad=pad,
        extend=extend, orientation=orientation,
        **kwargs,
    )
    if label:
        cb.set_label(label, labelpad=labelpad)
    return cb


def add_bottom_colorbar(mappable, ax, label='', shrink=0.8, pad=0.08,
                        extend='both', labelpad=2, **kwargs):
    """Horizontal colorbar placed below a single axes.

    Use when the axes is very wide or when vertical space is available below.

    Parameters
    ----------
    labelpad : float
        Distance in points between tick labels and colorbar label. Default 2
        (tighter than the matplotlib default of 4, appropriate for the
        compact horizontal layout).
    """
    fig = ax.get_figure()
    cb = fig.colorbar(
        mappable, ax=ax,
        shrink=shrink, pad=pad,
        extend=extend, orientation='horizontal',
        **kwargs,
    )
    if label:
        cb.set_label(label, labelpad=labelpad)
    return cb
