# Task Contract

## Conclusion

Create one reproducible regional annual-total time-series figure from the supplied station
files, subject to a bounded validation.

## Relevance

The figure is a bounded input to a later research discussion; it is not itself a trend
claim.

## Deliverables

- `scripts/make_regional_series.py` — reproducible processing script.
- `outputs/regional_annual_total.png` — one annual-total time series.
- Workflow record: `outputs/RUN_RECORD.json`.
- Validation record: `outputs/VALIDATION.md`.

## Inputs

- Data: `data/stations/*.csv`.
- Variables: monthly precipitation total and station identifier.
- Time range: all complete years present in the input files.
- Depth range: not applicable.
- Region/grid: all supplied stations, unweighted mean.
- Units: millimetres; stop if units are absent or inconsistent.
- Code to reuse: `scripts/io_helpers.py`.
- Environment/configuration: existing project Python environment.

## Non-Goals

- No scientific interpretation or trend significance test.
- No parameter variants, map, report, slides, new dependency, or unrelated refactor.
- No raw-data modification or changes outside the allowed files.

## Scope Budget

- Primary experiments: 1
- Sanity checks: 1
- Parameter variants: 0
- Expected figures: 1
- Extra reports or presentations: 0
- New dependencies: 0
- Unrelated refactors: 0
- Scientific interpretation: 0
- Expected files to modify: 4
- HPC run required: no
- Compute scale: local bounded
- External data download required: no

## Files Allowed to Change

- `scripts/make_regional_series.py`
- `outputs/regional_annual_total.png`
- `outputs/RUN_RECORD.json`
- `outputs/VALIDATION.md`

## Execution Plan

1. Inspect CSV headers and a small sample; stop if the approved variable or units are absent.
2. Aggregate complete station-years using the existing missing-month convention and run one bounded sanity check.
3. Write the approved figure and workflow records only if the sanity check passes.

## Success Criteria

- The script exits successfully on the approved inputs.
- The output has one annual series with labelled units.
- Raw inputs remain unchanged.
- Every output is generated from the approved configuration.
- Run and validation metadata are recorded.

## Risks

- Inconsistent units or missing-month conventions can invalidate the aggregation.

## Stop Conditions

- A required file, variable, unit, or shared convention is absent or inconsistent.
- The requested scope, output count, compute, dependencies, or changed files must expand.
- Bounded validation fails in a way that changes the approved method.

## Blocking Questions

- None.

## Approval Status

- Status: `APPROVED`
- Approved by: example user
- Approved at: 2026-08-04T12:00:00Z
