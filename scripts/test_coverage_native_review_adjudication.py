#!/usr/bin/env python
"""Regression tests for v0.3 coverage native-review adjudication."""

from __future__ import annotations

import csv
from copy import deepcopy
from pathlib import Path

from analyze_coverage_native_review_adjudication import validate_long_reviews
from finalize_coverage_native_review_adjudication import finalize_labels
from test_coverage_native_review_completion import require_raises


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def make_double_roster(launch_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for coverage_slice in sorted({row["coverage_slice"] for row in launch_rows}):
        first = next(row for row in launch_rows if row["coverage_slice"] == coverage_slice)
        for index in (1, 2):
            rows.append(
                {
                    "reviewer_id": f"{coverage_slice}_reviewer_{index}",
                    "coverage_slice": coverage_slice,
                    "language_pair": first["language_pair"],
                    "target_content_language": first["content_language"],
                    "can_validate_instruction_language": "TRUE",
                    "can_validate_target_language": "TRUE",
                    "can_validate_script": "TRUE",
                    "qualification_notes": "Fixture qualified reviewer.",
                    "conflict_of_interest": "FALSE",
                    "notes": "",
                }
            )
    return rows


def make_double_completed(launch_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for row in launch_rows:
        for index in (1, 2):
            out = dict(row)
            out.update(
                {
                    "reviewer_id": f"{row['coverage_slice']}_reviewer_{index}",
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


def main() -> None:
    launch_rows = read_csv(Path("data/coverage_native_review_v03/coverage_native_review_packet_v03.csv"))
    completed = make_double_completed(launch_rows)
    roster = make_double_roster(launch_rows)

    summary, by_slice, by_content_language, by_instruction_language, adjudication = validate_long_reviews(
        annotation_rows=completed,
        launch_rows=launch_rows,
        roster_rows=roster,
    )
    if summary["review_items"] != 60 or summary["annotation_rows"] != 120 or summary["reviewers"] != 12:
        raise AssertionError(f"unexpected double-review summary: {summary}")
    if len(by_slice) != 6 or len(by_content_language) != 4 or len(by_instruction_language) != 4:
        raise AssertionError("unexpected stratified agreement rows")
    if adjudication:
        raise AssertionError(f"perfect agreement should not create adjudication rows: {adjudication}")

    final_rows, source_rows = finalize_labels(
        annotation_rows=completed,
        launch_rows=launch_rows,
        roster_rows=roster,
        adjudication_rows_input=[],
    )
    if len(final_rows) != 60:
        raise AssertionError(f"unexpected finalized row count: {len(final_rows)}")
    if {row["final_label_source"] for row in source_rows} != {"consensus"}:
        raise AssertionError(f"unexpected source rows: {source_rows[:3]}")

    disagreement = deepcopy(completed)
    disagreement[1]["reviewer_prompt_clear"] = "FALSE"
    disagreement[1]["reviewer_release_usable"] = "FALSE"
    disagreement[1]["reviewer_issue_types"] = "ambiguous_instruction"
    disagreement[1]["reviewer_notes"] = "Fixture prompt clarity issue."
    *_, disagreement_packet = validate_long_reviews(
        annotation_rows=disagreement,
        launch_rows=launch_rows,
        roster_rows=roster,
    )
    if len(disagreement_packet) != 1:
        raise AssertionError(f"unexpected adjudication packet: {disagreement_packet}")
    disagreed = set(disagreement_packet[0]["disagreed_components"].split(";"))
    if disagreed != {"prompt_clear", "release_usable", "issue_types"}:
        raise AssertionError(f"unexpected disagreed components: {disagreed}")
    require_raises(
        lambda: finalize_labels(
            annotation_rows=disagreement,
            launch_rows=launch_rows,
            roster_rows=roster,
            adjudication_rows_input=[],
        ),
        "completed adjudication IDs must equal required disagreement IDs",
    )

    completed_adjudication = [dict(disagreement_packet[0])]
    completed_adjudication[0].update(
        {
            "adjudicator_id": disagreement[0]["reviewer_id"],
            "adjudicated_prompt_clear": "TRUE",
            "adjudicated_target_language_natural": "TRUE",
            "adjudicated_script_expectation_valid": "TRUE",
            "adjudicated_preservation_spans_valid": "TRUE",
            "adjudicated_known_bad_outputs_valid": "TRUE",
            "adjudicated_release_usable": "TRUE",
            "adjudicated_issue_types": "",
            "adjudication_notes": "Final label follows reviewer 1.",
        }
    )
    adjudicated_final, adjudicated_sources = finalize_labels(
        annotation_rows=disagreement,
        launch_rows=launch_rows,
        roster_rows=roster,
        adjudication_rows_input=completed_adjudication,
    )
    source_by_id = {row["review_id"]: row for row in adjudicated_sources}
    if source_by_id["rpt_v03_native_001"]["final_label_source"] != "adjudicated":
        raise AssertionError(f"expected adjudicated source row: {source_by_id['rpt_v03_native_001']}")
    final_by_id = {row["review_id"]: row for row in adjudicated_final}
    final_row = final_by_id["rpt_v03_native_001"]
    if final_row["reviewer_release_usable"] != "TRUE" or not final_row["reviewer_notes"].startswith("ADJUDICATED"):
        raise AssertionError(f"unexpected adjudicated final label: {final_row}")

    single_reviewer = [row for row in completed if row["reviewer_id"].endswith("_1")]
    require_raises(
        lambda: validate_long_reviews(annotation_rows=single_reviewer, launch_rows=launch_rows, roster_rows=roster),
        "fewer than 2 reviews",
    )
    duplicate_reviewer = deepcopy(completed)
    duplicate_reviewer[1]["reviewer_id"] = duplicate_reviewer[0]["reviewer_id"]
    require_raises(
        lambda: validate_long_reviews(annotation_rows=duplicate_reviewer, launch_rows=launch_rows, roster_rows=roster),
        "duplicate review",
    )

    print("coverage native-review adjudication regression tests passed")


if __name__ == "__main__":
    main()
