#!/usr/bin/env python
"""Validate docs/result_card.md against current paper-facing artifacts."""

from __future__ import annotations

from pathlib import Path


RESULT_CARD = Path("docs/result_card.md")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    require(RESULT_CARD.exists(), f"missing {RESULT_CARD}")
    text = RESULT_CARD.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required_phrases = [
        "Current-Model Refresh",
        "| gpt-5.4-mini | baseline | 80.0% | 0.25 | 1.38x | 2.5% | 87.5% | 87.5% |",
        "| gpt-5.4-mini | contract | 85.0% | 0.25 | 1.24x | 5.0% | 66.7% | 66.7% |",
        "| gpt-5.5 | baseline | 81.7% | 0.23 | 1.28x | 1.7% | 86.4% | 90.9% |",
        "| gpt-5.5 | contract | 98.3% | 0.02 | 1.02x | 0.0% | 100.0% | 100.0% |",
        "1,504 API response rows",
        "1,288 model-response rows",
        "72 repair-variant rows",
        "144 judge-audit rows",
        "285,930 saved provider-reported tokens",
        "85.8% vs 85.0% FTGA on `gpt-5.4-mini`",
        "99.2% vs 98.3% on `gpt-5.5`",
        "paper/current_model_error_analysis_v02.md",
        "paper/current_model_case_studies_v02.md",
        "paper/current_model_uncertainty_v02.md",
        "`gpt-5.5` FTGA improves by +16.7 pp with a [10.0, 24.2] pp item-bootstrap interval",
        "20 improved versus 0 worsened paired items",
        "`gpt-5.4-mini` FTGA improves by +5.0 pp, but its [-0.8, 11.7] pp interval crosses zero",
        "token-tax interval stays positive at [0.010, 0.269]x",
        "paper/current_model_heterogeneity_v02.md",
        "`gpt-5.5` effect is positive for all three language pairs",
        "+25.0 pp on Arabic-English",
        "+20.0 pp on Spanish-English",
        "+5.0 pp on Hindi-English",
        "removing editing leaves only +2.2 pp",
        "removing Arabic-English leaves -1.3 pp",
        "removing editing leaves -4.5 pp",
        "contract fixes 20 baseline first-turn failures",
        "introduces zero first-turn regressions",
        "contract fixes 11 baseline failures but introduces five first-turn regressions",
        "`gpt-5.5` baseline wrapper tax fixed by the contract",
        "a `gpt-5.5` contract residual that repairs in one turn",
        "two unresolved `gpt-5.4-mini` contract cases",
        "paper/current_model_scorer_sensitivity_v02.md",
        "not driven by a single fragile scorer rule",
        "`gpt-5.5` contract moves from 98.3% to 100.0% FTGA",
        "`gpt-5.4-mini` contract moves from 85.0% to 89.2%",
        "Taxonomy traceability",
        "paper/taxonomy_traceability_v02.md",
        "all six aggregate WildChat cue categories",
        "Five categories map to deterministic scorer components",
        "not real-world prevalence evidence",
        "Scorer challenge audit",
        "paper/scorer_challenge_v02.md",
        "390 known-bad probes",
        "forbidden-marker",
        "fails 390/390 probes",
        "detects 390/390 expected deterministic failure signals",
        "native/human validation boundary",
        "Scorer positive-control audit",
        "paper/scorer_positive_control_v02.md",
        "120 constrained pass templates",
        "accepts 120/120 templates",
        "passes 120/120 component checks",
        "over-rejection by deterministic rules",
        "paper/current_model_regression_risk_v02.md",
        "`gpt-5.5` has 20 fixes and 0 first-turn regressions",
        "`gpt-5.4-mini` has 11 fixes, 5 first-turn regressions, and 4 resolved-to-unresolved shifts",
        "content-preservation avoids 3 of the 5 `gpt-5.4-mini` regression cases",
        "paper/generation_progress_probe_v02.md",
        "96/360 GPT-4.1-family baseline model-item failures",
        "46/240 current-family baseline failures",
        "`gpt-5.5` passes 38 of the 40 items",
        "All-model robustness and balanced pilot design",
        "paper/all_model_paired_significance_v02.md",
        "paper/all_model_uncertainty_v02.md",
        "paper/balanced_subsample_robustness_v02.md",
        "paper/sentinel_suite_v02.md",
        "+10.2 pp aggregate FTGA effect over 600 paired model-item rows",
        "67 fixes and 6 regressions",
        "prompt-cluster bootstrap interval is +5.8 to +15.0 pp",
        "Balanced 48-item stratified pilots recover the all-model and `gpt-5.5` positive directions in 100.0%",
        "land within 5 pp of both full-run effects in 100.0% of simulations",
        "`gpt-5.4-mini` recovers the positive direction in 92.2% of 48-item simulations",
        "`gpt-4.1-mini` in 93.5%",
        "data/stress_v02_sentinel24_ids.txt",
        "compact 24-item subset",
        "covers all 12 language-family cells",
        "captures 19/20 GPT-5.x contract failure pairs",
        "both GPT-5.5 contract residual items",
        "non-headline until confirmed on the full 120-item benchmark",
        "paper/efficiency_tradeoff_v02.md",
        "contract lowers normalized token tax but increases absolute total tokens",
        "+114.5 absolute tokens per item",
        "-36.8 repair tokens after first turn",
        "Token tax is not dollar cost",
        "paper/followup_plan_readiness_v02.md",
        "eight paper-facing complete items",
        "three launch-ready annotation surfaces",
        "original 72-row human audit",
        "48-row current-model human audit",
        "60-row v0.3 native-review packet",
        "paper/label_collection_launch_pack_v02.md",
        "180 reviewer-facing packet rows",
        "70/72 pass/fail labels",
        "69/72 labels",
        "data/current_model_human_audit/",
        "one first-turn response for every `gpt-5.4-mini` / `gpt-5.5` model-condition-language-family stratum",
        "32 automatic passes and 16 automatic failures",
        "paper/current_model_human_audit_design_v02.md",
        "data/coverage_native_review_v03/",
        "data/coverage_native_review_v03/review_sheets_v03/",
        "same CSV schema",
        "scripts/validate_completed_coverage_native_review_v03.py",
        "paper/human_audit_acceptance_rules_v02.md",
        "pre-specified quantitative gates",
        "at least 90% pass/fail agreement and 85% component agreement",
        "requires all 60 rows to be release usable",
        "native-speaker validation remains required",
        "Do not claim:",
        "v0.3 coverage pilot is paper-facing benchmark evidence before native review is completed",
    ]
    for phrase in required_phrases:
        require(phrase in normalized, f"result card missing phrase: {phrase}")
    prohibited = [
        "1,290 saved API response rows",
        "1,218 model-response rows",
        "228,831 saved provider-reported tokens",
        "three GPT-4.1-family API models exhibit measurable",
    ]
    for phrase in prohibited:
        require(phrase not in normalized, f"result card still contains stale phrase: {phrase}")
    print("result-card validation passed")


if __name__ == "__main__":
    main()
