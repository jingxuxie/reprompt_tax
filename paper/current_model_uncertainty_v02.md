# Current-Model Uncertainty And Claim Scope

This diagnostic combines paired bootstrap intervals from
`paired_contract_effects_by_model.csv` with exact paired sign tests from
`paired_significance_by_model.csv` for the two full-120 GPT-5.x refresh
runs. It makes no API calls. The intervals are item-bootstrap intervals
over the 120 synthetic paired items, not population confidence intervals,
and they do not replace native/near-native validation.

## Model-Level Effects

| Model | FTGA delta, 95% interval | FTGA sign test | RTT reduction, 95% interval | Token-tax reduction, 95% interval | Unresolved reduction, 95% interval | Claim scope |
|---|---:|---|---:|---:|---:|---|
| gpt-5.4-mini | +5.0 pp [-0.8, +11.7] | 11 improved / 5 worsened / 104 tied; p=0.2101 | +0.000 [-0.117, +0.117] | +0.138x [+0.010, +0.269] | -2.5 pp [-6.7, +0.8] | bounded_token_tax_effect_directional_ftga |
| gpt-5.5 | +16.7 pp [+10.0, +24.2] | 20 improved / 0 worsened / 100 tied; p=0.0000019 | +0.208 [+0.125, +0.308] | +0.262x [+0.164, +0.374] | +1.7 pp [+0.0, +4.2] | headline_current_model_effect |

## Interpretation

The `gpt-5.5` headline survives both bootstrap and exact paired sign-test checks: FTGA improves by 16.7 pp with a [10.0, 24.2] pp item-bootstrap interval, and the paired FTGA sign test has 20 improved, 0 worsened, 100 tied items (p=0.0000019). RTT and token-tax reductions are also one-sided in the observed paired signs.

The `gpt-5.4-mini` FTGA interval crosses zero: FTGA improves by 5.0 pp, but the interval is [-0.8, 11.7] pp and the paired sign test is 11 improved versus 5 worsened (p=0.2101). The token-tax interval remains positive for `gpt-5.4-mini` ([0.010, 0.269]x; p=0.0023), so the lower-cost current-model claim should emphasize token-burden reduction and directional FTGA, not universal repair improvement.

Claim boundary: this artifact strengthens the current-model statistical sensitivity story, but it remains automatic-scoring evidence on a synthetic stress pilot. Native/near-native audit labels are still required before stronger human-validation claims.
