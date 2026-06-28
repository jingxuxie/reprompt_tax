# Task-Useful Contract-Failure Diagnostic

Generated from first-turn rows in `results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl`.

This diagnostic asks whether first-turn failures are always task failures.
A **task-useful contract failure** is a row where the automatic task
component passes but full first-turn global alignment fails because at
least one interaction-contract component fails. This is conservative
automatic evidence for hidden repair burden, not a replacement for
human/native-speaker validation.

## Overall

| Condition | First-turn failures | Task-useful contract failures | Share of failures | Task+preservation useful failures | Language/script framing failures |
|---|---:|---:|---:|---:|---:|
| baseline | 96 | 31 (8.6% of all rows) | 32.3% | 11 | 11 |
| contract | 61 | 20 (5.6% of all rows) | 32.8% | 1 | 1 |

## By Model And Condition

| Model | Condition | Failures | Task-useful failures | Task+preservation useful | Task noncompletion failures |
|---|---|---:|---:|---:|---:|
| gpt-4.1 | baseline | 28 | 17 | 10 | 11 |
| gpt-4.1 | contract | 8 | 6 | 0 | 2 |
| gpt-4.1-mini | baseline | 29 | 7 | 0 | 22 |
| gpt-4.1-mini | contract | 25 | 7 | 0 | 18 |
| gpt-4.1-nano | baseline | 39 | 7 | 1 | 32 |
| gpt-4.1-nano | contract | 28 | 7 | 1 | 21 |

## By Family And Condition

| Condition | Task family | Failures | Task-useful failures | Task+preservation useful | Task noncompletion failures |
|---|---|---:|---:|---:|---:|
| baseline | Editing preservation | 60 | 10 | 10 | 50 |
| baseline | Quote preservation | 9 | 0 | 0 | 9 |
| baseline | Script/register/locale | 27 | 21 | 1 | 6 |
| contract | Editing preservation | 27 | 0 | 0 | 27 |
| contract | Quote preservation | 8 | 0 | 0 | 8 |
| contract | Script/register/locale | 26 | 20 | 1 | 6 |

## Task-Useful Failure Signatures

| Condition | Task family | Failed components | Count | Share within task-useful failures |
|---|---|---|---:|---:|
| baseline | Editing preservation | language | 10 | 100.0% |
| baseline | Script/register/locale | language | 1 | 4.8% |
| baseline | Script/register/locale | preservation | 20 | 95.2% |
| contract | Script/register/locale | language | 1 | 5.0% |
| contract | Script/register/locale | preservation | 19 | 95.0% |

## Interpretation

Under baseline prompting, 31/96 first-turn failures are task-useful contract failures
(32.3% of failures). Under the Global
Interaction Contract this count falls to 20/61 failures.

The stricter task+preservation useful subset falls from 11
to 1. This is the cleanest automatic
slice for the paper's hidden-tax claim: the response has performed the task
and preserved required spans, but still violates language or script framing.

Most baseline task-useful failures are concentrated in
script/register/locale (21) and
editing-preservation (10) rows. After
the contract, residual task-useful failures are concentrated in
script/register/locale (20) rows,
which keeps the mitigation claim bounded.
