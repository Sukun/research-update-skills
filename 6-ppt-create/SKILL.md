---
name: 6-ppt-create
description: Render an approved scientific storyboard (or a figure-first markdown / topic-record Summary via the md_to_slides adapter) to PPTX with a direct python-pptx builder and a static postprocessor. Preserve authored text, Notes, slide IDs and figure sources; support opt-in balanced layouts, short/full variants and structural or visual QA. Makes no scientific content decisions.
---
# Create PowerPoint slides

## Two entry points

| Flow | Path | When |
|---|---|---|
| **Create** | `/5-ppt-design` → storyboard `<name>.md` → this skill → `<name>.pptx` + `<name>.layout.json` | first version of a deck, or a content redesign |
| **Revise** | edit `<name>.pptx` in PowerPoint → `/7-ppt-to-5` → this skill | the author moved, resized, retitled or rewrote things by hand |

Three files, one job each: `<name>.md` holds the words (titles, bullets, Notes, which figures); `<name>.layout.json` holds where each shape sits (box, font size, crop); `<name>.pptx` is the view. The `.md` and `.layout.json` sit side by side and are matched by stable `slide-id`. `/5-ppt-design` is needed again only to change the story itself (reorder sections, merge or split slides), and must keep existing `slide-id`s.

Pipeline: Markdown input adapter (`md_to_slides.py`, optional) -> storyboard -> `render_storyboard.py` -> `build_pptx.py` (direct python-pptx engine, default) -> `postprocess_template.py` (layout geometry, labels, identity stamping) -> `qa_slides.py`. Pandoc is no longer needed: its PPTX writer drops pictures and splits slides that hold text plus several figures (`--engine pandoc` remains for one transition period, deprecated). Render the approved content; do not rewrite findings, choose new figures, crop scientific context or silently change layouts.

## Steps

1. Locate the storyboard and output path. Use Python 3.9+ with `python-pptx` and Pillow. **No reference template by default; layout is owned by this skill; a template is applied only when explicitly requested** (`--reference <template.pptx>`; a sibling `reference.pptx` is no longer picked up automatically).
1a. **Sharing pass (default on).** Decks and their outlines are for sharing. Before rendering, check the storyboard against [sharing copy rules](references/sharing-copy.md): no paths, links or storage details, no status or to-do labels, no "not regenerated from code" lines in slide text or Notes; one-line take-home titles. Rendering does not rewrite text: report any breach by slide ID and ask whether to fix it in the storyboard (via `/5-ppt-design`) or render as is. Skip only when the user asks for an internal draft.
2. Check titles, figure paths, annotations and IDs. Every slide needs one `##` heading outside code/Notes. Compare heading order with the exported slides; separators and YAML frontmatter are not slide indices. Keep long titles unless shortening is approved.
3. Run `python <skill-dir>/render_storyboard.py <storyboard.md> -o <output.pptx> --project-root <project>`. Add `--reference <template.pptx>` only when a template is explicitly requested. `--engine pptx|pandoc` selects the builder (default `pptx`). The layout file `<storyboard>.layout.json` beside the storyboard is restored automatically and rewritten after the render (see "Layout file"); `--layout-json PATH` picks another file, `--fresh-layout` ignores it. The command writes a formatted `.render.md`, a filled `.postprocess.py`, a `.slides.json` manifest and `figure_registry.json` beside the deck; the approved source stays unchanged.
3a. Optional project post-step: a project finishing script (for example section bands, figure sizes) runs inside the render with `--post-step <script.py>` (called as `python script.py deck.pptx`), so that the recorded layout is restored after it, not overwritten by it. If a `build_deck.sh` sits in the storyboard's folder, use it instead of step 3: it wraps the same render call with the project's post-step and preview options. Skip it when absent or when the user declines; report that it ran and its output.
4. For requested variants, add `--variants short full`; every slide must have an explicit stable `slide-id`. Choose backup handling with `--backup exclude|append|hidden` (default: exclude).
5. When rendering a deck, run `python <skill-dir>/qa_slides.py <output.pptx> --out <qa-directory> --preview` for the requested outputs. Inspect available previews; fix mechanical problems only. Geometry diagrams are optional and are not office renders.
6. Report outputs, checks and remaining warnings by slide ID. If no preview renderer is available, report structural results only. Hidden-slide playback needs a separate check in PowerPoint-compatible presentation software.

