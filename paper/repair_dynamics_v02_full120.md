# Repair Dynamics Analysis

Generated from `results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv`.

RTT=0 means first-turn success, RTT=1 or RTT=2 means success after one or
two standardized repair prompts, and RTT=3 means unresolved after two repair
prompts.

## RTT Distribution By Model

| Model | Condition | RTT0 | RTT1 | RTT2 | RTT3 unresolved | Mean RTT | Initial failures | Repair1/fail | Repair2 exact/fail | Unresolved/fail |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gpt-4.1 | baseline | 92 (76.7%) | 25 (20.8%) | 0 (0.0%) | 3 (2.5%) | 0.283 | 28 | 89.3% | 0.0% | 10.7% |
| gpt-4.1 | contract | 112 (93.3%) | 3 (2.5%) | 0 (0.0%) | 5 (4.2%) | 0.150 | 8 | 37.5% | 0.0% | 62.5% |
| gpt-4.1-mini | baseline | 91 (75.8%) | 26 (21.7%) | 2 (1.7%) | 1 (0.8%) | 0.275 | 29 | 89.7% | 6.9% | 3.4% |
| gpt-4.1-mini | contract | 95 (79.2%) | 23 (19.2%) | 0 (0.0%) | 2 (1.7%) | 0.242 | 25 | 92.0% | 0.0% | 8.0% |
| gpt-4.1-nano | baseline | 81 (67.5%) | 29 (24.2%) | 3 (2.5%) | 7 (5.8%) | 0.467 | 39 | 74.4% | 7.7% | 17.9% |
| gpt-4.1-nano | contract | 92 (76.7%) | 22 (18.3%) | 1 (0.8%) | 5 (4.2%) | 0.325 | 28 | 78.6% | 3.6% | 17.9% |

## Aggregate RTT Distribution By Task Family

| Condition | Task family | RTT0 | RTT1 | RTT2 | RTT3 unresolved | Mean RTT |
|---|---|---:|---:|---:|---:|---:|
| baseline | editing_preservation | 30 | 60 | 0 | 0 | 0.667 |
| baseline | output_language_inference | 90 | 0 | 0 | 0 | 0.000 |
| baseline | quote_preservation | 81 | 3 | 2 | 4 | 0.211 |
| baseline | script_register_locale | 63 | 17 | 3 | 7 | 0.489 |
| contract | editing_preservation | 63 | 27 | 0 | 0 | 0.300 |
| contract | output_language_inference | 90 | 0 | 0 | 0 | 0.000 |
| contract | quote_preservation | 82 | 6 | 1 | 1 | 0.122 |
| contract | script_register_locale | 64 | 15 | 0 | 11 | 0.533 |

## Paired RTT Movement

| Model | Mean RTT reduction | Improved | Worsened | Tied | Baseline fail -> contract pass | Baseline pass -> contract fail | Unresolved -> resolved | Resolved -> unresolved |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| gpt-4.1 | 0.133 | 20 | 2 | 98 | 20 | 0 | 0 | 2 |
| gpt-4.1-mini | 0.033 | 5 | 1 | 114 | 4 | 0 | 0 | 1 |
| gpt-4.1-nano | 0.142 | 17 | 3 | 100 | 12 | 1 | 4 | 2 |

## Interpretation

For gpt-4.1, the contract changes the distribution from 92 first-turn
successes and 28 initial failures to 112
first-turn successes and 8 initial failures. Paired RTT movement is
20 improved, 2 worsened, and 98 tied.

For gpt-4.1-nano, unresolved trajectories drop from 7 to
5, while first-turn successes rise from
81 to 92.

The mini result is intentionally modest: paired RTT movement is 5 improved,
1 worsened, and 114 tied.

A caveat remains: script/register/locale unresolved cases under the contract are 11/90,
so the prompt does not remove residual repair failures.
