# Prompt-Family Scorecard

This artifact consolidates the saved prompt-control and prompt-mechanism
diagnostics. It makes no API calls. It compares only prompts that were
already run: baseline, full Global Interaction Contract, the narrower
content-preservation scaffold, and the generic-helpfulness control where
available.

## Model Scorecard

| Model | Tested conditions | Best FTGA prompt | Baseline FTGA | Contract FTGA | Content-preservation FTGA | Content minus contract | Boundary |
|---|---|---|---:|---:|---:|---:|---|
| gpt-4.1-nano | baseline;content_preservation;contract;generic_helpfulness | content_preservation | 67.5% | 76.7% | 80.0% | +3.3 pp (7/3/110) | single_model_generic_control_only |
| gpt-5.4-mini | baseline;content_preservation;contract | content_preservation | 80.0% | 85.0% | 85.8% | +0.8 pp (5/4/111) | generic_not_tested_current_models |
| gpt-5.5 | baseline;content_preservation;contract | content_preservation | 81.7% | 98.3% | 99.2% | +0.8 pp (2/1/117) | generic_not_tested_current_models |

## Aggregate Prompt Metrics

| Model | Condition | FTGA | Mean RTT | Token tax | Unresolved | Initial failures |
|---|---|---:|---:|---:|---:|---:|
| gpt-4.1-nano | baseline | 67.5% | 0.467 | 1.693x | 5.8% | 39 |
| gpt-4.1-nano | generic_helpfulness | 75.0% | 0.325 | 1.370x | 3.3% | 30 |
| gpt-4.1-nano | content_preservation | 80.0% | 0.267 | 1.279x | 3.3% | 24 |
| gpt-4.1-nano | contract | 76.7% | 0.325 | 1.341x | 4.2% | 28 |
| gpt-5.4-mini | baseline | 80.0% | 0.250 | 1.379x | 2.5% | 24 |
| gpt-5.4-mini | contract | 85.0% | 0.250 | 1.241x | 5.0% | 18 |
| gpt-5.4-mini | content_preservation | 85.8% | 0.242 | 1.252x | 5.0% | 17 |
| gpt-5.5 | baseline | 81.7% | 0.225 | 1.278x | 1.7% | 22 |
| gpt-5.5 | contract | 98.3% | 0.017 | 1.016x | 0.0% | 2 |
| gpt-5.5 | content_preservation | 99.2% | 0.008 | 1.012x | 0.0% | 1 |

## Paired Prompt Comparisons

| Model | Comparison | FTGA delta | Improved | Worsened | Tied | Sign p | RTT reduction | Token-tax reduction |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-4.1-nano | content_preservation_minus_baseline | +12.5 pp | 16 | 1 | 103 | 0.0002747 | +0.200 | +0.414x |
| gpt-4.1-nano | contract_minus_baseline | +9.2 pp | 12 | 1 | 107 | 0.003418 | +0.142 | +0.351x |
| gpt-4.1-nano | content_preservation_minus_contract | +3.3 pp | 7 | 3 | 110 | 0.3438 | -0.058 | -0.063x |
| gpt-5.4-mini | contract_minus_baseline | +5.0 pp | 11 | 5 | 104 | 0.2101 | +0.000 | +0.138x |
| gpt-5.4-mini | content_preservation_minus_baseline | +5.8 pp | 11 | 4 | 105 | 0.1185 | +0.008 | +0.128x |
| gpt-5.4-mini | content_preservation_minus_contract | +0.8 pp | 5 | 4 | 111 | 1 | +0.008 | -0.010x |
| gpt-5.5 | contract_minus_baseline | +16.7 pp | 20 | 0 | 100 | 1.907e-06 | +0.208 | +0.262x |
| gpt-5.5 | content_preservation_minus_baseline | +17.5 pp | 22 | 1 | 97 | 5.722e-06 | +0.217 | +0.267x |
| gpt-5.5 | content_preservation_minus_contract | +0.8 pp | 2 | 1 | 117 | 1 | +0.008 | +0.005x |

## Interpretation

Across the three models with saved content-preservation rows, the content-preservation scaffold is the highest-FTGA tested prompt: 80.0% on `gpt-4.1-nano`, 85.8% on `gpt-5.4-mini`, and 99.2% on `gpt-5.5`.

The margins over the full contract are model-dependent: +3.3 pp on nano, +0.8 pp on `gpt-5.4-mini`, and +0.8 pp on `gpt-5.5`. The two current-model margins are one net item or essentially tied, so they should be framed as mechanism evidence rather than prompt dominance.

The family slice reinforces the mechanism claim: content preservation reaches 80.0% editing-preservation FTGA on nano and 100.0% on `gpt-5.5`, while non-editing families are often saturated or sparse.

Claim boundary: generic-helpfulness was only tested for `gpt-4.1-nano`; the current-model prompt comparison is baseline, contract, and content-preservation only. This artifact does not claim the narrow prompt is universally best.
