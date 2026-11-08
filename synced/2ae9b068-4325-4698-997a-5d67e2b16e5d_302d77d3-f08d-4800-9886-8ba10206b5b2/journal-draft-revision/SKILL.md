---
name: "journal-draft-revision"
description: "Use when revising, compressing or polishing a journal manuscript draft before submission: baseline sync, batched sentence-level edit ledgers, evidence checks, comment handling, submission closeout."
---

# Journal draft revision pipeline

A staged pipeline for taking a near-final scientific manuscript to submission. It was distilled from a multi-batch revision of an ocean-science paper that used a planner/reviewer pair (Leader + Consultant) and a local applying agent, with the manuscript in Markdown under Git. It also works with a single agent: keep the roles, and run them one after another.

Core principle: **revision is not reinterpretation.** Make the paper shorter and clearer without changing what the author meant, how strongly they claimed it, or what the main result is.

## 0. Roles and authority

Roles:
- **Planner (Leader)**: proposes edits and owns the ledger.
- **Reviewer (Consultant)**: independently checks evidence and attacks claims.
- **Applier (local agent)**: applies edits verbatim, builds, commits, and pushes.
- **Author**: decides.

Priority of instructions:
1. The author's explicit current instruction and frozen decisions.
2. The repository's revision policy, if one exists.
3. Tracker notes and earlier plans.
4. External writing advice.

Agreement between agents is a proposal, not author approval. Label provenance (`[User input]`, `[A synthesis]`). Never upgrade a co-author comment or a reviewer suggestion into an author decision.

Keep one tracker file (for example `pending.md`): author decisions with dates, a queue, open comments, and one summary line per batch. Do not create additional trackers, branches or reports unless the author asks for them.

## 1. Baseline first

1. Identify the newest author text (often a co-author-reviewed .docx) and the maintained source of truth (Markdown under Git).
2. **Sync the source to the newest draft as its own commit, before any editing.** If sync and edits share a diff, nobody can review either. Do it paragraph by paragraph:
   - Accept tracked changes.
   - Do not port Word comments; record them in the tracker.
   - Keep the source's markup conventions, such as LaTeX display equations, pipe tables and caption style.
   - Carry typos over unchanged and log them for a later fix.
3. Put figure or file renumbering in its own commit (filenames, manifest, build-script keys, caption labels), separate from text.
4. Do not import uncaptioned or sample images found in the draft. Log them.
5. Verify the sync: compare draft and source paragraph by paragraph after normalisation, and list every paragraph below about 0.98 similarity with the reason. Check scripts go in a temp directory and are not committed.
6. Reviewers in a browser often cannot read .docx or .png files. The synced Markdown, plus figure numbers reported by the applier, is what they review.

## 2. Diagnose before rewriting

- Word count per section. Find structural weight, for example Data and Methods taking about a third of the main text before any result.
- Check the target journal's actual guidelines; do not rely on memory. Look at word limits (often there are none), Appendix versus Supplement rules, first-citation figure order, AI-use disclosure, and the short summary.
  - Copernicus journals, for example, put technical developments in Appendices, and a Supplement must not introduce conclusions that are absent from the main text.
- List open review comments by thread, and record which are resolved.
- Look for **scientific consistency defects** before any polishing:
  - figure legend or inset numbers against the text;
  - text that describes a method different from the one the figure used;
  - averaging periods in captions against panel titles;
  - abstract claims that the body does not contain;
  - summary-table cells stronger than the text.

## 3. Decisions up front, kept short

Before batching, give the author one compact list. For each item give options, a recommendation and its impact. Split the list into three classes:
- **A, affects results:** must be settled before submission. Examples: method or figure mismatch, sign or definition conventions, wrong periods.
- **B, author choice:** keep or delete a paragraph or figure, Appendix versus Supplement, adding an analysis.
- **C, submission checklist:** references, DOIs, author information, data and code availability, AI statement.

The author decides whether a code check is worth doing. Do not impose verification the author has waived. Record each decision as a dated line in the tracker and treat it as frozen.

## 4. Batching

- One planner-plus-applier task completes **one batch**.
- Batch by chapter, not by paragraph. Plan at most about three paragraphs per discussion round, but apply and review a whole chapter as a diff, with one commit per section.
- Typical order:
  0. Baseline sync.
  1. Introduction plus Data and Methods compression; move technical detail to an Appendix; complete equation and symbol definitions.
  2. Results, part one.
  3. Results, part two.
  4. Discussion, summary table and abstract. The abstract comes last because it must summarise the final body.
  5. Supplement, references, cross-references and captions, typos, submission material.
- Put **scientific-wording corrections** (weakened claims, removed attributions, changed numbers) in a separate batch or commit, so the author can review them line by line with `git diff`.
- Every new batch starts by verifying the previous batch's commit SHA.
- Do not run rounds just to reach a count. Converge as soon as the ledger covers the batch and the reviewer has no substantive objection.

## 5. Sentence-level ledger: the unit of work

