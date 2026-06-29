# Label Collection Launch Pack

This launch pack consolidates the human/native review surfaces that remain
incomplete in the follow-up plan. It is operational scaffolding, not completed
human/native validation.

## Summary

- Surfaces ready for label collection: 3
- Reviewer-facing packet rows: 180
- Roster template slots: 18
- Sendable reviewer bundles: `results/label_collection_bundles_v02`
- Claim boundary: do not claim completed human/native validation until
  finalized labels pass the relevant completed-label validator and summary gate.

## Surfaces

| Surface | Status | Rows | Roster slots | Sheets | Final validator |
|---|---|---:|---:|---:|---|
| Original v0.2 human/native audit | launch_ready_needs_labels | 72 | 3 | 3 | `scripts/validate_completed_human_audit.py` |
| Current-model GPT-5.x human/native audit | launch_ready_needs_labels | 48 | 3 | 3 | `scripts/validate_completed_human_audit.py` |
| v0.3 coverage native review | launch_ready_needs_labels | 60 | 12 | 6 | `scripts/validate_completed_coverage_native_review_v03.py` |

## Completion Rules

- Build sendable reviewer zip files with
  `scripts/build_label_collection_bundles.py`, then validate them with
  `scripts/validate_label_collection_bundles.py` before sending.
- Merge returned slice exports with `scripts/merge_review_exports.py`
  before running finalized-label validation.
- Use one completed row per item only after single-review finalization or
  two-reviewer adjudication finalization.
- For the preferred stronger workflow, concatenate independent labels into
  the `double_completed_path`, run the adjudication analyzer, fill only
  disagreement rows, then run the finalizer.
- Ensure failed component fields carry their matching failure or issue
  code; the completed-label validators reject missing or contradictory
  reason codes.
- Keep answer keys and automatic labels away from reviewers; send only the
  slice CSV or static review sheet for the relevant language/slice.
- After finalized-label summaries are produced, run
  `scripts/analyze_completed_label_claim_gates.py` and
  `scripts/validate_completed_label_claim_gates.py` before updating
  any paper claim.

## Commands

| Surface | Role | Command |
|---|---|---|
| human_audit_v02 | merge_single_label_exports | `conda run -n reprompt_tax python scripts/merge_review_exports.py --mode human_audit --launch-packet data/human_audit/human_audit_packet_v0.2.csv --out data/human_audit/human_audit_packet_v0.2_completed.csv --inputs data/human_audit/human_audit_packet_v0.2_ar-en_completed.csv data/human_audit/human_audit_packet_v0.2_es-en_completed.csv data/human_audit/human_audit_packet_v0.2_hi-en_completed.csv` |
| human_audit_v02 | validate_finalized_labels | `conda run -n reprompt_tax python scripts/validate_completed_human_audit.py --annotations data/human_audit/human_audit_packet_v0.2_completed.csv --answer-key data/human_audit/human_audit_answer_key_v0.2.csv --annotator-roster data/human_audit/human_audit_annotator_roster_v0.2.csv` |
| human_audit_v02 | summarize_finalized_labels | `conda run -n reprompt_tax python scripts/summarize_human_audit.py --annotations data/human_audit/human_audit_packet_v0.2_completed.csv --answer-key data/human_audit/human_audit_answer_key_v0.2.csv --out-dir results/tables/human_audit_v0.2` |
| human_audit_v02 | analyze_double_labels | `conda run -n reprompt_tax python scripts/analyze_human_audit_adjudication.py --annotations data/human_audit/human_audit_packet_v0.2_double_completed.csv` |
| human_audit_v02 | finalize_adjudicated_labels | `conda run -n reprompt_tax python scripts/finalize_human_audit_adjudication.py --annotations data/human_audit/human_audit_packet_v0.2_double_completed.csv --adjudication results/tables/human_audit_v0.2_adjudication/human_audit_adjudication_packet.csv --out data/human_audit/human_audit_packet_v0.2_adjudicated_completed.csv` |
| current_model_human_audit_v02 | merge_single_label_exports | `conda run -n reprompt_tax python scripts/merge_review_exports.py --mode human_audit --launch-packet data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv --out data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_completed.csv --inputs data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_ar-en_completed.csv data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_es-en_completed.csv data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_hi-en_completed.csv` |
| current_model_human_audit_v02 | validate_finalized_labels | `conda run -n reprompt_tax python scripts/validate_completed_human_audit.py --annotations data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_completed.csv --answer-key data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv --annotator-roster data/current_model_human_audit/human_audit_annotator_roster_v0.2_current_gpt5.csv --expected-models gpt-5.4-mini,gpt-5.5` |
| current_model_human_audit_v02 | summarize_finalized_labels | `conda run -n reprompt_tax python scripts/summarize_human_audit.py --annotations data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_completed.csv --answer-key data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv --out-dir results/tables/human_audit_v0.2_current_gpt5 --expected-models gpt-5.4-mini,gpt-5.5` |
| current_model_human_audit_v02 | analyze_double_labels | `conda run -n reprompt_tax python scripts/analyze_human_audit_adjudication.py --annotations data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_double_completed.csv` |
| current_model_human_audit_v02 | finalize_adjudicated_labels | `conda run -n reprompt_tax python scripts/finalize_human_audit_adjudication.py --annotations data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_double_completed.csv --adjudication results/tables/current_model_human_audit_v0.2_adjudication/human_audit_adjudication_packet.csv --out data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_adjudicated_completed.csv` |
| coverage_native_review_v03 | merge_single_label_exports | `conda run -n reprompt_tax python scripts/merge_review_exports.py --mode coverage_native_review --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv --out data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv --inputs data/coverage_native_review_v03/coverage_native_review_v03_arabic_instruction_arabic_filenames_completed.csv data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_arabic_content_completed.csv data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_hindi_content_completed.csv data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_spanish_content_completed.csv data/coverage_native_review_v03/coverage_native_review_v03_hindi_english_instruction_hindi_devanagari_completed.csv data/coverage_native_review_v03/coverage_native_review_v03_spanish_instruction_arabic_quote_completed.csv` |
| coverage_native_review_v03 | validate_finalized_labels | `conda run -n reprompt_tax python scripts/validate_completed_coverage_native_review_v03.py --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv` |
| coverage_native_review_v03 | summarize_finalized_labels | `conda run -n reprompt_tax python scripts/summarize_coverage_native_review_v03.py --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv --out-dir results/tables/coverage_native_review_v03 --out-md paper/coverage_native_review_v03.md` |
| coverage_native_review_v03 | analyze_double_labels | `conda run -n reprompt_tax python scripts/analyze_coverage_native_review_adjudication.py --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_double_completed.csv` |
| coverage_native_review_v03 | finalize_adjudicated_labels | `conda run -n reprompt_tax python scripts/finalize_coverage_native_review_adjudication.py --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_double_completed.csv --adjudication results/tables/coverage_native_review_v03_adjudication/coverage_native_review_adjudication_packet.csv --out data/coverage_native_review_v03/coverage_native_review_packet_v03_adjudicated_completed.csv` |

## Reviewer Bundle Commands

```bash
conda run -n reprompt_tax python scripts/build_label_collection_bundles.py
conda run -n reprompt_tax python scripts/validate_label_collection_bundles.py
```

## Claim Gate Commands

```bash
conda run -n reprompt_tax python scripts/analyze_completed_label_claim_gates.py
conda run -n reprompt_tax python scripts/validate_completed_label_claim_gates.py
```
