# Execution records from 3-conduct-plan

These records contain reproducibility and validation facts. They intentionally do not say
whether the result supports a scientific hypothesis.

## outputs/RUN_RECORD.json

```json
{
  "objective": "Create the approved annual-total station mean figure.",
  "contract_path": "TASK_CONTRACT.md",
  "contract_sha256": "<recorded at runtime>",
  "inputs": ["data/stations/*.csv"],
  "commands": ["python scripts/make_regional_series.py"],
  "outputs": ["outputs/regional_annual_total.png"],
  "warnings": [],
  "deviations": []
}
```

## outputs/VALIDATION.md

```markdown
# Validation

- PASS: input CSV sample contained the approved precipitation variable.
- PASS: sampled units were millimetres.
- PASS: output file exists and has labelled axes.
- PASS: raw input files were unchanged.
```

To discuss a trend, mechanism, or implication, the user must explicitly invoke
`4-report` with validated artifacts.
