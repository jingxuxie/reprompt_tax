# RePromptTax Artifact Manifest

Schema: `reprompt-tax-artifact-manifest-v1`

## Notes

- Deterministic manifest for paper-facing artifacts only.
- API keys, raw external logs, caches, and TeX build intermediates are intentionally excluded.
- Run scripts/make_artifact_manifest.py after regenerating artifacts.

## Reproduction Commands

- `conda run -n reprompt_tax python scripts/run_submission_checks.py`
- `conda run -n reprompt_tax python scripts/build_full_v02_scores.py`
- `conda run -n reprompt_tax python scripts/compute_metrics.py --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl --out-dir results/tables/openai_three_model_stress_v02_full120`
- `conda run -n reprompt_tax python scripts/build_full_v02_prompt_control_scores.py`
- `conda run -n reprompt_tax python scripts/compute_metrics.py --scores results/scores/openai_nano_stress_v02_full120_generic_helpfulness_auto_scores.jsonl --out-dir results/tables/openai_nano_stress_v02_full120_generic_helpfulness`
- `conda run -n reprompt_tax python scripts/score_auto.py --benchmark data/benchmark_stress_v0.2.jsonl --outputs results/model_outputs/openai_nano_stress_v02_full120_content_preservation.jsonl --out results/scores/openai_nano_stress_v02_full120_content_preservation_auto_scores.jsonl`
- `conda run -n reprompt_tax python scripts/compute_metrics.py --scores results/scores/openai_nano_stress_v02_full120_content_preservation_auto_scores.jsonl --out-dir results/tables/openai_nano_stress_v02_full120_content_preservation`
- `conda run -n reprompt_tax python scripts/paired_effects.py --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv --out-dir results/tables/openai_three_model_stress_v02_full120`
- `conda run -n reprompt_tax python scripts/analyze_language_slices.py --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv --out-dir results/tables/openai_three_model_stress_v02_full120 --out-md paper/language_slice_analysis_v02_full120.md`
- `conda run -n reprompt_tax python scripts/analyze_repair_dynamics.py --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv --out-dir results/tables/openai_three_model_stress_v02_full120 --out-md paper/repair_dynamics_v02_full120.md`
- `conda run -n reprompt_tax python scripts/analyze_benchmark_quality.py --benchmark data/benchmark_stress_v0.2.jsonl --out-dir results/tables/benchmark_quality_v02 --out-md paper/benchmark_quality_audit_v02.md`
- `conda run -n reprompt_tax python scripts/generate_coverage_expansion_v03.py --out data/benchmark_stress_v0.3_expansion.jsonl`
- `conda run -n reprompt_tax python scripts/analyze_coverage_expansion_v03.py --benchmark data/benchmark_stress_v0.3_expansion.jsonl --out-dir results/tables/coverage_expansion_v03 --out-md paper/coverage_expansion_v03.md`
- `conda run -n reprompt_tax python scripts/validate_coverage_expansion_v03.py --benchmark data/benchmark_stress_v0.3_expansion.jsonl --tables-dir results/tables/coverage_expansion_v03 --report paper/coverage_expansion_v03.md`
- `conda run -n reprompt_tax python scripts/make_coverage_native_review_packet_v03.py --benchmark data/benchmark_stress_v0.3_expansion.jsonl --out-dir data/coverage_native_review_v03`
- `conda run -n reprompt_tax python scripts/validate_coverage_native_review_packet_v03.py --benchmark data/benchmark_stress_v0.3_expansion.jsonl --out-dir data/coverage_native_review_v03`
- `conda run -n reprompt_tax python scripts/make_coverage_native_review_sheets_v03.py --packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv --out-dir data/coverage_native_review_v03/review_sheets_v03`
- `conda run -n reprompt_tax python scripts/validate_coverage_native_review_sheets_v03.py --packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv --out-dir data/coverage_native_review_v03/review_sheets_v03`
- `conda run -n reprompt_tax python scripts/analyze_coverage_native_review_design_v03.py --packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv --out-dir results/tables/coverage_native_review_v03_design --out-md paper/coverage_native_review_design_v03.md`
- `conda run -n reprompt_tax python scripts/score_auto.py --benchmark data/benchmark_stress_v0.3_expansion.jsonl --outputs results/model_outputs/openai_gpt54mini_stress_v03_smoke6.jsonl --out results/scores/openai_gpt54mini_stress_v03_smoke6_auto_scores.jsonl`
- `conda run -n reprompt_tax python scripts/compute_metrics.py --scores results/scores/openai_gpt54mini_stress_v03_smoke6_auto_scores.jsonl --out-dir results/tables/openai_gpt54mini_stress_v03_smoke6`
- `conda run -n reprompt_tax python scripts/analyze_coverage_smoke_v03.py --benchmark data/benchmark_stress_v0.3_expansion.jsonl --scores results/scores/openai_gpt54mini_stress_v03_smoke6_auto_scores.jsonl --outputs results/model_outputs/openai_gpt54mini_stress_v03_smoke6.jsonl --out-dir results/tables/openai_gpt54mini_stress_v03_smoke6 --out-md paper/coverage_smoke_gpt54mini_v03.md`
- `conda run -n reprompt_tax python scripts/validate_coverage_smoke_v03.py --outputs results/model_outputs/openai_gpt54mini_stress_v03_smoke6.jsonl --scores results/scores/openai_gpt54mini_stress_v03_smoke6_auto_scores.jsonl --tables-dir results/tables/openai_gpt54mini_stress_v03_smoke6 --report paper/coverage_smoke_gpt54mini_v03.md`
- `conda run -n reprompt_tax python scripts/build_coverage_pilot_v03_outputs.py --smoke results/model_outputs/openai_gpt54mini_stress_v03_smoke6.jsonl --remaining results/model_outputs/openai_gpt54mini_stress_v03_pilot24_remaining18.jsonl --pilot-ids data/stress_v03_pilot24_ids.txt --out results/model_outputs/openai_gpt54mini_stress_v03_pilot24.jsonl`
- `conda run -n reprompt_tax python scripts/score_auto.py --benchmark data/benchmark_stress_v0.3_expansion.jsonl --outputs results/model_outputs/openai_gpt54mini_stress_v03_pilot24.jsonl --out results/scores/openai_gpt54mini_stress_v03_pilot24_auto_scores.jsonl`
- `conda run -n reprompt_tax python scripts/compute_metrics.py --scores results/scores/openai_gpt54mini_stress_v03_pilot24_auto_scores.jsonl --out-dir results/tables/openai_gpt54mini_stress_v03_pilot24`
- `conda run -n reprompt_tax python scripts/analyze_coverage_pilot_v03.py --benchmark data/benchmark_stress_v0.3_expansion.jsonl --scores results/scores/openai_gpt54mini_stress_v03_pilot24_auto_scores.jsonl --outputs results/model_outputs/openai_gpt54mini_stress_v03_pilot24.jsonl --out-dir results/tables/openai_gpt54mini_stress_v03_pilot24 --out-md paper/coverage_pilot_gpt54mini_v03.md`
- `conda run -n reprompt_tax python scripts/validate_coverage_pilot_v03.py --outputs results/model_outputs/openai_gpt54mini_stress_v03_pilot24.jsonl --scores results/scores/openai_gpt54mini_stress_v03_pilot24_auto_scores.jsonl --tables-dir results/tables/openai_gpt54mini_stress_v03_pilot24 --report paper/coverage_pilot_gpt54mini_v03.md`
- `conda run -n reprompt_tax python scripts/score_auto.py --benchmark data/benchmark_stress_v0.3_expansion.jsonl --outputs results/model_outputs/openai_gpt55_stress_v03_smoke6.jsonl --out results/scores/openai_gpt55_stress_v03_smoke6_auto_scores.jsonl`
- `conda run -n reprompt_tax python scripts/compute_metrics.py --scores results/scores/openai_gpt55_stress_v03_smoke6_auto_scores.jsonl --out-dir results/tables/openai_gpt55_stress_v03_smoke6`
- `conda run -n reprompt_tax python scripts/analyze_coverage_smoke_v03.py --benchmark data/benchmark_stress_v0.3_expansion.jsonl --scores results/scores/openai_gpt55_stress_v03_smoke6_auto_scores.jsonl --outputs results/model_outputs/openai_gpt55_stress_v03_smoke6.jsonl --out-dir results/tables/openai_gpt55_stress_v03_smoke6 --out-md paper/coverage_smoke_gpt55_v03.md`
- `conda run -n reprompt_tax python scripts/validate_coverage_smoke_v03.py --outputs results/model_outputs/openai_gpt55_stress_v03_smoke6.jsonl --scores results/scores/openai_gpt55_stress_v03_smoke6_auto_scores.jsonl --tables-dir results/tables/openai_gpt55_stress_v03_smoke6 --report paper/coverage_smoke_gpt55_v03.md --expected-model gpt-5.5 --expected-api-rows 12 --expected-input-tokens 1632 --expected-output-tokens 870 --expected-baseline-first-turn-passes 6 --expected-contract-first-turn-passes 6 --expected-first-turn-failure-count 0 --expected-successful-repair-rows 0 --expected-baseline-mean-rtt 0 --expected-contract-mean-rtt 0 --expected-es-ar-baseline-ftga 1 --expected-failure-item '' --expected-failure-types ''`
- `conda run -n reprompt_tax python scripts/analyze_token_burden.py --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl --out-dir results/tables/openai_three_model_stress_v02_full120 --out-md paper/token_burden_analysis_v02_full120.md`
- `conda run -n reprompt_tax python scripts/summarize_experiment_ledger.py --out-dir results/tables/experiment_ledger_v02 --out-md paper/experiment_ledger_v02.md`
- `conda run -n reprompt_tax python scripts/analyze_failure_modes.py --tables-dir results/tables/openai_three_model_stress_v02_full120 --paper-out paper/failure_mode_analysis_v02_full120.md`
- `conda run -n reprompt_tax python scripts/analyze_item_consistency.py --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv --out-dir results/tables/openai_three_model_stress_v02_full120 --out-md paper/item_consistency_analysis_v02_full120.md`
- `conda run -n reprompt_tax python scripts/analyze_component_breakdown.py --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl --out-dir results/tables/openai_three_model_stress_v02_full120 --out-md paper/component_breakdown_v02_full120.md`
- `conda run -n reprompt_tax python scripts/analyze_scorer_ablation.py --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl --out-dir results/tables/openai_three_model_stress_v02_full120 --out-md paper/scorer_ablation_sensitivity_v02_full120.md`
- `conda run -n reprompt_tax python scripts/analyze_task_useful_failures.py --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl --out-dir results/tables/openai_three_model_stress_v02_full120 --out-md paper/task_useful_failure_analysis_v02_full120.md --expected-first-turn-rows 720`
- `conda run -n reprompt_tax python scripts/analyze_prompt_control.py`
- `conda run -n reprompt_tax python scripts/analyze_prompt_ablation.py`
- `conda run -n reprompt_tax python scripts/build_error_atlas.py --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl --trajectories results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv --out-csv results/tables/openai_three_model_stress_v02_full120/first_turn_error_atlas.csv --out-md paper/error_atlas_v02_full120.md`
- `conda run -n reprompt_tax python scripts/paired_significance.py --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv --out-csv results/tables/openai_three_model_stress_v02_full120/paired_significance_by_model.csv --out-md paper/paired_significance_v02_full120.md`
- `conda run -n reprompt_tax python scripts/score_auto.py --benchmark data/benchmark_stress_v0.2.jsonl --outputs results/model_outputs/openai_gpt54mini_stress_v02_full120.jsonl --out results/scores/openai_gpt54mini_stress_v02_full120_auto_scores.jsonl`
- `conda run -n reprompt_tax python scripts/compute_metrics.py --scores results/scores/openai_gpt54mini_stress_v02_full120_auto_scores.jsonl --out-dir results/tables/openai_gpt54mini_stress_v02_full120`
- `conda run -n reprompt_tax python scripts/paired_effects.py --trajectory-metrics results/tables/openai_gpt54mini_stress_v02_full120/trajectory_metrics.csv --out-dir results/tables/openai_gpt54mini_stress_v02_full120`
- `conda run -n reprompt_tax python scripts/paired_significance.py --trajectory-metrics results/tables/openai_gpt54mini_stress_v02_full120/trajectory_metrics.csv --out-csv results/tables/openai_gpt54mini_stress_v02_full120/paired_significance_by_model.csv --out-md paper/paired_significance_gpt54mini_v02_full120.md`
- `conda run -n reprompt_tax python scripts/analyze_task_useful_failures.py --scores results/scores/openai_gpt54mini_stress_v02_full120_auto_scores.jsonl --out-dir results/tables/openai_gpt54mini_stress_v02_full120 --out-md paper/task_useful_failure_analysis_gpt54mini_v02_full120.md --expected-first-turn-rows 240`
- `conda run -n reprompt_tax python scripts/score_auto.py --benchmark data/benchmark_stress_v0.2.jsonl --outputs results/model_outputs/openai_gpt54mini_stress_v02_full120_content_preservation.jsonl --out results/scores/openai_gpt54mini_stress_v02_full120_content_preservation_auto_scores.jsonl`
- `conda run -n reprompt_tax python scripts/compute_metrics.py --scores results/scores/openai_gpt54mini_stress_v02_full120_content_preservation_auto_scores.jsonl --out-dir results/tables/openai_gpt54mini_stress_v02_full120_content_preservation`
- `conda run -n reprompt_tax python scripts/score_auto.py --benchmark data/benchmark_stress_v0.2.jsonl --outputs results/model_outputs/openai_gpt55_stress_v02_pilot40.jsonl --out results/scores/openai_gpt55_stress_v02_pilot40_auto_scores.jsonl`
- `conda run -n reprompt_tax python scripts/compute_metrics.py --scores results/scores/openai_gpt55_stress_v02_pilot40_auto_scores.jsonl --out-dir results/tables/openai_gpt55_stress_v02_pilot40`
- `conda run -n reprompt_tax python scripts/paired_effects.py --trajectory-metrics results/tables/openai_gpt55_stress_v02_pilot40/trajectory_metrics.csv --out-dir results/tables/openai_gpt55_stress_v02_pilot40`
- `conda run -n reprompt_tax python scripts/paired_significance.py --trajectory-metrics results/tables/openai_gpt55_stress_v02_pilot40/trajectory_metrics.csv --out-csv results/tables/openai_gpt55_stress_v02_pilot40/paired_significance_by_model.csv --out-md paper/paired_significance_gpt55_v02_pilot40.md`
- `conda run -n reprompt_tax python scripts/analyze_task_useful_failures.py --scores results/scores/openai_gpt55_stress_v02_pilot40_auto_scores.jsonl --out-dir results/tables/openai_gpt55_stress_v02_pilot40 --out-md paper/task_useful_failure_analysis_gpt55_v02_pilot40.md --expected-first-turn-rows 80`
- `conda run -n reprompt_tax python scripts/score_auto.py --benchmark data/benchmark_stress_v0.2.jsonl --outputs results/model_outputs/openai_gpt55_stress_v02_full120.jsonl --out results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl`
- `conda run -n reprompt_tax python scripts/compute_metrics.py --scores results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl --out-dir results/tables/openai_gpt55_stress_v02_full120`
- `conda run -n reprompt_tax python scripts/paired_effects.py --trajectory-metrics results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv --out-dir results/tables/openai_gpt55_stress_v02_full120`
- `conda run -n reprompt_tax python scripts/paired_significance.py --trajectory-metrics results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv --out-csv results/tables/openai_gpt55_stress_v02_full120/paired_significance_by_model.csv --out-md paper/paired_significance_gpt55_v02_full120.md`
- `conda run -n reprompt_tax python scripts/analyze_task_useful_failures.py --scores results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl --out-dir results/tables/openai_gpt55_stress_v02_full120 --out-md paper/task_useful_failure_analysis_gpt55_v02_full120.md --expected-first-turn-rows 240`
- `conda run -n reprompt_tax python scripts/score_auto.py --benchmark data/benchmark_stress_v0.2.jsonl --outputs results/model_outputs/openai_gpt55_stress_v02_full120_content_preservation.jsonl --out results/scores/openai_gpt55_stress_v02_full120_content_preservation_auto_scores.jsonl`
- `conda run -n reprompt_tax python scripts/compute_metrics.py --scores results/scores/openai_gpt55_stress_v02_full120_content_preservation_auto_scores.jsonl --out-dir results/tables/openai_gpt55_stress_v02_full120_content_preservation`
- `conda run -n reprompt_tax python scripts/analyze_current_model_refresh.py`
- `conda run -n reprompt_tax python scripts/validate_current_model_refresh.py`
- `conda run -n reprompt_tax python scripts/analyze_current_model_uncertainty.py`
- `conda run -n reprompt_tax python scripts/validate_current_model_uncertainty.py`
- `conda run -n reprompt_tax python scripts/analyze_current_model_heterogeneity.py`
- `conda run -n reprompt_tax python scripts/validate_current_model_heterogeneity.py`
- `conda run -n reprompt_tax python scripts/analyze_current_model_regression_risk.py`
- `conda run -n reprompt_tax python scripts/validate_current_model_regression_risk.py`
- `conda run -n reprompt_tax python scripts/analyze_current_model_error_analysis.py`
- `conda run -n reprompt_tax python scripts/validate_current_model_error_analysis.py`
- `conda run -n reprompt_tax python scripts/analyze_current_model_case_studies.py`
- `conda run -n reprompt_tax python scripts/validate_current_model_case_studies.py`
- `conda run -n reprompt_tax python scripts/analyze_current_model_scorer_sensitivity.py`
- `conda run -n reprompt_tax python scripts/validate_current_model_scorer_sensitivity.py`
- `conda run -n reprompt_tax python scripts/analyze_generation_progress_probe.py`
- `conda run -n reprompt_tax python scripts/validate_generation_progress_probe.py`
- `conda run -n reprompt_tax python scripts/analyze_efficiency_tradeoff.py`
- `conda run -n reprompt_tax python scripts/validate_efficiency_tradeoff.py`
- `conda run -n reprompt_tax python scripts/analyze_followup_plan_readiness.py`
- `conda run -n reprompt_tax python scripts/validate_followup_plan_readiness.py`
- `conda run -n reprompt_tax python scripts/analyze_human_audit_acceptance_rules.py`
- `conda run -n reprompt_tax python scripts/validate_human_audit_acceptance_rules.py`
- `conda run -n reprompt_tax python scripts/analyze_completed_label_claim_gates.py`
- `conda run -n reprompt_tax python scripts/validate_completed_label_claim_gates.py`
- `conda run -n reprompt_tax python scripts/analyze_label_collection_launch_pack.py`
- `conda run -n reprompt_tax python scripts/validate_label_collection_launch_pack.py`
- `conda run -n reprompt_tax python scripts/build_label_collection_bundles.py`
- `conda run -n reprompt_tax python scripts/validate_label_collection_bundles.py`
- `conda run -n reprompt_tax python scripts/analyze_current_prompt_mechanism.py`
- `conda run -n reprompt_tax python scripts/validate_current_prompt_mechanism.py`
- `conda run -n reprompt_tax python scripts/analyze_judge_agreement.py --audit results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl --out-dir results/tables/openai_three_model_stress_v02_full120_judge_audit72 --out-md paper/judge_agreement_analysis_v02_full120.md`
- `conda run -n reprompt_tax python scripts/analyze_judge_refresh.py`
- `conda run -n reprompt_tax python scripts/validate_judge_refresh.py`
- `conda run -n reprompt_tax python scripts/analyze_repair_realism.py`
- `conda run -n reprompt_tax python scripts/validate_repair_realism.py`
- `conda run -n reprompt_tax python scripts/make_figures.py --tables-dir results/tables/openai_three_model_stress_v02_full120 --extra-summary results/tables/openai_gpt54mini_stress_v02_full120/metrics_summary.csv --extra-summary results/tables/openai_gpt55_stress_v02_full120/metrics_summary.csv --extra-trajectories results/tables/openai_gpt54mini_stress_v02_full120/trajectory_metrics.csv --extra-trajectories results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv --out-dir results/figures/openai_three_model_stress_v02_full120`
- `conda run -n reprompt_tax python scripts/make_human_audit_packet.py --benchmark data/benchmark_stress_v0.2.jsonl --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl --out-dir data/human_audit --packet-version v0.2 --seed 23`
- `conda run -n reprompt_tax python scripts/make_human_audit_review_sheets.py --packet data/human_audit/human_audit_packet_v0.2.csv --out-dir data/human_audit/review_sheets_v0.2 --packet-version v0.2`
- `conda run -n reprompt_tax python scripts/validate_human_audit_review_sheets.py --packet data/human_audit/human_audit_packet_v0.2.csv --out-dir data/human_audit/review_sheets_v0.2 --packet-version v0.2`
- `conda run -n reprompt_tax python scripts/analyze_human_audit_design.py --packet data/human_audit/human_audit_packet_v0.2.csv --answer-key data/human_audit/human_audit_answer_key_v0.2.csv --out-dir results/tables/human_audit_v0.2_design --out-md paper/human_audit_design_audit_v02.md`
- `conda run -n reprompt_tax python scripts/make_human_audit_packet.py --benchmark data/benchmark_stress_v0.2.jsonl --scores results/scores/openai_gpt54mini_stress_v02_full120_auto_scores.jsonl results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl --out-dir data/current_model_human_audit --packet-version v0.2_current_gpt5 --seed 29 --prefer-failures`
- `conda run -n reprompt_tax python scripts/validate_human_audit_packet.py --out-dir data/current_model_human_audit --packet-version v0.2_current_gpt5 --expected-models gpt-5.4-mini,gpt-5.5`
- `conda run -n reprompt_tax python scripts/make_human_audit_review_sheets.py --packet data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv --out-dir data/current_model_human_audit/review_sheets_v0.2_current_gpt5 --packet-version v0.2_current_gpt5`
- `conda run -n reprompt_tax python scripts/validate_human_audit_review_sheets.py --packet data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv --out-dir data/current_model_human_audit/review_sheets_v0.2_current_gpt5 --packet-version v0.2_current_gpt5`
- `conda run -n reprompt_tax python scripts/analyze_human_audit_design.py --packet data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv --answer-key data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv --out-dir results/tables/current_model_human_audit_v02_design --out-md paper/current_model_human_audit_design_v02.md --expected-models gpt-5.4-mini,gpt-5.5 --title 'Current-Model Human Audit Design Audit'`
- `conda run -n reprompt_tax python scripts/validate_current_model_human_audit_packet.py`
- `conda run -n reprompt_tax python scripts/test_coverage_native_review_completion.py`
- `conda run -n reprompt_tax python scripts/test_coverage_native_review_adjudication.py`
- `conda run -n reprompt_tax python scripts/test_human_audit_adjudication.py`
- `conda run -n reprompt_tax python scripts/test_merge_review_exports.py`
- `conda run -n reprompt_tax python scripts/test_completed_label_claim_gates.py`
- `conda run -n reprompt_tax python scripts/test_score_auto.py`
- `conda run -n reprompt_tax python scripts/lint_claim_boundaries.py`
- `conda run -n reprompt_tax python scripts/validate_result_card.py`
- `cd paper && latexmk -pdf -interaction=nonstopmode main.tex`
- `conda run -n reprompt_tax python scripts/validate_paper_claims.py`
- `conda run -n reprompt_tax python scripts/validate_qualitative_examples.py`
- `conda run -n reprompt_tax python scripts/validate_followup_probe.py`
- `conda run -n reprompt_tax python scripts/validate_human_audit_packet.py`
- `conda run -n reprompt_tax python scripts/validate_stress_benchmark.py --benchmark data/benchmark_stress_v0.2.jsonl --expected-per-cell 10`
- `conda run -n reprompt_tax python scripts/discover_repair_cues.py --dataset allenai/WildChat --split train --max-conversations 20000 --out-dir results/discovery/wildchat_20k_repair_cues`
- `conda run -n reprompt_tax python scripts/analyze_discovery_cues.py --summary results/discovery/wildchat_20k_repair_cues/summary.json --metadata results/discovery/wildchat_20k_repair_cues/hit_metadata_hashed.csv --out-dir results/discovery/wildchat_20k_repair_cues --out-md paper/discovery_cue_analysis.md`
- `rg -n "Warning|undefined|Overfull|Underfull|Error" paper/main.log`

