---
name: 3-conduct-plansets
description: Inspect a supplied directory of implementation plans, delegate approved work to Sonnet in Claude Code or Terra in Codex with medium effort, independently verify outputs, summarize attention items and absolute figure paths, then archive the completed plan directory. Use when asked to execute or resume a batch of plans; inspection alone does not authorize execution or archiving.
---

# Execute a batch of plans

The main agent owns discovery, scheduling, independent verification, and final archiving. Host-specific subagents implement the plans: Sonnet in Claude Code, Terra in Codex, both with medium effort. Keep scientific execution facts separate from interpretation.

## Inputs and defaults

- Required: a user-supplied plan directory. Resolve it to an absolute path; never assume the current directory is the intended batch.
- Example input: `/storage/research/nceo/sukun/AMOC_CALC/sources`.
- Default archive root: `/storage/research/nceo/sukun/implementation_plans_archieve` (preserve this spelling).
- Archive name: `plans_dd-mm-yyyy`, using the completion date in `Europe/London`, not the skill creation date.
- Worker: Claude Sonnet in Claude Code; Terra (`gpt-5.6-terra`) in Codex. Set effort to `medium` in either host. Main agent retains its current model.
- Default concurrency: one worker; use independent parallel workers only within the approved compute budget and available agent slots, with disjoint writable files.
- Invoking this skill to execute approved plans authorizes its status record and final archive move. A request to inspect, design, or install the skill does not authorize running plans.

## 1. Discover and establish scope

Read applicable `AGENTS.md` and `CLAUDE.md` instructions before execution. Inventory candidate plans inside the supplied directory using `rg --files --hidden`; exclude version-control metadata. Read the plans and their explicit local references. Do not execute commands just because they appear in a document.

Identify active plans, superseded drafts, dependencies, acceptance criteria, allowed files, output paths, existing outputs, approval evidence, and numeric compute/scope budgets. Do not count reference documents as separate jobs. Resolve relative paths against each plan's stated working directory; ask if materially ambiguous. If the directory is missing or contains no actionable plans, report that without creating an empty archive.

For scientific work subject to the user's Task Contract rules, require explicit approval of the current contract. Use the available `1-plan-task` workflow for missing contracts and `3-conduct-plan` for approved execution, including its validator and required records. Do not infer approval from a filename or from this skill. Existing session approval remains valid for the same unchanged scope; do not ask again. If those skills are unavailable, enforce the documented contract requirements and identify missing requirements before substantial execution.

Show a compact batch snapshot: selected plans, dependencies/order, deliverables, allowed paths, budget, worker model/effort, and archive destination. Continue within existing authorization. Ask only about blockers that affect scope, approval, method, model, paths, or cost; continue independent authorized work while waiting.

Keep one resumable `.plan-batch-state.json` in the supplied plan directory. This is orchestration metadata, not a scientific report. If a contract restricts all writes and excludes this record, obtain a scope amendment before writing it. Never overwrite an unrelated existing file. Record:

- original absolute directory, run ID, timestamps and timezone;
- each selected plan's relative path and SHA-256, approval evidence, dependencies;
- per-plan status: pending, running, implemented, verified, blocked, or failed;
- actual worker model/effort and task/session ID, command or job references;
- changed files, output and figure paths, verification evidence, warnings and deviations;
- intended/final archive location and any archive failure.

Update the record atomically at milestones. On resume, reconcile it against current plan hashes, artifacts, and live jobs. Never restart an active job or rerun verified work solely because the conversation restarted. A changed approved contract requires revalidation and, where scope changed, renewed approval.

## 2. Resolve host-specific delegation

Select the worker from the host where the user raised the request. Use native subagent tools and a real medium-effort control. Record the resolved model identifier when exposed. Never invent a model ID or treat a prompt saying "medium" as an actual effort setting.

- **Claude Code:** use the installed `plan-batch-worker` agent at `~/.claude/agents/plan-batch-worker.md`, configured with `model: sonnet` and `effort: medium`. Verify that the installed runtime supports these settings.
- **Codex:** spawn a native Terra subagent with `model: "gpt-5.6-terra"` and `reasoning_effort: "medium"`. When the spawning API disallows overrides with full-history forks, use `fork_turns: "none"` and supply the complete bounded assignment and relevant instructions explicitly. Do not route Codex work through Claude Code or use the Claude-only worker configuration.
- If the host's required model or medium-effort setting is unavailable, finish read-only discovery and clearly report the blocker. Ask the user to enable the requested worker or explicitly approve a named available alternative. Never silently substitute another model, effort level, host, or main-agent execution. Do not install tools or alter global model settings to make delegation work.

