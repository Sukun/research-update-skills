# Research documentation framework

Design reference for `01-research-outline` and the skills it coordinates (00, 4b, 4-mk_quickview, 5, 6).
First derived from the `simple_smoother_application` reorganisation (2026-11-11). Decisions are numbered so later changes can cite them.

## Purpose

Turn long-running, scattered research material (experiments, code folders, notes, quickviews, old decks) into one knowledge structure organised by scientific question. It must let the researcher:

- recover the whole project's reasoning in minutes from one outline;
- drill from a question to its evidence and figures, and compare across questions;
- present any part as slides without maintaining a second copy of the conclusions;
- absorb new results with a small, reviewable edit.

AI links material, drafts concise scientific text and proposes figures. The researcher chooses representative figures and approves scientific changes.

## D1 · Three project levels

Level names L1–L3 are used **only at project level**.

| Level | Meaning | Lives in |
|---|---|---|
| L1 | Scientific framework: chapters of the research question | `docs/outline.md`, `##` headings |
| L2 | One research question or topic: short text + 0–2 figures | `docs/outline.md`, `###` headings |
| L3 | Detailed evidence for one L2: numbers, methods, all figures, history | Topic record (preferred) or Evidence Index + Gallery (fallback), see D3 |

The outline's headings are the mind-map tree (Obsidian mdmap or markmap). Keep heading text stable once the author accepts it; changing a heading changes anchors and the map.

## D2 · Topic record sections are Summary / Evidence / Log

Inside a topic record (`4b-topic-record`), sections are named **Summary**, **Evidence**, **Log** — never L1/L2/L3 — so that "L2" always means an outline topic.

| Topic record section | Role | Feeds |
|---|---|---|
| Summary | Slide-shaped findings: one figure + ≤ 2 bullets each | Outline L2 text and figure candidates; topic slides |
| Evidence | Numbers, methods, extra figures | Project L3 |
| Log | Dated history, newest first | Project L3 |

A topic record declares the outline L2 it serves on its second line: `Outline: §1 Metric` (several allowed).

## D3 · Where L3 comes from (dual mode)

For each L2, in order of preference:

1. **Topic record exists** → the L2 links to `<topic>/00_README.md`. Figures and evidence are maintained there only.
2. **No topic record** → the L2 links to its section of the Evidence Index (text evidence) and of the Figure Gallery (figures). This is the fallback for legacy projects.

When a topic record is created for an L2, its Gallery section shrinks to one link line, and its Evidence Index section keeps only cross-topic notes or a link. Never keep the same figure catalogue in two places.

Topic records are created when a topic is actively revisited (new runs, re-analysis, a talk), not in bulk from stale material. A legacy project may pilot one topic record to test the interface.

Placement: a topic that maps to one code/data folder keeps its record in that folder; a topic spanning folders uses `docs/topics/<slug>/00_README.md`. Code folders and outline topics are often many-to-many; record the mapping in a crosswalk, not by moving files.

## D4 · Information owners

| Information | Owner |
|---|---|
| L1/L2 framework, L2 text, representative figures and their status | `docs/outline.md` |
| Detailed evidence of a topic | Its topic record (D3-1) or Evidence Index (D3-2) |
| Figure catalogue without a topic record | `docs/03_Figure_Gallery.md` |
| Raw single-experiment records | Existing folder READMEs, run notes |
| Progress, priorities, next steps | Roadmap, `todo.md` |
| Identity of figures from a historical deck | The deck's page/figure map (frozen) |
| Slides | Derived output; never a source |

Every numeric claim in an L2 must be traceable to its L3 source.

## D5 · L2 writing rules

- Heading: the topic name accepted by the author (stable). A finding- or question-style slide title may be added in the derived storyboard.
- Body: 1–3 short paragraphs: question → what the records show (with numbers that have a source) → what is unverified or open. No Evidence/Limit/Open label stacks.
- Distinguish result, interpretation, hypothesis and proposal. Keep necessary limits. Do not merge different experimental conditions into one comparison.
- An L2 with no reliable result states its purpose, evidence status and open question only. Never fill gaps with invented results.
- Keep the project's language and terminology.
- Ending line: links to L3 (`Evidence` / topic record) and, in fallback mode, `Figures` (Gallery).

## D6 · Figure status and selection

Figure lines use task checkboxes, so the author can tick a figure in Obsidian:

```markdown
![P015-F01](../path/P015-F01.png)

- [ ] P015-F01 — spatial mean of grid-point variances by depth, uniform bias vs L = 36 (CIGAR 2010–2013)
```

Symbol set (adopted 2026-11-11). Each symbol is defined here once; every skill uses only these.