The author's layout preferences are listed under "Author layout preferences" below; apply them unless the storyboard or the user says otherwise.

Keep the source storyboard, manuscript and scientific figures unchanged. Do not commit or push unless requested. Read [legacy layout rules](references/layouts.md) only for existing layout syntax or width rules; read [metadata and variants](references/metadata.md) for new annotations.

## Markdown input adapter

`md_to_slides.py` (this folder; `4-mk_quickview/md_to_slides.py` is a forwarding shim) converts a figure-first markdown (quickview, or a topic record) into a storyboard and, with `--render`, calls `render_storyboard.render()` (no private render chain). `--section Summary` keeps one level-1 section; the legacy `L1` is accepted and either spelling matches (`# Summary`, `# L1 · Summary`). Each `##` becomes one slide whose heading is the slide title; `--tag-prefix X` adds `X` as the small corner label. `--render-only` renders an existing storyboard. It makes no content decisions.

## Titles and section tags

The slide title always stays in its title placeholder (24 pt bold, top-left, up to two lines, never shortened). A `section-tag` is only a small label in the top-right corner (13 pt, tag colour or `grey`); a tag identical to the title is not drawn. Content starts below the title (`CONTENT_TOP_IN`, 1.05 in). The figure region now starts directly under the measured text band (never smaller than the legacy bullet-count fractions) and keeps a bottom margin; an explicit `figure-height` keeps the legacy fraction rule.

## Direct engine (`build_pptx.py`)

Parses the same storyboard format (frontmatter, `##` titles, layout/section-tag/slide-id/figures annotations, bullets, `::: notes`, pipe tables) and creates a blank 16:9 deck: title placeholder, one body placeholder with authored text (bold/italic/links kept), every declared picture (text plus any number of figures on one slide), Notes. `postprocess_template.py` is then run unchanged for geometry, labels and STAMP_IDS metadata / `figure_registry.json` (the `/7-ppt-to-5` contract). A slide with `slide-id: COVER` or `layout: cover` becomes a title slide. Inline `$...$` becomes plain Unicode text (Greek, `\ln`, `^`, `_`, `\Delta`, `\sum`, `\approx`, `\times`, `\le`, `\ge`, `\frac`...); any command it cannot map is dropped and listed in a `WARNING: LaTeX not mapped` line.

## Layouts

`custom` uses the generic fallback for elements without recorded geometry; it does not reconstruct unrecorded manual formatting. Existing defaults remain: `text-only`, `single`, `figure-dominant` (`annotated` alias), `vstack-2`, `hstack-2`, `vstack-3`, `hstack-3`, `focus-context`, `grid-2x2`, and `table`. The legacy `grid-2x3` remains a separate, manually validated helper workflow, not a supported automatic render tag.

New opt-in choices:

| Layout | Behaviour |
|---|---|
| `figure-right-text-left` | One figure at right; text uses about 30% width at left. |
| `figure-pair-right-text-left` | Two aligned figures at right, text at left; preserve both image ratios. |
| `figure-left-text-right` | Mirror image: one figure at left, text at right. |
| `figure-pair-left-text-right` | Mirror image: two aligned figures at left, text at right. |

All four side-by-side layouts share one text rule: the text box spans the figure region, so the box is vertically centred against the figure, and its text is anchored middle. Text is 18 pt by default (`font_pt` overrides) and every non-empty paragraph is a bullet point; existing bullets are kept.
| `figure-full-width` | One wide or multi-panel figure (aspect about 2.2 or wider, e.g. a 2×3 panel grid) spanning the full content width below up to three short top bullets; the section label stays top-right. Figure is never stretched or cropped; if the full width would exceed the height budget it is scaled down and centred. The top-bullet count is the largest N ≤ 3 that still leaves the figure at least 75% of content width; the rest go to Notes, prefixed "Also on the slide:". Caption is a plain line under the figure. |
| `vertical-balanced-text` | One figure below; centre text in the available space above it without overlap. Text spans the slide width less margins (about 95%). Recommended for a single near-square figure (aspect about 0.8–1.25): figure in the lower-middle, horizontally centred, text above. |
| `large-text-summary` | Three or four editable statements, evenly spaced, 28 pt by default; no coloured cards. |

