# Judge Agreement Analysis

Generated from `results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl`
and first-turn component labels in
`results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl`.

The judge is an LLM audit, not a native-speaker human audit. These numbers
support scorer sanity checks but do not replace native/near-native validation.

## Pass/Fail Agreement

| n | Agreement | Wilson 95% CI | Auto pass | Judge pass | Auto fail / judge pass | Auto pass / judge fail | Parse errors |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 72 | 71/72 (98.6%) | [92.5, 99.8] | 64 (88.9%) | 65 (90.3%) | 1 | 0 | 0 |

## Pass/Fail Agreement By Family

| Task family | n | Agreement | Wilson 95% CI | Auto pass | Judge pass |
|---|---:|---:|---:|---:|---:|
| editing_preservation | 18 | 17/18 (94.4%) | [74.2, 99.0] | 13 | 14 |
| output_language_inference | 18 | 18/18 (100.0%) | [82.4, 100.0] | 18 | 18 |
| quote_preservation | 18 | 18/18 (100.0%) | [82.4, 100.0] | 17 | 17 |
| script_register_locale | 18 | 18/18 (100.0%) | [82.4, 100.0] | 16 | 16 |

## Component Agreement

| Component | Agreement | Wilson 95% CI | Auto pass | Judge pass | Auto fail / judge pass | Auto pass / judge fail |
|---|---:|---:|---:|---:|---:|---:|
| language | 71/72 (98.6%) | [92.5, 99.8] | 67 | 68 | 1 | 0 |
| script | 71/72 (98.6%) | [92.5, 99.8] | 70 | 69 | 0 | 1 |
| preservation | 69/72 (95.8%) | [88.5, 98.6] | 69 | 66 | 0 | 3 |
| task | 71/72 (98.6%) | [92.5, 99.8] | 68 | 67 | 0 | 1 |
| register_locale | 68/72 (94.4%) | [86.6, 97.8] | 72 | 68 | 0 | 4 |

## Pass/Fail Disagreements

| Item | Model | Condition | Family | Language pair | Auto pass | Judge pass | Judge reason |
|---|---|---|---|---|---:|---:|---|
| es_en_SA_007 | gpt-4.1 | baseline | editing_preservation | es-en | False | True | The assistant provided improved English versions as requested, maintaining politeness and content. |

## Interpretation

The pass/fail agreement is 71/72 (98.6%; Wilson 95% CI 92.5--99.8).
The single pass/fail disagreement is an editing-preservation case where
the automatic scorer rejects Spanish framing around English rewrites and
the judge accepts the response.

Component agreement is more nuanced than the headline pass/fail number:
preservation agreement is 69/72 and register/locale agreement is 68/72.
This supports the current conservative claim boundary: use the judge audit
as a scorer sanity check, while keeping native/near-native audit as a
required next step before stronger final claims.
