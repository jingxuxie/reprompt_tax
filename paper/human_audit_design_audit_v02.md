# Human Audit Design Audit

Generated from the blinded launch packet and private answer key. This is
a design-readiness audit only; it is not completed human validation.

## Overview

| Metric | Value |
|---|---:|
| packet_rows | 72 |
| answer_key_rows | 72 |
| language_pairs | 3 |
| task_families | 4 |
| models | 3 |
| conditions | 2 |
| model_condition_language_family_strata | 72 |
| first_turn_only | True |
| packet_private_fields_present | False |
| annotation_fields_blank | True |
| auto_pass_rows | 57 |
| auto_fail_rows | 15 |
| auto_pass_rate | 0.7917 |

## Language Coverage

| Language pair | Rows | Auto pass | Auto fail | Auto pass rate |
|---|---:|---:|---:|---:|
| ar-en | 24 | 16 | 8 | 66.7% |
| es-en | 24 | 18 | 6 | 75.0% |
| hi-en | 24 | 23 | 1 | 95.8% |

## Task-Family Coverage

| Task family | Rows | Auto pass | Auto fail | Auto pass rate |
|---|---:|---:|---:|---:|
| editing_preservation | 18 | 9 | 9 | 50.0% |
| output_language_inference | 18 | 18 | 0 | 100.0% |
| quote_preservation | 18 | 16 | 2 | 88.9% |
| script_register_locale | 18 | 14 | 4 | 77.8% |

## Model-Condition Coverage

| Model | Condition | Rows | Auto pass | Auto fail | Auto pass rate |
|---|---|---:|---:|---:|---:|
| gpt-4.1 | baseline | 12 | 10 | 2 | 83.3% |
| gpt-4.1 | contract | 12 | 11 | 1 | 91.7% |
| gpt-4.1-mini | baseline | 12 | 10 | 2 | 83.3% |
| gpt-4.1-mini | contract | 12 | 8 | 4 | 66.7% |
| gpt-4.1-nano | baseline | 12 | 9 | 3 | 75.0% |
| gpt-4.1-nano | contract | 12 | 9 | 3 | 75.0% |

## Auto-Failure Coverage

| Auto failure type | Sampled rows with type | Sampled auto-fail rows |
|---|---:|---:|
| preservation_failure | 6 | 15 |
| script_mismatch | 4 | 15 |
| task_noncompletion | 11 | 15 |
| wrong_output_language | 9 | 15 |

## Interpretation

The packet covers one first-turn response for every model, condition,
language-pair, and task-family stratum: 72 strata total. The annotator
packet contains no private model, condition, item-id, or automatic-label
fields, and all annotation fields, including `annotator_id`, are blank.
The launch package includes an annotator roster template so completed
validation can tie every filled row to a qualified language/script
annotator. The answer key shows that the sample includes both automatic
passes and automatic failures, so the completed audit can test agreement
rather than only confirm easy cases.

Completed native/near-native annotation is still required before widening
the paper claim beyond automatic scoring plus LLM-judge audit.
