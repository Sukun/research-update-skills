---
name: 2-review-plan
description: "Review a research plan or methodology document with a structured audit workflow. Checks metric validity, baseline fairness, validation design, and feasibility. Produces a verdict (REJECT / CONDITIONALLY_ACCEPT / ACCEPT) and an executable task list."
license: MIT
---

# Research Plan Review Skill

## Purpose
Audit a research plan, experimental design, or methodology document and decide whether it is executable. Domain-agnostic — works for any quantitative research project.

Checks:
- Metric design and potential artifacts
- Baseline fairness and benchmark completeness
- Validation strategy (in-sample vs out-of-sample, independent targets)
- Feasibility and reproducibility
- Failure modes and falsification conditions

## Recommended settings

| Setting | Value | Why |
|---------|-------|-----|
| **Mode** | Plan mode (default) | This skill is read-only audit. Plan mode prevents accidental edits. |
| **Model** | Sonnet (default) | Structured checklist evaluation. Opus not required. |

## How To Invoke

```
/2-review-plan <path-to-plan.md>
```

## When To Skip
Skip this skill for routine tasks where the methodology is well-established:
- Extending an existing pipeline to new variables (same methods, new data)
- Replicating a prior analysis with minor parameter changes
- Tasks where skill-1 enrichment already validated data paths and feasibility

Use this skill when:
- The methodology is novel or untested
- Success metrics could be misleading (post-processing artifacts, metric leakage)
- The task involves training/validation splits or out-of-sample claims
- Significant compute investment is at stake

## Parameters

| # | Parameter | Default | Description |
|---|-----------|---------|-------------|
| 1 | `PLAN_FILE` | User-provided or auto-detected `.md` in current directory | The plan/methodology document to review |
| 2 | `REFERENCE_DIR` | Extracted from plan content | Directory with existing code, notes, or prior results for context |

## Scope

**In scope:**
- Research plan critique and structured audit
- Metric design and validity checks
- Baseline fairness and benchmarking completeness
- Experiment phase readiness and execution plan
- Revising the plan into an executable, code-aligned version before implementation begins

**Out of scope:**
- Writing production code
- Running experiments or training
- Fabricating results not present in provided documents

## Workflow

### PHASE 0 — Context Gathering (read-only)

1. Read the plan document.
2. If a `REFERENCE_DIR` is provided or referenced, read relevant code and notes to understand the current state.
3. Check for existing experiment notes, research notes, or CLAUDE.md for project conventions.

### PHASE 1 — Structured Audit

Apply the Mandatory Audit Checklist (below). Present findings using the Output Contract format.

### PHASE 2 — Plan Revision (only if not REJECT_FOR_NOW)

After the user addresses blocking issues:
1. Revise the plan into a clean, executable version.
2. Update relevant project documentation (experiment notes, research notes) if they exist.

---

## Core Review Rules

1. Do not approve by default.
2. Identify blocking issues first.
3. Separate mandatory fixes from optional improvements.
4. Baseline comparisons must be fair — same data, same periods, same pre-processing.
5. Check for metric leakage or artifacts introduced by post-processing steps.
6. Require out-of-sample or independent validation design before declaring success.
7. Only produce an executable task list after the document passes the decision gate.
8. Ask for clarification if any part of the plan is ambiguous or under-specified.

---

## Mandatory Audit Checklist

### A. Metric Integrity
Verify:
- Metrics are clearly defined with formulas or unambiguous references.
- Metrics potentially inflated by post-processing are identified.
- Raw (pre-processing) and final (post-processing) metrics are separated where applicable.
- The document states which conclusions depend on which metric variant.

Flag as blocker if:
- Success claims rely solely on metrics that could be artifacts of post-processing.

### B. Validation Strategy
Verify:
- Training / validation / test splits are explicit and non-overlapping.
- At least one independent or quasi-independent validation target exists.
- Out-of-distribution or out-of-sample robustness is evaluated (not only in-sample skill).
- Criteria distinguish different failure modes (e.g., bias vs variance, systematic vs random).

Flag as blocker if:
- Plan lacks out-of-sample success criteria but claims generalisability.

### C. Baseline Fairness
Verify:
- At least one established baseline method is included.
- Baseline and proposed method use identical data, periods, and pre-processing.
- Comparison is on the same metrics under the same conditions.

Flag as blocker if:
- Baseline comparison is absent or uses different conditions.

### D. Metric Adequacy
Verify:
- Success criteria include both skill metrics and robustness metrics.
- Failure modes and falsification conditions are explicit.
- Metrics collectively answer the stated research question.

Flag as blocker if:
- All metrics can be passed while the core research question remains unanswered.

### E. Feasibility and Reproducibility
Verify:
- Data periods, masks, splits, and processing logic are explicit.
- Dependency order among phases/tasks is clear.
- Acceptance criteria are testable and unambiguous.
- Computational requirements are realistic for available resources.

Flag as blocker if:
- Plan cannot be executed deterministically from written instructions.

---

## Decision Gate

Classify exactly one:
- **REJECT_FOR_NOW**: blocking issues exist.
- **CONDITIONALLY_ACCEPT**: no blockers, but revisions required.
- **ACCEPT**: execution-ready.

---

## Output Contract

### 1) Verdict
- Verdict: REJECT_FOR_NOW | CONDITIONALLY_ACCEPT | ACCEPT
- Confidence: High | Medium | Low
- One-sentence rationale

### 2) Essential Fixes (Blocking)

| ID | Severity | Issue | Why It Matters | Required Change | Evidence Needed |
|---|---|---|---|---|---|

### 3) Revision Suggestions (Non-blocking)
Numbered list, concise and actionable.

### 4) Domain-Specific Audit Summary
Include explicit lines for each relevant domain check:
- Baseline fairness: PASS/FAIL + reason
- Metric integrity: PASS/FAIL + reason
- Validation strategy: PASS/FAIL + reason

### 5) Executable Plan / Task List (only if not REJECT_FOR_NOW)

| Task ID | Task | Dependency | Deliverable | Acceptance Criteria | Priority |
|---|---|---|---|---|---|

Rules:
- Tasks must be ordered and executable.
- Include at least one metric-audit task, one validation task, one documentation task.
- Include stop criteria for each phase.

### 6) Open Questions
List unknowns that could change conclusions.

---

## Safety Constraints
- Phase 0 and Phase 1 are strictly read-only.
- Phase 2 only activates after user approval.
- Never fabricate results or metrics.
- Never modify source files without explicit approval.
