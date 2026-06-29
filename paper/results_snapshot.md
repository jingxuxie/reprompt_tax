# RePromptTax Results Snapshot

Generated: 2026-06-28

## Paper-Facing Result

The current paper-facing result is the full `RePromptTax-Stress-v0.2`
evaluation: 120 synthetic stress items, 3 language pairs, 4 task families, 10
items per cell, GPT-4.1-family and GPT-5.x-family model runs, and baseline vs
Global Interaction Contract prompting. Repair budget is two follow-up prompts.

Source artifacts:

- benchmark: `data/benchmark_stress_v0.2.jsonl`
- benchmark-quality audit: `paper/benchmark_quality_audit_v02.md`
- v0.3 coverage scaffold: `data/benchmark_stress_v0.3_expansion.jsonl`,
  `paper/coverage_expansion_v03.md`
- v0.3 native-review launch packet:
  `data/coverage_native_review_v03/`,
  `paper/coverage_native_review_design_v03.md`
- v0.3 coverage smoke: `paper/coverage_smoke_gpt54mini_v03.md`,
  `results/model_outputs/openai_gpt54mini_stress_v03_smoke6.jsonl`
- v0.3 coverage pilot: `paper/coverage_pilot_gpt54mini_v03.md`,
  `results/model_outputs/openai_gpt54mini_stress_v03_pilot24.jsonl`
- v0.3 GPT-5.5 smoke: `paper/coverage_smoke_gpt55_v03.md`,
  `results/model_outputs/openai_gpt55_stress_v03_smoke6.jsonl`
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
- current-model prompt mechanism: `paper/current_prompt_mechanism_gpt54mini_v02.md`,
  `paper/current_prompt_mechanism_gpt55_v02.md`
- current-model refresh: `paper/current_model_refresh_v02.md`
- current-model uncertainty:
  `paper/current_model_uncertainty_v02.md`
- current-model heterogeneity:
  `paper/current_model_heterogeneity_v02.md`
- current-model regression risk:
  `paper/current_model_regression_risk_v02.md`
- current-model residual-error analysis:
  `paper/current_model_error_analysis_v02.md`
- current-model qualitative case studies:
  `paper/current_model_case_studies_v02.md`
- current-model scorer sensitivity:
  `paper/current_model_scorer_sensitivity_v02.md`
- generation progress probe: `paper/generation_progress_probe_v02.md`
- efficiency tradeoff: `paper/efficiency_tradeoff_v02.md`
- follow-up readiness audit: `paper/followup_plan_readiness_v02.md`
- judge agreement analysis: `paper/judge_agreement_analysis_v02_full120.md`,
  `paper/judge_refresh_gpt55_v02_full120.md`
- discovery cue analysis: `paper/discovery_cue_analysis.md`
- human audit design audit: `paper/human_audit_design_audit_v02.md`
- human/native-review acceptance rules:
  `paper/human_audit_acceptance_rules_v02.md`
- human audit review sheets: `data/human_audit/review_sheets_v0.2/`
- current-model human audit launch packet:
  `data/current_model_human_audit/`,
  `paper/current_model_human_audit_design_v02.md`
- full-v0.2 judge audits:
  `results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl`,
  `results/scores/openai_three_model_stress_v02_full120_judge_gpt55_audit72.jsonl`

## Main Metrics

| Model | Condition | FTGA | Mean RTT | Token tax | Unresolved | Repair@1 | Repair@2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-4.1-nano | baseline | 67.5% | 0.47 | 1.69x | 5.8% | 74.4% | 82.1% |
| gpt-4.1-nano | contract | 76.7% | 0.33 | 1.34x | 4.2% | 78.6% | 82.1% |
| gpt-4.1-mini | baseline | 75.8% | 0.28 | 1.43x | 0.8% | 89.7% | 96.6% |
| gpt-4.1-mini | contract | 79.2% | 0.24 | 1.27x | 1.7% | 92.0% | 92.0% |
| gpt-4.1 | baseline | 76.7% | 0.28 | 1.43x | 2.5% | 89.3% | 89.3% |
| gpt-4.1 | contract | 93.3% | 0.15 | 1.13x | 4.2% | 37.5% | 37.5% |
| gpt-5.4-mini | baseline | 80.0% | 0.25 | 1.38x | 2.5% | 87.5% | 87.5% |
| gpt-5.4-mini | contract | 85.0% | 0.25 | 1.24x | 5.0% | 66.7% | 66.7% |
| gpt-5.5 | baseline | 81.7% | 0.23 | 1.28x | 1.7% | 86.4% | 90.9% |
| gpt-5.5 | contract | 98.3% | 0.02 | 1.02x | 0.0% | 100.0% | 100.0% |

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

