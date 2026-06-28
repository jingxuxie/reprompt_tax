# RePromptTax Results Snapshot

Generated: 2026-06-28

## Paper-Facing Result

The current paper-facing result is the full `RePromptTax-Stress-v0.2`
evaluation: 120 synthetic stress items, 3 language pairs, 4 task families, 10
items per cell, 3 GPT-4.1-family models, and baseline vs Global Interaction
Contract prompting. Repair budget is two follow-up prompts.

Source artifacts:

- benchmark: `data/benchmark_stress_v0.2.jsonl`
- benchmark-quality audit: `paper/benchmark_quality_audit_v02.md`
- full score file: `results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl`
- main tables: `results/tables/openai_three_model_stress_v02_full120/`
- main figures: `results/figures/openai_three_model_stress_v02_full120/`
- failure-mode analysis: `paper/failure_mode_analysis_v02_full120.md`
- item-consistency analysis: `paper/item_consistency_analysis_v02_full120.md`
- scorer-component breakdown: `paper/component_breakdown_v02_full120.md`
- scorer-ablation sensitivity: `paper/scorer_ablation_sensitivity_v02_full120.md`
- error atlas: `paper/error_atlas_v02_full120.md`
- qualitative examples: `paper/qualitative_examples.md`
- paired sign-test sensitivity: `paper/paired_significance_v02_full120.md`
- language-slice analysis: `paper/language_slice_analysis_v02_full120.md`
- repair-dynamics analysis: `paper/repair_dynamics_v02_full120.md`
- experiment ledger: `paper/experiment_ledger_v02.md`
- prompt-control diagnostic: `paper/prompt_control_analysis.md`
- prompt-ablation diagnostic: `paper/prompt_ablation_analysis.md`
- judge agreement analysis: `paper/judge_agreement_analysis_v02_full120.md`
- discovery cue analysis: `paper/discovery_cue_analysis.md`
- human audit design audit: `paper/human_audit_design_audit_v02.md`
- full-v0.2 judge audit: `results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl`

## Main Metrics

| Model | Condition | FTGA | Mean RTT | Token tax | Unresolved | Repair@1 | Repair@2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-4.1-nano | baseline | 67.5% | 0.47 | 1.69x | 5.8% | 74.4% | 82.1% |
| gpt-4.1-nano | contract | 76.7% | 0.33 | 1.34x | 4.2% | 78.6% | 82.1% |
| gpt-4.1-mini | baseline | 75.8% | 0.28 | 1.43x | 0.8% | 89.7% | 96.6% |
| gpt-4.1-mini | contract | 79.2% | 0.24 | 1.27x | 1.7% | 92.0% | 92.0% |
| gpt-4.1 | baseline | 76.7% | 0.28 | 1.43x | 2.5% | 89.3% | 89.3% |
| gpt-4.1 | contract | 93.3% | 0.15 | 1.13x | 4.2% | 37.5% | 37.5% |

## Paired Effects

Paired bootstrap effects compare contract minus baseline on the same 120 items
per model. Positive FTGA means improvement; positive RTT/token-tax reductions
mean lower burden.

| Model | FTGA delta | 95% CI | RTT reduction | 95% CI | Token-tax reduction | 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| gpt-4.1-nano | +9.2 pp | [+4.2, +15.0] | 0.14 | [0.07, 0.23] | 0.35x | [0.23, 0.48] |
| gpt-4.1-mini | +3.3 pp | [+0.8, +6.7] | 0.03 | [0.00, 0.07] | 0.16x | [0.10, 0.23] |
| gpt-4.1 | +16.7 pp | [+10.0, +23.3] | 0.13 | [0.05, 0.22] | 0.30x | [0.19, 0.43] |

Paired sign-test sensitivity over item-level FTGA changes gives 12 improved vs
1 worsened item for `gpt-4.1-nano` (two-sided p=0.0034), 4 vs 0 for
`gpt-4.1-mini` (p=0.1250), and 20 vs 0 for `gpt-4.1` (p<0.0001). This supports
the stronger nano/GPT-4.1 FTGA effects while keeping the mini FTGA claim
directional.

## Language Slices

