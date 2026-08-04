# Task Contract

## Conclusion

[One sentence describing the intended result.]

## Relevance

[Why this task matters to the current project or user.]

## Deliverables

- [Output path or naming pattern; format; new or modified.]
- Workflow record: `RUN_RECORD.json` [destination].
- Validation record: `VALIDATION.md` [destination].

## Inputs

- Data: [path or pattern]
- Variables: [names]
- Time range: [range]
- Depth range: [range or not applicable]
- Region/grid: [selection]
- Units: [units]
- Code to reuse: [path/symbol]
- Environment/configuration: [environment and config]

Prefix every inferred value with `ASSUMPTION`.

## Non-Goals

- No scientific interpretation.
- No extra parameter sweep.
- No unrelated bug fix or refactor.
- No new dependency.
- No extra plot, report, or presentation.
- No modification of raw data.
- No changes outside Files Allowed to Change.

## Scope Budget

- Primary experiments: 1
- Sanity checks: 1
- Parameter variants: 0
- Expected figures: 0
- Extra reports or presentations: 0
- New dependencies: 0
- Unrelated refactors: 0
- Scientific interpretation: 0
- Expected files to modify: 0
- HPC run required: no
- Compute scale: local bounded
- External data download required: no

For Level C, replace every value with an explicit task-specific value; do not use “as needed”, “several”, or another open-ended value.

## Files Allowed to Change

- [Exact file or bounded directory pattern]

## Execution Plan

1. [Action; affected input/file; output; validation.]
2. [Action; affected input/file; output; validation.]
3. [Action; affected input/file; output; validation.]

## Success Criteria

- [Observable condition.]
- Raw inputs remain unchanged.
- Every output is generated from the approved configuration.
- Run and validation metadata are recorded.

## Risks

- [Material risk only.]

## Stop Conditions

- A required file is absent.
- Variables, coordinates, units, or scientific definitions conflict.
- Time, depth, region, or grid alignment cannot be resolved without changing the method.
- The requested scope, compute, downloads, outputs, dependencies, or changed files must expand.
- A destructive action is required.
- Bounded validation fails in a way that changes the approved method.

## Blocking Questions

- None.

Ask no more than three at one time. Convert non-blocking uncertainty into a visible recommended assumption.

## Approval Status

- Status: `AWAITING_APPROVAL`
- Approved by: not approved
- Approved at: not approved

