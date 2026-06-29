#!/usr/bin/env python
"""Regression tests for completed v0.3 coverage native-review validation."""

from __future__ import annotations

import csv
from copy import deepcopy
from pathlib import Path

from summarize_coverage_native_review_v03 import issue_type_rows, nonusable_rows, summarize_by
from validate_completed_coverage_native_review_v03 import validate_completed_reviews


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def make_roster(launch_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for coverage_slice in sorted({row["coverage_slice"] for row in launch_rows}):
        rows.append(
            {
                "reviewer_id": f"{coverage_slice}_reviewer",
                "coverage_slice": coverage_slice,
                "language_pair": next(row["language_pair"] for row in launch_rows if row["coverage_slice"] == coverage_slice),
                "target_content_language": next(row["content_language"] for row in launch_rows if row["coverage_slice"] == coverage_slice),
                "can_validate_instruction_language": "TRUE",
                "can_validate_target_language": "TRUE",
                "can_validate_script": "TRUE",
                "qualification_notes": "Fixture qualified reviewer.",
                "conflict_of_interest": "FALSE",
                "notes": "",
            }
        )
    return rows


def make_completed(launch_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for row in launch_rows:
        out = dict(row)
        out.update(
            {
                "reviewer_id": f"{row['coverage_slice']}_reviewer",
                "reviewer_prompt_clear": "TRUE",
                "reviewer_target_language_natural": "TRUE",
                "reviewer_script_expectation_valid": "TRUE",
                "reviewer_preservation_spans_valid": "TRUE",
                "reviewer_known_bad_outputs_valid": "TRUE",
                "reviewer_release_usable": "TRUE",
                "reviewer_issue_types": "",
                "reviewer_notes": "",
            }
        )
        rows.append(out)
    return rows


def require_raises(fn, expected_fragment: str) -> None:
    try:
        fn()
    except AssertionError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected error containing {expected_fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected AssertionError containing {expected_fragment!r}")


def main() -> None:
    launch_rows = read_csv(Path("data/coverage_native_review_v03/coverage_native_review_packet_v03.csv"))
    completed = make_completed(launch_rows)
    roster = make_roster(launch_rows)

    summary = validate_completed_reviews(annotation_rows=completed, launch_rows=launch_rows, roster_rows=roster)
    if summary["rows"] != 60 or summary["release_usable"] != 60 or summary["reviewers"] != 6:
        raise AssertionError(f"unexpected completed-review summary: {summary}")

    placeholder_roster = deepcopy(roster)
    placeholder_roster[0]["reviewer_id"] = "replace_with_reviewer_id"
    require_raises(
        lambda: validate_completed_reviews(annotation_rows=completed, launch_rows=launch_rows, roster_rows=placeholder_roster),
        "placeholder reviewer_id",
    )

    wrong_reviewer = deepcopy(completed)
    wrong_reviewer[0]["reviewer_id"] = roster[-1]["reviewer_id"]
    require_raises(
        lambda: validate_completed_reviews(annotation_rows=wrong_reviewer, launch_rows=launch_rows, roster_rows=roster),
        "is not assigned",
    )

    missing_issue = deepcopy(completed)
    missing_issue[0]["reviewer_target_language_natural"] = "FALSE"
    missing_issue[0]["reviewer_release_usable"] = "FALSE"
    require_raises(
        lambda: validate_completed_reviews(annotation_rows=missing_issue, launch_rows=launch_rows, roster_rows=roster),
        "has no issue types",
    )

    missing_component_issue = deepcopy(missing_issue)
    missing_component_issue[0]["reviewer_issue_types"] = "other"
    missing_component_issue[0]["reviewer_notes"] = "Fixture issue row."
    require_raises(
        lambda: validate_completed_reviews(annotation_rows=missing_component_issue, launch_rows=launch_rows, roster_rows=roster),
        "missing unnatural_target_text",
    )

    contradictory_component_issue = deepcopy(missing_issue)
    contradictory_component_issue[0]["reviewer_issue_types"] = "unnatural_target_text,script_expectation_problem"
    require_raises(
        lambda: validate_completed_reviews(annotation_rows=contradictory_component_issue, launch_rows=launch_rows, roster_rows=roster),
        "lists script_expectation_problem but reviewer_script_expectation_valid is TRUE",
    )

    json_issue = deepcopy(completed)
    json_issue[0]["reviewer_target_language_natural"] = "FALSE"
    json_issue[0]["reviewer_release_usable"] = "FALSE"
    json_issue[0]["reviewer_issue_types"] = '["unnatural_target_text", "cultural_or_locale_issue"]'
    json_issue[0]["reviewer_notes"] = "Fixture issue row."
    json_summary = validate_completed_reviews(annotation_rows=json_issue, launch_rows=launch_rows, roster_rows=roster)
    if json_summary["release_usable"] != 59 or json_summary["issue_rows"] != 1:
        raise AssertionError(f"unexpected JSON issue validation summary: {json_summary}")
    overall = summarize_by(json_issue, tuple())[0]
    if overall["n"] != 60 or overall["release_usable_n"] != 59 or overall["issue_rows"] != 1:
        raise AssertionError(f"unexpected coverage summary row: {overall}")
    issues = {row["reviewer_issue_type"]: row["rows_with_type"] for row in issue_type_rows(json_issue)}
    if issues != {"cultural_or_locale_issue": 1, "unnatural_target_text": 1}:
        raise AssertionError(f"unexpected JSON issue type summary: {issues}")
    nonusable = nonusable_rows(json_issue)
    if len(nonusable) != 1 or nonusable[0]["review_id"] != json_issue[0]["review_id"]:
        raise AssertionError(f"unexpected nonusable row summary: {nonusable}")

    print("coverage native-review completion regression tests passed")


if __name__ == "__main__":
    main()
