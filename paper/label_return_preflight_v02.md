# Label Return Preflight

This no-API preflight checks whether expected reviewer return files and
qualified roster files are present before merge and completed-label
validation commands run. It is operational support, not completed
human/native validation.

## Summary

- Workflow surfaces checked: 6
- Expected return CSV files: 36
- Present return CSV files: 0
- Qualified roster files present: 0/6 workflow checks
- Workflows ready to merge: 0
- OpenAI API calls: 0
- Claim boundary: no human/native-validation claim is unlocked until
  merge, completed-label validation, summaries, and claim gates pass.

## Workflow Preflight

| Priority | Surface | Workflow | Expected returns | Present | Roster present | Ready to merge | Next action |
|---:|---|---|---:|---:|---|---|---|
| 1 | `current_model_human_audit_v02` | minimum_single_label | 3 | 0 | False | False | collect 3 missing return file(s); create the filled qualified reviewer roster |
| 1 | `current_model_human_audit_v02` | preferred_double_label | 6 | 0 | False | False | collect 6 missing return file(s); create the filled qualified reviewer roster |
| 2 | `human_audit_v02` | minimum_single_label | 3 | 0 | False | False | collect 3 missing return file(s); create the filled qualified reviewer roster |
| 2 | `human_audit_v02` | preferred_double_label | 6 | 0 | False | False | collect 6 missing return file(s); create the filled qualified reviewer roster |
| 3 | `coverage_native_review_v03` | minimum_single_label | 6 | 0 | False | False | collect 6 missing return file(s); create the filled qualified reviewer roster |
| 3 | `coverage_native_review_v03` | preferred_double_label | 12 | 0 | False | False | collect 12 missing return file(s); create the filled qualified reviewer roster |

## Return File Checklist

