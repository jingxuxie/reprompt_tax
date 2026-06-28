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

## Key Findings

1. Baseline re-prompt tax appears across all three models.
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

The paper-facing artifacts contain 1,290 saved API response rows: 1,218
model-response rows and 72 judge-audit rows, totaling 228,831 saved
provider-reported tokens. The ledger reports token usage only, not dollar cost.

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

> On a 120-item stress pilot, three GPT-4.1-family API models exhibit measurable
> re-prompt tax under baseline prompting, especially on implicit content-language
> preservation. A simple Global Interaction Contract reduces but does not
> uniformly eliminate the tax for cheaper models, with gains largest for the
> strongest model.

Do not claim:

- that this benchmark is representative of all multilingual users,
- that the result generalizes across providers,
- that LLM-judge audit replaces native-speaker validation,
- that the full Global Interaction Contract is the best prompt tested,
- that prompt mitigation fully solves the problem.

## Current Paper Artifact

- TeX source: `paper/main.tex`
- PDF: `paper/main.pdf`
- Build command: `cd paper && latexmk -pdf -interaction=nonstopmode main.tex`
