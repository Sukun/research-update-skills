# Workflow details

## Setup

Linking does not require Git, fixed folders or a slide deck. Work only on the requested documents and figures. Keep non-Markdown documents in their original format; link the whole file if section links are unsupported.

For requested PNG tracking in an existing Git repository:

1. Copy this skill's `scripts/refresh_png_allowlist.py` to `<project>/tools/refresh_png_allowlist.py`. Inspect an existing script before changing it. Do not run the bundled copy directly against a project: it finds the root from its own location.
2. Create or extend `tools/png_sources.json` with a JSON array of project-relative Markdown and Canvas paths, for example: `["docs/topic/report.md", "notes/evidence.md", "research-map.canvas"]`.
3. Keep existing `.gitignore` rules. Add `*.[pP][nN][gG]` and one generated block, with `# BEGIN GENERATED PNG ALLOWLIST` and `# END GENERATED PNG ALLOWLIST` on separate lines. Place the block after the PNG ignore rule. Review existing PNG exceptions rather than deleting them blindly.
4. Run `python3 tools/refresh_png_allowlist.py`. Check the complete source list and proposed changes before syncing.

The tool uses only Python 3's standard library. No packages are needed. Do not initialize Git or install tracking tools for a linking-only task.

## Links and sources

- Verify local figures and code before linking. Trace titles, axes, legends, parameters and save calls such as Python `savefig`, R `ggsave` or MATLAB `exportgraphics`. A matching filename alone does not prove a figure's origin.
- Keep existing figure IDs. Assign unique IDs only where missing; slide-based IDs such as `P001-F01` are optional and follow picture-object order. Keep original source files unchanged.
- Resolve Markdown links from the document's directory. Encode spaces and special characters; add `#L142` for a verified code line. Editor support for line anchors varies. Write unverified or external HPC paths as plain code text, not local links.
- Add source entries without rewriting scientific content. Update existing entries instead of adding duplicates. Create an audit table only when requested or needed for the requested provenance task.
- Use `exact` when title templates, filenames and parameters agree; `probable` when the function matches but the entry point, parameters or composition remain uncertain; `unknown` when no source is found. Record search terms and blockers. Record file existence separately from source confidence.
- From `docs/topic/report.md`, a figure link could target `../../figures/case.png` and a code link `../../analysis/plot_case.py#L142`. Check actual files and lines before using these examples.
- For a requested TSV audit, reuse the project's schema. Useful fields are `figure_id`, `document_section`, `visible_text_key`, `code_location`, `save_path_or_pattern`, `path_verified`, `confidence` and `note`. Separate columns with tabs; include every requested figure and all plausible source candidates.

## Canvas

- Read the JSON first. Preserve node IDs, positions, sizes, edges and manual layout; change only relevant fields. Keep the original formatting where practical.
- File nodes use `file` for the target and `subpath` for a heading anchor. Preserve heading text exactly. For a requested new Canvas, use unique IDs and group existing evidence by topic without inventing scientific claims.
- Obsidian resolves file paths from the vault root. Find the actual vault and existing symlinks; do not assume it is the project root or create symlinks or image copies automatically.
- The PNG tool resolves Canvas paths from the Canvas directory. A Canvas at the vault root avoids this mismatch. Otherwise, ensure both resolve correctly or adapt the parser within the authorized scope before syncing.
- Check modified file and heading targets. If the app cannot be opened, report static validation only and leave the final click-through check to the user.

## PNG tracking

- Scan only `tools/png_sources.json` sources. Read explicit local links from Markdown and Canvas file nodes, not plain candidate paths. Markdown code examples, comments and remote URLs are excluded.
- Supported forms include Markdown links/images, reference definitions, Obsidian links and HTML images. Use explicit paths; the tool does not search by bare filename or parse dynamic HTML.
- Markdown paths resolve from the document directory; Canvas paths from its directory. A leading `/` means project-relative. Missing images or paths outside the repository stop writes.
- The default command checks only. `--write` updates only the generated ignore block. `--write --sync-index` also stages all referenced PNGs, including changed image contents, and untracks all other PNGs with `git rm --cached`. Local files remain.
- The tool does not stage documents, Canvas files, configuration or `.gitignore`. Include all documents whose PNGs must stay tracked before syncing. Preserve unrelated staged work; do not force removals or reset the index.
- Only PNG tracking is managed. Other figure formats can be linked without changing their Git rules. Notebook, Word and PDF contents are not scanned; link their PNGs explicitly from a configured Markdown or Canvas file if needed.
- This limits future tracking; it does not shrink Git history.

## Results

- Exit 0: check passed or write completed. Exit 1: check found pending changes. Exit 2: input or execution failed.
- `MISSING`: fix the file, path or mount before writing. `UNTRACK`: sync will remove the file from Git tracking, while keeping it on disk.
- A Git failure can leave earlier operations applied. Inspect staged changes, fix the cause and rerun; do not discard user work.
