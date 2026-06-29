# Current-Model Residual Error Analysis

This artifact inspects the saved full 120-item `gpt-5.4-mini` and
`gpt-5.5` refresh runs. It is generated from trajectory metrics and
auto-score rows; it makes no new API calls.

## Topline

| Model | Condition | First-turn failures | Unresolved | Failure-type counts |
|---|---|---:|---:|---|
| gpt-5.4-mini | baseline | 24/120 (20.0%) | 3 (2.5%) | wrong_output_language=21; script_mismatch=10; task_noncompletion=10; preservation_failure=3 |
| gpt-5.4-mini | contract | 18/120 (15.0%) | 6 (5.0%) | wrong_output_language=12; task_noncompletion=9; preservation_failure=6; script_mismatch=1 |
| gpt-5.5 | baseline | 22/120 (18.3%) | 2 (1.7%) | wrong_output_language=21; task_noncompletion=20; script_mismatch=10 |
| gpt-5.5 | contract | 2/120 (1.7%) | 0 (0.0%) | wrong_output_language=2 |

## Paired Transitions

| Model | Both pass | Baseline fail -> contract pass | Baseline pass -> contract fail | Both fail | RTT improved | RTT worsened | RTT tied |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-5.4-mini | 91 | 11 | 5 | 13 | 11 | 6 | 103 |
| gpt-5.5 | 98 | 20 | 0 | 2 | 21 | 0 | 99 |

## Interpretation

`gpt-5.5` has 22 baseline first-turn failures, of which 20 are editing-preservation rows. Under the contract it has only 2 first-turn failures and 0 unresolved trajectories.
The paired transition table shows 20 baseline failures fixed by the contract, 0 first-turn regressions, and 2 items that fail on both prompts.
Both contract residuals are Spanish-English editing-preservation rows with wrong-output-language failures, and both repair in one turn.

`gpt-5.4-mini` is more mixed: baseline has 24 first-turn failures and 3 unresolved trajectories, while contract has 18 first-turn failures and 6 unresolved trajectories.
The contract fixes 11 baseline failures but introduces 5 first-turn regressions and leaves 13 both-prompt failures.
This is why the low-cost current-model claim should emphasize bounded FTGA and token-tax improvement, not universal repair improvement.

The current-model residuals preserve the main claim boundary: the contract sharply reduces GPT-5.5 burden,
but it does not eliminate first-turn misalignment; on the lower-cost current model, residual failures remain spread across
editing preservation, quote preservation, and script/register/locale rows.

## Contract Residual Cases

| Model | Item | Language | Family | RTT | Unresolved | First failure types |
|---|---|---|---|---:|---:|---|
| gpt-5.4-mini | `es_en_SA_001` | es-en | editing_preservation | 1 | 0 | wrong_output_language,task_noncompletion |
| gpt-5.4-mini | `es_en_SA_002` | es-en | editing_preservation | 1 | 0 | wrong_output_language,task_noncompletion |
| gpt-5.4-mini | `es_en_SA_003` | es-en | editing_preservation | 1 | 0 | wrong_output_language,task_noncompletion |
| gpt-5.4-mini | `es_en_SA_004` | es-en | editing_preservation | 1 | 0 | wrong_output_language,task_noncompletion |
| gpt-5.4-mini | `es_en_SA_006` | es-en | editing_preservation | 1 | 0 | wrong_output_language,task_noncompletion |
| gpt-5.4-mini | `es_en_SA_007` | es-en | editing_preservation | 1 | 0 | wrong_output_language |
| gpt-5.4-mini | `es_en_SA_008` | es-en | editing_preservation | 1 | 0 | wrong_output_language |
| gpt-5.4-mini | `es_en_SA_009` | es-en | editing_preservation | 1 | 0 | wrong_output_language,task_noncompletion |
| gpt-5.4-mini | `es_en_SA_010` | es-en | editing_preservation | 1 | 0 | wrong_output_language,task_noncompletion |
| gpt-5.4-mini | `es_en_SD_008` | es-en | script_register_locale | 3 | 1 | preservation_failure |
| gpt-5.4-mini | `es_en_SD_010` | es-en | script_register_locale | 1 | 0 | preservation_failure |
| gpt-5.4-mini | `hi_en_SC_003` | hi-en | quote_preservation | 3 | 1 | wrong_output_language |
| gpt-5.4-mini | `hi_en_SC_008` | hi-en | quote_preservation | 3 | 1 | wrong_output_language |
| gpt-5.4-mini | `hi_en_SD_008` | hi-en | script_register_locale | 3 | 1 | preservation_failure |
| gpt-5.4-mini | `ar_en_SA_003` | ar-en | editing_preservation | 1 | 0 | wrong_output_language,script_mismatch,task_noncompletion |
| gpt-5.4-mini | `ar_en_SD_006` | ar-en | script_register_locale | 3 | 1 | preservation_failure |
| gpt-5.4-mini | `ar_en_SD_007` | ar-en | script_register_locale | 1 | 0 | preservation_failure,task_noncompletion |
| gpt-5.4-mini | `ar_en_SD_008` | ar-en | script_register_locale | 3 | 1 | preservation_failure |
| gpt-5.5 | `es_en_SA_004` | es-en | editing_preservation | 1 | 0 | wrong_output_language |
| gpt-5.5 | `es_en_SA_009` | es-en | editing_preservation | 1 | 0 | wrong_output_language |

## Contract Failure Families

| Model | Family | First-turn failures | Unresolved | Failure-type counts |
|---|---|---:|---:|---|
| gpt-5.4-mini | editing_preservation | 10/30 | 0 | wrong_output_language=10; task_noncompletion=8; script_mismatch=1 |
| gpt-5.4-mini | quote_preservation | 2/30 | 2 | wrong_output_language=2 |
| gpt-5.4-mini | script_register_locale | 6/30 | 4 | preservation_failure=6; task_noncompletion=1 |
| gpt-5.5 | editing_preservation | 2/30 | 0 | wrong_output_language=2 |
