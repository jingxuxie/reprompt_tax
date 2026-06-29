# Current-Model Prompt Mechanism Diagnostic

This artifact compares the full Global Interaction Contract with the narrower
content-preservation prompt on the full 120-item stress benchmark for
`gpt-5.4-mini`. Baseline and contract rows reuse the current-model refresh run;
the content-preservation row is a new one-condition follow-up.

## Summary

| Condition | FTGA | Mean RTT | Token tax | Unresolved | First-turn failures |
|---|---:|---:|---:|---:|---:|
| baseline | 80.0% | 0.250 | 1.379x | 2.5% | 24 |
| contract | 85.0% | 0.250 | 1.241x | 5.0% | 18 |
| content_preservation | 85.8% | 0.242 | 1.252x | 5.0% | 17 |

## Paired Effects

| Comparison | FTGA delta | Improved | Worsened | Tied | Sign p | RTT reduction | Token-tax reduction | Unresolved reduction |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| contract_minus_baseline | +5.0 pp | 11 | 5 | 104 | 0.210114 | +0.000 | +0.138x | -2.5 pp |
| content_preservation_minus_baseline | +5.8 pp | 11 | 4 | 105 | 0.118469 | +0.008 | +0.128x | -2.5 pp |
| content_preservation_minus_contract | +0.8 pp | 5 | 4 | 111 | 1 | +0.008 | -0.010x | +0.0 pp |

## Family FTGA

| Family | Baseline | Contract | Content preservation |
|---|---:|---:|---:|
| editing_preservation | 33.3% | 66.7% | 66.7% |
| output_language_inference | 100.0% | 100.0% | 100.0% |
| quote_preservation | 100.0% | 93.3% | 93.3% |
| script_register_locale | 86.7% | 80.0% | 83.3% |

## API Usage

| Artifact | API calls | Input tokens | Output tokens | Total tokens |
|---|---:|---:|---:|---:|
| baseline+contract | 291 | 40286 | 8730 | 49016 |
| content_preservation | 143 | 19353 | 2882 | 22235 |

## Interpretation

Content preservation improves FTGA from 80.0% to 85.8% (+5.8 pp), close to the full contract's 85.0%.
Against the full contract, content preservation changes FTGA by +0.8 pp
(5 improved, 4 worsened items),
with -0.010x token-tax reduction.
The mechanism claim should therefore be softened: on this current low-cost model,
the narrower content-preservation prompt is essentially tied with the full contract,
rather than clearly dominating it as in the earlier nano diagnostic.
