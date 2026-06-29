# Current-Model Human Audit Design Audit

Generated from the blinded launch packet and private answer key. This is
a design-readiness audit only; it is not completed human validation.

## Overview

| Metric | Value |
|---|---:|
| packet_rows | 48 |
| answer_key_rows | 48 |
| language_pairs | 3 |
| task_families | 4 |
| models | 2 |
| conditions | 2 |
| model_condition_language_family_strata | 48 |
| first_turn_only | True |
| packet_private_fields_present | False |
| annotation_fields_blank | True |
| auto_pass_rows | 32 |
| auto_fail_rows | 16 |
| auto_pass_rate | 0.6667 |

## Language Coverage

| Language pair | Rows | Auto pass | Auto fail | Auto pass rate |
|---|---:|---:|---:|---:|
| ar-en | 16 | 11 | 5 | 68.8% |
| es-en | 16 | 10 | 6 | 62.5% |
| hi-en | 16 | 11 | 5 | 68.8% |

## Task-Family Coverage

| Task family | Rows | Auto pass | Auto fail | Auto pass rate |
|---|---:|---:|---:|---:|
| editing_preservation | 12 | 5 | 7 | 41.7% |
| output_language_inference | 12 | 11 | 1 | 91.7% |
| quote_preservation | 12 | 11 | 1 | 91.7% |
| script_register_locale | 12 | 5 | 7 | 41.7% |

## Model-Condition Coverage

| Model | Condition | Rows | Auto pass | Auto fail | Auto pass rate |
|---|---|---:|---:|---:|---:|
| gpt-5.4-mini | baseline | 12 | 7 | 5 | 58.3% |
| gpt-5.4-mini | contract | 12 | 6 | 6 | 50.0% |
| gpt-5.5 | baseline | 12 | 8 | 4 | 66.7% |
| gpt-5.5 | contract | 12 | 11 | 1 | 91.7% |

## Auto-Failure Coverage

| Auto failure type | Sampled rows with type | Sampled auto-fail rows |
|---|---:|---:|
| preservation_failure | 6 | 16 |
| script_mismatch | 3 | 16 |
| task_noncompletion | 6 | 16 |
| wrong_output_language | 9 | 16 |

## Interpretation

The packet covers one first-turn response for every model, condition,
language-pair, and task-family stratum: 48 strata total. The annotator
packet contains no private model, condition, item-id, or automatic-label
fields, and all annotation fields, including `annotator_id`, are blank.
The launch package includes an annotator roster template so completed
validation can tie every filled row to a qualified language/script
annotator. The answer key shows that the sample includes both automatic
passes and automatic failures, so the completed audit can test agreement
rather than only confirm easy cases.

Completed native/near-native annotation is still required before widening
the paper claim beyond automatic scoring plus LLM-judge audit.
