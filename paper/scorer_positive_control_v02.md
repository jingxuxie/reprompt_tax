# Scorer Positive-Control Audit v0.2

This no-API audit generates one constrained positive-control response for
each v0.2 benchmark item and feeds it through `scripts/score_auto.py`.
The controls include deterministic required markers, preserved spans,
expected script, and lightweight language markers. They test scorer
over-rejection, not human fluency or native/near-native semantic validity.

## Overall

| Controls | Auto passed | All components passed | Auto failed |
|---:|---:|---:|---:|
| 120 | 120 (100.0%) | 120 (100.0%) | 0 |

## By Task Family

| Family | n | Auto passed | All components passed | Auto failed |
|---|---:|---:|---:|---:|
| editing_preservation | 30 | 30 (100.0%) | 30 (100.0%) | 0 |
| output_language_inference | 30 | 30 (100.0%) | 30 (100.0%) | 0 |
| quote_preservation | 30 | 30 (100.0%) | 30 (100.0%) | 0 |
| script_register_locale | 30 | 30 (100.0%) | 30 (100.0%) | 0 |

## By Language Pair

| Language pair | n | Auto passed | All components passed | Auto failed |
|---|---:|---:|---:|---:|
| ar-en | 40 | 40 (100.0%) | 40 (100.0%) | 0 |
| es-en | 40 | 40 (100.0%) | 40 (100.0%) | 0 |
| hi-en | 40 | 40 (100.0%) | 40 (100.0%) | 0 |

## By Expected Response Language

| Expected language | n | Auto passed | All components passed | Auto failed |
|---|---:|---:|---:|---:|
| Arabic | 20 | 20 (100.0%) | 20 (100.0%) | 0 |
| English | 60 | 60 (100.0%) | 60 (100.0%) | 0 |
| Hindi/Hinglish | 20 | 20 (100.0%) | 20 (100.0%) | 0 |
| Spanish | 20 | 20 (100.0%) | 20 (100.0%) | 0 |

## Interpretation

The scorer accepts 120/120 constrained positive controls, complementing the
known-bad scorer-challenge audit. Together, the two audits test both
directions of deterministic rule plumbing: known failures are rejected,
and constrained known passes are not over-rejected.

Claim boundary: these controls are synthetic templates built to satisfy
the automatic rules. They do not replace LLM-judge checks or completed
human/native review for semantic, register, or cultural validity.
