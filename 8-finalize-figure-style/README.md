# figure-style — Claude Code skill

Portable, standalone version of the "figure-style" publication-figure-QA
skill — pure matplotlib/numpy/scipy, no platform SDK dependencies. Ported for
use with Claude Code on a cluster (or any Agent-Skills-compatible client).

## Install (project-scoped, recommended)

From the root of your project repo (e.g. your paper-draft repo on the
cluster):

```bash
mkdir -p .claude/skills
cp -r /path/to/figure-style .claude/skills/figure-style
```

Claude Code auto-discovers skills under `.claude/skills/` in your working
directory and every parent directory up to the repo root, so committing this
folder to your repo means every collaborator (and every future session) gets
it automatically.

## Install (personal, all projects)

```bash
mkdir -p ~/.agents/skills
cp -r /path/to/figure-style ~/.agents/skills/8-finalize-figure-style
```

## Verify it loads

Start Claude Code in the project and ask something like *"polish this figure
for publication"* — Claude Code should pick up the skill via its
`description` field in `SKILL.md` and mention loading it. You can also ask it
directly: *"do you have the figure-style skill available?"*

## What's inside

- `SKILL.md` — the skill manifest (frontmatter + workflow instructions).
- `reference/RULES.md` — full §0–§9 checklist (data fidelity, label
  floor/ceiling, axes, color, typography, chart-family guidance, layout,
  anti-patterns, render-then-verify QA).
- `scripts/figure_style.py` — matplotlib helper functions
  (`apply_figure_style`, `focal_palette`, `bar_with_points`,
  `strip_with_median`, `panel_letter`, `end_of_line_labels`, `panel_crops`,
  `set_frame`, `goodness_arrow`). Pure stdlib + matplotlib + numpy, with
  `scipy.stats` used only inside the optional `ci95` error-bar path.

## Requirements

```
matplotlib
numpy
scipy       # only needed if you use bar_with_points(errorbar="ci95")
pillow      # only needed for the §9.2 perceptual-crop workflow
```

## Note on scope vs. the full Claude Science skill set

This package covers **single-figure** correctness and polish (the
`figure-style` layer). It does not include the multi-panel composition
orchestrator (`figure-composer`, which fans work out across sub-agents) or
the whole-paper figure-arc reviewer (`paper-narrative`) from the source
platform — those rely on that platform's agent-delegation SDK and aren't
portable as plain scripts. For a single plot or a hand-assembled multi-panel
figure, this package is self-sufficient.
