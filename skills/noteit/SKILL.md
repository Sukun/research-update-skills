---
name: noteit
description: Log a user-approved research insight or work-progress record to a project notes file. Use only when the user explicitly asks to log, save, or note an insight. Preserve supplied or already-established facts without adding scientific interpretation.
---

# Log a Research Note

Record a settled, user-approved fact, decision, assumption, or work-progress item. Do not infer a scientific explanation or turn an execution result into a conclusion.

## Input gate

Require an explicit request such as `log note`, `save this insight`, or `add this to research log`.

Before writing, identify:

- the project notes destination;
- the concise declarative claim;
- whether it is a verified fact, an assumption, an observation, or a user interpretation.

If the destination or the claim is ambiguous, ask one blocking question. Do not create a global home-directory note file unless the user explicitly provides its path.

## Default output

Write to `./docs/<PROJECT_NAME>_notes.md`, where `PROJECT_NAME` is the workspace folder name. Create `docs/` and the notes file only when the user has approved that destination.

Use this structure:

```markdown
# Research Notes — <PROJECT_NAME>

## [YYYY-MM-DD] <Declarative claim>

**Type**
Verified fact | Assumption | Observation | User interpretation

**Context**
What was examined or decided.

**Evidence / Source**
Relevant file, command, validated result, or user statement.

**Note**
A concise record of the established information. Do not add new scientific reasoning.
```

Prepend new entries below the title so the latest record is first. Preserve existing content.

## Optional global index

Write a second short entry only when the user explicitly specifies a global note path. Use an Obsidian-compatible line if requested:

```markdown
## [YYYY-MM-DD] [[PROJECT_NAME]] <Short declarative claim>
```

Never assume a particular notes application, username, or home-directory layout.

## Completion

Report the files written and classify the logged content as fact, assumption, observation, or user interpretation. Do not add a report, figure, experiment, or scientific explanation.
