# RePromptTax Claim-Evidence Checklist

This checklist maps paper-facing claims to the artifacts that support them. It
is intended to keep the draft conservative and easy to audit.

## Paper-Facing Claims

| Claim | Evidence | Validation |
|---|---|---|
| The benchmark is a 120-item stress pilot over 3 language pairs, 4 task families, and 10 items per cell. | `data/benchmark_stress_v0.2.jsonl` | `scripts/validate_paper_claims.py` checks 120 rows, unique IDs, and exact cell counts. |
| The paper-facing stress benchmark has release-hygiene checks for duplicate prompts, scoring-marker coverage, preservation-span coverage, prompt lengths, and privacy-like markers. | `paper/benchmark_quality_audit_v02.md`, `results/tables/benchmark_quality_v02/` | `scripts/analyze_benchmark_quality.py` generates the audit; `scripts/validate_paper_claims.py` checks 120 unique prompts, zero normalized duplicates, zero privacy-marker hits, and expected family coverage. |
| Paper-facing API usage and provenance are summarized without double-counting historical shards. | `paper/experiment_ledger_v02.md`, `results/tables/experiment_ledger_v02/` | `scripts/summarize_experiment_ledger.py` reports 1,290 saved API response rows and 228,831 saved provider-reported tokens across the main evaluation, prompt-control diagnostic, prompt-ablation diagnostic, and judge audit. `scripts/validate_paper_claims.py` checks the totals and that no dollar-cost estimate is claimed. |
| Baseline GPT-4.1-family models exhibit measurable re-prompt tax on the stress pilot. | `results/tables/openai_three_model_stress_v02_full120/metrics_summary.csv` | `scripts/validate_paper_claims.py` checks all main metric values against `paper/main.tex`. |
| The Global Interaction Contract improves FTGA, mean RTT, and mean token tax for every model on the paper-facing stress pilot. | `results/tables/openai_three_model_stress_v02_full120/metrics_summary.csv`, `paper/main.tex` | `scripts/validate_paper_claims.py` checks FTGA, mean RTT, mean token tax, unresolved rate, Repair@1, and Repair@2. |
| The paired mitigation effect is positive for FTGA and reduces RTT/token tax on the paper-facing stress pilot. | `results/tables/openai_three_model_stress_v02_full120/paired_contract_effects_by_model.csv` | `scripts/validate_paper_claims.py` checks paired effect values and the paper text. |
| Language-slice effects show the aggregate gain is strongest on Arabic-English, weaker on Spanish-English, and saturated on Hindi-English in this stress pilot. | `paper/language_slice_analysis_v02_full120.md`, `results/tables/openai_three_model_stress_v02_full120/language_slice_*.csv` | `scripts/analyze_language_slices.py` generates paired language-slice effects. `scripts/validate_paper_claims.py` checks headline slice values and the caveat that this is not a population-level claim. |
| Repair-dynamics analysis shows how trajectories move among first-turn success, one-repair success, two-repair success, and unresolved outcomes. | `paper/repair_dynamics_v02_full120.md`, `results/tables/openai_three_model_stress_v02_full120/repair_*.csv` | `scripts/analyze_repair_dynamics.py` generates RTT distributions and paired transition matrices. `scripts/validate_paper_claims.py` checks headline RTT distributions, paired movement, and residual unresolved caveats. |
| Token tax is a repair-burden ratio, not an absolute API-cost claim; the longer contract prompt increases absolute total tokens. | `paper/token_burden_analysis_v02_full120.md`, `results/tables/openai_three_model_stress_v02_full120/token_burden_by_model.csv`, `results/tables/openai_three_model_stress_v02_full120/token_burden_paired_effects_by_model.csv` | `scripts/analyze_token_burden.py` generates absolute token-burden tables. `scripts/validate_paper_claims.py` checks headline token values and the caveat. |
| Paired sign-test sensitivity supports the strongest FTGA effects while showing mini's FTGA change is weaker. | `paper/paired_significance_v02_full120.md`, `results/tables/openai_three_model_stress_v02_full120/paired_significance_by_model.csv` | `scripts/paired_significance.py` computes exact two-sided sign tests over paired items. `scripts/validate_paper_claims.py` checks the key counts and supplemental artifact. |
| A single-model generic-helpfulness prompt control partially improves nano but does not match the contract's FTGA or token tax. | `paper/prompt_control_analysis.md`, `results/tables/openai_nano_stress_v02_full120_prompt_control/` | `scripts/analyze_prompt_control.py` generates the diagnostic over all 120 v0.2 stress items. `scripts/validate_paper_claims.py` checks the key values and that the control remains labeled as a single-model diagnostic, not a paper-facing three-model claim. |
| A single-model content-preservation prompt ablation outperforms the full contract on nano, sharpening the mechanism claim and bounding the mitigation claim. | `paper/prompt_ablation_analysis.md`, `results/tables/openai_nano_stress_v02_full120_prompt_ablation/`, `prompts/content_preservation_system.txt` | `scripts/analyze_prompt_ablation.py` reports 80.0% FTGA for content preservation vs 76.7% for the full contract on nano, and `scripts/validate_paper_claims.py` checks the paired effects, transition slices, and caveats. |
| Editing preservation is the dominant baseline failure family, while output-language inference is saturated in this stress pilot. | `paper/failure_mode_analysis_v02_full120.md`, `results/tables/openai_three_model_stress_v02_full120/family_effect_summary.csv`, `results/tables/openai_three_model_stress_v02_full120/failure_type_summary.csv` | `scripts/analyze_failure_modes.py` generates the family/failure summaries. `scripts/validate_paper_claims.py` checks the headline family and failure-mode values against `paper/main.tex`. |
| Item-consistency analysis separates systematic hard items from one-off model failures. | `paper/item_consistency_analysis_v02_full120.md`, `results/tables/openai_three_model_stress_v02_full120/item_consistency_*.csv` | `scripts/analyze_item_consistency.py` reports that baseline all-model failures drop from 27/120 items to 8/120 under the contract, while 35/120 items still fail for at least one model. `scripts/validate_paper_claims.py` checks the headline counts and hardest residual rows. |
| Component-level scorer analysis shows the mitigation mostly moves language/script/task checks, while preservation and register/locale boundaries remain. | `paper/component_breakdown_v02_full120.md`, `results/tables/openai_three_model_stress_v02_full120/component_*.csv` | `scripts/analyze_component_breakdown.py` generates first-turn component pass rates and paired component effects. `scripts/validate_paper_claims.py` checks headline component rows and conservative caveats. |
| Scorer-ablation sensitivity checks whether headline FTGA depends on one fragile automatic component. | `paper/scorer_ablation_sensitivity_v02_full120.md`, `results/tables/openai_three_model_stress_v02_full120/scorer_ablation_*.csv` | `scripts/analyze_scorer_ablation.py` relaxes one automatic component at a time and shows bounded single-component effects plus multi-component editing failure signatures. `scripts/validate_paper_claims.py` checks the headline counterfactuals and caveat. |
| Task-useful first-turn failures show a hidden repair-burden slice that is not simple task noncompletion. | `paper/task_useful_failure_analysis_v02_full120.md`, `results/tables/openai_three_model_stress_v02_full120/task_useful_failure_*.csv` | `scripts/analyze_task_useful_failures.py` reports that 31/96 baseline first-turn failures pass the task component, while the task+preservation useful subset falls from 11 to 1 under the contract. `scripts/validate_paper_claims.py` checks the diagnostic counts and paper wording. |
| First-turn failure cases are inspectable in a generated atlas rather than only aggregate tables. | `paper/error_atlas_v02_full120.md`, `results/tables/openai_three_model_stress_v02_full120/first_turn_error_atlas.csv` | `scripts/build_error_atlas.py` generates the atlas. `scripts/validate_paper_claims.py` checks the row count, family/model counts, unresolved cases, and key markdown anchors. |
| The strongest model reaches 93.3% FTGA under the contract on this stress pilot. | `results/tables/openai_three_model_stress_v02_full120/metrics_summary.csv` | `scripts/validate_paper_claims.py` checks the `gpt-4.1` contract row and rendered table value. |
| Qualitative examples are backed by saved full-v0.2 score rows and trajectory metrics, not manual paraphrase alone. | `paper/qualitative_examples.md`, `results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl`, `results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv` | `scripts/validate_qualitative_examples.py` checks cited items, model/condition rows, RTT values, pass/fail labels, failure types, and response snippets. `scripts/validate_paper_claims.py` invokes it. |
| A blinded GPT-4.1 judge audit agrees with the corrected automatic scorer on 71/72 sampled first-turn pass/fail labels. | `results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl`, `results/tables/openai_three_model_stress_v02_full120_judge_audit72/` | `scripts/validate_paper_claims.py` checks 72 rows, 71/72 pass/fail agreement, zero parse errors, and 3 examples per model/condition/task-family stratum. |
| Judge-audit uncertainty and component agreement are reported conservatively. | `paper/judge_agreement_analysis_v02_full120.md`, `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_*agreement*.csv` | `scripts/analyze_judge_agreement.py` computes Wilson intervals, pass/fail agreement by family, and component agreement. `scripts/validate_paper_claims.py` checks the 92.5--99.8 Wilson interval and lower preservation/register-locale component agreement. |
| Related-work positioning distinguishes RePromptTax from broad multilingual benchmarks, output-language alignment, and multi-turn dialogue preference evaluation. | `paper/main.tex`, `paper/related_work_positioning_v02.md`, `paper/refs.bib` | `scripts/validate_paper_claims.py` checks the related-work citations and the positioning note, including the MT-Bench/Chatbot Arena distinction. |
| Automatic scorer rule behavior is covered by deterministic regression tests for language, script, preservation, task, and register/locale failures. | `scripts/score_auto.py`, `scripts/test_score_auto.py` | `scripts/test_score_auto.py` checks 11 controlled cases. `scripts/validate_paper_claims.py` invokes it. |
| The WildChat scan is only a bounded aggregate motivation check, not a prevalence estimate. | `results/discovery/wildchat_20k_repair_cues/summary.json`, `paper/discovery_snapshot.md` | `scripts/validate_paper_claims.py` checks scan counts, category counts, and that no raw text was written. |
| Hashed WildChat cue metadata supports the taxonomy without exposing raw text. | `paper/discovery_cue_analysis.md`, `results/discovery/wildchat_20k_repair_cues/cue_*.csv`, `results/discovery/wildchat_20k_repair_cues/repeated_cue_conversations_hashed.csv` | `scripts/analyze_discovery_cues.py` reports unique conversations by category, repeated cue conversations, top cue patterns, and language metadata. `scripts/validate_paper_claims.py` checks the counts and no-raw-text caveat. |
| The human audit packet is launch-ready but not completed human validation. | `data/human_audit/`, `data/human_audit/audit_manifest_v0.2.md`, `data/human_audit/human_audit_launch_checklist_v0.2.md`, `docs/human_audit_guide.md` | `scripts/validate_human_audit_packet.py` checks blinding, blank annotation fields, balanced strata, language slices, launch checklist, and smoke-only marking. `scripts/validate_paper_claims.py` also checks packet readiness. |
| The human audit design covers all 72 model/condition/language/family strata and includes both automatic passes and failures. | `paper/human_audit_design_audit_v02.md`, `results/tables/human_audit_v0.2_design/` | `scripts/analyze_human_audit_design.py` reports 57 auto-pass and 15 auto-fail sampled rows, confirms no private fields in the blinded packet, and checks that completed annotation is still required before widening claims. |
| Completed human validation has a strict future gate and must not be confused with the smoke file. | `paper/human_audit_completion_plan.md`, `scripts/validate_completed_human_audit.py` | `scripts/validate_completed_human_audit.py` validates a completed 72-row annotation file, requires a qualified annotator roster, and rejects smoke-only files unless `--allow-smoke` is explicitly used for plumbing tests. |
| The earlier 24-item v0.2 probe remains reproducible as historical diagnostic evidence. | `data/stress_v02_new_balanced_24_ids.txt`, `results/tables/openai_three_model_stress_v02_new24/` | `scripts/validate_followup_probe.py` checks that v0.2 extends v0.1 exactly for the first five items per cell, the 24-item probe is balanced, and follow-up metrics match the documented diagnostic. |
| The paper-facing release package is reproducible from a deterministic artifact manifest. | `paper/artifact_manifest.json`, `paper/artifact_manifest.md` | `scripts/make_artifact_manifest.py --check` validates hashes, sizes, and expected artifact membership. `scripts/validate_paper_claims.py` invokes it. |
| Unsupported claim widening is linted before submission. | `scripts/lint_claim_boundaries.py`, `paper/main.tex`, `paper/extended_abstract_draft.md`, `paper/results_snapshot.md` | `scripts/lint_claim_boundaries.py` rejects representative/prevalence/generalization/human-validation overclaims on claim surfaces and checks required caveats. `scripts/validate_paper_claims.py` invokes it. |