No layout guarantees legible plot labels from aspect ratio alone. Warn about small panels or dense text; keep the content and ask for a layout decision when geometry cannot solve it. Never stretch plots. Preserve existing crops; new crops require an explicit safe choice that retains axes, labels, legends and units.

## Layout file (two-way)

`layout_record.py` is the coordinate layer. Each render does: generic layout → optional `--post-step` → restore `<storyboard>.layout.json` → record the final geometry back to it. The file stores, per `slide_id`, every stamped text box by role (`title`, `takeaway`, `section`, `section-band`, `caption`) and every picture by image SHA-256: position and size as slide fractions, the dominant font size, and the crop. It also stores per-slide storyboard and deck-text hashes, which `/7-ppt-to-5` uses to tell which side changed each slide (newer edit wins).

- Restoring matches by slide ID and shape key, never by position. New slides keep the generic layout. A slide whose figure set changed keeps the generic layout (recorded text boxes would overlap new figures). Render-minted IDs (no `slide-id` in the storyboard) are never restored.
- When a slide's text changed since the layout was recorded, the boxes are still restored and a warning names any box the text may overflow. Fix by editing the text or the box; do not shrink fonts unasked.
- Not recorded: colours, shadows, animations, run-level formatting other than size, text boxes added by hand (their text is read back by `/7-ppt-to-5`, their position is not).
- An old `7-ppt-to-5` `<name>.deck.json` (schema 1) is still read when no layout file exists; it restores figures only.
- `--fresh-layout` renders with the generic rules and records to `<output>.layout.json` when a layout file already exists, so the author's positions are not lost.
- QA: `python layout_record.py diff deck.pptx <name>.layout.json` lists shapes that moved, appeared or vanished.

## Author layout preferences

From the author's reviews of the CIGAR outline deck (2026-11-11 to 2026-11-12). The skill's own layouts do not implement all of them: set what `layout-options` supports and apply the rest in the project post-step (step 3a). These are the current values; update them here when the author changes them.

- **Workflow.** `/5-ppt-design` writes the storyboard `.md` from the reviewed outline and the storyboard is the source of the deck text; this skill renders it, with the project post-step passed as `--post-step` (or via `build_deck.sh`); hand edits in PowerPoint come back through `/7-ppt-to-5` into the same `.md` and its `.layout.json`. Do not export a PDF into the project; write previews (PNG per slide, contact sheet) to a scratch folder. On-slide text is copied from the outline; notes hold the full outline text, caption and evidence anchor, with no file paths, open points or to-dos (see [sharing copy rules](references/sharing-copy.md)); add no science on slides. View every slide preview, run `qa_slides.py`, and say what was not checked (PowerPoint rendering is left to the author).
- **Type and spacing.** Body text on content slides is 20 pt everywhere, including the status or caption line and text-only slides; runs carry explicit sizes, so editing the master changes nothing. Titles are 24 pt bold, left, paragraph space before and after 0, directly under the section band, with the body text directly under the title. Bullets: space before 8 pt, space after 8 pt, single line spacing. The section label is never smaller than the body text.
- **Section band (top left).** Filled rectangle at x = 0, y = 0, about 0.46 in high, width fitted to the label (about 2.8 to 4.2 in), label 20 pt bold with a 0.15 in left inset; no band on the cover. Colour-blind-safe Okabe-Ito fills with the higher-contrast (WCAG) text colour: grey #595959 (first and last section, outline slide), blue #0072B2, orange #E69F00, bluish green #009E73, reddish purple #CC79A7, vermillion #D55E00. The label always names the section, so colour is never the only cue.
- **Figures and layouts.** Never stretch or crop a figure. Vertical layout (text above, figure below): make multi-panel figures as large as the slide allows (about 11 in wide or more) by keeping on the slide only the bullet that supports the title and moving the other bullets to the notes. Side-by-side layout (text left, figure right): text column and figure column each about half the content width, gap about 0.2 in, the group centred; a single near-square or portrait figure may be smaller than its half; the text box is vertically centred on the same horizontal axis as the figure, and the figure is centred in the content area below the title. Figure-status labels (Selected, Candidate, Placeholder) never appear on slides or in notes (changed 2026-11-12; track status in storyboard comments).