Each entry has these fields:

| ID | location (section/para/first words) | old text (verbatim from SHA X) | new text (empty = delete; move = "→ Appendix A.x") | type | one-line reason | status (decided / needs author) |

Rules:
- The old text must match the file exactly once. Check with `count(old) == 1` before handing over.
- One entry covers one sentence or one contiguous fragment.
- Anything that changes scientific meaning, such as weakening, removing a qualifier or changing a number, is marked **needs author**.
- Moved text is copied verbatim. Any bridging edit is a separate entry.
- The applier applies entries **verbatim**. If an entry fails to match, it reports the failure and skips the entry; it never rewrites.
- Commit C1 contains the decided entries and C2 the needs-author entries, so the author can revert C2 alone.
- Dry-run all entries in sequence on a copy, run the build checker, then hand over. Embed the ledger as JSON in the apply prompt, with explicit stop-on-failure and baseline-SHA checks.
- Commit messages are a single line of English. Add no co-author or attribution trailers.

## 6. Editing rules

In order of priority:
1. **Minimum change.** Do not rewrite a sentence that is already clear. Delete redundancy before rewording. Keep the author's own words.
2. **Delete, don't hedge.** Remove:
   - restatements of tables, captions or earlier sections;
   - "this section provides…" openers and "discussed below" closers;
   - evaluative adverbs ("very good", "clearly", "greatly");
   - "significant" when no statistical test was done;
   - defensive completeness: paragraphs on unused diagnostics, results asserted without a figure (flag these to the author rather than silently deleting a frozen paragraph).
3. **Match claim strength to evidence.**
   - Do not turn a possible explanation into a mechanism.
   - Do not add a list of plausible mechanisms. One interpretation plus "not isolated here" is enough.
   - Do not write a strong claim and then follow it with caveats.
   - Write "possibly" or "may contribute" when the paper did not test attribution.
   - Cite literature as background ("X et al. suggest…"), not as this paper's result.
4. **Concrete beats abstract.** Prefer numbers from the figure to adjectives, and avoid invented frameworks or labels. Make the conditional explicit, for example "√2·σ holds only for similar variances and negligible mean difference".
5. **One job per paragraph.**
   - Results: finding, evidence, one comparison.
   - Discussion: interpretation, one qualification, an open question only if it is directly connected.
6. **Style references.** Use the author's own published papers as the voice model. Use Humanizer-type checks only to find padding: staging, forced triads, inflated significance, re-explaining things to the reader.
7. Keep the application motivation, such as prediction, at the same strength in the abstract, introduction and conclusion: "candidate…; not tested here".

## 7. Verification checklist, per entry

- Each number matches the figure legend or inset. Read the image; do not trust the text.
- Statistic definitions are consistent: mean of maxima versus maximum of the mean, and centred RMSD versus RMSD.
- Averaging and comparison periods match between text, caption and panel title.
- Equations: coordinate direction is defined, units are consistent, and the text's accumulation direction matches the formula.
- Error and uncertainty statements are not overreached:
  - no derived bounds without an assumed covariance;
  - OSSE differences are not lower bounds;
  - do not compare quantities across different time scales.
- Every cited paper supports exactly the claim made. Check its scope: which products, which periods, "suggest" or "show".
- Figure numbering follows first citation. Every supplement figure is cited in the main text.
- Every abstract and summary-table statement exists in the body.
- The build and checker pass, and the diff touches only the ledger's files.

## 8. Two-agent review discipline

- The reviewer independently re-reads sources (papers, code, repository) and gives counter-examples. The planner evaluates each point; agreement is not automatic.
- Both sides retract cleanly when shown wrong. Record what changed and why.
- Each round: judgment first, then evidence, then a one-line next step, plus a compact progress outline (settled, open, waiting for the author).
- Before adding any safeguard, review step or file, name the concrete risk, the benefit and the cost, and compare it with a simpler option. "No change needed" is a valid outcome.

## 9. Review comments

- Track each thread with author, anchor, one-line content and status.
- Draft a short reply that says what changed and what was deliberately not done, for example no new figure or no ensemble mean.
- A thread is "recommended to close" only after the change lands and is checked.
- Comments the author defers stay recorded in the tracker, untouched.

## 10. Submission closeout

- References in both directions: every citation is in the list and every list entry is cited. Check DOIs and dataset versions against landing pages. Remove orphans only after confirming they are no longer cited.
- Author list, affiliations, corresponding author, CRediT roles, competing interests, funding.
- Data and code availability with exact versions and DOIs. AI-use statement, which the author confirms against the journal policy. Short summary.
- Final cross-reference and caption pass. Build the submission file and run the checker.

## Communication defaults

- Discuss with the author in Chinese, keeping technical terms in English. Be concise, put the judgment first, and do not use defensive or marketing language.
- Tag anything unverified as 待核验. Never present an estimate (word counts, percentages) as a measured result.
- Ask the author only what evidence cannot settle. Batch the questions, at most about five per round, each with options and a recommendation.