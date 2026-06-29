# Reviewer Concern Audit

This no-API audit maps likely reviewer concerns to current evidence,
claim boundaries, and validators. It is not a new experiment and does
not replace completed human/native validation.

## Summary

- Reviewer concerns audited: 10
- Covered concerns: 2
- Covered with explicit boundary: 6
- Diagnostic-only concerns: 1
- External label blockers: 1
- OpenAI API calls: 0
- Claim boundary: native/near-native validation is launch-ready but not completed.

## Concern Matrix

| Concern | Readiness | Paper claim use | Key answer | Next action |
|---|---|---|---|---|
| `current_model_timeliness` | covered | Use the full gpt-5.5 run as the current-model headline and keep gpt-5.4-mini bounded. | Full 120-item gpt-5.5 evidence shows 81.7% to 98.3% FTGA, 20 paired fixes, zero first-turn regressions, and zero unresolved trajectories under the contract. | No additional API run is needed for this claim boundary. |
| `lower_cost_model_boundary` | covered_with_boundary | Report lower normalized token tax plus directional FTGA; do not claim universal repair improvement. | gpt-5.4-mini improves from 80.0% to 85.0% FTGA, but the interval crosses zero, unresolved rate rises, and five first-turn regressions remain. | Keep the gpt-5.4-mini language as a bounded lower-cost diagnostic. |
| `synthetic_scope` | covered_with_boundary | Use as a stress pilot and progress probe, not a prevalence or population claim. | The benchmark card, limitations, and claim linter enforce synthetic-pilot, non-representative wording. | Do not describe the result as representative or prevalence-estimating. |
| `scorer_validity` | covered_with_boundary | Use deterministic scorer audits and LLM-judge audits as scorer sanity checks, not as native validation. | Known-bad probes fail 390/390, constrained positive controls pass 120/120, and paired judge audits agree on 71/72 and 70/72 sampled labels. | Collect qualified human/native labels before widening validity claims. |
| `human_native_validation` | external_label_blocker | Do not claim completed human/native validation. | Reviewer packets, launch checklists, adjudication workflows, and claim gates are ready, but completed qualified labels are absent. | Collect current-model labels first, then original v0.2 labels, then v0.3 coverage review if reviewer capacity allows. |
| `mechanism_vs_prompt_engineering` | covered_with_boundary | Frame preservation scaffolding as mechanism evidence, not prompt dominance. | Content-preservation prompts are close to or above the full contract, and contract fixes are concentrated in editing preservation. | Keep the full contract as the pre-specified intervention and avoid best-prompt claims. |
| `coverage_expansion_v03` | diagnostic_only | Use v0.3 as launch-ready coverage scaffold and smoke evidence, not headline benchmark evidence. | The v0.3 scaffold adds 60 rows across six coverage slices and has review sheets plus smoke/pilot diagnostics, but native review is incomplete. | Complete native review before treating v0.3 as benchmark evidence. |
| `statistical_robustness` | covered | Use all-five-model paired tests, clustered uncertainty, and balanced-pilot robustness as support. | Across 600 paired model-item rows the contract has 67 fixes vs. 6 regressions; clustered bootstrap gives +5.8 to +15.0 pp. | Keep headline claims anchored to full 120-item runs. |
| `token_cost_interpretation` | covered_with_boundary | Report token tax as normalized repair burden, not dollar cost. | The contract lowers normalized token tax for all five full-run models but increases absolute total tokens for every contract row. | Keep cost language focused on repair burden and absolute-token caveats. |
| `real_world_motivation_privacy` | covered_with_boundary | Use WildChat only as aggregate taxonomy motivation. | The scan writes hashed metadata only, reports no raw text, and the taxonomy audit maps all six cue categories to benchmark/scorer/metric surfaces. | Do not report WildChat cue hits as prevalence estimates. |

## Evidence Index

