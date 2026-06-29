# Task-Useful Contract-Failure Diagnostic

Generated from first-turn rows in `results/scores/openai_gpt55_stress_v02_pilot40_auto_scores.jsonl`.

This diagnostic asks whether first-turn failures are always task failures.
A **task-useful contract failure** is a row where the automatic task
component passes but full first-turn global alignment fails because at
least one interaction-contract component fails. This is conservative
automatic evidence for hidden repair burden, not a replacement for
human/native-speaker validation.

## Overall

| Condition | First-turn failures | Task-useful contract failures | Share of failures | Task+preservation useful failures | Language/script framing failures |
|---|---:|---:|---:|---:|---:|
| baseline | 8 | 0 (0.0% of all rows) | 0.0% | 0 | 0 |
| contract | 0 | 0 (0.0% of all rows) | 0.0% | 0 | 0 |

## By Model And Condition

| Model | Condition | Failures | Task-useful failures | Task+preservation useful | Task noncompletion failures |
|---|---|---:|---:|---:|---:|
| gpt-5.5 | baseline | 8 | 0 | 0 | 8 |
| gpt-5.5 | contract | 0 | 0 | 0 | 0 |

## By Family And Condition

| Condition | Task family | Failures | Task-useful failures | Task+preservation useful | Task noncompletion failures |
|---|---|---:|---:|---:|---:|
| baseline | Editing preservation | 8 | 0 | 0 | 8 |

## Task-Useful Failure Signatures

| Condition | Task family | Failed components | Count | Share within task-useful failures |
|---|---|---|---:|---:|

No task-useful first-turn failures were observed in this run.

## Interpretation

Under baseline prompting, 0/8 first-turn failures are task-useful contract failures
(0.0% of failures). Under the Global Interaction Contract, there are no first-turn failures in this run.

This run does not show a hidden task-useful failure slice: all observed
first-turn failures are task-noncompletion failures under the automatic
scorer. The result should be read as a bounded pilot diagnostic, not as
evidence that hidden repair burden is absent in the full benchmark.
