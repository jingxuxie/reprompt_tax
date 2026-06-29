# RePromptTax Claim-Evidence Checklist

This checklist maps paper-facing claims to the artifacts that support them. It
is intended to keep the draft conservative and easy to audit.

## Paper-Facing Claims

| Claim | Evidence | Validation |
|---|---|---|
| The benchmark is a 120-item stress pilot over 3 language pairs, 4 task families, and 10 items per cell. | `data/benchmark_stress_v0.2.jsonl` | `scripts/validate_paper_claims.py` checks 120 rows, unique IDs, and exact cell counts. |
| The paper-facing stress benchmark has release-hygiene checks for duplicate prompts, scoring-marker coverage, preservation-span coverage, prompt lengths, and privacy-like markers. | `paper/benchmark_quality_audit_v02.md`, `results/tables/benchmark_quality_v02/` | `scripts/analyze_benchmark_quality.py` generates the audit; `scripts/validate_paper_claims.py` checks 120 unique prompts, zero normalized duplicates, zero privacy-marker hits, and expected family coverage. |
| A v0.3 synthetic coverage scaffold broadens non-English target-content editing coverage without changing the paper-facing v0.2 result. | `data/benchmark_stress_v0.3_expansion.jsonl`, `paper/coverage_expansion_v03.md`, `results/tables/coverage_expansion_v03/` | `scripts/generate_coverage_expansion_v03.py`, `scripts/analyze_coverage_expansion_v03.py`, and `scripts/validate_coverage_expansion_v03.py` check 60 rows, six coverage slices, zero model-result rows, privacy hygiene, and the native-validation-before-claims caveat. |
| The v0.3 coverage scaffold now has a launch-ready native-review packet, but not completed native validation. | `data/coverage_native_review_v03/`, `paper/coverage_native_review_design_v03.md`, `results/tables/coverage_native_review_v03_design/` | `scripts/make_coverage_native_review_packet_v03.py`, `scripts/validate_coverage_native_review_packet_v03.py`, and `scripts/analyze_coverage_native_review_design_v03.py` check all 60 synthetic rows, six 10-row coverage slices, blank review fields, roster/checklist files, and the not-completed-native-validation caveat. `scripts/make_coverage_native_review_sheets_v03.py` and `scripts/validate_coverage_native_review_sheets_v03.py` generate and validate per-slice browser review sheets that export the same CSV schema. `scripts/validate_completed_coverage_native_review_v03.py` and `scripts/summarize_coverage_native_review_v03.py` define the future completed-review gate, with `scripts/test_coverage_native_review_completion.py` covering the validator plumbing. `scripts/analyze_coverage_native_review_adjudication.py`, `scripts/finalize_coverage_native_review_adjudication.py`, and `scripts/test_coverage_native_review_adjudication.py` define the stronger two-reviewer adjudication path. |
| A six-item v0.3 `gpt-5.4-mini` smoke verifies that the new coverage scaffold is runnable and scoreable, without making a headline benchmark claim. | `paper/coverage_smoke_gpt54mini_v03.md`, `results/model_outputs/openai_gpt54mini_stress_v03_smoke6.jsonl`, `results/tables/openai_gpt54mini_stress_v03_smoke6/` | `scripts/analyze_coverage_smoke_v03.py` reports 5/6 baseline FTGA, 6/6 contract FTGA, one repaired baseline failure, and 2,260 saved provider-reported tokens; `scripts/validate_coverage_smoke_v03.py` checks the exact rows and the native-validation-before-claims caveat. |
| A 24-item v0.3 `gpt-5.4-mini` pilot provides a larger synthetic coverage diagnostic without making a headline benchmark claim. | `paper/coverage_pilot_gpt54mini_v03.md`, `results/model_outputs/openai_gpt54mini_stress_v03_pilot24.jsonl`, `results/tables/openai_gpt54mini_stress_v03_pilot24/` | `scripts/build_coverage_pilot_v03_outputs.py` merges the six smoke rows with an 18-item remaining shard; `scripts/analyze_coverage_pilot_v03.py` reports 75.0% baseline FTGA, 95.8% contract FTGA, 5 improved and 0 worsened paired items, and `scripts/validate_coverage_pilot_v03.py` checks exact rows, failures, tokens, and caveats. |
| A six-item v0.3 `gpt-5.5` smoke provides a flagship contrast on the expanded coverage slices. | `paper/coverage_smoke_gpt55_v03.md`, `results/model_outputs/openai_gpt55_stress_v03_smoke6.jsonl`, `results/tables/openai_gpt55_stress_v03_smoke6/` | `scripts/analyze_coverage_smoke_v03.py` reports 6/6 baseline and 6/6 contract FTGA with zero repair rows; `scripts/validate_coverage_smoke_v03.py` checks exact rows, tokens, and the non-paper-facing caveat with GPT-5.5-specific expected values. |
| Tracked API usage and provenance are summarized without double-counting historical shards. | `paper/experiment_ledger_v02.md`, `results/tables/experiment_ledger_v02/` | `scripts/summarize_experiment_ledger.py` reports 1,504 saved API response rows and 285,930 saved provider-reported tokens across the main evaluation, prompt-control diagnostic, prompt-ablation diagnostic, v0.3 pilot, GPT-5.5 v0.3 smoke, repair-realism diagnostic, original judge audit, and GPT-5.5 judge refresh. `scripts/validate_paper_claims.py` checks the totals and that no dollar-cost estimate is claimed. |
| Baseline GPT-4.1-family models exhibit measurable re-prompt tax on the stress pilot. | `results/tables/openai_three_model_stress_v02_full120/metrics_summary.csv` | `scripts/validate_paper_claims.py` checks all main metric values against `paper/main.tex`. |
| The Global Interaction Contract improves FTGA, mean RTT, and mean token tax for every model on the paper-facing stress pilot. | `results/tables/openai_three_model_stress_v02_full120/metrics_summary.csv`, `paper/main.tex` | `scripts/validate_paper_claims.py` checks FTGA, mean RTT, mean token tax, unresolved rate, Repair@1, and Repair@2. |
| The paired mitigation effect is positive for FTGA and reduces RTT/token tax on the paper-facing stress pilot. | `results/tables/openai_three_model_stress_v02_full120/paired_contract_effects_by_model.csv` | `scripts/validate_paper_claims.py` checks paired effect values and the paper text. |
| Language-slice effects show the aggregate gain is strongest on Arabic-English, weaker on Spanish-English, and saturated on Hindi-English in this stress pilot. | `paper/language_slice_analysis_v02_full120.md`, `results/tables/openai_three_model_stress_v02_full120/language_slice_*.csv` | `scripts/analyze_language_slices.py` generates paired language-slice effects. `scripts/validate_paper_claims.py` checks headline slice values and the caveat that this is not a population-level claim. |
| Repair-dynamics analysis shows how trajectories move among first-turn success, one-repair success, two-repair success, and unresolved outcomes. | `paper/repair_dynamics_v02_full120.md`, `results/tables/openai_three_model_stress_v02_full120/repair_*.csv` | `scripts/analyze_repair_dynamics.py` generates RTT distributions and paired transition matrices. `scripts/validate_paper_claims.py` checks headline RTT distributions, paired movement, and residual unresolved caveats. |
| Repair-realism evidence shows first-repair success on dominant editing-preservation failures is sensitive to repair wording. | `paper/repair_realism_editing_baseline24.md`, `results/scores/openai_three_model_stress_v02_repair_realism_editing_baseline24.jsonl`, `results/tables/openai_three_model_stress_v02_repair_realism_editing_baseline24/` | `scripts/analyze_repair_realism.py` reports 24/24 success for saved standard and terse repairs, 17/24 for frustrated repair, and 5/24 for explicit source-language contract repair; `scripts/validate_repair_realism.py` and `scripts/validate_paper_claims.py` check exact rows, paired effects, and the user-study caveat. |
| Token tax is a repair-burden ratio, not an absolute API-cost claim; the longer contract prompt increases absolute total tokens. | `paper/token_burden_analysis_v02_full120.md`, `results/tables/openai_three_model_stress_v02_full120/token_burden_by_model.csv`, `results/tables/openai_three_model_stress_v02_full120/token_burden_paired_effects_by_model.csv` | `scripts/analyze_token_burden.py` generates absolute token-burden tables. `scripts/validate_paper_claims.py` checks headline token values and the caveat. |
| All-five-model efficiency tradeoff extends the token-tax caveat to the current-model refresh. | `paper/efficiency_tradeoff_v02.md`, `results/tables/efficiency_tradeoff_v02/` | `scripts/analyze_efficiency_tradeoff.py` and `scripts/validate_efficiency_tradeoff.py` check that normalized token tax falls for all five full-run models while absolute total tokens increase for all five; no dollar-cost estimate is claimed. |
| The follow-up plan readiness audit separates paper-facing completed evidence from launch-ready-but-unlabeled human/native review surfaces. | `paper/followup_plan_readiness_v02.md`, `results/tables/followup_plan_readiness_v02/followup_plan_readiness.csv` | `scripts/analyze_followup_plan_readiness.py` maps `additional_experiments_plan .md` to 15 plan items, and `scripts/validate_followup_plan_readiness.py` checks eight paper-facing complete items, two supporting complete diagnostics, three launch-ready annotation blockers, one bounded v0.3 diagnostic surface, and one not-started collaborator-language-pair item. |
| Paired sign-test sensitivity supports the strongest FTGA effects while showing mini's FTGA change is weaker. | `paper/paired_significance_v02_full120.md`, `results/tables/openai_three_model_stress_v02_full120/paired_significance_by_model.csv` | `scripts/paired_significance.py` computes exact two-sided sign tests over paired items. `scripts/validate_paper_claims.py` checks the key counts and supplemental artifact. |
| Current-model refresh evidence shows RePromptTax persists on full 120-item `gpt-5.4-mini` and `gpt-5.5` runs, with model-specific scope limits. | `paper/current_model_refresh_v02.md`, `results/tables/current_model_refresh_v02/`, `results/tables/openai_gpt54mini_stress_v02_full120/`, `results/tables/openai_gpt55_stress_v02_full120/` | `scripts/validate_current_model_refresh.py` checks the full `gpt-5.4-mini` and `gpt-5.5` values, provider-reported usage totals, the scorer-coverage fix, the two residual GPT-5.5 contract first-turn failures, and zero GPT-5.5 contract unresolved trajectories. |
| Current-model uncertainty checks make the GPT-5.5 headline statistically explicit while bounding the `gpt-5.4-mini` claim. | `paper/current_model_uncertainty_v02.md`, `results/tables/current_model_uncertainty_v02/current_model_uncertainty.csv` | `scripts/analyze_current_model_uncertainty.py` combines paired bootstrap intervals with exact paired sign tests; `scripts/validate_current_model_uncertainty.py` checks that `gpt-5.5` FTGA is +16.7 pp with a [10.0, 24.2] pp item-bootstrap interval and 20/0 improved/worsened paired items, while `gpt-5.4-mini` FTGA has a [-0.8, 11.7] pp interval that crosses zero but a positive [0.010, 0.269]x token-tax interval. |
| Current-model heterogeneity checks show the GPT-5.5 refresh is multilingual but editing-preservation concentrated, while `gpt-5.4-mini` is not robust across strata. | `paper/current_model_heterogeneity_v02.md`, `results/tables/current_model_heterogeneity_v02/` | `scripts/analyze_current_model_heterogeneity.py` reports language-pair, task-family, and leave-one-stratum paired effects; `scripts/validate_current_model_heterogeneity.py` checks `gpt-5.5` language-pair deltas of +25.0, +20.0, and +5.0 pp, a +60.0 pp editing-preservation delta, and only +2.2 pp when editing is removed, while `gpt-5.4-mini` becomes negative when Arabic-English or editing preservation is removed. |
| Current-model contract-regression risk distinguishes the clean GPT-5.5 effect from the lower-cost-model boundary. | `paper/current_model_regression_risk_v02.md`, `results/tables/current_model_regression_risk_v02/` | `scripts/analyze_current_model_regression_risk.py` isolates paired baseline-pass/contract-fail and resolved-to-unresolved shifts; `scripts/validate_current_model_regression_risk.py` checks that `gpt-5.5` has 20 fixes and 0 first-turn regressions, while `gpt-5.4-mini` has 11 fixes, 5 first-turn regressions, 4 resolved-to-unresolved shifts, and content-preservation avoids 3 of those 5 regression cases. |
| Current-model residual-error analysis identifies where the GPT-5.x refresh still fails and bounds the mitigation claim. | `paper/current_model_error_analysis_v02.md`, `results/tables/current_model_error_analysis_v02/` | `scripts/analyze_current_model_error_analysis.py` reports that `gpt-5.5` contract leaves two Spanish-English editing-preservation first-turn failures with zero unresolved trajectories, while `gpt-5.4-mini` contract leaves 18 first-turn failures and six unresolved trajectories. `scripts/validate_current_model_error_analysis.py` checks the exact counts, paired transitions, and residual-case IDs. |
| Current-model qualitative case studies make the GPT-5.5 headline and lower-cost-model boundary inspectable from saved outputs. | `paper/current_model_case_studies_v02.md`, `results/tables/current_model_case_studies_v02/current_model_case_studies.csv` | `scripts/analyze_current_model_case_studies.py` extracts four fixed cases from saved GPT-5.x score logs: a `gpt-5.5` baseline row fixed by the contract, a `gpt-5.5` contract residual repaired in one turn, and two unresolved `gpt-5.4-mini` contract cases. `scripts/validate_current_model_case_studies.py` checks exact IDs, RTTs, failure types, pass labels, and response snippets. |
| Current-model scorer sensitivity shows the GPT-5.x refresh headline is not driven by one fragile automatic component. | `paper/current_model_scorer_sensitivity_v02.md`, `results/tables/current_model_scorer_sensitivity_v02/` | `scripts/analyze_current_model_scorer_sensitivity.py` relaxes one scorer component at a time over 480 current-model first-turn rows; `scripts/validate_current_model_scorer_sensitivity.py` checks that `gpt-5.5` contract only rises from 98.3% to 100.0% when language is relaxed, while `gpt-5.4-mini` contract rises from 85.0% to 89.2% when preservation is relaxed. |
| Generation-progress probing shows the stress set distinguishes GPT-4.1-family and GPT-5.x-family behavior without becoming a broad leaderboard. | `paper/generation_progress_probe_v02.md`, `results/tables/generation_progress_probe_v02/` | `scripts/analyze_generation_progress_probe.py` compares saved trajectory metrics across the five full-run models. `scripts/validate_generation_progress_probe.py` checks 96/360 GPT-4.1-family baseline failure pairs, 46/240 GPT-5.x baseline failure pairs, 20/240 GPT-5.x contract failure pairs, and the two current-family contract hard items. |
| Current-model prompt-mechanism evidence shows content-preservation scaffolding is close to the full contract on `gpt-5.4-mini` and `gpt-5.5`, but does not establish prompt dominance. | `paper/current_prompt_mechanism_gpt54mini_v02.md`, `paper/current_prompt_mechanism_gpt55_v02.md`, `results/tables/current_prompt_mechanism_gpt54mini_v02/`, `results/tables/current_prompt_mechanism_gpt55_v02/`, `results/tables/openai_gpt54mini_stress_v02_full120_content_preservation/`, `results/tables/openai_gpt55_stress_v02_full120_content_preservation/` | `scripts/validate_current_prompt_mechanism.py` checks the full 120-item content-preservation values for both current models, paired content-vs-contract effects, provider-reported usage, and the conservative near-tie/mechanism wording. |
| Prompt-family scorecard consolidates the prompt-mechanism evidence and bounds prompt-dominance claims. | `paper/prompt_family_scorecard_v02.md`, `results/tables/prompt_family_scorecard_v02/` | `scripts/analyze_prompt_family_scorecard.py` and `scripts/validate_prompt_family_scorecard.py` check that content preservation is highest-FTGA in the three tested models, current-model content-vs-contract margins are +0.8 pp, and generic-helpfulness was only tested on `gpt-4.1-nano`. |
| All-five-model paired significance supports the aggregate first-turn mitigation claim under both model-item and item-cluster units. | `paper/all_model_paired_significance_v02.md`, `results/tables/all_model_paired_significance_v02/all_model_paired_significance.csv` | `scripts/analyze_all_model_paired_significance.py` and `scripts/validate_all_model_paired_significance.py` check 67 fixes vs. 6 regressions over 600 paired model-item rows, plus the repeated-item sensitivity check with 24 net-positive vs. 5 net-negative items. |
| All-five-model clustered uncertainty bounds the aggregate FTGA gain under prompt resampling. | `paper/all_model_uncertainty_v02.md`, `results/tables/all_model_uncertainty_v02/all_model_cluster_bootstrap.csv` | `scripts/analyze_all_model_uncertainty.py` and `scripts/validate_all_model_uncertainty.py` check the +10.2 point aggregate FTGA gain with a +5.8 to +15.0 prompt-cluster bootstrap interval, plus slice intervals for generation, task family, and language pair. |
| Contract-benefit decomposition shows the all-five-model first-turn gain is concentrated in editing preservation. | `paper/contract_benefit_decomposition_v02.md`, `results/tables/contract_benefit_decomposition_v02/` | `scripts/analyze_contract_benefit_decomposition.py` and `scripts/validate_contract_benefit_decomposition.py` check 600 paired model-item rows, 67 contract fixes, 6 regressions, and that editing preservation contributes 61 of 67 fixes and all +61 net first-turn gain. The artifact remains automatic-score mechanism evidence, not completed human/native validation. |
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
| A paired GPT-5.5 judge refresh on the same 72 rows agrees with the automatic scorer on 70/72 labels and with the GPT-4.1 judge on 69/72 labels. | `paper/judge_refresh_gpt55_v02_full120.md`, `results/scores/openai_three_model_stress_v02_full120_judge_gpt55_audit72.jsonl`, `results/tables/openai_three_model_stress_v02_full120_judge_refresh_gpt55/` | `scripts/analyze_judge_refresh.py` computes auto-vs-judge and judge-vs-judge agreement, and `scripts/validate_judge_refresh.py` plus `scripts/validate_paper_claims.py` check the exact paired sample, zero parse errors, disagreement rows, and conservative non-human-audit wording. |
| Related-work positioning distinguishes RePromptTax from broad multilingual benchmarks, output-language alignment, multi-turn dialogue preference evaluation, and broad leaderboard claims. | `paper/main.tex`, `paper/related_work_positioning_v02.md`, `paper/refs.bib` | `scripts/validate_paper_claims.py` checks the related-work citations and the positioning note, including the MT-Bench/Chatbot Arena distinction, GPT-5.x current-model framing, repair-realism diagnostics, launch-ready human/native review protocols, and the `gpt-5.4-mini` regression-risk caveat. |
| Automatic scorer rule behavior is covered by deterministic regression tests for language, script, preservation, task, and register/locale failures. | `scripts/score_auto.py`, `scripts/test_score_auto.py` | `scripts/test_score_auto.py` checks 11 controlled cases. `scripts/validate_paper_claims.py` invokes it. |
| The WildChat scan is only a bounded aggregate motivation check, not a prevalence estimate. | `results/discovery/wildchat_20k_repair_cues/summary.json`, `paper/discovery_snapshot.md` | `scripts/validate_paper_claims.py` checks scan counts, category counts, and that no raw text was written. |
| Hashed WildChat cue metadata supports the taxonomy without exposing raw text. | `paper/discovery_cue_analysis.md`, `results/discovery/wildchat_20k_repair_cues/cue_*.csv`, `results/discovery/wildchat_20k_repair_cues/repeated_cue_conversations_hashed.csv` | `scripts/analyze_discovery_cues.py` reports unique conversations by category, repeated cue conversations, top cue patterns, and language metadata. `scripts/validate_paper_claims.py` checks the counts and no-raw-text caveat. |
| The human audit packet is launch-ready but not completed human validation. | `data/human_audit/`, `data/human_audit/audit_manifest_v0.2.md`, `data/human_audit/human_audit_launch_checklist_v0.2.md`, `docs/human_audit_guide.md` | `scripts/validate_human_audit_packet.py` checks blinding, blank annotation fields, balanced strata, language slices, launch checklist, and smoke-only marking. `scripts/validate_paper_claims.py` also checks packet readiness. |
| Static per-language human-audit review sheets make the launch packet easier to collect without exposing private answer-key fields. | `data/human_audit/review_sheets_v0.2/`, `scripts/make_human_audit_review_sheets.py` | `scripts/validate_human_audit_review_sheets.py` checks all 72 audit IDs across the three language sheets, 24 rows per sheet, blank annotation fields, local CSV export fields, and absence of private answer-key markers. |
| The human audit design covers all 72 model/condition/language/family strata and includes both automatic passes and failures. | `paper/human_audit_design_audit_v02.md`, `results/tables/human_audit_v0.2_design/` | `scripts/analyze_human_audit_design.py` reports 57 auto-pass and 15 auto-fail sampled rows, confirms no private fields in the blinded packet, and checks that completed annotation is still required before widening claims. |
| Current-model outputs have a separate launch-ready human-audit packet, but not completed human validation. | `data/current_model_human_audit/`, `paper/current_model_human_audit_design_v02.md`, `results/tables/current_model_human_audit_v02_design/` | `scripts/make_human_audit_packet.py` builds a 48-row current-model packet from `gpt-5.4-mini` and `gpt-5.5` first-turn rows, `scripts/validate_current_model_human_audit_packet.py` checks the blinded packet, review sheets, and 32-pass/16-fail failure-enriched design, and `scripts/validate_paper_claims.py` invokes the validator. Completed labels are still required before claiming human validation for current-model rows. |
| Future human/native-review labels have pre-specified acceptance thresholds before any claim is widened. | `paper/human_audit_acceptance_rules_v02.md`, `results/tables/human_audit_acceptance_rules_v02/human_audit_acceptance_rules.csv` | `scripts/analyze_human_audit_acceptance_rules.py` and `scripts/validate_human_audit_acceptance_rules.py` check that the 72-row audit needs at least 65 pass/fail agreements and 306 component agreements, the 48-row current-model audit needs at least 44 pass/fail agreements and 204 component agreements, and the 60-row v0.3 native review needs all rows marked release usable before v0.3 benchmark claims. |
| The human/native-review thresholds have an auditable statistical rationale. | `paper/human_audit_threshold_rationale_v02.md`, `results/tables/human_audit_threshold_rationale_v02/human_audit_threshold_rationale.csv` | `scripts/analyze_human_audit_threshold_rationale.py` and `scripts/validate_human_audit_threshold_rationale.py` compute the threshold rates and Wilson 95% intervals for 65/72, 306/360, 44/48, 204/240, and 60/60, while preserving the boundary that no completed labels are reported yet. |
| The three incomplete label surfaces have one consolidated launch pack. | `paper/label_collection_launch_pack_v02.md`, `results/tables/label_collection_launch_pack_v02/` | `scripts/analyze_label_collection_launch_pack.py` and `scripts/validate_label_collection_launch_pack.py` check 180 reviewer-facing packet rows, 18 roster-template slots, 12 static review sheets, finalization/adjudication commands, and the no-completed-human/native-validation claim boundary. |
| The sendable reviewer bundles have a dispatch manifest with expected return filenames and claim-gate status. | `paper/label_collection_dispatch_v02.md`, `results/tables/label_collection_dispatch_v02/`, `results/label_collection_bundles_v02/label_collection_bundle_manifest.csv` | `scripts/analyze_label_collection_dispatch.py` and `scripts/validate_label_collection_dispatch.py` check all 12 zip bundles, 180 reviewer-facing rows, bundle checksums, unique completed CSV return paths, and that claim gates remain `no_claim` until qualified completed labels arrive. |
| Completed human validation has a strict future gate and must not be confused with the smoke file. | `paper/human_audit_completion_plan.md`, `scripts/validate_completed_human_audit.py` | `scripts/validate_completed_human_audit.py` validates a completed 72-row annotation file, requires a qualified annotator roster, and rejects smoke-only files unless `--allow-smoke` is explicitly used for plumbing tests. |
| The earlier 24-item v0.2 probe remains reproducible as historical diagnostic evidence. | `data/stress_v02_new_balanced_24_ids.txt`, `results/tables/openai_three_model_stress_v02_new24/` | `scripts/validate_followup_probe.py` checks that v0.2 extends v0.1 exactly for the first five items per cell, the 24-item probe is balanced, and follow-up metrics match the documented diagnostic. |
| The paper-facing release package is reproducible from a deterministic artifact manifest. | `paper/artifact_manifest.json`, `paper/artifact_manifest.md` | `scripts/make_artifact_manifest.py --check` validates hashes, sizes, and expected artifact membership. `scripts/validate_paper_claims.py` invokes it. |
| Unsupported claim widening is linted before submission. | `scripts/lint_claim_boundaries.py`, `paper/main.tex`, `paper/extended_abstract_draft.md`, `paper/results_snapshot.md` | `scripts/lint_claim_boundaries.py` rejects representative/prevalence/generalization/human-validation overclaims on claim surfaces and checks required caveats. `scripts/validate_paper_claims.py` invokes it. |

