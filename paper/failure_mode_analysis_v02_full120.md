# RePromptTax Failure-Mode Analysis

Generated from `results/tables/openai_three_model_stress_v02_full120/`.

## Family-Level Burden

| Task family | Baseline FTGA | Contract FTGA | Baseline failures | Contract failures | Baseline RTT | Contract RTT |
|---|---:|---:|---:|---:|---:|---:|
| Editing preservation | 33.3% | 70.0% | 60/90 | 27/90 | 0.67 | 0.30 |
| Output-language inference | 100.0% | 100.0% | 0/90 | 0/90 | 0.00 | 0.00 |
| Quote preservation | 90.0% | 91.1% | 9/90 | 8/90 | 0.21 | 0.12 |
| Script/register/locale | 70.0% | 71.1% | 27/90 | 26/90 | 0.49 | 0.53 |

## Main Interpretations

- Editing preservation is the dominant baseline burden: across models, baseline first-turn failures occur in 60/90 editing-preservation trajectories, and aggregate FTGA is 33.3%.
- The contract improves editing-preservation FTGA by 63.3 pp for gpt-4.1, 13.3 pp for gpt-4.1-mini, and 33.3 pp for gpt-4.1-nano.
- Output-language inference is saturated in this pilot: aggregate FTGA is 100.0% in baseline and 100.0% under the contract.
- Nano quote-preservation remains a capability boundary: first-turn FTGA is 70.0% in baseline and 73.3% under the contract, but mean RTT falls from 0.63 to 0.37.

## Aggregated First-Turn Failure Types

| Condition | Task family | Failure type | Count | Share of initial failures |
|---|---|---|---:|---:|
| baseline | Editing preservation | script_mismatch | 30 | 50.0% |
| baseline | Editing preservation | task_noncompletion | 50 | 83.3% |
| baseline | Editing preservation | wrong_output_language | 60 | 100.0% |
| baseline | Quote preservation | preservation_failure | 9 | 100.0% |
| baseline | Quote preservation | task_noncompletion | 9 | 100.0% |
| baseline | Script/register/locale | preservation_failure | 26 | 96.3% |
| baseline | Script/register/locale | task_noncompletion | 6 | 22.2% |
| baseline | Script/register/locale | wrong_output_language | 1 | 3.7% |
| contract | Editing preservation | script_mismatch | 7 | 25.9% |
| contract | Editing preservation | task_noncompletion | 27 | 100.0% |
| contract | Editing preservation | wrong_output_language | 27 | 100.0% |
| contract | Quote preservation | preservation_failure | 8 | 100.0% |
| contract | Quote preservation | task_noncompletion | 8 | 100.0% |
| contract | Script/register/locale | preservation_failure | 25 | 96.2% |
| contract | Script/register/locale | task_noncompletion | 6 | 23.1% |
| contract | Script/register/locale | wrong_output_language | 1 | 3.8% |
