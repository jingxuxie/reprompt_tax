#!/usr/bin/env python
"""Finalize double-reviewed v0.3 native-review labels after adjudication."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

from analyze_coverage_native_review_adjudication import (
    ADJUDICATION_FIELDS,
    COMPONENTS,
    adjudication_rows,
    normalized_issue_types,
    parse_review_values,
    validate_long_reviews,
    validate_reviewer_assignment,
    write_csv,
)
from validate_completed_coverage_native_review_v03 import (
    BOOLEAN_FIELDS,
    COMPONENT_FIELDS,
    parse_bool,
    parse_issue_types,
    read_csv,
    require,
    validate_completed_reviews,
    validate_roster,
)


ADJUDICATED_COMPONENTS = {
    "adjudicated_prompt_clear": "reviewer_prompt_clear",
    "adjudicated_target_language_natural": "reviewer_target_language_natural",
    "adjudicated_script_expectation_valid": "reviewer_script_expectation_valid",
    "adjudicated_preservation_spans_valid": "reviewer_preservation_spans_valid",
    "adjudicated_known_bad_outputs_valid": "reviewer_known_bad_outputs_valid",
    "adjudicated_release_usable": "reviewer_release_usable",
}


def read_optional_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def bool_text(value: bool) -> str:
    return "TRUE" if value else "FALSE"


def validate_adjudication_row(
    row: dict[str, str],
    *,
    expected_row: dict[str, Any],
    roster_by_id: dict[str, dict[str, str]],
) -> dict[str, bool]:
    row_id = row["review_id"]
    for field in ("coverage_slice", "language_pair", "instruction_language", "content_language", "task_family"):
        require(row.get(field, "") == expected_row.get(field, ""), f"{row_id} adjudication mismatch for {field}")
    missing = [field for field in ADJUDICATION_FIELDS if field not in row]
    require(not missing, f"{row_id} adjudication row missing fields: {missing}")
    adjudicator_id = row["adjudicator_id"].strip()
    assignment_row = dict(expected_row)
    assignment_row["adjudicator_id"] = adjudicator_id
    validate_reviewer_assignment(assignment_row, roster_by_id=roster_by_id, reviewer_field="adjudicator_id")

    values = {
        reviewer_field: parse_bool(row.get(adjudicated_field), row_id=row_id, field=adjudicated_field)
        for adjudicated_field, reviewer_field in ADJUDICATED_COMPONENTS.items()
    }
    expected_release = all(values[field] for field in COMPONENT_FIELDS)
    require(
        values["reviewer_release_usable"] == expected_release,
        f"{row_id} adjudicated_release_usable must equal conjunction of adjudicated components",
    )
    issue_types = parse_issue_types(row.get("adjudicated_issue_types", ""), row_id=row_id)
    if values["reviewer_release_usable"]:
        require(not issue_types, f"{row_id} adjudicated release usable lists issue types")
    else:
        require(issue_types, f"{row_id} adjudicated non-usable row has no issue types")
        if "other" in issue_types:
            require(row.get("adjudication_notes", "").strip(), f"{row_id} uses other without adjudication_notes")
    return values


def finalize_labels(
    *,
    annotation_rows: list[dict[str, str]],
    launch_rows: list[dict[str, str]],
    roster_rows: list[dict[str, str]],
    adjudication_rows_input: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    _, _, _, _, expected_adjudication = validate_long_reviews(
        annotation_rows=annotation_rows,
        launch_rows=launch_rows,
        roster_rows=roster_rows,
    )
    expected_by_id = {row["review_id"]: row for row in expected_adjudication}
    adjudication_by_id = {row["review_id"]: row for row in adjudication_rows_input}
    require(len(adjudication_by_id) == len(adjudication_rows_input), "duplicate review_id values in adjudication packet")
    require(
        set(adjudication_by_id) == set(expected_by_id),
        f"completed adjudication IDs must equal required disagreement IDs: expected={sorted(expected_by_id)}, got={sorted(adjudication_by_id)}",
    )

    roster_by_id = validate_roster(roster_rows)
    rows_by_review: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in annotation_rows:
        rows_by_review[row["review_id"]].append(row)

    final_rows: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []
    for review_id, rows in sorted(rows_by_review.items()):
        first = dict(rows[0])
        source = {
            "review_id": review_id,
            "source_reviewer_ids": ";".join(row["reviewer_id"] for row in rows),
        }
        if review_id in adjudication_by_id:
            adjudication = adjudication_by_id[review_id]
            values = validate_adjudication_row(adjudication, expected_row=expected_by_id[review_id], roster_by_id=roster_by_id)
            first["reviewer_id"] = adjudication["adjudicator_id"].strip()
            for field in BOOLEAN_FIELDS:
                first[field] = bool_text(values[field])
            first["reviewer_issue_types"] = adjudication.get("adjudicated_issue_types", "")
            notes = adjudication.get("adjudication_notes", "").strip()
            first["reviewer_notes"] = f"ADJUDICATED: {notes}" if notes else "ADJUDICATED"
            source.update({"final_label_source": "adjudicated", "adjudicator_id": first["reviewer_id"]})
        else:
            values_by_field = {
                field: {parse_review_values(row)[field] for row in rows}
                for _, field in COMPONENTS
            }
            for field, values in values_by_field.items():
                require(len(values) == 1, f"{review_id} has unresolved component disagreement for {field}")
                first[field] = bool_text(next(iter(values)))
            issue_type_values = {normalized_issue_types(row) for row in rows}
            require(len(issue_type_values) == 1, f"{review_id} has unresolved issue-type disagreement")
            first["reviewer_issue_types"] = ",".join(next(iter(issue_type_values)))
            first["reviewer_notes"] = "CONSENSUS: " + ";".join(row["reviewer_id"] for row in rows)
            source.update({"final_label_source": "consensus", "adjudicator_id": ""})
        final_rows.append(first)
        source_rows.append(source)

    validate_completed_reviews(
        annotation_rows=final_rows,
        launch_rows=launch_rows,
        roster_rows=roster_rows,
    )
    return final_rows, source_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--launch-packet", type=Path, default=Path("data/coverage_native_review_v03/coverage_native_review_packet_v03.csv"))
    parser.add_argument("--reviewer-roster", type=Path, default=Path("data/coverage_native_review_v03/coverage_native_review_roster_v03.csv"))
    parser.add_argument("--adjudication", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("data/coverage_native_review_v03/coverage_native_review_packet_v03_adjudicated_completed.csv"))
    parser.add_argument(
        "--source-out",
        type=Path,
        default=Path("results/tables/coverage_native_review_v03_adjudication/coverage_native_review_final_label_sources.csv"),
    )
    args = parser.parse_args()

    final_rows, source_rows = finalize_labels(
        annotation_rows=read_csv(args.annotations),
        launch_rows=read_csv(args.launch_packet),
        roster_rows=read_csv(args.reviewer_roster),
        adjudication_rows_input=read_optional_csv(args.adjudication),
    )
    write_csv(args.out, final_rows)
    write_csv(args.source_out, source_rows)
    print(
        "finalized adjudicated v0.3 coverage native-review labels: "
        f"rows={len(final_rows)}, "
        f"adjudicated={sum(row['final_label_source'] == 'adjudicated' for row in source_rows)}, "
        f"consensus={sum(row['final_label_source'] == 'consensus' for row in source_rows)}"
    )


if __name__ == "__main__":
    main()