| Symbol | Where | Meaning |
|---|---|---|
| `[ ]` | figure line | Candidate: proposed, not chosen |
| `[x]` | figure line | Selected: chosen by the author |
| `[-]` | figure line | Rejected by the author: kept so the same figure is not proposed again |
| `?` | evidence lines, figure captions | Open: unresolved question or unverified item |
| `!` | evidence lines, audit reports | Conflict: two sources disagree (name both) |
| `~` | evidence lines, captions | Stale: depends on a result under correction or re-run |
| `=` | Gallery group label | Like-for-like: groups differ in one factor only |
| `≠` | Gallery group label | Not comparable: different conditions; do not read quantitatively |
| `Placeholder — <what is needed>` (no checkbox) | outline | No suitable figure yet |

Rules for the symbols:
- Symbols are for scanning; sentences in L2 text stay in words.
- Presentation decks show only `[ ]` / `[x]`, `?`, `=` / `≠`; `[-]`, `!`, `~` go to Notes.
- Stale items are tagged `~` only with a stated reason; the audit lists them.

- At most two figures per L2 in the outline (`[x]` only; `[ ]` candidates may be more); any number in the topic record or Gallery.
- Selection flow: topic record Summary figures (or Gallery candidates) → author ticks 1–2 → outline. The caption names the source (`topic record Figure 3`, or a stable figure ID).
- AI may add, reorder or remove `[ ]` candidates; only the author changes `[ ]` to `[x]`. Tools must never tick a box.
- Figures need not be committed to Git; a missing local image is reported, not a reason to block structure work.
- Gallery layout: wide figures (time series) one per row; maps and parameter comparisons two per row. Label every group as like-for-like (one factor differs) or not comparable.

Note: in mdmap/markmap the checkbox lines appear as leaf nodes under the L2. This is intended: figures are visible in the map.

## D7 · Slides

Two derived deck types, both regenerated, never edited as a source:

| Deck | Source | Path |
|---|---|---|
| Topic deck | One topic record's Summary | `md_to_slides` adapter → renderer |
| Project deck | `docs/outline.md` (one slide per L2, L1 as section label) | storyboard (5-ppt-design) → renderer |

Rules learned from the first project deck:

- Slide text is copied from the outline; a mechanical check compares every visible bullet with the outline.
- Titles must stay visible; L1 identity is a small corner label, not a title replacement.
- Visible caption is short (`[ ] P015-F01 — not selected`); conditions go to Notes. At most 3 visible bullets on a figure slide; the rest go to Notes.
- Wide figures (aspect ≥ 2.4) go below the text at full width; aspect 1.4–1.9 beside the text; portrait figures are height-limited, so report them rather than crop.
- Visual QA means exporting through real office software (PowerPoint → PDF → page PNGs + contact sheet) and looking at every figure slide.
- Storyboards are tracked in Git; PPTX, PDF and previews stay local.

**Renderer direction (decided, not yet implemented):**

- **No Pandoc reference template.** Layout is owned by the skill's own renderer; a project or corporate master is optional and applied only on request.
- **Merge `md_to_slides` into `6-ppt-create`** as its Markdown input adapter: one renderer, one layout engine, one QA. `4-mk_quickview` and `4b-topic-record` call the adapter instead of carrying their own render chain.
- **Pandoc rule (author decision 2026-11-11):** keep Pandoc only if, after the title fix and the adapter merge, it renders without dropped pictures, split or extra slides, missing titles, or shapes that must be deleted and recreated afterwards. Otherwise drop it and build slides directly with python-pptx. Pandoc currently causes the observed failures (one picture per text slide, split slides for stacked layouts, hidden titles with section tags) and an extra environment dependency. The one thing to preserve is equation support: Pandoc converts LaTeX math to native PowerPoint equations; without it, keep math as Unicode text or render it as an image. Decide that before removing Pandoc.

## D8 · Update workflow

```text
new experiment → folder record / topic record → (Evidence Index if fallback) → reviewed L2 text → slides when needed
```

- A changed conclusion enters L3 first, with its source, then reaches the outline after the author's review.
- Figure selection is a separate manual step (D6).
- Lightweight checks instead of synchronisation machinery: relative links and anchors resolve; outline heading tree unchanged; every image in the outline has a status line; every L2 has an L3 link; missing generated (HPC-only) images are warnings, missing documents are errors.

## D9 · What not to build

- No Canvas as an authority (historical Canvas files stay, frozen).
- No per-L2 folders by default; a new file must bring clear reading or maintenance benefit.
- No automatic figure selection, no automatic scientific rewriting, no sync daemon.

## Open design items

1. Equation handling if Pandoc is dropped (D7).
2. Whether `5-ppt-design` reads outline L2 directly for project decks or keeps reading topic-record Summaries (both are allowed now).
3. Migration of existing topic records from `# L1 · Summary` headings to `# Summary` (`md_to_slides --section` must accept both during transition).
