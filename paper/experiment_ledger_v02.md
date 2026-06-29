# Experiment Ledger

Generated from saved score, smoke, and judge-audit artifacts.

This ledger reports API response rows and saved token usage only. It does
not estimate dollar cost because provider prices change over time. Historical
diagnostic shards are excluded to avoid double-counting rows that were merged
into aggregate score files. The v0.3 pilot and GPT-5.5 smoke are included for API accounting
but is not a paper-facing benchmark result.

## Summary

| Metric | Value |
|---|---:|
| tracked_api_artifacts | 8 |
| api_response_rows | 1504 |
| model_response_rows | 1288 |
| repair_variant_response_rows | 72 |
| judge_response_rows | 144 |
| trajectories_or_judged_rows | 1236 |
| input_tokens | 229646 |
| output_tokens | 56284 |
| total_tokens | 285930 |
| created_at_start | 2026-06-28T01:15:43.155159+00:00 |
| created_at_end | 2026-06-29T02:42:32.020621+00:00 |

## By Artifact

| Label | Kind | API rows | First-turn rows | Trajectories/judged rows | Input tokens | Output tokens | Total tokens |
|---|---|---:|---:|---:|---:|---:|---:|
| main_evaluation | model_responses | 917 | 720 | 720 | 126306 | 25737 | 152043 |
| prompt_control | model_responses | 155 | 120 | 120 | 23494 | 3968 | 27462 |
| prompt_ablation_content_preservation | model_responses | 146 | 120 | 120 | 20056 | 3324 | 23380 |
| coverage_pilot_v03_gpt54mini | model_responses | 58 | 48 | 48 | 8007 | 1958 | 9965 |
| coverage_smoke_v03_gpt55 | model_responses | 12 | 12 | 12 | 1632 | 870 | 2502 |
| judge_audit | judge_audit | 72 | 72 | 72 | 20607 | 5339 | 25946 |
| judge_refresh_gpt55 | judge_audit | 72 | 72 | 72 | 20535 | 10512 | 31047 |
| repair_realism_editing_baseline24 | repair_variant_responses | 72 | 0 | 72 | 9009 | 4576 | 13585 |

## Model Response Usage

| Artifact | Model | Condition | API rows | First-turn rows | Trajectories | Input tokens | Output tokens | Total tokens |
|---|---|---|---:|---:|---:|---:|---:|---:|
| coverage_pilot_v03_gpt54mini | gpt-5.4-mini | baseline | 32 | 24 | 24 | 2373 | 1340 | 3713 |
| coverage_pilot_v03_gpt54mini | gpt-5.4-mini | contract | 26 | 24 | 24 | 5634 | 618 | 6252 |
| coverage_smoke_v03_gpt55 | gpt-5.5 | baseline | 6 | 6 | 6 | 345 | 480 | 825 |
| coverage_smoke_v03_gpt55 | gpt-5.5 | contract | 6 | 6 | 6 | 1287 | 390 | 1677 |
| main_evaluation | gpt-4.1 | baseline | 151 | 120 | 120 | 10029 | 5895 | 15924 |
| main_evaluation | gpt-4.1 | contract | 134 | 120 | 120 | 28516 | 2519 | 31035 |
| main_evaluation | gpt-4.1-mini | baseline | 154 | 120 | 120 | 9935 | 4834 | 14769 |
| main_evaluation | gpt-4.1-mini | contract | 150 | 120 | 120 | 32489 | 3548 | 36037 |
| main_evaluation | gpt-4.1-nano | baseline | 173 | 120 | 120 | 11571 | 5504 | 17075 |
| main_evaluation | gpt-4.1-nano | contract | 155 | 120 | 120 | 33766 | 3437 | 37203 |
| prompt_ablation_content_preservation | gpt-4.1-nano | content_preservation | 146 | 120 | 120 | 20056 | 3324 | 23380 |
| prompt_control | gpt-4.1-nano | generic_helpfulness | 155 | 120 | 120 | 23494 | 3968 | 27462 |

## Judge Audit Usage

| Artifact | Judge model | API rows | Input tokens | Output tokens | Total tokens |
|---|---|---:|---:|---:|---:|
| judge_audit | gpt-4.1 | 72 | 20607 | 5339 | 25946 |
| judge_refresh_gpt55 | gpt-5.5 | 72 | 20535 | 10512 | 31047 |

## Repair Variant Usage

| Artifact | Model | Repair variant | API rows | Input tokens | Output tokens | Total tokens |
|---|---|---|---:|---:|---:|---:|
| repair_realism_editing_baseline24 | gpt-4.1 | explicit_contract | 8 | 1157 | 669 | 1826 |
| repair_realism_editing_baseline24 | gpt-4.1 | frustrated_dont_translate | 8 | 1109 | 633 | 1742 |
| repair_realism_editing_baseline24 | gpt-4.1 | terse_keep_english | 8 | 1117 | 671 | 1788 |
| repair_realism_editing_baseline24 | gpt-4.1-mini | explicit_contract | 8 | 1041 | 492 | 1533 |
| repair_realism_editing_baseline24 | gpt-4.1-mini | frustrated_dont_translate | 8 | 993 | 508 | 1501 |
| repair_realism_editing_baseline24 | gpt-4.1-mini | terse_keep_english | 8 | 1001 | 548 | 1549 |
| repair_realism_editing_baseline24 | gpt-4.1-nano | explicit_contract | 8 | 893 | 365 | 1258 |
| repair_realism_editing_baseline24 | gpt-4.1-nano | frustrated_dont_translate | 8 | 845 | 341 | 1186 |
| repair_realism_editing_baseline24 | gpt-4.1-nano | terse_keep_english | 8 | 853 | 349 | 1202 |

## Interpretation

The tracked artifact package contains 1,288 saved model-response API rows
for the main evaluation plus nano prompt-control, prompt-ablation, v0.3 pilot, and GPT-5.5 smoke diagnostics,
72 repair-variant API rows, and 144 saved
judge-audit API rows. The main evaluation covers
720 first-turn trajectories; additional rows are standardized
repair turns emitted only when the first turn failed. Token counts are
provider-reported usage stored with each saved response.
