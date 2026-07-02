---
name: 4-report
description: "Generate a research report from notes or validated results. Supports two styles: informal (internal tech report) and formal (journal-paper manuscript with numbered figures, cross-references, and bibliography). Three-phase workflow: outline → draft → export."
license: MIT
---

# Research Report Skill

## Purpose

Transform research notes, experiment outputs, or validated results into a structured research report. Two styles are supported:

- **informal** (default): Internal tech report for domain experts. Filters out code/debug noise, translates implementation jargon to domain terms. Output: `TECH_REPORT_DRAFT.md`.
- **formal**: Journal-paper-style manuscript with structured abstract, numbered figures/tables, cross-references, equations, and bibliography. Output: `PAPER_DRAFT.md`.

## When To Use

Trigger this skill when prompts include phrases like:
- "extract report from notes"
- "write a tech report"
- "turn notes into a report"
- "summarize results as a report"
- "draft technical report"
- "clean up notes into a report"
- "write up the results"
- "write a paper"
- "formal report"
- "journal paper draft"
- "write up for publication"
- "paper draft from results"
- "academic report"
- "manuscript draft"
- "prepare a paper"

## Parameters

| # | Parameter | Default | Description |
|---|-----------|---------|-------------|
| 1 | `NOTES_DIR` | Current working directory | Directory containing source research notes and figures |
| 2 | `NOTES_FILE` | Auto-detect: `TECH_REPORT_DRAFT.md`, `RESEARCH_NOTES.md`, or first `.md` in `NOTES_DIR` | Primary source document |
| 3 | `OUTPUT_FILE` | `TECH_REPORT_DRAFT.md` (informal) or `PAPER_DRAFT.md` (formal) | Output filename |
| 4 | `STYLE` | `informal` | `informal` (internal tech report) or `formal` (journal paper) |
| 5 | `JOURNAL_STYLE` | `general` | Only used when `STYLE=formal`. Hint: `general`, `agu`, `els`, `nature` — affects section naming and abstract structure |

If parameters are omitted, apply defaults. Do not ask — proceed to Phase 1.

**Style selection shortcut:** If the user says "formal report", "write a paper", "journal draft", or "manuscript", set `STYLE=formal`. Otherwise default to `informal`.

---

## Content Filtering Rules (CRITICAL — both styles)

### KEEP & EMPHASISE
- **Scientific objectives**: research questions, hypotheses, physical context.
- **Data & methodology**: datasets, methods described conceptually (not as code), mathematical formulations, constraints, assumptions.
- **Validated results**: only final, validated figures and metrics that answer the research questions.
- **Interpretation**: what the results mean scientifically, comparisons with prior work or baselines.

### REMOVE COMPLETELY
- Code snippets, script names, function names, class names.
- File paths, directory trees, repository structure.
- Intermediate/failed experiments (e.g., "Experiment 3 failed, tweaked learning rate").
- Implementation details: architecture layers, hyperparameter tuning logs, training curves.
- Bug fixes, troubleshooting logs, internal Q&A, TODO items.
- Cluster/HPC job details (SLURM, PBS, job IDs).

### TRANSLATE — Implementation terms → Domain terms
When the notes use implementation-specific jargon, translate to the equivalent domain/mathematical term. For example:
- "training data" → "calibration period" or "historical reference dataset"
- "loss function" → "cost function" or "objective function"
- "validation set" → "independent verification period"
- "overfitting" → "over-fitting to noise; reduced generalisation"

Adapt the translation table to the specific domain of the project.

---

## Document Structure

### Informal style (`STYLE=informal`)

```yaml
---
title: "Technical Report Draft"
source_notes: "<NOTES_FILE>"
notes_dir: "<NOTES_DIR>"
author: [from project config or user profile]
generated: <today's date>
status: draft — awaiting review
---
```

Sections:
1. **Title & Abstract** — 1 paragraph: the problem, the approach, and key findings.
2. **Introduction** — Context: why this work matters, what gap it fills, what prior work exists.
3. **Data & Methods** — Datasets, methodological formulation (conceptual/mathematical), key assumptions.
4. **Results** — Grouped by *research question* or *validation metric* (not chronological). Embed best final figures.
5. **Discussion** — Interpretation, limitations, comparison with baselines or prior work.
6. **Summary & Future Work** — Conclusions and next steps.

Tone: clear narrative for domain experts. First or third person. No strict figure numbering required.

### Formal style (`STYLE=formal`)

```yaml
---
title: "[Paper Title]"
authors:
  - name: [Author Name]
    affiliation: [Institution]
    email: [email]
date: YYYY-MM-DD
status: draft
journal_target: [journal name or "general"]
---
```

Sections:
1. **Abstract** — Structured: context → gap → approach → key results → significance. 150-250 words.
2. **1. Introduction** — Problem statement, literature context, research gap, objectives, paper outline.
3. **2. Data and Methods** — Numbered subsections (2.1, 2.2, ...).
4. **3. Results** — Numbered subsections by research theme.
5. **4. Discussion** — 4.1 Interpretation, 4.2 Limitations, 4.3 Comparison with Prior Work.
6. **5. Conclusions**
7. **Acknowledgements**
8. **References**
9. **Appendix A: Supplementary Material** (if needed)

### Formal-only conventions

- **Tone**: Third person, past tense for methods/results. Present tense for established facts.
- **Figures**: Numbered sequentially (Figure 1, Figure 2, ...). Full caption below. Cross-referenced in text ("As shown in Figure 3, ...").

