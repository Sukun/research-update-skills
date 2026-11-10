---
name: 00-init-project-structure
description: Initialize or lightly organize documentation for an existing project, including research outlines, overviews, and roadmaps. Preserve numeric document naming, reuse existing notes, and improve navigation and evidence traceability without duplicating information or adding scientific interpretation.
---

# Initialize and Organize a Project

## Purpose

Help a user navigate and maintain a personal coding or research project with minimal documentation overhead.

Apply this skill to `<project_root>/`, using the user-supplied path. If the path is not specified, use the current workspace only when its project identity is clear.

The goal is to make existing information easy to find, not to build a documentation management system.

Core principles:

1. Reuse existing documents before creating new ones.
2. Organize by project area, such as research topic, component, or workflow.
3. Use numeric prefixes for new project documentation.
4. Keep one authoritative location for each detailed record.
5. Use a lightweight roadmap to navigate existing work.
6. Avoid unnecessary processes, duplicate summaries, and file migrations.

## 1. Inspect Before Organizing

Before changing project documentation:

- Read applicable project instructions (`CLAUDE.md`, `AGENTS.md`, etc.).
- Inspect the existing directory structure and documentation.
- Identify current README files, notes, reports, task lists, figures, and run records.
- Determine which files already explain each project area.
- Identify missing navigation and obvious duplication.

Use existing documentation first. Do not scan large raw datasets, execute programs, or run experiments merely to organize documents.

For a new organization request, briefly propose which files to create or update and ask for approval.

For routine maintenance already authorized by the user, proceed directly.

Do not treat organization as permission for a project-wide migration.

## 2. Documentation Structure

Organize documentation by project area.

An area may represent:

- A research topic
- A software component
- A feature or service
- An experiment series
- A workflow or subsystem

Each area should have an easy-to-find overview.

Reuse an existing README, topic record, or research-notes document whenever possible.

Do not create another document solely to enforce a preferred naming or folder structure.

Small projects may need only a README.

Larger projects may benefit from one roadmap linking their existing documents.

## 3. Numeric Document Naming

Use numeric prefixes for new project-owned narrative documents.

Naming convention:

- Two-digit chapter numbers: `00`, `01`, `02`.
- Nested chapters: `02.01`, `02.02`, `02.02.01`.
- Descriptive English names with initial capitals.
- Separate words with underscores.
- Preserve established acronyms and technical names.

Examples:

    00_Project_Overview.md
    01_Project_Roadmap.md
    02_Methodology.md
    03_Experiments/
        03.00_Overview.md
        03.01_Experiment_A.md
        03.02_Experiment_B.md
    04_Results/
        04.00_Overview.md
        04.01_Validation.md

Numbers describe reading order and hierarchy, not dates or completion status.

Use `.00` for an overview when a numbered chapter has several documents.

Keep numbers stable. Gaps are acceptable.

For dated deliverables, append `YYYY-MM-DD` when useful.

Do not rename existing files merely to enforce this convention.

Preserve filenames required by tools or conventions, including:

- `README.md`
- `SKILL.md`
- `AGENTS.md`
- Existing contract and configuration filenames
- Source code, data, logs, and machine-generated files

Apply numeric naming primarily to new narrative documents or explicitly approved reorganizations.

## 4. Lightweight Project Roadmap

For a project with many existing notes, prefer one short roadmap over additional summaries or new documentation layers.

Default name:

    docs/01_Project_Roadmap.md

If a suitable project index or roadmap already exists, update it instead of creating another.

The roadmap should help the user understand the project in a few minutes.

Recommended structure:

    # Project Roadmap

    Last reviewed: YYYY-MM-DD

    ## Quick View

    - Goal and key question:
    - Current progress:
    - Main documented finding, if available: [Evidence](...)
    - Blocker or open decision:
    - Next action: [Existing task or plan](...)

    ## Research / Work Areas

    | Area | Current Stage | Main Records | Key Figures | Next |
    |------|---------------|--------------|-------------|------|
    | Topic A | Completed | [Notes](...) | [Figure](...) | — |
    | Topic B | In progress | [Notes](...) | [Figure](...) | [Task](...) |
    | Topic C | Planned | [Plan](...) | — | [Task](...) |

    ## Current Focus

    - The most important active task.
    - The most important unresolved problem.
    - The next practical action.

