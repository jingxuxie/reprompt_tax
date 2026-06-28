# Scorer-Ablation Sensitivity

Generated from first-turn rows in `results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl`.
Each counterfactual relaxes exactly one automatic component while keeping
all other components fixed. This is a scorer-sensitivity diagnostic, not a
replacement for human validation.

## Overall Component Relaxation

| Condition | Actual FTGA | Relax language | Relax script | Relax preservation | Relax task | Relax register/locale |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 73.3% | 76.4% (+3.1) | 73.3% (+0.0) | 78.9% (+5.6) | 73.3% (+0.0) | 73.3% (+0.0) |
| contract | 83.1% | 83.3% (+0.2) | 83.1% (+0.0) | 88.3% (+5.2) | 83.1% (+0.0) | 83.1% (+0.0) |

## Family-Level Binding Checks

| Condition | Task family | Actual FTGA | Relax language delta | Relax preservation delta | Relax task delta | Top sole blocker counts |
|---|---|---:|---:|---:|---:|---|
| baseline | Editing preservation | 33.3% | +11.1 pp | +0.0 pp | +0.0 pp | language:10 |
| baseline | Output-language inference | 100.0% | +0.0 pp | +0.0 pp | +0.0 pp | none |
| baseline | Quote preservation | 90.0% | +0.0 pp | +0.0 pp | +0.0 pp | none |
| baseline | Script/register/locale | 70.0% | +1.1 pp | +22.2 pp | +0.0 pp | language:1; preservation:20 |
| contract | Editing preservation | 70.0% | +0.0 pp | +0.0 pp | +0.0 pp | none |
| contract | Output-language inference | 100.0% | +0.0 pp | +0.0 pp | +0.0 pp | none |
| contract | Quote preservation | 91.1% | +0.0 pp | +0.0 pp | +0.0 pp | none |
| contract | Script/register/locale | 71.1% | +1.1 pp | +21.1 pp | +0.0 pp | language:1; preservation:19 |

## Dominant Failure Signatures

| Condition | Task family | Failed components | Count | Share of first-turn failures |
|---|---|---|---:|---:|
| baseline | Editing preservation | language+script+task | 30 | 50.0% |
| baseline | Editing preservation | language+task | 20 | 33.3% |
| baseline | Quote preservation | preservation+task | 9 | 100.0% |
| baseline | Script/register/locale | preservation | 20 | 74.1% |
| baseline | Script/register/locale | preservation+task | 6 | 22.2% |
| contract | Editing preservation | language+task | 20 | 74.1% |
| contract | Editing preservation | language+script+task | 7 | 25.9% |
| contract | Quote preservation | preservation+task | 8 | 100.0% |
| contract | Script/register/locale | preservation | 19 | 73.1% |
| contract | Script/register/locale | preservation+task | 6 | 23.1% |

## Interpretation

Relaxing a single component produces only bounded changes because many
first-turn failures violate multiple automatic checks at once. In baseline
rows, relaxing language alone would move FTGA from 73.3% to
76.4%; relaxing task alone would move it to
73.3%. Under the contract, the corresponding
counterfactuals are 83.3% and
83.1%.

The main scorer boundary is therefore not a single fragile rule. Editing
failures often combine language, script, and task violations; preservation
and script/register/locale failures remain distinct residual checks. This
supports reporting the automatic scorer as a conservative diagnostic while
keeping native/near-native human validation as the stronger claim gate.
