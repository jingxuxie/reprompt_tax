# Sentinel Suite v0.2

This no-API artifact selects a compact 24-item diagnostic suite from the
paper-facing 120-item stress benchmark. It is intended for future fast
model checks and reviewer inspection, not as a replacement for the full
benchmark or native/near-native validation.

## Selection Rule

The suite first selects the top-ranked item from each language-pair/task-family
cell so every stratum is represented, then fills the remaining slots by
global saved full-run diagnostic density. The score prioritizes GPT-5.5
contract residuals, GPT-5.x contract failures, contract regressions,
contract fixes, remaining contract failures, unresolved trajectories, and
baseline first-turn failures. Ties are broken by item ID, making the suite
deterministic.

## Coverage Summary

| Signal | Full set | Sentinel set | Coverage |
|---|---:|---:|---:|
| Baseline first-turn failure pairs | 142 | 78 | 54.9% |
| Contract fix pairs | 67 | 26 | 38.8% |
| Contract regression pairs | 6 | 4 | 66.7% |
| Contract first-turn failure pairs | 81 | 56 | 69.1% |
| Unresolved trajectory flags | 34 | 26 | 76.5% |
| GPT-5.x contract failure pairs | 20 | 19 | 95.0% |
| GPT-5.5 contract residual items | 2 | 2 | 100.0% |
| GPT-5.4-mini contract-regression items | 5 | 4 | 80.0% |
| Language-family cells with at least one selected item | 12 | 12 | 100.0% |

## Selected Items

| Item | Language | Family | Score | Fixes | Regressions | Contract failures | Rationale |
|---|---|---|---:|---:|---:|---:|---|
| `ar_en_SA_003` | ar-en | editing_preservation | 32 | 4 | 0 | 1 | 1 GPT-5.x contract fail pairs; 4 contract fixes |
| `ar_en_SA_001` | ar-en | editing_preservation | 25 | 5 | 0 | 0 | 5 contract fixes |
| `ar_en_SB_001` | ar-en | output_language_inference | 0 | 0 | 0 | 0 | balanced cell representative |
| `ar_en_SC_001` | ar-en | quote_preservation | 6 | 0 | 0 | 1 | 1 unresolved trajectory flags |
| `ar_en_SD_006` | ar-en | script_register_locale | 37 | 0 | 1 | 4 | 1 GPT-5.x contract fail pairs; 1 contract regressions; 4 unresolved trajectory flags |
| `ar_en_SD_008` | ar-en | script_register_locale | 36 | 0 | 0 | 4 | 1 GPT-5.x contract fail pairs; 6 unresolved trajectory flags |
| `ar_en_SD_007` | ar-en | script_register_locale | 29 | 0 | 1 | 4 | 1 GPT-5.x contract fail pairs; 1 contract regressions |
| `es_en_SA_004` | es-en | editing_preservation | 47 | 1 | 0 | 4 | gpt-5.5 contract residual; 2 GPT-5.x contract fail pairs; 1 contract fixes |
| `es_en_SA_009` | es-en | editing_preservation | 47 | 1 | 0 | 4 | gpt-5.5 contract residual; 2 GPT-5.x contract fail pairs; 1 contract fixes |
| `es_en_SA_001` | es-en | editing_preservation | 31 | 3 | 0 | 2 | 1 GPT-5.x contract fail pairs; 3 contract fixes |
| `es_en_SA_002` | es-en | editing_preservation | 30 | 2 | 0 | 3 | 1 GPT-5.x contract fail pairs; 2 contract fixes |
| `es_en_SA_003` | es-en | editing_preservation | 30 | 2 | 0 | 3 | 1 GPT-5.x contract fail pairs; 2 contract fixes |
| `es_en_SA_006` | es-en | editing_preservation | 30 | 2 | 0 | 3 | 1 GPT-5.x contract fail pairs; 2 contract fixes |
| `es_en_SA_007` | es-en | editing_preservation | 30 | 2 | 0 | 3 | 1 GPT-5.x contract fail pairs; 2 contract fixes |
| `es_en_SA_008` | es-en | editing_preservation | 30 | 2 | 0 | 3 | 1 GPT-5.x contract fail pairs; 2 contract fixes |
| `es_en_SA_010` | es-en | editing_preservation | 29 | 1 | 0 | 4 | 1 GPT-5.x contract fail pairs; 1 contract fixes |
| `es_en_SB_001` | es-en | output_language_inference | 0 | 0 | 0 | 0 | balanced cell representative |
| `es_en_SC_001` | es-en | quote_preservation | 0 | 0 | 0 | 0 | balanced cell representative |
| `es_en_SD_008` | es-en | script_register_locale | 38 | 0 | 0 | 4 | 1 GPT-5.x contract fail pairs; 7 unresolved trajectory flags |
| `es_en_SD_010` | es-en | script_register_locale | 29 | 0 | 1 | 4 | 1 GPT-5.x contract fail pairs; 1 contract regressions |
| `hi_en_SA_001` | hi-en | editing_preservation | 0 | 0 | 0 | 0 | balanced cell representative |
| `hi_en_SB_001` | hi-en | output_language_inference | 7 | 1 | 0 | 0 | 1 contract fixes; 1 unresolved trajectory flags |
| `hi_en_SC_003` | hi-en | quote_preservation | 19 | 0 | 1 | 1 | 1 GPT-5.x contract fail pairs; 1 contract regressions; 1 unresolved trajectory flags |
| `hi_en_SD_008` | hi-en | script_register_locale | 36 | 0 | 0 | 4 | 1 GPT-5.x contract fail pairs; 6 unresolved trajectory flags |

## Interpretation

The 24-item suite covers all 12 language-family cells and captures 26 of 67 contract fix pairs (38.8%). It also captures 4 of 6 contract regression pairs and all 2 GPT-5.5 contract residual items.

Use `data/stress_v02_sentinel24_ids.txt` as an item-id file for future
smoke runs when a full 120-item model refresh is too expensive. Any
paper-facing model claim should still be confirmed on the full benchmark
and, for cultural/register claims, by completed qualified human/native labels.