## Safe Main Claim

On a 120-item synthetic stress pilot, GPT-4.1-family and GPT-5.x-family API
models exhibit measurable re-prompt tax under baseline prompting, especially on
implicit content-language preservation. A simple Global Interaction Contract
improves first-turn alignment and reduces turn/token tax on this pilot, with
the cleanest current-model result on `gpt-5.5`, but it does not eliminate
first-turn misalignment or residual exact-preservation failures. Two stratified
blinded LLM-judge audits support most sampled automatic pass/fail labels, while
native-speaker validation remains necessary before stronger final claims.

## Claims Not Supported Yet

- Do not claim the benchmark is representative of all multilingual or
  code-switched users.
- Do not claim prevalence of re-prompt tax in WildChat or any real-user
  dataset.
- Do not claim the mitigation fully solves multilingual interaction failures.
- Do not claim cross-provider generality.
- Do not claim native-speaker validation has been completed.
- Do not claim the current-model human-audit launch packet is completed human
  validation; it only prepares GPT-5.x rows for qualified annotation.
- Do not describe the 24-item v0.2 probe as the current paper-facing result;
  the paper-facing result is the completed 120-item v0.2 evaluation.
- Do not treat the generic-helpfulness control as proof that every mitigation
  gain is specific to multilingual-contract wording.