Keep the roadmap concise, preferably one screen or approximately one page.

The roadmap is primarily a navigation page.

Do not copy detailed methods, experiment results, figures, or long task lists into it.

Use links to existing records.

A short status or finding may be included when needed to orient the reader, but detailed information remains in its original document.

Do not create a separate STATUS, FINDINGS, or TODO document simply because the roadmap exists.

## 5. Area Overview

Reuse the existing area overview format when it is useful.

For a new overview, prefer:

    # Area Title

    Last updated: YYYY-MM-DD

    ## Quick View

    - Purpose:
    - Key question:
    - Current progress:
    - Main documented finding or outcome: [Evidence](...)
    - Open problem:
    - Next step:

    ## Details and Evidence

    Links to relevant methods, figures, results, and records.

    ## History

    - YYYY-MM-DD — Important result or decision. [Source](...)

Keep the first section short.

The supporting detail may be extensive when the subject requires it, but do not duplicate material already maintained elsewhere.

An existing L1/L2/L3 research topic record can serve as the area overview. Do not replace it with another format.

### Research Overview Content Guidelines

Apply these guidelines when creating or revising research outlines, roadmaps, summaries, project overviews, or Markdown knowledge bases within the authorized scope. Existing names such as `outline.md` and `roadmap.md` do not require renaming.

**Structure for quick reading**

- Lead with a short Quick View: research goal, key questions, current progress, major documented findings, and blockers or open decisions. Include only fields supported by available records; do not invent findings to fill a template.
- Put supporting detail after the overview. Preserve useful detail and scientific meaning rather than shortening solely to meet a length target.
- Use `#` for the document, `##` for topics, and `###` for subtopics in new ordinary Markdown overviews. Preserve useful established formats, including L1/L2/L3 topic records.
- Keep paragraphs and bullets focused on one main idea; avoid deep nesting. Use bold selectively for important findings, decisions, risks, and actions.
- Add a compact plain-text concept map when relationships would otherwise be difficult to follow. It should clarify documented relationships, not imply untested causal links. For example:

    Research question
    ├── Data → Method → Diagnostic
    ├── Validation → Supporting records
    └── Open question → Next action

**Evidence and uncertainty**

Use consistent evidence labels where they clarify the status of a claim:

| Label | Meaning |
|-------|---------|
| Confirmed | Supported by verified evidence within the stated conditions; identify the supporting validation record. |
| Reported | Described in existing records; not independently verified in this documentation task. |
| Hypothesis | Proposed but untested explanation or prediction. |
| Open | Unresolved question or decision. |
| Needs verification | A specific claim, source, or reference still requires checking. |

- Preserve established labels when their meanings are clear. Keep evidence labels separate from progress states such as planned, running, or completed.
- Distinguish observations, recorded interpretations, assumptions, and next actions. Attribute existing interpretations to their source; do not add new scientific interpretation.
- A completed experiment is not automatically a validated finding. An accessible file or working link does not establish scientific validity.
- Preserve uncertainty, contradictory evidence, experimental conditions, and validation limits. Mark historical or superseded results clearly when the records establish that status.

**Topic structure and terminology**

For each topic, include whichever elements help the reader; they need not become six separate headings:

    Research Topic
    ├── Purpose      — What question does it address?
    ├── Method       — How is it investigated?
    ├── Finding      — What has been observed, under which conditions?
    ├── Limitation   — What remains uncertain?
    ├── Evidence     — Where are the supporting records?
    └── Next Action  — What should happen next?

- Briefly explain technical concepts at first use; add a compact glossary only for frequently reused terms that need it.
- Use consistent mathematical notation, preferably LaTeX when supported. Define variables, units, and indices when introduced. Qualify symbols used for different concepts.
- Do not infer missing definitions or units. Flag them explicitly and replace ambiguous placeholders such as `Method (?)` with a specific unresolved question.

**Links, results, and figures**

