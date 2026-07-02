---
name: 1-plan-task
description: "Help the user plan a research task in two stages: build a structured plan (questionnaire + template), then critically review and enrich it with concrete details (file paths, data formats, code patterns, risks)."
license: MIT
---

Help the user plan a research task in two stages:

**Stage 1 — Build:** create an empty plan template if user hasn't provided one. 
if user has provided some context, pre-fill what you can infer. Then
Guide the user through a structured questionnaire to capture all necessary planning information. Pre-fill what you can from context provided, ask for missing critical fields, and write the completed plan to `<work_path>/doc/*.md`.

**Stage 2 — critical thinking:** do a logical examination of the raw plan critically. ask for questions to clarify any vague or incomplete sections. 

**Stage 3 — Enrich:**
Fill in concrete details the user may not know yet: actual file paths, data formats, variable names, code patterns to reuse, and likely risks. Update the plan file in place.
if user accepts the plan, save it to the same file.

---

## Recommended settings

| Setting | Value | Why |
|---------|-------|-----|
| **Mode** | Plan mode (default) | This skill is read-only exploration + writing a plan document. Plan mode prevents accidental edits elsewhere. |
| **Model** | Sonnet (default) | Template filling and data inspection don't need Opus-level reasoning. Save Opus for execution (skill-3). |

**Typical workflow:** skill-1 (plan) → optionally skill-2 (review) → skill-3 (conduct). Skill-3 will detect the enrichment notes this skill produces and skip redundant data exploration.


## When To Use

Trigger this skill when prompts include phrases like:
- "plan task from readme"
- "make a plan"
- "plan a task"

---

## Stage 1 — Build

### How to run
1. If the user has provided context, pre-fill what you can infer.
2. Present the template below with any pre-filled fields.
3. Ask for missing critical fields: `purpose`, `data sources`, `work path`.
4. Once complete, write the plan to `<work_path>/doc/readme.md`.

### Template

```
purpose:
  [One or two sentences: what is the goal? What question are you answering or problem solving?]

background:
  [Why is this being done? What motivates it? Link to prior findings, papers, or discussions.]

reference work:
  [Path(s) to existing code or analyses to build on. Note what to reuse and what to adapt.]

research scope:
  - [Geographic / temporal / thematic focus — be specific to keep the task manageable.]
  - [Explicit exclusions or simplifying assumptions.]

research questions:
  - [Primary question]
  - [Secondary questions, comparisons, or sub-goals]

hypotheses / expected outcomes:
  - [What do you expect to find, and why? Even rough expectations help guide analysis choices.]

methodology / approach:
  - [High-level steps: data loading → processing → analysis → visualisation]
  - [Key methods, algorithms, or statistical approaches]
  - [How will results be validated or checked?]

data sources:
  - [Dataset name, path, format, resolution, time period]
  - [Known data quality issues, gaps, or preprocessing required]

work path:
  [Absolute path where code, outputs, and notes will be stored. Intended folder structure.]

deliverables:
  - [Figures, tables, CSV exports, report sections expected as output]

success criteria:
  - code runs without errors

risks / dependencies:
  - [What could block progress? Missing data, compute limits, unclear methods, external dependencies?]

notes:
  [Any other context, open questions, or reminders.]
```

---

## Stage 3 — Enrich

### How to run
1. Read the plan file (`<work_path>/doc/readme.md`) or the file the user points to.
2. Explore the project using `~/.claude/skills/skill-0-explore-data/SKILL.md`:
   - Scan the reference work directory for reusable code patterns and pipeline structure.
   - Inspect data source paths: list files, check formats, read headers/metadata.
   - Check existing documentation and notes for relevant methodology details.
3. For each plan section, replace placeholders and vague statements with concrete findings:
   - `data sources` → actual file names, variable names, units, time coverage, missing-value flags
   - `reference work` → specific scripts and functions to reuse, with file paths
   - `methodology / approach` → concrete steps grounded in the reference code structure
   - `risks / dependencies` → real issues found during exploration (format mismatches, gaps, etc.)
   - `hypotheses` → refine based on any preliminary data inspection
4. Add a new section at the bottom:

```
## enrichment notes  [date]
  - Files found at data path: [list]
  - Reference scripts identified for reuse: [list]
  - Data issues discovered: [list]
  - Open questions requiring user input: [list]
```

5. Save the updated plan back to the same file.

---

## Example — Stage 1 output (CGR intra-annual relationship study)

```
purpose:
  Investigate intra-annual correlations between CGR and VOD / 2 m temperature / NDVI
  datasets from Bathen, as an extension of the intra-annual CGR–TWS correlation study.

background:
  A previous analysis (cgr-tws_monthly_analysis) found interesting seasonal correlation
  patterns between CGR and TWS in the Northern Hemisphere. This task extends that work
  to three additional Earth-observation variables to test whether the CGR seasonal signal
  is driven primarily by water availability or also by vegetation state and temperature.

reference work:
  /path/to/project/cgr-tws_monthly_analysis/
  — especially ./doc for methodology notes.
  Reuse code structure and processing pipeline; adapt only for the new variables.

research scope:
  - Northern Hemisphere only (consistent with reference work, keeps results comparable).
  - Same temporal coverage as the TWS analysis.
  - Exclude tropics and high-latitude regions flagged as data-poor in the reference work.

research questions:
  - What are the intra-annual correlation patterns between CGR and VOD / 2 m T / NDVI?
  - How do these patterns compare with the CGR–TWS patterns?
  - What physical or ecological mechanisms explain observed differences or similarities?

hypotheses / expected outcomes:
  - Temperature likely shows the strongest spring–autumn signal in mid-latitudes.
  - VOD and NDVI may track TWS in water-limited regions but diverge in energy-limited ones.

methodology / approach:
  - Load each variable; align to the same monthly grid and time axis as CGR.
  - Apply the same seasonal decomposition and intra-annual correlation method as reference work.
  - Compare correlation maps side-by-side with the TWS result.
  - Validate against published literature values where available.

data sources:
  - Bathen datasets: VOD, 2 m temperature, NDVI
    Path: /path/to/project/cgr_intra-annual_relationship/data_BathenH-4-2026
  - Check documentation for differences in units, variable definitions, or missing-value flags.

work path:
  /path/to/project/cgr_intra-annual_relationship/
  Folder structure: code/, outputs/, doc/ (mirrors reference work layout).

deliverables:
  - Correlation maps for each variable (NH, seasonal breakdown).
  - Comparison figure: CGR–TWS vs CGR–VOD / temperature / NDVI.
  - Short methods note in doc/ summarising deviations from the reference workflow.

success criteria:
  - All three variables processed through the full pipeline without errors.
  - Correlation maps visually consistent with expected seasonal patterns.
  - At least one comparison figure ready for discussion with collaborators.

risks / dependencies:
  - Data format differences between Bathen VOD/NDVI and TWS files may need extra preprocessing.
  - Compute time for full NH spatial correlation could be high — test on a subregion first.

notes:
  Keep changes to the reference codebase minimal to maintain reproducibility.
```
