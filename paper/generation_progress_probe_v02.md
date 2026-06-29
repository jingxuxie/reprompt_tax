# Generation Progress Probe

This artifact compares item-level first-turn failures across the saved
GPT-4.1-family and GPT-5.x-family full 120-item runs. It is a progress
probe over one benchmark, not a broad model leaderboard or population-level
claim.

## Generation Summary

| Generation | Condition | Model-item pairs | Failure pairs | Any-fail items | All-model fail items | Unresolved pairs |
|---|---|---:|---:|---:|---:|---:|
| GPT-4.1 family | baseline | 360 | 96 (26.7%) | 40 | 27 | 11 |
| GPT-4.1 family | contract | 360 | 61 (16.9%) | 35 | 8 | 12 |
| GPT-5.x family | baseline | 240 | 46 (19.2%) | 26 | 20 | 5 |
| GPT-5.x family | contract | 240 | 20 (8.3%) | 18 | 2 | 6 |

## Cross-Generation Item Movement

| Category | Items | Editing | Output-language | Quote | Script/register/locale |
|---|---:|---:|---:|---:|---:|
| gpt41_baseline_any_fail_items | 40 | 20 | 0 | 9 | 11 |
| gpt41_baseline_all_fail_items | 27 | 20 | 0 | 0 | 7 |
| gpt41_contract_all_fail_items | 8 | 1 | 0 | 0 | 7 |
| gpt5x_baseline_both_fail_items | 20 | 20 | 0 | 0 | 0 |
| gpt5x_contract_both_fail_items | 2 | 2 | 0 | 0 | 0 |
| gpt41_all_baseline_fail_gpt55_baseline_pass | 7 | 0 | 0 | 0 | 7 |
| gpt41_any_baseline_fail_gpt55_baseline_pass | 19 | 0 | 0 | 9 | 10 |
| gpt41_any_baseline_fail_gpt55_contract_pass | 38 | 18 | 0 | 9 | 11 |
| gpt41_all_contract_fail_gpt55_contract_pass | 8 | 1 | 0 | 0 | 7 |

## Interpretation

Under baseline prompting, GPT-4.1-family models fail 96/360 model-item pairs (26.7%), with 40/120 items failing for at least one model and 27/120 failing for all three. GPT-5.x-family baseline runs lower the normalized failure-pair rate to 46/240 (19.2%), with 26/120 any-fail items and 20/120 both-model fail items.

Under the contract, the GPT-5.x-family failure-pair rate falls to 20/240 (8.3%), compared with 61/360 (16.9%) for GPT-4.1-family contract rows. The current-family all-model-fail set shrinks to 2 items.

`gpt-5.5` baseline passes 7 of the 27 items that all GPT-4.1-family baselines fail, and passes 19 of the 40 items where at least one GPT-4.1-family baseline fails.
With the contract, `gpt-5.5` passes 38 of those 40 older-family baseline-hard items and all 8 items that all GPT-4.1-family contract rows fail.

The two items that both current models still fail under the contract are `es_en_SA_004`, `es_en_SA_009`. Both are Spanish-English editing-preservation rows.
This supports the progress-probe framing: the benchmark distinguishes model generations and prompt conditions while retaining a small residual hard set.
