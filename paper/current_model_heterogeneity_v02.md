# Current-Model Heterogeneity

This diagnostic uses saved full-120 trajectory metrics for `gpt-5.4-mini`
and `gpt-5.5`. It makes no API calls. It asks whether the current-model
refresh headline is broad across language pairs and whether it is
concentrated in a single task family.

## Stratum Effects

| Model | Stratum type | Stratum | N | Baseline FTGA | Contract FTGA | Delta | Fixed | Regressed | RTT reduction | Token-tax reduction |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| gpt-5.4-mini | language_pair | ar-en | 40 | 72.5% | 90.0% | +17.5 pp | 9 | 2 | +0.075 | +0.272x |
| gpt-5.4-mini | language_pair | es-en | 40 | 72.5% | 72.5% | +0.0 pp | 1 | 1 | +0.000 | +0.158x |
| gpt-5.4-mini | language_pair | hi-en | 40 | 95.0% | 92.5% | -2.5 pp | 1 | 2 | -0.075 | -0.016x |
| gpt-5.4-mini | task_family | editing_preservation | 30 | 33.3% | 66.7% | +33.4 pp | 10 | 0 | +0.333 | +0.737x |
| gpt-5.4-mini | task_family | output_language_inference | 30 | 100.0% | 100.0% | +0.0 pp | 0 | 0 | +0.000 | +0.000x |
| gpt-5.4-mini | task_family | quote_preservation | 30 | 100.0% | 93.3% | -6.7 pp | 0 | 2 | -0.200 | -0.163x |
| gpt-5.4-mini | task_family | script_register_locale | 30 | 86.7% | 80.0% | -6.7 pp | 1 | 3 | -0.133 | -0.023x |
| gpt-5.5 | language_pair | ar-en | 40 | 75.0% | 100.0% | +25.0 pp | 10 | 0 | +0.250 | +0.338x |
| gpt-5.5 | language_pair | es-en | 40 | 75.0% | 95.0% | +20.0 pp | 8 | 0 | +0.225 | +0.331x |
| gpt-5.5 | language_pair | hi-en | 40 | 95.0% | 100.0% | +5.0 pp | 2 | 0 | +0.150 | +0.117x |
| gpt-5.5 | task_family | editing_preservation | 30 | 33.3% | 93.3% | +60.0 pp | 18 | 0 | +0.633 | +0.891x |
| gpt-5.5 | task_family | output_language_inference | 30 | 96.7% | 100.0% | +3.3 pp | 1 | 0 | +0.100 | +0.059x |
| gpt-5.5 | task_family | quote_preservation | 30 | 100.0% | 100.0% | +0.0 pp | 0 | 0 | +0.000 | +0.000x |
| gpt-5.5 | task_family | script_register_locale | 30 | 96.7% | 100.0% | +3.3 pp | 1 | 0 | +0.100 | +0.097x |

## Leave-One-Stratum FTGA Checks

| Model | Left-out type | Left-out stratum | Kept N | Baseline FTGA | Contract FTGA | Delta | Signal |
|---|---|---|---:|---:|---:|---:|---|
| gpt-5.4-mini | language_pair | ar-en | 80 | 83.8% | 82.5% | -1.3 pp | negative_remaining_ftga_effect |
| gpt-5.4-mini | language_pair | es-en | 80 | 83.8% | 91.2% | +7.4 pp | positive_remaining_effect |
| gpt-5.4-mini | language_pair | hi-en | 80 | 72.5% | 81.2% | +8.7 pp | positive_remaining_effect |
| gpt-5.4-mini | task_family | editing_preservation | 90 | 95.6% | 91.1% | -4.5 pp | negative_remaining_ftga_effect |
| gpt-5.4-mini | task_family | output_language_inference | 90 | 73.3% | 80.0% | +6.7 pp | positive_remaining_effect |
| gpt-5.4-mini | task_family | quote_preservation | 90 | 73.3% | 82.2% | +8.9 pp | positive_remaining_effect |
| gpt-5.4-mini | task_family | script_register_locale | 90 | 77.8% | 86.7% | +8.9 pp | positive_remaining_effect |
| gpt-5.5 | language_pair | ar-en | 80 | 85.0% | 97.5% | +12.5 pp | positive_remaining_effect |
| gpt-5.5 | language_pair | es-en | 80 | 85.0% | 100.0% | +15.0 pp | positive_remaining_effect |
| gpt-5.5 | language_pair | hi-en | 80 | 75.0% | 97.5% | +22.5 pp | positive_remaining_effect |
| gpt-5.5 | task_family | editing_preservation | 90 | 97.8% | 100.0% | +2.2 pp | positive_remaining_effect |
| gpt-5.5 | task_family | output_language_inference | 90 | 76.7% | 97.8% | +21.1 pp | positive_remaining_effect |
| gpt-5.5 | task_family | quote_preservation | 90 | 75.6% | 97.8% | +22.2 pp | positive_remaining_effect |
| gpt-5.5 | task_family | script_register_locale | 90 | 76.7% | 97.8% | +21.1 pp | positive_remaining_effect |

## Interpretation

The `gpt-5.5` effect is broad across language pairs: ar-en moves +25.0 pp, es-en moves +20.0 pp, and hi-en moves +5.0 pp. Every leave-one-language check remains positive, so the current flagship headline is not a single-language artifact.

The same `gpt-5.5` effect is task-family concentrated. Editing preservation moves +60.0 pp, and removing editing preservation leaves only a +2.2 pp FTGA effect because the other families are near ceiling. This supports a precise paper claim: the benchmark exposes a multilingual editing-preservation burden on the flagship model, not a uniform gain over all task types.

The lower-cost `gpt-5.4-mini` result is not robust across strata: ar-en moves +17.5 pp, es-en moves +0.0 pp, and hi-en moves -2.5 pp. Removing ar-en leaves a -1.3 pp FTGA effect, and removing editing preservation leaves -4.5 pp. The lower-cost current-model claim should remain bounded to token burden and directional aggregate FTGA.

Claim boundary: these are synthetic-pilot automatic-score slices. They should guide paper wording and reviewer discussion, but they do not replace native/near-native validation.
