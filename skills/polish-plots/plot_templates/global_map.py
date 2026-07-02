"""
Cartopy map helpers (global PlateCarree and regional Mercator).

Historical conventions encoded here:
  - ccrs.PlateCarree() for global maps
  - ccrs.Mercator() for regional (Atlantic) maps
  - cfeature.LAND facecolor='lightgrey', zorder=3
  - cfeature.COASTLINE, zorder=4
  - Gridlines: draw_labels=True, top/right labels off
  - transform=ccrs.PlateCarree() always required for plotted data
  - figsize (14, 6) for global maps; (7, 7) or (8, 8) for regional
  - No cmocean or cmcrameri required

Usage example
-------------
    from plot_templates.layout import apply_style, save_fig
    from plot_templates.global_map import make_map_ax, plot_map_field
    from plot_templates.colorbar import add_colorbar

    apply_style('ppt')
    fig = plt.figure(figsize=(14, 6))
    ax = make_map_ax(fig, 111)
    im, _ = plot_map_field(ax, lon, lat, data, vmin=-1, vmax=1, add_cb=False)
    add_colorbar(im, ax, label='SST anomaly (°C)')
    save_fig(fig, 'output/map.png')
"""

import numpy as np
import matplotlib.pyplot as plt

try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    _CARTOPY_AVAILABLE = True
except ImportError:
    _CARTOPY_AVAILABLE = False

from .colorbar import add_colorbar
from .contourf import _auto_norm_and_cmap


def _require_cartopy():
    if not _CARTOPY_AVAILABLE:
        raise ImportError(
            'cartopy is required for map plots. '
            'Install with: conda install -c conda-forge cartopy'
        )


def make_map_ax(fig, subplot_spec=111, projection='platecarree',
                extent=None, land=True, coastline=True, gridlines=True):
    """Add a Cartopy axes to a figure.

    Parameters
    ----------
    fig : Figure
    subplot_spec : int or SubplotSpec
        Position in the figure (e.g. 111 or a GridSpec cell).
    projection : str or CRS
        'platecarree' (default), 'mercator', 'northpolar', or a CRS object.
    extent : list, optional
        [lon_min, lon_max, lat_min, lat_max]. None = global.
    land : bool
        Draw land feature (lightgrey). Default True.
    coastline : bool
        Draw coastline. Default True.
    gridlines : bool
        Draw labelled gridlines. Default True.

    Returns
    -------
    ax : GeoAxes
    """
    _require_cartopy()

    if isinstance(projection, str):
        projection = {
            'platecarree': ccrs.PlateCarree(),
            'mercator': ccrs.Mercator(),
            'northpolar': ccrs.NorthPolarStereo(),
        }.get(projection.lower(), ccrs.PlateCarree())

    ax = fig.add_subplot(subplot_spec, projection=projection)

    if extent is not None:
        ax.set_extent(extent, crs=ccrs.PlateCarree())

    if land:
        ax.add_feature(cfeature.LAND, facecolor='lightgrey', zorder=3)
    if coastline:
        ax.add_feature(cfeature.COASTLINE, zorder=4, linewidth=0.5)
    if gridlines:
        gl = ax.gridlines(draw_labels=True, linewidth=0.5,
                          color='gray', alpha=0.5, linestyle='--')
        gl.top_labels = False
        gl.right_labels = False
        # Cartopy ignores rcParams for gridline labels — set explicitly.
        # Value comes from xtick.labelsize in ppt.mplstyle / paper.mplstyle.
        gl.xlabel_style = {'size': plt.rcParams['xtick.labelsize']}
        gl.ylabel_style = {'size': plt.rcParams['xtick.labelsize']}

    return ax


def plot_map_field(ax, lon, lat, data, vmin=None, vmax=None, vcenter=None,
                   cmap=None, levels=None, n_levels=20,
                   method='contourf', extend='both',
                   add_cb=True, cb_label='', **kwargs):
    """Plot a 2-D field on a Cartopy map axes.

    Parameters
    ----------
    ax : GeoAxes
        Created by make_map_ax().
    lon, lat : array-like
        1-D coordinate arrays or 2-D meshgrid arrays.
    data : 2-D array-like
        Field to plot. Shape (lat, lon).
    vmin, vmax : float, optional
        Color scale limits. Auto-detected from 5–95th percentile if None.
    vcenter : float, optional
        Center of diverging colormap. Default 0 when data crosses zero.
    cmap : str, optional
        Colormap. Auto-selected (RdBu_r / viridis) if None.
    levels : array-like, optional
        Explicit contour/colorbar levels.
    n_levels : int
        Number of levels if levels not given. Default 20.
    method : str
        'contourf' (default) or 'pcolormesh'.
    extend : str
        'both', 'min', 'max', 'neither'. Default 'both'.
    add_cb : bool
        Attach a colorbar. Default True.
    cb_label : str
        Colorbar label.
    **kwargs
        Passed to contourf or pcolormesh.

    Returns
    -------
    mappable, cb
    """
    _require_cartopy()

    data = np.asarray(data)
    if vmin is None:
        vmin = float(np.nanpercentile(data, 5))
    if vmax is None:
        vmax = float(np.nanpercentile(data, 95))

    norm, cmap = _auto_norm_and_cmap(vmin, vmax, cmap, vcenter)

    transform = ccrs.PlateCarree()

    if method == 'pcolormesh':
        im = ax.pcolormesh(lon, lat, data, cmap=cmap, norm=norm,
                           transform=transform, shading='auto', **kwargs)
    else:
        if levels is None:
            levels = np.linspace(vmin, vmax, n_levels)
        im = ax.contourf(lon, lat, data, levels=levels, cmap=cmap, norm=norm,
                         transform=transform, extend=extend, **kwargs)

    cb = None
    if add_cb:
        cb = add_colorbar(im, ax, label=cb_label)

    return im, cb


def make_map_grid(fig, nrows, ncols, projection='platecarree',
                  extent=None, land=True, coastline=True,
                  hspace=0.1, wspace=0.05):
    """Create a grid of Cartopy map axes using GridSpec.

    Parameters
    ----------
    fig : Figure
    nrows, ncols : int
    projection, extent, land, coastline : same as make_map_ax()
    hspace, wspace : float
        GridSpec spacing.

    Returns
    -------
    axes : list of GeoAxes (row-major order)
    """
    import matplotlib.gridspec as gridspec
    gs = gridspec.GridSpec(nrows, ncols, hspace=hspace, wspace=wspace)
    axes = []
    for i in range(nrows):
        for j in range(ncols):
            ax = make_map_ax(fig, gs[i, j], projection=projection,
                             extent=extent, land=land, coastline=coastline)
            axes.append(ax)
    return axes
