---
name: 0-explore-data
description: "Project and data exploration. First reads existing project memory (docs, outputs, previous reports, CLAUDE.md) to build context, then fills gaps by scanning raw data files. Produces an EDA report with structure, coverage, statistics, and quick-look plots. Avoids redundant data scans when prior knowledge exists."
license: MIT
---

# Data & Project Exploration Skill

## Purpose

Build a working understanding of a project and its data. This is step zero of the research workflow — before you organise notes, plan experiments, or write code, you need to understand what you're working with.

**Key principle: read existing knowledge first, scan raw data only to fill gaps.** Most projects accumulate documentation, previous reports, and output summaries over time. Re-scanning raw data files from scratch is slow and wasteful when this knowledge already exists.

## When To Use

Trigger this skill when prompts include phrases like:
- "explore this data"
- "explore this project"
- "what data do I have"
- "EDA"
- "look at this dataset"
- "summarise the data"
- "data overview"
- "what's in this directory"
- "initial data check"
- "inspect the files"
- "help me understand this data"
- "get familiar with this project"
- "onboard me to this codebase"

## Parameters

| # | Parameter | Default | Description |
|---|-----------|---------|-------------|
| 1 | `DATA_DIR` | Current working directory | Directory containing data files to explore |
| 2 | `OUTPUT_FILE` | `EDA_REPORT.md` in `DATA_DIR` | Output report filename |
| 3 | `QUICK` | `false` | If `true`, skip plotting — text summary only |

---

## Workflow

### PHASE 0 — Read Project Memory (read-only, always do this first)

Before touching any raw data files, gather existing knowledge:

1. **Project configuration**: read `CLAUDE.md`, `.claude/` config, and any project-level instructions.
2. **Accumulated documentation**: search for and read files in common knowledge locations:
   - `docs/`, `doc/`, `documentation/`
   - `outputs/`, `output/`, `results/`, `output_*/`
   - `RESEARCH_NOTES.md`, `EXPERIMENT_NOTES.md`, `README.md`
   - Previous `EDA_REPORT.md` or `TECH_REPORT_DRAFT.md`
   - Any `.md` files at project root or in subdirectories
3. **Previous results**: scan for existing output summaries (`run_results.json`, `summary.json`, `*.log`).
4. **Claude memory**: read `.claude/` memory files if they exist — they contain accumulated project context from prior conversations.

**After reading**: summarise what is already known about the project — its purpose, data sources, structure, key findings, and any gaps. Present this to the user.

**Decision point**: if existing documentation already covers data structure, variables, and coverage sufficiently, **skip Phases 1–2** and go directly to Phase 3 (plots) or Phase 4 (report). Only scan raw data files to fill specific gaps.

### PHASE 1 — File Inventory (read-only, skip if already known)

1. **Scan directory** recursively. List files grouped by type:
   - Data files: `.nc`, `.npz`, `.npy`, `.csv`, `.parquet`, `.zarr`, `.grib`, `.h5`, `.hdf5`, `.mat`
   - Config files: `.yaml`, `.json`, `.toml`, `.cfg`, `.ini`
   - Documentation: `.md`, `.txt`, `.pdf`
   - Figures: `.png`, `.pdf`, `.svg`
   - Scripts: `.py`, `.sh`, `.r`, `.m`
2. **Report file counts** and total sizes per type.
3. **Identify the primary data files** — the ones likely to be the main dataset (largest, most numerous, or matching common patterns).

### PHASE 2 — Structure & Coverage (skip if already known from Phase 0)

For each primary data file (or a representative sample if many):

1. **Open and inspect** structure:
   - NetCDF/HDF5: dimensions, variables, attributes, coordinate ranges.
   - NPZ/NPY: array shapes, dtypes.
   - CSV/Parquet: columns, dtypes, row counts.
2. **Summarise coverage**:
   - Temporal: start date, end date, time step, gaps.
   - Spatial: lat/lon bounds, grid resolution, depth levels (if applicable).
   - Variables: list with units and brief description.
3. **Basic statistics** for key variables:
   - Min, max, mean, std, % NaN/missing.
   - Flag anomalies: all-NaN slices, constant values, suspicious ranges.

### PHASE 3 — Quick-Look Plots (skip if `QUICK=true`)

Generate minimal diagnostic plots (save to `DATA_DIR/eda_plots/`):
1. **Time series**: mean of primary variable(s) over time.
2. **Spatial snapshot**: one representative time step as a map or heatmap.
3. **Histogram**: distribution of primary variable(s).
4. **Coverage map**: where data exists vs where it's missing (spatial).

Use matplotlib with sensible defaults. No styling polish needed — these are diagnostic.

### PHASE 4 — EDA Report

Write `OUTPUT_FILE` with:

```markdown
---
title: "Data & Project Exploration Report"
data_dir: "<DATA_DIR>"
generated: <today's date>
status: initial exploration
---

# Data & Project Exploration Report

## Project Context (from existing documentation)
- **Purpose**: [what this project is about, from docs/README/CLAUDE.md]
- **Key data sources**: [datasets identified from prior documentation]
- **Current state**: [what has been done, key findings so far]
- **Source documents read**: [list of docs that informed this section]

## File Inventory
| Type | Count | Total Size | Example |
|---|---|---|---|

## Data Structure
### [Primary dataset name]
- Format: [NetCDF / NPZ / CSV / ...]
- Dimensions: [list with sizes]
- Variables: [list with units]
- Temporal coverage: [start] to [end], [step], [N gaps]
- Spatial coverage: [lat range] × [lon range], [resolution]

## Key Statistics
| Variable | Min | Max | Mean | Std | % Missing |
|---|---|---|---|---|---|

## Anomalies / Warnings
- [any issues found]

## Quick-Look Figures
![Time series](./eda_plots/timeseries.png)
*Figure 1: ...*

## Observations & Next Steps
- [key observations about the data]
- [gaps in current knowledge that need further investigation]
- [suggested next steps for analysis]
```

---

## Safety Constraints
- Phases 1–2 are strictly read-only (no files written).
- Phase 3 only creates plots in a subdirectory — never overwrites existing files.
- Phase 4 writes one report file — proposes versioned name if it exists.
- Never modify or delete data files.
- For large files, read only metadata and a small sample — do not load entire datasets into memory.
- If a file format is unrecognised, note it in the report and skip.