| Concern | Evidence | Validators |
|---|---|---|
| `current_model_timeliness` | `paper/current_model_refresh_v02.md`<br>`paper/current_model_uncertainty_v02.md`<br>`paper/current_model_error_analysis_v02.md`<br>`paper/current_model_regression_risk_v02.md` | `scripts/validate_current_model_refresh.py`<br>`scripts/validate_current_model_uncertainty.py`<br>`scripts/validate_current_model_error_analysis.py`<br>`scripts/validate_current_model_regression_risk.py` |
| `lower_cost_model_boundary` | `paper/current_model_uncertainty_v02.md`<br>`paper/current_model_regression_risk_v02.md`<br>`paper/current_model_error_analysis_v02.md` | `scripts/validate_current_model_uncertainty.py`<br>`scripts/validate_current_model_regression_risk.py`<br>`scripts/validate_current_model_error_analysis.py` |
| `synthetic_scope` | `docs/benchmark_card.md`<br>`paper/sections/08_limitations_and_ethics.tex`<br>`paper/claim_evidence_checklist.md` | `scripts/lint_claim_boundaries.py`<br>`scripts/validate_release_docs.py`<br>`scripts/validate_paper_claims.py` |
| `scorer_validity` | `paper/scorer_challenge_v02.md`<br>`paper/scorer_positive_control_v02.md`<br>`paper/judge_agreement_analysis_v02_full120.md`<br>`paper/judge_refresh_gpt55_v02_full120.md` | `scripts/validate_scorer_challenge_v02.py`<br>`scripts/validate_scorer_positive_control_v02.py`<br>`scripts/validate_judge_refresh.py`<br>`scripts/test_score_auto.py` |
| `human_native_validation` | `paper/label_collection_launch_pack_v02.md`<br>`paper/label_collection_dispatch_v02.md`<br>`paper/completed_label_claim_gates_v02.md`<br>`data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv` | `scripts/validate_label_collection_launch_pack.py`<br>`scripts/validate_label_collection_dispatch.py`<br>`scripts/validate_completed_label_claim_gates.py`<br>`scripts/validate_completed_human_audit.py` |
| `mechanism_vs_prompt_engineering` | `paper/prompt_family_scorecard_v02.md`<br>`paper/current_prompt_mechanism_gpt54mini_v02.md`<br>`paper/current_prompt_mechanism_gpt55_v02.md`<br>`paper/contract_benefit_decomposition_v02.md` | `scripts/validate_prompt_family_scorecard.py`<br>`scripts/validate_current_prompt_mechanism.py`<br>`scripts/validate_contract_benefit_decomposition.py` |
| `coverage_expansion_v03` | `paper/coverage_expansion_v03.md`<br>`paper/coverage_native_review_design_v03.md`<br>`paper/coverage_pilot_gpt54mini_v03.md`<br>`paper/coverage_smoke_gpt55_v03.md` | `scripts/validate_coverage_expansion_v03.py`<br>`scripts/validate_coverage_native_review_packet_v03.py`<br>`scripts/validate_coverage_pilot_v03.py`<br>`scripts/validate_coverage_smoke_v03.py` |
| `statistical_robustness` | `paper/all_model_paired_significance_v02.md`<br>`paper/all_model_uncertainty_v02.md`<br>`paper/balanced_subsample_robustness_v02.md`<br>`paper/sentinel_suite_v02.md` | `scripts/validate_all_model_paired_significance.py`<br>`scripts/validate_all_model_uncertainty.py`<br>`scripts/validate_balanced_subsample_robustness.py`<br>`scripts/validate_sentinel_suite_v02.py` |
| `token_cost_interpretation` | `paper/token_burden_analysis_v02_full120.md`<br>`paper/efficiency_tradeoff_v02.md`<br>`docs/evaluation_card.md` | `scripts/validate_efficiency_tradeoff.py`<br>`scripts/validate_release_docs.py`<br>`scripts/validate_paper_claims.py` |
| `real_world_motivation_privacy` | `paper/discovery_cue_analysis.md`<br>`paper/taxonomy_traceability_v02.md`<br>`results/discovery/wildchat_20k_repair_cues/summary.json` | `scripts/validate_taxonomy_traceability_v02.py`<br>`scripts/validate_paper_claims.py` |

## Interpretation

The current package is strongest on current-model timeliness, scorer
plumbing, mechanism diagnostics, robustness checks, and release hygiene.
The main unresolved reviewer concern is external: completed qualified
human/native labels are still missing. Until those labels pass the
completed-label gates, the paper should keep native-validation claims
as launch-ready protocol evidence only.
