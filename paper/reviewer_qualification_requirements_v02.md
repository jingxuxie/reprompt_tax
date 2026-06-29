# Reviewer Qualification Requirements

This no-API audit makes the qualification requirements for pending
human/native labels explicit before any returned labels are merged. It
does not certify completed human/native validation.

## Summary

- Surfaces checked: 3
- Reviewer qualification slots: 24
- Completed qualified rosters present: 0/3
- OpenAI API calls: 0
- Claim boundary: no human/native-validation claim is unlocked until
  completed labels and qualified rosters pass their completed-label validators.

## Surface Requirements

| Priority | Surface | Slots | Slices | Native/near-native slots | Target-language slots | Script slots | Completed roster present | Status |
|---:|---|---:|---:|---:|---:|---:|---|---|
| 1 | `current_model_human_audit_v02` | 6 | 3 | 6 | 0 | 6 | False | requirements_defined_labels_absent |
| 2 | `human_audit_v02` | 6 | 3 | 6 | 0 | 6 | False | requirements_defined_labels_absent |
| 3 | `coverage_native_review_v03` | 12 | 6 | 0 | 12 | 12 | False | requirements_defined_labels_absent |

## Slot Requirements

| Surface | Slot | Template reviewer ID | Language pair | Target content language | Native/near-native | Instruction language | Target language | Script | No conflict | Validator |
|---|---|---|---|---|---|---|---|---|---|---|
| `current_model_human_audit_v02` | `ar-en` | `replace_with_ar_en_annotator_1_id` | ar-en |  | True | not_applicable | not_applicable | True | True | `scripts/validate_completed_human_audit.py` |
| `current_model_human_audit_v02` | `ar-en` | `replace_with_ar_en_annotator_2_id` | ar-en |  | True | not_applicable | not_applicable | True | True | `scripts/validate_completed_human_audit.py` |
| `current_model_human_audit_v02` | `es-en` | `replace_with_es_en_annotator_1_id` | es-en |  | True | not_applicable | not_applicable | True | True | `scripts/validate_completed_human_audit.py` |
| `current_model_human_audit_v02` | `es-en` | `replace_with_es_en_annotator_2_id` | es-en |  | True | not_applicable | not_applicable | True | True | `scripts/validate_completed_human_audit.py` |
| `current_model_human_audit_v02` | `hi-en` | `replace_with_hi_en_annotator_1_id` | hi-en |  | True | not_applicable | not_applicable | True | True | `scripts/validate_completed_human_audit.py` |
| `current_model_human_audit_v02` | `hi-en` | `replace_with_hi_en_annotator_2_id` | hi-en |  | True | not_applicable | not_applicable | True | True | `scripts/validate_completed_human_audit.py` |
| `human_audit_v02` | `ar-en` | `replace_with_ar_en_annotator_1_id` | ar-en |  | True | not_applicable | not_applicable | True | True | `scripts/validate_completed_human_audit.py` |
| `human_audit_v02` | `ar-en` | `replace_with_ar_en_annotator_2_id` | ar-en |  | True | not_applicable | not_applicable | True | True | `scripts/validate_completed_human_audit.py` |
| `human_audit_v02` | `es-en` | `replace_with_es_en_annotator_1_id` | es-en |  | True | not_applicable | not_applicable | True | True | `scripts/validate_completed_human_audit.py` |
| `human_audit_v02` | `es-en` | `replace_with_es_en_annotator_2_id` | es-en |  | True | not_applicable | not_applicable | True | True | `scripts/validate_completed_human_audit.py` |
| `human_audit_v02` | `hi-en` | `replace_with_hi_en_annotator_1_id` | hi-en |  | True | not_applicable | not_applicable | True | True | `scripts/validate_completed_human_audit.py` |
| `human_audit_v02` | `hi-en` | `replace_with_hi_en_annotator_2_id` | hi-en |  | True | not_applicable | not_applicable | True | True | `scripts/validate_completed_human_audit.py` |
| `coverage_native_review_v03` | `arabic_instruction_arabic_filenames` | `replace_with_arabic_instruction_arabic_filenames_reviewer_1_id` | ar-ar | Arabic with English file names | not_applicable | True | True | True | True | `scripts/validate_completed_coverage_native_review_v03.py` |
| `coverage_native_review_v03` | `arabic_instruction_arabic_filenames` | `replace_with_arabic_instruction_arabic_filenames_reviewer_2_id` | ar-ar | Arabic with English file names | not_applicable | True | True | True | True | `scripts/validate_completed_coverage_native_review_v03.py` |
| `coverage_native_review_v03` | `english_instruction_arabic_content` | `replace_with_english_instruction_arabic_content_reviewer_1_id` | en-ar | Arabic | not_applicable | True | True | True | True | `scripts/validate_completed_coverage_native_review_v03.py` |
| `coverage_native_review_v03` | `english_instruction_arabic_content` | `replace_with_english_instruction_arabic_content_reviewer_2_id` | en-ar | Arabic | not_applicable | True | True | True | True | `scripts/validate_completed_coverage_native_review_v03.py` |
| `coverage_native_review_v03` | `english_instruction_hindi_content` | `replace_with_english_instruction_hindi_content_reviewer_1_id` | en-hi | Hindi | not_applicable | True | True | True | True | `scripts/validate_completed_coverage_native_review_v03.py` |
| `coverage_native_review_v03` | `english_instruction_hindi_content` | `replace_with_english_instruction_hindi_content_reviewer_2_id` | en-hi | Hindi | not_applicable | True | True | True | True | `scripts/validate_completed_coverage_native_review_v03.py` |
| `coverage_native_review_v03` | `english_instruction_spanish_content` | `replace_with_english_instruction_spanish_content_reviewer_1_id` | en-es | Spanish | not_applicable | True | True | True | True | `scripts/validate_completed_coverage_native_review_v03.py` |
| `coverage_native_review_v03` | `english_instruction_spanish_content` | `replace_with_english_instruction_spanish_content_reviewer_2_id` | en-es | Spanish | not_applicable | True | True | True | True | `scripts/validate_completed_coverage_native_review_v03.py` |
| `coverage_native_review_v03` | `hindi_english_instruction_hindi_devanagari` | `replace_with_hindi_english_instruction_hindi_devanagari_reviewer_1_id` | hi-hi | Hindi | not_applicable | True | True | True | True | `scripts/validate_completed_coverage_native_review_v03.py` |
| `coverage_native_review_v03` | `hindi_english_instruction_hindi_devanagari` | `replace_with_hindi_english_instruction_hindi_devanagari_reviewer_2_id` | hi-hi | Hindi | not_applicable | True | True | True | True | `scripts/validate_completed_coverage_native_review_v03.py` |
| `coverage_native_review_v03` | `spanish_instruction_arabic_quote` | `replace_with_spanish_instruction_arabic_quote_reviewer_1_id` | es-ar | Arabic | not_applicable | True | True | True | True | `scripts/validate_completed_coverage_native_review_v03.py` |
| `coverage_native_review_v03` | `spanish_instruction_arabic_quote` | `replace_with_spanish_instruction_arabic_quote_reviewer_2_id` | es-ar | Arabic | not_applicable | True | True | True | True | `scripts/validate_completed_coverage_native_review_v03.py` |
