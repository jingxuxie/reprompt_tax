# Language-Slice Analysis

Generated from `results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv`.

This supplement checks whether aggregate mitigation effects are concentrated
in a single language pair. Each language-pair slice has 40 paired items per
model. The analysis is still a synthetic stress-slice analysis, not a
population-level statement about speakers of these languages.

## Metrics By Model And Language

| Model | Condition | Language pair | FTGA | Mean RTT | Token tax | Unresolved | Initial failures |
|---|---|---|---:|---:|---:|---:|---:|
| gpt-4.1 | baseline | ar-en | 65.0% | 0.400 | 1.622 | 2.5% | 14 |
| gpt-4.1 | baseline | es-en | 67.5% | 0.375 | 1.594 | 2.5% | 13 |
| gpt-4.1 | baseline | hi-en | 97.5% | 0.075 | 1.087 | 2.5% | 1 |
| gpt-4.1 | contract | ar-en | 90.0% | 0.250 | 1.218 | 7.5% | 4 |
| gpt-4.1 | contract | es-en | 92.5% | 0.125 | 1.122 | 2.5% | 3 |
| gpt-4.1 | contract | hi-en | 97.5% | 0.075 | 1.063 | 2.5% | 1 |
| gpt-4.1-mini | baseline | ar-en | 62.5% | 0.400 | 1.636 | 0.0% | 15 |
| gpt-4.1-mini | baseline | es-en | 67.5% | 0.375 | 1.574 | 2.5% | 13 |
| gpt-4.1-mini | baseline | hi-en | 97.5% | 0.050 | 1.085 | 0.0% | 1 |
| gpt-4.1-mini | contract | ar-en | 72.5% | 0.325 | 1.366 | 2.5% | 11 |
| gpt-4.1-mini | contract | es-en | 67.5% | 0.375 | 1.421 | 2.5% | 13 |
| gpt-4.1-mini | contract | hi-en | 97.5% | 0.025 | 1.029 | 0.0% | 1 |
| gpt-4.1-nano | baseline | ar-en | 37.5% | 0.975 | 2.432 | 15.0% | 25 |
| gpt-4.1-nano | baseline | es-en | 70.0% | 0.325 | 1.530 | 0.0% | 12 |
| gpt-4.1-nano | baseline | hi-en | 95.0% | 0.100 | 1.116 | 2.5% | 2 |
| gpt-4.1-nano | contract | ar-en | 62.5% | 0.550 | 1.573 | 7.5% | 15 |
| gpt-4.1-nano | contract | es-en | 72.5% | 0.325 | 1.359 | 2.5% | 11 |
| gpt-4.1-nano | contract | hi-en | 95.0% | 0.100 | 1.092 | 2.5% | 2 |

## Paired Contract Minus Baseline Effects

| Model | Language pair | FTGA delta | RTT reduction | Token-tax reduction | Unresolved reduction | FTGA + / - / tie | Sign p |
|---|---|---:|---:|---:|---:|---:|---:|
| gpt-4.1 | ar-en | +25.0 pp | 0.150 | 0.404 | -5.0 pp | 10 / 0 / 30 | 0.0020 |
| gpt-4.1 | es-en | +25.0 pp | 0.250 | 0.473 | +0.0 pp | 10 / 0 / 30 | 0.0020 |
| gpt-4.1 | hi-en | +0.0 pp | 0.000 | 0.024 | +0.0 pp | 0 / 0 / 40 | 1.0000 |
| gpt-4.1-mini | ar-en | +10.0 pp | 0.075 | 0.270 | -2.5 pp | 4 / 0 / 36 | 0.1250 |
| gpt-4.1-mini | es-en | +0.0 pp | 0.000 | 0.152 | +0.0 pp | 0 / 0 / 40 | 1.0000 |
| gpt-4.1-mini | hi-en | +0.0 pp | 0.025 | 0.056 | +0.0 pp | 0 / 0 / 40 | 1.0000 |
| gpt-4.1-nano | ar-en | +25.0 pp | 0.425 | 0.859 | +7.5 pp | 10 / 0 / 30 | 0.0020 |
| gpt-4.1-nano | es-en | +2.5 pp | 0.000 | 0.170 | -2.5 pp | 1 / 0 / 39 | 1.0000 |
| gpt-4.1-nano | hi-en | +0.0 pp | 0.000 | 0.024 | +0.0 pp | 1 / 1 / 38 | 1.0000 |

## Aggregate Across Models By Language Pair

| Language pair | Models | Mean FTGA delta | Mean RTT reduction | Mean token-tax reduction | FTGA + / - / tie |
|---|---:|---:|---:|---:|---:|
| ar-en | 3 | +20.0 pp | 0.217 | 0.511 | 24 / 0 / 96 |
| es-en | 3 | +9.2 pp | 0.083 | 0.265 | 11 / 0 / 109 |
| hi-en | 3 | +0.0 pp | 0.008 | 0.035 | 1 / 1 / 118 |

## Interpretation

The largest language-slice gains appear in Arabic-English:
averaged across models, FTGA increases by +20.0 pp.
`gpt-4.1-nano` improves by +25.0 pp on this slice
(10 improved, 0 worsened).

`gpt-4.1` improves by +25.0 pp on Arabic-English and
+25.0 pp on Spanish-English, while Hindi-English
has little room to improve because baseline FTGA is already high.

The main weak slice for the contract is Spanish-English on `gpt-4.1-mini`,
where FTGA delta is +0.0 pp despite lower token tax.
Aggregated Hindi-English FTGA movement is +0.0 pp.

These language-slice results support the aggregate claim that the contract
reduces burden in the stress pilot, but they also make the boundary clear:
the mitigation is not uniformly strong across every model/language pair.
