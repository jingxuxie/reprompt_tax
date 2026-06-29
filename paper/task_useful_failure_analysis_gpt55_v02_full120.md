# Task-Useful Contract-Failure Diagnostic

Generated from first-turn rows in `results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl`.

This diagnostic asks whether first-turn failures are always task failures.
A **task-useful contract failure** is a row where the automatic task
component passes but full first-turn global alignment fails because at
least one interaction-contract component fails. This is conservative
automatic evidence for hidden repair burden, not a replacement for
human/native-speaker validation.

## Overall

| Condition | First-turn failures | Task-useful contract failures | Share of failures | Task+preservation useful failures | Language/script framing failures |
|---|---:|---:|---:|---:|---:|
| baseline | 22 | 2 (1.7% of all rows) | 9.1% | 2 | 2 |
| contract | 2 | 2 (1.7% of all rows) | 100.0% | 2 | 2 |

## By Model And Condition

| Model | Condition | Failures | Task-useful failures | Task+preservation useful | Task noncompletion failures |
|---|---|---:|---:|---:|---:|
| gpt-5.5 | baseline | 22 | 2 | 2 | 20 |
| gpt-5.5 | contract | 2 | 2 | 2 | 0 |

## By Family And Condition

| Condition | Task family | Failures | Task-useful failures | Task+preservation useful | Task noncompletion failures |
|---|---|---:|---:|---:|---:|
| baseline | Editing preservation | 20 | 1 | 1 | 19 |
| baseline | Output-language inference | 1 | 0 | 0 | 1 |
| baseline | Script/register/locale | 1 | 1 | 1 | 0 |
| contract | Editing preservation | 2 | 2 | 2 | 0 |

## Task-Useful Failure Signatures

| Condition | Task family | Failed components | Count | Share within task-useful failures |
|---|---|---|---:|---:|
| baseline | Editing preservation | language+script | 1 | 100.0% |
| baseline | Script/register/locale | language | 1 | 100.0% |
| contract | Editing preservation | language | 2 | 100.0% |

## Interpretation

Under baseline prompting, 2/22 first-turn failures are task-useful contract failures
(9.1% of failures). Under the Global Interaction Contract this count falls to 2/2 failures.

The stricter task+preservation useful subset falls from 2
to 2. This is the cleanest automatic
slice for the paper's hidden-tax claim: the response has performed the task
and preserved required spans, but still violates language or script framing.

Most baseline task-useful failures are concentrated in
Editing preservation (1), and Script/register/locale (1) rows. After
the contract, residual task-useful failures are concentrated in
Editing preservation (2) rows,
which keeps the mitigation claim bounded.
