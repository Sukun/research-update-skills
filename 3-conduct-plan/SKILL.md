---
name: 3-conduct-plan
description: Execute an explicitly approved research Task Contract without changing its scope. Use when asked to conduct or implement a bounded Level B or Level C research task from TASK_CONTRACT.md. Validate approval, show an execution snapshot, run a minimal bounded validation before any full run, record reproducibility facts, and stop on scope or method changes. Never perform scientific interpretation.
---

# Conduct an Approved Research Task

Execute the contract as written. This skill is an executor, not a planner, reviewer, report writer, or scientific interpreter.

## Entry gate

Require a saved or user-approved `TASK_CONTRACT.md` for Level B and Level C tasks. Validate a saved contract before any implementation:

```bash
python3 ~/.agents/skills/1-plan-task/scripts/validate_task_contract.py \
  /path/to/TASK_CONTRACT.md --require-approved
```

Stop if validation fails, approval is absent, allowed paths are unclear, or the contract omits `RUN_RECORD.json` and `VALIDATION.md` from its workflow records.

Before changing anything, display a compact execution snapshot:

- goal;
- deliverables;
- Scope Budget;
- files allowed to change;
- main risk;
- Task Contract SHA-256.

## Hard boundaries

- Execute only approved deliverables and validation.
- Do not fix an unrelated bug, even when the fix appears obvious.
- Do not generalise, refactor, clean up, rename, migrate, or add a dependency unless named in the contract.
- Do not add analyses, parameter variants, figures, tables, reports, presentations, or downloads.
- Do not change scientific definitions, units, masks, periods, grids, metrics, or output naming.
- Do not overwrite the original instruction file or reference work.
- Do not delete or overwrite existing outputs without explicit approval in the contract.
- Do not interpret results, decide whether a hypothesis is supported, prefer one result, add mechanisms, or write conclusions. If interpretation was requested, finish execution first and route it to a separate explicit `4-report` stage.

## Execute

1. Resolve the approved inputs and allowed paths. Record the contract hash, repository commit, environment, and command plan.
2. Run the smallest contract-approved validation subset first.
3. Check the subset against observable criteria such as exit status, dimensions, coordinates, units, finite-value regions, file naming, and raw-input preservation.
4. Run the full approved workload only after the bounded validation passes and only when its scale matches the Scope Budget.
5. Verify every declared output. Do not substitute or add outputs.
6. Write the workflow records declared by the contract:
   - `RUN_RECORD.json`: objective, contract path/hash, timestamp, Git commit, environment, dependency versions when relevant, inputs, selections, parameters, exact commands, random seed, HPC job ID, outputs, warnings, failures, and deviations;
   - `VALIDATION.md`: observable checks and `PASS`/`FAIL` outcomes only.
7. Report delivered files, validation status, deviations, and anything not run. Keep scientific meaning out of these records and the completion message.

## Stop and return control

Stop before proceeding when:

- a required file, variable, unit, coordinate, or dependency conflicts with the contract;
- validation fails in a way that changes the method;
- a new output, bug fix, refactor, parameter variant, download, destructive action, or expensive run is needed;
- the contract changed after approval or its hash no longer matches the execution snapshot;
- execution would leave the allowed paths or Scope Budget.

Describe the blocker and the smallest contract revision needed. Do not silently repair or broaden the task.
