# Label Collection Operator Handoff

This handoff converts the validated reviewer bundles into an execution
checklist for collecting the missing qualified human/native labels. It
is operational support, not completed human/native validation.

## Summary

- Outgoing reviewer bundle assignments: 12
- Reviewer-facing rows to collect: 180
- First priority: current-model human/native audit.
- OpenAI API calls: 0
- Claim boundary: no human/native-validation claim is unlocked until
  returned labels, rosters, summaries, and completed-label gates pass.

## Send Checklist

| Priority | Surface | Slice | Rows | Bundle | Expected return |
|---:|---|---|---:|---|---|
| 1 | current_model_human_audit_v02 | ar-en | 16 | `results/label_collection_bundles_v02/current_model_human_audit_v02/ar-en.zip` | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_ar-en_completed.csv` |
| 1 | current_model_human_audit_v02 | es-en | 16 | `results/label_collection_bundles_v02/current_model_human_audit_v02/es-en.zip` | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_es-en_completed.csv` |
| 1 | current_model_human_audit_v02 | hi-en | 16 | `results/label_collection_bundles_v02/current_model_human_audit_v02/hi-en.zip` | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_hi-en_completed.csv` |
| 2 | human_audit_v02 | ar-en | 24 | `results/label_collection_bundles_v02/human_audit_v02/ar-en.zip` | `data/human_audit/human_audit_packet_v0.2_ar-en_completed.csv` |
| 2 | human_audit_v02 | es-en | 24 | `results/label_collection_bundles_v02/human_audit_v02/es-en.zip` | `data/human_audit/human_audit_packet_v0.2_es-en_completed.csv` |
| 2 | human_audit_v02 | hi-en | 24 | `results/label_collection_bundles_v02/human_audit_v02/hi-en.zip` | `data/human_audit/human_audit_packet_v0.2_hi-en_completed.csv` |
| 3 | coverage_native_review_v03 | arabic_instruction_arabic_filenames | 10 | `results/label_collection_bundles_v02/coverage_native_review_v03/arabic_instruction_arabic_filenames.zip` | `data/coverage_native_review_v03/coverage_native_review_v03_arabic_instruction_arabic_filenames_completed.csv` |
| 3 | coverage_native_review_v03 | english_instruction_arabic_content | 10 | `results/label_collection_bundles_v02/coverage_native_review_v03/english_instruction_arabic_content.zip` | `data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_arabic_content_completed.csv` |
| 3 | coverage_native_review_v03 | english_instruction_hindi_content | 10 | `results/label_collection_bundles_v02/coverage_native_review_v03/english_instruction_hindi_content.zip` | `data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_hindi_content_completed.csv` |
| 3 | coverage_native_review_v03 | english_instruction_spanish_content | 10 | `results/label_collection_bundles_v02/coverage_native_review_v03/english_instruction_spanish_content.zip` | `data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_spanish_content_completed.csv` |
| 3 | coverage_native_review_v03 | hindi_english_instruction_hindi_devanagari | 10 | `results/label_collection_bundles_v02/coverage_native_review_v03/hindi_english_instruction_hindi_devanagari.zip` | `data/coverage_native_review_v03/coverage_native_review_v03_hindi_english_instruction_hindi_devanagari_completed.csv` |
| 3 | coverage_native_review_v03 | spanish_instruction_arabic_quote | 10 | `results/label_collection_bundles_v02/coverage_native_review_v03/spanish_instruction_arabic_quote.zip` | `data/coverage_native_review_v03/coverage_native_review_v03_spanish_instruction_arabic_quote_completed.csv` |

## Return Intake

| Priority | Surface | Step | Command role |
|---:|---|---:|---|
| 1 | current_model_human_audit_v02 | 1 | `merge_single_label_exports` |
| 1 | current_model_human_audit_v02 | 2 | `validate_finalized_labels` |
| 1 | current_model_human_audit_v02 | 3 | `summarize_finalized_labels` |
| 1 | current_model_human_audit_v02 | 4 | `analyze_double_labels` |
| 1 | current_model_human_audit_v02 | 5 | `finalize_adjudicated_labels` |
| 2 | human_audit_v02 | 1 | `merge_single_label_exports` |
| 2 | human_audit_v02 | 2 | `validate_finalized_labels` |
| 2 | human_audit_v02 | 3 | `summarize_finalized_labels` |
| 2 | human_audit_v02 | 4 | `analyze_double_labels` |
| 2 | human_audit_v02 | 5 | `finalize_adjudicated_labels` |
| 3 | coverage_native_review_v03 | 1 | `merge_single_label_exports` |
| 3 | coverage_native_review_v03 | 2 | `validate_finalized_labels` |
| 3 | coverage_native_review_v03 | 3 | `summarize_finalized_labels` |
| 3 | coverage_native_review_v03 | 4 | `analyze_double_labels` |
| 3 | coverage_native_review_v03 | 5 | `finalize_adjudicated_labels` |

Run the single-label merge, finalized-label validator, and summary only
after every expected slice export and qualified roster for the surface
has been returned. For the stronger two-reviewer workflow, use the
`analyze_double_labels` and `finalize_adjudicated_labels` commands
before any paper claim is widened.

## Claim Gate Status

| Priority | Surface | Gate status | Decision | Required action |
|---:|---|---|---|---|
| 1 | current_model_human_audit_v02 | needs_labels | no_claim | missing completed inputs: data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_completed.csv; data/current_model_human_audit/human_audit_annotator_roster_v0.2_current_gpt5.csv |
| 2 | human_audit_v02 | needs_labels | no_claim | missing completed inputs: data/human_audit/human_audit_packet_v0.2_completed.csv; data/human_audit/human_audit_annotator_roster_v0.2.csv |
| 3 | coverage_native_review_v03 | needs_labels | no_claim | missing completed inputs: data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv; data/coverage_native_review_v03/coverage_native_review_roster_v03.csv |
