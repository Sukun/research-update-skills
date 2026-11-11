---
name: 6-ppt-create
description: Render an approved scientific storyboard to PPTX with Pandoc and a static python-pptx postprocessor. Preserve authored text, Notes, slide IDs and figure sources; support opt-in balanced layouts, short/full variants and structural or visual QA. Makes no scientific content decisions.
---
# Create PowerPoint slides

Keep the Pandoc + python-pptx workflow. Render the approved content; do not rewrite findings, choose new figures, crop scientific context or silently change layouts.

## Steps

1. Locate the storyboard, output path and optional `reference.pptx`. Use Python 3.9+ with `python-pptx` and Pillow; locate Pandoc on PATH or pass `--pandoc /path/to/pandoc`.
2. Check titles, figure paths, annotations and IDs. Every slide needs one `##` heading outside code/Notes. Compare heading order with the exported slides; separators and YAML frontmatter are not slide indices. Keep long titles unless shortening is approved.
3. Run `python <skill-dir>/render_storyboard.py <storyboard.md> -o <output.pptx> --project-root <project>`. Add `--reference <template.pptx>` when needed. A matching sibling `.deck.json` is used automatically; pass `--deck-json /path/to/deck.json` when it is elsewhere or has a different name. The command writes a formatted `.render.md`, a filled `.postprocess.py`, a `.slides.json` manifest and `figure_registry.json` beside the deck; the approved source stays unchanged.
4. For requested variants, add `--variants short full`; every slide must have an explicit stable `slide-id`. Choose backup handling with `--backup exclude|append|hidden` (default: exclude).
5. When rendering a deck, run `python <skill-dir>/qa_slides.py <output.pptx> --out <qa-directory> --preview` for the requested outputs. Inspect available previews; fix mechanical problems only. Geometry diagrams are optional and are not office renders.
6. Report outputs, checks and remaining warnings by slide ID. If no preview renderer is available, report structural results only. Hidden-slide playback needs a separate check in PowerPoint-compatible presentation software.

Keep the source storyboard, manuscript and scientific figures unchanged. Do not commit or push unless requested. Read [legacy layout rules](references/layouts.md) only for existing layout syntax or width rules; read [metadata and variants](references/metadata.md) for new annotations.

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
| `vertical-balanced-text` | One figure below; centre text in the available space above it without overlap. Text spans the slide width less margins (about 95%). Recommended for a single near-square figure (aspect about 0.8–1.25): figure in the lower-middle, horizontally centred, text above. |
| `large-text-summary` | Three or four editable statements, evenly spaced, 28 pt by default; no coloured cards. |

No layout guarantees legible plot labels from aspect ratio alone. Warn about small panels or dense text; keep the content and ask for a layout decision when geometry cannot solve it. Never stretch plots. Preserve existing crops; new crops require an explicit safe choice that retains axes, labels, legends and units.

## Recorded manual layouts

A compatible `deck.json` from `7-ppt-to-5` takes precedence over generic layout rules for recorded figures. Match explicit stable slide IDs and unique image SHA-256 hashes; restore recorded position, size and crop after generic processing, before generating variants. New or unmatched slides and figures use generic layout; warn when a recorded figure cannot be matched. Never match by slide position or guess among duplicate images.

The current `deck.json` schema records figure geometry only, not text-box positions, font formatting or section-tag geometry. It therefore cannot fully reconstruct a manually adjusted slide; inspect overlaps and report this limitation. If a complete manual layout is required, retain the edited PPTX as the reference and apply changes to it directly rather than claiming that `deck.json` preserves everything. Do not overwrite the source PPTX or deck.json.

## Renderer contract

- `postprocess_template.py` is the static renderer. The command fills only its DATA BLOCK; do not generate or patch per-project geometry code below it.
- Three-picture rebuilds must retain authored text, emphasis and Notes. Reuse matching pictures to preserve crops and metadata; replace only unmatched pictures. Keep Notes formatting unless reformatting is explicitly requested.
- Section tags are recognised by role metadata, so the 24 pt bold white style survives the body-font pass. Ordinary text boxes still receive body styling. Body text defaults to 20 pt; summary font is configurable.
- Legacy DATA BLOCK fields remain supported: `PPTX_PATH`, `SECTION_TAGS`, `LAYOUT_MAP`, `FIGURES`, `FIGURE_HEIGHT_OVERRIDE`, `BULLET_PLACEHOLDERS`, `STAMP_IDS`, `SLIDE_IDS`, `PROJECT_ROOT`. New `LAYOUT_OPTIONS` accepts stable slide-ID keys, or legacy indices.
- `STAMP_IDS=True` preserves the `/7-ppt-to-5` contract: slide identity on a semantic anchor, figure hash/source/ID in shape metadata, and the append-only figure registry. Selection uses IDs, not positions.
- Keep the old bullet-driven figure-height defaults. An explicit `figure-height` overrides them subject to space needed by authored text. No bullets are invented by the render command; the manual template retains its legacy `BULLET_PLACEHOLDERS=True` default.
- A compatible sibling `.index.json` can supply missing layout tags, matched by title. Paths and explicit annotations come from the current storyboard, not stale index positions.
- Generic geometry QA estimates overflow, bounds, proportional sizing, overlaps, small figures, corner concentration and tag alignment. These are warnings or structural errors, not proof of a good office render. Do not merge or remove slides based on whitespace.