## Safe Main Claim

On a 120-item synthetic stress pilot, three GPT-4.1-family API models exhibit
measurable re-prompt tax under baseline prompting, especially on implicit
content-language preservation. A simple Global Interaction Contract improves
first-turn alignment and reduces turn/token tax on this pilot, but it does not
remove residual exact-preservation failures. A stratified blinded LLM-judge
audit supports 71/72 sampled automatic pass/fail labels, while native-speaker
validation remains necessary before stronger final claims.

## Claims Not Supported Yet

- Do not claim the benchmark is representative of all multilingual or
  code-switched users.
- Do not claim prevalence of re-prompt tax in WildChat or any real-user
  dataset.
- Do not claim the mitigation fully solves multilingual interaction failures.
- Do not claim cross-provider generality.
- Do not claim native-speaker validation has been completed.
- Do not describe the 24-item v0.2 probe as the current paper-facing result;
  the paper-facing result is the completed 120-item v0.2 evaluation.
- Do not treat the generic-helpfulness control as proof that every mitigation
  gain is specific to multilingual-contract wording.
- Do not claim the full Global Interaction Contract is the best prompt tested;
  the nano content-preservation ablation performs better in this diagnostic.
- Do not describe token-tax reductions as absolute API-cost reductions; the
  contract prompt is longer and increases absolute total tokens in this pilot.

