---
name: link-research-canvas
description: Link local scientific figures, source code and research documents in Obsidian Canvas. Use for figure provenance, broken links, research maps and optional PNG Git tracking across projects.
---
# Link research Canvas

Use the project's folders, figure IDs and language. Keep existing headings, scientific text and Canvas layout. Do not run analyses, commit or push unless separately requested.

## User steps

1. Ask: “Use link-research-canvas for <project>, <documents> and <canvas>; link, trace or repair <scope>.” Request a new Canvas if needed.
2. For PNG Git tracking, ask the agent to install the bundled tool and list all source documents in `tools/png_sources.json`.
3. Check only, from the project root: `python3 tools/refresh_png_allowlist.py`
4. Refresh and sync when needed: `python3 tools/refresh_png_allowlist.py --write --sync-index`
5. Open the Canvas and test links. Review staged changes with `git diff --cached --stat` if using Git.

Step 4 stages referenced PNGs and untracks every PNG outside the list; local files stay on disk. Skip steps 2–4 when Git image tracking is not needed.

## Agent steps

1. Read project rules and target files. Find the project root and vault root; inspect Git status if available.
2. For requested PNG tracking, follow [Setup](references/workflow.md#setup). Copy the bundled Python script into the project; do not overwrite an existing tool blindly.
3. Verify figures and source code, add or update source links, and edit only the relevant Canvas nodes. Create a Canvas only when requested.
4. Check file paths, code lines and heading links. If PNG tracking is configured, run the check command above.
5. Run the sync command only when requested and the source list is complete. Preserve unrelated staged changes.
6. Report changed files, checks, unresolved sources and any Git changes.

Read [Workflow details](references/workflow.md) when setting up, tracing sources or fixing links. The reusable tool is included at [scripts/refresh_png_allowlist.py](scripts/refresh_png_allowlist.py).