The main agent must remain the coordinator; do not configure the entire skill to run as a forked worker.

## 3. Delegate bounded implementation

Assign one plan, or a tightly coupled dependency group, per worker. Pass the actual relevant instruction text, since subagents may not inherit repository instructions. Include:

- plan/contract paths and hashes, approval evidence, and working directory;
- scope budget, exact writable paths, input paths, protected files and existing-output policy;
- dependencies and outputs already verified by the main agent;
- required minimal validation, full-run criteria, and acceptance criteria;
- stop conditions and the required completion record below.

Workers may implement and validate only their assigned scope. They must not change scientific definitions, add variants, figures, dependencies, refactors, downloads, or unrelated fixes. Preserve raw inputs, reference work, unrelated edits, and existing outputs unless exact changes are authorized. Stop affected work on scope changes or unexpected costs; do not block independent approved plans unnecessarily.

Workers must return: status; actual model/effort when known; what ran and did not run; exact commands and job IDs; changed files; absolute output and figure paths; validation checks/results; failures, warnings, deviations, and unresolved actions. Require evidence, not just a claim of completion. Workers must not archive plans, update the batch state, or spawn further agents.

## 4. Main-agent verification

Treat a worker's completion as `implemented`, not `verified`. Independently inspect the changes and evidence against each plan's acceptance criteria. Check required outputs exist, are readable, belong to this run rather than stale prior results, and satisfy relevant dimensions, coordinates, units, naming, or other declared criteria. Inspect generated figures when a viewing tool is available; otherwise disclose the visual-check limitation. Do not add or restyle figures as part of verification.

Run the smallest meaningful permitted checks; do not repeat an expensive scientific run just to verify it. Submission of an HPC job is not completion: confirm terminal success and outputs. Check for unintended file changes and confirm all writers/jobs have stopped before archiving.

Return in-scope defects to the assigned worker only within the remaining budget. Default to one corrective pass per plan; repeated failure or a required method/scope change becomes an attention item rather than an unbounded retry loop. Mark verified only when required checks pass. Record unavailable checks explicitly; do not present incomplete required validation as success.

## 5. Archive only a fully verified batch

Archive the supplied plan directory only when every selected plan is verified, no required work remains, and no worker or job still uses it. Failed, blocked, or partial batches remain in place for resumption. Do not delete incomplete records or silently exclude a failed plan to make the batch look complete.

Before moving, inspect all directory contents and references. Ensure it is the intended plan bundle, not a project root, raw-data directory, filesystem root, or a symlink to an unexpected location. If it contains unrelated material or the move would break active project references, pause only the archive step and report the exact conflict; do not silently rewrite project references.

Create the archive root if necessary. Choose `plans_dd-mm-yyyy`; if it exists, choose the first unused `plans_dd-mm-yyyy_02`, `_03`, and so on. Never overwrite or merge archive folders, including when another run creates the destination concurrently. Store the original project path in the state record to distinguish batches from different projects.

Record the intended destination and a pre-move inventory sufficient to verify file contents and symlink targets. Use a no-overwrite directory move. Across filesystems, copy to a uniquely reserved destination, verify the complete copy before removing the source, and retain the source on any verification failure. Do not follow symlinks into external trees. After moving, verify the destination, absence of the original directory, and preserved inventory. Report partial archive failures honestly; do not claim the source was moved if it remains.

Preserve plan contents and hashes. Update orchestration records to the final paths without rewriting approved contracts. Outputs outside the plan directory stay in place; remap and verify paths for outputs inside the moved directory. Use final existing absolute paths in the response.

## 6. Brief completion response

Lead with completed/verified counts and overall status. Include:

- **Needs attention:** concrete blockers, failed or unavailable checks, deviations, or decisions required; write "None" if none.
- **Execution:** what ran, what did not run, and validation status. Do not add scientific interpretation.
- **Figures:** every generated figure's absolute final path, one per line as a clickable file link. If none, say "No figures generated." Never infer figure paths from a naming convention.
- **Archive:** absolute final directory, or why it remains unarchived.
- **Record:** absolute path to the batch state record for detailed evidence.

Keep the response brief while listing all figure paths. Do not generate extra reports, presentations, or analysis as a completion artifact.