## Required Gates Before Submission

Run:

```bash
conda run -n reprompt_tax python scripts/run_submission_checks.py
```

The one-command gate regenerates paper-facing tables and figures, rebuilds the
PDF, refreshes the artifact manifest, and runs the validators below without API
calls. For targeted debugging, run the underlying checks directly:

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
conda run -n reprompt_tax python scripts/analyze_judge_agreement.py \
  --audit results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --out-dir results/tables/openai_three_model_stress_v02_full120_judge_audit72 \
  --out-md paper/judge_agreement_analysis_v02_full120.md
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
conda run -n reprompt_tax python scripts/analyze_token_burden.py \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --out-dir results/tables/openai_three_model_stress_v02_full120 \
  --out-md paper/token_burden_analysis_v02_full120.md
conda run -n reprompt_tax python scripts/score_auto.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --outputs results/model_outputs/openai_nano_stress_v02_full120_content_preservation.jsonl \
  --out results/scores/openai_nano_stress_v02_full120_content_preservation_auto_scores.jsonl
conda run -n reprompt_tax python scripts/compute_metrics.py \
  --scores results/scores/openai_nano_stress_v02_full120_content_preservation_auto_scores.jsonl \
  --out-dir results/tables/openai_nano_stress_v02_full120_content_preservation
