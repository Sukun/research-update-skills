---
name: 0-explore-data
description: Inspect a research project, data, code, notes, and prior outputs to establish bounded execution context. Use when asked to explore data or a project, verify inputs for a Task Contract, inspect dataset structure, or fill a specific planning gap. Default to read-only inspection; create reports or plots only when they are explicit approved deliverables.
---

# Explore Data and Project Context

Build only the context needed for the current request. Read existing knowledge before scanning raw data.

## Default boundary

- Treat inspection as read-only.
- Do not create an EDA report, plot, cache, converted dataset, or summary file unless it is an explicit deliverable.
- Do not interpret scientific meaning, choose a preferred result, or propose a broader experiment.
- Do not load a full large dataset when metadata or a representative sample is sufficient.
- Stay inside the user-specified directory and any explicitly referenced read-only sources.

## Workflow

1. Read applicable `CLAUDE.md`, `AGENTS.md`, project notes, prior reports, configs, and output summaries.
2. State what is already known and identify only the gaps that block the request.
3. Inspect the minimum files needed to close those gaps:
   - inventory names, counts, formats, and sizes;
   - inspect dimensions, variables, coordinates, units, coverage, and missing-value conventions;
   - compute small structural checks only when needed.
4. Report facts, assumptions, conflicts, and unresolved blockers separately.
5. Stop when the requested context is sufficient.

For many similar files, inspect metadata plus a representative sample. Escalate before a full scan, external download, expensive calculation, or any write.

## Optional explicit EDA outputs

Generate a report or quick-look plot only when the user or an approved Task Contract names it as a deliverable. Before writing:

- confirm the output path and overwrite policy;
- count it in the Scope Budget;
- use a bounded sample before full processing;
- label observations as structural or descriptive, not scientific interpretation.

Never modify raw data. If an output already exists, stop and request a versioned destination unless overwrite approval is explicit.
