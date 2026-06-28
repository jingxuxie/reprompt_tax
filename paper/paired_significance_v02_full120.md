# RePromptTax Paired Sign-Test Sensitivity

Generated from `results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv`.

Positive counts mean the contract improved the paired item in the stated
direction. Ties are excluded from the exact two-sided sign test.

| Model | Metric | Direction | + | - | Ties | Mean delta | Sign-test p |
|---|---|---|---:|---:|---:|---:|---:|
| gpt-4.1 | FTGA | contract_minus_baseline | 20 | 0 | 100 | 0.167 | 0.0000 |
| gpt-4.1 | RTT reduction | baseline_minus_contract | 20 | 2 | 98 | 0.133 | 0.0001 |
| gpt-4.1 | Token-tax reduction | baseline_minus_contract | 26 | 2 | 92 | 0.300 | 0.0000 |
| gpt-4.1 | Unresolved reduction | baseline_minus_contract | 0 | 2 | 118 | -0.017 | 0.5000 |
| gpt-4.1-mini | FTGA | contract_minus_baseline | 4 | 0 | 116 | 0.033 | 0.1250 |
| gpt-4.1-mini | RTT reduction | baseline_minus_contract | 5 | 1 | 114 | 0.033 | 0.2188 |
| gpt-4.1-mini | Token-tax reduction | baseline_minus_contract | 29 | 0 | 91 | 0.159 | 0.0000 |
| gpt-4.1-mini | Unresolved reduction | baseline_minus_contract | 0 | 1 | 119 | -0.008 | 1.0000 |
| gpt-4.1-nano | FTGA | contract_minus_baseline | 12 | 1 | 107 | 0.092 | 0.0034 |
| gpt-4.1-nano | RTT reduction | baseline_minus_contract | 17 | 3 | 100 | 0.142 | 0.0026 |
| gpt-4.1-nano | Token-tax reduction | baseline_minus_contract | 39 | 1 | 80 | 0.351 | 0.0000 |
| gpt-4.1-nano | Unresolved reduction | baseline_minus_contract | 4 | 2 | 114 | 0.017 | 0.6875 |
