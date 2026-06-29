# All-Model Clustered Uncertainty

This artifact estimates item-cluster bootstrap intervals for the
first-turn contract effect across all five full 120-item runs. It uses
saved trajectory metrics only and makes no API calls. The bootstrap
resamples prompt items, keeping all selected model rows for each item,
so it is a repeated-prompt sensitivity check rather than a population
confidence interval.

## Cluster Bootstrap Table

| Stratum type | Stratum | Items | Pairs | Baseline FTGA | Contract FTGA | Delta, 95% interval | Net-positive items | Net-negative items |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| overall | all | 120 | 600 | 76.3% | 86.5% | +10.2 pp [+5.8, +15.0] | 24 | 5 |
| generation | GPT-4.1 family | 120 | 360 | 73.3% | 83.1% | +9.7 pp [+5.6, +14.4] | 22 | 1 |
| generation | GPT-5.x family | 120 | 240 | 80.8% | 91.7% | +10.8 pp [+5.4, +16.7] | 21 | 5 |
| task_family | editing_preservation | 30 | 150 | 33.3% | 74.0% | +40.7 pp [+28.0, +53.3] | 20 | 0 |
| task_family | output_language_inference | 30 | 150 | 99.3% | 100.0% | +0.7 pp [+0.0, +2.0] | 1 | 0 |
| task_family | quote_preservation | 30 | 150 | 94.0% | 93.3% | -0.7 pp [-2.7, +1.3] | 1 | 2 |
| task_family | script_register_locale | 30 | 150 | 78.7% | 78.7% | +0.0 pp [-3.3, +4.0] | 2 | 3 |
| language_pair | ar-en | 40 | 200 | 62.5% | 83.0% | +20.5 pp [+9.5, +32.5] | 11 | 2 |
| language_pair | es-en | 40 | 200 | 70.5% | 80.0% | +9.5 pp [+4.0, +15.5] | 11 | 1 |
| language_pair | hi-en | 40 | 200 | 96.0% | 96.5% | +0.5 pp [-2.0, +3.5] | 2 | 2 |

## Interpretation

Across all five full-run models, baseline FTGA is 76.3% and contract FTGA is 86.5%, for a +10.2 pp [+5.8, +15.0] item-cluster bootstrap interval. The prompt-level movement is 24 net-positive items versus 5 net-negative items.

The editing-preservation family remains the dominant and most stable slice: its effect is +40.7 pp [+28.0, +53.3] with 20 net-positive items and 0 net-negative items.

Language-pair uncertainty is heterogeneous: Arabic-English is +20.5 pp [+9.5, +32.5], Spanish-English is +9.5 pp [+4.0, +15.5], and Hindi-English is +0.5 pp [-2.0, +3.5]. This supports the current caveat that Hindi-English is near ceiling in this synthetic pilot.

Claim boundary: this is automatic-score uncertainty over a synthetic stress pilot. It strengthens the robustness story under prompt resampling, but it does not replace native/near-native validation.
