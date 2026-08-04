Research Workflow Skills  (trigger with /<name>)
=================================================

0-explore-data      → EDA report (data structure, coverage, quick-look plots)
1-plan-task         → research plan document in docs/
2-review-plan (optional) → audit verdict (ACCEPT / CONDITIONALLY ACCEPT / REJECT) + fix list
3-conduct-plan      → scripts + outputs + clean research note (from readme instructions)
4-report            → TECH_REPORT_DRAFT.md  or  PAPER_DRAFT.md
5-ppt-design        → <topic>_<dd-mm-yyyy>.md  (slide storyboard with layout tags)
6-ppt-create        → <topic>_<dd-mm-yyyy>.pptx  (rendered from storyboard via Pandoc)

Pipeline: 1-plan-task → [2-review-plan] → 3-conduct-plan
Use 2-review-plan when the plan is high-stakes (e.g. paper-submission-level
analysis, expensive compute/experiments) and you want a structured critique of
metric validity and baseline fairness before committing. Skip it for routine
exploratory tasks.

Standalone utilities (not pipeline steps — use any time, ongoing maintenance):

organize-notes      → RESEARCH_NOTES.md (index) + notes/<topic>.md (detail files)
noteit              → weekly research log entry (insights, conclusions, validated facts)
polish-plots        → refactor matplotlib scripts to use shared_plotting style

organize-notes → notes/<topic>.md
       │
       ├──► 4-report ──────────────────► TECH_REPORT_DRAFT.md  (for reading / submission)
       │
       └──► 5-ppt-design ──► 6-ppt-create ──► .pptx  (for presenting)

Write a paper	organize-notes → 4-report
Give a talk	organize-notes → 5-ppt-design → 6-ppt-create
Both	organize-notes → 4-report (report) and separately organize-notes → 5-ppt-design → 6-ppt-create (slides)
4-report → 5-ppt-design pipeline (write report, then convert it to slides) still works — skill 5 accepts a report file as input. But it's no longer required; skill 5 can read notes/ directly.
