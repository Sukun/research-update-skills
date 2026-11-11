Research Workflow Skills  (trigger with /<name>)
=================================================
1-plan → 2-review → 3-conduct
        │
        ▼  per run
4-mk_quickview ──(optional "share": --pptx)──► 6-ppt-create ──► PPTX (fast share)
        │  accumulate
        ▼  per topic
4b-topic-record (00_README.md: L1 / L2 / L3)
        │  accumulate topics
        ▼  per audience
5-ppt-design (reads several L1s → cross-topic storyboard) ──► 6-ppt-create ──► PPTX
                                                                   │ hand-edited?
                                                                   ▼
                                                             7-ppt-to-5


0-explore-data      → EDA report (data structure, coverage, quick-look plots)
1-plan-task         → research plan document in docs/
2-review-plan (optional) → audit verdict (ACCEPT / CONDITIONALLY ACCEPT / REJECT) + fix list
3-conduct-plan      → scripts + outputs + clean research note (from readme instructions)
4-report            → TECH_REPORT_DRAFT.md  or  PAPER_DRAFT.md
4-mk_quickview      → quickview_<topic>_<dd-mm-yyyy>.md  (figure-first view of one run)
                      + optional share: md_to_slides.py --render → storyboard + .pptx
                      (Mode B = former 5a: assemble_figures.py for an explicit
                      slides × figures arrangement of files in a directory)
4b-topic-record     → <topic>/00_README.md  (per-topic ppt-style record: L1 summary slides,
                      L2 evidence, L3 log; notes renamed 01_, 02_ … plan → results)
5-ppt-design        → <topic>_<dd-mm-yyyy>.md  (cross-topic story; default source = L1 of topic records)
5a-ppt-quick-assembly  REMOVED → use 4-mk_quickview share step, Mode B (recoverable from git history)
6-ppt-create        → <topic>_<dd-mm-yyyy>.pptx  (rendered from storyboard via Pandoc)
7-ppt-to-5          → deck.json + deck_revised.md  (read a hand-edited PPTX back into a
                      storyboard; closes the Markdown <-> PowerPoint loop)

Pipeline: 1-plan-task → [2-review-plan] → 3-conduct-plan
Use 2-review-plan when the plan is high-stakes (e.g. paper-submission-level
analysis, expensive compute/experiments) and you want a structured critique of
metric validity and baseline fairness before committing. Skip it for routine
exploratory tasks.

Standalone utilities (not pipeline steps — use any time, ongoing maintenance):

notes-organizer      → RESEARCH_NOTES.md (index) + notes/<topic>.md (detail files)
noteit              → weekly research log entry (insights, conclusions, validated facts)
polish-plots        → refactor matplotlib scripts to use shared_plotting style
8-finalize-figure-style → publication-ready figure checklist + QA pass (final ship step only)

notes-organizer → notes/<topic>.md
       │
       ├──► 4-report ──────────────────► TECH_REPORT_DRAFT.md  (for reading / submission)
       │
       └──► 5-ppt-design ──► 6-ppt-create ──► .pptx  (for presenting)

Write a paper	notes-organizer / 4b-topic-record → 4-report
Give a talk	4b-topic-record (per topic) → 5-ppt-design → 6-ppt-create
Share one run fast	4-mk_quickview → "share" (md_to_slides.py --render)
Share one topic	md_to_slides.py <topic>/00_README.md --section L1 --render
Just arrange existing figures	4-mk_quickview share step, Mode B (assemble_figures.py → md_to_slides.py --render-only)
Recover a hand-edited deck	6-ppt-create → [edit in PowerPoint] → 7-ppt-to-5
  (use --bootstrap once for a legacy deck that predates ID stamping)
  (use quickview Mode B when the user already states the slides, figure order and layout;
   use 5 when the model must decide the story, grouping or conclusions)
Both	notes-organizer → 4-report (report) and separately notes-organizer → 5-ppt-design → 6-ppt-create (slides)
4-report → 5-ppt-design pipeline (write report, then convert it to slides) still works — skill 5 accepts a report file as input. But it's no longer required; skill 5 can read notes/ directly.
