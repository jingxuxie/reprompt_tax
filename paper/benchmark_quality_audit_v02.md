# Benchmark Quality Audit

Generated from `data/benchmark_stress_v0.2.jsonl`.

This audit checks release-facing benchmark hygiene: balance, duplicate
prompts, scoring-marker coverage, preservation-span coverage, prompt
lengths, and privacy-like markers. It is not a substitute for native
speaker validation of semantic or register judgments.

## Summary

| Metric | Value |
|---|---:|
| benchmark_rows | 120 |
| language_pairs | 3 |
| task_families | 4 |
| stress_tags | 4 |
| unique_user_prompts | 120 |
| normalized_duplicate_prompts | 0 |
| rows_with_required_markers | 120 |
| rows_with_known_bad_outputs | 120 |
| rows_with_forbidden_markers | 60 |
| rows_with_preservation_spans | 60 |
| total_preservation_spans | 99 |
| total_forbidden_markers | 300 |
| privacy_marker_hits | 0 |
| min_prompt_words | 13 |
| mean_prompt_words | 22.4 |
| max_prompt_words | 35 |

## By Task Family

| Family | n | Required markers | Known-bad outputs | Forbidden markers | Rows with preservation spans | Total preservation spans | Mean prompt words |
|---|---:|---:|---:|---:|---:|---:|---:|
| editing_preservation | 30 | 30 | 30 | 30 | 0 | 0 | 22.6 |
| output_language_inference | 30 | 30 | 30 | 0 | 0 | 0 | 15.6 |
| quote_preservation | 30 | 30 | 30 | 0 | 30 | 60 | 21.3 |
| script_register_locale | 30 | 30 | 30 | 30 | 30 | 39 | 30.2 |

## By Language Pair

| Language pair | n | Unique prompts | Rows with preservation spans | Mean prompt words |
|---|---:|---:|---:|---:|
| ar-en | 40 | 40 | 20 | 21.6 |
| es-en | 40 | 40 | 20 | 22.9 |
| hi-en | 40 | 40 | 20 | 22.9 |

## Stress Tags

| Stress tag | n |
|---|---:|
| correction_only | 30 |
| implicit_content_language | 30 |
| literal_locale_span | 30 |
| translatable_quoted_heading | 30 |

## Interpretation

The released stress pilot is balanced across the planned 3 x 4 design,
contains no exact or normalized duplicate user prompts, and contains no
email, URL, phone-like, SSN-like, or placeholder privacy markers under
the audit regexes. All rows include required scoring markers and
known-bad-output notes. Preservation spans are intentionally present
only in quote-preservation and script/register/locale items.
