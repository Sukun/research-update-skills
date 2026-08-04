"""
Figure layout helpers.

Historical conventions encoded here:
  - Default figsize (14, 6) for single-panel landscape
  - Default figsize (8, 8) for square panels (maps, T-S)
  - tight_layout() is the default spacing method
  - save_fig() always uses dpi=300 and bbox_inches='tight'
  - Style is applied with apply_style() before any plotting
"""

import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Absolute path to the styles directory — resolved at import time
_STYLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles')

# Default figsize presets (PPT-oriented; scale down for paper if needed)
_FIGSIZE_PRESETS = {
    'single':     (14, 6),   # single landscape panel
    'square':     (8,  8),   # square panel (regional maps, T-S)
    'wide':       (16, 5),   # very wide single panel
    '1x2':        (16, 6),   # two panels side by side
    '2x1':        (14, 8),   # two panels stacked
    '2x2':        (14, 10),  # 2×2 grid
    '2x3':        (18, 10),  # 2×3 grid
    '3x4':        (20, 14),  # 3×4 grid
}


def apply_style(mode='ppt'):
    """Apply the shared base style plus a named mode overlay.

    Parameters
    ----------
    mode : str
        'ppt' (default) or 'paper'.

    Notes
    -----
    Always calls plt.style.use('seaborn-v0_8-paper') first (the universal
    historical base), then overlays the mode-specific mplstyle file.
    """
    plt.style.use('seaborn-v0_8-paper')
    style_path = os.path.join(_STYLES_DIR, f'{mode}.mplstyle')
    if not os.path.exists(style_path):
        raise FileNotFoundError(f'Style file not found: {style_path}')
    plt.style.use(style_path)


def make_figure(nrows=1, ncols=1, preset=None, figsize=None,
                hspace=0.1, wspace=0.1, sharex=False, sharey=False,
                **subplot_kw):
    """Create a figure with a standard subplot grid.

    Parameters
    ----------
    nrows, ncols : int
        Grid dimensions.
    preset : str, optional
        Named size preset ('single', 'square', '1x2', '2x1', '2x2', '2x3',
        '3x4', 'wide'). Overrides figsize if given.
    figsize : tuple, optional
        Explicit (width, height) in inches. Used if preset is None.
    hspace : float
        Vertical space between rows. Starting default: 0.1.
    wspace : float
        Horizontal space between columns. Starting default: 0.1.
    sharex, sharey : bool
        Share axes across the grid.
    **subplot_kw :
        Passed to plt.subplots().

    Returns
    -------
    fig : Figure
    axes : Axes or ndarray of Axes
    """
    if preset is not None:
        figsize = _FIGSIZE_PRESETS.get(preset, (14, 6))
    elif figsize is None:
        figsize = (14, 6)

    fig, axes = plt.subplots(
        nrows, ncols,
        figsize=figsize,
        sharex=sharex, sharey=sharey,
        **subplot_kw,
    )
    fig.subplots_adjust(hspace=hspace, wspace=wspace)
    return fig, axes


def make_gridspec_figure(nrows, ncols, figsize=None, hspace=0.1, wspace=0.1):
    """Create a figure with a GridSpec for fine-grained panel control.

    Parameters
    ----------
    nrows, ncols : int
        Grid dimensions.
    figsize : tuple, optional
        Figure size. Default (14, 6).
    hspace : float
        Vertical space between rows.
    wspace : float
        Horizontal space between columns.

    Returns
    -------
    fig : Figure
    gs : GridSpec
    """
    if figsize is None:
        figsize = (14, 6)
    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(nrows, ncols, hspace=hspace, wspace=wspace)
    return fig, gs


def save_fig(fig, filepath, dpi=300, close=True):
    """Save figure to disk at 300 DPI, then close it.

    Parameters
    ----------
    fig : Figure
    filepath : str or Path
        Output file path (png, pdf, svg, etc.).
    dpi : int
        Resolution. Default 300.
    close : bool
        Close the figure after saving. Default True.
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
    if close:
        plt.close(fig)
    print(f'Saved: {filepath}')


def pad_yaxis(ax, margin=0.05):
    """Reduce excessive top/bottom whitespace on a line-plot axes.

    Adds a fractional margin to the data range without calling ax.autoscale(),
    which can produce large padding. Call after all lines have been plotted.

    Parameters
    ----------
    ax : Axes
    margin : float
        Fractional margin added above and below the data range.
    """
    lines = ax.get_lines()
    if not lines:
        return
    import numpy as np
    ys = [y for line in lines for y in line.get_ydata() if np.isfinite(y)]
    if not ys:
        return
    lo, hi = min(ys), max(ys)
    span = hi - lo if hi != lo else 1.0
    ax.set_ylim(lo - margin * span, hi + margin * span)
