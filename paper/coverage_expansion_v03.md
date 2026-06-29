# Coverage Expansion v0.3 Scaffold

Generated from `data/benchmark_stress_v0.3_expansion.jsonl`.

This is a synthetic scaffold for non-English target-content editing coverage.
It is not paper-facing model result evidence, and it requires native validation before claims.
The v0.2 benchmark remains the original paper-facing stress pilot.

## Summary

| Metric | Value |
|---|---:|
| coverage_rows | 60 |
| benchmark_version | v0.3-expansion-scaffold |
| validation_status | synthetic_scaffold_requires_native_validation |
| coverage_slices | 6 |
| language_pairs | 6 |
| task_families | 1 |
| unique_user_prompts | 60 |
| normalized_duplicate_prompts | 0 |
| rows_with_preservation_spans | 60 |
| total_preservation_spans | 120 |
| rows_requiring_native_validation | 60 |
| model_result_rows | 0 |
| privacy_marker_hits | 0 |
| min_prompt_words | 21 |
| mean_prompt_words | 26.4 |
| max_prompt_words | 32 |

## Coverage Slices

| Slice | Pair | Instruction | Content | Expected response | Script | n | Preservation spans |
|---|---|---|---|---|---|---:|---:|
| arabic_instruction_arabic_filenames | ar-ar | Arabic | Arabic with English file names | Arabic | Arabic | 10 | 20 |
| english_instruction_arabic_content | en-ar | English | Arabic | Arabic | Arabic | 10 | 20 |
| english_instruction_hindi_content | en-hi | English | Hindi | Hindi | Devanagari | 10 | 20 |
| english_instruction_spanish_content | en-es | English | Spanish | Spanish | Latin | 10 | 20 |
| hindi_english_instruction_hindi_devanagari | hi-hi | Hindi/English code-switched | Hindi | Hindi | Devanagari | 10 | 20 |
| spanish_instruction_arabic_quote | es-ar | Spanish | Arabic | Arabic | Arabic | 10 | 20 |

## Claim Boundary

- Treat this as benchmark-construction scaffolding only.
- Do not merge these rows into headline v0.2 results without a native-speaker review pass.
- Do not report model performance on this expansion until model outputs, scoring, and audit artifacts are generated.
