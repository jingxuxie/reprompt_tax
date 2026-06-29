# RePromptTax Result Card

## Main Stress Result

Source table:
`results/tables/openai_three_model_stress_v02_full120/metrics_summary.csv`

| Model | Condition | FTGA | Mean RTT | Token tax | Unresolved | Repair@1 | Repair@2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-4.1-nano | baseline | 67.5% | 0.47 | 1.69x | 5.8% | 74.4% | 82.1% |
| gpt-4.1-nano | contract | 76.7% | 0.33 | 1.34x | 4.2% | 78.6% | 82.1% |
| gpt-4.1-mini | baseline | 75.8% | 0.28 | 1.43x | 0.8% | 89.7% | 96.6% |
| gpt-4.1-mini | contract | 79.2% | 0.24 | 1.27x | 1.7% | 92.0% | 92.0% |
| gpt-4.1 | baseline | 76.7% | 0.28 | 1.43x | 2.5% | 89.3% | 89.3% |
| gpt-4.1 | contract | 93.3% | 0.15 | 1.13x | 4.2% | 37.5% | 37.5% |

## Current-Model Refresh

Source artifacts:
`paper/current_model_refresh_v02.md`,
`results/tables/current_model_refresh_v02/`,
`results/tables/openai_gpt54mini_stress_v02_full120/`, and
`results/tables/openai_gpt55_stress_v02_full120/`.

| Model | Condition | FTGA | Mean RTT | Token tax | Unresolved | Repair@1 | Repair@2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-5.4-mini | baseline | 80.0% | 0.25 | 1.38x | 2.5% | 87.5% | 87.5% |
| gpt-5.4-mini | contract | 85.0% | 0.25 | 1.24x | 5.0% | 66.7% | 66.7% |
| gpt-5.5 | baseline | 81.7% | 0.23 | 1.28x | 1.7% | 86.4% | 90.9% |
| gpt-5.5 | contract | 98.3% | 0.02 | 1.02x | 0.0% | 100.0% | 100.0% |

The `gpt-5.5` full120 run is the clean current-model headline: FTGA rises from
81.7% to 98.3%, mean RTT falls from 0.225 to 0.017, and unresolved
trajectories fall to 0.0%. The `gpt-5.4-mini` result is more bounded: FTGA
moves from 80.0% to 85.0%, but the FTGA sign test is not decisive and
unresolved rate increases from 2.5% to 5.0%.

Current-model uncertainty:
`paper/current_model_uncertainty_v02.md`

Bootstrap and exact paired sign-test checks sharpen that boundary. `gpt-5.5`
FTGA improves by +16.7 pp with a [10.0, 24.2] pp item-bootstrap interval and
20 improved versus 0 worsened paired items. `gpt-5.4-mini` FTGA improves by
+5.0 pp, but its [-0.8, 11.7] pp interval crosses zero; its token-tax interval
stays positive at [0.010, 0.269]x.

Current-model heterogeneity:
`paper/current_model_heterogeneity_v02.md`

The `gpt-5.5` effect is positive for all three language pairs: +25.0 pp on
Arabic-English, +20.0 pp on Spanish-English, and +5.0 pp on Hindi-English.
Leave-one-language checks remain positive, but task-family effects are
editing-preservation concentrated: editing moves +60.0 pp and removing editing
leaves only +2.2 pp. `gpt-5.4-mini` is not robust across strata: removing
Arabic-English leaves -1.3 pp and removing editing leaves -4.5 pp.

Residual-error analysis:
`paper/current_model_error_analysis_v02.md`

For `gpt-5.5`, the contract fixes 20 baseline first-turn failures, introduces
zero first-turn regressions, and leaves two Spanish-English editing-preservation
first-turn failures that both repair in one turn. For `gpt-5.4-mini`, the
contract fixes 11 baseline failures but introduces five first-turn regressions
and leaves six unresolved trajectories.

Current-model case studies:
`paper/current_model_case_studies_v02.md`