conda run -n reprompt_tax python scripts/analyze_prompt_ablation.py
conda run -n reprompt_tax python scripts/summarize_experiment_ledger.py \
  --out-dir results/tables/experiment_ledger_v02 \
  --out-md paper/experiment_ledger_v02.md
conda run -n reprompt_tax python scripts/analyze_discovery_cues.py \
  --summary results/discovery/wildchat_20k_repair_cues/summary.json \
  --metadata results/discovery/wildchat_20k_repair_cues/hit_metadata_hashed.csv \
  --out-dir results/discovery/wildchat_20k_repair_cues \
  --out-md paper/discovery_cue_analysis.md
conda run -n reprompt_tax python scripts/analyze_human_audit_design.py \
  --packet data/human_audit/human_audit_packet_v0.2.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --out-dir results/tables/human_audit_v0.2_design \
  --out-md paper/human_audit_design_audit_v02.md
conda run -n reprompt_tax python scripts/test_score_auto.py
conda run -n reprompt_tax python scripts/lint_claim_boundaries.py
conda run -n reprompt_tax python scripts/validate_paper_claims.py
conda run -n reprompt_tax python scripts/validate_qualitative_examples.py
conda run -n reprompt_tax python scripts/validate_human_audit_packet.py
conda run -n reprompt_tax python scripts/validate_followup_probe.py
conda run -n reprompt_tax python scripts/make_artifact_manifest.py --check
```

Build:

```bash
cd paper
latexmk -pdf -interaction=nonstopmode main.tex
```

Check the TeX log has no warning/error/overfull/underfull markers:

```bash
rg -n "Warning|undefined|Overfull|Underfull|Error" paper/main.log
```

If native-speaker annotations are completed, summarize them with
`scripts/validate_completed_human_audit.py` and
`scripts/summarize_human_audit.py`, then update this checklist before widening
the claim boundary.
