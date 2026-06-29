# Follow-up Plan Readiness Audit

This audit maps `additional_experiments_plan .md` to current repo
evidence. It is a planning and claim-boundary artifact: it identifies
which follow-up items are paper-facing now and which still need
qualified human/native review before stronger claims are supportable.

## Status Counts

| Status | Count |
|---|---:|
| bounded_diagnostic_not_headline | 1 |
| complete_paper_facing | 8 |
| complete_supporting | 2 |
| launch_ready_needs_labels | 3 |
| not_started_requires_validator | 1 |

## Evidence Map

| Plan item | Section | Status | Paper use | Validation signal | Next step |
|---|---|---|---|---|---|
| current_model_refresh | Experiment A | complete_paper_facing | headline current-model result | gpt-5.5 contract 98.3 FTGA, 0.017 RTT; gpt-5.4-mini contract 85.0 FTGA with bounded sign-test evidence | none for current submission; keep GPT-5.5 as the current-model headline |
| main_results_metrics | Submission-ready checklist | complete_paper_facing | main results table | FTGA, RTT, unresolved, Repair@1/2, and token-tax rows are present for all five full-run models | none |
| family_level_failure_story | Submission-ready checklist | complete_paper_facing | failure-mode and residual-error claims | editing-preservation dominance and current-model residual families are separately audited | none |
| language_slice_caveat | Submission-ready checklist | complete_paper_facing | bounded language-slice interpretation | language-slice effects are reported with the non-population caveat enforced by the claim linter | none |
| token_burden_caveat | Submission-ready checklist | complete_paper_facing | token-tax interpretation | normalized token tax falls for five models, while absolute total tokens rise for five contract rows | none |
| prompt_mechanism | Experiment C | complete_paper_facing | mechanism and mitigation-scope paragraph | content-preservation is close to the full contract on both current models, so prompt dominance is not claimed | none |
| repair_realism | Experiment F | complete_supporting | interaction-burden sensitivity diagnostic | repair wording sensitivity is measured on the dominant editing-preservation failures | treat as a controlled diagnostic, not a user-study result |
| judge_refresh | Experiment G | complete_supporting | scorer sanity-check evidence | GPT-5.5 judge refresh agrees with the automatic scorer on 70/72 sampled labels | do not substitute judge agreement for native-speaker validation |
| original_human_audit_labels | Experiment B | launch_ready_needs_labels | protocol-ready only until completed annotations exist | 72 launch rows, 57 auto passes, 15 auto failures, blank annotation fields | collect qualified native/near-native labels and pass validate_completed_human_audit.py |
| current_model_human_audit_labels | Experiment B extension | launch_ready_needs_labels | protocol-ready current-model validation only | 48 launch rows, 32 auto passes, 16 auto failures, one row per current-model stratum | collect qualified labels for GPT-5.x rows before claiming current-model human validation |
| v03_coverage_native_review | Experiment D | launch_ready_needs_labels | v0.3 coverage protocol only | 60 synthetic rows across 6 slices; status launch_ready_but_not_completed_native_validation | complete native review before using v0.3 as paper-facing benchmark evidence |
| v03_coverage_model_smokes | Experiment D | bounded_diagnostic_not_headline | runnability and scoring smoke only | saved v0.3 model-output diagnostics exist, but native review is still incomplete | keep out of headline benchmark claims until v0.3 review and a prespecified run are complete |
| related_work_and_limitations | Submission-ready checklist | complete_paper_facing | positioning and claim boundary | related work and limitations are checked by validate_paper_claims.py | none |
| artifact_manifest_claim_checklist | Submission-ready checklist | complete_paper_facing | release and reproducibility gate | manifest and claim checklist are regenerated and checked in the submission gate | rerun run_submission_checks.py after any artifact change |
| collaborator_validated_language_pair | Experiment E | not_started_requires_validator | not claim-ready | no new collaborator-validated language pair is claimed in the current artifact set | add only if a qualified validator is available; otherwise leave out of the current submission |

## Claim Boundary

The current-model refresh, prompt-mechanism diagnostic, repair-realism
diagnostic, judge refresh, token-burden caveat, language-slice caveat,
related work, and release manifest are ready for the current submission.

Three launch-ready annotation surfaces remain incomplete: the original
72-row v0.2 human-audit packet, the 48-row current-model human-audit
packet, and the 60-row v0.3 native-review packet. Do not claim
native/near-native validation has been completed until the completed
annotation files and qualified rosters pass their validators.
The consolidated label-collection launch pack in
`paper/label_collection_launch_pack_v02.md` lists all reviewer-facing
files, roster templates, finalization commands, and claim gates.

The v0.3 model-output smokes remain bounded diagnostics. They show that
the expanded coverage scaffold is runnable and scoreable, but they are
not paper-facing benchmark evidence before native review and a
pre-specified larger run are complete.

Current recommendation: submit with the GPT-5.5 current-model headline
and the launch-ready audit protocols if labels cannot be collected in
time; upgrade the final paper only after completed labels pass the
human/native-review gates.
