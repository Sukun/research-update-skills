# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.2.0] - 2026-08-04

### Added
- Approval-gated `TASK_CONTRACT.md` planning with Non-Goals, Scope Budget, allowed
  changed files, stop conditions, and a portable validator.
- `RUN_RECORD.json` and factual `VALIDATION.md` boundaries for contract execution.
- `claude-figure-style` and a portable public-skill-tree validator.
- Automatic corner placement for free text annotations in `polish-plots`, with numeric
  and datetime axis support.

### Changed
- Split bounded execution (`3-conduct-plan`) from explicit scientific interpretation
  (`4-report`); no skill silently adds fixes, generalisation, reports, or extra outputs.
- Reworked the example and README around the approval and provenance model.
- Removed machine-specific paths, project identifiers, personal examples, and private
  historical code inventories from the public release.

## [0.1.0] - 2026-07-02

Initial public release.

### Added
- `0-explore-data` — EDA report generation with quick-look plots.
- `1-plan-task` — two-stage research task planning (build, then critically review/enrich).
- `2-review-plan` — structured audit of a research plan (metric validity, baseline
  fairness, validation design, feasibility).
- `3-conduct-plan` — end-to-end conductor: plan → implement → document from a rough
  `readme.md`.
- `4-report` — informal or formal research report generation from notes.
- `5-ppt-design` — slide storyboard design from notes or a report.
- `6-ppt-create` — storyboard-to-`.pptx` rendering via Pandoc + python-pptx.
- `organize-notes` — living `RESEARCH_NOTES.md` index plus per-topic notes.
- `noteit` — quick research-log entries, per-project and global.
- `polish-plots` — shared matplotlib style helpers and refactoring rules.
- One end-to-end demo under `examples/demo-precip-trend/`.
