#!/usr/bin/env python
"""Validate pre-specified human/native-review acceptance rules."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED = {
    "human_audit_v02_gpt41_family": {
        "review_type": "human_audit_completed_labels",
        "expected_rows": "72",
        "min_qualified_reviewers": "3",
        "min_pass_agreements": "65",
        "min_component_agreements": "306",
        "min_release_usable_rows": "",
        "expected_models": "gpt-4.1,gpt-4.1-mini,gpt-4.1-nano",
    },
    "human_audit_v02_current_gpt5": {
        "review_type": "human_audit_completed_labels",
        "expected_rows": "48",
        "min_qualified_reviewers": "3",
        "min_pass_agreements": "44",
        "min_component_agreements": "204",
        "min_release_usable_rows": "",
        "expected_models": "gpt-5.4-mini,gpt-5.5",
    },
    "coverage_native_review_v03": {
        "review_type": "native_review_scaffold_release",
        "expected_rows": "60",
        "min_qualified_reviewers": "6",
        "min_pass_agreements": "",
        "min_component_agreements": "",
        "min_release_usable_rows": "60",
        "expected_models": "",
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing acceptance rules CSV {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_csv(path: Path) -> None:
    rows = {row["surface"]: row for row in load_csv(path)}
    require(set(rows) == set(EXPECTED), f"unexpected acceptance-rule surfaces: {sorted(rows)}")
    for surface, expected in EXPECTED.items():
        row = rows[surface]
        for field in (
            "review_type",
            "expected_rows",
            "min_qualified_reviewers",
            "min_pass_agreements",
            "min_component_agreements",
            "min_release_usable_rows",
        ):
            require(row[field] == expected[field], f"{surface} mismatch for {field}: expected {expected[field]}, got {row[field]}")
        if expected["expected_models"]:
            require(expected["expected_models"] in row["completion_validator"], f"{surface} validator missing expected models")
        require("validate_completed" in row["completion_validator"], f"{surface} missing completion validator command")
        require("summarize" in row["summary_command"], f"{surface} missing summary command")
        require(row["claim_if_pass"], f"{surface} missing pass claim boundary")
        require(row["claim_if_fail"], f"{surface} missing fail claim boundary")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing acceptance rules report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "Human/Native Review Acceptance Rules",
        "They are not completed human validation",
        "human_audit_v02_gpt41_family | 72 | 3",
        "human_audit_v02_current_gpt5 | 48 | 3",
        "coverage_native_review_v03 | 60 | 6",
        "human_audit_v02_gpt41_family | 65 | 306",
        "human_audit_v02_current_gpt5 | 44 | 204",
        "coverage_native_review_v03 | | | 60",
        "A smoke-completed file never unlocks a paper claim",
        "Passing validation alone is necessary but not sufficient",
        "Completed-label validation requires every failed component",
        "If human-audit agreement misses threshold",
    ]
    for phrase in required:
        require(phrase in normalized, f"acceptance rules report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=Path("results/tables/human_audit_acceptance_rules_v02/human_audit_acceptance_rules.csv"))
    parser.add_argument("--report", type=Path, default=Path("paper/human_audit_acceptance_rules_v02.md"))
    args = parser.parse_args()

    check_csv(args.csv)
    check_report(args.report)
    print("human/native-review acceptance rules validation passed")


if __name__ == "__main__":
    main()
