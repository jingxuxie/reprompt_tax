# Item-Consistency Analysis

Generated from `results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv`. This diagnostic aggregates over the
three evaluated models to separate systematic hard items from scattered
single-model failures. It is item-level evidence for the stress pilot, not
a population-level claim.

## Overall

| Metric | Items | Share |
|---|---:|---:|
| Baseline all-model pass | 80 | 66.7% |
| Baseline any-model fail | 40 | 33.3% |
| Baseline all-model fail | 27 | 22.5% |
| Contract all-model pass | 85 | 70.8% |
| Contract any-model fail | 35 | 29.2% |
| Contract all-model fail | 8 | 6.7% |
| Fewer failing models under contract | 22 | 18.3% |
| More failing models under contract | 1 | 0.8% |
| Lower mean RTT under contract | 28 | 23.3% |
| Contract has any unresolved model | 6 | 5.0% |

## By Task Family

| Task family | Items | Baseline any fail | Contract any fail | Baseline all fail | Contract all fail | Fewer failing models | More failing models |
|---|---:|---:|---:|---:|---:|---:|---:|
| Editing preservation | 30 | 20 (66.7%) | 16 (53.3%) | 20 | 1 | 19 | 0 |
| Output-language inference | 30 | 0 (0.0%) | 0 (0.0%) | 0 | 0 | 0 | 0 |
| Quote preservation | 30 | 9 (30.0%) | 8 (26.7%) | 0 | 0 | 1 | 0 |
| Script/register/locale | 30 | 11 (36.7%) | 11 (36.7%) | 7 | 7 | 2 | 1 |

## Hardest Residual Items

| Item | Language | Family | Baseline fail models | Contract fail models | Reduction | Contract failure models | Contract unresolved models | RTT reduction |
|---|---|---|---:|---:|---:|---|---|---:|
| ar_en_SD_008 | ar-en | Script/register/locale | 3 | 3 | 0 | gpt-4.1;gpt-4.1-mini;gpt-4.1-nano | gpt-4.1;gpt-4.1-mini;gpt-4.1-nano | -0.333 |
| es_en_SD_008 | es-en | Script/register/locale | 3 | 3 | 0 | gpt-4.1;gpt-4.1-mini;gpt-4.1-nano | gpt-4.1;gpt-4.1-mini;gpt-4.1-nano | -0.333 |
| ar_en_SD_006 | ar-en | Script/register/locale | 3 | 3 | 0 | gpt-4.1;gpt-4.1-mini;gpt-4.1-nano | gpt-4.1;gpt-4.1-nano | -0.667 |
| hi_en_SD_008 | hi-en | Script/register/locale | 3 | 3 | 0 | gpt-4.1;gpt-4.1-mini;gpt-4.1-nano | gpt-4.1;gpt-4.1-nano | 0.333 |
| ar_en_SD_010 | ar-en | Script/register/locale | 3 | 3 | 0 | gpt-4.1;gpt-4.1-mini;gpt-4.1-nano | gpt-4.1 | -0.667 |
| es_en_SA_010 | es-en | Editing preservation | 3 | 3 | 0 | gpt-4.1;gpt-4.1-mini;gpt-4.1-nano | none | 0.000 |
| ar_en_SD_007 | ar-en | Script/register/locale | 3 | 3 | 0 | gpt-4.1;gpt-4.1-mini;gpt-4.1-nano | none | 0.000 |
| es_en_SD_010 | es-en | Script/register/locale | 3 | 3 | 0 | gpt-4.1;gpt-4.1-mini;gpt-4.1-nano | none | 0.000 |
| ar_en_SA_004 | ar-en | Editing preservation | 3 | 2 | 1 | gpt-4.1-mini;gpt-4.1-nano | none | 0.333 |
| es_en_SA_002 | es-en | Editing preservation | 3 | 2 | 1 | gpt-4.1-mini;gpt-4.1-nano | none | 0.333 |
| es_en_SA_003 | es-en | Editing preservation | 3 | 2 | 1 | gpt-4.1-mini;gpt-4.1-nano | none | 0.333 |
| es_en_SA_004 | es-en | Editing preservation | 3 | 2 | 1 | gpt-4.1-mini;gpt-4.1-nano | none | 0.333 |

## Interpretation

The stress set contains both systematic and model-specific failures. Under
baseline prompting, 40/120 items fail for at least
one model and 27/120 fail for all three models.
The contract shifts the distribution but does not eliminate hard cases:
35/120 items still fail for at least one model,
while 8/120 fail for all three models.
Fewer models fail under the contract on 22/120
items, while more models fail on 1/120.
This supports the conservative claim boundary: the mitigation reduces
interaction burden on the pilot, but residual item-level failures remain.
