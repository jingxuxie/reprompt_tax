# RePromptTax Paired Sign-Test Sensitivity

Generated from `results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv`.

Positive counts mean the contract improved the paired item in the stated
direction. Ties are excluded from the exact two-sided sign test.

| Model | Metric | Direction | + | - | Ties | Mean delta | Sign-test p |
|---|---|---|---:|---:|---:|---:|---:|
| gpt-5.5 | FTGA | contract_minus_baseline | 20 | 0 | 100 | 0.167 | 0.0000 |
| gpt-5.5 | RTT reduction | baseline_minus_contract | 21 | 0 | 99 | 0.208 | 0.0000 |
| gpt-5.5 | Token-tax reduction | baseline_minus_contract | 22 | 0 | 98 | 0.262 | 0.0000 |
| gpt-5.5 | Unresolved reduction | baseline_minus_contract | 2 | 0 | 118 | 0.017 | 0.5000 |
