# RePromptTax Paired Sign-Test Sensitivity

Generated from `results/tables/openai_gpt54mini_stress_v02_full120/trajectory_metrics.csv`.

Positive counts mean the contract improved the paired item in the stated
direction. Ties are excluded from the exact two-sided sign test.

| Model | Metric | Direction | + | - | Ties | Mean delta | Sign-test p |
|---|---|---|---:|---:|---:|---:|---:|
| gpt-5.4-mini | FTGA | contract_minus_baseline | 11 | 5 | 104 | 0.050 | 0.2101 |
| gpt-5.4-mini | RTT reduction | baseline_minus_contract | 11 | 6 | 103 | 0.000 | 0.3323 |
| gpt-5.4-mini | Token-tax reduction | baseline_minus_contract | 23 | 6 | 91 | 0.138 | 0.0023 |
| gpt-5.4-mini | Unresolved reduction | baseline_minus_contract | 1 | 4 | 115 | -0.025 | 0.3750 |
