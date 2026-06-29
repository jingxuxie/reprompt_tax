# Scorer Challenge Audit v0.2

This no-API audit feeds synthetic known-bad responses through the real
`scripts/score_auto.py` scorer for every v0.2 benchmark item. It checks
whether the deterministic scorer catches benchmark-wide challenge probes
for forbidden markers, omitted required markers, wrong script/language,
dropped preservation spans, and over-formal register. It is a scorer
stress test, not native/near-native validation.

## Overall

| Challenges | Auto failed | Expected signal detected | Auto passed |
|---:|---:|---:|---:|
| 390 | 390 (100.0%) | 390 (100.0%) | 0 |

## By Challenge Type

| Challenge | n | Auto failed | Expected signal detected | Top failure types |
|---|---:|---:|---:|---|
| forbidden_marker | 60 | 60 (100.0%) | 60 (100.0%) | task_noncompletion:60;wrong_output_language:30;register_locale_mismatch:30 |
| overformal_register | 30 | 30 (100.0%) | 30 (100.0%) | task_noncompletion:30;register_locale_mismatch:30;wrong_output_language:23;script_mismatch:10 |
| preservation_drop | 60 | 60 (100.0%) | 60 (100.0%) | preservation_failure:60;task_noncompletion:60 |
| required_marker_omission | 120 | 120 (100.0%) | 120 (100.0%) | task_noncompletion:120;preservation_failure:60 |
| wrong_script | 120 | 120 (100.0%) | 120 (100.0%) | wrong_output_language:120;script_mismatch:120;task_noncompletion:120;preservation_failure:60 |

## By Task Family

| Family | n | Auto failed | Expected signal detected |
|---|---:|---:|---:|
| editing_preservation | 90 | 90 (100.0%) | 90 (100.0%) |
| output_language_inference | 60 | 60 (100.0%) | 60 (100.0%) |
| quote_preservation | 90 | 90 (100.0%) | 90 (100.0%) |
| script_register_locale | 150 | 150 (100.0%) | 150 (100.0%) |

## By Language Pair

| Language pair | n | Auto failed | Expected signal detected |
|---|---:|---:|---:|
| ar-en | 130 | 130 (100.0%) | 130 (100.0%) |
| es-en | 130 | 130 (100.0%) | 130 (100.0%) |
| hi-en | 130 | 130 (100.0%) | 130 (100.0%) |

## Interpretation

The synthetic challenge suite is intentionally adversarial and narrow: it
tests whether known-bad perturbations trigger deterministic failure
components, not whether fluent real model answers are culturally or
pragmatically correct. Passing this audit supports using the scorer as
a conservative benchmark triage tool, while the human/native review
gates remain necessary for stronger validation claims.
