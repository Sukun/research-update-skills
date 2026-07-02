# research-update-skills

**Turn messy numerical experiment work into advisor-ready updates.**

A small set of Claude Code skills built from my own daily research workflow. Not a
research-automation framework. Not a giant skill library.

**Who this is for:** graduate students, postdocs, and early-career faculty who run
numerical experiments, simulations, or data analysis as their main research activity,
and who regularly have to explain "what did I actually do this week" to an advisor, PI,
or collaborator.

**Who this is not for:** people looking for a fully autonomous "AI does the research"
system, a large all-purpose academic skill library (lectures, grant writing, email
triage), or a workflow built around meetings and project management rather than
hands-on computational work. If that's you, this probably isn't the right repo — no
hard feelings, just save yourself the install.

Just the handful of steps I actually use every week to turn scattered experiment
progress — half-finished scripts, a folder of figures, a few Slack-message-length
insights — into a clear plan, clean notes, a short report, and a slide deck I can put in
front of an advisor or collaborator without an extra hour of formatting.

If most of your "research overhead" is repetitive, mechanical, and eats time you'd
rather spend on the actual science — writing up what you did, organizing notes so you
can find them later, making figures presentable, building the same slide skeleton every
week — that's exactly what these skills offload. The judgment stays yours; the grunt
work doesn't have to.

## What it actually does

Five recurring moments in a research week, each mapped to a skill:

1. You have a vague idea → turn it into a concrete plan.
2. You have scattered results and logs → turn them into organized notes.
3. You're about to run something expensive → sanity-check the plan first.
4. You have results → turn them into a short progress report.
5. You need to present → turn the report/notes into a slide storyboard, then a deck.

Two more run in the background the whole time: `noteit` catches an insight the moment
you have it, and `polish-plots` makes sure figures look presentable without you
hand-tuning `rcParams` every time.

## What it does not do

- It does not decide what your research question should be.
- It does not draw scientific conclusions for you.
- It does not run unattended experiments while you're away.
- It does not replace your judgment — you approve every meaningful step (plans get
  reviewed before execution, reports get read before they're sent).

## Workflow

```
0-explore-data ──► 1-plan-task ──► [2-review-plan] ──► 3-conduct-plan ──┬──► 4-report
                                                                          └──► 5-ppt-design ──► 6-ppt-create

always on, any time:  organize-notes · noteit · polish-plots
```

1. **Explore** the data before you plan against it.
2. **Plan** the task — a structured questionnaire produces a plan doc, then a critical
   pass enriches it with concrete file paths, data formats, and risks.
3. **Review** the plan (optional) — worth it before anything paper-submission-level or
   compute-expensive; skip it for a routine exploratory pass.
4. **Conduct** the plan — drives a rough `readme.md` through implement → document. This
   is an *execution assistant*, not an autonomous research agent: it runs the plan
   *you* already reviewed, writes the code, and documents the outcome — it doesn't
   decide what the plan should be or what the results mean.
5. **Write it up** as a report, and/or **design and create slides** for the next
   check-in.

Throughout: `organize-notes` keeps a living notes index, `noteit` logs quick insights as
you have them, and `polish-plots` keeps matplotlib output consistent.

## Skills at a glance

| Skill | When to use it | Trigger phrase (example) | Output |
|---|---|---|---|
| `0-explore-data` | Starting a new dataset or project, before you plan against it | "explore this data" | EDA report + quick-look plots |
| `1-plan-task` | Starting a new experiment or task | "make a plan" | Structured plan doc in `docs/` |
| `2-review-plan` | Before running something costly | "review my plan" | Verdict (ACCEPT / CONDITIONALLY_ACCEPT / REJECT) + fix list |
| `3-conduct-plan` | Executing an already-reviewed plan end to end *(execution assistant — see note above)* | "conduct task from readme" | Scripts + outputs + a clean, sectioned research note |
| `4-report` | Before a check-in with your advisor or collaborators | "write a tech report" | `TECH_REPORT_DRAFT.md` or `PAPER_DRAFT.md` |
| `5-ppt-design` | Before a group meeting or talk — deciding the story | "design slides" | `<topic>_<dd-mm-yyyy>.md` storyboard |
| `6-ppt-create` | Once the storyboard is approved — mechanical export only | "export to pptx" | `.pptx`, rendered via Pandoc |
| `organize-notes` | After a work session, before you forget the details | "organize research notes" | `RESEARCH_NOTES.md` index + `notes/<topic>.md` |
| `noteit` | The moment you realize something worth remembering | "save this insight" | Dated, appended research-log entry |
| `polish-plots` | Before figures go into a report or slide | "polish plots" | Matplotlib script refactored onto a shared style |

## Install

These are [Claude Code skills](https://docs.claude.com/en/docs/claude-code) — plain
folders with a `SKILL.md` that the agent reads and invokes by name.

```bash
git clone https://github.com/<you>/research-update-skills.git
cp -r research-update-skills/skills/* ~/.claude/skills/
```

Or symlink instead of copying if you want to track updates:

```bash
ln -s "$(pwd)/research-update-skills/skills/"* ~/.claude/skills/
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
loop on a small, synthetic scenario: a rough one-paragraph experiment log goes in, a
plan, research notes, and a slide storyboard come out — the same shape as a real week's
worth of "get this ready to show my advisor." Start there — reading it end to end takes
about five minutes.

## Design principles

- **Small over comprehensive.** Ten skills, one job each. No shared runtime, no plugin
  system, no config file.
- **Demo-first.** If you can't see it working in five minutes, it's not documented well
  enough yet.
- **Human-in-the-loop.** Every skill proposes; you approve. Plans get reviewed before
  execution, reports get read before they're sent.
- **File-based.** Everything a skill produces is a markdown file, a script, or a
  standard file format (`.pptx`, `.png`) — versioned with git, nothing locked into this
  repo.
- **Built from real use.** Every skill here has been used weekly on real analysis work,
  not written once and left untested.
- **No lock-in.** Stop using any single skill without breaking the others.

## Non-goals

- This repo is not for autonomous research.
- It does not replace scientific judgment.
- It does not decide what claims are valid.
- It does not turn vague ideas into publishable work without human review.
- It is designed to reduce friction in planning, documenting, and presenting research
  progress — not to remove the researcher from the loop.
- **No magic infra.** `6-ppt-create` needs Pandoc and `python-pptx` on your machine —
  that's a real dependency, not hidden away.
- **One-way, not synced.** This repo is a manually maintained snapshot of skills I use
  privately. It does not auto-update from my personal setup, and pushing changes here
  won't pull anything from it either.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — issues and small, focused PRs are welcome.

## License

MIT — see [LICENSE](LICENSE).
