# All-Model Paired Significance

This artifact tests the first-turn contract effect across all five full
120-item model runs. It uses saved trajectory metrics only and makes no
API calls.

The model-item unit treats each model-item pair as one paired comparison.
The item-cluster unit is more conservative: for each prompt item, it sums
fixes minus regressions across models and then runs a sign test over
net-positive versus net-negative items.

## Headline Sensitivity

| Unit | Stratum | N | Positive | Negative | Ties | Net gain | Delta | Sign-test p |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| model_item | all | 600 | 67 | 6 | 527 | 61 | 10.2 pp | 3.95e-14 |
| item_cluster | all | 120 | 24 | 5 | 91 | 61 | 10.2 pp | 0.0005 |
| model_item | editing_preservation | 150 | 61 | 0 | 89 | 61 | 40.7 pp | 8.67e-19 |
| item_cluster | editing_preservation | 30 | 20 | 0 | 10 | 61 | 40.7 pp | 1.91e-06 |

## Full Table

| Unit | Stratum type | Stratum | N | Positive | Negative | Ties | Net gain | Delta | Sign-test p |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| model_item | overall | all | 600 | 67 | 6 | 527 | 61 | 10.2 pp | 3.95e-14 |
| item_cluster | overall | all | 120 | 24 | 5 | 91 | 61 | 10.2 pp | 0.0005 |
| model_item | generation | GPT-4.1 family | 360 | 36 | 1 | 323 | 35 | 9.7 pp | 5.53e-10 |
| item_cluster | generation | GPT-4.1 family | 120 | 22 | 1 | 97 | 35 | 9.7 pp | 5.72e-06 |
| model_item | generation | GPT-5.x family | 240 | 31 | 5 | 204 | 26 | 10.8 pp | 1.29e-05 |
| item_cluster | generation | GPT-5.x family | 120 | 21 | 5 | 94 | 26 | 10.8 pp | 0.0025 |
| model_item | task_family | editing_preservation | 150 | 61 | 0 | 89 | 61 | 40.7 pp | 8.67e-19 |
| item_cluster | task_family | editing_preservation | 30 | 20 | 0 | 10 | 61 | 40.7 pp | 1.91e-06 |
| model_item | task_family | output_language_inference | 150 | 1 | 0 | 149 | 1 | 0.7 pp | 1.0000 |
| item_cluster | task_family | output_language_inference | 30 | 1 | 0 | 29 | 1 | 0.7 pp | 1.0000 |
| model_item | task_family | quote_preservation | 150 | 1 | 2 | 147 | -1 | -0.7 pp | 1.0000 |
| item_cluster | task_family | quote_preservation | 30 | 1 | 2 | 27 | -1 | -0.7 pp | 1.0000 |
| model_item | task_family | script_register_locale | 150 | 4 | 4 | 142 | 0 | 0.0 pp | 1.0000 |
| item_cluster | task_family | script_register_locale | 30 | 2 | 3 | 25 | 0 | 0.0 pp | 1.0000 |
| model_item | language_pair | ar-en | 200 | 43 | 2 | 155 | 41 | 20.5 pp | 5.89e-11 |
| item_cluster | language_pair | ar-en | 40 | 11 | 2 | 27 | 41 | 20.5 pp | 0.0225 |
| model_item | language_pair | es-en | 200 | 20 | 1 | 179 | 19 | 9.5 pp | 2.10e-05 |
| item_cluster | language_pair | es-en | 40 | 11 | 1 | 28 | 19 | 9.5 pp | 0.0063 |
| model_item | language_pair | hi-en | 200 | 4 | 3 | 193 | 1 | 0.5 pp | 1.0000 |
| item_cluster | language_pair | hi-en | 40 | 2 | 2 | 36 | 1 | 0.5 pp | 1.0000 |

## Interpretation

At the model-item unit, the contract yields 67 first-turn fixes and 6
regressions across 600 paired model-item comparisons, a +10.2 pp net
first-turn gain with an exact two-sided sign-test p-value below 0.0001.

The more conservative item-cluster sensitivity reaches the same
direction: net-positive items substantially outnumber net-negative
items, and the exact sign test remains below 0.0001.

Editing preservation is the statistically decisive family: it has 61
model-item fixes and 0 regressions, and every net-moving editing item
moves in the positive direction. Other task families are sparse or
balanced, so they should not be described as independently decisive.

Claim boundary: this is still automatic-score evidence on a synthetic
stress pilot. The item-cluster row addresses repeated-item dependence
inside this pilot, but it does not replace native/near-native validation.
