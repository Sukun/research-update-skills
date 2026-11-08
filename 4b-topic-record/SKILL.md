---
name: 4b-topic-record
description: "Summarise accumulated notes, quickviews and reports on ONE research topic into a single ppt-style markdown record — <topic>/00_README.md with L1 summary slides (key figure + 2 lines each), L2 skippable evidence, L3 dated log, and a source-notes table — and number the topic's notes in plan → results order. Project mode: one cross-topic progress page (STATUS.md) from the records' L1. Use when the user says topic record, summarise this topic, organise this topic folder, consolidate these notes, or wants to pick a topic back up after weeks. Figures are linked, never copied, so regenerated plots update automatically. Not for a single run's figures (use 4-mk_quickview), manuscripts (use 4-report), or multi-topic decks (use 5-ppt-design, which reads these records' L1)."
---

# Topic Record

## Purpose

One file per research topic that can be reviewed **like a short deck**: read L1 in two
minutes to recover the framework, conclusions-so-far and open decisions; drop to L2 only for
numbers and method; use L3 to see the order in which things happened.

```
4-mk_quickview (per run) ──accumulate──► 4b-topic-record (per topic) ──several topics──► 5-ppt-design → 6-ppt-create
```

This skill **condenses and organises existing documented facts**. It runs no analysis, makes no
new figures and adds no new interpretation.

## When To Use

- "topic record", "summarise / organise / consolidate this topic (folder)"
- several quickviews or reports have piled up in one topic folder
- the user wants to pick up a topic after weeks away
- refreshing an existing `00_README.md` after new notes land in the folder

