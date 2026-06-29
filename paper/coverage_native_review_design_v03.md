# v0.3 Coverage Native-Review Design

This report analyzes the launch packet for native/near-native review of
the 60 synthetic v0.3 rows. It is launch-ready but not completed native validation.
Do not claim native validation has been completed from this artifact.

## Summary

| Metric | Value |
|---|---:|
| review_rows | 60 |
| coverage_slices | 6 |
| language_pairs | 6 |
| instruction_languages | 4 |
| content_languages | 4 |
| task_families | 1 |
| rows_per_slice_min | 10 |
| rows_per_slice_max | 10 |
| review_fields_blank | True |
| rows_requiring_native_review | 60 |
| validation_status | launch_ready_but_not_completed_native_validation |

## Coverage Slices

| Slice | Language pair | Instruction | Content | Rows | Preserve rows | Preserve spans |
|---|---|---|---|---:|---:|---:|
| arabic_instruction_arabic_filenames | ar-ar | Arabic | Arabic with English file names | 10 | 10 | 20 |
| english_instruction_arabic_content | en-ar | English | Arabic | 10 | 10 | 20 |
| english_instruction_hindi_content | en-hi | English | Hindi | 10 | 10 | 20 |
| english_instruction_spanish_content | en-es | English | Spanish | 10 | 10 | 20 |
| hindi_english_instruction_hindi_devanagari | hi-hi | Hindi/English code-switched | Hindi | 10 | 10 | 20 |
| spanish_instruction_arabic_quote | es-ar | Spanish | Arabic | 10 | 10 | 20 |

## Target Content Languages

| Content language | Rows | Preserve rows | Preserve spans | Known-bad rows |
|---|---:|---:|---:|---:|
| Arabic | 20 | 20 | 40 | 20 |
| Arabic with English file names | 10 | 10 | 20 | 10 |
| Hindi | 20 | 20 | 40 | 20 |
| Spanish | 10 | 10 | 20 | 10 |

## Interpretation

The packet gives reviewers one row per synthetic v0.3 item and keeps all
review fields blank. It is designed to collect prompt clarity, target-language
naturalness, script expectation, preservation-span, known-bad-output, and
release-usability judgments. Completed reviewer labels and a qualified roster
are still required before v0.3 can support paper-facing benchmark claims.
