# RePromptTax Paired Sign-Test Sensitivity

Generated from `results/tables/openai_three_model_stress60/trajectory_metrics.csv`.

Positive counts mean the contract improved the paired item in the stated
direction. Ties are excluded from the exact two-sided sign test.

| Model | Metric | Direction | + | - | Ties | Mean delta | Sign-test p |
|---|---|---|---:|---:|---:|---:|---:|
| gpt-4.1 | FTGA | contract_minus_baseline | 10 | 0 | 50 | 0.167 | 0.0020 |
| gpt-4.1 | RTT reduction | baseline_minus_contract | 10 | 0 | 50 | 0.167 | 0.0020 |
| gpt-4.1 | Token-tax reduction | baseline_minus_contract | 10 | 0 | 50 | 0.290 | 0.0020 |
| gpt-4.1 | Unresolved reduction | baseline_minus_contract | 0 | 0 | 60 | 0.000 | 1.0000 |
| gpt-4.1-mini | FTGA | contract_minus_baseline | 3 | 0 | 57 | 0.050 | 0.2500 |
| gpt-4.1-mini | RTT reduction | baseline_minus_contract | 3 | 0 | 57 | 0.050 | 0.2500 |
| gpt-4.1-mini | Token-tax reduction | baseline_minus_contract | 11 | 0 | 49 | 0.138 | 0.0010 |
| gpt-4.1-mini | Unresolved reduction | baseline_minus_contract | 0 | 0 | 60 | 0.000 | 1.0000 |
| gpt-4.1-nano | FTGA | contract_minus_baseline | 6 | 0 | 54 | 0.100 | 0.0312 |
| gpt-4.1-nano | RTT reduction | baseline_minus_contract | 10 | 1 | 49 | 0.200 | 0.0117 |
| gpt-4.1-nano | Token-tax reduction | baseline_minus_contract | 18 | 0 | 42 | 0.387 | 0.0000 |
| gpt-4.1-nano | Unresolved reduction | baseline_minus_contract | 4 | 1 | 55 | 0.050 | 0.3750 |
