---
name: noteit
description: "Log research insights and work-progress records into two persistent files: a per-project notes file (./docs/<PROJECT_NAME>_notes.md) for detailed reasoning, and a global quick-notes file (~/docs/quick_notes.md) for short Obsidian-compatible progress entries. New entries are prepended (most recent first). Invoke directly: /noteit <what to remember>."
license: MIT
---

# Research Note Logger

## Purpose

Preserve the *why* and *what-it-means* from plan-mode reasoning and Q&A threads — the dense conceptual understanding that evaporates fast during vibe-coding. Write it down at the moment of insight, in the language of physics and numerics, so it stays findable weeks later.

**Key principle: distil, don't transcribe. Capture the settled conclusion and the logical path to it, not the exploration steps.**

## How To Invoke

```
/noteit <what to remember>
```

Also worth invoking right after finishing an implementation or bug fix, to capture the
detail that would otherwise be forgotten by next week — see "What To Log" below.

## What To Log

**YES — capture these:**
- Physical or numerical facts with their reasoning (e.g., "LLC90 splits a zonal section into U-faces because the C-grid staggers velocity at cell edges; a constant-j slice cuts through u-points, not tracer points")
- Questions that any researcher working on this topic would plausibly ask
- Hypotheses and the evidence for/against them
- Conclusions from Q&A threads (the question + the settled answer)
- Assumptions that were validated or rejected, and why
- Failure modes and why they occur
- Conceptual links between ideas (e.g., "NEMO's EOS is not Boussinesq-consistent if you use in-situ density for the buoyancy flux term")

**NO — skip these:**
- Code syntax, API details, how to call a specific function
- Debugging steps that are not conceptually generalisable
- Intermediate exploration that didn't converge to a conclusion

---

## Output Files

Two files are written every time this skill runs.

### File 1 — Project Notes (detailed)

| Property | Value |
|----------|-------|
| **Location** | `./docs/` in the current workspace root |
| **Filename** | `<PROJECT_NAME>_notes.md` — one file per project, grows indefinitely |
| **Example** | `docs/ocean-model-run_notes.md` |

PROJECT_NAME is the workspace folder name (e.g., `ocean-model-run`).

Create `./docs/` if it does not exist. Create the file if it does not exist with a single header line `# Research Notes — <PROJECT_NAME>`. **New entries are prepended: inserted directly below the header line, above all prior entries.**

### File 2 — Global Quick Notes (short / Obsidian-compatible)

| Property | Value |
|----------|-------|
| **Location** | `~/docs/quick_notes.md` |
| **Purpose** | One-liner progress records, sortable by project and date in Obsidian |

Create `~/docs/` if it does not exist. Create `quick_notes.md` if it does not exist with the header `# Quick Notes`. **New entries are prepended: inserted directly below the header line.**

---

## Entry Format — quick_notes.md

One line per entry, prepended below the `# Quick Notes` header:

```
## [YYYY-MM-DD] [[PROJECT_NAME]] <Short declarative claim>
```

**Concrete example:**
```
## [2026-05-28] [[ocean-model-run]] Zonal sections sample velocity on rotated grid tiles
```

Rules:
- Date in ISO format `YYYY-MM-DD` so Obsidian date-sort works correctly.
- `[[PROJECT_NAME]]` is an Obsidian wiki-link — enables backlinks from the project page and project-based filtering.
- The claim must be declarative (a fact or action, not a label).

---

## Entry Format — Project Notes File (`<PROJECT_NAME>_notes.md`)

Prepend entries using this exact template (new entries go directly below the file header line, above all prior entries). The topic title **must be a declarative claim**, not a question.

## [YYYY-MM-DD] <Topic title — a short declarative claim>

**Context / Question**
One or two sentences: what problem was being investigated or what question was asked.

**Reasoning**
The logical chain: physical/numerical logic, assumptions, sign conventions, grid conventions — whatever is needed to follow the argument. Write as prose, 3–10 sentences. Be precise about quantities and conventions.

**Conclusion**
The settled fact or validated hypothesis. Self-contained enough to be understood without re-reading the full thread.

