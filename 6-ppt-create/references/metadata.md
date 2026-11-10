# Storyboard metadata and variants

## Placement

Keep the source language and scientific text unchanged. Put metadata in HTML comments in the slide block, before its `##` heading or within the block. Separate slides with `---`; do not split a slide across several level-2 headings. The parser ignores headings inside YAML, comments, code and Notes. A conventional `<!-- Slide N -->` marker is supported but never determines the slide index.

- Stable identity: `<!-- slide-id: RESULT-01 -->` (unique within the storyboard).
- Layout: `<!-- layout: figure-right-text-left -->` (use any documented layout).
- Tag: `<!-- section-tag: "Study · Method · Topic" color="teal" -->`.
- Multi-figure sources: `<!-- figures: figures/a.png, figures/b.png, figures/c.png -->`. Use explicit local paths; commas in names are not supported by this legacy annotation.
- Height: `<!-- figure-height: 10/14 -->` or a decimal in `(0, 1]`.
- Geometry: `<!-- layout-options: {"text_fraction": 0.30, "margin": 0.25, "gap": 0.15, "content_top": 0.52, "font_pt": 20} -->`.

`margin`, `gap` and `content_top` are inches. Valid ranges: margin 0–1.5, gap 0.02–1, content_top 0.48–3, text_fraction 0.25–0.35, font_pt 16–44. Reject unknown keys and invalid values; do not silently clamp them. `font_pt` affects new balanced layouts only. Keep Notes in `::: notes` fenced divs. Rich text stays editable.

For three-picture rebuilds or `figure-pair-right-text-left`, list all figure sources; only the first needs a Markdown image anchor for Pandoc. The postprocessor fills the declared picture region without removing authored text or Notes.

## Short, full and backup

Use one `<!-- variant: ... -->` comment per slide:

| Value | Short deck | Full deck |
|---|---|---|
| `short-keep` | Include | Include |
| `short-only` | Include | Exclude |
| `full-only` | Exclude | Include |
| Unmarked | Exclude | Include |
| `backup` | Controlled by backup option | Controlled by backup option |

The base output is the complete rendered source. Derived short/full files are made after post-processing and identity stamping. `--backup exclude` omits backups, `append` puts them last, and `hidden` appends them with the OOXML hidden flag. Existing source ordering is preserved within the main and backup groups. Unselected slide parts are removed through python-pptx package relationships, without rebuilding selected slides or copying scientific text.

Stable IDs are required for variants. Never assume the first slide is a cover or force it into a variant: mark it `short-keep` when it belongs in both. Unknown flags, duplicate IDs and source/deck ID mismatches stop processing. Hidden flags can be structurally checked, but playback must be tested in compatible presentation software before claiming support verified. Use separate decks if hidden playback cannot be checked.

## Producer interface

`5-ppt-design` and quickview producers may emit these comments without changing their scientific content or story choices. Older storyboards remain valid; generated positional IDs are allowed for a single legacy render, but not variant selection. No producer skill is modified by this change. A project-specific comment such as `full-height-map` has no generic effect: choose a documented layout and geometry options instead.

## QA outputs

`qa_slides.py` writes `qa-report.json` with slide IDs, severity, structural issues, visual status and unverified hidden-playback status. With LibreOffice/soffice and pdftoppm installed, `--preview` creates office-rendered slide PNGs and a contact sheet. It does not automatically declare visual success; inspect all images. If unavailable, the report says so and structural checks still run. Geometry diagrams produced by `--geometry` are approximate diagnostics, never office-rendered visual evidence.
