# Experiment Ledger

Generated from saved paper-facing score and judge-audit artifacts.

This ledger reports API response rows and saved token usage only. It does
not estimate dollar cost because provider prices change over time. Historical
diagnostic shards are excluded to avoid double-counting rows that were merged
into the paper-facing score files.

## Summary

| Metric | Value |
|---|---:|
| paper_facing_artifacts | 4 |
| api_response_rows | 1290 |
| model_response_rows | 1218 |
| judge_response_rows | 72 |
| trajectories_or_judged_rows | 1032 |
| input_tokens | 190463 |
| output_tokens | 38368 |
| total_tokens | 228831 |
| created_at_start | 2026-06-28T01:15:43.155159+00:00 |
| created_at_end | 2026-06-28T05:50:04.200919+00:00 |

## By Artifact

| Label | Kind | API rows | First-turn rows | Trajectories/judged rows | Input tokens | Output tokens | Total tokens |
|---|---|---:|---:|---:|---:|---:|---:|
| main_evaluation | model_responses | 917 | 720 | 720 | 126306 | 25737 | 152043 |
| prompt_control | model_responses | 155 | 120 | 120 | 23494 | 3968 | 27462 |
| prompt_ablation_content_preservation | model_responses | 146 | 120 | 120 | 20056 | 3324 | 23380 |
| judge_audit | judge_audit | 72 | 72 | 72 | 20607 | 5339 | 25946 |

## Model Response Usage

| Artifact | Model | Condition | API rows | First-turn rows | Trajectories | Input tokens | Output tokens | Total tokens |
|---|---|---|---:|---:|---:|---:|---:|---:|
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

## Interpretation

The paper-facing package contains 1,218 saved model-response API rows
for the main evaluation plus nano prompt-control and prompt-ablation diagnostics,
and 72 saved judge-audit API rows. The main evaluation covers
720 first-turn trajectories; additional rows are standardized
repair turns emitted only when the first turn failed. Token counts are
provider-reported usage stored with each saved response.