Four saved-output case studies make the current-model boundary inspectable:
`gpt-5.5` baseline wrapper tax fixed by the contract, a `gpt-5.5` contract
residual that repairs in one turn, and two unresolved `gpt-5.4-mini` contract
cases covering Hindi/Hinglish quote preservation and Arabic literal-data
preservation.

Current-model scorer sensitivity:
`paper/current_model_scorer_sensitivity_v02.md`

Component relaxation shows the current-model headline is not driven by a single
fragile scorer rule. `gpt-5.5` contract moves from 98.3% to 100.0% FTGA only
when language is relaxed; `gpt-5.4-mini` contract moves from 85.0% to 89.2%
when preservation is relaxed, isolating the lower-cost model's literal-data
boundary.

Scorer challenge audit:
`paper/scorer_challenge_v02.md`

A synthetic challenge audit generates 390 known-bad probes from the v0.2
benchmark and feeds them through `scripts/score_auto.py`: forbidden-marker,
required-marker omission, wrong-script, preservation-drop, and
over-formal-register probes. The scorer fails 390/390 probes and detects
390/390 expected deterministic failure signals. This strengthens scorer
plumbing evidence while preserving the native/human validation boundary.

Scorer positive-control audit:
`paper/scorer_positive_control_v02.md`

A complementary positive-control audit generates 120 constrained pass templates,
one for each v0.2 item, and feeds them through `scripts/score_auto.py`. The scorer
accepts 120/120 templates and passes 120/120 component checks. This tests
over-rejection by deterministic rules while preserving the native/human
validation boundary.

Current-model regression risk:
`paper/current_model_regression_risk_v02.md`

The contract-regression diagnostic separates the flagship and lower-cost
current-model claims. `gpt-5.5` has 20 fixes and 0 first-turn regressions.
`gpt-5.4-mini` has 11 fixes, 5 first-turn regressions, and 4
resolved-to-unresolved shifts; content-preservation avoids 3 of the 5
`gpt-5.4-mini` regression cases.

Generation-progress probe:
`paper/generation_progress_probe_v02.md`

GPT-5.x-family baseline rows lower the normalized failure-pair rate from
96/360 GPT-4.1-family baseline model-item failures to 46/240 current-family
baseline failures. With the contract, GPT-5.x-family failures fall to 20/240,
and `gpt-5.5` passes 38 of the 40 items where at least one GPT-4.1-family
baseline failed.

All-model robustness and balanced pilot design:
`paper/all_model_paired_significance_v02.md`,
`paper/all_model_uncertainty_v02.md`,
`paper/balanced_subsample_robustness_v02.md`,
`paper/sentinel_suite_v02.md`

Across the five full 120-item runs, the contract has a +10.2 pp aggregate FTGA
effect over 600 paired model-item rows, with 67 fixes and 6 regressions. The
prompt-cluster bootstrap interval is +5.8 to +15.0 pp. Balanced 48-item
stratified pilots recover the all-model and `gpt-5.5` positive directions in
100.0% of saved-trajectory simulations and land within 5 pp of both full-run
effects in 100.0% of simulations. Smaller-effect models stay bounded:
`gpt-5.4-mini` recovers the positive direction in 92.2% of 48-item simulations
and `gpt-4.1-mini` in 93.5%.

For future smoke runs, `data/stress_v02_sentinel24_ids.txt` provides a compact
24-item subset selected from saved full-run diagnostics. It covers all 12
language-family cells, captures 19/20 GPT-5.x contract failure pairs, captures
both GPT-5.5 contract residual items, and remains explicitly non-headline until
confirmed on the full 120-item benchmark.

Efficiency tradeoff:
`paper/efficiency_tradeoff_v02.md`

Across all five full-run models, the contract lowers normalized token tax but
increases absolute total tokens. For `gpt-5.5`, that is +114.5 absolute tokens
per item versus -36.8 repair tokens after first turn. Token tax is not dollar
cost.

Follow-up readiness audit:
`paper/followup_plan_readiness_v02.md`

The follow-up plan now maps to eight paper-facing complete items, two completed
supporting diagnostics, three launch-ready annotation surfaces that still need
qualified labels, one bounded v0.3 diagnostic surface, and one not-started
collaborator-language-pair item. The remaining blockers are the original
72-row human audit, the 48-row current-model human audit, and the 60-row v0.3
native-review packet.