## Artifacts

| Path | Bytes | Lines | SHA-256 |
|---|---:|---:|---|
| `README.md` | 30434 | 727 | `5157c1b2e75d074bf1f17db0efab22574a16306cf571b24effdc988a0d335d30` |
| `additional_experiments_plan .md` | 22285 | 475 | `ff4eb8d55923446896fdbb05a35c1223509cf5e7501830dadc5aef1544f6cc9a` |
| `data/benchmark_stress_v0.1.jsonl` | 72197 | 60 | `921b241f56ce8fd2d4ebff9d66b66081376d3fb0e98b94d40a450cbf785e745d` |
| `data/benchmark_stress_v0.2.jsonl` | 144232 | 120 | `b8389dae43cb474efa1473d7c957b1ce12176f2a951f1f1d16163c72a81bbb92` |
| `data/benchmark_stress_v0.3_expansion.jsonl` | 102407 | 60 | `1b8010f8dc87defdaeca1a8c59b33dd9292131b27e3cfcc0aab92bc0b700245e` |
| `data/coverage_native_review_v03/coverage_native_review_launch_checklist_v03.md` | 4995 | 89 | `210d6ef47bfbd24e9a51e7501116d3775040fc9fc0e4574be3d945040ba3bb4e` |
| `data/coverage_native_review_v03/coverage_native_review_manifest_v03.md` | 5365 | 101 | `06a6f7bf77b036ee252cbb39bf5189a1a524a50276f096ed4520987fb48c40b6` |
| `data/coverage_native_review_v03/coverage_native_review_packet_v03.csv` | 56684 | 61 | `8a66ff904779d4dd6541dee74b5da7fc83ccd82e1e1c206a7d0dc2c7577f5998` |
| `data/coverage_native_review_v03/coverage_native_review_roster_template_v03.csv` | 1661 | 13 | `293fb8dff01345ca1006408b7481c78f1ab82c8b5ab57efe0c05fadc49795ec5` |
| `data/coverage_native_review_v03/coverage_native_review_v03_arabic_instruction_arabic_filenames.csv` | 10663 | 11 | `7bde4f76e60dc10d72acfad0d654b423d158f343ea8de83d51731120cbbf44be` |
| `data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_arabic_content.csv` | 9047 | 11 | `bd05346839e4af4a19ab523d65919104c1acf3e44e3dbe3a0542be883d2eadf7` |
| `data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_hindi_content.csv` | 10036 | 11 | `b6fa66bb31c36cbbd812d34cb7e716df43b744c8b15aba2ff778214862d34947` |
| `data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_spanish_content.csv` | 9300 | 11 | `910ffe66d6af57d5482150bcf4e045898dd261db6a3cdd41226001b7ee03f490` |
| `data/coverage_native_review_v03/coverage_native_review_v03_hindi_english_instruction_hindi_devanagari.csv` | 10416 | 11 | `5f00f3a779149c7b5d395ad45df6afcfdb8ae763185153f4d7226167f724544b` |
| `data/coverage_native_review_v03/coverage_native_review_v03_spanish_instruction_arabic_quote.csv` | 9807 | 11 | `707eaa036f305ed9718f51c49415d3a9f6f11be78905dc811685743a8a8fdc13` |
| `data/coverage_native_review_v03/review_sheets_v03/README.md` | 1108 | 19 | `bdd32293510c84ada3207f94205dfddd2c500653d1f775b0278b2816326a2aa9` |
| `data/coverage_native_review_v03/review_sheets_v03/coverage_native_review_sheet_v03_arabic_instruction_arabic_filenames.html` | 25446 | 169 | `2f5448b78f9f18fb2d0afd06e3f3a9e47a68ccfc939124c60d663838c82b8465` |
| `data/coverage_native_review_v03/review_sheets_v03/coverage_native_review_sheet_v03_english_instruction_arabic_content.html` | 23782 | 169 | `a46b0697effa5a2b34e0d434a1837b030b596635c11156dd3d15171e38393893` |
| `data/coverage_native_review_v03/review_sheets_v03/coverage_native_review_sheet_v03_english_instruction_hindi_content.html` | 24767 | 169 | `862d6a5ccc6a2adf4cd171f702fabbf70a618fa6cc531fc64f851f4e6c96de15` |
| `data/coverage_native_review_v03/review_sheets_v03/coverage_native_review_sheet_v03_english_instruction_spanish_content.html` | 24039 | 169 | `1b59dbe235f52b09ec4123aa0b078c7941e44a95e474653c1b8f1440eb75f195` |
| `data/coverage_native_review_v03/review_sheets_v03/coverage_native_review_sheet_v03_hindi_english_instruction_hindi_devanagari.html` | 25199 | 169 | `ce21f9a9160ac4220e939adc17557f5db39e8c35d2170e478c1ad9eb8b05798e` |
| `data/coverage_native_review_v03/review_sheets_v03/coverage_native_review_sheet_v03_spanish_instruction_arabic_quote.html` | 24534 | 169 | `aad887ff992c625d458bece7801862404565a7eef0752ef9cf5e6c1a304d49b5` |
| `data/coverage_native_review_v03/review_sheets_v03/index.html` | 1944 | 26 | `a7d75c7fa403d813a546579c3ac59df391df2f9f48cb4be8e9591692f1ab7402` |
| `data/current_model_human_audit/audit_manifest_v0.2_current_gpt5.md` | 6655 | 139 | `728dda2971b72e44a58377d68430f258d94ca0dbb0dfce0a7b8b48450d4a3713` |
| `data/current_model_human_audit/human_audit_annotator_roster_template_v0.2_current_gpt5.csv` | 245 | 4 | `9c3a2f651cc370eee3dcbe3fcdcfef05d2278164ff6ebe4a2b15833b8cf32bd8` |
| `data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv` | 6107 | 49 | `7e110f9c6bd7891d3d08bb8137aa7de8b67a47dbe2a1b1a146aa1dac0039ce58` |
| `data/current_model_human_audit/human_audit_launch_checklist_v0.2_current_gpt5.md` | 5567 | 108 | `f6847ae5b574859ad26bfb444f2d177b229d14f8d564bdedcdb401b3c33dbbc8` |
| `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv` | 26327 | 97 | `61e626b3fe0ea6468f9e0c9be7769ab634bd59a95b43e3a3d2c00d44a1b1c49f` |
| `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_ar-en.csv` | 9781 | 36 | `514edf0f45aa93cba90d061e64c9136ddcb6a98ca2f9e6e2e9fd49482b8a43ca` |
| `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_es-en.csv` | 8629 | 36 | `712614b30b8bc0c849fcc7862dd10a152b23afe5649e2424bfe33696e94260d0` |
| `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_hi-en.csv` | 8655 | 27 | `37d1e4f121f7645a7dd8b746530bde8277692f33b447f88d72c8187a2c81fe00` |
| `data/current_model_human_audit/review_sheets_v0.2_current_gpt5/README.md` | 846 | 14 | `2715b110c65d867d167cd288116d23f724e75ac51aa632e3db153037da43e2dc` |
| `data/current_model_human_audit/review_sheets_v0.2_current_gpt5/human_audit_review_sheet_v0.2_current_gpt5_ar-en.html` | 25465 | 169 | `cc82b3583b6cfc7e901326de19e40f8ad1f9dc4d5aeb4c45de541482902c761a` |
| `data/current_model_human_audit/review_sheets_v0.2_current_gpt5/human_audit_review_sheet_v0.2_current_gpt5_es-en.html` | 24313 | 169 | `6cf082eb71079913ca216ac2cbf75ea7a544a9941375f8dc52363d5bf24e81bd` |
| `data/current_model_human_audit/review_sheets_v0.2_current_gpt5/human_audit_review_sheet_v0.2_current_gpt5_hi-en.html` | 24316 | 169 | `4872dc459f7e1ab088f393b34c3511b2cc45f5e39b3b07fb2baf17bded5199cd` |
| `data/current_model_human_audit/review_sheets_v0.2_current_gpt5/index.html` | 1204 | 23 | `e0dcd7c02b99def913e80fc3a7f991cfca511babc254398b149f1922485571eb` |
| `data/human_audit/audit_manifest_v0.2.md` | 5853 | 138 | `ec49fca2d6de8262646cacc4d9b4627ee1478c78fcbd7844aaeae5a7ea2cb561` |
| `data/human_audit/human_audit_annotator_roster_template_v0.2.csv` | 245 | 4 | `9c3a2f651cc370eee3dcbe3fcdcfef05d2278164ff6ebe4a2b15833b8cf32bd8` |
| `data/human_audit/human_audit_answer_key_v0.2.csv` | 8947 | 73 | `ccaf29c327317f032c2798ef722ecfa23d41dba57d49a4193abb45311f2d05d8` |
| `data/human_audit/human_audit_launch_checklist_v0.2.md` | 4952 | 108 | `d2fc3487603137c3b57da33a5bf7d7c3367ac6e11e91a07002777700f0228ad7` |
| `data/human_audit/human_audit_packet_v0.2.csv` | 40824 | 126 | `37a1414f3d5e613c5ae21d58bc11fe98ad72dfbac62dc89cb2bb487e6fc187f7` |
| `data/human_audit/human_audit_packet_v0.2_ar-en.csv` | 15041 | 45 | `0f40ead5586ce8670c6da783337bb98d19309036446740b7a3b1a2481faa0b9b` |
| `data/human_audit/human_audit_packet_v0.2_es-en.csv` | 13082 | 48 | `caa4bf394eac2758a942ad3403f0263e7c8ce2664cc6b76c621ece1a2914c46e` |
| `data/human_audit/human_audit_packet_v0.2_hi-en.csv` | 13439 | 35 | `e3657e91bf50cd9eac7ed2a1ca6bfc46b6efba169519ebe56ba9de687515efe3` |
| `data/human_audit/review_sheets_v0.2/README.md` | 779 | 14 | `03ac4dcd5115dbc94a5d6a0f1e65ebe5f1051b7d557d18acf05a43b9014ce657` |
| `data/human_audit/review_sheets_v0.2/human_audit_review_sheet_v0.2_ar-en.html` | 34604 | 169 | `074f52efde1dad7f4dd72686f2210c216d7785381a3007a2f8890a6ea2e6d104` |
| `data/human_audit/review_sheets_v0.2/human_audit_review_sheet_v0.2_es-en.html` | 32646 | 169 | `13e0d1de74810bea64d1deb458f941fd63a95023d590e7364ec5a4bb46fa161b` |
| `data/human_audit/review_sheets_v0.2/human_audit_review_sheet_v0.2_hi-en.html` | 32966 | 169 | `9a083896bd77446bff53e1e37458da10466ebf100ba27d5ad62603b9d6d60366` |
| `data/human_audit/review_sheets_v0.2/index.html` | 1139 | 23 | `1df21567a75422d3b1190292dff9f6277bb792db71d1a365586b1419b4b2921a` |
| `data/stress_v02_gpt55_pilot40_ids.txt` | 520 | 40 | `35c462e6985a2b906d4aa704bd91d66c8763dfc5721710203b368c6d75b4ff06` |
| `data/stress_v02_new_60_ids.txt` | 780 | 60 | `82709e81a0a165808a67a4ef52bc881fb6c44d52f494ab8654305c3069addaa1` |
| `data/stress_v02_new_balanced_24_ids.txt` | 312 | 24 | `8a62685673d2ac2d45724096c7803da191e669efdc99ccf573bb03dfba6354a2` |
| `data/stress_v02_remaining_36_ids.txt` | 468 | 36 | `1518dd71b3a07eae29f58f1c784b075523881b0e54e18427833edbf58d3d92f8` |
| `data/stress_v03_pilot24_ids.txt` | 471 | 25 | `7641fe4a5b40af2000f9f4f7be277ea5fe43b291e54aa0875c2d0641c9dad561` |
| `data/stress_v03_pilot24_remaining18_ids.txt` | 374 | 19 | `25117ca1f000fae8f5161c31cde6a265fd291ecde068caaf42dcac9081e5c950` |
| `data/stress_v03_smoke6_ids.txt` | 163 | 7 | `3c82600bd8db67ba38864412dcb94cfee1a204d94a68f3eb2b87abe101e8b724` |
| `docs/benchmark_card.md` | 6454 | 171 | `0f958cf8920e3add5ae10d5a542cb1ad065e655135d3e9fd5462d4d9f92a0199` |
| `docs/evaluation_card.md` | 7407 | 216 | `16521afa372794832dafea1e550eba71976ed8f83f369befe7324507d4243e9b` |
| `docs/human_audit_guide.md` | 13449 | 265 | `f3537e907ade875514c28aa0c9dd0b8ffc2c82f72cddc58f603fcc8f0d257ba3` |
| `docs/result_card.md` | 17740 | 403 | `523c577d0afb780b5b0b1e8cd438c12ad32f5ca09346164e311d389805453f10` |
| `paper/appendix.md` | 22584 | 541 | `a249d39b476e2b04cfb1f2e76785c1410c8deaf7fd712d58bd0f04c4bf0b4fff` |
| `paper/benchmark_quality_audit_v02.md` | 2165 | 64 | `4496d0ad427b825daa769542bbb73c6c7e68cc0a071b412c23bdcba9e69e8fdc` |
| `paper/claim_evidence_checklist.md` | 37076 | 225 | `874ecea8b59d7b4ae74d12d1cbfe7c967a85a9f20045e272301eb684cf836d42` |
| `paper/completed_label_claim_gates_v02.md` | 1125 | 15 | `00a418f89d02ff3db69b9076952826011e7895c51f51929a597881e246bbadcc` |
| `paper/component_breakdown_v02_full120.md` | 3508 | 70 | `55cefed242fc5279ab83995d48ce07768490ba1f47f07d9ea54d94eb719107cc` |
| `paper/coverage_expansion_v03.md` | 1963 | 45 | `9c0638f4c37301553fcdd821f4534434091e55c25316662ed89d97d411abec1c` |
| `paper/coverage_native_review_design_v03.md` | 2010 | 49 | `f5948a133336ed5ce9d6e711ef45f6d786430d28cc182b154a707bc8abd9362e` |
| `paper/coverage_pilot_gpt54mini_v03.md` | 4246 | 50 | `7a076f1fc124a66e39aa843ec2dfc497df1f090a2dc1e5d5a0b76edcff03521e` |
| `paper/coverage_smoke_gpt54mini_v03.md` | 1982 | 45 | `63e32796d8e4fe9f7a479fe76686790bccfb63401ef88c17eb66301ea9b53c7e` |
| `paper/coverage_smoke_gpt55_v03.md` | 1561 | 43 | `116528d3c9cf0597be1c0aa13af72ea8c297a64adade5a9d75da99c00828b54c` |
| `paper/current_model_case_studies_v02.md` | 6264 | 148 | `37acc02949ffa1b8f8d9c9ff9215dbf0a66cee645e446c21487c5c045e18e414` |
| `paper/current_model_error_analysis_v02.md` | 5088 | 69 | `0c5288746668bc0684f3630143c1c201d164f44bdc44ec5089f525e8f5beb492` |
| `paper/current_model_heterogeneity_v02.md` | 4792 | 54 | `5a8659db404279251c131c04bd71db2ee942e0782e4789a89566546dae832909` |
| `paper/current_model_human_audit_design_v02.md` | 2424 | 72 | `d2748d022b41de82a75a1f3c77d5e34a826290d0dba2b93e2b5741fbb33f7b3b` |
| `paper/current_model_refresh_v02.md` | 2484 | 39 | `b31f72b5d062b01b2dcd62e2f22794c5a26563cae9881d88a4bfc26b21eeb0cd` |
| `paper/current_model_regression_risk_v02.md` | 2858 | 42 | `9b179c9c1e8dc639d7d9d31b1de69d39f98a279994b51b1af93260d928d4d0c0` |
| `paper/current_model_scorer_sensitivity_v02.md` | 4794 | 76 | `2a5b6efed2ab4ac81ab34f585f56c1ba2ac5c72e895fbe23f9dea6832654aca4` |
| `paper/current_model_uncertainty_v02.md` | 2082 | 23 | `1df515f73531084e9ca44265cd879901dfa900072add421ece432fa0c65e2e45` |
| `paper/current_prompt_mechanism_gpt54mini_v02.md` | 2121 | 48 | `39273133673f02e31396154b213a7571514942431020b2589e03142c5c3e4d5d` |
| `paper/current_prompt_mechanism_gpt55_v02.md` | 2301 | 50 | `4fd7e3ae89b4d7fc0bfc113095900858cb7a6dc98a5b5ac9874b87815dd36ee7` |
| `paper/discovery_cue_analysis.md` | 2599 | 68 | `9d72eca4c37c1d7ba531387d845aa275b3cb2fd9cd591ed14a4a08050b9a368f` |
| `paper/discovery_snapshot.md` | 1845 | 64 | `2d5186a320b4b6b9a47e0b41c4306e5a3ffe300f923badfed375f9ed0c7ca1d4` |
| `paper/efficiency_tradeoff_v02.md` | 3136 | 49 | `d4c27f0ae567d49a16382d8b8982f819c1b550176779d881b0c92d177678eb8d` |
| `paper/error_atlas_v02_full120.md` | 46430 | 220 | `8dc96aa65041be5d702af83a5661b7557634f68d10e24e25657981be23ee119a` |
| `paper/experiment_ledger_v02.md` | 4777 | 86 | `07c9ece77151ea005a33df4943f4ffd51f4c07e79c7f5618a6685568cb78485b` |
| `paper/extended_abstract_draft.md` | 10698 | 192 | `82e21261d8e226323d1ebcb5b95acad18921a6199ea852a35f3848760f577bc6` |
| `paper/failure_mode_analysis_v02_full120.md` | 2474 | 40 | `9f451cb72c2eadbd941a9dfe40314a6a04292edbbdfd04621d26f4ea6bfb9601` |
| `paper/figures/ftga_by_condition.png` | 85086 |  | `4a8531faacea1bbcc9503e5cc2f7d9fc99efe4683e1832b4b49bb892b7793d62` |
| `paper/figures/repair_curve.png` | 124613 |  | `6014b54843d96e0387de4d122f9fb15076c04c9d5fd18fc1c19d370f8477d535` |
| `paper/followup_plan_readiness_v02.md` | 5653 | 61 | `3a24869b239bfa2e03f46ca724cdfa9c5c1cd79139ea40485512ee6d79c0d2f9` |
| `paper/generation_progress_probe_v02.md` | 2550 | 41 | `8d58b2bc2b494dc4ab73a6a22eae36fc35132dfa15de1ccfa9888614ae54be7e` |
| `paper/human_audit_acceptance_rules_v02.md` | 4662 | 73 | `32a2efbd461cdcb8536af9600b2f03522ae6d0fe0254261d66d366290b252763` |
| `paper/human_audit_completion_plan.md` | 6568 | 148 | `aff292f12b1dca4a5989767328e15281c6c677eaa4dcedb6a79700270e15c704` |
| `paper/human_audit_design_audit_v02.md` | 2513 | 74 | `d62ed82524a16695b16d6181a329843b2d334c63571d0989df43eb3ae587281b` |
| `paper/item_consistency_analysis_v02_full120.md` | 3553 | 60 | `bfbb182bbcb2e198034ba10587c69d4434a14f8d36f664b1871c0ef4c39020c0` |
| `paper/judge_agreement_analysis_v02_full120.md` | 2524 | 52 | `4fee9895693920669176c8545f14eca2f5d8ab82c4e3e5307cbe3220fccd215d` |
| `paper/judge_refresh_gpt55_v02_full120.md` | 2238 | 38 | `bbf319f6e1a682e260976f6559ca28102410596521d444b6e09d3d8c620f0a07` |
| `paper/label_collection_launch_pack_v02.md` | 9095 | 78 | `7ee715c7fb4f5a17816d31b148a0871c5c485deacc60c743c54839b2e604ac18` |
| `paper/language_slice_analysis_v02_full120.md` | 3925 | 72 | `12d4da2d0ff01b5215c9bd51a8b052c2d5ad8bde46d6d786ef34b53ffe1aa79a` |
| `paper/main.pdf` | 240230 |  | `dce37e5dd847fa426008754c5eca3e9223823d6e27b5d7d88b5a3d0d417d16f3` |
| `paper/main.tex` | 1082 | 44 | `1a09b462988020ead361be338a7d3ec29e9c104e27c384cafe408080dcdf9474` |
| `paper/paired_significance_gpt54mini_v02_full120.md` | 755 | 13 | `d29116e1c39e4a56e08e84fd86b022ce220b4b35c696c57689fc019154d8b3cc` |
| `paper/paired_significance_gpt55_v02_full120.md` | 729 | 13 | `e6bdb635f4b8bca1cdf5ceb707c6a852a2cdd581e6f344df3d476b28af4a212a` |
| `paper/paired_significance_gpt55_v02_pilot40.md` | 724 | 13 | `36b7a29bc2197b487f0c5cd20655c2eb534d0be0acc6957f671cbb51f5e76159` |
| `paper/paired_significance_v02_full120.md` | 1467 | 21 | `6093644e2ef6ac3486c690d4c22079e2985910a1792d389b9ad6274c1458e295` |
| `paper/prompt_ablation_analysis.md` | 6347 | 74 | `6ab68c79d3f7f459a7d765d0473ae2d9b55ffabc9dc4ef2df05150f205b727a8` |
| `paper/prompt_control_analysis.md` | 1614 | 33 | `268f517a0050c6eb65d8dcd1bf0f2d5274fc3f1c1fcd15d0e98fe94d811bff6d` |
| `paper/qualitative_examples.md` | 3977 | 142 | `1a417d225c1f47354a4648d094daca7618f0ab78ae54b16824e309a544b0746e` |
| `paper/refs.bib` | 8892 | 233 | `c8951f43a0f2b3dd4a3f80e0cb907d701fe9e3266d849cdb664bd004cdd56faf` |
| `paper/related_work_positioning_v02.md` | 3886 | 53 | `5510dedcb29bb2f20bd293415dd364b8647bbe77c6692367cf65ab324c6a114e` |
| `paper/repair_dynamics_v02_full120.md` | 2838 | 56 | `51355fe1c072c65b807558c210eefa2ed9529fbf0d8ffc8bf87b493e5f605269` |
| `paper/repair_realism_editing_baseline24.md` | 11576 | 82 | `abf3e0f1093555d1902dae28c95af0a18386b90800bd5aa325e437064c613073` |
| `paper/results_snapshot.md` | 27734 | 494 | `1997319a71b2a41a2acf5da70511578850266a5fa08901a45d0650f03f90dad8` |
| `paper/scorer_ablation_sensitivity_v02_full120.md` | 3167 | 57 | `fed29921eb43863bda11a671beae3b3e531e93bbffc2632d4e55bdfa044da6b3` |
| `paper/sections/00_abstract.tex` | 2043 | 29 | `5a865a3207e463913cf0198e4e3a84e9a872ca5fb30af0f2003bcfe88471a0a1` |
| `paper/sections/01_introduction.tex` | 4304 | 70 | `a011b0ecd4b8ea32399ca28323fbb69d19c8cb668f6bb6725e604346a1496d78` |
| `paper/sections/02_interaction_contracts_and_metrics.tex` | 2373 | 49 | `dc87229ec6879056dffda6407050692c575fd5e7649b0ea4113eea8ebc9a3641` |
| `paper/sections/03_benchmark_construction.tex` | 2660 | 41 | `38059ae3db8bd1b3a312083d4f251ef327837631a987cebbe3166cf7c5e45a62` |
| `paper/sections/04_experimental_protocol.tex` | 2475 | 43 | `50e4e7d0a96cea15ada689386529b2444869209d79b9aa9c8a5c0c883ad9c678` |
| `paper/sections/05_results.tex` | 7930 | 148 | `602c3bdaeb0675152bed0f379bc9c5a3deea453000f89cf122934e92218c74ed` |
| `paper/sections/06_discussion.tex` | 1789 | 28 | `9dddcc91764c33c13b3424767360903da6c95504262e29e71fa202e86b43c733` |
| `paper/sections/07_related_work.tex` | 3567 | 57 | `2f59ebb5af789aefc1d83701f9150e1262b144e66ebc5dc83a60c36a430ad5b0` |
| `paper/sections/08_limitations_and_ethics.tex` | 1939 | 32 | `6fec65aa722f6ef74bca12132aa15329e0d645df079972bb8a5df33b4bba303f` |
| `paper/sections/09_conclusion.tex` | 1042 | 16 | `4ddf2e265b15a319284fe4c67a46e69c95876bababd6cb191e98713fef2f2cbd` |
| `paper/task_useful_failure_analysis_gpt54mini_v02_full120.md` | 2857 | 61 | `c574bcbfd3b7307974cbcc7ae68c46158faa18374ee5c8a7ba6ddb640d2e5f76` |
| `paper/task_useful_failure_analysis_gpt55_v02_full120.md` | 2541 | 57 | `97ac234566ce9683b988854b153bbb77477584cd78d2ad13a5950db80086dbd4` |
| `paper/task_useful_failure_analysis_gpt55_v02_pilot40.md` | 2031 | 47 | `f06aa03f5be64e7e57c685d7990be8860771f7642097f1c2065511f555f23723` |
| `paper/task_useful_failure_analysis_v02_full120.md` | 2977 | 65 | `a9a001db707bafb0b7ba5a6c20b360234508a37000943b76b6628fa7e05a82b6` |
| `paper/token_burden_analysis_v02_full120.md` | 1595 | 34 | `197ab127d34a2951b8dddca321277c83bd40a4982cf6a98146bd6d3e94ede74c` |
| `prompts/baseline_system.txt` | 30 | 2 | `1a576e23794b48e45e2dbfc9a8c6240d60e351b2432d6ee5e9c5d06c5365c301` |
| `prompts/content_preservation_system.txt` | 427 | 5 | `8f2f6eb7cff91e81ccdb53438f4db9691155cd268d612c5a08956648e8c30613` |
| `prompts/generic_helpfulness_system.txt` | 487 | 8 | `93384811b9c6a92aeb5efd5fb2c97ab5179d67830e57703c5984f7347311b5bb` |
| `prompts/global_interaction_contract.txt` | 838 | 9 | `d6ef558ea1389e7407a86a548103d9ba5c4b711dc47ccb99826a5caf8a3501fc` |
| `prompts/judge_prompt.txt` | 848 | 32 | `f555705f9c54efb39998339343ca313ef79cfec910f919e323703e5164190ef2` |
| `reprompt_tax_workshop_paper_plan.md` | 46099 | 1541 | `db27cd7a17f68147da01204406acd4792b24d1743e02a24bded3cca3dc62049a` |
| `results/discovery/wildchat_20k_repair_cues/category_counts.csv` | 152 | 7 | `9496d33431650ed7deefd12f60ec22c2a50b17e1d48fb27ad9f8a8d461673df7` |
| `results/discovery/wildchat_20k_repair_cues/cue_category_conversation_counts.csv` | 409 | 7 | `ee0221a66d6044ca8f087f4f6808de78d42cb779e48c64034b26da8acb419f65` |
| `results/discovery/wildchat_20k_repair_cues/cue_discovery_overview.csv` | 313 | 2 | `f4ccdd34668c791208e9e39868b2bcd93f75d84b6af4ee54d86ddcb4d7c63944` |
| `results/discovery/wildchat_20k_repair_cues/cue_language_category_counts.csv` | 1528 | 34 | `b135e129d18bc613f943725598058ad93f85d4009f61187037ed8c50290be03a` |
| `results/discovery/wildchat_20k_repair_cues/cue_pattern_counts.csv` | 928 | 23 | `03435b83e6853dc7f34ce1868f81d4f0ad2bb2d4311474132beed6098ba6632e` |
| `results/discovery/wildchat_20k_repair_cues/hit_metadata_hashed.csv` | 15664 | 220 | `1a83d1a4a01840f13729b96602bb2474545622cdf218df8efb749d7f6d8381f8` |
| `results/discovery/wildchat_20k_repair_cues/repeated_cue_conversations_hashed.csv` | 1980 | 32 | `a11e0048892bfaadf43545a31e15af864c57f7ecdfe91c7dcaf25c03d8d6ccea` |
| `results/discovery/wildchat_20k_repair_cues/summary.json` | 727 | 29 | `d693234ce2293e05e467488820a79698a1c99849b765fb10a4708c76ed173182` |
| `results/figures/openai_three_model_stress_v02_full120/ftga_by_condition.png` | 85086 |  | `4a8531faacea1bbcc9503e5cc2f7d9fc99efe4683e1832b4b49bb892b7793d62` |
| `results/figures/openai_three_model_stress_v02_full120/ftga_by_condition_source.csv` | 317 | 11 | `0ee7644bba8c83d77234ea4613447bf1b8067df1243ed3bae421eea486ca41fd` |
| `results/figures/openai_three_model_stress_v02_full120/repair_curve.png` | 124613 |  | `6014b54843d96e0387de4d122f9fb15076c04c9d5fd18fc1c19d370f8477d535` |
| `results/figures/openai_three_model_stress_v02_full120/repair_curve_source.csv` | 495 | 11 | `14bbc842f9df7ea199461c7f88b948de013506abb12722042e1352b34ffbce49` |
| `results/label_collection_bundles_v02/coverage_native_review_v03/arabic_instruction_arabic_filenames.zip` | 6862 |  | `a6d239ba8154055d4e5cd149a6c3285f9c7cfa43c51c2ac9d0338522169e7472` |
| `results/label_collection_bundles_v02/coverage_native_review_v03/english_instruction_arabic_content.zip` | 6613 |  | `5120d81e8ea40620d6929605b1d2fbb253a52a3953c2815e91c96438b9118536` |
| `results/label_collection_bundles_v02/coverage_native_review_v03/english_instruction_hindi_content.zip` | 6883 |  | `9295de2b9a086a81d14f3557cd373f0f2a025eb603c8f7e13b228c56239e75a6` |
| `results/label_collection_bundles_v02/coverage_native_review_v03/english_instruction_spanish_content.zip` | 6512 |  | `97653dc8f0ab0cea293b3ea53c00779b7e5622e5b23bcd07ec5fd14164b5845d` |
| `results/label_collection_bundles_v02/coverage_native_review_v03/hindi_english_instruction_hindi_devanagari.zip` | 6935 |  | `9b794db92b009eb7e3a0144bd3c95367c731861629b4d5dfd9749dd205f5a025` |
| `results/label_collection_bundles_v02/coverage_native_review_v03/spanish_instruction_arabic_quote.zip` | 6764 |  | `cc72f48b4ce52fb11a421a851c6cedc673b4b4df19e4b8e6541f58fe096f0093` |
| `results/label_collection_bundles_v02/current_model_human_audit_v02/ar-en.zip` | 8198 |  | `5de8736621a4ee6c8a4dd2543f323ea741dc9607598ade045f3c269609432670` |
| `results/label_collection_bundles_v02/current_model_human_audit_v02/es-en.zip` | 7482 |  | `a43d00010bc7364b9474d8f7d01b82cea57d8068a119084f5584cc8fe3204648` |
| `results/label_collection_bundles_v02/current_model_human_audit_v02/hi-en.zip` | 7452 |  | `e7147d3581fd3060fe5d365bb2370cf043c843ec09197a2e3bf71e13c8f3abcc` |
| `results/label_collection_bundles_v02/human_audit_v02/ar-en.zip` | 10569 |  | `234b1233764c66e6d1eb0cc5262e3c629086d4e77704239463e6db3badc9a8e7` |
| `results/label_collection_bundles_v02/human_audit_v02/es-en.zip` | 8992 |  | `4ef5328ee36d3f3adcafb64f402122e118ccc33c47e4722bed5a90f4dd5be9f1` |
| `results/label_collection_bundles_v02/human_audit_v02/hi-en.zip` | 9222 |  | `4641a7d9fd9cbe1fe100ced5f3407792781436c90f561e4eb19edb9c2880da4c` |
| `results/label_collection_bundles_v02/label_collection_bundle_manifest.csv` | 3897 | 13 | `4ceb6d74d41536f71035540537b791a011037b73a685c46cbc14ded972257ae3` |
| `results/label_collection_bundles_v02/label_collection_bundles.md` | 2075 | 20 | `f00f3736162cc8094f44803497f24fb334c84d399bcca499783ff714962e0d57` |
| `results/model_outputs/openai_gpt54mini_stress_v02_full120.jsonl` | 110525 | 291 | `4c66bd56eaa4e176de451dc2bd14cd0422b1469094e0b4a8b6e35cf78e5e417e` |
| `results/model_outputs/openai_gpt54mini_stress_v02_full120_content_preservation.jsonl` | 49785 | 143 | `90c6a7f423468a53554c193c8dd083e196acbb729361d312d26df7bb86c7a5f3` |
| `results/model_outputs/openai_gpt54mini_stress_v03_pilot24.jsonl` | 26288 | 58 | `351f45474692025f8522cff6ea589e4f99e7f94b683261fe29be3f3c0aa2ff8b` |
| `results/model_outputs/openai_gpt54mini_stress_v03_pilot24_remaining18.jsonl` | 20320 | 45 | `a8a65b36201ea6ab1c410ae7b14b933903a59ddfd239697fe7108c41b065884f` |
| `results/model_outputs/openai_gpt54mini_stress_v03_smoke6.jsonl` | 5968 | 13 | `6e915b016d1d476b38b87a24ac781f00fe5b5cd16f0726da8aa24954447463b0` |
| `results/model_outputs/openai_gpt55_stress_v02_full120.jsonl` | 98650 | 267 | `eaecf32878d485b99ff6dd83188dd525457e4ff01842cb41cf2ef21e698e3c3d` |
| `results/model_outputs/openai_gpt55_stress_v02_full120_content_preservation.jsonl` | 40189 | 121 | `5718dfb6ebf9bb3f3310e58f44ecf955678c90a3ca8f8d569feaa647b9bbfb45` |
| `results/model_outputs/openai_gpt55_stress_v02_pilot40.jsonl` | 33066 | 88 | `f007135587e2c960bd9c5af9fe33cc79e5af997c686b9f95decf79f23c03533c` |
| `results/model_outputs/openai_gpt55_stress_v03_smoke6.jsonl` | 4889 | 12 | `ced85aa5be7081591519a2f3af9a32454674830f173a110782b49c4f8a505d06` |
| `results/scores/openai_gpt54mini_stress_v02_full120_auto_scores.jsonl` | 189950 | 291 | `a61086c23a748885286be06541128d9acf9a6205b9816b26117a1221aa588421` |
| `results/scores/openai_gpt54mini_stress_v02_full120_content_preservation_auto_scores.jsonl` | 88613 | 143 | `c48d2863c3dde0eb9787bebc599d4294f149f98624362a70b4951250f490ee56` |
| `results/scores/openai_gpt54mini_stress_v03_pilot24_auto_scores.jsonl` | 41799 | 58 | `20b8a081f6e49e3436ee530fbf030e778654acc3955b312570afc02e448edf75` |
| `results/scores/openai_gpt54mini_stress_v03_smoke6_auto_scores.jsonl` | 9404 | 13 | `30701fd4b6d666d4895c7ba4dec1430426414992d5ca815b0de660205fbe18db` |
| `results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl` | 171064 | 267 | `5a7ba061b74a82acfb30cd8a9689d185da8ff2632cbcd37fdcce8a8c7372b9d5` |
| `results/scores/openai_gpt55_stress_v02_full120_content_preservation_auto_scores.jsonl` | 72187 | 121 | `1c9ae531404846917dbf8acfa213aeb753b40733d5bc2f3e5abfe74a35a53116` |
| `results/scores/openai_gpt55_stress_v02_pilot40_auto_scores.jsonl` | 56980 | 88 | `ce1516333672212c3cbf487d2d0d5f22b179a33f47f11f64ba7a3964d7e73554` |
| `results/scores/openai_gpt55_stress_v03_smoke6_auto_scores.jsonl` | 8045 | 12 | `109b18f1614954a63f4a361ae0422e4d8ae5003104b9a7291bfa4be593b5a1b0` |
| `results/scores/openai_mini_gpt41_stress_v02_remaining36_auto_scores.jsonl` | 130033 | 195 | `e7a11b47088c5718ad95d350ef35b82e0d2995c82711845212830cd309383c28` |
| `results/scores/openai_nano_stress60_generic_helpfulness_auto_scores.jsonl` | 49693 | 75 | `ce3f43fa8b72660372f85da2f6055c108733ea4e4a71b4e5a4e0c1024a3f0421` |
| `results/scores/openai_nano_stress_v02_full120_content_preservation_auto_scores.jsonl` | 94587 | 146 | `b15f53f06f7057f1af611e35f3843137993a43f1d1937e17917d560154577d76` |
| `results/scores/openai_nano_stress_v02_full120_generic_helpfulness_auto_scores.jsonl` | 102747 | 155 | `a38a0166a0be8d6ad1e070cf7e9a72c0374104d45492381b4618bb845f1c5617` |
| `results/scores/openai_nano_stress_v02_new60_generic_helpfulness_auto_scores.jsonl` | 53054 | 80 | `81713932162a580504d253d8616b6fcc2d1d31c7051a24a8dac4c761abbb9c12` |
| `results/scores/openai_nano_stress_v02_remaining36_auto_scores.jsonl` | 71020 | 105 | `9225e333c8bbb8064594bb89938de0f8ae35b7406ac5b3f478db5b5621d943fa` |
| `results/scores/openai_three_model_stress60_auto_scores.jsonl` | 286792 | 435 | `416b18e36e02eda8bc6a284b19a4d6891f45017588659f8bb432ebaee8a3e180` |
| `results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl` | 607833 | 917 | `c12f04d5c2c69b6c0d065fee053132a8f6050055c765e89e7f719f5ed325fac4` |
| `results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl` | 71573 | 72 | `d16c073339e8e49bf4fac6963ae979db7bddaf37c75bede5ccb6000d9013ae46` |
| `results/scores/openai_three_model_stress_v02_full120_judge_gpt55_audit72.jsonl` | 75795 | 72 | `77f53250cd2e0b11ead869fe6566a6a12286d70f3f75a90c7fdb2f8a4c396f27` |
| `results/scores/openai_three_model_stress_v02_new24_auto_scores.jsonl` | 119988 | 182 | `5625b2098374fd5f20ecddeb97a4708a4d3f4b9190eb78135cce96adf842293f` |
| `results/scores/openai_three_model_stress_v02_repair_realism_editing_baseline24.jsonl` | 125548 | 96 | `543e8409404f0a90e3aec3943f535f81a3e547cc30f6adefcbe0b4f31d584d98` |
| `results/tables/benchmark_quality_v02/benchmark_quality_by_family.csv` | 434 | 5 | `451ab9592340f8ad3ec41a19985385f8666304e03d109c83ebd95c7d5eaa3a90` |
| `results/tables/benchmark_quality_v02/benchmark_quality_by_language.csv` | 339 | 4 | `9297af0e959938b107f6e058c3c2f32fff696e29a3bb4f7af51fb901f686a100` |
| `results/tables/benchmark_quality_v02/benchmark_quality_by_language_family.csv` | 936 | 13 | `cef05a1f44cfbd1e6be8f51716278395528cf03220ee339603f4657a75890b3c` |
| `results/tables/benchmark_quality_v02/benchmark_quality_summary.csv` | 388 | 2 | `81de8dd28f377cba691a4f1b8b209df13963759e48893081da672217fbdaf4d5` |
| `results/tables/completed_label_claim_gates_v02/completed_label_claim_gates.csv` | 938 | 4 | `3f6b961b5bc9c0f848e2307bd50f73a017cb30c2828421e1e37ff7a4ec854068` |
| `results/tables/coverage_expansion_v03/coverage_expansion_by_content_language.csv` | 376 | 5 | `df3a1f3ef923c42c3252fe0e3ed7984fcb229569c1deaab6e410d7c68d85c3e9` |
| `results/tables/coverage_expansion_v03/coverage_expansion_by_slice.csv` | 830 | 7 | `607790dd68a796ee451e207e3a02ad36d5d43037e88049aa7d015c120da2a6e9` |
| `results/tables/coverage_expansion_v03/coverage_expansion_privacy_scan.csv` | 41 | 2 | `2cc6131b0949a394d05f02891b61a0459e9dbcf225bcaa985e988fffae15383a` |
| `results/tables/coverage_expansion_v03/coverage_expansion_summary.csv` | 430 | 2 | `2950408f12b7585b55241ed777f33bec96d656e04b1bac407812793235ce4cff` |
| `results/tables/coverage_native_review_v03_design/coverage_native_review_by_content_language.csv` | 280 | 5 | `877f9ee278bbac52709b1b45065fd64503c54fe660f5293fb940f07afa7ef5a8` |
| `results/tables/coverage_native_review_v03_design/coverage_native_review_by_instruction_language.csv` | 283 | 5 | `cac816f0f1e7b228f802c61bd06df30084214747953fcca69fb7fb49eb698233` |
| `results/tables/coverage_native_review_v03_design/coverage_native_review_by_language_pair.csv` | 297 | 7 | `b6973dff47ea05e842d48751573896032c626c4061764e72b79fd7e10d665e3e` |
| `results/tables/coverage_native_review_v03_design/coverage_native_review_by_slice.csv` | 699 | 7 | `eb5feec68fe1fa9e18b186088957b84863de79b2a60ed64e634c607076c727fd` |
| `results/tables/coverage_native_review_v03_design/coverage_native_review_summary.csv` | 278 | 2 | `558ce7e4b8ba3c9e961a4dda1d904b041f058b94ea4bee9a61a4f91510d2d35c` |
| `results/tables/current_model_case_studies_v02/current_model_case_studies.csv` | 3710 | 5 | `6583a84171df63fc999058a166672a92730fb05e0d2016b433e8f1e6694b49d6` |
| `results/tables/current_model_error_analysis_v02/current_model_contract_residual_cases.csv` | 3523 | 21 | `fea207927335c80c42c812a3909ccbc15d7dbf9e7f1ad1c144f84b9597e62eb7` |
| `results/tables/current_model_error_analysis_v02/current_model_error_by_family.csv` | 1443 | 17 | `108e1b6b2cb1c55719745473bfb075f8e29c7564834598a734550bdc93fe0080` |
| `results/tables/current_model_error_analysis_v02/current_model_error_by_language.csv` | 1212 | 13 | `240caabbc8f8ac2cc5ca0753347d20598304e3f3b027b19da8311df6fa0538c9` |
| `results/tables/current_model_error_analysis_v02/current_model_error_summary.csv` | 636 | 5 | `110b8b58d217ea4fcf389ce665b4e5544fe710cd0bfc90a62ff27ed3821b2cb6` |
| `results/tables/current_model_error_analysis_v02/current_model_first_turn_failures.csv` | 11991 | 67 | `33ab65eb38dfbdbdd44475aae31a2d57ae0f7cc20b1fe4eead991c516d184c91` |
| `results/tables/current_model_error_analysis_v02/current_model_paired_transitions.csv` | 280 | 3 | `afc35e4f186c7c09a88bdb5c89eefb50bbb75507aff5cd621bbcaae704c1e006` |
| `results/tables/current_model_heterogeneity_v02/current_model_heterogeneity_by_stratum.csv` | 1342 | 15 | `19e33763c9f869c2014255fdba2ab57ee21dc8aec6376a2f455894828038bf04` |
| `results/tables/current_model_heterogeneity_v02/current_model_heterogeneity_leave_one.csv` | 1764 | 15 | `4e79e315e5494d0a48ea608297e38d947b5c028be77fe52c10f6221eac77bc88` |
| `results/tables/current_model_human_audit_v02_design/human_audit_design_by_auto_failure_type.csv` | 170 | 5 | `fd07a26f5e998ac3e66894a62351c1a1c4eaf0b98b095bd9f78e045034b95bcd` |
| `results/tables/current_model_human_audit_v02_design/human_audit_design_by_family.csv` | 200 | 5 | `3a6bb04d238641d9c42aa22fb4896f173cde7791138880b3ccfcaa5cadaae631` |
| `results/tables/current_model_human_audit_v02_design/human_audit_design_by_language.csv` | 117 | 4 | `7e44a07041ce6bf2efbf078893cae0a23e6376b8b4a0cca79730a6e3c501dfef` |
| `results/tables/current_model_human_audit_v02_design/human_audit_design_by_language_family.csv` | 530 | 13 | `3131f40b4a4c62ae891b1b5ea630f7815e8c787b0a65abf9844d2ff658f8939a` |
| `results/tables/current_model_human_audit_v02_design/human_audit_design_by_model_condition.csv` | 189 | 5 | `311c31ca1957667027b9c51d455601fe880993f804e490d229f6394260d6ecd3` |
| `results/tables/current_model_human_audit_v02_design/human_audit_design_summary.csv` | 275 | 2 | `8f678d1a463917e4e82ee98eb0a92d288c1f3f2694449d371485cbec105a26c9` |
| `results/tables/current_model_refresh_v02/current_model_refresh_api_usage.csv` | 139 | 3 | `4116f3c4a5034f08c73b59a0e6b16b6607ffd959ad267cfe48dd5c9d379dfc82` |
| `results/tables/current_model_refresh_v02/current_model_refresh_summary.csv` | 980 | 6 | `912eed972cef0266e3646d2d106dd8d6b6f2bcd94634d590526b6854344ca0dc` |
| `results/tables/current_model_regression_risk_v02/current_model_contract_regression_cases.csv` | 764 | 6 | `0aa0506fd02d0a7a5d29eb1546e79f7bbcfd3f8ffd136164f1c52bcb76cd88e5` |
| `results/tables/current_model_regression_risk_v02/current_model_regression_risk_summary.csv` | 455 | 3 | `e32d569f513b2f51b16569da2548ba4633f024c8c4d27fb59f299aeaf50dfdc9` |
| `results/tables/current_model_regression_risk_v02/current_model_resolved_to_unresolved_cases.csv` | 586 | 5 | `daefe73fdd48a0af8d7a2b92b4d862905cbdf50b8174a5f40f5e556b52832a4f` |
| `results/tables/current_model_scorer_sensitivity_v02/current_model_scorer_sensitivity_by_condition.csv` | 746 | 3 | `9e5e1d978daea42c35f5d6eba3105a1842358b76addff5f8fd8379960f243133` |
| `results/tables/current_model_scorer_sensitivity_v02/current_model_scorer_sensitivity_by_model_condition.csv` | 982 | 5 | `820a9c8e15f95ce20d778a75af2bd823941e5758d7c52e250b60072382de6293` |
| `results/tables/current_model_scorer_sensitivity_v02/current_model_scorer_sensitivity_by_model_family_condition.csv` | 2611 | 17 | `50b8217744a2f1856580bb7f1bd294b7a1cc78a5e210a3b9c054fcb954123d3e` |
| `results/tables/current_model_scorer_sensitivity_v02/current_model_scorer_sensitivity_failure_signatures.csv` | 1069 | 17 | `47d31b1d95b68fb28cc8a4ee440e20ae340be46f7b6cb2b5901e83c1caaca9e4` |
| `results/tables/current_model_scorer_sensitivity_v02/current_model_scorer_sensitivity_top_failure_signatures.csv` | 938 | 15 | `99e4eafb471ad331154b5d4eb55e1b07ddb4997c4e2328da11d16f56615adde4` |
| `results/tables/current_model_uncertainty_v02/current_model_uncertainty.csv` | 911 | 3 | `2491e5f562adc475733a272ced446f2bc7a3f003aa95a8c68859b4557bf04d7a` |
| `results/tables/current_prompt_mechanism_gpt54mini_v02/current_prompt_mechanism_api_usage.csv` | 140 | 3 | `21c52a500e9b2351bfad53e05e25f40192d5f658bb13cf9814e06c1cad7c3c0e` |
| `results/tables/current_prompt_mechanism_gpt54mini_v02/current_prompt_mechanism_by_family.csv` | 977 | 13 | `125a5277e3d13e5f6e11ac97dfa068a986be336638e942173cc33bf2a82c94d6` |
| `results/tables/current_prompt_mechanism_gpt54mini_v02/current_prompt_mechanism_paired_effects.csv` | 379 | 4 | `afe9a5fe0bf2a9b095583c72677e26c168287136e4d4a05359f25e2ed4c7c9a8` |
| `results/tables/current_prompt_mechanism_gpt54mini_v02/current_prompt_mechanism_summary.csv` | 244 | 4 | `4f450d43655b0b3d5e993e52c44e5d9ce90148434f26494cd11babef1f1d18da` |
| `results/tables/current_prompt_mechanism_gpt55_v02/current_prompt_mechanism_api_usage.csv` | 141 | 3 | `97fe018b14e1299ae215b689d040b3d6fdcfc157edaad9ded596c7cad5e52ebf` |
| `results/tables/current_prompt_mechanism_gpt55_v02/current_prompt_mechanism_by_family.csv` | 901 | 13 | `b7ae213dcad9ef0086b7964efccc030d13e2298868d3368e88eed760e3fd0612` |
| `results/tables/current_prompt_mechanism_gpt55_v02/current_prompt_mechanism_paired_effects.csv` | 385 | 4 | `040ea9e165570cb5fea39d8c9ea330205fc8eb55c54acad9e1b90ed85ea11241` |
| `results/tables/current_prompt_mechanism_gpt55_v02/current_prompt_mechanism_summary.csv` | 229 | 4 | `6822be1025311e9d96c97f4a2ecd2b7c48586f8479879ec455742acb51f1a814` |
| `results/tables/efficiency_tradeoff_v02/efficiency_tradeoff_by_model_condition.csv` | 1091 | 11 | `4c87fc27c2ad3ad0f36fee1ba391030afbf4a4abf491727579a87b344df5a35b` |
| `results/tables/efficiency_tradeoff_v02/efficiency_tradeoff_paired_effects.csv` | 607 | 6 | `3fed2b66a9944333af4a2c566bfda16cc77009d20da097dd8240fcb335b171cf` |
| `results/tables/efficiency_tradeoff_v02/efficiency_tradeoff_trajectory_metrics.csv` | 126373 | 1201 | `b0e80e0ad2a2889b9c724042c5bee0b0a5734aac9a5457527c549fce860b7b9c` |
| `results/tables/experiment_ledger_v02/api_usage_by_artifact.csv` | 1822 | 9 | `97229aae5c88adeb876244e052d2cecda057509496224034f7c0d4966777a168` |
| `results/tables/experiment_ledger_v02/api_usage_by_judge.csv` | 338 | 3 | `4bee1c715489b8fd177bdcb1d625ae018791df9725a846d7ef64fc125b27e119` |
| `results/tables/experiment_ledger_v02/api_usage_by_model_condition.csv` | 1781 | 13 | `6c1801f0ab6928eccd6108f0e7015485703a63b58f8be77387cf22ca5e00efd2` |
| `results/tables/experiment_ledger_v02/api_usage_by_repair_variant.csv` | 1457 | 10 | `e3bf74631a6aacb693df373aa295460e3936f79f74cb89f53d3b11393dcd834a` |
| `results/tables/experiment_ledger_v02/experiment_ledger_summary.csv` | 319 | 2 | `bb577054b3540faf0b4f6bca01ae14e4d448c1173c91f470d100f4aaa1cd5574` |
| `results/tables/followup_plan_readiness_v02/followup_plan_readiness.csv` | 6271 | 16 | `82989be3e5e95c5690a5f3bf6340a15e09528629a5602163d1136602f7712b04` |
| `results/tables/generation_progress_probe_v02/generation_progress_by_family.csv` | 1137 | 17 | `ad2365fd922e3d47b54f835e0d4278ef3ae1349cf18f1d0da3c2572311ab7090` |
| `results/tables/generation_progress_probe_v02/generation_progress_categories.csv` | 2745 | 10 | `0d5e007efb55bce5efbea103f4495992000e5a58aac66a2fd4b6d712affef28f` |
| `results/tables/generation_progress_probe_v02/generation_progress_item_matrix.csv` | 7970 | 121 | `a679568c6702b35ab0544d36946dca60d402e54c8e098e75241b4239471b2cbb` |
| `results/tables/generation_progress_probe_v02/generation_progress_summary.csv` | 389 | 5 | `7f8cc248e85fc40e2e8ae36952ebfa58dca93fda3f9306b105e29b9501846120` |
| `results/tables/human_audit_acceptance_rules_v02/human_audit_acceptance_rules.csv` | 3944 | 4 | `c9c2c2778909ec52fab76ccc22a0444723c61840af310e0e60622034590acfa3` |
| `results/tables/human_audit_v0.2_design/human_audit_design_by_auto_failure_type.csv` | 171 | 5 | `f2a4261f07f52bb296be871752ccd7111ed602f4857a0a54d8c43f47aaf2b8a3` |
| `results/tables/human_audit_v0.2_design/human_audit_design_by_family.csv` | 195 | 5 | `7f76f1da7d6300d3c04f929219950579492d2b949568e323d39ec4a4ee3f134d` |
| `results/tables/human_audit_v0.2_design/human_audit_design_by_language.csv` | 116 | 4 | `8594125546c33a82351613e13b8b87005ea3e2fb65ba3b8411eb6b1133157362` |
| `results/tables/human_audit_v0.2_design/human_audit_design_by_language_family.csv` | 544 | 13 | `ea1ae074d6223d2ef449925e3d811ba01526ea472d73b5d76d36fa4f136187b7` |
| `results/tables/human_audit_v0.2_design/human_audit_design_by_model_condition.csv` | 262 | 7 | `8a2aeb3ba789051e04696739d12faf32611a2ee46a0d0ae83e4737530d108c94` |
| `results/tables/human_audit_v0.2_design/human_audit_design_summary.csv` | 275 | 2 | `a330b1ec0eea2ee67b6406c4c9ddb741f9ea073f56c56adb839234cd410b4619` |
| `results/tables/label_collection_launch_pack_v02/label_collection_commands.csv` | 6362 | 16 | `a25381f0d49a3764482a4ddd350f4bc76a8fa63dd2fcc366e6e7ca8182b6d813` |
| `results/tables/label_collection_launch_pack_v02/label_collection_files.csv` | 2058 | 19 | `e607561268e6d1b8f9386620742d0c2db311ebb4dad4357c9b6b0ca781e234ea` |
| `results/tables/label_collection_launch_pack_v02/label_collection_surfaces.csv` | 3356 | 4 | `f8a1063139347ef4ff0128317f2c2097e7e2cefdae8bdb02ce0bff065e247980` |
| `results/tables/openai_gpt54mini_stress_v02_full120/failure_types_by_family.csv` | 859 | 12 | `bd9f5859aa571ec77fa4f668ecbd2f99368a15ef9ac090c9cd3c848c61fa2111` |
| `results/tables/openai_gpt54mini_stress_v02_full120/metrics_by_family.csv` | 1282 | 9 | `1687b371b0ff2518142dae439708c496a5535d8dc7e97a6caa294942b690ca71` |
| `results/tables/openai_gpt54mini_stress_v02_full120/metrics_by_language.csv` | 828 | 7 | `b3b00654b0c153b584bbb233910d66c2d095862d93f4e99f916f57c3ae31d93b` |
| `results/tables/openai_gpt54mini_stress_v02_full120/metrics_summary.csv` | 482 | 3 | `fede95aa50a77a74fee495f569403b5b10edbd6e649b5b13bba1324646a7bfea` |
| `results/tables/openai_gpt54mini_stress_v02_full120/paired_contract_effects_by_family.csv` | 1004 | 5 | `fb5a64e69cccbf0975d750b78daa8d994a8bd0163ae8c33cf058e184396307bc` |
| `results/tables/openai_gpt54mini_stress_v02_full120/paired_contract_effects_by_model.csv` | 498 | 2 | `dd3d3e33856121a89de32ab484680493566f612944bd8fe13779288c71b3241f` |
| `results/tables/openai_gpt54mini_stress_v02_full120/paired_significance_by_model.csv` | 479 | 5 | `106a4d64f19af91b0aaa8004c4a66ae72e7e322812b68b97d9d8e791b5dfc21f` |
| `results/tables/openai_gpt54mini_stress_v02_full120/task_useful_failure_by_condition.csv` | 518 | 3 | `61f9b9c8872c3fc332a1cfb2251528697265f0d6352655bfc445046260591d9d` |
| `results/tables/openai_gpt54mini_stress_v02_full120/task_useful_failure_by_family_condition.csv` | 1045 | 9 | `72564c3af00d56d24a1c016b7f3acbc782d9d23fb810be2c271d48681ff4ac87` |
| `results/tables/openai_gpt54mini_stress_v02_full120/task_useful_failure_by_language_condition.csv` | 795 | 7 | `8604231760c7bd64af84851316799dd1f24a9a9d5814fb860b2dd493087a026b` |
| `results/tables/openai_gpt54mini_stress_v02_full120/task_useful_failure_by_model_condition.csv` | 550 | 3 | `db45248698776c5aa6ad2d9c7c7c9c0f9a3d2f8b575b75fdcb0942fa06f314d4` |
| `results/tables/openai_gpt54mini_stress_v02_full120/task_useful_failure_signatures.csv` | 380 | 7 | `bb02cb644fc5ad213e1ddb4f88a95fa55999db9a5d1bcf494747aeb5a805ec5e` |
| `results/tables/openai_gpt54mini_stress_v02_full120/trajectory_metrics.csv` | 22583 | 241 | `df53db86f345ee278c089c314cd0ab0894ba1dabf3c840cf24cc75e227c9daf6` |
| `results/tables/openai_gpt54mini_stress_v02_full120_content_preservation/failure_types_by_family.csv` | 479 | 6 | `b4537414af6751935ce11de0f3f699ec4267f9528bd509eef6b369232c750106` |
| `results/tables/openai_gpt54mini_stress_v02_full120_content_preservation/metrics_by_family.csv` | 800 | 5 | `1948068610537cb479b017a20712549d8f64b2951f42f2ce59c45d5468dc8099` |
| `results/tables/openai_gpt54mini_stress_v02_full120_content_preservation/metrics_by_language.csv` | 515 | 4 | `1f1020f3d83fa25814a46a5c7b7b9537d64e8efc8c5922ee6ebdc2d68b172b42` |
| `results/tables/openai_gpt54mini_stress_v02_full120_content_preservation/metrics_summary.csv` | 386 | 2 | `84ea0ae4c5443d7626a9761d0c9cc3bed009ecc30770ebfbdf8df5cae353dcae` |
| `results/tables/openai_gpt54mini_stress_v02_full120_content_preservation/trajectory_metrics.csv` | 12576 | 121 | `3b74a4e7d402ee9b8d73034dc9be344932dfd28cb5682881deff60d232b602b3` |
| `results/tables/openai_gpt54mini_stress_v03_pilot24/coverage_pilot_by_slice.csv` | 985 | 13 | `b7e78259383c896224142f7176ec1f850f5f2e89a21b84184f29b09f751d3dc1` |
| `results/tables/openai_gpt54mini_stress_v03_pilot24/coverage_pilot_first_turn_failures.csv` | 2184 | 8 | `7fda847ea8c118008e57548e3e30dcbb24cacc1556988fd0176c823d13e0ff19` |
| `results/tables/openai_gpt54mini_stress_v03_pilot24/coverage_pilot_paired_items.csv` | 2058 | 25 | `d60a905a865de44e5c6387eb93c13503c8d5ffacb5a1ddc1f96ff79559404509` |
| `results/tables/openai_gpt54mini_stress_v03_pilot24/coverage_pilot_summary.csv` | 274 | 3 | `ed4f3bba0bd287180d97e4c000d0ec2bc537a04d9cc6e08c61581bcbae20beb2` |
| `results/tables/openai_gpt54mini_stress_v03_pilot24/failure_types_by_family.csv` | 311 | 4 | `15c22bfccd0ecbb2a7ee4f28a9426b7c40c9354dde0875463dd0a5fb38296a10` |
| `results/tables/openai_gpt54mini_stress_v03_pilot24/metrics_by_family.csv` | 527 | 3 | `c71b8096a03a3633ad54c5a11e344911c85e7214f4cb6c21a2957c0888094211` |
| `results/tables/openai_gpt54mini_stress_v03_pilot24/metrics_by_language.csv` | 946 | 13 | `bf46e925f4c2a5df868e453d97301dada1654cf7eb82d38a5b7508a318cdf503` |
| `results/tables/openai_gpt54mini_stress_v03_pilot24/metrics_summary.csv` | 473 | 3 | `18cd31793ed72ea2896bb4997358d9f59c423240979f165c4ea1e4c957092af0` |
| `results/tables/openai_gpt54mini_stress_v03_pilot24/trajectory_metrics.csv` | 4582 | 49 | `63d80481955a6f71f08ffaad9fbd8eae700bec2e74a8d31178e7e60a1a165d1f` |
| `results/tables/openai_gpt54mini_stress_v03_smoke6/coverage_smoke_by_slice.csv` | 650 | 7 | `d2dc741d60e36d6be27dac5310b8b89115be1fb46b1dc0a95963eb9639a91d09` |
| `results/tables/openai_gpt54mini_stress_v03_smoke6/coverage_smoke_first_turn_failures.csv` | 432 | 2 | `3828d852e18ba6d9d611a13db62b86f93260913078d3c1fba7662d7b0c199953` |
| `results/tables/openai_gpt54mini_stress_v03_smoke6/coverage_smoke_summary.csv` | 370 | 2 | `5e15fc3ad07b138ba1746bb93bb8393f94bbedef71158784268cd6b64ad172e9` |
| `results/tables/openai_gpt54mini_stress_v03_smoke6/failure_types_by_family.csv` | 141 | 2 | `f6124e8f822b542e7d89d8a6c0d1f56447a72189dffa267875ecb261bd4ac5a4` |
| `results/tables/openai_gpt54mini_stress_v03_smoke6/metrics_by_family.csv` | 386 | 3 | `6ebe03059bfa88256868d9348cf78f404bcd4d0a1b41f29e318eb1d8d2aa97db` |
| `results/tables/openai_gpt54mini_stress_v03_smoke6/metrics_by_language.csv` | 838 | 13 | `d78fccfaa59e7219c88ec0607c2431144f75a19a18085a013995763a797032aa` |
| `results/tables/openai_gpt54mini_stress_v03_smoke6/metrics_summary.csv` | 332 | 3 | `498f63767d62243db4e13268b216f243f694a6dec352acfa554d3e33eadbd878` |
| `results/tables/openai_gpt54mini_stress_v03_smoke6/trajectory_metrics.csv` | 1238 | 13 | `7f0444fbf2d95cedc1aa825cc8f65a1bbbbab963e7d84f5e378455cd7c724ba2` |
| `results/tables/openai_gpt55_stress_v02_full120/failure_types_by_family.csv` | 468 | 7 | `1753fc9bcb7482f8648ab0b121d77466cdef054eda4b042cb4c4488c6c3223ce` |
| `results/tables/openai_gpt55_stress_v02_full120/metrics_by_family.csv` | 985 | 9 | `44310a5c7ef50d88e1f3b5eae9ed49f589eac9810a797aed90bb6a5e969049ab` |
| `results/tables/openai_gpt55_stress_v02_full120/metrics_by_language.csv` | 642 | 7 | `73269d38246fe3750d1f05ac40938d576fe55bfab102c17218be13adcc549921` |
| `results/tables/openai_gpt55_stress_v02_full120/metrics_summary.csv` | 507 | 3 | `370a3a4c45f7d3e592eefe387926679e00f33c11226903c0c365092029e12b0e` |
| `results/tables/openai_gpt55_stress_v02_full120/paired_contract_effects_by_family.csv` | 860 | 5 | `fd917f49cfd5206cd06712b591ae5f7e61dcccafab2cee0ced2c9692efdb75cc` |
| `results/tables/openai_gpt55_stress_v02_full120/paired_contract_effects_by_model.csv` | 489 | 2 | `c7213712cbf8d747321c6e2f321004b7e283aa24f572881b6475dc15a869802b` |
| `results/tables/openai_gpt55_stress_v02_full120/paired_significance_by_model.csv` | 506 | 5 | `1243f1c2d66f991657062d24e4a3301ae80563e9dc4ad168ab7f56b0b9275f2b` |
| `results/tables/openai_gpt55_stress_v02_full120/task_useful_failure_by_condition.csv` | 513 | 3 | `c1eb57872e668b55b11d7425053ce7607aa639a77cfb84e83208846fe18c6148` |
| `results/tables/openai_gpt55_stress_v02_full120/task_useful_failure_by_family_condition.csv` | 1030 | 9 | `ee6a76b6d3a3ee416d482965b162ca78c2472cbd375ebc6e491989ac9cb4f6f5` |
| `results/tables/openai_gpt55_stress_v02_full120/task_useful_failure_by_language_condition.csv` | 783 | 7 | `76acf7cfb21108a8cdd1cd7e65682eba3ef0289c1c4cf8f1ffae7fdac3a4b3f0` |
| `results/tables/openai_gpt55_stress_v02_full120/task_useful_failure_by_model_condition.csv` | 535 | 3 | `beabb07a2e0eff3790b804d6bc008be6b5cf840018d49a9fb76c13ede8af4ab7` |
| `results/tables/openai_gpt55_stress_v02_full120/task_useful_failure_signatures.csv` | 230 | 4 | `9bbf4f6543957140006af287bae0ec6224e523bbd25d4d790d3ef9d65d3d1d18` |
| `results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv` | 20725 | 241 | `1c8c398c970d21609fa39e33a3b827e20fc33227109a5bd5c81a6b7c92b89977` |
| `results/tables/openai_gpt55_stress_v02_full120_content_preservation/failure_types_by_family.csv` | 153 | 2 | `10184e7664b2138c1cc30f638264a82a1bb2a12b3f28e2d2fd2560992dd6dcc0` |
| `results/tables/openai_gpt55_stress_v02_full120_content_preservation/metrics_by_family.csv` | 556 | 5 | `b78eaa0c43299a53ec8f3f111b26097081d062746e1a5f435e42ddc642ace6cd` |
| `results/tables/openai_gpt55_stress_v02_full120_content_preservation/metrics_by_language.csv` | 411 | 4 | `23c9e36fc71c87e4e1dcf7613ff1d196bd132c03551c3ed66a3b74e50dc61fda` |
| `results/tables/openai_gpt55_stress_v02_full120_content_preservation/metrics_summary.csv` | 300 | 2 | `13f236bc38ef421f2e1055e903801edb85c20e27459156071723fa92dd12c02c` |
| `results/tables/openai_gpt55_stress_v02_full120_content_preservation/trajectory_metrics.csv` | 11147 | 121 | `3b838d2a7a76a658e9e8c296d02cdd382bdc7800f868b7166d6b09074581d4a2` |
| `results/tables/openai_gpt55_stress_v02_pilot40/failure_types_by_family.csv` | 262 | 4 | `86b4a8b07c7ab6ae5871a10f8feedd21ba21644341dde081c026b49a4c6e30be` |
| `results/tables/openai_gpt55_stress_v02_pilot40/metrics_by_family.csv` | 826 | 9 | `9978f4ac7d460ff2757a0ab1839a43e44e1122cbca1a0ecffcedbff0e43ecded` |
| `results/tables/openai_gpt55_stress_v02_pilot40/metrics_by_language.csv` | 700 | 7 | `9790a8ed6fbd4867c5da45506cb6fa67f5c46b6b5ff326f489be5e1239e0ae95` |
| `results/tables/openai_gpt55_stress_v02_pilot40/metrics_summary.csv` | 305 | 3 | `04dac7ee3b4b5d783a36d3615378618ae9b5aae7efd444b7d7169c3775fed119` |
| `results/tables/openai_gpt55_stress_v02_pilot40/paired_contract_effects_by_family.csv` | 757 | 5 | `c286c0d39739c898749d812243024eb1a32a84adc689e2fafe7d7f804f4926ca` |
| `results/tables/openai_gpt55_stress_v02_pilot40/paired_contract_effects_by_model.csv` | 401 | 2 | `a0cc30e33c5628fd4e5d95230a313a7400b5e22525fff10b4cc10c9893ec78b2` |
| `results/tables/openai_gpt55_stress_v02_pilot40/paired_significance_by_model.csv` | 417 | 5 | `fcb27d718fc3df23c6c5c367331a559b9c119b0b449db996721c2c293dc5d603` |
| `results/tables/openai_gpt55_stress_v02_pilot40/task_useful_failure_by_condition.csv` | 507 | 3 | `233505534f0f3e6e9e64ad8c7c5603e898681d44f089d21005cdc057bf19eb5a` |
| `results/tables/openai_gpt55_stress_v02_pilot40/task_useful_failure_by_family_condition.csv` | 1018 | 9 | `9c2143cd23c4a2563ce8ffcdd863bc4859106bbe6eaab4a151bc44e6277a2181` |
| `results/tables/openai_gpt55_stress_v02_pilot40/task_useful_failure_by_language_condition.csv` | 777 | 7 | `10472193f948d0d09b9c4c16811445c11fb4cae25b8ee377c08cbbb705fc00a7` |
| `results/tables/openai_gpt55_stress_v02_pilot40/task_useful_failure_by_model_condition.csv` | 529 | 3 | `f3e8466eb9983f98373203554316f3bc94e51d2104e1a8650130913f48f5d2e4` |
| `results/tables/openai_gpt55_stress_v02_pilot40/task_useful_failure_signatures.csv` | 80 | 1 | `b60e3554109ddb6a40f22536bee9865c638ab5d732ffdd1b32d68c398f8c4d92` |
| `results/tables/openai_gpt55_stress_v02_pilot40/trajectory_metrics.csv` | 7066 | 81 | `c3edf68f5d6e2f2d48bd9f0e3b2f5c8cd1acde7a8f8f573a760c5c77861a4d1d` |
| `results/tables/openai_gpt55_stress_v03_smoke6/coverage_smoke_by_slice.csv` | 632 | 7 | `6fe401b614d57431a27b1966cb9acd4c453cd07d2c64de1eceea8ec76df06e20` |
| `results/tables/openai_gpt55_stress_v03_smoke6/coverage_smoke_first_turn_failures.csv` | 69 | 2 | `b4bd6cc32c139d52ad3d5d100c8843e08d430a5753bf74fa5fe98b553a787772` |
| `results/tables/openai_gpt55_stress_v03_smoke6/coverage_smoke_summary.csv` | 319 | 2 | `357c9f55fd2111e9ef338eca5ea6a3829c457c7621be4fced4c5898ca6e253e2` |
| `results/tables/openai_gpt55_stress_v03_smoke6/failure_types_by_family.csv` | 0 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `results/tables/openai_gpt55_stress_v03_smoke6/metrics_by_family.csv` | 316 | 3 | `8de1cb0f9e7895947c459ff035e6cf57f2d65f538386202127cd858c35176e1e` |
| `results/tables/openai_gpt55_stress_v03_smoke6/metrics_by_language.csv` | 758 | 13 | `1888ff53f9c811b40d5f910ec69d1a482d6bec5b0547608bb7e7bced0b2d4e95` |
| `results/tables/openai_gpt55_stress_v03_smoke6/metrics_summary.csv` | 262 | 3 | `29af4486d4c4c86ecd5047e5b34f277b9f97a0f102fef296cde9a63e95ecfe00` |
| `results/tables/openai_gpt55_stress_v03_smoke6/trajectory_metrics.csv` | 1144 | 13 | `d9abb96a425de32640c9ef15d0afd1df2c474d874714f6ee9d2bbf0dae917412` |
| `results/tables/openai_nano_stress_v02_full120_content_preservation/failure_types_by_family.csv` | 660 | 8 | `5943990b66944d3bdf271c7c3b2cc214393fa9df7d58bef2c206490799ec19c4` |
| `results/tables/openai_nano_stress_v02_full120_content_preservation/metrics_by_family.csv` | 911 | 5 | `8eee16d899b98498d6def7c071244605c13680d737e4f209ea86087ae702aa68` |
| `results/tables/openai_nano_stress_v02_full120_content_preservation/metrics_by_language.csv` | 546 | 4 | `36e887c5ea16033a791161c248df571f6a777106a38eec2a76e0dd9142509b72` |
| `results/tables/openai_nano_stress_v02_full120_content_preservation/metrics_summary.csv` | 400 | 2 | `83194023e2f5499e656a43380774b12d073bc910b431750fc4b4d6ef15e69d75` |
| `results/tables/openai_nano_stress_v02_full120_content_preservation/trajectory_metrics.csv` | 12921 | 121 | `edbc0235b4dac3e772fe07cc96f013e35efa05257d57a07cd2273c67927578bd` |
| `results/tables/openai_nano_stress_v02_full120_generic_helpfulness/failure_types_by_family.csv` | 731 | 9 | `8761f608a2d36395784e15dafe07c784c3111285be0715f440ca01eab25474c6` |
| `results/tables/openai_nano_stress_v02_full120_generic_helpfulness/metrics_by_family.csv` | 814 | 5 | `250d448f93fa4586efc7b2cda222d39162ddd6732b00fc9e179f2188c5ac126a` |
| `results/tables/openai_nano_stress_v02_full120_generic_helpfulness/metrics_by_language.csv` | 539 | 4 | `f517591d24404ecd1097216e88bc43ca385f0eb9786cbbe5ff79febfe5d2b7e9` |
| `results/tables/openai_nano_stress_v02_full120_generic_helpfulness/metrics_summary.csv` | 359 | 2 | `6f8b91e67aa07104b085380ea335a15c281367547af7b5a55cc877dd310c597c` |
| `results/tables/openai_nano_stress_v02_full120_generic_helpfulness/trajectory_metrics.csv` | 13269 | 121 | `416aff2cdb616dcd88d38f97afcfa1aca02fd0108bb0aee8c23f255252386fdd` |
| `results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_by_family.csv` | 1780 | 17 | `6137cc3f43487567b3dedc27b636c4a7f595c9b685c63abc77cab161529b46ef` |
| `results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_contract_vs_content_by_family.csv` | 282 | 5 | `4690341003e933c5d5938c7b3130206c0166956c8c6aa9db116a61dd5e886f96` |
| `results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_contract_vs_content_by_language.csv` | 195 | 4 | `738caff3dee614ac9326dfe2c415380607fdee11e3d4874014a12994865e0a88` |
| `results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_contract_vs_content_examples.csv` | 4559 | 12 | `2c906cd7896f7a071cdd04f25fc9e5e5e60d88d308df7a3d32c07f729334ca94` |
| `results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_contract_vs_content_items.csv` | 34215 | 121 | `9714c9232d3035422be8f9869a10ff4aa2cd4090204a739adc622c8e51349ae8` |
| `results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_paired_effects.csv` | 736 | 6 | `335463464b4f916f3b194cec3bd68dcbd2da6dc6c3530547df2827a746092aac` |
| `results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_summary.csv` | 464 | 5 | `6387eb81c3aa6b191b261031006778a72f2aa54eb1e14a58c1836b0692e980c3` |
| `results/tables/openai_nano_stress_v02_full120_prompt_control/prompt_control_paired_effects.csv` | 498 | 4 | `91c3089e6cd6a6f5d132063c9b118248888768c96588dcaeb2e0f7a4eb8fa071` |
| `results/tables/openai_nano_stress_v02_full120_prompt_control/prompt_control_summary.csv` | 360 | 4 | `617efecc76bfd87e196eb44db9b301bc5f65fcfa523a4298069887ba400c4ea7` |
| `results/tables/openai_three_model_stress60/trajectory_metrics.csv` | 33625 | 361 | `1f94f423ca0bb98275f2599dbf67db225319d8c24163b32eeaad61702e34618a` |
| `results/tables/openai_three_model_stress_v02_full120/component_paired_effects_by_model.csv` | 818 | 19 | `2708c33f7fa815e4c393b76dd1f691cf170679363c3e6d9ba16d19309904b92d` |
| `results/tables/openai_three_model_stress_v02_full120/component_pass_by_family_condition.csv` | 914 | 9 | `635ac9c2dcb652036a944bcfec58c6b625368e1e41043b35d6674f074d680c06` |
| `results/tables/openai_three_model_stress_v02_full120/component_pass_by_language_condition.csv` | 671 | 7 | `2d554a3d42370d03d405f7ca0e2b37ef022d6705cb2837050865db0f3dbb44a5` |
| `results/tables/openai_three_model_stress_v02_full120/component_pass_by_model_condition.csv` | 692 | 7 | `2c6ddeb6f3a0cb7df344c89fbe73de33477bdbc0d8f6d1b6585cbf8e0841447e` |
| `results/tables/openai_three_model_stress_v02_full120/failure_type_summary.csv` | 1060 | 17 | `cab3cf4903f322e0a80561d3c3e5415b3c7fd997f60a366cab6ece07361be443` |
| `results/tables/openai_three_model_stress_v02_full120/failure_types_by_family.csv` | 2516 | 36 | `27237f2c134b0685e9de38420eb074b9d90a74c10a926dbf0879b3a0a1f9a82c` |
| `results/tables/openai_three_model_stress_v02_full120/family_effect_summary.csv` | 2378 | 13 | `701e29ab0f1f3a64bc856d6499128bf8df23c4410d5f9d1a07eb7a811421e57f` |
| `results/tables/openai_three_model_stress_v02_full120/first_turn_error_atlas.csv` | 47595 | 158 | `2a6d586fc095d7f796d347bf377b7b828465160e2ab09fa08a0d3fdde90809ff` |
| `results/tables/openai_three_model_stress_v02_full120/item_consistency_by_family.csv` | 637 | 5 | `c1f5d94794d492351c91d191f39ad0d57f9050e44a1215e052c8badb1ec2bf0a` |
| `results/tables/openai_three_model_stress_v02_full120/item_consistency_by_item.csv` | 12310 | 121 | `41d300e17f0603ff16797ffd15a3e661bf620ad105bd1917efd0b6297e7dea86` |
| `results/tables/openai_three_model_stress_v02_full120/item_consistency_hardest_items.csv` | 1362 | 13 | `21ef438afe9dc7dd7d52892a7ade3d037cd8187b3304e22b72a026ef5040187a` |
| `results/tables/openai_three_model_stress_v02_full120/item_consistency_summary.csv` | 430 | 2 | `cb27d6a8e2a53d26bb3c87c82e85e16f4461ea90d97479098573722ef21dbc79` |
| `results/tables/openai_three_model_stress_v02_full120/language_slice_aggregate_effects.csv` | 244 | 4 | `0d5186267d9a6f7b7efaf268cc99598be96779a3763314f9c725bb81eac423cf` |
| `results/tables/openai_three_model_stress_v02_full120/language_slice_metrics.csv` | 1040 | 19 | `ea9578c4f71633847b22ec421d72f2bd8defd102ec94dda084cb13ee811dbc57` |
| `results/tables/openai_three_model_stress_v02_full120/language_slice_paired_effects.csv` | 629 | 10 | `f5ad09fde8ff8113556f168620061901a43bb4424136c413bb8f9d832827e6c3` |
| `results/tables/openai_three_model_stress_v02_full120/metrics_by_family.csv` | 3494 | 25 | `9d389b90ea38099419d43eac341ff0ee4e7f721145e1ef48d29216ae017ff22d` |
| `results/tables/openai_three_model_stress_v02_full120/metrics_by_language.csv` | 2141 | 19 | `9b880c9371fe1693222cb0169e0037cbcf298692d64bd7b996646e271b0e137a` |
| `results/tables/openai_three_model_stress_v02_full120/metrics_summary.csv` | 1313 | 7 | `03ef52d7a580714e8344f23271e1e1c779d8f8b26a4d92e10a6c8b6496c5d3f6` |
| `results/tables/openai_three_model_stress_v02_full120/paired_contract_effects_by_family.csv` | 2119 | 13 | `984175756866cc28723238352ab68cb5f8431cea90b56d5af08ca695beefad18` |
| `results/tables/openai_three_model_stress_v02_full120/paired_contract_effects_by_model.csv` | 901 | 4 | `a748f1932568bac012026ffc492c8a85c854b137362b9194a39d1c0b61007116` |
| `results/tables/openai_three_model_stress_v02_full120/paired_significance_by_model.csv` | 1350 | 13 | `c37d197de92b0444efbecca49c0dd4624a314051933108ac3348294acffacb98` |
| `results/tables/openai_three_model_stress_v02_full120/repair_dynamics_by_family_condition.csv` | 998 | 9 | `d80b87557ed9a42aec7b3dc61448a60dd644bf726133869eebf0a0edff9c95d3` |
| `results/tables/openai_three_model_stress_v02_full120/repair_dynamics_by_language_condition.csv` | 749 | 7 | `10df908d348b3cf6815b3612468a698e175898d5d5f521a15c74e62f53b40df1` |
| `results/tables/openai_three_model_stress_v02_full120/repair_dynamics_by_model_condition.csv` | 772 | 7 | `4c04be7016ab4ecc1664060dfc584cc4abb08bccccba0e76539f253c83ada912` |
| `results/tables/openai_three_model_stress_v02_full120/repair_paired_effects_by_model.csv` | 317 | 4 | `050fafa7aab7f8420bf3f5b0195af8968acb2732770e9ac4569572ff697f9716` |
| `results/tables/openai_three_model_stress_v02_full120/repair_rtt_transition_by_model.csv` | 877 | 49 | `9989a685ea31657a7ec06449854e77f1b5a2b4fbe7daf8137b70edb8bdccd8fa` |
| `results/tables/openai_three_model_stress_v02_full120/scorer_ablation_by_condition.csv` | 749 | 3 | `5a886c63eb0df64c3e25bb09f508766343055cf2889e6c80d98692d356bc8bab` |
| `results/tables/openai_three_model_stress_v02_full120/scorer_ablation_by_family_condition.csv` | 1494 | 9 | `42c025736f56762537dda96d681ef00b94b7d287900f6fb29a1a4e2a48ebc05d` |
| `results/tables/openai_three_model_stress_v02_full120/scorer_ablation_by_model_condition.csv` | 1192 | 7 | `f4d62d22cd81c622d3d8acc34f954668ccda847fac3d772aaf897fb6e8151484` |
| `results/tables/openai_three_model_stress_v02_full120/scorer_ablation_failure_signatures.csv` | 772 | 14 | `52dd2709e9bd94972c87b22670d98d684708c6ab02ba9b963762e51f78b2c9bd` |
| `results/tables/openai_three_model_stress_v02_full120/scorer_ablation_top_failure_signatures.csv` | 626 | 11 | `0b42634e99616858d000ad1846086cebb6953e68758cb8a7e01ff1b18c12cd31` |
| `results/tables/openai_three_model_stress_v02_full120/task_useful_failure_by_condition.csv` | 522 | 3 | `575accb5499a33500d6727fd4870be00506b104f324936994bdca5d31be000c8` |
| `results/tables/openai_three_model_stress_v02_full120/task_useful_failure_by_family_condition.csv` | 1047 | 9 | `a5350e7c4df665d18f82f9cb16b5c17fb4fc9b3f2bdbedfd3fea8cb7f02bfdbb` |
| `results/tables/openai_three_model_stress_v02_full120/task_useful_failure_by_language_condition.csv` | 806 | 7 | `bfdbb21c44b755e89b0fd917174700c0e07dabbf910a788185aabd162b03b4ae` |
| `results/tables/openai_three_model_stress_v02_full120/task_useful_failure_by_model_condition.csv` | 830 | 7 | `bc857c8dcd97100b3828b2627c113962af11045c3c5591cd7d9a64df49cd1a6c` |
| `results/tables/openai_three_model_stress_v02_full120/task_useful_failure_signatures.csv` | 328 | 6 | `f7f7ed3ce6c4ab86b742f779ea6acede2ba3b693c9ddca61c04131701accab60` |
| `results/tables/openai_three_model_stress_v02_full120/token_burden_by_family.csv` | 3217 | 25 | `40b9172af6b3be65305f9f6651057d118bedcc944662c9f5c1f6232ec8f3119b` |
| `results/tables/openai_three_model_stress_v02_full120/token_burden_by_language.csv` | 1876 | 19 | `b5385bfa7aa48544f2ff76f824ad10e2aea5585b58290ce824c64c267a1fa80b` |
| `results/tables/openai_three_model_stress_v02_full120/token_burden_by_model.csv` | 967 | 7 | `65c5d84400f5a299fe9df6e6ac92ff25a67808a629b33879c73b05587bc748a3` |
| `results/tables/openai_three_model_stress_v02_full120/token_burden_paired_effects_by_model.csv` | 480 | 4 | `434d7414df5289f105b7f3544a7ed8d65961e528818fb09ab53f8205d3959ffc` |
| `results/tables/openai_three_model_stress_v02_full120/token_burden_trajectory_metrics.csv` | 65574 | 721 | `e35f50d5a66b2ffcd9cd04eb8bc787999158b9381a74eec77d8bb6c136fe7b95` |
| `results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv` | 68501 | 721 | `6413a5b3c2640817fb3d0b236004e8a9fa3aabd5afad7afef8a05162b6fad415` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_agreement_by_family.csv` | 504 | 5 | `48a7a6cc7d980bb61c179c6dccb4292df8d0649b7df1cf0134fb0c752cf9e854` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_agreement_by_model_condition.csv` | 633 | 7 | `8a666545beb9a8bf4eebae3cb8da905d827d01e2b204e515908bb294930234c4` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_agreement_summary.csv` | 266 | 2 | `0114fffe8bd558e7b9f17b0929f25efaff9b4b4d399b9850c5ee343d9a4945e3` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_audit_by_family.csv` | 367 | 5 | `e24bf5982a86c0256d61652b08f667a683849ecf42104b1f8a240bf83a3ad608` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_audit_by_model_condition.csv` | 472 | 7 | `890bc75a8018bf5be7b95a32d93b892d7ee24f0b9201a77e0ecba6f4b5a4db7f` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_audit_disagreements.csv` | 338 | 2 | `b3f74a171f4e12feaec92d91f0ac5d14515d2b7fd00bed4f8b1da6d4ac08501b` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_audit_summary.csv` | 149 | 2 | `9119fbb6c3b2cdcf9354a79098b9adae38c563ca5f6abd2837752e1456533bfe` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_component_agreement.csv` | 370 | 6 | `8bff4f098ad7508e556351075290cc814d4c36998867debe8d5839a393599d9d` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_component_disagreements.csv` | 3560 | 11 | `74c666b25bef33794a2bdfb2e8c2dcac6a75d306917389051f99928c8218254c` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_pass_fail_disagreements.csv` | 338 | 2 | `b3f74a171f4e12feaec92d91f0ac5d14515d2b7fd00bed4f8b1da6d4ac08501b` |
| `results/tables/openai_three_model_stress_v02_full120_judge_refresh_gpt55/judge_refresh_by_family.csv` | 934 | 9 | `ba97cd25e0f0ef7faa6fcc6f6470e32e1e4adcb2fe09aeee77be57ba5ad3efcd` |
| `results/tables/openai_three_model_stress_v02_full120_judge_refresh_gpt55/judge_refresh_component_agreement.csv` | 661 | 11 | `81a9193c40f22dd2ac4e1caf5cf5afaad59a58221982046743fddd7e6c95f167` |
| `results/tables/openai_three_model_stress_v02_full120_judge_refresh_gpt55/judge_refresh_disagreements.csv` | 1408 | 4 | `620832949009bab08a9addd75a733457807bf45239caab85856c508a95dfe6a4` |
| `results/tables/openai_three_model_stress_v02_full120_judge_refresh_gpt55/judge_refresh_pairwise_comparison.csv` | 245 | 2 | `607989e5e544581d097f3ca4ec2e7ba906b41b901e9acd36563ae3f5b2ae2690` |
| `results/tables/openai_three_model_stress_v02_full120_judge_refresh_gpt55/judge_refresh_summary.csv` | 367 | 3 | `dcf07011035f49df2b69825ac4ff704c10b202b30a5de85adaa86fd4ab47e9f3` |
| `results/tables/openai_three_model_stress_v02_new24/metrics_summary.csv` | 1055 | 7 | `472f910ad09bb5e31fe88bc51ac0da91472d4f5c830e10a9dcb5edac930870eb` |
| `results/tables/openai_three_model_stress_v02_repair_realism_editing_baseline24/repair_realism_by_model.csv` | 744 | 13 | `f8b2517199b05920701701fbbfb561fa0805118d45628aed604e98d76e3fd29d` |
| `results/tables/openai_three_model_stress_v02_repair_realism_editing_baseline24/repair_realism_disagreements.csv` | 9417 | 27 | `2cb471a6f0dd449f0af56b55377fdf0a71ce2a7d8f947a9cb98da1d917357410` |
| `results/tables/openai_three_model_stress_v02_repair_realism_editing_baseline24/repair_realism_paired_effects.csv` | 366 | 4 | `61b1540071a9ab9a296b01a790d6d01b02a3ccfcb7aeb14d0297cc16a0798797` |
| `results/tables/openai_three_model_stress_v02_repair_realism_editing_baseline24/repair_realism_summary.csv` | 577 | 5 | `f45d67d13be6161214380faa9f846361b0597065804e8cca6640e79a7f240f34` |
| `scripts/analyze_benchmark_quality.py` | 12546 | 287 | `caf4fb572eb57d7a96fede7b03750c35eb1d8802ef7d20bdfc763924ec6d2524` |
| `scripts/analyze_completed_label_claim_gates.py` | 11724 | 275 | `eae8fdc3f6365589165d8ffa0eb048db60a33390a127842d79439d1684ba756e` |
| `scripts/analyze_component_breakdown.py` | 10918 | 263 | `fd8d5cd9a66ec153873202cfaa56c15dc656d8a6b3475f732ed147701dd153b0` |
| `scripts/analyze_coverage_expansion_v03.py` | 10917 | 269 | `35c1836f361f5b27198f8eaccf47b68e1d98a85c9f5a90c928c4d19c438b8470` |
| `scripts/analyze_coverage_native_review_adjudication.py` | 15779 | 357 | `ad9ddd95f0477d7d53d4907151a6f2df5fdfc239226e452d7b99d975c49f5b44` |
| `scripts/analyze_coverage_native_review_design_v03.py` | 7283 | 181 | `e974f9abd206f87a2ac06b53e873720cbbcb467a284ce7bd1d35602be093fcc2` |
| `scripts/analyze_coverage_pilot_v03.py` | 11020 | 267 | `ac56de665d6eb9ce97f6436920bcdcf31c913a8e9433b69087d8181c02eda714` |
| `scripts/analyze_coverage_smoke_v03.py` | 10497 | 247 | `e93faa31980ce1db5be99e00db6b4cff97abc18199de0232f0f2d45576dba612` |
| `scripts/analyze_current_model_case_studies.py` | 11320 | 314 | `576b04434c28e93e878d34af90d5f652a678c66a2bf38483c4c3e2642f3d0bde` |
| `scripts/analyze_current_model_error_analysis.py` | 16045 | 365 | `e50ad7d1eba9c9b7d76ea11896eebe7a16914776cdfc15aaf58f6ef09eb337e4` |
| `scripts/analyze_current_model_heterogeneity.py` | 12146 | 270 | `13344720677c0dc7ef80c14be19daa42c126a805e9424bbe41d9fa68130a4a7e` |
| `scripts/analyze_current_model_refresh.py` | 10081 | 209 | `7a22d81af651061bf6bcbd373daa91abd200c585fa6e6e1ffe71d41a267f2679` |
| `scripts/analyze_current_model_regression_risk.py` | 13806 | 316 | `d3d46de786d9d1411b5702a693d86713eecb84bc2fd6a46a15dff23b4d221f51` |
| `scripts/analyze_current_model_scorer_sensitivity.py` | 13897 | 339 | `73703e5518d3ba98f9ab5c9c886c16f5c60dd8fba323484bb1bfccd0caf78f30` |
| `scripts/analyze_current_model_uncertainty.py` | 9251 | 197 | `368ae13a292840390103c14a7ea997df44645031bb443d1582d57ecf5a0be56c` |
| `scripts/analyze_current_prompt_mechanism.py` | 16776 | 432 | `7f42e4c4539c2c376e9a7635e97907d7d9a57c2b77b554f9b4429b7302424e27` |
| `scripts/analyze_discovery_cues.py` | 9520 | 218 | `3fa4247132e3293235c19f9b2b13b74ab707c073c1458e8703cf95a3719bb990` |
| `scripts/analyze_efficiency_tradeoff.py` | 11762 | 250 | `a290b330d298278fcd2f367274f0abf6abbb15be173c8e28609abc39c0220165` |
| `scripts/analyze_failure_modes.py` | 11786 | 312 | `eaf844b2f22730244de1b6ccfed32d1f2972686f8fa7284e6217799d78412911` |
| `scripts/analyze_followup_plan_readiness.py` | 19919 | 449 | `2c3272e32ce174c85f197cdfdee1278cab2a100b5a17700ec550b84f58fb62ea` |
| `scripts/analyze_generation_progress_probe.py` | 15165 | 311 | `aa1a2bd5f1b4fd3c88f956a5b3c650b5389f34218d3dee7f22ceb92a5c3af2d0` |
| `scripts/analyze_human_audit_acceptance_rules.py` | 9754 | 243 | `59514011f2e2875af1fe448c8a017db101280bfb76c7ae38a7bf68059a91145b` |
| `scripts/analyze_human_audit_adjudication.py` | 14977 | 351 | `f08a2129425022659c0fae65fca5dbeabc0ac7a35ab61fd2a1e2ef807d8f8c9f` |
| `scripts/analyze_human_audit_design.py` | 12131 | 304 | `288283b01225c9defa4f9b2cdc723b4ee3e9b1a1a4e87d46e9389f4ec011191e` |
| `scripts/analyze_item_consistency.py` | 13208 | 292 | `9948d8afa5e2a8d3307e5ab1f09e74ac5f1b0079515508f5c3fa47c9f2c3fd01` |
| `scripts/analyze_judge_agreement.py` | 15295 | 348 | `d3d7d4aa3003bc7a5d4050a326ee5ad4713af734517ccce4f8f37acde18a6674` |
| `scripts/analyze_judge_refresh.py` | 16180 | 351 | `970d8855da46d3d3f656dd3b27dca593e9f588d0782ddb7552800304f049c532` |
| `scripts/analyze_label_collection_launch_pack.py` | 19191 | 324 | `4b2099d67aecbb65092ba565e599863e9c80dda907e5f2664141121ee3a66136` |
| `scripts/analyze_language_slices.py` | 11656 | 262 | `cc1449c42578c389809574c14ba0c2db8ee8ff4b974de4d270b24971f838408c` |
| `scripts/analyze_prompt_ablation.py` | 20681 | 515 | `1e277f0aa80ce8cd21ca9f3339248925fb95e4517f8e99c085330b172888e8dd` |
| `scripts/analyze_prompt_control.py` | 9823 | 248 | `6e901ad027174411c5efe9d8c2e193457992650b653d5b0567fe7d68e24368ba` |
| `scripts/analyze_repair_dynamics.py` | 11361 | 247 | `f83ce31b4f9405a359a3aa5094a1f84961d42a468a3343b200a7cc0174ab3310` |
| `scripts/analyze_repair_realism.py` | 14419 | 341 | `1dcaa53df56572b4728ba35fedf3c9d4a1bdc5f26fdc36e615f08dedcfa3ef66` |
| `scripts/analyze_scorer_ablation.py` | 12302 | 314 | `72a401b925a05507b625bbdcce224216c08af642a2aa012841c8d9858697d95f` |
| `scripts/analyze_task_useful_failures.py` | 15520 | 391 | `f1da1a1ba93a43955aaeb825c71ba197de9e96df447d5074f6d4568dd6798aaf` |
| `scripts/analyze_token_burden.py` | 9310 | 216 | `6145c4f6f50568570f1d657f876d7675ed30446548764b344493e1fb88ee6883` |
| `scripts/build_coverage_pilot_v03_outputs.py` | 3455 | 77 | `7b693e5e44338902fb52d0a9c5ef1928420e267b4b2ac13f1ae99f31360cab1d` |
| `scripts/build_error_atlas.py` | 7032 | 199 | `4387b5b671149721a399893104bad72e1c8e256275b573224c5b4441da540d10` |
| `scripts/build_full_v02_prompt_control_scores.py` | 3334 | 86 | `6f0a1f66e2f2c78f1492109338e533a8147d65ae80285025d63cf90607cf3c69` |
| `scripts/build_full_v02_scores.py` | 3507 | 89 | `d8f36dbfe48e68288cbf5c8486ac3c3f3920a5c2aab89225e449ef5d79ce45c5` |
| `scripts/build_label_collection_bundles.py` | 10652 | 282 | `ae3fa5d79493b076fe6dc0cb92f5c5250d9dca002131f467b59dc477ea827559` |
| `scripts/compute_metrics.py` | 7510 | 195 | `b1cff3dfe48d16dccc7c5874f6d3cbfa03f209e55af8bc51631010969b3988fc` |
| `scripts/discover_repair_cues.py` | 8177 | 243 | `0f5069812b0e8ca60defb1f4b1a8de3920a84acd089bf1dc3fdcfa3068b2208b` |
| `scripts/finalize_coverage_native_review_adjudication.py` | 8170 | 188 | `2741cacca5f01d122a1ddb354fffbc212bfd083ce579399a2537d89e4b16993d` |
| `scripts/finalize_human_audit_adjudication.py` | 8437 | 187 | `1d4414b210e281faa4ef2a27fba82950a6a8ea56e62a5f5058fdd6ce8bff31d6` |
| `scripts/generate_benchmark.py` | 20043 | 470 | `68a3e454555497be971db9046adbca2ff5bcb2009eff1aa6a9c297e78ff8f31d` |
| `scripts/generate_coverage_expansion_v03.py` | 15699 | 271 | `c1ae68ac501edbb5627a90b89017b7849e6873fea98b84cd99c391290554b08f` |
| `scripts/generate_stress_benchmark.py` | 11980 | 267 | `89677da4df607023f352a6a314e33850d7162f480b0a5f2abcbf4d3095d0fc41` |
| `scripts/generate_stress_benchmark_v02.py` | 10953 | 262 | `ee407c0bbc5567895b155a59e5dce7722a2e320703a64995ff5fdf51238b4ff1` |
| `scripts/judge_outputs.py` | 10150 | 274 | `bc090a1735c5ce24f9941949b042956c03c5f287255ff1f7f83d099854e4dffb` |
| `scripts/lint_claim_boundaries.py` | 4838 | 141 | `b6f16925077cbcb9d5661f78be76bf90164de1c4db6500f8c218df2ea6a8fe0d` |
| `scripts/make_artifact_manifest.py` | 67082 | 781 | `cd84677ff8a3914ee4f84610cc50423a4530bc929e6d23a00a6c8d7f0820f32a` |
| `scripts/make_coverage_native_review_packet_v03.py` | 16653 | 365 | `fd0d380e50e12da17a71d3989393c6ad485b5e68ef530b95960fe242bbf45d2e` |
| `scripts/make_coverage_native_review_sheets_v03.py` | 13720 | 307 | `9158944b71d8e932ccdc4c95e6308a967a686dac22bf84a5ad6bbc1f3a5fdc94` |
| `scripts/make_figures.py` | 6172 | 180 | `16bdd9f91481beb5eb2b28719e1cde1af0399d64782856e782feb83d302e5191` |
| `scripts/make_human_audit_packet.py` | 20934 | 523 | `4bcc1cb4959529f1b70d6ced56a4447a597689a5de4c1a616be58cd9d3deaf09` |
| `scripts/make_human_audit_review_sheets.py` | 13560 | 330 | `02dabeb53112713c5e9bdca29c88b2e1c6e2d0ca0bb83d4640b6486660757959` |
| `scripts/merge_review_exports.py` | 11200 | 292 | `495efda4cdc20a72b809b64eaf61dad16b3fb0cb52d086d93b6035aaedf0bfc6` |
| `scripts/paired_effects.py` | 4814 | 121 | `e0172ab16761ce235a795cf14d106164b79da7854c935be89d2a68d4caafc5fd` |
| `scripts/paired_significance.py` | 5385 | 147 | `1e1a6a3105a73e40c2363d3924d0e38d0442818065353aa63846015aa2dedd34` |
| `scripts/run_models.py` | 12175 | 330 | `46205fe276e0f5d967b42f791cdc952a6b519b6b20350bc78d2636423d327124` |
| `scripts/run_repair_prompt_variants.py` | 9442 | 235 | `ee83343c399b68c03721488ed7f170e5dd33dc3ad89d861b4969f03cf58b781e` |
| `scripts/run_submission_checks.py` | 31100 | 751 | `cb7c5ac72698d27abc9996f984dac9facb08409b993b51b48a8ff0408ae135bd` |
| `scripts/score_auto.py` | 8236 | 302 | `401194f2530033217cc33e7617539a46bee792b93a4af525512f43f055c82b5e` |
| `scripts/summarize_coverage_native_review_v03.py` | 6214 | 155 | `5b5a1bafa0d89a3bdc782362adf98fa736a570e9a5e282593e79b831d090f4df` |
| `scripts/summarize_experiment_ledger.py` | 18150 | 438 | `b8c110d4c92c3bc489febb115f39a76e491f6f2b11de859c490c584ff8671c31` |
| `scripts/summarize_human_audit.py` | 7476 | 190 | `6e3d0e88f55058e6b4e81279d92f1714a177f16746976ee27ae7ca8e8500d852` |
| `scripts/summarize_judge_audit.py` | 4016 | 108 | `800e085640b0fcbfa23e300233f03e06dd7c727d5d569fcddb70cb91b18422ec` |
| `scripts/test_completed_label_claim_gates.py` | 3685 | 84 | `630208ffae799d6df046ba782a2db4f8800ac13a093c52bc7b0f136c481bf24d` |
| `scripts/test_coverage_native_review_adjudication.py` | 6954 | 161 | `1767f41ce0e46b5873031ddbb077f4557ddbb1c3b9b0c16d0193c87a548e1e01` |
| `scripts/test_coverage_native_review_completion.py` | 6216 | 138 | `921c7b7be1e8afe8fc827d8d0eff41826b5d8a8ff415c9b335a4107c6f35f5e6` |
| `scripts/test_human_audit_adjudication.py` | 6720 | 162 | `7541f33f12f6087a173a8eef8b84e4209008ebf994ba31d9f6b3cd09d4fb0212` |
| `scripts/test_human_audit_completion.py` | 9480 | 256 | `90c4ab7276e4706c71942be0ecac55d63877891e3e9979762c3cc66dbda3562e` |
| `scripts/test_merge_review_exports.py` | 8553 | 234 | `7a1d06c1575195241e7f19cc45d18b5dd7552409c9b1f54840856b2b80a08d7d` |
| `scripts/test_score_auto.py` | 7840 | 192 | `874c13feab86027263ff2d586da644928deb78cf8f7b98d918a6d2823ade8f2d` |
| `scripts/validate_completed_coverage_native_review_v03.py` | 9869 | 235 | `efe206953e9405459648662ee522963a7aaebdbd4ca1075a910f8fb6c41ca69d` |
| `scripts/validate_completed_human_audit.py` | 11945 | 280 | `9a1adbdd534cef4ac4b50e82c88945db4ad4e87b3d622b9d95262bd052608045` |
| `scripts/validate_completed_label_claim_gates.py` | 2780 | 71 | `df69271fc94a7e1f799571506be9a2d5c6d57c3cb3f375bcea2585f926753fae` |
| `scripts/validate_coverage_expansion_v03.py` | 8552 | 187 | `d39214172d7d186741e01125e62ab18eb15cbab59cc112bb0a21fe4b6443f703` |
| `scripts/validate_coverage_native_review_packet_v03.py` | 8103 | 196 | `68cb715dde64309de85128dbf0cb415a041eedbbac1658f84e61d4c14be612a7` |
| `scripts/validate_coverage_native_review_sheets_v03.py` | 5027 | 121 | `1f7d3a025cfd231c976a96880430db01270dc80d915bbaeff58a775fd0e6b6bc` |
| `scripts/validate_coverage_pilot_v03.py` | 7824 | 167 | `80e1cb810b4c875042a4dcaaed07eb69ea0ce809f1ff83345b54cb6c82067f74` |
| `scripts/validate_coverage_smoke_v03.py` | 9431 | 178 | `c2d6a32b7131adb3563daafea7b66935a8cd179ee730fe8c71dc3327c4be9135` |
| `scripts/validate_current_model_case_studies.py` | 4697 | 140 | `0cb7d18625a3299d221e8945748279ad1dea3042475c380fa0470c150daed255` |
| `scripts/validate_current_model_error_analysis.py` | 4869 | 123 | `690a901e92f2af6169553897abce2d46f9ec73467d5cf6246314be6ee7743644` |
| `scripts/validate_current_model_heterogeneity.py` | 5620 | 108 | `8425c1b74ad185a1056d74a6e74fb2345b4831812d95904c4ca151ca48a9ebfd` |
| `scripts/validate_current_model_human_audit_packet.py` | 8971 | 224 | `0c1b17b057eb756321cf88d951207f13211b57e1d963d533e518bdaf517fe556` |
| `scripts/validate_current_model_refresh.py` | 5517 | 142 | `e4503fe9549f0eeb36c0abc1ac35b334626bd86ef160855d1dcb04389615c669` |
| `scripts/validate_current_model_regression_risk.py` | 6450 | 153 | `56d226ea48104104d7019f917baebfa4cf12bd4c2937a680105afbc6e2e75069` |
| `scripts/validate_current_model_scorer_sensitivity.py` | 6783 | 161 | `9160faf9ea64c8ac2174dca90c0047bbb6bd4a50428faeefb475c65692084c18` |
| `scripts/validate_current_model_uncertainty.py` | 4799 | 134 | `53366890c3dc08e3317c2a467cdb8c7872309148ffb9a83eba9bbb0eebb3cbe9` |
| `scripts/validate_current_prompt_mechanism.py` | 11556 | 294 | `e2c7fa112418a77b2ac1ffe28591114eb1bc844d5d47ee88aa94bb59e393328b` |
| `scripts/validate_efficiency_tradeoff.py` | 5061 | 128 | `fe841e1c80e876d8dd1073208b7dceaa055de1a99af3643821673b25daa95d9d` |
| `scripts/validate_followup_plan_readiness.py` | 4548 | 111 | `09bfaa141fc737a5716c3acf3e38ef24cc4668072ef7e7238d2bb57d5c2fb773` |
| `scripts/validate_followup_probe.py` | 6033 | 138 | `641f94e0233e92e807056dcd306aaceab7d84e514d5b8cabe259c57514d404b3` |
| `scripts/validate_generation_progress_probe.py` | 4823 | 124 | `ea6319496030b90f85b36fe96d8bd29d089b21ed91a52b5cf6ee991e9e4390cb` |
| `scripts/validate_human_audit_acceptance_rules.py` | 4203 | 109 | `71515e141ea5f387981daae98e3afe2e4c0718f79a5355998c501c39d3fb4bfa` |
| `scripts/validate_human_audit_packet.py` | 9646 | 217 | `9ae7ac15d7915e00e1a8cafce0eec1b380a204ac87c527760a08154290dd2d9e` |
| `scripts/validate_human_audit_review_sheets.py` | 5196 | 133 | `bdb55cae4576ec70fdc94844486e01591f8c72f9ecd28ef4882225746ca2e49c` |
| `scripts/validate_judge_refresh.py` | 6241 | 173 | `04718b3339405c80b138ec9daa7a137991b543618b08da1a9829b160da9e5942` |
| `scripts/validate_label_collection_bundles.py` | 3922 | 112 | `4a6d3a09919404aff8f78191683266b21b2b82e32e48ceda37f5a8b2f6215d43` |
| `scripts/validate_label_collection_launch_pack.py` | 5365 | 116 | `a488b744eb896cfe6d449002851d286202b98a53754649dd84f443a30b235ced` |
| `scripts/validate_paper_claims.py` | 137197 | 2605 | `b7b02b1c607d44f7115e4cb895b1b93f2719dc973e1a01fc6e27bb5253d3dd16` |
| `scripts/validate_qualitative_examples.py` | 6982 | 202 | `b483926397b7df75c18a626d0af28332e7c5c22e34ae9b8dc1f61ff28be78d62` |
| `scripts/validate_release_docs.py` | 4041 | 112 | `c8e0d2f10acfc9d70b8948135f3fe0e8b44a0879cecb7ac1a51ef4a5bbd14690` |
| `scripts/validate_repair_realism.py` | 5832 | 165 | `0ccdaffe830d77407b097e16b53608a81b0d98bac5aa050b265744c31d75e0f5` |
| `scripts/validate_result_card.py` | 5223 | 112 | `391be4ea5a1ccb703772ff41216e3548b75add185837a33ffd9cd0ccd652115d` |
| `scripts/validate_stress_benchmark.py` | 3087 | 88 | `d5edb4e9d83a9f40c9b57d175abe689a9f2b419a19ebbb430344def190cfa2f7` |