## Current-Model Refresh

A bounded follow-up refresh adds current GPT-5.x-family evidence. On the full
120-item `gpt-5.4-mini` run, FTGA improves from 80.0% to 85.0% and mean token
tax falls by 0.138x, but the FTGA sign test is not decisive (p=0.2101) and
unresolved rate increases from 2.5% to 5.0%. The safe interpretation is lower
token burden plus a bounded FTGA gain, not universal repair improvement.

The full 120-item `gpt-5.5` run is now the clean current-model headline: FTGA
rises from 81.7% to 98.3% (+16.7 pp; exact sign-test p=0.0000019), mean RTT
falls from 0.225 to 0.017, token tax falls by 0.262x, and unresolved
trajectories fall from 1.7% to 0.0%. The contract still leaves two first-turn
failures, so the claim remains bounded: RePromptTax persists on the current
flagship, and the contract sharply reduces but does not eliminate first-turn
misalignment. See `paper/current_model_refresh_v02.md` and
`scripts/validate_current_model_refresh.py`.

The uncertainty supplement adds paired bootstrap intervals to that current-model
claim. `gpt-5.5` improves by +16.7 pp FTGA with a [10.0, 24.2] pp
item-bootstrap interval and 20 improved versus 0 worsened paired FTGA items.
`gpt-5.4-mini` improves by +5.0 pp FTGA, but its [-0.8, 11.7] pp interval
crosses zero; its token-tax interval remains positive at [0.010, 0.269]x.
This keeps the flagship result strong while bounding the lower-cost result to
token-burden reduction plus directional FTGA. See
`paper/current_model_uncertainty_v02.md`.

The heterogeneity supplement shows that the `gpt-5.5` effect is not a
single-language artifact: Arabic-English moves +25.0 pp, Spanish-English moves
+20.0 pp, Hindi-English moves +5.0 pp, and all leave-one-language checks remain
positive. It is still task-family concentrated: editing preservation moves
+60.0 pp, and removing editing leaves only +2.2 pp because other task families
are near ceiling. The lower-cost `gpt-5.4-mini` result is weaker: removing
Arabic-English leaves -1.3 pp and removing editing preservation leaves -4.5 pp.
See `paper/current_model_heterogeneity_v02.md`.

The contract-regression diagnostic makes the lower-cost boundary sharper.
`gpt-5.5` has 20 baseline-fail/contract-pass fixes, 0 first-turn regressions,
and 0 resolved-to-unresolved shifts. `gpt-5.4-mini` has 11 fixes but 5
first-turn regressions and 4 resolved-to-unresolved shifts; content-preservation
avoids first-turn failure on 3 of those 5 regression cases. See
`paper/current_model_regression_risk_v02.md`.

The residual-error analysis makes that boundary concrete. For `gpt-5.5`, the
contract fixes 20 baseline failures with zero first-turn regressions and leaves
only two Spanish-English editing-preservation first-turn failures, both repaired
in one turn. For `gpt-5.4-mini`, the contract fixes 11 baseline failures but
introduces five first-turn regressions and leaves six unresolved trajectories.
See `paper/current_model_error_analysis_v02.md` and
`scripts/validate_current_model_error_analysis.py`.

The current-model case-study supplement turns those aggregates into inspectable
examples: one `gpt-5.5` baseline wrapper-tax row fixed by the contract, one
`gpt-5.5` contract residual that repairs after a single prompt, and two
unresolved `gpt-5.4-mini` contract rows covering quote/output-language and
literal-data preservation boundaries. See
`paper/current_model_case_studies_v02.md`.

The current-model scorer-sensitivity supplement checks whether the refresh
headline depends on one fragile automatic component. It does not: relaxing
language moves `gpt-5.5` contract FTGA from 98.3% to 100.0%, while relaxing
preservation moves `gpt-5.4-mini` contract FTGA from 85.0% to 89.2%. This
separates the flagship wrapper-language residual from the lower-cost model's
literal-preservation boundary. See
`paper/current_model_scorer_sensitivity_v02.md`.

The generation-progress probe frames this as a benchmark progress signal rather
than only a per-model table. GPT-4.1-family baseline rows fail 96/360 model-item
pairs and 40/120 items fail for at least one model; GPT-5.x-family baseline
rows lower the normalized failure-pair rate to 46/240 and 26/120 any-fail
items. With the contract, GPT-5.x-family failure pairs fall to 20/240.
`gpt-5.5` with the contract passes 38 of the 40 items where at least one
GPT-4.1-family baseline failed, and the two items both current models still
fail are `es_en_SA_004` and `es_en_SA_009`. See
`paper/generation_progress_probe_v02.md`.

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