- **Constants** (inches unless noted; slide 13.33 x 7.5 in). Keep the project's post-step script in step with this list.
  - Body: `BODY_PT` 20 pt; `PARA_BEFORE_PT` 8, `PARA_AFTER_PT` 8; line-count estimate with `CHAR_EM` 0.40 (average glyph width in em) and `LINE_FACTOR` 1.2.
  - Title: `TITLE_PT` 24 pt bold; `TITLE_EM` 0.43; `TITLE_W` 12.7; `TITLE_GAP_BAND` 0.02 (band bottom to title top); `TITLE_BODY_GAP` 0.03 (title bottom to body top); space before and after 0, line spacing 1.0; one title line is about 0.5 in high.
  - Band: `BAND_H` 0.46; `BAND_PT` 20 bold; `INSET` 0.15; width = `CHAR_W` 0.155 per character plus 0.3, clamped to `BAND_MIN_W` 2.8 and `BAND_MAX_W` 4.2; a "(1 of 2)" suffix is part of the label.
  - Palette (fill, then text colour by WCAG contrast): section 0 and 6 and the outline slide `595959`; 1 `0072B2`; 2 `E69F00`; 3 `009E73`; 4 `CC79A7`; 5 `D55E00`. Contrast ratios: 7.00, 5.19, 9.32, 6.14, 6.86, 5.43.
  - Layout: `BOTTOM` 7.38 (lowest edge of any shape); side-by-side `SIDE_MARGIN` 0.25 and `SIDE_GAP` 0.2, giving about 6.3 in for the text column and up to 6.3 in for the figure; multi-panel figures in vertical layouts aim for 11 in or more in total width.

## Renderer contract

- `postprocess_template.py` is the static renderer. The command fills only its DATA BLOCK; do not generate or patch per-project geometry code below it.
- Three-picture rebuilds must retain authored text, emphasis and Notes. Reuse matching pictures to preserve crops and metadata; replace only unmatched pictures. Keep Notes formatting unless reformatting is explicitly requested.
- Section labels are recognised by role metadata (13 pt, top-right) and are not restyled by the body-font pass; QA flags a label that is not small/top-right and any empty or overlapped title. Ordinary text boxes still receive body styling. Body text defaults to 20 pt; summary font is configurable.
- Legacy DATA BLOCK fields remain supported: `PPTX_PATH`, `SECTION_TAGS`, `LAYOUT_MAP`, `FIGURES`, `FIGURE_HEIGHT_OVERRIDE`, `BULLET_PLACEHOLDERS`, `STAMP_IDS`, `SLIDE_IDS`, `PROJECT_ROOT`. New `LAYOUT_OPTIONS` accepts stable slide-ID keys, or legacy indices.
- `STAMP_IDS=True` preserves the `/7-ppt-to-5` contract: slide identity on a semantic anchor, figure hash/source/ID in shape metadata, and the append-only figure registry. Selection uses IDs, not positions.
- Keep the old bullet-driven figure-height defaults. An explicit `figure-height` overrides them subject to space needed by authored text. No bullets are invented by the render command; the manual template retains its legacy `BULLET_PLACEHOLDERS=True` default.
- A compatible sibling `.index.json` can supply missing layout tags, matched by title. Paths and explicit annotations come from the current storyboard, not stale index positions.
- Generic geometry QA estimates overflow, bounds, proportional sizing, overlaps, small figures, corner concentration and tag alignment. These are warnings or structural errors, not proof of a good office render. Do not merge or remove slides based on whitespace.

