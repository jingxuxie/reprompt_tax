#!/usr/bin/env python
"""Validate the submission decision audit artifact."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_DECISIONS = {
    "submit_now_if_no_labels": "ready_with_external_label_blocker",
    "main_headline": "paper_facing_ready",
    "human_native_upgrade": "external_labels_required",
    "coverage_v03_boundary": "diagnostic_only_until_native_review",
    "api_budget_posture": "no_api_next_step",
}

EXPECTED_SUMMARY = {
    "paper_facing_complete_items": "8",
    "supporting_complete_items": "3",
    "launch_ready_label_surfaces": "3",
    "reviewer_concerns_audited": "10",
    "reviewer_concerns_answered_or_bounded": "9",
    "external_label_blockers": "1",
    "completed_label_gates_needing_labels": "3",
    "priority_first_surface": "current_model_human_audit_v02",
    "priority_first_rows": "48",
    "openai_api_calls": "0",
    "submission_decision": "submit_with_conservative_claims_if_labels_are_unavailable",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing submission-decision table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    require(rows, f"empty submission-decision table {path}")
    return rows


def check_decisions(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == len(EXPECTED_DECISIONS), f"unexpected decision row count: {len(rows)}")
    by_id = {row["decision_id"]: row for row in rows}
    require(set(by_id) == set(EXPECTED_DECISIONS), f"unexpected decision IDs: {sorted(by_id)}")
    for decision_id, status in EXPECTED_DECISIONS.items():
        row = by_id[decision_id]
        require(row["status"] == status, f"{decision_id} status mismatch: {row['status']}")
        require(row["decision"], f"{decision_id} missing decision")
        require(row["paper_use_now"], f"{decision_id} missing paper_use_now")
        require(row["evidence_signal"], f"{decision_id} missing evidence_signal")
        require(row["claim_boundary"], f"{decision_id} missing claim_boundary")
        require(row["next_action"], f"{decision_id} missing next_action")
        paths = [item.strip() for item in row["evidence"].split(";") if item.strip()]
        require(paths, f"{decision_id} missing evidence paths")
        for path_text in paths:
            require(Path(path_text).exists(), f"{decision_id} missing evidence path {path_text}")
    require("Do not claim completed native/near-native validation" in by_id["submit_now_if_no_labels"]["claim_boundary"], "submit decision must preserve native-validation boundary")
    require("81.7% to 98.3% FTGA" in by_id["main_headline"]["paper_use_now"], "headline row missing GPT-5.5 headline")
    require("48 current-model audit rows first" in by_id["human_native_upgrade"]["next_action"], "human-upgrade row missing first label priority")
    require("Do not treat v0.3 as paper-facing benchmark evidence" in by_id["coverage_v03_boundary"]["claim_boundary"], "v0.3 row missing benchmark-evidence boundary")
    require("OpenAI API calls for this audit: 0" in by_id["api_budget_posture"]["evidence_signal"], "API posture row must record zero calls")


def check_summary(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == 1, f"expected one summary row, found {len(rows)}")
    row = rows[0]
    for field, expected in EXPECTED_SUMMARY.items():
        require(row.get(field) == expected, f"summary {field} mismatch: expected {expected}, got {row.get(field)}")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing submission-decision report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "Submission Decision Audit",
        "no-API audit",
        "not completed human/native validation",
        "Paper-facing complete items: 8",
        "Supporting complete diagnostics: 3",
        "Launch-ready label surfaces still needing labels: 3",
        "Reviewer concerns audited: 10",
        "Reviewer concerns answered or bounded: 9",
        "External label blockers: 1",
        "Completed-label gates still needing labels: 3",
        "First label priority: `current_model_human_audit_v02` (48 rows)",
        "OpenAI API calls: 0",
        "submit with conservative claims if labels are unavailable",
        "upgrade only after completed labels pass gates",
        "submit_now_if_no_labels",
        "human_native_upgrade",
        "coverage_v03_boundary",
        "do_not_spend_more_api_before_labels",
        "completed native/near-native validation is not",
        "collect the 48-row current-model human/native audit first",
    ]
    for phrase in required:
        require(phrase in normalized, f"submission-decision report missing phrase: {phrase}")


def check_source_gate(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == 3, f"expected three completed-label gates, found {len(rows)}")
    require(all(row["status"] == "needs_labels" for row in rows), "completed-label gate unexpectedly does not need labels")
    require(all(row["claim_decision"] == "no_claim" for row in rows), "completed-label gate unexpectedly unlocks a claim")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/submission_decision_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/submission_decision_v02.md"))
    args = parser.parse_args()

    check_decisions(args.out_dir / "submission_decision.csv")
    check_summary(args.out_dir / "submission_decision_summary.csv")
    check_report(args.report)
    check_source_gate(Path("results/tables/completed_label_claim_gates_v02/completed_label_claim_gates.csv"))
    print("submission decision audit validation passed")


if __name__ == "__main__":
    main()
