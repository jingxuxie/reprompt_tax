#!/usr/bin/env python
"""Validate the reviewer-concern audit artifact."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


EXPECTED_IDS = {
    "current_model_timeliness": "covered",
    "lower_cost_model_boundary": "covered_with_boundary",
    "synthetic_scope": "covered_with_boundary",
    "scorer_validity": "covered_with_boundary",
    "human_native_validation": "external_label_blocker",
    "mechanism_vs_prompt_engineering": "covered_with_boundary",
    "coverage_expansion_v03": "diagnostic_only",
    "statistical_robustness": "covered",
    "token_cost_interpretation": "covered_with_boundary",
    "real_world_motivation_privacy": "covered_with_boundary",
}

EXPECTED_SUMMARY = {
    "covered": 2,
    "covered_with_boundary": 6,
    "diagnostic_only": 1,
    "external_label_blocker": 1,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing reviewer-concern table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_rows(path: Path) -> list[dict[str, str]]:
    rows = read_csv(path)
    require(len(rows) == len(EXPECTED_IDS), f"expected {len(EXPECTED_IDS)} concerns, found {len(rows)}")
    by_id = {row["concern_id"]: row for row in rows}
    require(set(by_id) == set(EXPECTED_IDS), f"unexpected concern IDs: {sorted(by_id)}")
    for concern_id, readiness in EXPECTED_IDS.items():
        row = by_id[concern_id]
        require(row["readiness"] == readiness, f"{concern_id} readiness mismatch: {row['readiness']}")
        require(row["paper_claim_use"], f"{concern_id} missing paper_claim_use")
        require(row["key_answer"], f"{concern_id} missing key_answer")
        require(row["next_action"], f"{concern_id} missing next_action")
        for field in ("evidence", "validators"):
            paths = [item.strip() for item in row[field].split(";") if item.strip()]
            require(paths, f"{concern_id} has no {field} paths")
            for path_text in paths:
                require(Path(path_text).exists(), f"{concern_id} missing {field} path {path_text}")
    human_row = by_id["human_native_validation"]
    require("Do not claim completed human/native validation" in human_row["paper_claim_use"], "human/native row must keep no-claim boundary")
    require("completed qualified labels are absent" in human_row["key_answer"], "human/native row must name missing completed labels")
    scorer_row = by_id["scorer_validity"]
    require("390/390" in scorer_row["key_answer"], "scorer row missing known-bad count")
    require("120/120" in scorer_row["key_answer"], "scorer row missing positive-control count")
    return rows


def check_summary(path: Path, rows: list[dict[str, str]]) -> None:
    summary_rows = read_csv(path)
    observed = {row["readiness"]: int(row["concern_count"]) for row in summary_rows}
    require(observed == EXPECTED_SUMMARY, f"summary counts mismatch: {observed}")
    row_counts = Counter(row["readiness"] for row in rows)
    require(dict(row_counts) == EXPECTED_SUMMARY, f"row readiness counts mismatch: {row_counts}")


def check_markdown(path: Path) -> None:
    require(path.exists(), f"missing reviewer-concern report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required_phrases = [
        "Reviewer Concern Audit",
        "no-API audit",
        "Reviewer concerns audited: 10",
        "Covered concerns: 2",
        "Covered with explicit boundary: 6",
        "Diagnostic-only concerns: 1",
        "External label blockers: 1",
        "OpenAI API calls: 0",
        "native/near-native validation is launch-ready but not completed",
        "current_model_timeliness",
        "scorer_validity",
        "human_native_validation",
        "coverage_expansion_v03",
        "token_cost_interpretation",
        "completed qualified human/native labels are still missing",
        "completed-label gates",
    ]
    for phrase in required_phrases:
        require(phrase in normalized, f"reviewer-concern report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/reviewer_concern_audit_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/reviewer_concern_audit_v02.md"))
    args = parser.parse_args()

    rows = check_rows(args.out_dir / "reviewer_concern_audit.csv")
    check_summary(args.out_dir / "reviewer_concern_summary.csv", rows)
    check_markdown(args.report)
    print("reviewer concern audit validation passed")


if __name__ == "__main__":
    main()
