# Current-Model Contract Regression Risk

This diagnostic isolates paired cases where the contract hurts first-turn
automatic success relative to the baseline. It uses saved full-120
trajectory metrics plus saved content-preservation rows; it makes no API
calls.

## Summary

| Model | N | Fixes | Regressions | Both fail | Resolved->unresolved | Content-preservation pass on regression cases |
|---|---:|---:|---:|---:|---:|---:|
| gpt-5.4-mini | 120 | 11 | 5 | 13 | 4 | 3 |
| gpt-5.5 | 120 | 20 | 0 | 2 | 0 | 0 |

## First-Turn Regression Cases

| Model | Item | Language | Family | Contract RTT | Contract unresolved | Contract failure | Content-preservation FTGA | Content unresolved |
|---|---|---|---|---:|---:|---|---:|---:|
| gpt-5.4-mini | ar_en_SD_006 | ar-en | script_register_locale | 3 | 1 | ['preservation_failure'] | 0 | 1 |
| gpt-5.4-mini | ar_en_SD_007 | ar-en | script_register_locale | 1 | 0 | ['preservation_failure', 'task_noncompletion'] | 1 | 0 |
| gpt-5.4-mini | es_en_SD_010 | es-en | script_register_locale | 1 | 0 | ['preservation_failure'] | 0 | 0 |
| gpt-5.4-mini | hi_en_SC_003 | hi-en | quote_preservation | 3 | 1 | ['wrong_output_language'] | 1 | 0 |
| gpt-5.4-mini | hi_en_SC_008 | hi-en | quote_preservation | 3 | 1 | ['wrong_output_language'] | 1 | 0 |

## Resolved-To-Unresolved Shifts

| Model | Item | Language | Family | Baseline FTGA | Contract FTGA | Contract failure | Content-preservation FTGA | Content unresolved |
|---|---|---|---|---:|---:|---|---:|---:|
| gpt-5.4-mini | ar_en_SD_006 | ar-en | script_register_locale | 1 | 0 | ['preservation_failure'] | 0 | 1 |
| gpt-5.4-mini | ar_en_SD_008 | ar-en | script_register_locale | 0 | 0 | ['preservation_failure'] | 0 | 1 |
| gpt-5.4-mini | hi_en_SC_003 | hi-en | quote_preservation | 1 | 0 | ['wrong_output_language'] | 1 | 0 |
| gpt-5.4-mini | hi_en_SC_008 | hi-en | quote_preservation | 1 | 0 | ['wrong_output_language'] | 1 | 0 |

## Interpretation

`gpt-5.5` has 20 baseline-fail/contract-pass fixes, 0 first-turn regressions, and 0 resolved-to-unresolved shifts. This supports the clean flagship mitigation claim.

`gpt-5.4-mini` has 11 fixes but 5 first-turn regressions and 4 resolved-to-unresolved shifts. The regressions are concentrated in quote-preservation and script/register/locale rows, not in output-language inference.

Content-preservation avoids first-turn failure on 3 of the 5 `gpt-5.4-mini` regression cases and leaves only 1 unresolved among those regression cases. This reinforces the mechanism result: for the lower-cost current model, the full contract is not uniformly safer than the narrower preservation scaffold.

The resolved-to-unresolved set has 4 `gpt-5.4-mini` cases and 0 `gpt-5.5` cases. The lower-cost result should therefore be worded as bounded token-burden and directional FTGA improvement, with explicit regression risk.
