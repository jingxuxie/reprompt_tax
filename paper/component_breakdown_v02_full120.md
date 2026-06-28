# Scorer Component Breakdown

Generated from first-turn rows in
`results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl`.

Each component is a conservative automatic check. Component pass rates are
not independent human judgments; they show which rule families drive the
automatic first-turn global-alignment score.

## By Model And Condition

| Model | Condition | FTGA | Language | Script | Preservation | Task | Register/locale |
|---|---|---:|---:|---:|---:|---:|---:|
| gpt-4.1 | baseline | 76.7% | 83.3% | 91.7% | 93.3% | 90.8% | 100.0% |
| gpt-4.1 | contract | 93.3% | 99.2% | 100.0% | 94.2% | 98.3% | 100.0% |
| gpt-4.1-mini | baseline | 75.8% | 83.3% | 91.7% | 92.5% | 81.7% | 100.0% |
| gpt-4.1-mini | contract | 79.2% | 86.7% | 95.0% | 92.5% | 85.0% | 100.0% |
| gpt-4.1-nano | baseline | 67.5% | 82.5% | 91.7% | 85.0% | 73.3% | 100.0% |
| gpt-4.1-nano | contract | 76.7% | 90.8% | 99.2% | 85.8% | 82.5% | 100.0% |

## Aggregate By Task Family

| Condition | Task family | FTGA | Language | Script | Preservation | Task | Register/locale |
|---|---|---:|---:|---:|---:|---:|---:|
| baseline | editing_preservation | 33.3% | 33.3% | 66.7% | 100.0% | 44.4% | 100.0% |
| baseline | output_language_inference | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| baseline | quote_preservation | 90.0% | 100.0% | 100.0% | 90.0% | 90.0% | 100.0% |
| baseline | script_register_locale | 70.0% | 98.9% | 100.0% | 71.1% | 93.3% | 100.0% |
| contract | editing_preservation | 70.0% | 70.0% | 92.2% | 100.0% | 70.0% | 100.0% |
| contract | output_language_inference | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| contract | quote_preservation | 91.1% | 100.0% | 100.0% | 91.1% | 91.1% | 100.0% |
| contract | script_register_locale | 71.1% | 98.9% | 100.0% | 72.2% | 93.3% | 100.0% |

## Paired Contract Minus Baseline Effects

| Model | Component | Delta | Improved | Worsened | Tied |
|---|---|---:|---:|---:|---:|
| gpt-4.1 | Language | +15.8 pp | 19 | 0 | 101 |
| gpt-4.1 | Script | +8.3 pp | 10 | 0 | 110 |
| gpt-4.1 | Preservation | +0.8 pp | 1 | 0 | 119 |
| gpt-4.1 | Task | +7.5 pp | 10 | 1 | 109 |
| gpt-4.1 | Register/locale | +0.0 pp | 0 | 0 | 120 |
| gpt-4.1-mini | Language | +3.3 pp | 4 | 0 | 116 |
| gpt-4.1-mini | Script | +3.3 pp | 4 | 0 | 116 |
| gpt-4.1-mini | Preservation | +0.0 pp | 0 | 0 | 120 |
| gpt-4.1-mini | Task | +3.3 pp | 4 | 0 | 116 |
| gpt-4.1-mini | Register/locale | +0.0 pp | 0 | 0 | 120 |
| gpt-4.1-nano | Language | +8.3 pp | 11 | 1 | 108 |
| gpt-4.1-nano | Script | +7.5 pp | 9 | 0 | 111 |
| gpt-4.1-nano | Preservation | +0.8 pp | 1 | 0 | 119 |
| gpt-4.1-nano | Task | +9.2 pp | 11 | 0 | 109 |
| gpt-4.1-nano | Register/locale | +0.0 pp | 0 | 0 | 120 |

## Interpretation

The largest component-level movement is language alignment: gpt-4.1 gains +15.8 pp
on paired first-turn language checks under the contract. The contract also
improves nano task completion by +9.2 pp.

At the task-family level, editing-preservation is where component changes
matter most: language pass rate rises from 33.3% to
70.0%, and script pass rate rises from
66.7% to 92.2%.

The analysis also marks a boundary: preservation pass rates barely move
for some models (for example, mini preservation delta is +0.0 pp),
and script/register/locale preservation remains below saturation
(72.2% under contract). Register/locale checks
are saturated under the current rule set, so they should not be presented
as evidence that nuanced register judgments are solved.
