---
name: 4-report
description: Create an explicitly requested scientific report or interpretation from validated research results. Use only when the user asks to explain, interpret, discuss, write up, or report completed results. Keep execution records unchanged, separate observed results from scientific interpretation, propose an outline before writing, and never run new analysis or create extra figures unless separately approved.
---

# Report Validated Research Results

Use this stage only after execution and validation are complete. This skill owns scientific explanation; `3-conduct-plan` does not.

## Inputs

Require:

- validated results or figures;
- `RUN_RECORD.json` and `VALIDATION.md` when produced by `3-conduct-plan`;
- the intended audience, format, destination, and requested interpretation scope.

If validation failed or provenance is unclear, report the limitation and stop rather than explain uncertain outputs as established findings.

## Workflow

1. Read the validated outputs and relevant methods/notes without modifying them.
2. Separate content into:
   - **Observed Results:** values, patterns, comparisons, and validation facts directly supported by artifacts;
   - **Scientific Interpretation:** mechanisms, hypotheses, limitations, and implications, clearly marked as interpretation.
3. Propose a concise outline, selected figures, output path, and explicit Non-Goals.
4. Wait for explicit outline approval before writing a report file.
5. Write only the approved report. Preserve uncertainty and distinguish evidence from inference.

Do not run a new experiment, recompute a metric, generate a figure, start a literature search, add future-work recommendations, or make publication/generalisation claims unless explicitly approved. Never modify source notes, execution records, or original instructions.

For an existing output path, propose a versioned name and wait for approval. Never fabricate values, citations, or statistical significance.
