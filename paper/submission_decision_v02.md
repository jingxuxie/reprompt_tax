# Submission Decision Audit

This no-API audit synthesizes the follow-up plan readiness map, reviewer
concern audit, label-collection priority, and completed-label claim gates.
It is a submission-control artifact, not a new experiment and not completed
human/native validation.

## Summary

- Paper-facing complete items: 8
- Supporting complete diagnostics: 3
- Launch-ready label surfaces still needing labels: 3
- Reviewer concerns audited: 10
- Reviewer concerns answered or bounded: 9
- External label blockers: 1
- Completed-label gates still needing labels: 3
- First label priority: `current_model_human_audit_v02` (48 rows)
- OpenAI API calls: 0
- Decision: submit with conservative claims if labels are unavailable; upgrade only after completed labels pass gates.

## Decision Matrix

| Decision ID | Decision | Status | Evidence signal | Claim boundary | Next action |
|---|---|---|---|---|---|
| `submit_now_if_no_labels` | submit_with_conservative_claims | ready_with_external_label_blocker | 8 paper-facing items, 3 supporting diagnostics, and 9/10 reviewer concerns answered or bounded | Do not claim completed native/near-native validation. | Rerun scripts/run_submission_checks.py after any artifact or claim-boundary change. |
| `main_headline` | lead_with_gpt55_progress_probe | paper_facing_ready | current_model_refresh is complete_paper_facing and current_model_timeliness is covered | Keep GPT-5.4-mini as a bounded lower-cost diagnostic because its FTGA interval crosses zero. | No additional API run is justified for the current-model headline before labels. |
| `human_native_upgrade` | upgrade_only_after_completed_labels | external_labels_required | 3 launch-ready label surfaces remain incomplete; 3 completed-label claim gates still need labels | No human/native-validation claim is unlocked until finalized labels and rosters pass the completed-label gates. | Collect 48 current-model audit rows first, then original v0.2 labels, then v0.3 coverage review if reviewer capacity allows. |
| `coverage_v03_boundary` | keep_v03_out_of_headline | diagnostic_only_until_native_review | v03_coverage_model_smokes is bounded_diagnostic_not_headline and v03_coverage_native_review still needs labels | Do not treat v0.3 as paper-facing benchmark evidence until native review and a pre-specified larger run are complete. | Complete v0.3 native review before adding any v0.3 benchmark-performance claim. |
| `api_budget_posture` | do_not_spend_more_api_before_labels | no_api_next_step | OpenAI API calls for this audit: 0; the remaining high-value step is label collection, not another model run | Any new paid run must be tied to a claim gap that completed labels cannot answer. | Spend remaining effort on qualified labels and release-gate synchronization. |

## Evidence Index

| Decision ID | Evidence |
|---|---|
| `submit_now_if_no_labels` | `paper/followup_plan_readiness_v02.md`<br>`paper/reviewer_concern_audit_v02.md`<br>`paper/claim_evidence_checklist.md`<br>`scripts/run_submission_checks.py` |
| `main_headline` | `paper/current_model_refresh_v02.md`<br>`paper/current_model_uncertainty_v02.md`<br>`paper/current_model_regression_risk_v02.md`<br>`paper/reviewer_concern_audit_v02.md` |
| `human_native_upgrade` | `paper/label_collection_priority_v02.md`<br>`paper/completed_label_claim_gates_v02.md`<br>`results/tables/completed_label_claim_gates_v02/completed_label_claim_gates.csv`<br>`results/tables/label_collection_priority_v02/label_collection_priority.csv` |
| `coverage_v03_boundary` | `paper/coverage_expansion_v03.md`<br>`paper/coverage_native_review_design_v03.md`<br>`paper/coverage_pilot_gpt54mini_v03.md`<br>`paper/coverage_smoke_gpt55_v03.md` |
| `api_budget_posture` | `additional_experiments_plan .md`<br>`paper/experiment_ledger_v02.md`<br>`paper/followup_plan_readiness_v02.md` |

## Submission Posture

The current package is submission-ready only under conservative wording:
current-model, robustness, scorer-audit, mechanism, repair-realism,
and launch-protocol claims are supported; completed native/near-native
validation is not. The highest-value upgrade is to collect the 48-row
current-model human/native audit first, because it is the smallest
label surface that directly supports the GPT-5.x headline.