## Key Findings

1. Baseline re-prompt tax appears across the GPT-4.1-family and current-model
   refresh runs.
2. The Global Interaction Contract improves FTGA for every model and reduces
   mean RTT and token tax.
3. Implicit editing preservation is the dominant baseline failure mode.
4. `gpt-4.1-nano` uniquely struggles with some quote-preservation stress items.
5. The initial 120-item standard pilot was too easy for paper-facing claims; the
   stress set is the main result.
6. Component analysis shows the mitigation mainly moves language/script/task
   checks; preservation barely moves, and register/locale checks are saturated
   under the current rules.
7. Language-slice analysis shows the clearest average FTGA gain on Arabic-English
   and near-saturated Hindi-English baseline performance.
8. Repair-dynamics analysis shows first-turn successes rise under the contract,
   while residual unresolved cases remain in quote-preservation and
   script/register/locale families.
9. The current flagship `gpt-5.5` still has measurable first-turn burden under
   baseline prompting, but the contract reduces it sharply.

Family-level analysis:
`paper/failure_mode_analysis_v02_full120.md`

Scorer-component breakdown:
`paper/component_breakdown_v02_full120.md`

Scorer-ablation sensitivity:
`paper/scorer_ablation_sensitivity_v02_full120.md`

First-turn error atlas:
`paper/error_atlas_v02_full120.md`

Item-consistency supplement:
`paper/item_consistency_analysis_v02_full120.md`

## Paired Mitigation Effects

Source table:
`results/tables/openai_three_model_stress_v02_full120/paired_contract_effects_by_model.csv`

Effects compare contract minus baseline on the same 120 items per model.
Positive FTGA means improvement; positive RTT/token-tax reductions mean lower
burden.

| Model | FTGA delta | 95% CI | RTT reduction | 95% CI | Token-tax reduction | 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| gpt-4.1-nano | +9.2 pp | [+4.2, +15.0] | 0.14 | [0.07, 0.23] | 0.35x | [0.23, 0.48] |
| gpt-4.1-mini | +3.3 pp | [+0.8, +6.7] | 0.03 | [0.00, 0.07] | 0.16x | [0.10, 0.23] |
| gpt-4.1 | +16.7 pp | [+10.0, +23.3] | 0.13 | [0.05, 0.22] | 0.30x | [0.19, 0.43] |

Paired sign-test sensitivity:
`paper/paired_significance_v02_full120.md`

Language-slice analysis:
`paper/language_slice_analysis_v02_full120.md`

Repair-dynamics analysis:
`paper/repair_dynamics_v02_full120.md`

Absolute token-burden supplement:
`paper/token_burden_analysis_v02_full120.md`

Token tax is a repair-burden ratio, not an absolute API-cost claim. The longer
contract prompt lowers token-tax ratios but increases absolute total tokens in
this pilot.

Benchmark-quality audit:
`paper/benchmark_quality_audit_v02.md`

The audit reports 120 unique stress prompts, zero normalized duplicate prompts,
complete required-marker and known-bad-output coverage, and zero privacy-like
marker hits under the release-hygiene regexes.

Experiment ledger:
`paper/experiment_ledger_v02.md`

The tracked saved artifacts contain 1,504 API response rows: 1,288
model-response rows, 72 repair-variant rows, and 144 judge-audit rows, totaling
285,930 saved provider-reported tokens. The ledger reports token usage only,
not dollar cost.

## Prompt Diagnostics

A bounded `gpt-4.1-nano` diagnostic compares the baseline, the Global
Interaction Contract, a longer generic helpfulness prompt, and a narrower
content-preservation prompt.

Source artifacts:
`paper/prompt_control_analysis.md`, `paper/prompt_ablation_analysis.md`,
`results/tables/openai_nano_stress_v02_full120_prompt_control/`, and
`results/tables/openai_nano_stress_v02_full120_prompt_ablation/`

