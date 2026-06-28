# Prompt-Control Diagnostic

This is a single-model diagnostic on `gpt-4.1-nano`, not a paper-facing
three-model claim. It tests whether a longer generic helpfulness prompt
explains the Global Interaction Contract result on the 120-item stress pilot.

## Aggregate Metrics

| Condition | FTGA | Mean RTT | Token tax | Unresolved | Initial failures |
|---|---:|---:|---:|---:|---:|
| baseline | 67.5% | 0.47 | 1.69x | 5.8% | 39 |
| generic_helpfulness | 75.0% | 0.33 | 1.37x | 3.3% | 30 |
| contract | 76.7% | 0.33 | 1.34x | 4.2% | 28 |

## Paired Effects

| Comparison | FTGA delta | Improved / worsened / tied | Sign-test p | RTT reduction | Token-tax reduction | Unresolved reduction |
|---|---:|---:|---:|---:|---:|---:|
| generic_helpfulness_minus_baseline | +7.5 pp | 9 / 0 / 111 | 0.0039 | 0.14 | 0.32x | +2.5 pp |
| contract_minus_baseline | +9.2 pp | 12 / 1 / 107 | 0.0034 | 0.14 | 0.35x | +1.7 pp |
| contract_minus_generic_helpfulness | +1.7 pp | 4 / 2 / 114 | 0.6875 | 0.00 | 0.03x | -0.8 pp |

## Interpretation

The generic helpfulness prompt improves FTGA from 67.5% to 75.0%,
so some mitigation benefit comes from generic instruction-following scaffolding.
The specific contract reaches 76.7% FTGA and has the lowest token tax.
Relative to generic helpfulness, the contract adds +1.7 pp
FTGA with no additional mean RTT reduction. This diagnostic supports a conservative
claim: the Global Interaction Contract beats generic helpfulness in this
three-condition control, but this does not prove that every gain is specific
to multilingual-contract wording or that the full contract is globally best.

