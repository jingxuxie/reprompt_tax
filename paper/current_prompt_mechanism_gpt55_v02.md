# Current-Model Prompt Mechanism Diagnostic

This artifact compares the full Global Interaction Contract with the narrower
content-preservation prompt on the full 120-item stress benchmark for
`gpt-5.5`. Baseline and contract rows reuse the current-model refresh run;
the content-preservation row is a new one-condition follow-up.

## Summary

| Condition | FTGA | Mean RTT | Token tax | Unresolved | First-turn failures |
|---|---:|---:|---:|---:|---:|
| baseline | 81.7% | 0.225 | 1.278x | 1.7% | 22 |
| contract | 98.3% | 0.017 | 1.016x | 0.0% | 2 |
| content_preservation | 99.2% | 0.008 | 1.012x | 0.0% | 1 |

## Paired Effects

| Comparison | FTGA delta | Improved | Worsened | Tied | Sign p | RTT reduction | Token-tax reduction | Unresolved reduction |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| contract_minus_baseline | +16.7 pp | 20 | 0 | 100 | 1.90735e-06 | +0.208 | +0.262x | +1.7 pp |
| content_preservation_minus_baseline | +17.5 pp | 22 | 1 | 97 | 5.72205e-06 | +0.217 | +0.267x | +1.7 pp |
| content_preservation_minus_contract | +0.8 pp | 2 | 1 | 117 | 1 | +0.008 | +0.005x | +0.0 pp |

## Family FTGA

| Family | Baseline | Contract | Content preservation |
|---|---:|---:|---:|
| editing_preservation | 33.3% | 93.3% | 100.0% |
| output_language_inference | 96.7% | 100.0% | 100.0% |
| quote_preservation | 100.0% | 100.0% | 100.0% |
| script_register_locale | 96.7% | 100.0% | 96.7% |

## API Usage

| Artifact | API calls | Input tokens | Output tokens | Total tokens |
|---|---:|---:|---:|---:|
| baseline+contract | 267 | 34172 | 18995 | 53167 |
| content_preservation | 121 | 15310 | 7691 | 23001 |

## Interpretation

Content preservation improves FTGA from 81.7% to 99.2% (+17.5 pp), close to the full contract's 98.3%.
Against the full contract, content preservation changes FTGA by +0.8 pp
(2 improved, 1 worsened items),
with +0.005x token-tax reduction.
For GPT-5.5, the narrower prompt matches or slightly exceeds the full contract on
auto-scored FTGA while using marginally less token tax; the difference from the full
contract is one net item and should be presented as mechanism evidence, not as a
dominance claim. This supports the interpretation that literal content-preservation
language accounts for most of the current-model gain on this stress benchmark.
