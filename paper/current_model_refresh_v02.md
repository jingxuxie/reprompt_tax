# Current-Model Refresh

This artifact summarizes the bounded current-model follow-up runs.
`gpt-5.4-mini` and `gpt-5.5` are full 120-item baseline-vs-contract
runs. The earlier GPT-5.5 40-item stratified/enriched pilot is retained
only as a development smoke check, not as the paper-facing result.

## Main Table

| Generation | Model | Scope | N | Baseline FTGA | Contract FTGA | Delta | Baseline RTT | Contract RTT | Token-tax delta | Unresolved delta | FTGA sign p |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GPT-4.1 family | gpt-4.1-nano | full120 | 120 | 67.5% | 76.7% | +9.2 pp | 0.467 | 0.325 | +0.351x | +1.7 pp | 0.00341796875 |
| GPT-4.1 family | gpt-4.1-mini | full120 | 120 | 75.8% | 79.2% | +3.3 pp | 0.275 | 0.242 | +0.159x | -0.8 pp | 0.125 |
| GPT-4.1 family | gpt-4.1 | full120 | 120 | 76.7% | 93.3% | +16.7 pp | 0.283 | 0.150 | +0.300x | -1.7 pp | 1.9073486328125e-06 |
| GPT-5.x family | gpt-5.4-mini | full120 | 120 | 80.0% | 85.0% | +5.0 pp | 0.250 | 0.250 | +0.138x | -2.5 pp | 0.210113525390625 |
| GPT-5.x family | gpt-5.5 | full120 | 120 | 81.7% | 98.3% | +16.7 pp | 0.225 | 0.017 | +0.262x | +1.7 pp | 1.9073486328125e-06 |

## API Usage

| Artifact | API calls | Input tokens | Output tokens | Total tokens |
|---|---:|---:|---:|---:|
| gpt-5.4-mini full120 | 291 | 40286 | 8730 | 49016 |
| gpt-5.5 full120 | 267 | 34172 | 18995 | 53167 |

## Interpretation

On the full 120-item run, `gpt-5.4-mini` improves FTGA from 80.0% to 85.0% (+5.0 pp) and reduces mean token tax by 0.138x. The FTGA sign test is not decisive
(p=0.210113525390625), while token-tax reduction is stronger (p=0.002315700054168701).
The unresolved rate moves from 2.5% to 5.0%,
so the mitigation claim for this model should emphasize lower token burden and bounded FTGA gain, not universal repair improvement.

On the full 120-item GPT-5.5 run, FTGA rises from 81.7% to 98.3% (+16.7 pp; sign-test p=1.9073486328125e-06).
Mean RTT falls from 0.225 to 0.017,
and token tax falls by 0.262x.
The contract leaves two first-turn failures but no unresolved trajectories.
This makes GPT-5.5 the cleanest headline current-model result: RePromptTax persists on the current flagship, and the contract sharply reduces it.

A scorer-coverage fix added `data are insufficient` as an accepted correction for the three `*_SB_001` grammar items.
That fix affects the GPT-5.5 runs, where the model used this valid correction; no saved GPT-4.1-family full-run output used this phrase.
