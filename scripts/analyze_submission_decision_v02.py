#!/usr/bin/env python
"""Synthesize current follow-up evidence into a submission decision audit."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Any


OUT_DIR = Path("results/tables/submission_decision_v02")
OUT_MD = Path("paper/submission_decision_v02.md")

READINESS_CSV = Path("results/tables/followup_plan_readiness_v02/followup_plan_readiness.csv")
CONCERN_CSV = Path("results/tables/reviewer_concern_audit_v02/reviewer_concern_audit.csv")
CONCERN_SUMMARY_CSV = Path("results/tables/reviewer_concern_audit_v02/reviewer_concern_summary.csv")
PRIORITY_CSV = Path("results/tables/label_collection_priority_v02/label_collection_priority.csv")
CLAIM_GATES_CSV = Path("results/tables/completed_label_claim_gates_v02/completed_label_claim_gates.csv")


EVIDENCE_PATHS = [
    "additional_experiments_plan .md",
    "paper/followup_plan_readiness_v02.md",
    "paper/reviewer_concern_audit_v02.md",
    "paper/label_collection_priority_v02.md",
    "paper/completed_label_claim_gates_v02.md",
    "paper/claim_evidence_checklist.md",
    "paper/main.tex",
    "scripts/run_submission_checks.py",
]

CSV_FIELDS = [
    "decision_id",
    "decision",
    "status",
    "paper_use_now",
    "evidence_signal",
    "claim_boundary",
    "next_action",
    "evidence",
]

SUMMARY_FIELDS = [
    "paper_facing_complete_items",
    "supporting_complete_items",
    "launch_ready_label_surfaces",
    "reviewer_concerns_audited",
    "reviewer_concerns_answered_or_bounded",
    "external_label_blockers",
    "completed_label_gates_needing_labels",
    "priority_first_surface",
    "priority_first_rows",
    "openai_api_calls",
    "submission_decision",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing submission-decision input {path}")
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    require(rows, f"empty submission-decision input {path}")
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, f"refusing to write empty submission-decision table {path}")
    fields = fieldnames or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def source_paths(*paths: str) -> str:
    for path in paths:
        require(Path(path).exists(), f"missing submission-decision evidence path {path}")
    return "; ".join(paths)


def build_summary(
    readiness_rows: list[dict[str, str]],
    concern_rows: list[dict[str, str]],
    concern_summary_rows: list[dict[str, str]],
    priority_rows: list[dict[str, str]],
    gate_rows: list[dict[str, str]],
) -> dict[str, Any]:
    readiness_counts = Counter(row["status"] for row in readiness_rows)
    concern_counts = {row["readiness"]: int(row["concern_count"]) for row in concern_summary_rows}
    gate_counts = Counter(row["status"] for row in gate_rows)

    require(readiness_counts["complete_paper_facing"] == 8, f"unexpected paper-facing count {readiness_counts}")
    require(readiness_counts["complete_supporting"] == 3, f"unexpected supporting count {readiness_counts}")
    require(readiness_counts["launch_ready_needs_labels"] == 3, f"unexpected launch-ready count {readiness_counts}")
    require(len(concern_rows) == 10, f"expected 10 reviewer concerns, found {len(concern_rows)}")
    require(concern_counts["external_label_blocker"] == 1, f"expected one external label blocker: {concern_counts}")
    require(gate_counts == Counter({"needs_labels": 3}), f"completed-label gates should still need labels: {gate_counts}")
    require(all(row["claim_decision"] == "no_claim" for row in gate_rows), "a completed-label gate unexpectedly unlocks a claim")

    priority_rows = sorted(priority_rows, key=lambda row: int(row["priority_rank"]))
    first = priority_rows[0]
    require(first["surface_id"] == "current_model_human_audit_v02", "current-model audit should remain first label priority")
    require(first["packet_rows"] == "48", "current-model audit should remain 48 rows")

    answered_or_bounded = (
        concern_counts["covered"]
        + concern_counts["covered_with_boundary"]
        + concern_counts["diagnostic_only"]
    )
    return {
        "paper_facing_complete_items": readiness_counts["complete_paper_facing"],
        "supporting_complete_items": readiness_counts["complete_supporting"],
        "launch_ready_label_surfaces": readiness_counts["launch_ready_needs_labels"],
        "reviewer_concerns_audited": len(concern_rows),
        "reviewer_concerns_answered_or_bounded": answered_or_bounded,
        "external_label_blockers": concern_counts["external_label_blocker"],
        "completed_label_gates_needing_labels": gate_counts["needs_labels"],
        "priority_first_surface": first["surface_id"],
        "priority_first_rows": first["packet_rows"],
        "openai_api_calls": 0,
        "submission_decision": "submit_with_conservative_claims_if_labels_are_unavailable",
    }


def build_decision_rows(summary: dict[str, Any]) -> list[dict[str, str]]:
    complete_signal = (
        f"{summary['paper_facing_complete_items']} paper-facing items, "
        f"{summary['supporting_complete_items']} supporting diagnostics, and "
        f"{summary['reviewer_concerns_answered_or_bounded']}/"
        f"{summary['reviewer_concerns_audited']} reviewer concerns answered or bounded"
    )
    label_signal = (
        f"{summary['launch_ready_label_surfaces']} launch-ready label surfaces remain incomplete; "
        f"{summary['completed_label_gates_needing_labels']} completed-label claim gates still need labels"
    )
    return [
        {
            "decision_id": "submit_now_if_no_labels",
            "decision": "submit_with_conservative_claims",
            "status": "ready_with_external_label_blocker",
            "paper_use_now": "Use the GPT-5.5 current-model headline, all-five-model robustness, scorer audits, prompt-mechanism diagnostics, and launch-ready label protocols.",
            "evidence_signal": complete_signal,
            "claim_boundary": "Do not claim completed native/near-native validation.",
            "next_action": "Rerun scripts/run_submission_checks.py after any artifact or claim-boundary change.",
            "evidence": source_paths(
                "paper/followup_plan_readiness_v02.md",
                "paper/reviewer_concern_audit_v02.md",
                "paper/claim_evidence_checklist.md",
                "scripts/run_submission_checks.py",
            ),
        },
        {
            "decision_id": "main_headline",
            "decision": "lead_with_gpt55_progress_probe",
            "status": "paper_facing_ready",
            "paper_use_now": "Report GPT-5.5 moving from 81.7% to 98.3% FTGA with zero unresolved trajectories under the contract.",
            "evidence_signal": "current_model_refresh is complete_paper_facing and current_model_timeliness is covered",
            "claim_boundary": "Keep GPT-5.4-mini as a bounded lower-cost diagnostic because its FTGA interval crosses zero.",
            "next_action": "No additional API run is justified for the current-model headline before labels.",
            "evidence": source_paths(
                "paper/current_model_refresh_v02.md",
                "paper/current_model_uncertainty_v02.md",
                "paper/current_model_regression_risk_v02.md",
                "paper/reviewer_concern_audit_v02.md",
            ),
        },
        {
            "decision_id": "human_native_upgrade",
            "decision": "upgrade_only_after_completed_labels",
            "status": "external_labels_required",
            "paper_use_now": "Describe human/native review as launch-ready protocol evidence only.",
            "evidence_signal": label_signal,
            "claim_boundary": "No human/native-validation claim is unlocked until finalized labels and rosters pass the completed-label gates.",
            "next_action": f"Collect {summary['priority_first_rows']} current-model audit rows first, then original v0.2 labels, then v0.3 coverage review if reviewer capacity allows.",
            "evidence": source_paths(
                "paper/label_collection_priority_v02.md",
                "paper/completed_label_claim_gates_v02.md",
                "results/tables/completed_label_claim_gates_v02/completed_label_claim_gates.csv",
                "results/tables/label_collection_priority_v02/label_collection_priority.csv",
            ),
        },
        {
            "decision_id": "coverage_v03_boundary",
            "decision": "keep_v03_out_of_headline",
            "status": "diagnostic_only_until_native_review",
            "paper_use_now": "Use v0.3 as coverage scaffold, native-review packet, and bounded smoke/pilot evidence only.",
            "evidence_signal": "v03_coverage_model_smokes is bounded_diagnostic_not_headline and v03_coverage_native_review still needs labels",
            "claim_boundary": "Do not treat v0.3 as paper-facing benchmark evidence until native review and a pre-specified larger run are complete.",
            "next_action": "Complete v0.3 native review before adding any v0.3 benchmark-performance claim.",
            "evidence": source_paths(
                "paper/coverage_expansion_v03.md",
                "paper/coverage_native_review_design_v03.md",
                "paper/coverage_pilot_gpt54mini_v03.md",
                "paper/coverage_smoke_gpt55_v03.md",
            ),
        },
        {
            "decision_id": "api_budget_posture",
            "decision": "do_not_spend_more_api_before_labels",
            "status": "no_api_next_step",
            "paper_use_now": "Saved model outputs and judge audits already support the current conservative package.",
            "evidence_signal": "OpenAI API calls for this audit: 0; the remaining high-value step is label collection, not another model run",
            "claim_boundary": "Any new paid run must be tied to a claim gap that completed labels cannot answer.",
            "next_action": "Spend remaining effort on qualified labels and release-gate synchronization.",
            "evidence": source_paths(
                "additional_experiments_plan .md",
                "paper/experiment_ledger_v02.md",
                "paper/followup_plan_readiness_v02.md",
            ),
        },
    ]


def write_markdown(path: Path, summary: dict[str, Any], rows: list[dict[str, str]]) -> None:
    lines = [
        "# Submission Decision Audit",
        "",
        "This no-API audit synthesizes the follow-up plan readiness map, reviewer",
        "concern audit, label-collection priority, and completed-label claim gates.",
        "It is a submission-control artifact, not a new experiment and not completed",
        "human/native validation.",
        "",
        "## Summary",
        "",
        f"- Paper-facing complete items: {summary['paper_facing_complete_items']}",
        f"- Supporting complete diagnostics: {summary['supporting_complete_items']}",
        f"- Launch-ready label surfaces still needing labels: {summary['launch_ready_label_surfaces']}",
        f"- Reviewer concerns audited: {summary['reviewer_concerns_audited']}",
        f"- Reviewer concerns answered or bounded: {summary['reviewer_concerns_answered_or_bounded']}",
        f"- External label blockers: {summary['external_label_blockers']}",
        f"- Completed-label gates still needing labels: {summary['completed_label_gates_needing_labels']}",
        f"- First label priority: `{summary['priority_first_surface']}` ({summary['priority_first_rows']} rows)",
        f"- OpenAI API calls: {summary['openai_api_calls']}",
        "- Decision: submit with conservative claims if labels are unavailable; upgrade only after completed labels pass gates.",
        "",
        "## Decision Matrix",
        "",
        "| Decision ID | Decision | Status | Evidence signal | Claim boundary | Next action |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['decision_id']}` | {row['decision']} | {row['status']} | "
            f"{row['evidence_signal']} | {row['claim_boundary']} | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Evidence Index",
            "",
            "| Decision ID | Evidence |",
            "|---|---|",
        ]
    )
    for row in rows:
        evidence = "<br>".join(f"`{item}`" for item in row["evidence"].split("; "))
        lines.append(f"| `{row['decision_id']}` | {evidence} |")
    lines.extend(
        [
            "",
            "## Submission Posture",
            "",
            "The current package is submission-ready only under conservative wording:",
            "current-model, robustness, scorer-audit, mechanism, repair-realism,",
            "and launch-protocol claims are supported; completed native/near-native",
            "validation is not. The highest-value upgrade is to collect the 48-row",
            "current-model human/native audit first, because it is the smallest",
            "label surface that directly supports the GPT-5.x headline.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    for path in EVIDENCE_PATHS:
        require(Path(path).exists(), f"missing submission-decision source {path}")
    readiness_rows = read_csv(READINESS_CSV)
    concern_rows = read_csv(CONCERN_CSV)
    concern_summary_rows = read_csv(CONCERN_SUMMARY_CSV)
    priority_rows = read_csv(PRIORITY_CSV)
    gate_rows = read_csv(CLAIM_GATES_CSV)
    summary = build_summary(readiness_rows, concern_rows, concern_summary_rows, priority_rows, gate_rows)
    decision_rows = build_decision_rows(summary)

    write_csv(args.out_dir / "submission_decision.csv", decision_rows, CSV_FIELDS)
    write_csv(args.out_dir / "submission_decision_summary.csv", [summary], SUMMARY_FIELDS)
    write_markdown(args.out_md, summary, decision_rows)
    print(f"wrote submission decision audit to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