| Condition | FTGA | Mean RTT | Token tax | Unresolved |
|---|---:|---:|---:|---:|
| baseline | 67.5% | 0.47 | 1.69x | 5.8% |
| generic_helpfulness | 75.0% | 0.33 | 1.37x | 3.3% |
| content_preservation | 80.0% | 0.27 | 1.28x | 3.3% |
| contract | 76.7% | 0.33 | 1.34x | 4.2% |

The generic prompt partially improves nano, so the control is not a clean
specificity win. The narrower content-preservation prompt is strongest in this
single-model diagnostic, so the safe claim is that content-language and
literal-preservation rules appear to drive much of the mitigation, not that the
full Global Interaction Contract is the best possible prompt.

Current-model mechanism diagnostics run the content-preservation prompt on full
120-item `gpt-5.4-mini` and `gpt-5.5` runs. They show near ties against the full
contract, not prompt dominance: 85.8% vs 85.0% FTGA on `gpt-5.4-mini`, and
99.2% vs 98.3% on `gpt-5.5`.

## Validation

The paper-facing validation command passes:

```bash
conda run -n reprompt_tax python scripts/run_submission_checks.py
```

For targeted debugging, the underlying local checks are:

```bash
conda run -n reprompt_tax python scripts/analyze_failure_modes.py \
  --tables-dir results/tables/openai_three_model_stress_v02_full120 \
  --paper-out paper/failure_mode_analysis_v02_full120.md
conda run -n reprompt_tax python scripts/analyze_component_breakdown.py \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --out-dir results/tables/openai_three_model_stress_v02_full120 \
  --out-md paper/component_breakdown_v02_full120.md
conda run -n reprompt_tax python scripts/build_error_atlas.py \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --trajectories results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv \
  --out-csv results/tables/openai_three_model_stress_v02_full120/first_turn_error_atlas.csv \
  --out-md paper/error_atlas_v02_full120.md
conda run -n reprompt_tax python scripts/paired_significance.py \
  --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv \
  --out-csv results/tables/openai_three_model_stress_v02_full120/paired_significance_by_model.csv \
  --out-md paper/paired_significance_v02_full120.md
conda run -n reprompt_tax python scripts/analyze_language_slices.py \
  --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv \
  --out-dir results/tables/openai_three_model_stress_v02_full120 \
  --out-md paper/language_slice_analysis_v02_full120.md
conda run -n reprompt_tax python scripts/analyze_repair_dynamics.py \
  --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv \
  --out-dir results/tables/openai_three_model_stress_v02_full120 \
  --out-md paper/repair_dynamics_v02_full120.md
conda run -n reprompt_tax python scripts/analyze_benchmark_quality.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --out-dir results/tables/benchmark_quality_v02 \
  --out-md paper/benchmark_quality_audit_v02.md
conda run -n reprompt_tax python scripts/summarize_experiment_ledger.py \
  --out-dir results/tables/experiment_ledger_v02 \
  --out-md paper/experiment_ledger_v02.md
conda run -n reprompt_tax python scripts/test_score_auto.py
conda run -n reprompt_tax python scripts/lint_claim_boundaries.py
conda run -n reprompt_tax python scripts/validate_paper_claims.py
conda run -n reprompt_tax python scripts/make_artifact_manifest.py --check
```

The qualitative examples are validated against saved score rows and trajectory
metrics:

```bash
conda run -n reprompt_tax python scripts/validate_qualitative_examples.py
```

The 72-response blinded judge audit reports:

- pass/fail agreement: 71/72 (98.6%),
- Wilson 95% CI for pass/fail agreement: [92.5%, 99.8%],
- component agreement: language 71/72, script 71/72, preservation 69/72,
  task 71/72, register/locale 68/72,
- parse errors: 0.

Judge agreement supplement:
`paper/judge_agreement_analysis_v02_full120.md`

A paired `gpt-5.5` judge refresh on the same 72 rows agrees with the automatic
scorer on 70/72 pass/fail labels and with the original `gpt-4.1` judge on
69/72 labels. It is a scorer sanity check, not native-speaker validation.

