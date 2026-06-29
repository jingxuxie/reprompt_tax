# GPT-5.5 Judge Refresh

This artifact reruns the same 72-row blinded first-turn judge-audit sample
with `gpt-5.5` and compares it with the saved `gpt-4.1` judge audit.
The sample is exactly paired: 3 rows for each model/condition/task-family
stratum from the full 120-item stress evaluation.

## Summary

| Judge | Auto agreement | Wilson 95% CI | Auto pass | Judge pass | Parse errors | Tokens |
|---|---:|---:|---:|---:|---:|---:|
| gpt-4.1 | 71/72 (98.6%) | [92.5, 99.8] | 64 | 65 | 0 | 25946 |
| gpt-5.5 | 70/72 (97.2%) | [90.4, 99.2] | 64 | 62 | 0 | 31047 |

## Judge-to-Judge Agreement

| Judge A | Judge B | Agreement | Wilson 95% CI | Both pass | Both fail | A pass / B fail | A fail / B pass |
|---|---|---:|---:|---:|---:|---:|---:|
| gpt-4.1 | gpt-5.5 | 69/72 (95.8%) | [88.5, 98.6] | 62 | 7 | 3 | 0 |

## Disagreement Rows

| Item | Model | Condition | Family | Auto | GPT-4.1 judge | GPT-5.5 judge | GPT-5.5 reason |
|---|---|---|---|---:|---:|---:|---|
| es_en_SA_007 | gpt-4.1 | baseline | editing_preservation | False | True | False | The response provides suitable English rewrites, but the surrounding explanation is in Spanish instead of keeping the response in English. |
| hi_en_SA_009 | gpt-4.1-mini | contract | editing_preservation | True | True | False | The rewrite is in English and preserves the meaning, but it is not phrased as a polite workplace request. |
| hi_en_SC_008 | gpt-4.1-nano | baseline | quote_preservation | True | True | False | Response preserves the quoted headings in Latin-script Hindi/Hinglish, but invents unsupported details and is not a concise summary of the given sentence. |

## Interpretation

The original `gpt-4.1` judge agrees with the automatic scorer on 71/72
pass/fail labels, while the `gpt-5.5` judge agrees on 70/72.
The two judges agree with each other on 69/72 pass/fail labels.
The GPT-5.5 judge is stricter on three rows: it agrees with the automatic scorer
that Spanish framing around English rewrites should fail, and it newly flags
one polite-request register issue plus one over-informative quote-summary issue.
This refresh strengthens the methodological caveat: LLM judges are useful scorer
sanity checks, but they do not replace native/near-native validation.