| Surface | Workflow | Slice | Reviewer | Expected return | Present | Shape ready | Blocker |
|---|---|---|---:|---|---|---|---|
| `current_model_human_audit_v02` | minimum_single_label | `ar-en` | 1 | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_ar-en_completed.csv` | False | False | missing returned CSV |
| `current_model_human_audit_v02` | minimum_single_label | `es-en` | 1 | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_es-en_completed.csv` | False | False | missing returned CSV |
| `current_model_human_audit_v02` | minimum_single_label | `hi-en` | 1 | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_hi-en_completed.csv` | False | False | missing returned CSV |
| `human_audit_v02` | minimum_single_label | `ar-en` | 1 | `data/human_audit/human_audit_packet_v0.2_ar-en_completed.csv` | False | False | missing returned CSV |
| `human_audit_v02` | minimum_single_label | `es-en` | 1 | `data/human_audit/human_audit_packet_v0.2_es-en_completed.csv` | False | False | missing returned CSV |
| `human_audit_v02` | minimum_single_label | `hi-en` | 1 | `data/human_audit/human_audit_packet_v0.2_hi-en_completed.csv` | False | False | missing returned CSV |
| `coverage_native_review_v03` | minimum_single_label | `arabic_instruction_arabic_filenames` | 1 | `data/coverage_native_review_v03/coverage_native_review_v03_arabic_instruction_arabic_filenames_completed.csv` | False | False | missing returned CSV |
| `coverage_native_review_v03` | minimum_single_label | `english_instruction_arabic_content` | 1 | `data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_arabic_content_completed.csv` | False | False | missing returned CSV |
| `coverage_native_review_v03` | minimum_single_label | `english_instruction_hindi_content` | 1 | `data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_hindi_content_completed.csv` | False | False | missing returned CSV |
| `coverage_native_review_v03` | minimum_single_label | `english_instruction_spanish_content` | 1 | `data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_spanish_content_completed.csv` | False | False | missing returned CSV |
| `coverage_native_review_v03` | minimum_single_label | `hindi_english_instruction_hindi_devanagari` | 1 | `data/coverage_native_review_v03/coverage_native_review_v03_hindi_english_instruction_hindi_devanagari_completed.csv` | False | False | missing returned CSV |
| `coverage_native_review_v03` | minimum_single_label | `spanish_instruction_arabic_quote` | 1 | `data/coverage_native_review_v03/coverage_native_review_v03_spanish_instruction_arabic_quote_completed.csv` | False | False | missing returned CSV |
| `current_model_human_audit_v02` | preferred_double_label | `ar-en` | 1 | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_ar-en_reviewer1_completed.csv` | False | False | missing returned CSV |
| `current_model_human_audit_v02` | preferred_double_label | `ar-en` | 2 | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_ar-en_reviewer2_completed.csv` | False | False | missing returned CSV |
| `current_model_human_audit_v02` | preferred_double_label | `es-en` | 1 | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_es-en_reviewer1_completed.csv` | False | False | missing returned CSV |
| `current_model_human_audit_v02` | preferred_double_label | `es-en` | 2 | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_es-en_reviewer2_completed.csv` | False | False | missing returned CSV |
| `current_model_human_audit_v02` | preferred_double_label | `hi-en` | 1 | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_hi-en_reviewer1_completed.csv` | False | False | missing returned CSV |
| `current_model_human_audit_v02` | preferred_double_label | `hi-en` | 2 | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_hi-en_reviewer2_completed.csv` | False | False | missing returned CSV |
| `human_audit_v02` | preferred_double_label | `ar-en` | 1 | `data/human_audit/human_audit_packet_v0.2_ar-en_reviewer1_completed.csv` | False | False | missing returned CSV |
| `human_audit_v02` | preferred_double_label | `ar-en` | 2 | `data/human_audit/human_audit_packet_v0.2_ar-en_reviewer2_completed.csv` | False | False | missing returned CSV |
| `human_audit_v02` | preferred_double_label | `es-en` | 1 | `data/human_audit/human_audit_packet_v0.2_es-en_reviewer1_completed.csv` | False | False | missing returned CSV |
| `human_audit_v02` | preferred_double_label | `es-en` | 2 | `data/human_audit/human_audit_packet_v0.2_es-en_reviewer2_completed.csv` | False | False | missing returned CSV |
| `human_audit_v02` | preferred_double_label | `hi-en` | 1 | `data/human_audit/human_audit_packet_v0.2_hi-en_reviewer1_completed.csv` | False | False | missing returned CSV |
| `human_audit_v02` | preferred_double_label | `hi-en` | 2 | `data/human_audit/human_audit_packet_v0.2_hi-en_reviewer2_completed.csv` | False | False | missing returned CSV |
| `coverage_native_review_v03` | preferred_double_label | `arabic_instruction_arabic_filenames` | 1 | `data/coverage_native_review_v03/coverage_native_review_v03_arabic_instruction_arabic_filenames_reviewer1_completed.csv` | False | False | missing returned CSV |
| `coverage_native_review_v03` | preferred_double_label | `arabic_instruction_arabic_filenames` | 2 | `data/coverage_native_review_v03/coverage_native_review_v03_arabic_instruction_arabic_filenames_reviewer2_completed.csv` | False | False | missing returned CSV |
| `coverage_native_review_v03` | preferred_double_label | `english_instruction_arabic_content` | 1 | `data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_arabic_content_reviewer1_completed.csv` | False | False | missing returned CSV |
| `coverage_native_review_v03` | preferred_double_label | `english_instruction_arabic_content` | 2 | `data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_arabic_content_reviewer2_completed.csv` | False | False | missing returned CSV |
| `coverage_native_review_v03` | preferred_double_label | `english_instruction_hindi_content` | 1 | `data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_hindi_content_reviewer1_completed.csv` | False | False | missing returned CSV |
| `coverage_native_review_v03` | preferred_double_label | `english_instruction_hindi_content` | 2 | `data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_hindi_content_reviewer2_completed.csv` | False | False | missing returned CSV |
| `coverage_native_review_v03` | preferred_double_label | `english_instruction_spanish_content` | 1 | `data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_spanish_content_reviewer1_completed.csv` | False | False | missing returned CSV |
| `coverage_native_review_v03` | preferred_double_label | `english_instruction_spanish_content` | 2 | `data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_spanish_content_reviewer2_completed.csv` | False | False | missing returned CSV |
| `coverage_native_review_v03` | preferred_double_label | `hindi_english_instruction_hindi_devanagari` | 1 | `data/coverage_native_review_v03/coverage_native_review_v03_hindi_english_instruction_hindi_devanagari_reviewer1_completed.csv` | False | False | missing returned CSV |
| `coverage_native_review_v03` | preferred_double_label | `hindi_english_instruction_hindi_devanagari` | 2 | `data/coverage_native_review_v03/coverage_native_review_v03_hindi_english_instruction_hindi_devanagari_reviewer2_completed.csv` | False | False | missing returned CSV |
| `coverage_native_review_v03` | preferred_double_label | `spanish_instruction_arabic_quote` | 1 | `data/coverage_native_review_v03/coverage_native_review_v03_spanish_instruction_arabic_quote_reviewer1_completed.csv` | False | False | missing returned CSV |
| `coverage_native_review_v03` | preferred_double_label | `spanish_instruction_arabic_quote` | 2 | `data/coverage_native_review_v03/coverage_native_review_v03_spanish_instruction_arabic_quote_reviewer2_completed.csv` | False | False | missing returned CSV |
