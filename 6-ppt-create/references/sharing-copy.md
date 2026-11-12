# Sharing copy rules

Outlines, storyboards, decks and speaker notes are written for colleagues and reviewers, not for the author's own bookkeeping. Apply this pass by default whenever an outline or its downstream products (storyboard, PPTX text, Notes) are written or revised. Skip it only when the user asks for an internal working draft.

Source: the author's revision criteria for the CIGAR outline deck (2026-11-12).

## Remove from all shared text (slides and Notes)

- Document links, file paths, folder names, storage locations, script names and figure file names. Figure provenance lives in `<name>.layout.json` / `figure_registry.json` and in the storyboard's `<!-- figures: -->` annotations, never in visible text or Notes.
- Build or provenance remarks, e.g. any sentence containing "not regenerated from code", "regenerate from code".
- Internal status and to-do labels: "Placeholder", "No figure on this slide", "Selected" / "Candidate" figure-status lines, "Open checks", "TODO", "confirm path". Keep these as HTML comments in the storyboard if they must be tracked; they never reach the slide or Notes.
- AI-style scaffolding: meta lines such as "This slide shows", "Key point:", "Speaker cue:", "Transition:", restated headings, summary-of-the-summary lines.

## Language

- Natural, brief copy. Apply the `humanizer` skill's patterns: no "not X but Y" framing, no staged openings ("Here's the thing"), no inflated significance, no filler, no needless em dashes.
- Keep every number and every factual claim. Add no facts.

## Titles

- Each title is a take-home message (a finding, not a topic label) that follows from the slide before it, so the titles read as the story in order.
- One line only (about 55 characters at 24 pt on a 12.7 in title box). Shorten wording, never drop the claim.

## Takeaways

- Short bullets. Keep the substance and figure references such as "Fig 19".

## Structure

- Merge slides only when asked; delete the slide a merge empties.

## Open issues: flag, do not fix

- Content or figure inconsistencies found during the pass (e.g. a bullet's quoted scale disagreeing with a colorbar, stray image fragments, uneven spacing or tight margins) are reported to the author by slide number. Do not change numbers, figures or layout to resolve them unless asked.
