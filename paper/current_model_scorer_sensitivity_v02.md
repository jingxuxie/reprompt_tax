# Current-Model Scorer Sensitivity

This diagnostic combines the saved full-120 `gpt-5.4-mini` and `gpt-5.5`
score logs. Each counterfactual relaxes exactly one automatic component
on first-turn rows while keeping all other components fixed. It makes no
new API calls and does not replace native/near-native validation.

## Overall Component Relaxation

| Condition | Actual FTGA | Relax language | Relax script | Relax preservation | Relax task | Relax register/locale |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 80.8% | 81.7% (+0.9) | 80.8% (+0.0) | 82.1% (+1.3) | 81.2% (+0.4) | 80.8% (+0.0) |
| contract | 91.7% | 94.2% (+2.5) | 91.7% (+0.0) | 93.8% (+2.1) | 91.7% (+0.0) | 91.7% (+0.0) |

## By Model And Condition

| Model | Condition | Actual FTGA | Relax language | Relax preservation | Relax task | Sole language blockers | Sole preservation blockers |
|---|---|---:|---:|---:|---:|---:|---:|
| gpt-5.4-mini | baseline | 80.0% | 80.8% (+0.8) | 82.5% (+2.5) | 80.0% (+0.0) | 1 | 3 |
| gpt-5.4-mini | contract | 85.0% | 88.3% (+3.3) | 89.2% (+4.2) | 85.0% (+0.0) | 4 | 5 |
| gpt-5.5 | baseline | 81.7% | 82.5% (+0.8) | 81.7% (+0.0) | 82.5% (+0.8) | 1 | 0 |
| gpt-5.5 | contract | 98.3% | 100.0% (+1.7) | 98.3% (+0.0) | 98.3% (+0.0) | 2 | 0 |

## Family-Level Binding Checks

| Model | Condition | Task family | Actual FTGA | Relax language delta | Relax preservation delta | Top sole blockers |
|---|---|---|---:|---:|---:|---|
| gpt-5.4-mini | baseline | Editing preservation | 33.3% | +0.0 pp | +0.0 pp | none |
| gpt-5.4-mini | baseline | Output-language inference | 100.0% | +0.0 pp | +0.0 pp | none |
| gpt-5.4-mini | baseline | Quote preservation | 100.0% | +0.0 pp | +0.0 pp | none |
| gpt-5.4-mini | baseline | Script/register/locale | 86.7% | +3.3 pp | +10.0 pp | language:1; preservation:3 |
| gpt-5.4-mini | contract | Editing preservation | 66.7% | +6.6 pp | +0.0 pp | language:2 |
| gpt-5.4-mini | contract | Output-language inference | 100.0% | +0.0 pp | +0.0 pp | none |
| gpt-5.4-mini | contract | Quote preservation | 93.3% | +6.7 pp | +0.0 pp | language:2 |
| gpt-5.4-mini | contract | Script/register/locale | 80.0% | +0.0 pp | +16.7 pp | preservation:5 |
| gpt-5.5 | baseline | Editing preservation | 33.3% | +0.0 pp | +0.0 pp | none |
| gpt-5.5 | baseline | Output-language inference | 96.7% | +0.0 pp | +0.0 pp | task:1 |
| gpt-5.5 | baseline | Quote preservation | 100.0% | +0.0 pp | +0.0 pp | none |
| gpt-5.5 | baseline | Script/register/locale | 96.7% | +3.3 pp | +0.0 pp | language:1 |
| gpt-5.5 | contract | Editing preservation | 93.3% | +6.7 pp | +0.0 pp | language:2 |
| gpt-5.5 | contract | Output-language inference | 100.0% | +0.0 pp | +0.0 pp | none |
| gpt-5.5 | contract | Quote preservation | 100.0% | +0.0 pp | +0.0 pp | none |
| gpt-5.5 | contract | Script/register/locale | 100.0% | +0.0 pp | +0.0 pp | none |

## Dominant Failure Signatures

| Model | Condition | Task family | Failed components | Count | Share of first-turn failures |
|---|---|---|---|---:|---:|
| gpt-5.4-mini | baseline | Editing preservation | language+script | 10 | 50.0% |
| gpt-5.4-mini | baseline | Editing preservation | language+task | 10 | 50.0% |
| gpt-5.4-mini | baseline | Script/register/locale | preservation | 3 | 75.0% |
| gpt-5.4-mini | baseline | Script/register/locale | language | 1 | 25.0% |
| gpt-5.4-mini | contract | Editing preservation | language+task | 7 | 70.0% |
| gpt-5.4-mini | contract | Editing preservation | language | 2 | 20.0% |
| gpt-5.4-mini | contract | Quote preservation | language | 2 | 100.0% |
| gpt-5.4-mini | contract | Script/register/locale | preservation | 5 | 83.3% |
| gpt-5.4-mini | contract | Script/register/locale | preservation+task | 1 | 16.7% |
| gpt-5.5 | baseline | Editing preservation | language+task | 10 | 50.0% |
| gpt-5.5 | baseline | Editing preservation | language+script+task | 9 | 45.0% |
| gpt-5.5 | baseline | Output-language inference | task | 1 | 100.0% |
| gpt-5.5 | baseline | Script/register/locale | language | 1 | 100.0% |
| gpt-5.5 | contract | Editing preservation | language | 2 | 100.0% |

## Interpretation

For `gpt-5.5` baseline, relaxing language alone moves FTGA from 81.7% to 82.5%,
consistent with wrapper/output-language failures. Under the contract, `gpt-5.5` is already near ceiling: relaxing language moves
FTGA from 98.3% to 100.0%.

For `gpt-5.4-mini` contract, relaxing preservation moves FTGA from 85.0% to 89.2%,
which isolates the lower-cost model's residual literal-preservation boundary.

The current-model headline is therefore not an artifact of a single fragile
component: the flagship result is dominated by output-language wrapper
failures under baseline, while the low-cost residual set includes distinct
preservation failures that remain after the contract.