- Give important scientific claims descriptive links to their supporting records, preferably to a specific section. Convert navigation labels such as `[Project Goal]` into working links when the destination is known; otherwise mark the missing destination explicitly.
- Use reference-style links when repeated citations would clutter the text. Keep one authoritative detailed record and link to it.
- Check links and anchors introduced or changed by the task where the environment permits. Report inaccessible destinations or version conflicts; do not expand this into an unrequested project-wide audit.
- Lead result entries with the documented finding and its uncertainty, rather than the figure filename. Separate experimental configuration, observation, and recorded interpretation into distinct statements.
- Include only essential existing figures in an overview; link to detailed figure inventories, experiment logs, and reports. Do not generate figures or new analysis.

**Outline versus roadmap**

| Aspect | Research outline | Research roadmap |
|--------|------------------|------------------|
| Main question | What is being studied? | What should happen next? |
| Organization | Scientific concepts and relationships | Phases, priorities, and dependencies |
| Emphasis | Questions, methods, documented findings, and evidence | Tasks, progress, and documented decision gates |
| Navigation | Topics → detailed records | Milestones → existing tasks or plans |
| Maintenance | When research understanding changes | When plans or progress change |

An outline may contain detailed topic structure; a roadmap should stay a short navigation page. Link to existing owners, deadlines, dependencies, and decision criteria when recorded and useful; do not invent commitments. Listing a next action does not authorize its execution.

Use **Quick View → Concept Map (when useful) → Structured Topics → Evidence and Open Questions** as a flexible reading order. Keep key findings in the Quick View or their owning topic rather than repeating them in another mandatory section.

## 6. Tasks, Decisions, and Historical Records

Use the project's existing task and decision records.

- Open tasks stay in the existing TODO, STATUS, issue tracker, or equivalent.
- Completed work can be recorded briefly in the area's history.
- Detailed decisions remain in their original decision records.
- Execution logs and validation results remain with their owning workspace.

The roadmap may link these records, but must not create another independently maintained task list.

Preserve personal todo items and historical records.

Use task IDs only when they help cross-reference work.

Do not introduce a new tracking system unless explicitly requested.

## 7. Figures, Results, and Existing Notes

Link existing figures and research outputs instead of copying them.

When organizing research material:

- Identify the relevant figure or result.
- Link to its original location.
- Keep its existing numbering and filename.
- Preserve the original experiment conditions and source information.
- Do not silently replace an older scientific conclusion with a new interpretation.

For figures actively selected for the roadmap or a new overview, check that the referenced path is accessible when the working environment permits.

If a figure or result clearly conflicts with newer documented evidence, add a brief note explaining the issue.

Do not perform a project-wide freshness audit unless explicitly requested.

Do not generate new figures, rerun experiments, or recalculate results as part of documentation organization.

Missing, inaccessible, and Git-untracked files should not be treated as equivalent.

## 8. Updating Existing Documentation

When new work is completed:

1. Update the existing document that owns the information.
2. Add a short dated history entry if useful.
3. Update the roadmap only if the area's overall status, key links, or next action changes.

Do not update every parent document for minor changes.

Avoid copying the same finding into several files.

If information appears in several places, prefer keeping one detailed version and replacing unnecessary duplicates with links, when that change is authorized.

Use substantive update dates rather than filesystem modification times.

## 9. Workspace Boundaries

Respect the project's existing repository and workspace layout.

Do not assume any required directory structure such as `src/`, `tests/`, `data/`, or `experiments/`.

Do not move source code, datasets, configurations, generated outputs, or execution records as part of routine documentation organization.

Do not create empty directories to match an example.

Do not rewrite historical run records.

For a larger authorized reorganization, present a concise old-path to new-path mapping before moving files.

Keep unrelated files unchanged.


## 10. Completion and Reporting

After an authorized organization task:

- Report which files were created or updated.
- Identify the main navigation improvements.
- Mention any unresolved or broken references.
- Note any decisions the user still needs to make.

Keep the report short.

Do not create a separate organization report unless explicitly requested.

Do not run experiments or create commits unless separately authorized.

The measure of success is whether the user can find the relevant information quickly, not how many documentation files were created.
