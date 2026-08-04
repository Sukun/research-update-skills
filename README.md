# research-update-skills

**Bounded skills for planning, executing, documenting, and presenting computational research.**

This is a portable, one-way public release of a personal research workflow. It supports
Claude Code, Codex, and compatible VS Code agent-skill installations. It does not
synchronize with any author's private configuration.

## What changed in this release

- Planning now creates an approval-gated `TASK_CONTRACT.md` with explicit
  **Non-Goals** and a numeric **Scope Budget**.
- Execution accepts only an approved, validated contract; it does not silently repair,
  generalize, refactor, add figures, or explain results.
- Scientific interpretation belongs to an explicit `4-report` stage after validation.
- Paths, examples, and installation instructions are machine-agnostic.

## Workflow

```
0-explore-data → 1-plan-task → [2-review-plan] → 3-conduct-plan → 4-report
                                                        │
                                                        └→ 5-ppt-design → 6-ppt-create

independent: organize-notes · noteit · polish-plots · claude-figure-style
```

| Skill | Purpose | Main output |
|---|---|---|
| `0-explore-data` | Read-only, bounded project/data inspection | Facts and unresolved gaps |
| `1-plan-task` | Convert a multi-step request into an approval-gated contract | `TASK_CONTRACT.md` |
| `2-review-plan` | Optional review for high-risk methods or compute | Verdict and blockers |
| `3-conduct-plan` | Execute an approved contract without scope expansion | Declared outputs, `RUN_RECORD.json`, `VALIDATION.md` |
| `4-report` | Explicit scientific reporting and interpretation | Approved report draft |
| `5-ppt-design` | Decide a slide story and storyboard | Storyboard Markdown |
| `6-ppt-create` | Mechanically render an approved storyboard | PPTX |
| `organize-notes` | Organize existing facts after approval | Notes index and topic files |
| `noteit` | Log an explicitly requested fact or decision | Project note entry |
| `polish-plots` | Apply bundled Matplotlib helpers | Targeted plot-code edits |
| `claude-figure-style` | Check a final submission figure | Figure-style checklist or edits |

## Safety model

For a Level B or C task, `1-plan-task` must define deliverables, input paths,
**Non-Goals**, allowed changed files, success criteria, stop conditions, and a Scope
Budget. The default Level B budget permits one primary experiment and one sanity check,
but no parameter variants, extra figures, extra reports, dependencies, refactors, or
scientific interpretation.

`3-conduct-plan` checks approval and contract validity before it writes or runs.
It first runs the smallest approved validation and stops for failed validation, a method
change, a budget expansion, a new output, a destructive action, or an unclear allowed
path. Its records contain observable facts only.

Call `4-report` explicitly when you want an interpretation or scientific explanation.
It separates observed results from interpretation and does not run new analyses by
default.

## Install

Clone the repository, then copy or link the desired folders from `skills/` into the
personal skills directory used by your client. Keep this repository as the editable
public source; do not use it to overwrite a private live configuration without review.

```bash
git clone https://github.com/Sukun/research-update-skills.git
cd research-update-skills
# Copy or link selected folders from ./skills/ into your client's skills location.
```

Common locations are `~/.claude/skills/` for Claude Code and `~/.agents/skills/`
for Codex. VS Code agent-skill discovery depends on the installed extension and
workspace settings; consult that client's documentation. Keep the folders intact:
each `SKILL.md` uses relative links to its bundled resources.

For `6-ppt-create`, install Pandoc plus `python-pptx` and Pillow. For
`polish-plots`, use Python with Matplotlib; Cartopy is optional for maps.

## Validate locally

```bash
python3 tools/verify_skill_tree.py skills
python3 skills/1-plan-task/scripts/validate_task_contract.py \
  /path/to/TASK_CONTRACT.md --require-approved
```

The first command checks frontmatter, directory/name matching, resource links, and
machine-specific paths. The second validates the execution contract.

## Example

See [the synthetic precipitation example](examples/demo-precip-trend/README.md). It
shows the separation between a proposed contract, execution facts, and a later
interpretation—not a real dataset or a private project.

## Non-goals

- This is not autonomous research or unattended HPC execution.
- It does not decide research questions or create scientific claims without review.
- It does not install editor extensions, manage credentials, or publish results.
- It is a manually maintained public release, not a bidirectional sync with a private
  skill directory.

## License

MIT — see [LICENSE](LICENSE).
