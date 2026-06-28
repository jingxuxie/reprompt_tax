# RePromptTax Failure-Mode Analysis

Generated from `results/tables/openai_three_model_stress60/`.

## Family-Level Burden

| Task family | Baseline FTGA | Contract FTGA | Baseline failures | Contract failures | Baseline RTT | Contract RTT |
|---|---:|---:|---:|---:|---:|---:|
| Editing preservation | 33.3% | 73.3% | 30/45 | 12/45 | 0.67 | 0.27 |
| Output-language inference | 100.0% | 100.0% | 0/45 | 0/45 | 0.00 | 0.00 |
| Quote preservation | 88.9% | 88.9% | 5/45 | 5/45 | 0.31 | 0.18 |
| Script/register/locale | 91.1% | 93.3% | 4/45 | 3/45 | 0.09 | 0.07 |

## Main Interpretations

- Editing preservation is the dominant baseline burden: across models, baseline first-turn failures occur in 30/45 editing-preservation trajectories, and aggregate FTGA is 33.3%.
- The contract improves editing-preservation FTGA by 66.7 pp for gpt-4.1, 20.0 pp for gpt-4.1-mini, and 33.3 pp for gpt-4.1-nano.
- Output-language inference is saturated in this pilot: aggregate FTGA is 100.0% in baseline and 100.0% under the contract.
- Nano quote-preservation remains a capability boundary: first-turn FTGA is 66.7% in baseline and 66.7% under the contract, but mean RTT falls from 0.93 to 0.53.

## Aggregated First-Turn Failure Types

| Condition | Task family | Failure type | Count | Share of initial failures |
|---|---|---|---:|---:|
| baseline | Editing preservation | script_mismatch | 15 | 50.0% |
| baseline | Editing preservation | task_noncompletion | 25 | 83.3% |
| baseline | Editing preservation | wrong_output_language | 30 | 100.0% |
| baseline | Quote preservation | preservation_failure | 5 | 100.0% |
| baseline | Quote preservation | task_noncompletion | 5 | 100.0% |
| baseline | Script/register/locale | preservation_failure | 3 | 75.0% |
| baseline | Script/register/locale | task_noncompletion | 3 | 75.0% |
| baseline | Script/register/locale | wrong_output_language | 1 | 25.0% |
| contract | Editing preservation | script_mismatch | 3 | 25.0% |
| contract | Editing preservation | task_noncompletion | 12 | 100.0% |
| contract | Editing preservation | wrong_output_language | 12 | 100.0% |
| contract | Quote preservation | preservation_failure | 5 | 100.0% |
| contract | Quote preservation | task_noncompletion | 5 | 100.0% |
| contract | Script/register/locale | preservation_failure | 3 | 100.0% |
| contract | Script/register/locale | task_noncompletion | 3 | 100.0% |
