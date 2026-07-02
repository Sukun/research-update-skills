---
name: research-task-conductor
description: "End-to-end research task conductor: reads a rough instruction document (default readme.md in the current directory), plans the implementation, executes it, and reorganises the instruction into a clear sectioned research note with date stamp. Invoke directly: /3-conduct-plan <path-to-readme.md>."
license: MIT
---

# Research Task Conductor Skill

## Purpose

Take a rough, unstructured instruction document — typically a `readme.md` dropped into a new working directory — and drive it through the full research cycle: **plan → implement → document**. The final deliverable is both the completed outputs (figures, presentations, data products) and a clean, sectioned markdown research note that replaces the original rough instructions.

Complements but does not replace `organize-notes`, which compiles notes across an entire
project — this skill operates on a **single task directory**.

## Recommended settings

| Setting | Value | Why |
|---------|-------|-----|
| **Mode** | Normal (not plan mode) | This skill writes code and runs scripts. Plan mode would block execution. |
| **Model** | Opus | Multi-file code generation, debugging, and adapting reference pipelines benefit from stronger reasoning. |
| **Effort** | High | The implementation and debugging phases need full attention. |

**Typical workflow:** Run after skill-1 (plan-task) has produced an enriched readme.md. If the readme contains `## enrichment notes`, Phase 0 will be fast — it reuses those findings instead of re-exploring.

## How To Invoke

```
/3-conduct-plan <path-to-readme.md>
```

## Parameters

| # | Parameter | Default | Description |
|---|-----------|---------|-------------|
| 1 | `INSTRUCTION_FILE` | `readme.md` in the user's current working directory | The rough instruction document |
| 2 | `REFERENCE_DIR` | Extracted from instruction file content | Directory containing reference scripts/outputs to follow |

If the instruction file references prior work or a reference directory, resolve that path and read the reference scripts to understand the target style and approach.

## Scope

**In scope:**
- Reading and parsing the instruction document
- Identifying reference work (prior scripts, data paths, plot styles)
- Planning the implementation (scripts to write, data to process, outputs to produce)
- Writing and running scripts
- Generating all specified outputs (figures, presentations, data products)
- Reorganising the instruction document into a clean research note

**Out of scope:**
- Modifying files outside the task directory without explicit approval
- Running long training jobs (inference, plotting, and post-processing only)
- Deleting or overwriting the user's reference work

---

## Workflow

### PHASE 0 — Intake (read-only)

1. **Locate the instruction file**: resolve the path from the user message, or default to `readme.md` in the current directory. Confirm it exists.
2. **Read the instruction file**: extract task description, reference work paths, data sources, requirements, and any configuration details.
3. **Check for prior enrichment**: if the instruction file contains an `## enrichment notes` section (produced by skill-1-plan-task Stage 2), treat it as pre-validated context:
   - Use the listed data files, reference scripts, and discovered issues directly — **do not re-explore** data paths or reference directories that are already documented there.
   - Only read reference scripts that you need to understand for implementation (code patterns, plot styles), not to re-discover their existence.
   - Skip to Phase 1 with a lighter confirmation step.
4. **If no enrichment notes exist** (raw/unenriched instruction file), perform full exploration:
   - **Read reference work**: if the instructions reference prior scripts or directories, read those scripts fully to understand data loading patterns, plot style, colormaps, layout conventions, output naming conventions, and presentation format.
   - **Inspect new data**: verify the new data source exists, check file naming patterns, variable structure, and year/time coverage.

### PHASE 1 — Plan (present to user before executing)

**If enrichment notes exist (skill-1 already ran):**
1. **Brief confirmation**: state the task, list the deliverables, and note any implementation decisions not already in the enriched plan (e.g., script names, function signatures).
2. **Present for approval** — this should be concise since the user already approved the enriched plan.

**If no enrichment notes (standalone invocation):**
1. **Summarise understanding**: state what the task is, what data is involved, and what outputs are expected.
2. **List deliverables**: scripts to write, figures to generate, presentations to build.
3. **Identify key differences** from reference work (data paths, filename patterns, year ranges, variable handling, bug fixes).
4. **Present the plan** to the user and wait for approval before proceeding.

### PHASE 2 — Implement

1. **Write scripts** based on the reference work, incorporating all changes identified in Phase 1.
   - Fix known bugs from reference code (e.g., Path vs string issues).
   - Generalise where the instructions call for it (e.g., loop over variables instead of manual commenting).
   - Preserve plot style, colormap choices, layout, and naming conventions exactly unless the instructions say otherwise.

2. **Test incrementally**: run with a minimal subset first (e.g., single year) to verify outputs before the full run.

3. **Execute full run**: generate all outputs. Verify file counts and spot-check naming.

4. **Generate presentations or secondary outputs** as specified.

### PHASE 3 — Document

Reorganise the original instruction file into a clean, sectioned research note. The output overwrites the instruction file (or writes to a user-specified path).

**Document structure:**

```markdown
# [Descriptive Title]

(last edit MM-YYYY)

[One-sentence summary of what this work is and its relationship to prior work.]

## Configuration
- Bullet list of key parameters: ensemble size, period, variables, grid, depth levels

## Data and Products
- Input data paths, file naming patterns, file sizes
- Reference data (if comparing with prior work)
- Mesh/mask files and auxiliary data
- Related resources (documentation PDFs, static fields, tuning files)

## [Domain-Specific Context Section] (if applicable)
- E.g., ensemble design, perturbation sources, model configuration details
- Preserve all technical detail from the original instructions

## Methodology
- Script names and what each does
- Plot types and styles (colormaps, layout, percentile thresholds)
- Any additional analysis (time series, statistics)

## Outputs
- List of all generated outputs with naming conventions
- Presentation file with slide count and ordering
- Output directory structure

## Findings
- Key results with embedded figures where appropriate
- Use: <img src="path" width="60%" alt="description">
- Physical interpretation of results
- Comparisons with reference/prior work

## Open Questions
- Unresolved technical questions from the original instructions
- New questions raised by the findings
- Items needing confirmation (keep uncertainty explicit)
```

**Documentation rules:**
- Preserve ALL technical information from the original instructions — do not drop content
- Fix grammar and spelling without changing scientific meaning
- Keep uncertainty statements explicit (e.g., "possibly", "needs confirmation")
- Embed figures at 60% width with descriptive alt text
- Add a date stamp `(last edit MM-YYYY)` directly under the title
- Bullet points preferred over prose for scannability
- No table of contents

---

## Safety Constraints

1. Phase 0 and Phase 1 are strictly read-only — no files written.
2. Phase 2 activates only after the user approves the plan from Phase 1.
3. Always test with a minimal subset before running the full job.
4. Never modify reference work directories.
5. Never delete existing outputs without user confirmation.
6. On script errors, diagnose before retrying — do not blindly re-run.
7. When reorganising the instruction document, preserve all original technical content. If in doubt about whether something is important, keep it.
