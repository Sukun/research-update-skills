# 5-minute demo: rough task → plan → notes → storyboard

A synthetic but realistic walkthrough of the pipeline, start to finish. No real data or
private paths — just to show what each skill hands to the next one.

**Scenario:** you've been handed a folder of monthly precipitation station data for a
region and a one-line ask from a colleague. You want to turn that into a plan, work
through it while keeping notes, and end with something you could present.

## The chain

1. **[`00-rough-task.md`](00-rough-task.md)** — the messy starting point. This is what
   you'd drop into a new working directory before running `1-plan-task`.

2. **[`01-plan.md`](01-plan.md)** — what `1-plan-task` produces: a structured plan with
   purpose, data sources, methodology, and hypotheses filled in from the rough task plus a
   quick look at the data folder. In a real run, `2-review-plan` could sit here too —
   worth it if this were headed for publication; skipped for a routine exploratory pass
   like this one.

3. **[`02-notes.md`](02-notes.md)** — what you'd accumulate via `noteit` (quick, dated
   log entries as you work) and `organize-notes` (compiling those into a per-topic note).
   This is the `3-conduct-plan` stage in miniature: the plan gets executed, and the
   findings get logged as they happen rather than reconstructed afterward.

4. **[`03-storyboard.md`](03-storyboard.md)** — what `5-ppt-design` produces from the
   notes: a slide-by-slide storyboard with layout tags, ready for `6-ppt-create` to render
   into a `.pptx`. (This demo stops at the storyboard — rendering needs Pandoc installed
   locally.)

## Reading order

If you only read one file, read `01-plan.md` — it's the clearest example of the "fill in
what's known, flag what isn't" style these skills aim for. Then skim `03-storyboard.md`
to see how loosely-organized notes turn into a tight, presentable structure.