Judge-refresh supplement:
`paper/judge_refresh_gpt55_v02_full120.md`

## Human Audit Readiness

The blinded 72-row launch packet covers one first-turn response for every
model/condition/language-pair/task-family stratum. The design audit reports 57
automatic passes and 15 automatic failures in the sampled rows, confirms the
annotator packet contains no private model/condition/item/auto-label fields,
includes a blank annotator-ID field plus roster template for qualified
annotator metadata, and keeps completed native/near-native annotation as a
required next step.

Design audit:
`paper/human_audit_design_audit_v02.md`

The current-model refresh now has a separate 48-row launch packet under
`data/current_model_human_audit/`. It covers one first-turn response for every
`gpt-5.4-mini` / `gpt-5.5` model-condition-language-family stratum and is
failure-enriched inside strata: 32 automatic passes and 16 automatic failures.
The packet and static review sheets are blinded; completed native/near-native
labels are still required before claiming human validation for current-model
rows.

Current-model audit design:
`paper/current_model_human_audit_design_v02.md`

The v0.3 coverage expansion also has a separate launch-ready native-review
packet under `data/coverage_native_review_v03/`. It covers all 60 synthetic
v0.3 rows across six 10-row slices and keeps review fields blank. The preferred
completion path uses two independent reviewer rows per item, an
inter-reviewer/adjudication analysis, and a finalized one-row-per-item label
file. Static per-slice browser sheets are available under
`data/coverage_native_review_v03/review_sheets_v03/` to reduce label-collection
friction while preserving the same CSV schema. Completed reviewer labels and a
qualified roster must pass
`scripts/validate_completed_coverage_native_review_v03.py` before v0.3 can be
treated as paper-facing benchmark evidence.

v0.3 review design audit:
`paper/coverage_native_review_design_v03.md`

Human/native-review acceptance rules:
`paper/human_audit_acceptance_rules_v02.md`

Future completed labels must pass the completed-label validators and the
pre-specified quantitative gates before claims widen. The two human-audit
surfaces require at least 90% pass/fail agreement and 85% component agreement
with qualified rosters; the v0.3 native-review surface requires all 60 rows to
be release usable before v0.3 can become paper-facing benchmark evidence.
The consolidated launch pack in `paper/label_collection_launch_pack_v02.md`
tracks all three surfaces together: 180 reviewer-facing packet rows, roster
templates, review-sheet indexes, finalization commands, and claim gates.

## Real-World Motivation Check

An aggregate-only scan of the first 20,000 streamed WildChat conversations found:

- 10,681 multi-turn conversations,
- 172 conversations with at least one repair cue,
- 219 total cue hits,
- no raw text written.

The scan supports taxonomy motivation but is not a representative prevalence
estimate.

Discovery cue analysis:
`paper/discovery_cue_analysis.md`

The hashed metadata analysis reports 172 unique hit conversations, 219 cue
hits, 31 conversations with repeated cue hits, and no raw text written. The
largest unique-conversation categories are generic repair (81 conversations)
and wrong output language (48 conversations).

## Claim Boundary

Detailed claim-to-artifact mapping:
`paper/claim_evidence_checklist.md`

Safe claim:

> On a 120-item synthetic stress pilot, GPT-4.1-family and GPT-5.x-family API
> models exhibit measurable re-prompt tax under baseline prompting, especially
> on implicit content-language preservation. A simple Global Interaction
> Contract reduces first-turn and repair burden, with the cleanest current-model
> result on `gpt-5.5`, while native-speaker validation remains required for
> stronger cultural or register claims.

Do not claim:

- that this benchmark is representative of all multilingual users,
- that the result generalizes across providers,
- that LLM-judge audit replaces native-speaker validation,
- that the full Global Interaction Contract is the best prompt tested,
- that the v0.3 coverage pilot is paper-facing benchmark evidence before
  native review is completed,
- that prompt mitigation fully solves the problem.

## Current Paper Artifact

- TeX source: `paper/main.tex`
- PDF: `paper/main.pdf`
- Build command: `cd paper && latexmk -pdf -interaction=nonstopmode main.tex`
