#!/usr/bin/env python
"""Regression tests for completed-label claim gates."""

from __future__ import annotations

import csv
from pathlib import Path
from tempfile import TemporaryDirectory

import analyze_completed_label_claim_gates as gates
from test_coverage_native_review_completion import make_completed as make_coverage_completed
from test_coverage_native_review_completion import make_roster as make_coverage_roster
from test_human_audit_completion import fixture_rows, roster_rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_missing_labels() -> None:
    surface = dict(gates.SURFACES[0])
    surface["annotations"] = Path("/tmp/reprompt_tax_missing_annotations.csv")
    surface["roster"] = Path("/tmp/reprompt_tax_missing_roster.csv")
    row = gates.evaluate_human_surface(surface)
    require(row["status"] == "needs_labels", f"unexpected missing-label status: {row}")
    require(row["claim_decision"] == "no_claim", f"missing labels should not unlock claims: {row}")


def test_human_claim_ready(tmp: Path) -> None:
    annotations, key_rows = fixture_rows()
    surface = dict(gates.SURFACES[0])
    surface["annotations"] = tmp / "human_completed.csv"
    surface["answer_key"] = tmp / "human_answer_key.csv"
    surface["roster"] = tmp / "human_roster.csv"
    write_csv(surface["annotations"], annotations)
    write_csv(surface["answer_key"], key_rows)
    write_csv(surface["roster"], roster_rows())
    row = gates.evaluate_human_surface(surface)
    require(row["status"] == "claim_ready", f"expected human claim-ready status: {row}")
    require(row["pass_agreements"] == 72, f"unexpected human pass agreements: {row}")
    require(row["component_agreements"] == 360, f"unexpected human component agreements: {row}")


def test_coverage_claim_blocked(tmp: Path) -> None:
    launch_rows = gates.read_coverage_csv(Path("data/coverage_native_review_v03/coverage_native_review_packet_v03.csv"))
    annotations = make_coverage_completed(launch_rows)
    annotations[0]["reviewer_target_language_natural"] = "FALSE"
    annotations[0]["reviewer_release_usable"] = "FALSE"
    annotations[0]["reviewer_issue_types"] = "unnatural_target_text"
    annotations[0]["reviewer_notes"] = "Fixture non-usable row."

    surface = dict(gates.SURFACES[2])
    surface["annotations"] = tmp / "coverage_completed.csv"
    surface["launch_packet"] = tmp / "coverage_launch.csv"
    surface["roster"] = tmp / "coverage_roster.csv"
    write_csv(surface["annotations"], annotations)
    write_csv(surface["launch_packet"], launch_rows)
    write_csv(surface["roster"], make_coverage_roster(launch_rows))
    row = gates.evaluate_coverage_surface(surface)
    require(row["status"] == "claim_blocked", f"expected coverage claim-blocked status: {row}")
    require(row["release_usable_rows"] == 59, f"unexpected coverage release usable count: {row}")
    require("not all rows are release usable" in row["required_action"], f"unexpected coverage action: {row}")


def main() -> None:
    test_missing_labels()
    with TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        test_human_claim_ready(tmp / "human")
        test_coverage_claim_blocked(tmp / "coverage")
    print("completed-label claim-gate regression tests passed")


if __name__ == "__main__":
    main()
