#!/usr/bin/env python
"""Regenerate local paper artifacts and run submission-facing checks."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = Path("results/tables/openai_three_model_stress_v02_full120")
FIGURES_DIR = Path("results/figures/openai_three_model_stress_v02_full120")
PAPER_FIGURES_DIR = Path("paper/figures")
SCORES_PATH = Path("results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl")
GENERIC_HELPFULNESS_FULL_SCORES_PATH = Path("results/scores/openai_nano_stress_v02_full120_generic_helpfulness_auto_scores.jsonl")
CONTENT_PRESERVATION_SCORES_PATH = Path("results/scores/openai_nano_stress_v02_full120_content_preservation_auto_scores.jsonl")
GPT54_TABLES_DIR = Path("results/tables/openai_gpt54mini_stress_v02_full120")
GPT54_CONTENT_TABLES_DIR = Path("results/tables/openai_gpt54mini_stress_v02_full120_content_preservation")
GPT55_TABLES_DIR = Path("results/tables/openai_gpt55_stress_v02_full120")
GPT55_CONTENT_TABLES_DIR = Path("results/tables/openai_gpt55_stress_v02_full120_content_preservation")
GPT54_SCORES_PATH = Path("results/scores/openai_gpt54mini_stress_v02_full120_auto_scores.jsonl")
GPT54_CONTENT_SCORES_PATH = Path("results/scores/openai_gpt54mini_stress_v02_full120_content_preservation_auto_scores.jsonl")
GPT55_SCORES_PATH = Path("results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl")
GPT55_CONTENT_SCORES_PATH = Path("results/scores/openai_gpt55_stress_v02_full120_content_preservation_auto_scores.jsonl")


def run_step(name: str, command: list[str], *, cwd: Path = ROOT) -> None:
    start = time.perf_counter()
    print(f"[run] {name}", flush=True)
    proc = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    elapsed = time.perf_counter() - start
    if proc.returncode != 0:
        print(f"[fail] {name} ({elapsed:.1f}s)", file=sys.stderr)
        if proc.stdout.strip():
            print("stdout:", file=sys.stderr)
            print(proc.stdout, file=sys.stderr)
        if proc.stderr.strip():
            print("stderr:", file=sys.stderr)
            print(proc.stderr, file=sys.stderr)
        raise SystemExit(proc.returncode)
    if proc.stdout.strip():
        print(proc.stdout.strip())
    if proc.stderr.strip():
        print(proc.stderr.strip(), file=sys.stderr)
    print(f"[ok] {name} ({elapsed:.1f}s)", flush=True)


def python_step(script: str, *args: str) -> list[str]:
    return [sys.executable, script, *args]


def refresh_paper_figures() -> None:
    print("[run] copy figures into paper/figures", flush=True)
    PAPER_FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for filename in ["ftga_by_condition.png", "repair_curve.png"]:
        src = FIGURES_DIR / filename
        dst = PAPER_FIGURES_DIR / filename
        if not src.exists():
            raise SystemExit(f"missing generated figure {src}")
        if src.stat().st_size <= 1000:
            raise SystemExit(f"generated figure too small: {src}")
        shutil.copy2(src, dst)
    print("[ok] copy figures into paper/figures", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-latex", action="store_true", help="skip PDF rebuild; validation still checks the existing PDF")
    args = parser.parse_args()

    run_step("build full v0.2 score file", python_step("scripts/build_full_v02_scores.py"))
    run_step(
        "compute full v0.2 aggregate metrics",
        python_step(
            "scripts/compute_metrics.py",
            "--scores",
            str(SCORES_PATH),
            "--out-dir",
            str(TABLES_DIR),
        ),
    )
    run_step(
        "build full v0.2 prompt-control score file",
        python_step("scripts/build_full_v02_prompt_control_scores.py"),
    )
    run_step(
        "compute full v0.2 generic-helpfulness control metrics",
        python_step(
            "scripts/compute_metrics.py",
            "--scores",
            str(GENERIC_HELPFULNESS_FULL_SCORES_PATH),
            "--out-dir",
            "results/tables/openai_nano_stress_v02_full120_generic_helpfulness",
        ),
    )
    run_step(
        "score full v0.2 content-preservation ablation",
        python_step(
            "scripts/score_auto.py",
            "--benchmark",
            "data/benchmark_stress_v0.2.jsonl",
            "--outputs",
            "results/model_outputs/openai_nano_stress_v02_full120_content_preservation.jsonl",
            "--out",
            str(CONTENT_PRESERVATION_SCORES_PATH),
        ),
    )
    run_step(
        "compute full v0.2 content-preservation ablation metrics",
        python_step(
            "scripts/compute_metrics.py",
            "--scores",
            str(CONTENT_PRESERVATION_SCORES_PATH),
            "--out-dir",
            "results/tables/openai_nano_stress_v02_full120_content_preservation",
        ),
    )
    run_step(
        "compute full v0.2 paired effects",
        python_step(
            "scripts/paired_effects.py",
            "--trajectory-metrics",
            str(TABLES_DIR / "trajectory_metrics.csv"),
            "--out-dir",
            str(TABLES_DIR),
        ),
    )
    run_step(
        "analyze full v0.2 language slices",
        python_step(
            "scripts/analyze_language_slices.py",
            "--trajectory-metrics",
            str(TABLES_DIR / "trajectory_metrics.csv"),
            "--out-dir",
            str(TABLES_DIR),
            "--out-md",
            "paper/language_slice_analysis_v02_full120.md",
        ),
    )
    run_step(
        "analyze full v0.2 repair dynamics",
        python_step(
            "scripts/analyze_repair_dynamics.py",
            "--trajectory-metrics",
            str(TABLES_DIR / "trajectory_metrics.csv"),
            "--out-dir",
            str(TABLES_DIR),
            "--out-md",
            "paper/repair_dynamics_v02_full120.md",
        ),
    )
    run_step(
        "analyze full v0.2 token burden",
        python_step(
            "scripts/analyze_token_burden.py",
            "--scores",
            str(SCORES_PATH),
            "--out-dir",
            str(TABLES_DIR),
            "--out-md",
            "paper/token_burden_analysis_v02_full120.md",
        ),
    )
    run_step(
        "analyze full v0.2 failure modes",
        python_step(
            "scripts/analyze_failure_modes.py",
            "--tables-dir",
            str(TABLES_DIR),
            "--paper-out",
            "paper/failure_mode_analysis_v02_full120.md",
        ),
    )
    run_step(
        "analyze full v0.2 item consistency",
        python_step(
            "scripts/analyze_item_consistency.py",
            "--trajectory-metrics",
            str(TABLES_DIR / "trajectory_metrics.csv"),
            "--out-dir",
            str(TABLES_DIR),
            "--out-md",
            "paper/item_consistency_analysis_v02_full120.md",
        ),
    )
    run_step(
        "analyze full v0.2 scorer components",
        python_step(
            "scripts/analyze_component_breakdown.py",
            "--scores",
            str(SCORES_PATH),
            "--out-dir",
            str(TABLES_DIR),
            "--out-md",
            "paper/component_breakdown_v02_full120.md",
        ),
    )
    run_step(
        "analyze full v0.2 scorer ablation",
        python_step(
            "scripts/analyze_scorer_ablation.py",
            "--scores",
            str(SCORES_PATH),
            "--out-dir",
            str(TABLES_DIR),
            "--out-md",
            "paper/scorer_ablation_sensitivity_v02_full120.md",
        ),
    )
    run_step(
        "analyze full v0.2 task-useful failures",
        python_step(
            "scripts/analyze_task_useful_failures.py",
            "--scores",
            str(SCORES_PATH),
            "--out-dir",
            str(TABLES_DIR),
            "--out-md",
            "paper/task_useful_failure_analysis_v02_full120.md",
            "--expected-first-turn-rows",
            "720",
        ),
    )
    run_step(
        "build full v0.2 first-turn error atlas",
        python_step(
            "scripts/build_error_atlas.py",
            "--scores",
            str(SCORES_PATH),
            "--trajectories",
            str(TABLES_DIR / "trajectory_metrics.csv"),
            "--out-csv",
            str(TABLES_DIR / "first_turn_error_atlas.csv"),
            "--out-md",
            "paper/error_atlas_v02_full120.md",
        ),
    )
    run_step(
        "compute full v0.2 paired sign tests",
        python_step(
            "scripts/paired_significance.py",
            "--trajectory-metrics",
            str(TABLES_DIR / "trajectory_metrics.csv"),
            "--out-csv",
            str(TABLES_DIR / "paired_significance_by_model.csv"),
            "--out-md",
            "paper/paired_significance_v02_full120.md",
        ),
    )
    run_step(
        "score GPT-5.4-mini current-model full120",
        python_step(
            "scripts/score_auto.py",
            "--benchmark",
            "data/benchmark_stress_v0.2.jsonl",
            "--outputs",
            "results/model_outputs/openai_gpt54mini_stress_v02_full120.jsonl",
            "--out",
            str(GPT54_SCORES_PATH),
        ),
    )
    run_step(
        "compute GPT-5.4-mini current-model metrics",
        python_step(
            "scripts/compute_metrics.py",
            "--scores",
            str(GPT54_SCORES_PATH),
            "--out-dir",
            str(GPT54_TABLES_DIR),
        ),
    )
    run_step(
        "compute GPT-5.4-mini current-model paired effects",
        python_step(
            "scripts/paired_effects.py",
            "--trajectory-metrics",
            str(GPT54_TABLES_DIR / "trajectory_metrics.csv"),
            "--out-dir",
            str(GPT54_TABLES_DIR),
        ),
    )
    run_step(
        "compute GPT-5.4-mini current-model paired sign tests",
        python_step(
            "scripts/paired_significance.py",
            "--trajectory-metrics",
            str(GPT54_TABLES_DIR / "trajectory_metrics.csv"),
            "--out-csv",
            str(GPT54_TABLES_DIR / "paired_significance_by_model.csv"),
            "--out-md",
            "paper/paired_significance_gpt54mini_v02_full120.md",
        ),
    )
    run_step(
        "analyze GPT-5.4-mini current-model task-useful failures",
        python_step(
            "scripts/analyze_task_useful_failures.py",
            "--scores",
            str(GPT54_SCORES_PATH),
            "--out-dir",
            str(GPT54_TABLES_DIR),
            "--out-md",
            "paper/task_useful_failure_analysis_gpt54mini_v02_full120.md",
            "--expected-first-turn-rows",
            "240",
        ),
    )
    run_step(
        "score GPT-5.4-mini current-model content-preservation",
        python_step(
            "scripts/score_auto.py",
            "--benchmark",
            "data/benchmark_stress_v0.2.jsonl",
            "--outputs",
            "results/model_outputs/openai_gpt54mini_stress_v02_full120_content_preservation.jsonl",
            "--out",
            str(GPT54_CONTENT_SCORES_PATH),
        ),
    )
    run_step(
        "compute GPT-5.4-mini current-model content-preservation metrics",
        python_step(
            "scripts/compute_metrics.py",
            "--scores",
            str(GPT54_CONTENT_SCORES_PATH),
            "--out-dir",
            str(GPT54_CONTENT_TABLES_DIR),
        ),
    )
    run_step(
        "score GPT-5.5 current-model full120",
        python_step(
            "scripts/score_auto.py",
            "--benchmark",
            "data/benchmark_stress_v0.2.jsonl",
            "--outputs",
            "results/model_outputs/openai_gpt55_stress_v02_full120.jsonl",
            "--out",
            str(GPT55_SCORES_PATH),
        ),
    )
    run_step(
        "compute GPT-5.5 current-model metrics",
        python_step(
            "scripts/compute_metrics.py",
            "--scores",
            str(GPT55_SCORES_PATH),
            "--out-dir",
            str(GPT55_TABLES_DIR),
        ),
    )
    run_step(
        "compute GPT-5.5 current-model paired effects",
        python_step(
            "scripts/paired_effects.py",
            "--trajectory-metrics",
            str(GPT55_TABLES_DIR / "trajectory_metrics.csv"),
            "--out-dir",
            str(GPT55_TABLES_DIR),
        ),
    )
    run_step(
        "compute GPT-5.5 current-model paired sign tests",
        python_step(
            "scripts/paired_significance.py",
            "--trajectory-metrics",
            str(GPT55_TABLES_DIR / "trajectory_metrics.csv"),
            "--out-csv",
            str(GPT55_TABLES_DIR / "paired_significance_by_model.csv"),
            "--out-md",
            "paper/paired_significance_gpt55_v02_full120.md",
        ),
    )
    run_step(
        "analyze GPT-5.5 current-model task-useful failures",
        python_step(
            "scripts/analyze_task_useful_failures.py",
            "--scores",
            str(GPT55_SCORES_PATH),
            "--out-dir",
            str(GPT55_TABLES_DIR),
            "--out-md",
            "paper/task_useful_failure_analysis_gpt55_v02_full120.md",
            "--expected-first-turn-rows",
            "240",
        ),
    )
    run_step(
        "score GPT-5.5 current-model content-preservation",
        python_step(
            "scripts/score_auto.py",
            "--benchmark",
            "data/benchmark_stress_v0.2.jsonl",
            "--outputs",
            "results/model_outputs/openai_gpt55_stress_v02_full120_content_preservation.jsonl",
            "--out",
            str(GPT55_CONTENT_SCORES_PATH),
        ),
    )
    run_step(
        "compute GPT-5.5 current-model content-preservation metrics",
        python_step(
            "scripts/compute_metrics.py",
            "--scores",
            str(GPT55_CONTENT_SCORES_PATH),
            "--out-dir",
            str(GPT55_CONTENT_TABLES_DIR),
        ),
    )
    run_step("analyze current-model refresh", python_step("scripts/analyze_current_model_refresh.py"))
    run_step("validate current-model refresh", python_step("scripts/validate_current_model_refresh.py"))
    run_step("analyze current-model uncertainty", python_step("scripts/analyze_current_model_uncertainty.py"))
    run_step("validate current-model uncertainty", python_step("scripts/validate_current_model_uncertainty.py"))
    run_step("analyze current-model heterogeneity", python_step("scripts/analyze_current_model_heterogeneity.py"))
    run_step("validate current-model heterogeneity", python_step("scripts/validate_current_model_heterogeneity.py"))
    run_step("analyze current-model regression risk", python_step("scripts/analyze_current_model_regression_risk.py"))
    run_step("validate current-model regression risk", python_step("scripts/validate_current_model_regression_risk.py"))
    run_step("analyze current-model residual errors", python_step("scripts/analyze_current_model_error_analysis.py"))
    run_step("validate current-model residual errors", python_step("scripts/validate_current_model_error_analysis.py"))
    run_step("analyze current-model case studies", python_step("scripts/analyze_current_model_case_studies.py"))
    run_step("validate current-model case studies", python_step("scripts/validate_current_model_case_studies.py"))
    run_step("analyze current-model scorer sensitivity", python_step("scripts/analyze_current_model_scorer_sensitivity.py"))
    run_step("validate current-model scorer sensitivity", python_step("scripts/validate_current_model_scorer_sensitivity.py"))
    run_step("analyze generation progress probe", python_step("scripts/analyze_generation_progress_probe.py"))
    run_step("validate generation progress probe", python_step("scripts/validate_generation_progress_probe.py"))
    run_step("analyze efficiency tradeoff", python_step("scripts/analyze_efficiency_tradeoff.py"))
    run_step("validate efficiency tradeoff", python_step("scripts/validate_efficiency_tradeoff.py"))
    run_step("analyze completed-label claim gates", python_step("scripts/analyze_completed_label_claim_gates.py"))
    run_step("validate completed-label claim gates", python_step("scripts/validate_completed_label_claim_gates.py"))
    run_step("analyze current-model prompt mechanism", python_step("scripts/analyze_current_prompt_mechanism.py"))
    run_step("validate current-model prompt mechanism", python_step("scripts/validate_current_prompt_mechanism.py"))
    run_step("analyze prompt-family scorecard", python_step("scripts/analyze_prompt_family_scorecard.py"))
    run_step("validate prompt-family scorecard", python_step("scripts/validate_prompt_family_scorecard.py"))
    run_step("analyze all-model paired significance", python_step("scripts/analyze_all_model_paired_significance.py"))
    run_step("validate all-model paired significance", python_step("scripts/validate_all_model_paired_significance.py"))
    run_step("analyze all-model clustered uncertainty", python_step("scripts/analyze_all_model_uncertainty.py"))
    run_step("validate all-model clustered uncertainty", python_step("scripts/validate_all_model_uncertainty.py"))
    run_step("analyze contract-benefit decomposition", python_step("scripts/analyze_contract_benefit_decomposition.py"))
    run_step("validate contract-benefit decomposition", python_step("scripts/validate_contract_benefit_decomposition.py"))
    run_step("analyze human/native-review acceptance rules", python_step("scripts/analyze_human_audit_acceptance_rules.py"))
    run_step("validate human/native-review acceptance rules", python_step("scripts/validate_human_audit_acceptance_rules.py"))
    run_step("analyze human/native-review threshold rationale", python_step("scripts/analyze_human_audit_threshold_rationale.py"))
    run_step("validate human/native-review threshold rationale", python_step("scripts/validate_human_audit_threshold_rationale.py"))
    run_step("analyze label-collection launch pack", python_step("scripts/analyze_label_collection_launch_pack.py"))
    run_step("validate label-collection launch pack", python_step("scripts/validate_label_collection_launch_pack.py"))
    run_step("analyze follow-up plan readiness", python_step("scripts/analyze_followup_plan_readiness.py"))
    run_step("validate follow-up plan readiness", python_step("scripts/validate_followup_plan_readiness.py"))
    run_step("analyze prompt-control diagnostic", python_step("scripts/analyze_prompt_control.py"))
    run_step("analyze prompt-ablation diagnostic", python_step("scripts/analyze_prompt_ablation.py"))
    run_step(
        "analyze judge agreement",
        python_step(
            "scripts/analyze_judge_agreement.py",
            "--audit",
            "results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl",
            "--scores",
            str(SCORES_PATH),
            "--out-dir",
            "results/tables/openai_three_model_stress_v02_full120_judge_audit72",
            "--out-md",
            "paper/judge_agreement_analysis_v02_full120.md",
        ),
    )
    run_step("analyze GPT-5.5 judge refresh", python_step("scripts/analyze_judge_refresh.py"))
    run_step("validate GPT-5.5 judge refresh", python_step("scripts/validate_judge_refresh.py"))
    run_step("analyze repair-realism diagnostic", python_step("scripts/analyze_repair_realism.py"))
    run_step("validate repair-realism diagnostic", python_step("scripts/validate_repair_realism.py"))
    run_step("generate v0.3 coverage expansion scaffold", python_step("scripts/generate_coverage_expansion_v03.py"))
    run_step("analyze v0.3 coverage expansion scaffold", python_step("scripts/analyze_coverage_expansion_v03.py"))
    run_step("validate v0.3 coverage expansion scaffold", python_step("scripts/validate_coverage_expansion_v03.py"))
    run_step("generate v0.3 coverage native-review packet", python_step("scripts/make_coverage_native_review_packet_v03.py"))
    run_step("validate v0.3 coverage native-review packet", python_step("scripts/validate_coverage_native_review_packet_v03.py"))
    run_step("generate v0.3 coverage native-review sheets", python_step("scripts/make_coverage_native_review_sheets_v03.py"))
    run_step("validate v0.3 coverage native-review sheets", python_step("scripts/validate_coverage_native_review_sheets_v03.py"))
    run_step("analyze v0.3 coverage native-review design", python_step("scripts/analyze_coverage_native_review_design_v03.py"))
    run_step(
        "score v0.3 coverage smoke",
        python_step(
            "scripts/score_auto.py",
            "--benchmark",
            "data/benchmark_stress_v0.3_expansion.jsonl",
            "--outputs",
            "results/model_outputs/openai_gpt54mini_stress_v03_smoke6.jsonl",
            "--out",
            "results/scores/openai_gpt54mini_stress_v03_smoke6_auto_scores.jsonl",
        ),
    )
    run_step(
        "compute v0.3 coverage smoke metrics",
        python_step(
            "scripts/compute_metrics.py",
            "--scores",
            "results/scores/openai_gpt54mini_stress_v03_smoke6_auto_scores.jsonl",
            "--out-dir",
            "results/tables/openai_gpt54mini_stress_v03_smoke6",
        ),
    )
    run_step("analyze v0.3 coverage smoke", python_step("scripts/analyze_coverage_smoke_v03.py"))
    run_step("validate v0.3 coverage smoke", python_step("scripts/validate_coverage_smoke_v03.py"))
    run_step(
        "score GPT-5.5 v0.3 coverage smoke",
        python_step(
            "scripts/score_auto.py",
            "--benchmark",
            "data/benchmark_stress_v0.3_expansion.jsonl",
            "--outputs",
            "results/model_outputs/openai_gpt55_stress_v03_smoke6.jsonl",
            "--out",
            "results/scores/openai_gpt55_stress_v03_smoke6_auto_scores.jsonl",
        ),
    )
    run_step(
        "compute GPT-5.5 v0.3 coverage smoke metrics",
        python_step(
            "scripts/compute_metrics.py",
            "--scores",
            "results/scores/openai_gpt55_stress_v03_smoke6_auto_scores.jsonl",
            "--out-dir",
            "results/tables/openai_gpt55_stress_v03_smoke6",
        ),
    )
    run_step(
        "analyze GPT-5.5 v0.3 coverage smoke",
        python_step(
            "scripts/analyze_coverage_smoke_v03.py",
            "--benchmark",
            "data/benchmark_stress_v0.3_expansion.jsonl",
            "--scores",
            "results/scores/openai_gpt55_stress_v03_smoke6_auto_scores.jsonl",
            "--outputs",
            "results/model_outputs/openai_gpt55_stress_v03_smoke6.jsonl",
            "--out-dir",
            "results/tables/openai_gpt55_stress_v03_smoke6",
            "--out-md",
            "paper/coverage_smoke_gpt55_v03.md",
        ),
    )
    run_step(
        "validate GPT-5.5 v0.3 coverage smoke",
        python_step(
            "scripts/validate_coverage_smoke_v03.py",
            "--outputs",
            "results/model_outputs/openai_gpt55_stress_v03_smoke6.jsonl",
            "--scores",
            "results/scores/openai_gpt55_stress_v03_smoke6_auto_scores.jsonl",
            "--tables-dir",
            "results/tables/openai_gpt55_stress_v03_smoke6",
            "--report",
            "paper/coverage_smoke_gpt55_v03.md",
            "--expected-model",
            "gpt-5.5",
            "--expected-api-rows",
            "12",
            "--expected-input-tokens",
            "1632",
            "--expected-output-tokens",
            "870",
            "--expected-baseline-first-turn-passes",
            "6",
            "--expected-contract-first-turn-passes",
            "6",
            "--expected-first-turn-failure-count",
            "0",
            "--expected-successful-repair-rows",
            "0",
            "--expected-baseline-mean-rtt",
            "0",
            "--expected-contract-mean-rtt",
            "0",
            "--expected-es-ar-baseline-ftga",
            "1",
            "--expected-failure-item",
            "",
            "--expected-failure-types",
            "",
        ),
    )
    run_step("build v0.3 coverage pilot outputs", python_step("scripts/build_coverage_pilot_v03_outputs.py"))
    run_step(
        "score v0.3 coverage pilot",
        python_step(
            "scripts/score_auto.py",
            "--benchmark",
            "data/benchmark_stress_v0.3_expansion.jsonl",
            "--outputs",
            "results/model_outputs/openai_gpt54mini_stress_v03_pilot24.jsonl",
            "--out",
            "results/scores/openai_gpt54mini_stress_v03_pilot24_auto_scores.jsonl",
        ),
    )
    run_step(
        "compute v0.3 coverage pilot metrics",
        python_step(
            "scripts/compute_metrics.py",
            "--scores",
            "results/scores/openai_gpt54mini_stress_v03_pilot24_auto_scores.jsonl",
            "--out-dir",
            "results/tables/openai_gpt54mini_stress_v03_pilot24",
        ),
    )
    run_step("analyze v0.3 coverage pilot", python_step("scripts/analyze_coverage_pilot_v03.py"))
    run_step("validate v0.3 coverage pilot", python_step("scripts/validate_coverage_pilot_v03.py"))
    run_step("summarize experiment ledger", python_step("scripts/summarize_experiment_ledger.py"))
    run_step(
        "make figures",
        python_step(
            "scripts/make_figures.py",
            "--tables-dir",
            str(TABLES_DIR),
            "--extra-summary",
            "results/tables/openai_gpt54mini_stress_v02_full120/metrics_summary.csv",
            "--extra-summary",
            "results/tables/openai_gpt55_stress_v02_full120/metrics_summary.csv",
            "--extra-trajectories",
            "results/tables/openai_gpt54mini_stress_v02_full120/trajectory_metrics.csv",
            "--extra-trajectories",
            "results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv",
            "--out-dir",
            str(FIGURES_DIR),
        ),
    )
    refresh_paper_figures()
    if not args.skip_latex:
        run_step(
            "build PDF",
            ["latexmk", "-pdf", "-interaction=nonstopmode", "main.tex"],
            cwd=ROOT / "paper",
    )
    run_step("score regression tests", python_step("scripts/test_score_auto.py"))
    run_step("human-audit completion regression tests", python_step("scripts/test_human_audit_completion.py"))
    run_step("human-audit adjudication regression tests", python_step("scripts/test_human_audit_adjudication.py"))
    run_step("coverage native-review completion regression tests", python_step("scripts/test_coverage_native_review_completion.py"))
    run_step("coverage native-review adjudication regression tests", python_step("scripts/test_coverage_native_review_adjudication.py"))
    run_step("review-export merge regression tests", python_step("scripts/test_merge_review_exports.py"))
    run_step("completed-label claim-gate regression tests", python_step("scripts/test_completed_label_claim_gates.py"))
    run_step("coverage native-review sheet validation", python_step("scripts/validate_coverage_native_review_sheets_v03.py"))
    run_step("claim-boundary lint", python_step("scripts/lint_claim_boundaries.py"))
    run_step("validate release docs", python_step("scripts/validate_release_docs.py"))
    run_step("validate result card", python_step("scripts/validate_result_card.py"))
    run_step("validate qualitative examples", python_step("scripts/validate_qualitative_examples.py"))
    run_step("validate follow-up probe", python_step("scripts/validate_followup_probe.py"))
    run_step(
        "generate v0.2 human audit packet",
        python_step(
            "scripts/make_human_audit_packet.py",
            "--benchmark",
            "data/benchmark_stress_v0.2.jsonl",
            "--scores",
            str(SCORES_PATH),
            "--out-dir",
            "data/human_audit",
            "--packet-version",
            "v0.2",
            "--seed",
            "23",
        ),
    )
    run_step("validate human audit packet", python_step("scripts/validate_human_audit_packet.py"))
    run_step("generate human audit review sheets", python_step("scripts/make_human_audit_review_sheets.py"))
    run_step("validate human audit review sheets", python_step("scripts/validate_human_audit_review_sheets.py"))
    run_step("analyze human audit design", python_step("scripts/analyze_human_audit_design.py"))
    run_step(
        "generate current-model human audit packet",
        python_step(
            "scripts/make_human_audit_packet.py",
            "--benchmark",
            "data/benchmark_stress_v0.2.jsonl",
            "--scores",
            str(GPT54_SCORES_PATH),
            str(GPT55_SCORES_PATH),
            "--out-dir",
            "data/current_model_human_audit",
            "--packet-version",
            "v0.2_current_gpt5",
            "--seed",
            "29",
            "--prefer-failures",
        ),
    )
    run_step(
        "validate current-model human audit packet",
        python_step(
            "scripts/validate_human_audit_packet.py",
            "--out-dir",
            "data/current_model_human_audit",
            "--packet-version",
            "v0.2_current_gpt5",
            "--expected-models",
            "gpt-5.4-mini,gpt-5.5",
        ),
    )
    run_step(
        "generate current-model human audit review sheets",
        python_step(
            "scripts/make_human_audit_review_sheets.py",
            "--packet",
            "data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv",
            "--out-dir",
            "data/current_model_human_audit/review_sheets_v0.2_current_gpt5",
            "--packet-version",
            "v0.2_current_gpt5",
        ),
    )
    run_step(
        "validate current-model human audit review sheets",
        python_step(
            "scripts/validate_human_audit_review_sheets.py",
            "--packet",
            "data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv",
            "--out-dir",
            "data/current_model_human_audit/review_sheets_v0.2_current_gpt5",
            "--packet-version",
            "v0.2_current_gpt5",
        ),
    )
    run_step(
        "analyze current-model human audit design",
        python_step(
            "scripts/analyze_human_audit_design.py",
            "--packet",
            "data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv",
            "--answer-key",
            "data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv",
            "--out-dir",
            "results/tables/current_model_human_audit_v02_design",
            "--out-md",
            "paper/current_model_human_audit_design_v02.md",
            "--expected-models",
            "gpt-5.4-mini,gpt-5.5",
            "--title",
            "Current-Model Human Audit Design Audit",
        ),
    )
    run_step("validate current-model human audit launch packet", python_step("scripts/validate_current_model_human_audit_packet.py"))
    run_step("build label-collection reviewer bundles", python_step("scripts/build_label_collection_bundles.py"))
    run_step("validate label-collection reviewer bundles", python_step("scripts/validate_label_collection_bundles.py"))
    run_step("analyze label-collection dispatch readiness", python_step("scripts/analyze_label_collection_dispatch.py"))
    run_step("validate label-collection dispatch readiness", python_step("scripts/validate_label_collection_dispatch.py"))
    run_step(
        "validate expanded stress benchmark",
        python_step(
            "scripts/validate_stress_benchmark.py",
            "--benchmark",
            "data/benchmark_stress_v0.2.jsonl",
            "--expected-per-cell",
            "10",
        ),
    )
    run_step("analyze discovery cues", python_step("scripts/analyze_discovery_cues.py"))
    run_step("analyze benchmark quality", python_step("scripts/analyze_benchmark_quality.py"))
    run_step("validate label-collection launch pack", python_step("scripts/validate_label_collection_launch_pack.py"))
    run_step("validate label-collection dispatch readiness", python_step("scripts/validate_label_collection_dispatch.py"))
    run_step("validate human/native-review threshold rationale", python_step("scripts/validate_human_audit_threshold_rationale.py"))
    run_step("validate all-model paired significance", python_step("scripts/validate_all_model_paired_significance.py"))
    run_step("validate all-model clustered uncertainty", python_step("scripts/validate_all_model_uncertainty.py"))
    run_step("validate contract-benefit decomposition", python_step("scripts/validate_contract_benefit_decomposition.py"))
    run_step("validate prompt-family scorecard", python_step("scripts/validate_prompt_family_scorecard.py"))
    run_step("refresh artifact manifest", python_step("scripts/make_artifact_manifest.py"))
    run_step("validate paper claims", python_step("scripts/validate_paper_claims.py"))
    run_step("check artifact manifest", python_step("scripts/make_artifact_manifest.py", "--check"))
    print("submission checks passed")


if __name__ == "__main__":
    main()
