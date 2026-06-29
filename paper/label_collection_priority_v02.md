# Label Collection Priority Audit

This no-API audit ranks the incomplete human/native label surfaces by
claim payoff and collection burden. It is a collection plan, not completed
human/native validation.

## Recommendation

Prioritize `current_model_human_audit_v02` first: it has 48 rows
across three 16-row language bundles and is the smallest label surface that
can directly support the GPT-5.x current-model headline if its completed
labels pass the pre-specified gates.

Collect `human_audit_v02` second to validate the original v0.2 scorer story.
Collect `coverage_native_review_v03` after the human audits, or in parallel
only if qualified reviewers are available for all six coverage slices; it
checks scaffold release usability but still does not create a v0.3 model
performance claim by itself.

## Summary

- Incomplete label surfaces: 3
- Reviewer-facing rows: 180
- Ready reviewer bundles: 12
- Minimum completion path: one qualified completed export per slice plus
  the matching filled roster, followed by the completed-label validator.
- Stronger path: two independent labels per item, adjudicate only
  disagreements, finalize one row per item, then rerun claim gates.
- Claim boundary: no completed human/native-validation claim is unlocked
  until finalized labels pass validators and thresholds.

## Priority Table

| Rank | Surface | Rows | Bundles | Threshold | Claim payoff | Next action |
|---:|---|---:|---:|---|---|---|
| 1 | current_model_human_audit_v02 | 48 | 3 | 44/48 pass agreements; 204/240 component agreements | native/near-native validation for the GPT-5.x current-model headline | send three 16-row current-model language bundles and collect a qualified roster |
| 2 | human_audit_v02 | 72 | 3 | 65/72 pass agreements; 306/360 component agreements | native/near-native validation for the original v0.2 automatic-scorer story | send three 24-row original v0.2 language bundles after current-model labels are underway |
| 3 | coverage_native_review_v03 | 60 | 6 | 60/60 release-usable rows | native review of the v0.3 coverage scaffold before any v0.3 benchmark-evidence claim | send six 10-row coverage-slice bundles only when qualified reviewers cover all slices |

## Slice Checklist

| Rank | Surface | Slice | Rows | Expected return file | Bundle ready |
|---:|---|---|---:|---|---|
| 1 | current_model_human_audit_v02 | ar-en | 16 | `human_audit_packet_v0.2_current_gpt5_ar-en_completed.csv` | True |
| 1 | current_model_human_audit_v02 | es-en | 16 | `human_audit_packet_v0.2_current_gpt5_es-en_completed.csv` | True |
| 1 | current_model_human_audit_v02 | hi-en | 16 | `human_audit_packet_v0.2_current_gpt5_hi-en_completed.csv` | True |
| 2 | human_audit_v02 | ar-en | 24 | `human_audit_packet_v0.2_ar-en_completed.csv` | True |
| 2 | human_audit_v02 | es-en | 24 | `human_audit_packet_v0.2_es-en_completed.csv` | True |
| 2 | human_audit_v02 | hi-en | 24 | `human_audit_packet_v0.2_hi-en_completed.csv` | True |
| 3 | coverage_native_review_v03 | arabic_instruction_arabic_filenames | 10 | `coverage_native_review_v03_arabic_instruction_arabic_filenames_completed.csv` | True |
| 3 | coverage_native_review_v03 | english_instruction_arabic_content | 10 | `coverage_native_review_v03_english_instruction_arabic_content_completed.csv` | True |
| 3 | coverage_native_review_v03 | english_instruction_hindi_content | 10 | `coverage_native_review_v03_english_instruction_hindi_content_completed.csv` | True |
| 3 | coverage_native_review_v03 | english_instruction_spanish_content | 10 | `coverage_native_review_v03_english_instruction_spanish_content_completed.csv` | True |
| 3 | coverage_native_review_v03 | hindi_english_instruction_hindi_devanagari | 10 | `coverage_native_review_v03_hindi_english_instruction_hindi_devanagari_completed.csv` | True |
| 3 | coverage_native_review_v03 | spanish_instruction_arabic_quote | 10 | `coverage_native_review_v03_spanish_instruction_arabic_quote_completed.csv` | True |

After any completed labels arrive, merge exports with
`scripts/merge_review_exports.py`, validate the finalized labels, summarize
them, then rerun `scripts/analyze_completed_label_claim_gates.py` and
`scripts/validate_completed_label_claim_gates.py` before changing paper
claims.
