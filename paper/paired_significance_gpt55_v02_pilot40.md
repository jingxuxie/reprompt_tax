# RePromptTax Paired Sign-Test Sensitivity

Generated from `results/tables/openai_gpt55_stress_v02_pilot40/trajectory_metrics.csv`.

Positive counts mean the contract improved the paired item in the stated
direction. Ties are excluded from the exact two-sided sign test.

| Model | Metric | Direction | + | - | Ties | Mean delta | Sign-test p |
|---|---|---|---:|---:|---:|---:|---:|
| gpt-5.5 | FTGA | contract_minus_baseline | 8 | 0 | 32 | 0.200 | 0.0078 |
| gpt-5.5 | RTT reduction | baseline_minus_contract | 8 | 0 | 32 | 0.200 | 0.0078 |
| gpt-5.5 | Token-tax reduction | baseline_minus_contract | 8 | 0 | 32 | 0.268 | 0.0078 |
| gpt-5.5 | Unresolved reduction | baseline_minus_contract | 0 | 0 | 40 | 0.000 | 1.0000 |
