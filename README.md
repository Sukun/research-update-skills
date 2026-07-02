# research-flow-skills

*Small, opinionated Claude Code skills for everyday research.*

A set of Claude Code skills I actually use, day to day, for AI-assisted computational
research: turning a rough idea into a plan, running the analysis, keeping notes, writing
it up, and putting together slides. This isn't a framework — it's my workflow, packaged
so other researchers can borrow the pieces that are useful to them.

## Who this is for

Computational / quantitative researchers using [Claude Code](https://claude.com/claude-code)
(or a similarly skill-aware coding agent) who want less friction between "I have a rough
idea" and "I have a plan, some notes, and a report or slide deck to show for it."

## What it solves

Research work has a recurring shape: understand the data, plan the task, do the work,
write down what you learned, and eventually turn it into a report or a talk. These skills
cover that shape end to end, plus two things that are easy to let slide — keeping notes
as you go, and keeping plot style consistent across scripts.

## Workflow

```
0-explore-data ──► 1-plan-task ──► [2-review-plan] ──► 3-conduct-plan ──┬──► 4-report
                                                                          └──► 5-ppt-design ──► 6-ppt-create

always on, any time:  organize-notes · noteit · polish-plots
```

1. **Explore** the data before you plan against it.
2. **Plan** the task — a structured questionnaire produces a plan doc, then a critical pass
   enriches it with concrete file paths, data formats, and risks.
3. **Review** the plan (optional) — worth it for anything paper-submission-level or
   compute-expensive; skip it for routine exploratory work.
4. **Conduct** the plan — drives a rough `readme.md` through implement → document.
5. **Write it up** as a report, and/or **design and create slides**.

Throughout: `organize-notes` keeps a living notes index, `noteit` logs quick insights as
you have them, and `polish-plots` keeps matplotlib output consistent.

## Skills

| Skill | Trigger phrase (example) | Output |
|---|---|---|
| `0-explore-data` | "explore this data" | EDA report + quick-look plots |
| `1-plan-task` | "plan this research task" | plan doc in `docs/` |
| `2-review-plan` | "review this plan" | verdict (ACCEPT / CONDITIONALLY_ACCEPT / REJECT) + fix list |
| `3-conduct-plan` | "conduct task from readme" | scripts + outputs + a clean, sectioned research note |
| `4-report` | "write the report" | `TECH_REPORT_DRAFT.md` or `PAPER_DRAFT.md` |
| `5-ppt-design` | "design slides" | `<topic>_<dd-mm-yyyy>.md` storyboard |
| `6-ppt-create` | "create the slides" | `.pptx`, rendered via Pandoc |
| `organize-notes` | "organize notes" | `RESEARCH_NOTES.md` index + `notes/<topic>.md` |
| `noteit` | "log this note" | dated research-log entry |
| `polish-plots` | "polish plots" | matplotlib script refactored onto a shared style |

## Install

These are [Claude Code skills](https://docs.claude.com/en/docs/claude-code) — plain
folders with a `SKILL.md` that the agent reads and invokes by name.

```bash
git clone https://github.com/<you>/research-flow-skills.git
cp -r research-flow-skills/skills/* ~/.claude/skills/
```

Or symlink instead of copying if you want to track updates:

```bash
ln -s "$(pwd)/research-flow-skills/skills/"* ~/.claude/skills/
```

Invoke a skill by name, e.g. `/1-plan-task`, or just describe what you want ("plan this
task", "polish these plots") — Claude Code matches on the trigger phrases in each
`SKILL.md`. If you're using a different skill-folder convention (e.g. a Copilot-style
skills directory), the same folders should drop in unchanged — each is self-contained.

**Requirements** (only for the skills that need them):
- `polish-plots` — Python + `matplotlib`; `cartopy` optional, only for map plots.
- `6-ppt-create` — [Pandoc](https://pandoc.org/) on `PATH`, plus `python-pptx` and
  `Pillow` (`pip install python-pptx pillow`).
- Everything else needs nothing beyond Claude Code itself.

## 5-minute demo

[`examples/demo-precip-trend/`](examples/demo-precip-trend/) walks through the whole
pipeline on a small, synthetic scenario: a rough one-paragraph task description goes in,
a plan, research notes, and a slide storyboard come out. Start there — reading the demo
end to end takes about five minutes.

## Design principles

- **Small.** Ten skills, one job each. No shared runtime, no plugin system, no config file.
- **Plain outputs.** Everything a skill produces is a markdown file, a script, or a
  standard file format (`.pptx`, `.png`) — nothing locked into this repo.
- **Honest triggers.** Each skill lists the phrases that invoke it, in its own `SKILL.md`.
  No hidden magic about when something fires.
- **No lock-in.** Stop using any single skill without breaking the others.

## Non-goals

- **Not a framework.** There's no orchestration layer tying the skills together beyond the
  plain-markdown handoffs described above.
- **Not comprehensive.** These cover *my* workflow, not every research workflow. Missing a
  step you need? Fork it, or open an issue.
- **No magic infra.** `6-ppt-create` needs Pandoc and `python-pptx` on your machine —
  that's a real dependency, not hidden away. `3-conduct-plan` is the heaviest skill here;
  it expects a rough `readme.md` to drive and writes/runs code, so use it in normal
  (not plan) mode.
- **One-way, not synced.** This repo is a manually maintained snapshot of skills I use
  privately. It does not auto-update from my personal setup, and pushing changes here
  won't pull anything from it either.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — issues and small, focused PRs are welcome.

## License

MIT — see [LICENSE](LICENSE).
