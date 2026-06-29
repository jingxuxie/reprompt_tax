# Contract Benefit Decomposition

This artifact decomposes first-turn contract fixes and regressions across
all five full 120-item model runs. It uses saved trajectory metrics only;
it makes no API calls and does not replace native/near-native validation.

## Overall

| Pairs | Both pass | Both fail | Fixes | Regressions | Net first-turn gain |
|---:|---:|---:|---:|---:|---:|
| 600 | 452 | 75 | 67 | 6 | 61 |

## By Task Family

| Task family | Pairs | Fixes | Regressions | Net gain | Fix share | Net share |
|---|---:|---:|---:|---:|---:|---:|
| editing_preservation | 150 | 61 | 0 | 61 | 91.0% | 100.0% |
| output_language_inference | 150 | 1 | 0 | 1 | 1.5% | 1.6% |
| quote_preservation | 150 | 1 | 2 | -1 | 1.5% | -1.6% |
| script_register_locale | 150 | 4 | 4 | 0 | 6.0% | 0.0% |

## By Generation

| Generation | Pairs | Fixes | Regressions | Net gain | Fix share |
|---|---:|---:|---:|---:|---:|
| GPT-4.1 family | 360 | 36 | 1 | 35 | 53.7% |
| GPT-5.x family | 240 | 31 | 5 | 26 | 46.3% |

## By Language Pair

| Language pair | Pairs | Fixes | Regressions | Net gain | Fix share |
|---|---:|---:|---:|---:|---:|
| ar-en | 200 | 43 | 2 | 41 | 64.2% |
| es-en | 200 | 20 | 1 | 19 | 29.9% |
| hi-en | 200 | 4 | 3 | 1 | 6.0% |

## By Generation And Family

| Generation | Task family | Pairs | Fixes | Regressions | Net gain |
|---|---|---:|---:|---:|---:|
| GPT-4.1 family | editing_preservation | 90 | 33 | 0 | 33 |
| GPT-4.1 family | output_language_inference | 90 | 0 | 0 | 0 |
| GPT-4.1 family | quote_preservation | 90 | 1 | 0 | 1 |
| GPT-4.1 family | script_register_locale | 90 | 2 | 1 | 1 |
| GPT-5.x family | editing_preservation | 60 | 28 | 0 | 28 |
| GPT-5.x family | output_language_inference | 60 | 1 | 0 | 1 |
| GPT-5.x family | quote_preservation | 60 | 0 | 2 | -2 |
| GPT-5.x family | script_register_locale | 60 | 2 | 3 | -1 |

## Interpretation

Across all five full-run models, the contract produces 67 first-turn
fixes and 6 first-turn regressions, for a net first-turn gain of 61
model-item pairs.

Editing preservation accounts for 61 of 67 fixes (91.0%) and zero
regressions. Its +61 net gain exactly equals the overall +61 net
first-turn gain. Output-language inference adds one net fix, quote
preservation contributes one net regression, and script/register/locale
is net zero.

This supports the paper's mechanism claim: the Global Interaction
Contract mainly reduces implicit editing-preservation failures rather
than uniformly improving every multilingual task family.

Claim boundary: this is automatic-score decomposition over a synthetic
stress pilot. It strengthens the mechanism story but does not unlock
native/near-native validation claims.
