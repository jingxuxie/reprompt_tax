# Efficiency Tradeoff Analysis

This supplement combines first-turn global alignment with absolute saved
token counts across the five full 120-item runs. It reports provider
token counts only; it is not a dollar-cost estimate.

## Model-Condition Surface

| Generation | Model | Condition | FTGA | Mean RTT | Unresolved | Mean first-turn tokens | Mean total tokens | Mean token tax | Total tokens |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| GPT-4.1 family | gpt-4.1 | baseline | 76.7% | 0.283 | 2.5% | 81.5 | 132.7 | 1.434x | 15924 |
| GPT-4.1 family | gpt-4.1 | contract | 93.3% | 0.150 | 4.2% | 223.4 | 256.3 | 1.134x | 30754 |
| GPT-4.1 family | gpt-4.1-mini | baseline | 75.8% | 0.275 | 0.8% | 76.8 | 120.9 | 1.432x | 14510 |
| GPT-4.1 family | gpt-4.1-mini | contract | 79.2% | 0.242 | 1.7% | 227.4 | 293.2 | 1.272x | 35179 |
| GPT-4.1 family | gpt-4.1-nano | baseline | 67.5% | 0.467 | 5.8% | 80.2 | 139.3 | 1.693x | 16711 |
| GPT-4.1 family | gpt-4.1-nano | contract | 76.7% | 0.325 | 4.2% | 226.9 | 308.1 | 1.341x | 36971 |
| GPT-5.x family | gpt-5.4-mini | baseline | 80.0% | 0.250 | 2.5% | 81.4 | 128.4 | 1.379x | 15412 |
| GPT-5.x family | gpt-5.4-mini | contract | 85.0% | 0.250 | 5.0% | 223.5 | 280.0 | 1.241x | 33604 |
| GPT-5.x family | gpt-5.5 | baseline | 81.7% | 0.225 | 1.7% | 122.8 | 164.3 | 1.278x | 19716 |
| GPT-5.x family | gpt-5.5 | contract | 98.3% | 0.017 | 0.0% | 274.0 | 278.8 | 1.016x | 33451 |

## Paired Baseline Minus Contract Effects

Positive token-tax reduction means lower normalized repair burden. Positive
total-token reduction would mean fewer absolute tokens; negative values mean
the longer contract uses more absolute tokens.

| Generation | Model | FTGA delta | RTT reduction | Token-tax reduction | Mean total-token reduction | Mean extra-token reduction | Sum total-token reduction |
|---|---|---:|---:|---:|---:|---:|---:|
| GPT-4.1 family | gpt-4.1 | +16.7 pp | +0.133 | +0.300x | -123.6 | +18.3 | -14830 |
| GPT-4.1 family | gpt-4.1-mini | +3.3 pp | +0.033 | +0.159x | -172.2 | -21.6 | -20669 |
| GPT-4.1 family | gpt-4.1-nano | +9.2 pp | +0.142 | +0.351x | -168.8 | -22.2 | -20260 |
| GPT-5.x family | gpt-5.4-mini | +5.0 pp | +0.000 | +0.138x | -151.6 | -9.5 | -18192 |
| GPT-5.x family | gpt-5.5 | +16.7 pp | +0.208 | +0.262x | -114.5 | +36.8 | -13735 |

## Interpretation

The Global Interaction Contract lowers normalized token tax for every full-run model,
but it increases absolute total tokens for every full-run model because the system prompt is longer.
This keeps the paper's token-tax claim scoped to repair burden rather than API-cost savings.

`gpt-5.5` contract is the strongest alignment point: 98.3% FTGA, 0.017 mean RTT, and 1.016x token tax.
However, compared with its baseline, it still uses 114.5 more
absolute tokens per item on average while saving
36.8 repair tokens after the first turn.

`gpt-5.4-mini` shows the lower-cost-current-model boundary: token tax falls by 0.138x,
but absolute total tokens increase by 151.6 per item
and unresolved trajectories increase. This supports a deployment-diagnostic framing rather than a simple cost-saving claim.
