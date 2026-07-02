"""
polish-plots — project-wide matplotlib style and plotting helpers.

Bundled directly inside the ~/.claude/skills/polish-plots skill folder — fully
self-contained, no external shared-plotting package required.

Quick start
-----------
    import sys, os
    sys.path.insert(0, os.path.expanduser('~/.claude/skills/polish-plots'))

    from plot_templates.layout import apply_style, make_figure, save_fig
    from plot_templates.line import line_plot
    from plot_templates.contourf import plot_contourf
    from plot_templates.global_map import make_map_ax, plot_map_field
    from plot_templates.colorbar import add_colorbar, add_shared_colorbar

Style modes
-----------
    apply_style('ppt')    # large fonts, for presentations (default)
    apply_style('paper')  # smaller fonts, for manuscripts

See SKILL.md for coding rules for automated agents.
See docs/plot_style_guide.md for full usage documentation.
"""

import os

SHARED_ROOT = os.path.dirname(__file__)
STYLES_DIR = os.path.join(SHARED_ROOT, 'styles')