Language-slice analysis shows that the aggregate mitigation effect is not
uniform across all model/language pairs. Averaged across models, Arabic-English
has the largest FTGA movement (+20.0 pp; 24 improved, 0 worsened, 96 tied
paired items), Spanish-English moves +9.2 pp, and Hindi-English moves +0.0 pp
because baseline FTGA is already high. The clearest slice gains are
`gpt-4.1` on Arabic-English and Spanish-English (+25.0 pp each) and
`gpt-4.1-nano` on Arabic-English (+25.0 pp). The main weak slice is
Spanish-English on `gpt-4.1-mini`, where FTGA delta is +0.0 pp despite lower
token tax.

## Repair Dynamics

Repair-dynamics analysis makes the RTT distribution explicit. For `gpt-4.1`,
first-turn successes rise from 92/120 to 112/120 under the contract; paired RTT
movement is 20 improved, 2 worsened, and 98 tied. For `gpt-4.1-nano`,
first-turn successes rise from 81/120 to 92/120 and unresolved trajectories
drop from 7 to 5. The mini result is modest: 5 improved, 1 worsened, and 114
tied. A residual caveat remains: script/register/locale unresolved cases under
the contract are 11/90, so the prompt does not remove repair failures.

## Token-Burden Caveat

Token tax is a repair-burden ratio, not an absolute API-cost claim. The longer
contract prompt reduces token-tax ratios for all three models, but it increases
absolute total tokens per trajectory in this pilot. See
`paper/token_burden_analysis_v02_full120.md` for absolute token totals.

## Benchmark Quality Audit

The paper-facing stress set has a deterministic release-hygiene audit. It
reports 120 unique user prompts, zero normalized duplicate prompts, required
scoring markers and known-bad-output notes for all rows, preservation spans in
the two preservation-relevant families, and zero email/URL/phone-like/SSN-like
or placeholder privacy markers under the audit regexes. This supports release
hygiene, but it is not a substitute for native-speaker validation.

## Experiment Ledger

The paper-facing saved artifacts contain 1,290 API response rows: 1,218
model-response rows for the main evaluation plus nano prompt-control and
prompt-ablation diagnostics, and 72 judge-audit rows. Provider-reported saved
usage totals 190,463 input tokens and 38,368 output tokens. The ledger
intentionally reports token usage without estimating dollar cost because
provider prices change over time.

## Failure Modes

Editing preservation is the dominant baseline burden: across models, baseline
first-turn failures occur in 60/90 editing-preservation trajectories, and
aggregate FTGA is 33.3%. The contract improves editing-preservation FTGA by
63.3 pp for `gpt-4.1`, 13.3 pp for `gpt-4.1-mini`, and 33.3 pp for
`gpt-4.1-nano`. Output-language inference is saturated at 100.0% FTGA under
both prompts.

`gpt-4.1-nano` remains weaker on exact quote preservation: first-turn FTGA is
70.0% in baseline and 73.3% under the contract, but mean RTT falls from 0.63 to
0.37 and unresolved rate falls from 13.3% to 3.3%.

The generated first-turn error atlas lists 157 first-turn failures and 23
unresolved cases after two repair prompts.

## Item Consistency

The item-consistency supplement separates systematic hard items from one-off
model failures. Under baseline prompting, 40/120 items fail for at least one
model and 27/120 fail for all three models. Under the contract, 35/120 items
still fail for at least one model, but all-model failures fall to 8/120. The
contract reduces the number of failing models on 22/120 items and increases it
on 1/120 item. This supports the mitigation claim while preserving the
residual-failure boundary.

## Scorer Components

Component-level first-turn analysis shows that the contract's gains primarily
come from language, script, and task checks. On paired first-turn rows,
`gpt-4.1` gains +15.8 pp on language checks and +8.3 pp on script checks, while
`gpt-4.1-nano` gains +9.2 pp on task checks. Preservation barely moves for some
models, and register/locale checks are saturated under the current rule set; do
not present that saturation as evidence that nuanced register judgments are
solved.

The scorer-ablation sensitivity supplement relaxes one automatic component at a
time. Relaxing language alone moves aggregate first-turn FTGA from 73.3% to
76.4% in baseline rows and from 83.1% to 83.3% under the contract. Relaxing
preservation is the largest single-component counterfactual, moving baseline
to 78.9% and contract to 88.3%. Dominant editing failures remain multi-component
language/script/task or language/task failures, so the automatic metric is not
driven by one fragile rule.

