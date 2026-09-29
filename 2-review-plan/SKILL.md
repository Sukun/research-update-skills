---
name: 2-review-plan
description: Perform an optional high-risk review of a research Task Contract or methodology. Use for new or untested methods, scientifically consequential metrics, expensive computation, broad parameter exploration, independent validation or generalisation claims, or plans whose failure would waste substantial time. Skip routine extensions of established pipelines.
---

# Review a High-Risk Research Plan

Audit only the methodology and risks relevant to the approved intent. Do not expand the task into a broader research programme.

## Entry gate

Use this skill only when at least one condition applies:

- method or metric is new, untested, or scientifically consequential;
- computation or data acquisition is expensive;
- parameter exploration is broad;
- independent validation, robustness, or generalisation is claimed;
- failure would waste substantial time or resources.

Skip it for routine code changes, replications, and established-pipeline extensions unless the user explicitly requests review.

## Review

1. Read the Task Contract and only the references needed to assess it.
2. Verify deliverables, Non-Goals, Scope Budget, files allowed to change, stop conditions, and observable success criteria.
3. Apply only relevant scientific checks:
   - metric integrity when metrics drive a claim;
   - baseline fairness when a comparison is claimed;
   - independent or out-of-sample validation when generalisation is claimed;
   - compute feasibility when cost is material;
   - deterministic inputs, parameters, and dependency order.
4. Separate blockers from optional suggestions. Optional suggestions must not enter the Task Contract without user approval.
5. Return exactly one verdict: `REJECT_FOR_NOW`, `CONDITIONALLY_ACCEPT`, or `ACCEPT`.

## Output

Lead with the verdict — do not make the user read supporting material to find it.

1. **Verdict line first**: verdict, confidence, one-sentence rationale.
2. **Blockers as decisions, not findings**: for each blocking issue, state the conflict in one line, then a recommended resolution the user can approve with a single "同意/agreed" — not just a description of the problem. If a blocker has no concrete fix yet, say so explicitly rather than listing it as prose.
3. Skip or compress everything else by default: checks performed/skipped and non-blocking suggestions are audit trail, not decisions — keep each to a single compact line (or a short list), and never let them outrank the blockers in length or position. Do not pad the response with them.
4. Open questions that can flip the verdict — only if they change what the user needs to decide right now.

Do not write code, run experiments, fabricate results, modify the contract, or add mandatory baseline, validation, documentation, or interpretation tasks when they are irrelevant to the stated claim.

Once the user approves the recommended resolutions, restate the verdict as updated (e.g. REJECT_FOR_NOW → ACCEPT) in one line — do not require a second review pass to reflect an approval already given.