```markdown
![Figure 1: Caption describing what is shown and key takeaway.](./figures/fig_name.png){width="90%"}
*Figure 1: Full caption. (a) Description of panel a. (b) Description of panel b.*
```

- **Tables**: Numbered sequentially (Table 1, Table 2, ...). Caption above the table. Cross-referenced.
- **Equations**: `$...$` inline, `$$...$$` display, manually numbered `(1)`, `(2)`.
- **References**: `[Author et al., Year]` in text. Full list at end. Mark missing: `[TODO: cite source for X]`.
- Precise, quantitative language — "significantly" only with statistical significance.

---

## Figure Sizing Rules (both styles)

During Phase 2, automatically detect the dimensions of every figure being embedded and set an appropriate display width. This ensures figures render at readable sizes without overflowing or appearing too small.

### Detection method
For each `.png` or `.jpg` figure, read its pixel dimensions using one of:
```bash
python3 -c "from PIL import Image; w,h = Image.open('path/to/fig.png').size; print(w,h)"
# or
file path/to/fig.png   # often reports dimensions
# or
identify path/to/fig.png  # ImageMagick
```

### Width assignment rules

| Image width (px) | Aspect ratio (w/h) | Display width | Typical use |
|---|---|---|---|
| < 600 | any | `{width="50%"}` | Small single-panel plots |
| 600-1200 | >= 1.5 (landscape) | `{width="90%"}` | Wide multi-panel or timeseries |
| 600-1200 | < 1.5 | `{width="70%"}` | Portrait or square plots |
| > 1200 | >= 1.5 (landscape) | `{width="100%"}` | Large multi-panel figures |
| > 1200 | < 1.5 | `{width="80%"}` | Large portrait/square figures |

### Embedding format
```markdown
![Caption text](./relative/path/to/figure.png){width="90%"}
```

- Always use relative paths from the output file location.
- For formal style, add the numbered caption below:
```markdown
![Figure 1: Brief alt text.](./figures/fig.png){width="90%"}
*Figure 1: Full caption describing what is shown and key takeaway.*
```
- If dimension detection fails (e.g., PDF figures, missing tools), default to `{width="90%"}`.

---

## Execution Workflow

### PHASE 1 — Synthesise & Outline (read-only — no file creation)

1. Resolve `NOTES_DIR` to an absolute path. Confirm `NOTES_FILE` exists.
2. Read `NOTES_FILE` and any companion markdown files in `NOTES_DIR`.
3. Scan for figures (`.png`, `.pdf`) and result CSVs.
4. Apply Content Filtering Rules to identify relevant material.
5. **Present a detailed outline** — do NOT write any files yet:

**For informal style:**
```
# TECH_REPORT_DRAFT — Proposed Outline

## Abstract
[1-sentence summary of what will be written]

## 1. Introduction
- [bullet: key context points to include]

## 2. Data & Methods
- [bullet: datasets, formulation points to include]

## 3. Results
### 3.1 [Research question or metric A]
- [bullet: specific validated findings]
- Figures: [list figure filenames selected, with justification]
### 3.2 [Research question or metric B]
...

## 4. Discussion
- [bullet: interpretation, limitations]

## 5. Summary & Future Work
- [bullet: conclusions and next steps]

## Figures selected
| Figure file | Section | Reason for inclusion |
|---|---|---|
| path/to/fig.png | 3.1 | Final validated result for X |

## Figures EXCLUDED (preliminary or developer-facing)
| Figure file | Reason |
|---|---|
| path/to/fig2.png | Intermediate training curve |
```

**For formal style:**
```
# PAPER_DRAFT — Proposed Outline

## Target: [journal or general]

## Abstract
[Draft abstract, 150-250 words]

## Proposed Sections
1. Introduction — [key points to cover]
2. Data and Methods
   2.1 [subsection] — [content]
   2.2 [subsection] — [content]
3. Results
   3.1 [theme] — Figures: [list]
   3.2 [theme] — Figures: [list]
4. Discussion — [key interpretation points]
5. Conclusions — [key takeaways]

## Figure Plan
| Fig # | Source file | Caption summary | Section |
|---|---|---|---|
| 1 | path/fig.png | Description | 3.1 |

## Gaps / Items Needing Input
- [e.g., "Need baseline comparison figure"]
- [e.g., "Literature references for Introduction — user to provide key papers"]
```

6. **Wait for explicit user approval** before Phase 2.

### PHASE 2 — Draft (only after approval)

1. Write the full report to `<NOTES_DIR>/<OUTPUT_FILE>`.
   - If the file already exists, propose a versioned name and wait for approval.
2. Apply all style-appropriate conventions above.
3. Mark uncertainties:
   - `[TODO: confirm value]` for uncertain numbers.
   - `[TODO: cite]` for missing references (formal only).
   - `[TODO: add figure]` for missing figures.
4. **Wait for user review** before Phase 3.

### PHASE 3 — Export (only after approval)

1. Address user feedback from Phase 2 review.
2. For formal style: final consistency check — all figures/equations numbered, cross-referenced, `[TODO]` items flagged.
3. Convert to PDF if requested and tools are available.
4. Confirm the output path to the user.

---

## Safety Constraints
- Phase 1 is strictly read-only — no files written.
- Phase 2 and Phase 3 activate only after explicit user approval.
- Never modify or delete source notes files.
- Never write outside `NOTES_DIR`.
- Never run model code or heavy computations.
- Never fabricate results, statistics, or citations — mark unknown values with `[TODO]`.
