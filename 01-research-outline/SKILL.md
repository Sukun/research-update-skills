---
name: 01-research-outline
description: "DRAFT. Build, update or audit a project's question-based research outline (docs/outline.md): L1 framework, concise L2 text with 0–2 figure candidates, and links to L3 evidence (topic records, or Evidence Index + Figure Gallery as fallback). Use when the user wants to organise a research project into a reviewable outline, absorb new results into it, check its consistency, or prepare it as the source of a project deck. Never selects representative figures and never rewrites topic records."
---
# Research outline (draft)

Read [references/framework.md](references/framework.md) first. It defines the levels (D1), topic-record sections (D2), L3 dual mode (D3), owners (D4), L2 writing rules (D5), figure and evidence symbols (D6), slides (D7), update workflow (D8) and non-goals (D9). This file only describes the procedure.

## Modes

| Mode | Use when | Writes |
|---|---|---|
| `init` | No outline yet, or a legacy project to organise | `docs/outline.md`; fallback L3 files only if no topic records exist |
| `update` | New or refreshed topic records, notes or results | Proposed L2 edits, applied after approval |
| `audit` | Before a talk, after a batch of changes, or on request | Report only (plus check-script output) |

Infer the mode from the request; if unclear, run `audit`.

## Common first steps

1. Check `git status`, branch and recent commits. Protect uncommitted user changes; work on a branch for multi-file edits.
2. Read the existing entry documents: README, outline, Roadmap, Evidence Index, todo, topic records (`**/00_README.md` with an `Outline:` line), folder READMEs. Reuse what exists; do not duplicate an accepted structure.
3. Build a crosswalk in memory: L2 → topic record (if any) → folder records → historical deck pages → figures.

## init

1. Propose the L1/L2 tree from the research question and existing records. Ask the author to accept or edit the headings before writing body text. If an accepted outline exists, keep its headings exactly.
2. For each L2 decide the L3 source (D3): topic record if present; otherwise an Evidence Index section and a Gallery section.
3. Investigation may be delegated to cheaper sub-agents, in parallel and read-only: (a) evidence per L2 with sources and conflicts, (b) figure catalogue per L2 with conditions and like-for-like groups. Verify consequential claims yourself against the source before using them.
4. Write every L2 yourself (D5). Add 0–2 figures as `- [ ]` candidates (D6). Never write `[x]`.
5. Write fallback L3 files only where no topic record exists. Keep them in one Evidence Index and one Gallery, not one file per L2.
6. Add or run the lightweight checks (D8). Report conflicts found; do not resolve scientific conflicts silently.

## update

1. Identify what changed: new or refreshed topic records (check `Outline:` lines), Log entries, folder records, Roadmap.
2. For each affected L2, draft the minimal text change and any new `[ ]` candidates taken from the topic record's Summary figures. Show the diff and the source of each changed claim; apply after approval.
3. When an L2 gains its first topic record, repoint its L3 link and shrink its Gallery section to one link line (D3).
4. Leave `[x]` figures untouched unless the author asks; if a selected figure's source changed or disappeared, report it.

## audit

Report, by L2:

- broken links or anchors; outline heading tree changed;
- images without a status line; L2 without an L3 link;
- L2 claims with no traceable source, or that conflict with L3, Roadmap or folder records;
- `[ ]` candidates whose figure is missing locally; `[x]` figures that changed upstream;
- every `!` (conflict) and `~` (stale) item with its stated reason; every `?` (open) item in the Evidence lines;
- Roadmap entries mixing completed experiments with direction research;
- slide text not found in the outline (if a project deck exists).

## Project deck

Derive a storyboard from the outline (one slide per L2; L1 as corner label; finding/question titles may be added in the storyboard), then render with `6-ppt-create` and run visual QA through real office software (D7). Slide text must be copied from the outline; run the bullet-versus-outline check before reporting.

## Boundaries

- Do not choose representative figures, tick checkboxes, or change topic records' scientific content.
- Do not modify scientific code or data; do not delete historical decks, Canvas files or figures.
- Do not push or merge without explicit permission.
- Keep the project's language; do not translate unless asked.

## Report

Changed files; L2s rewritten or unchanged and why; figures awaiting the author's selection; conflicts left open with their sources; checks run and results; anything not verified.
