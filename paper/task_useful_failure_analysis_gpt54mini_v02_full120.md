# Task-Useful Contract-Failure Diagnostic

Generated from first-turn rows in `results/scores/openai_gpt54mini_stress_v02_full120_auto_scores.jsonl`.

This diagnostic asks whether first-turn failures are always task failures.
A **task-useful contract failure** is a row where the automatic task
component passes but full first-turn global alignment fails because at
least one interaction-contract component fails. This is conservative
automatic evidence for hidden repair burden, not a replacement for
human/native-speaker validation.

## Overall

| Condition | First-turn failures | Task-useful contract failures | Share of failures | Task+preservation useful failures | Language/script framing failures |
|---|---:|---:|---:|---:|---:|
| baseline | 24 | 14 (11.7% of all rows) | 58.3% | 11 | 11 |
| contract | 18 | 9 (7.5% of all rows) | 50.0% | 4 | 4 |

## By Model And Condition

| Model | Condition | Failures | Task-useful failures | Task+preservation useful | Task noncompletion failures |
|---|---|---:|---:|---:|---:|
| gpt-5.4-mini | baseline | 24 | 14 | 11 | 10 |
| gpt-5.4-mini | contract | 18 | 9 | 4 | 9 |

## By Family And Condition

| Condition | Task family | Failures | Task-useful failures | Task+preservation useful | Task noncompletion failures |
|---|---|---:|---:|---:|---:|
| baseline | Editing preservation | 20 | 10 | 10 | 10 |
| baseline | Script/register/locale | 4 | 4 | 1 | 0 |
| contract | Editing preservation | 10 | 2 | 2 | 8 |
| contract | Quote preservation | 2 | 2 | 2 | 0 |
| contract | Script/register/locale | 6 | 5 | 0 | 1 |

## Task-Useful Failure Signatures

| Condition | Task family | Failed components | Count | Share within task-useful failures |
|---|---|---|---:|---:|
| baseline | Editing preservation | language+script | 10 | 100.0% |
| baseline | Script/register/locale | language | 1 | 25.0% |
| baseline | Script/register/locale | preservation | 3 | 75.0% |
| contract | Editing preservation | language | 2 | 100.0% |
| contract | Quote preservation | language | 2 | 100.0% |
| contract | Script/register/locale | preservation | 5 | 100.0% |

## Interpretation

Under baseline prompting, 14/24 first-turn failures are task-useful contract failures
(58.3% of failures). Under the Global Interaction Contract this count falls to 9/18 failures.

The stricter task+preservation useful subset falls from 11
to 4. This is the cleanest automatic
slice for the paper's hidden-tax claim: the response has performed the task
and preserved required spans, but still violates language or script framing.

Most baseline task-useful failures are concentrated in
Editing preservation (10), and Script/register/locale (4) rows. After
the contract, residual task-useful failures are concentrated in
Script/register/locale (5), Editing preservation (2), and 1 other families rows,
which keeps the mitigation claim bounded.
