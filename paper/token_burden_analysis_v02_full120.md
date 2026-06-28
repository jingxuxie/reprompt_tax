# Token-Burden Analysis

Generated from `results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl`.

This supplement reports absolute token burden in addition to the token-tax
ratio used in the main paper. Tokens are the API usage counts saved with
each response. For unresolved trajectories, totals include all three turns.

## By Model And Condition

| Model | Condition | Mean first-turn tokens | Mean total tokens | Mean extra tokens | Mean token tax | Total tokens |
|---|---|---:|---:|---:|---:|---:|
| gpt-4.1 | baseline | 81.5 | 132.7 | 51.2 | 1.43x | 15924 |
| gpt-4.1 | contract | 223.4 | 256.3 | 32.9 | 1.13x | 30754 |
| gpt-4.1-mini | baseline | 76.8 | 120.9 | 44.1 | 1.43x | 14510 |
| gpt-4.1-mini | contract | 227.4 | 293.2 | 65.7 | 1.27x | 35179 |
| gpt-4.1-nano | baseline | 80.2 | 139.3 | 59.0 | 1.69x | 16711 |
| gpt-4.1-nano | contract | 226.9 | 308.1 | 81.2 | 1.34x | 36971 |

## Paired Baseline Minus Contract Effects

| Model | Mean total tokens | Mean extra tokens | Mean token tax | Sum total tokens |
|---|---:|---:|---:|---:|
| gpt-4.1 | -123.6 | 18.3 | 0.30x | -14830 |
| gpt-4.1-mini | -172.2 | -21.6 | 0.16x | -20669 |
| gpt-4.1-nano | -168.8 | -22.2 | 0.35x | -20260 |

Positive values mean the contract uses fewer tokens than baseline; negative
values mean the longer contract prompt increases absolute token use. The
contract lowers token-tax ratios for all three models, but absolute total
tokens increase because the system prompt is longer. This is why the main
paper treats token tax as a repair-burden metric rather than as an API-cost
claim.