The all-five-model efficiency supplement extends this caveat to the
current-model rows: normalized token tax falls for every full-run model, but
absolute total tokens increase for every contract row. `gpt-5.5` contract has
the strongest alignment surface at 98.3% FTGA and 1.016x token tax, but it
still uses 114.5 more absolute tokens per item than baseline while saving 36.8
repair tokens after the first turn. Do not frame the contract as an API-cost
reduction. See `paper/efficiency_tradeoff_v02.md`.

The follow-up readiness audit maps the original experiment plan to the current
artifact set. It marks the current-model refresh, main metrics, family and
language caveats, token-burden caveat, prompt mechanism, related work, and
manifest/checklist surfaces as paper-facing complete; repair-realism and
judge-refresh diagnostics as supporting complete; and the original human audit,
current-model human audit, and v0.3 native review as launch-ready but still
missing qualified labels. See `paper/followup_plan_readiness_v02.md`.

## Repair Realism

A bounded 24-item diagnostic compares the saved standardized first repair
against three user-like repairs on baseline editing-preservation failures,
balanced across the three GPT-4.1-family models and Arabic-English /
Spanish-English failures. The saved standard repair and terse repair both
recover 24/24 sampled failures. The frustrated repair ("I meant don't translate
it.") recovers 17/24, while the explicit source-language contract repair
recovers 5/24 and often leaves Spanish or Arabic explanatory framing around the
English rewrite. This shows that repair burden is wording-sensitive; it is not
a replacement for a user study. See `paper/repair_realism_editing_baseline24.md`.

## Benchmark Quality Audit

The paper-facing stress set has a deterministic release-hygiene audit. It
reports 120 unique user prompts, zero normalized duplicate prompts, required
scoring markers and known-bad-output notes for all rows, preservation spans in
the two preservation-relevant families, and zero email/URL/phone-like/SSN-like
or placeholder privacy markers under the audit regexes. This supports release
hygiene, but it is not a substitute for native-speaker validation.

## Human Audit Launch Readiness

The human-audit packet remains launch-ready but not completed. In addition to
the blinded CSV slices, the repo now includes static per-language review sheets
under `data/human_audit/review_sheets_v0.2/`. The sheets are generated only from
the blinded launch packet, support local CSV export for annotators, and are
validated to cover all 72 audit IDs without answer-key fields. They do not
change the claim boundary: native/near-native labels and a completed roster are
still required before reporting human-validation results.

The current-model refresh has a separate launch-ready 48-row packet under
`data/current_model_human_audit/`, with one first-turn response for every
`gpt-5.4-mini` / `gpt-5.5` model-condition-language-family stratum. The design
audit reports 32 automatic passes and 16 automatic failures after
failure-enriched within-stratum sampling, plus blinded static review sheets for
the three language slices. This is not completed human validation; it prepares
the current-model rows for qualified native/near-native annotation.

The acceptance-rule supplement pre-specifies how completed labels can widen
claims. The original 72-row audit must reach at least 65 pass/fail agreements
and 306 component agreements with a qualified roster; the 48-row current-model
audit must reach at least 44 pass/fail agreements and 204 component agreements;
and the v0.3 native review must mark all 60 rows release usable before v0.3 can
be treated as paper-facing benchmark evidence. See
`paper/human_audit_acceptance_rules_v02.md`.

## Coverage Expansion Scaffold

The v0.3 scaffold adds 60 synthetic non-English target-content editing rows
across six coverage slices: English instructions with Spanish, Hindi, and
Arabic target content; Spanish instructions around Arabic content; Hindi-English
code-switched instructions around Hindi Devanagari content; and Arabic
instructions around Arabic content with English file names. This is not
paper-facing model result evidence. It requires native validation and a larger
pre-specified run before any benchmark performance statement; v0.2 remains the
original paper-facing stress pilot.

The repo now includes a launch-ready native-review packet for all 60 synthetic
v0.3 rows under `data/coverage_native_review_v03/`, plus a design audit in
`paper/coverage_native_review_design_v03.md`. The packet has six 10-row
coverage-slice CSVs, blank review fields, a roster template, and a launch
checklist. It is not completed native validation; completed reviewer labels and
a qualified roster must pass `scripts/validate_completed_coverage_native_review_v03.py`
and then be summarized with `scripts/summarize_coverage_native_review_v03.py`
before v0.3 can support paper-facing benchmark claims.

A six-item `gpt-5.4-mini` smoke, one row per coverage slice, verifies that the
v0.3 rows are runnable and scoreable. Baseline passes 5/6 first turns, while
the contract passes 6/6; the only baseline first-turn failure is the
Spanish-instruction/Arabic-content slice, where the answer wraps Arabic content
in Spanish framing and then repairs in one turn. This remains a smoke diagnostic
only, not paper-facing model result evidence.

A 24-item `gpt-5.4-mini` v0.3 pilot, four rows per coverage slice, reuses the
six smoke rows and adds an 18-item remaining shard. Baseline FTGA is 75.0%
with mean RTT 0.417; the contract reaches 95.8% FTGA with mean RTT 0.125.
The clearest movement is the Spanish-instruction/Arabic-content slice:
baseline fails all 4 first turns with Spanish framing around Arabic content,
while the contract passes all 4. A residual contract failure remains in the
English-instruction/Arabic-content slice due to exact-preservation scoring.
This pilot is synthetic v0.3 evidence only and still requires native validation
before claims.

A parallel six-item `gpt-5.5` smoke on the same v0.3 coverage slices saturates:
baseline and contract both pass 6/6 first turns, with no repair rows. This is a
small flagship contrast to the `gpt-5.4-mini` pilot; it should be framed as a
smoke diagnostic, not as evidence that v0.3 is solved.

## Experiment Ledger

The tracked saved artifacts contain 1,504 API response rows: 1,288
model-response rows for the main evaluation plus nano prompt-control,
prompt-ablation, v0.3 pilot, and GPT-5.5 smoke diagnostics, 72 repair-variant
rows, and 144 judge-audit rows across the original `gpt-4.1` judge audit and
paired `gpt-5.5` judge refresh. Provider-reported saved usage totals 229,646
input tokens and 56,284 output tokens. The ledger
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

A current-model mechanism diagnostic on full 120-item `gpt-5.4-mini` compares
baseline, the full contract, and the narrower content-preservation prompt.
Content preservation reaches 85.8% FTGA versus 85.0% for the full contract,
with 5 paired improvements and 4 paired regressions relative to the contract
(sign-test p=1.0). Token tax is slightly worse than the full contract
(1.252x vs 1.241x). The safe mechanism claim is therefore that preservation
scaffolding captures much of the benefit, not that it uniformly dominates the
full contract on current models. See
`paper/current_prompt_mechanism_gpt54mini_v02.md`.

The same full 120-item mechanism diagnostic on `gpt-5.5` strengthens the
preservation-mechanism interpretation while preserving the claim boundary.
Content preservation reaches 99.2% FTGA versus 98.3% for the full contract,
with 2 paired improvements, 1 paired regression, and an exact content-vs-contract
sign-test p=1.0. Token tax is marginally lower than the full contract
(1.012x vs 1.016x), and both prompts resolve all trajectories. The safe
interpretation is that literal content-preservation scaffolding accounts for
most of the current-model gain, but the content-vs-contract difference is one
net item rather than a dominance result. See
`paper/current_prompt_mechanism_gpt55_v02.md`.

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

A paired `gpt-5.5` judge refresh on the exact same 72 rows agrees with the
automatic scorer on 70/72 pass/fail labels (97.2%; Wilson 95% CI 90.4--99.2)
and has zero parse errors after one single-row rerun with a larger output cap.
The two LLM judges agree with each other on 69/72 pass/fail labels. The
`gpt-5.5` judge is stricter on three rows: it agrees with the automatic scorer
that Spanish framing around English rewrites should fail, and it newly rejects
one polite-request register case and one over-informative quote-summary case.
See `paper/judge_refresh_gpt55_v02_full120.md`.

## Claim Boundary

These are preliminary results with automatic scoring plus a 10% stratified
blinded LLM-judge audit and a paired `gpt-5.5` judge refresh. The objective
checks for exact-span preservation and script are reliable, and both judge
audits support most sampled language/task decisions. Human or native-speaker
audit is still needed before making strong final paper claims. Safe current
claim:

> On a 120-item synthetic stress pilot, GPT-4.1-family and GPT-5.x-family API
> model runs exhibit measurable re-prompt tax under baseline prompting,
> especially on implicit content-language preservation. A simple Global
> Interaction Contract improves first-turn alignment and reduces turn/token tax
> on this pilot, including a `gpt-5.5` refresh that moves from 81.7% to 98.3%
> first-turn alignment, but it does not remove all residual first-turn failures.
> Two stratified blinded LLM-judge audits support most sampled automatic
> pass/fail labels, while native-speaker validation remains necessary before
> stronger final claims.

## Validation

Run the full local gate:

```bash
conda run -n reprompt_tax python scripts/run_submission_checks.py
```

The current build produces `paper/main.pdf`, 10 pages, with no unresolved
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
