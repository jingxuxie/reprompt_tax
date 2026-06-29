# Balanced Subsample Robustness

This no-API diagnostic simulates balanced stratified pilots from the saved
full 120-item paired trajectories. Each simulated sample chooses the same
number of items from each language-pair/task-family cell, then recomputes
the baseline-vs-contract first-turn alignment effect. It tests whether
small pilots recover the full-run direction and approximate magnitude; it
does not replace the full-run results or native/near-native validation.

## Full-Run Effects

| Population | Items | Model-item pairs | Full FTGA delta | Improved pairs | Worsened pairs | Tied pairs |
|---|---:|---:|---:|---:|---:|---:|
| all_models | 120 | 600 | +10.2 pp | 67 | 6 | 527 |
| gpt-4.1 | 120 | 120 | +16.7 pp | 20 | 0 | 100 |
| gpt-4.1-mini | 120 | 120 | +3.3 pp | 4 | 0 | 116 |
| gpt-4.1-nano | 120 | 120 | +9.2 pp | 12 | 1 | 107 |
| gpt-5.4-mini | 120 | 120 | +5.0 pp | 11 | 5 | 104 |
| gpt-5.5 | 120 | 120 | +16.7 pp | 20 | 0 | 100 |

## Simulated Balanced Pilots

| Population | Items | k/cell | Full delta | Median pilot delta | 5--95% pilot delta | Direction recovered | Within 5 pp | Median abs. error |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all_models | 12 | 1 | +10.2 pp | +10.0 pp | [+6.7, +13.3] pp | 100.0% | 96.7% | 1.5 pp |
| all_models | 24 | 2 | +10.2 pp | +10.0 pp | [+7.5, +12.5] pp | 100.0% | 99.9% | 1.0 pp |
| all_models | 36 | 3 | +10.2 pp | +10.0 pp | [+8.3, +12.2] pp | 100.0% | 100.0% | 0.8 pp |
| all_models | 48 | 4 | +10.2 pp | +10.0 pp | [+8.8, +11.7] pp | 100.0% | 100.0% | 0.6 pp |
| all_models | 60 | 5 | +10.2 pp | +10.0 pp | [+9.0, +11.3] pp | 100.0% | 100.0% | 0.5 pp |
| all_models | 96 | 8 | +10.2 pp | +10.2 pp | [+9.6, +10.8] pp | 100.0% | 100.0% | 0.2 pp |
| all_models | 120 | 10 | +10.2 pp | +10.2 pp | [+10.2, +10.2] pp | 100.0% | 100.0% | 0.0 pp |
| gpt-4.1 | 12 | 1 | +16.7 pp | +16.7 pp | [+8.3, +25.0] pp | 100.0% | 81.9% | 0.0 pp |
| gpt-4.1 | 24 | 2 | +16.7 pp | +16.7 pp | [+12.5, +20.8] pp | 100.0% | 100.0% | 0.0 pp |
| gpt-4.1 | 36 | 3 | +16.7 pp | +16.7 pp | [+13.9, +19.4] pp | 100.0% | 100.0% | 0.0 pp |
| gpt-4.1 | 48 | 4 | +16.7 pp | +16.7 pp | [+14.6, +18.8] pp | 100.0% | 100.0% | 0.0 pp |
| gpt-4.1 | 60 | 5 | +16.7 pp | +16.7 pp | [+15.0, +18.3] pp | 100.0% | 100.0% | 0.8 pp |
| gpt-4.1 | 96 | 8 | +16.7 pp | +16.7 pp | [+15.6, +17.7] pp | 100.0% | 100.0% | 0.0 pp |
| gpt-4.1 | 120 | 10 | +16.7 pp | +16.7 pp | [+16.7, +16.7] pp | 100.0% | 100.0% | 0.0 pp |
| gpt-4.1-mini | 12 | 1 | +3.3 pp | +0.0 pp | [+0.0, +8.3] pp | 40.8% | 59.2% | 3.3 pp |
| gpt-4.1-mini | 24 | 2 | +3.3 pp | +4.2 pp | [+0.0, +8.3] pp | 65.7% | 87.5% | 0.9 pp |
| gpt-4.1-mini | 36 | 3 | +3.3 pp | +2.8 pp | [+0.0, +5.6] pp | 82.7% | 96.8% | 2.3 pp |
| gpt-4.1-mini | 48 | 4 | +3.3 pp | +4.2 pp | [+0.0, +6.2] pp | 93.5% | 99.6% | 1.2 pp |
| gpt-4.1-mini | 60 | 5 | +3.3 pp | +3.3 pp | [+1.7, +5.0] pp | 97.4% | 100.0% | 1.6 pp |
| gpt-4.1-mini | 96 | 8 | +3.3 pp | +3.1 pp | [+2.1, +4.2] pp | 100.0% | 100.0% | 0.2 pp |
| gpt-4.1-mini | 120 | 10 | +3.3 pp | +3.3 pp | [+3.3, +3.3] pp | 100.0% | 100.0% | 0.0 pp |
| gpt-4.1-nano | 12 | 1 | +9.2 pp | +8.3 pp | [+0.0, +16.7] pp | 85.4% | 63.7% | 0.9 pp |
| gpt-4.1-nano | 24 | 2 | +9.2 pp | +8.3 pp | [+4.2, +16.7] pp | 98.2% | 72.2% | 3.3 pp |
| gpt-4.1-nano | 36 | 3 | +9.2 pp | +8.3 pp | [+5.6, +13.9] pp | 100.0% | 95.1% | 1.9 pp |
| gpt-4.1-nano | 48 | 4 | +9.2 pp | +8.3 pp | [+6.2, +12.5] pp | 100.0% | 93.9% | 1.2 pp |
| gpt-4.1-nano | 60 | 5 | +9.2 pp | +10.0 pp | [+6.7, +11.7] pp | 100.0% | 100.0% | 0.9 pp |
| gpt-4.1-nano | 96 | 8 | +9.2 pp | +9.4 pp | [+7.3, +10.4] pp | 100.0% | 100.0% | 0.9 pp |
| gpt-4.1-nano | 120 | 10 | +9.2 pp | +9.2 pp | [+9.2, +9.2] pp | 100.0% | 100.0% | 0.0 pp |
| gpt-5.4-mini | 12 | 1 | +5.0 pp | +8.3 pp | [-8.3, +16.7] pp | 60.3% | 80.3% | 5.0 pp |
| gpt-5.4-mini | 24 | 2 | +5.0 pp | +4.2 pp | [-4.2, +12.5] pp | 75.6% | 83.0% | 3.3 pp |
| gpt-5.4-mini | 36 | 3 | +5.0 pp | +5.6 pp | [+0.0, +11.1] pp | 85.7% | 88.9% | 2.2 pp |
| gpt-5.4-mini | 48 | 4 | +5.0 pp | +4.2 pp | [+0.0, +10.4] pp | 92.2% | 92.5% | 1.2 pp |
| gpt-5.4-mini | 60 | 5 | +5.0 pp | +5.0 pp | [+1.7, +8.3] pp | 97.8% | 99.6% | 1.7 pp |
| gpt-5.4-mini | 96 | 8 | +5.0 pp | +5.2 pp | [+3.1, +7.3] pp | 100.0% | 100.0% | 0.8 pp |
| gpt-5.4-mini | 120 | 10 | +5.0 pp | +5.0 pp | [+5.0, +5.0] pp | 100.0% | 100.0% | 0.0 pp |
| gpt-5.5 | 12 | 1 | +16.7 pp | +16.7 pp | [+8.3, +25.0] pp | 100.0% | 70.0% | 0.0 pp |
| gpt-5.5 | 24 | 2 | +16.7 pp | +16.7 pp | [+12.5, +20.8] pp | 100.0% | 96.4% | 0.0 pp |
| gpt-5.5 | 36 | 3 | +16.7 pp | +16.7 pp | [+13.9, +19.4] pp | 100.0% | 92.7% | 2.7 pp |
| gpt-5.5 | 48 | 4 | +16.7 pp | +16.7 pp | [+12.5, +18.8] pp | 100.0% | 100.0% | 2.1 pp |
| gpt-5.5 | 60 | 5 | +16.7 pp | +16.7 pp | [+13.3, +20.0] pp | 100.0% | 100.0% | 1.6 pp |
| gpt-5.5 | 96 | 8 | +16.7 pp | +16.7 pp | [+15.6, +17.7] pp | 100.0% | 100.0% | 0.0 pp |
| gpt-5.5 | 120 | 10 | +16.7 pp | +16.7 pp | [+16.7, +16.7] pp | 100.0% | 100.0% | 0.0 pp |

## Interpretation

At the 48-item balanced-pilot scale (four items per cell), the all-model aggregate recovers the full positive direction in 100.0% of simulations and lands within 5 pp of the full +10.2 pp effect in 100.0% of simulations.

The GPT-5.5 headline is stable under the same 48-item design: the simulated direction is recovered in 100.0% of samples, with median pilot delta +16.7 pp versus the full +16.7 pp effect.

Weaker effects remain appropriately unstable: at 48 items, `gpt-5.4-mini` recovers the positive direction in 92.2% of simulations and `gpt-4.1-mini` in 93.5%. This supports the current claim boundary: the flagship current-model result is robust, while smaller-effect models should remain bounded.

Claim boundary: this artifact is a subsampling sensitivity check over saved automatic-score trajectories. It supports fast iteration and pilot design, but full paper claims should remain anchored to the complete 120-item runs and to completed human/native review when available.
