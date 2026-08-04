---
name: 1-plan-task
description: Compile a research request into a bounded, approval-gated Task Contract. Use when asked to plan an experiment, data-processing task, figure, pipeline extension, debugging rerun, costly computation, or other multi-step scientific work. Make assumptions visible, define Non-Goals and a numeric Scope Budget, ask at most three blocking questions, and do not execute the task.
---

# Plan a Research Task

Translate the user's intended deliverable into an executable contract without expanding the research question.

Read [the Task Contract template](./references/task-contract-template.md) whenever producing or revising a contract. Use `0-explore-data` only for targeted read-only gaps that cannot be resolved from existing context.

## Classify the task

- **Level A — Quick Task:** one clear explanation, local inspection, simple command, or small code edit. State material assumptions briefly and proceed without a contract when the active platform permits execution.
- **Level B — Bounded Research Task:** one processing task, figure, experiment, established-pipeline extension, or bounded debug/rerun. Produce a concise Task Contract and require approval before substantial execution.
- **Level C — Complex or High-Risk Task:** new methodology, multiple dependent experiments, costly HPC work, a parameter sweep, a scientific-definition change, or validation/generalisation claims. Produce a full contract with explicit budgets and stop gates. Recommend `2-review-plan` only when its high-risk trigger applies.

When uncertain between levels, choose the lower level only if the uncertainty cannot increase cost, scientific consequence, or changed files; otherwise choose the higher level and explain why.

## Build the contract

1. Reuse facts already supplied by the user or discoverable through bounded read-only inspection.
2. Mark every inferred value as `ASSUMPTION`.
3. List concrete deliverables and allowed file paths. Do not add a plot, report, presentation, analysis, refactor, dependency, parameter variant, or interpretation because it may be useful.
4. Add explicit Non-Goals. Preserve the default exclusions unless the user opts in.
5. Fill the Scope Budget:
   - For Level B use the template defaults unless the request explicitly changes them.
   - For Level C provide a numeric value for every count and explicit values for compute and download fields; do not use open-ended terms.
6. Write 3–7 concrete execution steps with affected inputs/files, output, and validation.
7. Use observable success criteria. Do not use “looks reasonable” as the only criterion.
8. Ask only questions that block safe implementation or materially change deliverables, methods, cost, or files. Ask no more than three at one time. Convert non-blocking uncertainty into a visible recommended assumption.
9. End at `AWAITING_APPROVAL`. Never mark a contract `APPROVED` on the user's behalf.

Do not add hypotheses, physical mechanisms, literature validation, robustness claims, or secondary research questions unless explicitly requested.

## Approval handling

- Treat only an explicit user approval of the displayed contract as approval.
- After approval, set `Status` to `APPROVED`, record the approval timestamp, and save `TASK_CONTRACT.md` only if the platform permits writes and the user-approved destination is clear.
- If any deliverable, method, budget, allowed path, or scientific definition changes, reset the status to `AWAITING_APPROVAL` and show the revision.
- If plan-mode restrictions prevent saving, return the complete contract in chat; `3-conduct-plan` may save the approved snapshot before execution.

Validate a saved contract with:

```bash
python3 ~/.agents/skills/1-plan-task/scripts/validate_task_contract.py /path/to/TASK_CONTRACT.md
```

Substantial execution is out of scope for this skill.
