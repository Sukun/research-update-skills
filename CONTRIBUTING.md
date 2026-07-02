# Contributing

This is a small, personal set of skills shared in case it's useful to others — issues and
small, focused PRs are welcome.

## Reporting issues

If a skill's trigger phrases don't match how you'd naturally ask for it, or a `SKILL.md`
assumes something about your setup that doesn't hold, open an issue. Include which skill,
what you expected, and what happened instead.

## Proposing changes

- Keep skills **single-purpose and machine-agnostic**. A `SKILL.md` shouldn't assume a
  specific OS, conda environment, or absolute path — see how existing skills fall back to
  `command -v <tool>` or `~`-relative paths instead of hardcoding a machine.
- Prefer editing an existing skill over adding a new one, unless it's genuinely a new step
  in the workflow.
- If you're changing behavior (not just fixing a typo or a broken path), explain the "why"
  in the PR description — what problem you hit and how the change fixes it.

## Testing a skill locally

Skills are just a folder with a `SKILL.md` that Claude Code reads. To try a change:

```bash
cp -r skills/<skill-name> ~/.claude/skills/<skill-name>
```

Then invoke it in a real (or throwaway) working directory and check the output matches
what the `SKILL.md` promises. There's no separate test suite — the skill's own output is
the test.
