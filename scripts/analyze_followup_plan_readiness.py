#!/usr/bin/env python
"""Map the follow-up experiment plan to current paper-ready evidence."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


PLAN_PATH = Path("additional_experiments_plan .md")
OUT_DIR = Path("results/tables/followup_plan_readiness_v02")
OUT_CSV = OUT_DIR / "followup_plan_readiness.csv"
OUT_MD = Path("paper/followup_plan_readiness_v02.md")

REQUIRED_PLAN_PHRASES = [
    "Current Execution Status",
    "Main remaining gap",
    "Current-model refresh",
    "Human/native-speaker validation",
    "Prompt mechanism experiments",
    "Benchmark coverage expansion",
    "Repair realism experiment",
    "Judge-refresh experiment",
    "Submission-ready checklist",
    "completed qualified human/native labels are still missing",
    "launch-ready but not completed",
    "If labels can be collected before submission",
    "If labels cannot be collected before submission",
    "Completed API/model-output order",
    "Remaining non-API step",
    "The human/native audit was never an API-spending step",
]

FORBIDDEN_STALE_PLAN_PHRASES = [
    "the model set is GPT-4.1-family only",
    "Day 1",
    "Day 2",
    "Days 3–5",
    "Days 3-5",
    "Completed priority order",
]

CSV_FIELDS = [
    "plan_item",
    "plan_section",
    "status",
    "paper_use",
    "evidence",
    "validation_signal",
    "next_step",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing required evidence table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_text(path: Path) -> str:
    require(path.exists(), f"missing required evidence file {path}")
    return path.read_text(encoding="utf-8")


def row_by(rows: list[dict[str, str]], field: str, value: str) -> dict[str, str]:
    for row in rows:
        if row[field] == value:
            return row
    raise AssertionError(f"missing row where {field}={value}")


def check_paths(paths: list[str]) -> str:
    for path in paths:
        require(Path(path).exists(), f"missing readiness evidence path {path}")
    return "; ".join(paths)


def one_row(path: Path) -> dict[str, str]:
    rows = load_csv(path)
    require(len(rows) == 1, f"expected one row in {path}, found {len(rows)}")
    return rows[0]


def build_rows() -> list[dict[str, str]]:
    plan = read_text(PLAN_PATH)
    normalized_plan = " ".join(plan.split())
    for phrase in REQUIRED_PLAN_PHRASES:
        require(phrase in plan or phrase in normalized_plan, f"follow-up plan missing phrase: {phrase}")
    for phrase in FORBIDDEN_STALE_PLAN_PHRASES:
        require(phrase not in plan and phrase not in normalized_plan, f"follow-up plan still contains stale phrase: {phrase}")

    refresh_rows = load_csv(Path("results/tables/current_model_refresh_v02/current_model_refresh_summary.csv"))
    require(len(refresh_rows) == 5, "expected five full-run current-refresh summary rows")
    g55 = row_by(refresh_rows, "model", "gpt-5.5")
    g54 = row_by(refresh_rows, "model", "gpt-5.4-mini")

    human_design = one_row(Path("results/tables/human_audit_v0.2_design/human_audit_design_summary.csv"))
    current_human_design = one_row(Path("results/tables/current_model_human_audit_v02_design/human_audit_design_summary.csv"))
    coverage_design = one_row(Path("results/tables/coverage_native_review_v03_design/coverage_native_review_summary.csv"))
    operator_single_assignments = load_csv(Path("results/tables/label_collection_operator_handoff_v02/operator_dispatch_assignments.csv"))
    operator_double_assignments = load_csv(Path("results/tables/label_collection_operator_handoff_v02/operator_double_label_assignments.csv"))
    require(len(operator_single_assignments) == 12, "expected 12 minimum single-label operator assignments")
    require(len(operator_double_assignments) == 24, "expected 24 preferred double-label operator assignments")

    efficiency_rows = load_csv(Path("results/tables/efficiency_tradeoff_v02/efficiency_tradeoff_paired_effects.csv"))
    require(len(efficiency_rows) == 5, "expected five efficiency paired-effect rows")
    require(
        all(float(row["token_tax_reduction"]) > 0 for row in efficiency_rows),
        "all full-run models should reduce normalized token tax",
    )
    require(
        all(float(row["mean_total_tokens_baseline_minus_contract"]) < 0 for row in efficiency_rows),
        "all full-run contract rows should increase absolute total tokens",
    )

    rows: list[dict[str, str]] = [
        {
            "plan_item": "current_model_refresh",
            "plan_section": "Experiment A",
            "status": "complete_paper_facing",
            "paper_use": "headline current-model result",
            "evidence": check_paths(
                [
                    "paper/current_model_refresh_v02.md",
                    "results/tables/current_model_refresh_v02/current_model_refresh_summary.csv",
                    "results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv",
                    "results/tables/openai_gpt54mini_stress_v02_full120/trajectory_metrics.csv",
                ]
            ),
            "validation_signal": (
                f"gpt-5.5 contract {g55['contract_ftga_pct']} FTGA, {g55['contract_mean_rtt']} RTT; "
                f"gpt-5.4-mini contract {g54['contract_ftga_pct']} FTGA with bounded sign-test evidence"
            ),
            "next_step": "none for current submission; keep GPT-5.5 as the current-model headline",
        },
        {
            "plan_item": "main_results_metrics",
            "plan_section": "Submission-ready checklist",
            "status": "complete_paper_facing",
            "paper_use": "main results table",
            "evidence": check_paths(
                [
                    "results/tables/openai_three_model_stress_v02_full120/metrics_summary.csv",
                    "results/tables/current_model_refresh_v02/current_model_refresh_summary.csv",
                    "paper/sections/05_results.tex",
                ]
            ),
            "validation_signal": "FTGA, RTT, unresolved, Repair@1/2, and token-tax rows are present for all five full-run models",
            "next_step": "none",
        },
        {
            "plan_item": "family_level_failure_story",
            "plan_section": "Submission-ready checklist",
            "status": "complete_paper_facing",
            "paper_use": "failure-mode and residual-error claims",
            "evidence": check_paths(
                [
                    "paper/failure_mode_analysis_v02_full120.md",
                    "paper/current_model_error_analysis_v02.md",
                    "results/tables/current_model_error_analysis_v02/current_model_error_by_family.csv",
                ]
            ),
            "validation_signal": "editing-preservation dominance and current-model residual families are separately audited",
            "next_step": "none",
        },
        {
            "plan_item": "language_slice_caveat",
            "plan_section": "Submission-ready checklist",
            "status": "complete_paper_facing",
            "paper_use": "bounded language-slice interpretation",
            "evidence": check_paths(
                [
                    "paper/language_slice_analysis_v02_full120.md",
                    "paper/sections/05_results.tex",
                    "scripts/lint_claim_boundaries.py",
                ]
            ),
            "validation_signal": "language-slice effects are reported with the non-population caveat enforced by the claim linter",
            "next_step": "none",
        },
        {
            "plan_item": "token_burden_caveat",
            "plan_section": "Submission-ready checklist",
            "status": "complete_paper_facing",
            "paper_use": "token-tax interpretation",
            "evidence": check_paths(
                [
                    "paper/token_burden_analysis_v02_full120.md",
                    "paper/efficiency_tradeoff_v02.md",
                    "results/tables/efficiency_tradeoff_v02/efficiency_tradeoff_paired_effects.csv",
                ]
            ),
            "validation_signal": "normalized token tax falls for five models, while absolute total tokens rise for five contract rows",
            "next_step": "none",
        },
        {
            "plan_item": "prompt_mechanism",
            "plan_section": "Experiment C",
            "status": "complete_paper_facing",
            "paper_use": "mechanism and mitigation-scope paragraph",
            "evidence": check_paths(
                [
                    "paper/prompt_ablation_analysis.md",
                    "paper/current_prompt_mechanism_gpt54mini_v02.md",
                    "paper/current_prompt_mechanism_gpt55_v02.md",
                    "scripts/validate_current_prompt_mechanism.py",
                ]
            ),
            "validation_signal": "content-preservation is close to the full contract on both current models, so prompt dominance is not claimed",
            "next_step": "none",
        },
        {
            "plan_item": "repair_realism",
            "plan_section": "Experiment F",
            "status": "complete_supporting",
            "paper_use": "interaction-burden sensitivity diagnostic",
            "evidence": check_paths(
                [
                    "paper/repair_realism_editing_baseline24.md",
                    "results/tables/openai_three_model_stress_v02_repair_realism_editing_baseline24/repair_realism_summary.csv",
                    "scripts/validate_repair_realism.py",
                ]
            ),
            "validation_signal": "repair wording sensitivity is measured on the dominant editing-preservation failures",
            "next_step": "treat as a controlled diagnostic, not a user-study result",
        },
        {
            "plan_item": "judge_refresh",
            "plan_section": "Experiment G",
            "status": "complete_supporting",
            "paper_use": "scorer sanity-check evidence",
            "evidence": check_paths(
                [
                    "paper/judge_refresh_gpt55_v02_full120.md",
                    "results/tables/openai_three_model_stress_v02_full120_judge_refresh_gpt55/judge_refresh_summary.csv",
                    "scripts/validate_judge_refresh.py",
                ]
            ),
            "validation_signal": "GPT-5.5 judge refresh agrees with the automatic scorer on 70/72 sampled labels",
            "next_step": "do not substitute judge agreement for native-speaker validation",
        },
        {
            "plan_item": "label_collection_operations",
            "plan_section": "If labels can be collected before submission",
            "status": "complete_supporting",
            "paper_use": "operator-ready label dispatch and return intake",
            "evidence": check_paths(
                [
                    "paper/label_collection_operator_handoff_v02.md",
                    "results/tables/label_collection_operator_handoff_v02/operator_dispatch_assignments.csv",
                    "results/tables/label_collection_operator_handoff_v02/operator_double_label_assignments.csv",
                    "results/tables/label_collection_operator_handoff_v02/operator_return_intake.csv",
                    "scripts/validate_label_collection_operator_handoff.py",
                ]
            ),
            "validation_signal": (
                f"{len(operator_single_assignments)} minimum single-label assignments and "
                f"{len(operator_double_assignments)} preferred double-label reviewer assignments are checked against return-intake commands"
            ),
            "next_step": "send current-model reviewer bundles first; completed labels are still required before widening claims",
        },
        {
            "plan_item": "original_human_audit_labels",
            "plan_section": "Experiment B",
            "status": "launch_ready_needs_labels",
            "paper_use": "protocol-ready only until completed annotations exist",
            "evidence": check_paths(
                [
                    "data/human_audit/human_audit_packet_v0.2.csv",
                    "data/human_audit/human_audit_launch_checklist_v0.2.md",
                    "paper/human_audit_design_audit_v02.md",
                    "paper/label_collection_launch_pack_v02.md",
                    "scripts/validate_completed_human_audit.py",
                ]
            ),
            "validation_signal": (
                f"{human_design['packet_rows']} launch rows, {human_design['auto_pass_rows']} auto passes, "
                f"{human_design['auto_fail_rows']} auto failures, blank annotation fields"
            ),
            "next_step": "collect qualified native/near-native labels and pass validate_completed_human_audit.py",
        },
        {
            "plan_item": "current_model_human_audit_labels",
            "plan_section": "Experiment B extension",
            "status": "launch_ready_needs_labels",
            "paper_use": "protocol-ready current-model validation only",
            "evidence": check_paths(
                [
                    "data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv",
                    "data/current_model_human_audit/human_audit_launch_checklist_v0.2_current_gpt5.md",
                    "paper/current_model_human_audit_design_v02.md",
                    "paper/label_collection_launch_pack_v02.md",
                    "scripts/validate_current_model_human_audit_packet.py",
                ]
            ),
            "validation_signal": (
                f"{current_human_design['packet_rows']} launch rows, {current_human_design['auto_pass_rows']} auto passes, "
                f"{current_human_design['auto_fail_rows']} auto failures, one row per current-model stratum"
            ),
            "next_step": "collect qualified labels for GPT-5.x rows before claiming current-model human validation",
        },
        {
            "plan_item": "v03_coverage_native_review",
            "plan_section": "Experiment D",
            "status": "launch_ready_needs_labels",
            "paper_use": "v0.3 coverage protocol only",
            "evidence": check_paths(
                [
                    "data/coverage_native_review_v03/coverage_native_review_packet_v03.csv",
                    "data/coverage_native_review_v03/coverage_native_review_launch_checklist_v03.md",
                    "paper/coverage_native_review_design_v03.md",
                    "paper/label_collection_launch_pack_v02.md",
                    "scripts/validate_completed_coverage_native_review_v03.py",
                ]
            ),
            "validation_signal": (
                f"{coverage_design['review_rows']} synthetic rows across {coverage_design['coverage_slices']} slices; "
                f"status {coverage_design['validation_status']}"
            ),
            "next_step": "complete native review before using v0.3 as paper-facing benchmark evidence",
        },
        {
            "plan_item": "v03_coverage_model_smokes",
            "plan_section": "Experiment D",
            "status": "bounded_diagnostic_not_headline",
            "paper_use": "runnability and scoring smoke only",
            "evidence": check_paths(
                [
                    "paper/coverage_smoke_gpt54mini_v03.md",
                    "paper/coverage_pilot_gpt54mini_v03.md",
                    "paper/coverage_smoke_gpt55_v03.md",
                ]
            ),
            "validation_signal": "saved v0.3 model-output diagnostics exist, but native review is still incomplete",
            "next_step": "keep out of headline benchmark claims until v0.3 review and a prespecified run are complete",
        },
        {
            "plan_item": "related_work_and_limitations",
            "plan_section": "Submission-ready checklist",
            "status": "complete_paper_facing",
            "paper_use": "positioning and claim boundary",
            "evidence": check_paths(
                [
                    "paper/sections/07_related_work.tex",
                    "paper/sections/08_limitations_and_ethics.tex",
                    "paper/related_work_positioning_v02.md",
                ]
            ),
            "validation_signal": "related work and limitations are checked by validate_paper_claims.py",
            "next_step": "none",
        },
        {
            "plan_item": "artifact_manifest_claim_checklist",
            "plan_section": "Submission-ready checklist",
            "status": "complete_paper_facing",
            "paper_use": "release and reproducibility gate",
            "evidence": check_paths(
                [
                    "paper/artifact_manifest.json",
                    "paper/artifact_manifest.md",
                    "paper/claim_evidence_checklist.md",
                    "scripts/run_submission_checks.py",
                ]
            ),
            "validation_signal": "manifest and claim checklist are regenerated and checked in the submission gate",
            "next_step": "rerun run_submission_checks.py after any artifact change",
        },
        {
            "plan_item": "collaborator_validated_language_pair",
            "plan_section": "Experiment E",
            "status": "not_started_requires_validator",
            "paper_use": "not claim-ready",
            "evidence": "additional_experiments_plan .md",
            "validation_signal": "no new collaborator-validated language pair is claimed in the current artifact set",
            "next_step": "add only if a qualified validator is available; otherwise leave out of the current submission",
        },
    ]
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    status_counts = Counter(row["status"] for row in rows)
    lines = [
        "# Follow-up Plan Readiness Audit",
        "",
        "This audit maps `additional_experiments_plan .md` to current repo",
        "evidence. It is a planning and claim-boundary artifact: it identifies",
        "which follow-up items are paper-facing now and which still need",
        "qualified human/native review before stronger claims are supportable.",
        "",
        "## Status Counts",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"| {status} | {count} |")
    lines.extend(
        [
            "",
            "## Evidence Map",
            "",
            "| Plan item | Section | Status | Paper use | Validation signal | Next step |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['plan_item']} | {row['plan_section']} | {row['status']} | "
            f"{row['paper_use']} | {row['validation_signal']} | {row['next_step']} |"
        )

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "The current-model refresh, prompt-mechanism diagnostic, repair-realism",
            "diagnostic, judge refresh, token-burden caveat, language-slice caveat,",
            "related work, and release manifest are ready for the current submission.",
            "",
            "Three launch-ready annotation surfaces remain incomplete: the original",
            "72-row v0.2 human-audit packet, the 48-row current-model human-audit",
            "packet, and the 60-row v0.3 native-review packet. Do not claim",
            "native/near-native validation has been completed until the completed",
            "annotation files and qualified rosters pass their validators.",
            "The consolidated label-collection launch pack in",
            "`paper/label_collection_launch_pack_v02.md` lists all reviewer-facing",
            "files, roster templates, finalization commands, and claim gates.",
            "The operator handoff in `paper/label_collection_operator_handoff_v02.md`",
            "adds validated minimum single-label assignments and preferred",
            "reviewer1/reviewer2 double-label return filenames for those same",
            "surfaces.",
            "",
            "The v0.3 model-output smokes remain bounded diagnostics. They show that",
            "the expanded coverage scaffold is runnable and scoreable, but they are",
            "not paper-facing benchmark evidence before native review and a",
            "pre-specified larger run are complete.",
            "",
            "Current recommendation: submit with the GPT-5.5 current-model headline",
            "and the launch-ready audit protocols if labels cannot be collected in",
            "time; upgrade the final paper only after completed labels pass the",
            "human/native-review gates.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-csv", type=Path, default=OUT_CSV)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    rows = build_rows()
    write_csv(args.out_csv, rows)
    write_markdown(args.out_md, rows)
    print(f"wrote follow-up plan readiness audit to {args.out_md} and {args.out_csv}")


if __name__ == "__main__":
    main()