| Situation | Use instead |
|---|---|
| Look at one run's figures | `4-mk_quickview` |
| Interpretation / write-up for readers | `4-report` |
| A deck across several topics | `5-ppt-design` (reads each record's L1) |
| Log one finding or decision | `log-finding` / `noteit` |

## Output

- `<topic_dir>/00_README.md` — the record (overwrite on refresh; keep L3 history).
- The topic's notes renamed `01_…`, `02_…` in **plan → results, oldest first** order.
- Updated links in the parent index files that point at renamed notes.

## Structure of `00_README.md`

```markdown
# <Topic> — topic record

Last updated <yyyy-mm-dd> · **State:** <one line: where the topic stands now>
Read **L1** for the overview (2 min). **L2** is skippable detail, numbered to match L1. **L3** is the dated log.

---

# L1 · Summary

## 1. Question and framework          ← 2–3 bullets, no figure: question, key definitions, conventions

---

## 2. <Result stated as a finding>    ← 1 key figure + caption, then ≤ 2 bullets with numbers; end with → **Continue/Stop** if the source says so

![](../../plots/…/key_figure.png)

**Figure 1.** <one line: what is plotted — data, window, smoothing>

- …
- …

---
… (≤ 6 result slides)

## N. Open decisions                  ← bullets only, taken from the notes' open questions

---

# L2 · Evidence (skippable)

## 2a. <same title stem as L1 slide 2> — detail
Compact paragraph(s): data, window, method, all numbers, flags, caveats; companion figures;
`Source: [01_…](01_….md) §x`.

---

# L3 · Log (newest first)
- yyyy-mm-dd — what was done (→ slide numbers)

# Source notes
| # | File | Content |
|---|---|---|
| 01 | [name](01_….md) | one line |
```

Figure numbering (journal style, so any figure can be cited as "Figure N" or "<topic> Figure N"):

- **One running `Figure N` per record**, assigned top to bottom in document order: L1 first, then L2.
  Never restart per section, and companion figures (Full/East/West, T/S/σ) get consecutive numbers,
  not sub-letters, unless the user asks for panels.
- **Every embedded figure is followed directly by `**Figure N.** <caption>`**, one line saying what
  is plotted (data, period, smoothing), with no interpretation. On an L1 slide the caption is the
  slide's first bullet, so a slide has the caption plus at most 2 more bullets.
- A figure that appears in both L1 and L2 keeps its **first** number. In L2, refer to it as
  "Figure N" in text and do not embed or caption it again.
- Text that points at a figure says "Figure N" (for example "see Figure 4") rather than re-describing it.
- When refreshing an existing record, keep the numbers of unchanged figures and append new ones
  at the end of the numbering (the next unused N). Don't renumber, because cited numbers must stay valid.
  A removed figure leaves its number unused.
- Figures that stay links only (a list of further dates or panels) are not numbered.
- If a note already carries its own `Figure N`, the record's number wins. Give the source's
  number in the caption as "(source note 04, its Fig 2)" so both stay traceable.

Rules for L1 (it must render cleanly with `4-mk_quickview/md_to_slides.py --section L1`):

- Every slide is a `## ` heading. **Titles state the finding**, not the topic ("Cross-latitude
  coupling is weak", not "Cross-latitude results"). Keep titles ≤ 65 characters after TeX → Unicode.
- ≤ 1 key figure per result slide (2–3 only for companion Full/East/West sets), ≤ 3 bullets,
  the first being the `**Figure N.**` caption.
  Put everything else in L2.
- No level-1 headings inside L1, no tables, no nested bullets.
- Slide 1 is the framework and the last slide is open decisions. Everything between is results in reading order.

## Content rules

- **Only documented facts** from the topic's notes, run records, validation files, or the user's
  words. Numbers must come from those sources and never be read off a figure.
- Keep the source's labels: an interpretation stays tagged **[INT]** (or "the report's reading"),
  and an observation stays plain. Never upgrade a hedge.
- Where sources conflict, keep both, with dates, and say which supersedes which. Don't choose silently.
- Mark stale content (figure older than a later decision, superseded definition) as **[stale]** with
  the reason.
- Relative figure paths only, verified from the topic directory. Never copy figures into `docs/`.

## Workflow

1. **Inventory (read-only).** List the topic folder's files (size, mtime, symlink targets) and grep
   the repo for references to each filename, including code comments, other docs, `contracts/` and
   run records. Read every note in full.
   **Staleness check:** list decisions, definition changes and data reprocessing dated after each
   figure or number (FINDINGS, STATUS, run records, git log). Tag affected items **[stale]** with the
   reason; never fix them here.
2. **Propose the rename table** (old → new, plan → results by date) and show which files
   reference each old name. Ask for approval before touching anything, unless the user already
   approved the renames for this folder.
   - Plans kept elsewhere (for example symlinks into `plans/`) keep their name and are listed first in
     the source-notes table.
3. **Rename** with `mv` (not `git mv`, so nothing is staged). For every old name cited by a file
   you may not edit (`contracts/`, run records, paper repo), leave an alias symlink
   `old_name.md -> 0N_old_name.md`. Update live references (index READMEs, STATUS boards,
   code comments) to the new names. Stale path strings inside the renamed notes may be updated
   only when the user asked for it.
4. **Write `00_README.md`** per the structure above.
5. **Verify.** Every `](…)` link in the record resolves from the topic directory. Every embedded
   figure has a caption, and numbers run 1..N in document order with no duplicates. Optionally,
   dry-run `md_to_slides.py 00_README.md --section L1 -o <scratchpad>/check.md`: it must exit 0.
6. **Link the record** as the first entry for the topic in the parent index (for example
   `docs/README.md`).
7. **Report:** record path, rename table, alias symlinks created, references updated, references
   deliberately left (and why), conflicts and stale items found.

## Project mode

Trigger: "project progress", "overview of all topics". Refresh each topic record first, then write
one page (the project's `STATUS.md` unless the user names another path) built **only from the
records' L1 and the staleness check**:

- Header: date, one-line current stage, current definitions/windows table.
- Per topic, one block: link to its record, 1 key figure + caption, then four one-line bullets —
  **Done**, **Finding**, **Problem** (incl. [stale] items), **Next**.
- Then one table of open decisions/next work across topics (ID, task, status, dependency).
- No L2 detail, no new interpretation. Listing work does not authorize it.

## Safety

- Never delete a note, figure or symlink. Retiring content means listing it under source notes.
- Never edit `contracts/`, run records, paper or manuscript repositories, or paper-locked sources.
- Never regenerate or move figures.
- Rename only inside the topic folder the user named.