**Source context** *(omit if obvious)*
Where this came from: "plan mode analysis of [topic]", "Q&A — [date]", "from reading [paper/doc]"

**Topic title rules:**
- Bad: "LLC90 grid question" → Good: "LLC90 zonal sections sample U-faces, not tracer points"
- Bad: "EOS investigation" → Good: "NEMO's linear EOS underestimates density in the deep North Atlantic"
- Bad: "debugging boundary issue" → Good: "NEMO subdomain raw output contains stale halo rows before lbc_lnk"

---

## Behaviour by Invocation Context

### Writing procedure (applies every time)

Every time this skill is invoked, write to **both files** in this order:

**Step A — Project Notes file (`./docs/<PROJECT_NAME>_notes.md`)**
1. If the file does not exist: create `./docs/` if needed, create the file with header `# Research Notes — <PROJECT_NAME>`, then write the detailed entry immediately below.
2. If the file exists: read the entire file. Write back: (header line) + blank line + (new detailed entry) + blank line + (all prior content after the header line).

**Step B — Quick Notes file (`~/docs/quick_notes.md`)**
1. If `~/docs/` does not exist: create it.
2. If the file does not exist: create it with header `# Quick Notes`, then write the one-line quick entry immediately below.
3. If the file exists: read the entire file. Write back: (header line) + blank line + (new one-line entry) + blank line + (all prior content after the header line).

After writing, report both file paths. Do not ask for confirmation unless the topic is ambiguous.

### Mid-conversation invocation
Invoked right after a Q&A exchange, while the reasoning is still fresh.

1. Infer the topic from the most recent exchange. If the topic is unambiguous, **write immediately without asking for confirmation** — report both file paths after writing.
2. If the topic is ambiguous (multiple threads active), ask: *"Which topic should I log — [A] or [B]?"* — one short question, then write.

### Plan-mode extraction
Invoked when the user asks to preserve reasoning from a plan-mode investigation.

1. Extract the key conceptual findings from the plan reasoning — skip the step-by-step task decomposition.
2. Write directly without asking for confirmation.

---

## Example Entry

```markdown
---
## [2026-05-21] NEMO subdomain raw output contains stale halo rows before lbc_lnk

**Context / Question**
Tracer fields on the western boundary looked discontinuous after reading raw subdomain outputs from a 1-degree NEMO run. Was this a model bug or a post-processing artefact?

**Reasoning**
NEMO's lateral boundary condition routine (lbc_lnk) fills halo rows via MPI exchange and applies the ORCA north-fold periodicity in the same call. When reading raw subdomain files directly (without the ioserver), halo rows are present in the binary but the fold has not been applied — the apparent "western edge" of a recombined field actually contains stale halo data from the previous time step, not physically meaningful values. The discontinuity therefore appeared only in the halo band, not in the interior, which confirmed it was not a model bug.

**Conclusion**
Never diagnose boundary discontinuities from raw NEMO subdomain output. Always use ioserver-assembled files, or manually strip halo rows before recombining. The interior (non-halo) cells are always valid.

**Source context**
Plan mode analysis of ORCA1 boundary artefact, 2026-05-21
```

## Example Quick-Note Entry

```markdown
## [2026-05-28] [[ocean-model-run]] Zonal sections sample velocity on rotated grid tiles
```

---

## Notes on Design Choices

- **Single file per project** accumulates all notes for that workspace in one place. Prepending keeps the most recent entry at the top — opening the file immediately shows the latest work.
- **Global quick_notes.md** acts as a cross-project diary. Obsidian wiki-links (`[[PROJECT]]`) allow filtering by project via backlinks without any folder structure.
- **Prepend requires reading the existing file once per write.** For `quick_notes.md`, which accumulates cross-project entries over time, this cost is acceptable. If the file becomes very large, older entries can be manually archived to a dated section at the bottom.
- **Declarative topic titles** make the file scannable as a flat list of facts — useful for ctrl-F and for building a mental map of what has been established.
- **Prose reasoning** (not bullets) forces a complete logical argument rather than a list of disconnected observations.
