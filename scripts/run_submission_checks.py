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
    run_step("summarize experiment ledger", python_step("scripts/summarize_experiment_ledger.py"))
    run_step(
        "make figures",
        python_step(
            "scripts/make_figures.py",
            "--tables-dir",
            str(TABLES_DIR),
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
    run_step("claim-boundary lint", python_step("scripts/lint_claim_boundaries.py"))
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
    run_step("analyze human audit design", python_step("scripts/analyze_human_audit_design.py"))
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
    run_step("refresh artifact manifest", python_step("scripts/make_artifact_manifest.py"))
    run_step("validate paper claims", python_step("scripts/validate_paper_claims.py"))
    run_step("check artifact manifest", python_step("scripts/make_artifact_manifest.py", "--check"))
    print("submission checks passed")


if __name__ == "__main__":
    main()