- Do not claim the full Global Interaction Contract is the best prompt tested;
  the nano content-preservation ablation performs better in this diagnostic.
- Do not claim content-preservation scaffolding dominates the full contract on
  current models; on `gpt-5.4-mini`, it is essentially tied and slightly worse
  on token tax, while on `gpt-5.5` it is one net item better than the full
  contract with sign-test p=1.0.
- Do not describe the six-item v0.3 smoke as paper-facing benchmark evidence;
  it only verifies that the synthetic coverage expansion is runnable and
  scoreable.
- Do not describe the 24-item v0.3 pilot as paper-facing benchmark evidence;
  it is still synthetic and requires native validation before claims.
- Do not describe the v0.3 native-review launch packet as completed native
  validation; it only prepares the synthetic rows for qualified review.
- Do not describe the six-item GPT-5.5 v0.3 smoke as evidence that the
  expanded benchmark is solved; it is only a small contrastive diagnostic.
- Do not describe token-tax reductions as absolute API-cost reductions; the
  all-five-model efficiency analysis shows the longer contract prompt increases
  absolute total tokens for every full-run model.
- Do not describe the earlier `gpt-5.5` pilot as the current paper-facing
  result; the current paper-facing `gpt-5.5` result is the completed 120-item
  run.
- Do not overstate the `gpt-5.4-mini` current-model full run: the FTGA direction
  is positive and token-tax reduction is stronger, but the FTGA sign test is not
  decisive and unresolved rate increases from 2.5% to 5.0%.

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
conda run -n reprompt_tax python scripts/make_coverage_native_review_packet_v03.py
conda run -n reprompt_tax python scripts/validate_coverage_native_review_packet_v03.py
conda run -n reprompt_tax python scripts/analyze_coverage_native_review_design_v03.py
conda run -n reprompt_tax python scripts/test_coverage_native_review_completion.py
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

If v0.3 coverage-native-review labels are completed, first run the stronger
two-reviewer adjudication path when duplicate independent rows are available:
`scripts/analyze_coverage_native_review_adjudication.py` followed by
`scripts/finalize_coverage_native_review_adjudication.py`. Then validate and
summarize the finalized one-row-per-item labels with
`scripts/validate_completed_coverage_native_review_v03.py` and
`scripts/summarize_coverage_native_review_v03.py`, then update this checklist
before treating v0.3 as paper-facing benchmark evidence.
