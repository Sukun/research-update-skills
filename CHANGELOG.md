# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