The task-useful failure diagnostic separates task noncompletion from hidden
interaction-contract burden. Under baseline prompting, 31/96 first-turn failures
already pass the task component, and 11 also pass both task and preservation
checks. Under the contract, the stricter task+preservation useful subset falls
from 11 to 1, while residual task-useful failures concentrate in
script/register/locale rows. Treat this as automatic diagnostic evidence for
hidden repair burden, not as a replacement for human/native-speaker validation.

## Prompt-Control and Prompt-Ablation Diagnostics

A single-model `gpt-4.1-nano` prompt-control diagnostic compares the baseline,
the Global Interaction Contract, and a longer generic helpfulness prompt that
does not mention multilingual, script, or preservation rules. Generic
helpfulness improves FTGA from 67.5% to 75.0%, while the contract reaches
76.7%. Relative to generic helpfulness, the contract adds +1.7 pp FTGA and
0.03x lower token tax, with no additional mean RTT reduction. This is useful
negative/nuance evidence: generic instruction-following scaffolding explains
much of nano's gain. A follow-up content-preservation ablation reaches 80.0%
FTGA, 0.27 mean RTT, and 1.28x token tax on the same 120 items, exceeding the
full contract for nano. The safe claim is therefore not that the Global
Interaction Contract is the best prompt tested, but that the pre-registered
three-model intervention improves the main evaluation and that narrower
content-language/literal-preservation rules appear to drive much of the effect.
See `paper/prompt_control_analysis.md` and `paper/prompt_ablation_analysis.md`.

## Judge Audit

A blinded `gpt-4.1` judge audit covered 72 first-turn full-v0.2 responses: 3
samples for each model/condition/task-family stratum, or 10% of the 720
first-turn trajectories. Agreement with the corrected automatic scorer was
71/72 pass/fail labels (98.6%; Wilson 95% CI 92.5--99.8) with zero parse
errors. The single disagreement was `es_en_SA_007`, where the rule scorer
penalized Spanish framing around English rewrites and the judge accepted the
response. Component agreement is more nuanced: language 71/72, script 71/72,
preservation 69/72, task 71/72, and register/locale 68/72. This supports using
the audit as a scorer sanity check, not as a replacement for native-speaker
validation.

## Claim Boundary

These are preliminary results with automatic scoring plus a 10% stratified
blinded LLM-judge audit. The objective checks for exact-span preservation and
script are reliable, and the judge audit supports the language/task decisions in
the sampled subset. Human or native-speaker audit is still needed before making
strong final paper claims. Safe current claim:

> On a 120-item synthetic stress pilot, three GPT-4.1-family API models exhibit
> measurable re-prompt tax under baseline prompting, especially on implicit
> content-language preservation. A simple Global Interaction Contract improves
> first-turn alignment and reduces turn/token tax on this pilot, but it does not
> remove residual exact-preservation failures. A stratified blinded LLM-judge
> audit supports the automatic pass/fail labels, while native-speaker validation
> remains necessary before stronger final claims.

## Validation

Run the full local gate:

```bash
conda run -n reprompt_tax python scripts/run_submission_checks.py
```

The current build produces `paper/main.pdf`, 4 pages, with no unresolved
citations, undefined references, overfull boxes, or LaTeX errors found in
`paper/main.log`.

## Human Audit Readiness

A balanced 72-row blinded human audit packet has been generated under
`data/human_audit/`. A design audit confirms one first-turn response for each
model/condition/language-pair/task-family stratum, no private model/condition/
item/auto-label fields in the annotator packet, blank annotation fields
including `annotator_id`, and 57 automatic passes plus 15 automatic failures in
the sampled rows. The packet is launch-ready but not completed validation. Any
smoke completed file in the same directory is a plumbing test only and is not
human validation. Completed annotations should first pass
`scripts/validate_completed_human_audit.py` with a filled qualified-annotator
roster; the validator rejects smoke-only files unless `--allow-smoke` is
explicitly used for plumbing tests.

## Real-World Discovery Check

A bounded, aggregate-only WildChat scan over the first 20,000 streamed
conversations found 172 conversations with repair cues among 10,681 multi-turn
conversations, with 219 total cue hits. No raw user or assistant text is
written; the hit metadata contains only hashed conversation IDs, message
indices, cue patterns, and language metadata. A local analysis of the hashed
metadata finds 31 conversations with repeated cue hits, with a maximum of 5 cue
hits in one conversation. The largest unique-conversation categories are generic
repair (81) and wrong output language (48). This is used only as a motivation
check, not a representative prevalence estimate.
