# Current-Model Label Sprint

This no-API sprint artifact isolates the smallest external-label task
that can upgrade the GPT-5.x headline: the 48-row current-model
human/native audit. It is an operational collection plan, not
completed human/native validation.

## Summary

- Surface: `current_model_human_audit_v02`
- Unique audit rows: 48
- Preferred reviewer slots: 6
- Preferred row judgments: 96
- Language pairs: ar-en, es-en, hi-en
- Fallback minimum path: one qualified reviewer per language pair.
- Stronger path: two independent reviewers per language pair, then
  adjudicate disagreements before running completed-label gates.
- OpenAI API calls: 0
- Claim boundary: do not claim current-model human/native validation
  until finalized labels and the qualified roster pass validation.

## Reviewer Slots

| Language pair | Reviewer | Rows | Bundle | Expected return |
|---|---:|---:|---|---|
| ar-en | 1 | 16 | `results/label_collection_bundles_v02/current_model_human_audit_v02/ar-en.zip` | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_ar-en_reviewer1_completed.csv` |
| ar-en | 2 | 16 | `results/label_collection_bundles_v02/current_model_human_audit_v02/ar-en.zip` | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_ar-en_reviewer2_completed.csv` |
| es-en | 1 | 16 | `results/label_collection_bundles_v02/current_model_human_audit_v02/es-en.zip` | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_es-en_reviewer1_completed.csv` |
| es-en | 2 | 16 | `results/label_collection_bundles_v02/current_model_human_audit_v02/es-en.zip` | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_es-en_reviewer2_completed.csv` |
| hi-en | 1 | 16 | `results/label_collection_bundles_v02/current_model_human_audit_v02/hi-en.zip` | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_hi-en_reviewer1_completed.csv` |
| hi-en | 2 | 16 | `results/label_collection_bundles_v02/current_model_human_audit_v02/hi-en.zip` | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_hi-en_reviewer2_completed.csv` |

## Screener

| Language pair | Question ID | Required response | Roster field |
|---|---|---|---|
| ar-en | native_or_near_native | TRUE | native_or_near_native |
| ar-en | script_validation | TRUE | can_validate_script |
| ar-en | qualification_notes | nonempty text | qualification_notes |
| ar-en | conflict_of_interest | FALSE | conflict_of_interest |
| ar-en | no_external_tools | TRUE | reviewer_attestation |
| es-en | native_or_near_native | TRUE | native_or_near_native |
| es-en | script_validation | TRUE | can_validate_script |
| es-en | qualification_notes | nonempty text | qualification_notes |
| es-en | conflict_of_interest | FALSE | conflict_of_interest |
| es-en | no_external_tools | TRUE | reviewer_attestation |
| hi-en | native_or_near_native | TRUE | native_or_near_native |
| hi-en | script_validation | TRUE | can_validate_script |
| hi-en | qualification_notes | nonempty text | qualification_notes |
| hi-en | conflict_of_interest | FALSE | conflict_of_interest |
| hi-en | no_external_tools | TRUE | reviewer_attestation |

## Send Messages

| Language pair | Reviewer | Subject | Bundle | Expected return |
|---|---:|---|---|---|
| ar-en | 1 | RePromptTax blinded review bundle: Arabic-English | `results/label_collection_bundles_v02/current_model_human_audit_v02/ar-en.zip` | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_ar-en_reviewer1_completed.csv` |
| ar-en | 2 | RePromptTax blinded review bundle: Arabic-English | `results/label_collection_bundles_v02/current_model_human_audit_v02/ar-en.zip` | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_ar-en_reviewer2_completed.csv` |
| es-en | 1 | RePromptTax blinded review bundle: Spanish-English | `results/label_collection_bundles_v02/current_model_human_audit_v02/es-en.zip` | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_es-en_reviewer1_completed.csv` |
| es-en | 2 | RePromptTax blinded review bundle: Spanish-English | `results/label_collection_bundles_v02/current_model_human_audit_v02/es-en.zip` | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_es-en_reviewer2_completed.csv` |
| hi-en | 1 | RePromptTax blinded review bundle: Hindi-English | `results/label_collection_bundles_v02/current_model_human_audit_v02/hi-en.zip` | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_hi-en_reviewer1_completed.csv` |
| hi-en | 2 | RePromptTax blinded review bundle: Hindi-English | `results/label_collection_bundles_v02/current_model_human_audit_v02/hi-en.zip` | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_hi-en_reviewer2_completed.csv` |

## Return Plan

| Step | ID | Action | Command |
|---:|---|---|---|
| 1 | screen_reviewers | Screen two qualified reviewers per language pair using the sprint screener. | operator action |
| 2 | fill_roster | Fill the current-model annotator roster with qualified reviewer IDs and notes. | operator action |
| 3 | send_bundles | Send the three blinded current-model bundles to reviewer1 and reviewer2 for each language pair. | operator action |
| 4 | merge_double_labels | Merge the six reviewer returns into the double-label packet. | `conda run -n reprompt_tax python scripts/merge_review_exports.py --mode human_audit --launch-packet data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv --out data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_double_completed.csv --labels-per-item 2 --inputs data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_ar-en_reviewer1_completed.csv data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_ar-en_reviewer2_completed.csv data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_es-en_reviewer1_completed.csv data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_es-en_reviewer2_completed.csv data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_hi-en_reviewer1_completed.csv data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_hi-en_reviewer2_completed.csv` |
| 5 | analyze_disagreements | Generate the disagreement packet for adjudication. | `conda run -n reprompt_tax python scripts/analyze_human_audit_adjudication.py --annotations data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_double_completed.csv --answer-key data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv --annotator-roster data/current_model_human_audit/human_audit_annotator_roster_v0.2_current_gpt5.csv --expected-models gpt-5.4-mini,gpt-5.5 --out-dir results/tables/current_model_human_audit_v0.2_adjudication --out-md paper/human_audit_adjudication_v02_current_gpt5.md` |
| 6 | finalize_adjudicated_labels | Finalize one adjudicated label row per audit item. | `conda run -n reprompt_tax python scripts/finalize_human_audit_adjudication.py --annotations data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_double_completed.csv --answer-key data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv --annotator-roster data/current_model_human_audit/human_audit_annotator_roster_v0.2_current_gpt5.csv --expected-models gpt-5.4-mini,gpt-5.5 --adjudication results/tables/current_model_human_audit_v0.2_adjudication/human_audit_adjudication_packet.csv --out data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_completed.csv --source-out results/tables/current_model_human_audit_v0.2_adjudication/human_audit_final_label_sources.csv` |
| 7 | validate_finalized_labels | Validate the completed current-model human audit labels and roster. | `conda run -n reprompt_tax python scripts/validate_completed_human_audit.py --annotations data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_completed.csv --answer-key data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv --annotator-roster data/current_model_human_audit/human_audit_annotator_roster_v0.2_current_gpt5.csv --expected-models gpt-5.4-mini,gpt-5.5` |
| 8 | summarize_finalized_labels | Summarize finalized labels before any claim wording changes. | `conda run -n reprompt_tax python scripts/summarize_human_audit.py --annotations data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_completed.csv --answer-key data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv --out-dir results/tables/human_audit_v0.2_current_gpt5` |

## Claim Boundary

This artifact does not report completed labels. It only makes the
first-priority label sprint concrete enough to execute and audit.
Paper claims remain unchanged until the completed current-model audit
file, qualified roster, summaries, and completed-label gates pass.
