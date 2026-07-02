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

Two more run in the background the whole time: `noteit` catches an insight or a
bug-fix detail the moment you have it, and `polish-plots` makes sure figures look
presentable without you hand-tuning `rcParams` every time.

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

1. **Explore** the data with `0-explore-data` before you plan against it — it reads
   existing docs first, then scans raw data, and produces an `EDA_REPORT.md` **plus a
   set of quick-look plots** (time series, spatial snapshot, histogram, coverage map),
   not just a text summary.
2. **Plan** the task with `1-plan-task`. This runs inside Claude Code's built-in Plan
   Mode, but produces something Plan Mode alone doesn't: a structured plan **file** on
   disk (`doc/*.md`) with a fixed schema — purpose, data sources, methodology, risks —
   that outlives the current session. A Plan Mode approval is a one-time,
   in-conversation gate; this plan document is a persistent artifact that
   `2-review-plan` audits later and `3-conduct-plan` executes from, possibly in a
   completely different session.
3. **Review** the plan (optional) with `2-review-plan` — a separate pass, run after the
   fact, that reads the plan file **and** your existing code, notes, and prior results
   (`REFERENCE_DIR`) as a cross-check: are the metrics valid, is the baseline fair, does
   this actually match what's already in the repo? That's the double-check
   `1-plan-task` alone can't do — it doesn't have your prior work in front of it while
   drafting. Worth it before anything paper-submission-level or compute-expensive; skip
   it for a routine exploratory pass.
4. **Conduct** the plan with `3-conduct-plan` — this is the skill that actually writes
   Python code and runs the experiment, then reorganizes the rough instructions into a
   clean, dated research note. It's an *execution assistant*, not an autonomous
   research agent: it runs the plan *you* already reviewed — it doesn't decide what
   the plan should be or what the results mean.
5. **Report** with `4-report` — once the experiment has run, this gathers the
   resulting notes and figures into one document, instead of you opening and writing
   up each output figure by hand. And/or **design and create slides**
   (`5-ppt-design` → `6-ppt-create`) for the next check-in.

Throughout: `organize-notes` keeps a living notes index; `noteit` is for the
lightweight catch — right after finishing an implementation, a modification, or a bug
fix, log the detail that's worth remembering before it's forgotten; and `polish-plots`
applies your preferred matplotlib style, used both *before* the numerical experiment
(so figures come out styled from the start) and again *before* `4-report` (to clean up
anything that still needs it).

## Skills at a glance

Each skill is a function: an explicit invocation, a defined input, a defined output.
No skill guesses which one you meant from a vague phrase — you call it directly.

| Skill | When to use it | Invoke | Input | Output |
|---|---|---|---|---|
| `0-explore-data` | Starting a new dataset or project, before you plan against it | `/0-explore-data <path-to-project-or-data-dir>` | A data/project directory | `EDA_REPORT.md` + `eda_plots/` (quick-look plots) |
| `1-plan-task` | Starting a new experiment or task | `/1-plan-task <work_dir>` | A rough task description (conversation context) | Structured plan doc at `<work_dir>/doc/*.md` |
| `2-review-plan` | Before running something costly — cross-checks the plan against local docs/prior results | `/2-review-plan <path-to-plan.md>` | A plan file + a reference directory of existing code/notes | Verdict (ACCEPT / CONDITIONALLY_ACCEPT / REJECT) + fix list |
| `3-conduct-plan` | Executing an already-reviewed plan end to end *(execution assistant — see note above)* | `/3-conduct-plan <path-to-readme.md>` | A reviewed instruction document | Written + run scripts, generated outputs, a clean sectioned research note |
| `4-report` | After the experiment runs — gathers outputs into one document instead of writing up each figure by hand | `/4-report <notes_dir>` | A directory of research notes and figures | `TECH_REPORT_DRAFT.md` or `PAPER_DRAFT.md` |
| `5-ppt-design` | Before a group meeting or talk — deciding the story | `/5-ppt-design <path-to-notes-or-draft>` | Research notes or a rough draft | `<topic>_<dd-mm-yyyy>.md` storyboard |
| `6-ppt-create` | Once the storyboard is approved — mechanical export only | `/6-ppt-create <path-to-storyboard.md>` | An approved storyboard file | `.pptx`, rendered via Pandoc |
| `organize-notes` | After a work session, before you forget the details | `/organize-notes <target_directory>` | A project directory with scattered notes/figures | `RESEARCH_NOTES.md` index + `notes/<topic>.md` |
| `noteit` | Right after finishing an implementation or a fix — capture the detail before it's gone | `/noteit <what to remember>` | An insight, conclusion, or bug-fix detail | Dated entries appended to `docs/<PROJECT>_notes.md` + `~/docs/quick_notes.md` |
| `polish-plots` | Before the numerical experiment (styled from the start) and again before `4-report` | `/polish-plots <path-to-script.py>` | A Python matplotlib script | The same script refactored onto the shared style templates |

## Install

These are [Claude Code skills](https://docs.claude.com/en/docs/claude-code) — plain
folders with a `SKILL.md` that the agent reads and invokes by name.

**Prerequisites:**
- [Pandoc](https://pandoc.org/installing.html) — **required for `6-ppt-create`**
  (`brew install pandoc`, `apt install pandoc`, or see the link for other platforms).
- `pip install python-pptx pillow` — also required for `6-ppt-create`.
- Python + `matplotlib` — required for `polish-plots` (`cartopy` optional, map plots
  only).
- Everything else needs nothing beyond Claude Code itself.

```bash
git clone https://github.com/<you>/research-update-skills.git
cp -r research-update-skills/skills/* ~/.claude/skills/
```

Or symlink instead of copying if you want to track updates:

```bash
ln -s "$(pwd)/research-update-skills/skills/"* ~/.claude/skills/
```

**Invoke a skill explicitly, with a target**, e.g.:

```
/0-explore-data data/stations/
/4-report notes/
```

This repo intentionally does not rely on natural-language trigger-phrase matching —
every `SKILL.md` here documents a `/skill-name <target>` invocation instead, so you get
the exact skill you meant, not a best guess at which vague phrase you meant. If you're
using a different skill-folder convention (e.g. a Copilot-style skills directory), the
same folders should drop in unchanged — each is self-contained.

## 5-minute demo

[`examples/demo-precip-trend/`](examples/demo-precip-trend/) walks through the whole
loop on a small, synthetic scenario: a rough one-paragraph experiment log goes in, a
plan, research notes, and a slide storyboard come out — the same shape as a real week's
worth of "get this ready to show my advisor." Start there — reading it end to end takes
about five minutes.

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
