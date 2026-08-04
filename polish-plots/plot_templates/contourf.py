"""
Filled contour plot helpers (Hovmöller, depth-time, density-latitude).

Historical conventions encoded here:
  - RdBu_r for diverging fields (dominant); viridis for sequential
  - TwoSlopeNorm(vmin, vcenter=0, vmax) for diverging fields
  - extend='both' when explicit vmin/vmax are used
  - colorbar: shrink=0.9, pad=0.02 (single panel)
  - ax.invert_yaxis() for depth/density y-axis
  - Thin black contour overlay (linewidths=0.1–0.3) is common
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from .colorbar import add_colorbar


def _auto_norm_and_cmap(vmin, vmax, cmap, vcenter):
    """Return (norm, cmap_name) based on sign of vmin/vmax."""
    if cmap is not None:
        # User-supplied cmap: derive norm from vcenter if data is diverging
        if vmin < 0 < vmax and vcenter is not None:
            norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
        else:
            norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
        return norm, cmap

    if vmin < 0 < vmax:
        # Diverging: RdBu_r with TwoSlopeNorm
        vcenter = vcenter if vcenter is not None else 0.0
        norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
        return norm, 'RdBu_r'
    else:
        # Sequential
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
        return norm, 'viridis'


def plot_contourf(ax, x, y, z, vmin=None, vmax=None, vcenter=None,
                  cmap=None, levels=None, n_levels=20,
                  extend='both', add_cb=True, cb_label='',
                  invert_y=False, overlay_contour=False,
                  contour_levels=None, contour_lw=0.2,
                  **kwargs):
    """Plot a filled contour on ax with historical defaults.

    Parameters
    ----------
    ax : Axes
        Target axes.
    x, y : array-like
        1-D or 2-D coordinate arrays (e.g. time/lat, depth/density).
    z : 2-D array-like
        Data to plot. Shape must be consistent with x, y.
    vmin, vmax : float, optional
        Color scale limits. If None, inferred from data percentiles (5–95).
    vcenter : float, optional
        Center of diverging colormap. Default 0.
    cmap : str, optional
        Colormap name. Auto-selected (RdBu_r or viridis) if None.
    levels : array-like, optional
        Explicit contour levels. Overrides n_levels.
    n_levels : int
        Number of evenly-spaced levels if levels is not given. Default 20.
    extend : str
        'both', 'min', 'max', or 'neither'. Default 'both'.
    add_cb : bool
        Attach a colorbar. Default True.
    cb_label : str
        Colorbar label.
    invert_y : bool
        Invert y-axis (for depth/density panels). Default False.
    overlay_contour : bool
        Add thin black contour overlay on top. Default False.
    contour_levels : array-like, optional
        Levels for the contour overlay. Defaults to same as filled levels.
    contour_lw : float
        Line width for contour overlay. Default 0.2.
    **kwargs
        Extra kwargs passed to ax.contourf().

    Returns
    -------
    mappable : QuadContourSet
        Return value of ax.contourf(), usable for colorbar calls.
    cb : Colorbar or None
    """
    z = np.asarray(z)
    if vmin is None:
        vmin = float(np.nanpercentile(z, 5))
    if vmax is None:
        vmax = float(np.nanpercentile(z, 95))

    norm, cmap = _auto_norm_and_cmap(vmin, vmax, cmap, vcenter)

    if levels is None:
        levels = np.linspace(vmin, vmax, n_levels)

    im = ax.contourf(x, y, z, levels=levels, cmap=cmap, norm=norm,
                     extend=extend, **kwargs)

    if overlay_contour:
        clev = contour_levels if contour_levels is not None else levels
        ax.contour(x, y, z, levels=clev, colors='k',
                   linewidths=contour_lw, alpha=0.5)

    if invert_y:
        ax.invert_yaxis()

    cb = None
    if add_cb:
        cb = add_colorbar(im, ax, label=cb_label)

    return im, cb


def plot_pcolormesh(ax, x, y, z, vmin=None, vmax=None, vcenter=None,
                    cmap=None, add_cb=True, cb_label='',
                    invert_y=False, **kwargs):
    """Plot a pcolormesh (faster than contourf for regular grids).

    Same auto-norm logic as plot_contourf. Use for regular lon-lat grids
    where contour smoothing is not desired.
    """
    z = np.asarray(z)
    if vmin is None:
        vmin = float(np.nanpercentile(z, 5))
    if vmax is None:
        vmax = float(np.nanpercentile(z, 95))

    norm, cmap = _auto_norm_and_cmap(vmin, vmax, cmap, vcenter)

    im = ax.pcolormesh(x, y, z, cmap=cmap, norm=norm,
                       shading='auto', **kwargs)

    if invert_y:
        ax.invert_yaxis()

    cb = None
    if add_cb:
        cb = add_colorbar(im, ax, label=cb_label)

    return im, cb
