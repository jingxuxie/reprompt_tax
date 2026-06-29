#!/usr/bin/env python
"""Validate completed v0.3 coverage native-review annotations."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


EXPECTED_SLICES = {
    "arabic_instruction_arabic_filenames",
    "english_instruction_arabic_content",
    "english_instruction_hindi_content",
    "english_instruction_spanish_content",
    "hindi_english_instruction_hindi_devanagari",
    "spanish_instruction_arabic_quote",
}

BOOLEAN_FIELDS = (
    "reviewer_prompt_clear",
    "reviewer_target_language_natural",
    "reviewer_script_expectation_valid",
    "reviewer_preservation_spans_valid",
    "reviewer_known_bad_outputs_valid",
    "reviewer_release_usable",
)

COMPONENT_FIELDS = tuple(field for field in BOOLEAN_FIELDS if field != "reviewer_release_usable")

ISSUE_TYPES = {
    "ambiguous_instruction",
    "unnatural_target_text",
    "wrong_expected_language",
    "script_expectation_problem",
    "preservation_span_problem",
    "known_bad_output_problem",
    "privacy_or_safety_issue",
    "cultural_or_locale_issue",
    "other",
}

COMPONENT_ISSUE_TYPES = {
    "reviewer_prompt_clear": "ambiguous_instruction",
    "reviewer_target_language_natural": "unnatural_target_text",
    "reviewer_script_expectation_valid": "script_expectation_problem",
    "reviewer_preservation_spans_valid": "preservation_span_problem",
    "reviewer_known_bad_outputs_valid": "known_bad_output_problem",
}

ROSTER_FIELDS = (
    "reviewer_id",
    "coverage_slice",
    "can_validate_instruction_language",
    "can_validate_target_language",
    "can_validate_script",
    "qualification_notes",
    "conflict_of_interest",
)

STATIC_FIELDS = (
    "review_id",
    "item_id",
    "coverage_slice",
    "language_pair",
    "instruction_language",
    "content_language",
    "task_family",
    "user_prompt",
    "expected_response_language",
    "expected_script",
    "must_preserve_spans",
    "required_any_markers",
    "forbidden_markers",
    "known_bad_outputs",
    "register_requirement",
    "locale_requirement",
    "notes_for_reviewers",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def parse_bool(value: Any, *, row_id: str, field: str) -> bool:
    text = str(value).strip().lower()
    if text in {"1", "true", "t", "yes", "y", "pass", "passed"}:
        return True
    if text in {"0", "false", "f", "no", "n", "fail", "failed"}:
        return False
    raise AssertionError(f"{row_id} field {field} must be a completed boolean, got {value!r}")


def parse_issue_types(value: str, *, row_id: str) -> list[str]:
    text = value.strip()
    if not text:
        return []
    if text.startswith("["):
        parsed = json.loads(text)
        require(isinstance(parsed, list), f"{row_id} reviewer_issue_types JSON must be a list")
        items = [str(item).strip() for item in parsed if str(item).strip()]
    else:
        items = [item.strip() for item in text.split(",") if item.strip()]
    unknown = sorted(set(items) - ISSUE_TYPES)
    require(not unknown, f"{row_id} has unknown reviewer_issue_types: {unknown}")
    return items


def validate_roster(roster_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    require(roster_rows, "v0.3 native-review roster is empty")
    fields = set(roster_rows[0])
    missing = [field for field in ROSTER_FIELDS if field not in fields]
    require(not missing, f"v0.3 native-review roster missing fields: {missing}")
    by_id: dict[str, dict[str, str]] = {}
    for row in roster_rows:
        reviewer_id = row["reviewer_id"].strip()
        require(reviewer_id, "v0.3 native-review roster has blank reviewer_id")
        require(not reviewer_id.startswith("replace_with_"), f"roster still contains placeholder reviewer_id {reviewer_id}")
        require(reviewer_id not in by_id, f"duplicate reviewer_id in roster: {reviewer_id}")
        coverage_slice = row["coverage_slice"].strip()
        require(coverage_slice in EXPECTED_SLICES, f"{reviewer_id} has unsupported coverage_slice {coverage_slice!r}")
        target = parse_bool(row["can_validate_target_language"], row_id=reviewer_id, field="can_validate_target_language")
        script = parse_bool(row["can_validate_script"], row_id=reviewer_id, field="can_validate_script")
        parse_bool(row["can_validate_instruction_language"], row_id=reviewer_id, field="can_validate_instruction_language")
        conflict = parse_bool(row["conflict_of_interest"], row_id=reviewer_id, field="conflict_of_interest")
        require(target, f"{reviewer_id} is not marked can_validate_target_language")
        require(script, f"{reviewer_id} is not marked can_validate_script")
        require(not conflict, f"{reviewer_id} is marked conflict_of_interest")
        require(row["qualification_notes"].strip(), f"{reviewer_id} missing qualification_notes")
        by_id[reviewer_id] = row
    return by_id


def validate_completed_reviews(
    *,
    annotation_rows: list[dict[str, str]],
    launch_rows: list[dict[str, str]],
    roster_rows: list[dict[str, str]],
) -> dict[str, Any]:
    require(len(annotation_rows) == 60, f"expected 60 completed v0.3 review rows, found {len(annotation_rows)}")
    require(len(launch_rows) == 60, f"expected 60 v0.3 launch rows, found {len(launch_rows)}")
    require(annotation_rows, "completed v0.3 review file is empty")

    launch_by_id = {row["review_id"]: row for row in launch_rows}
    review_ids = [row["review_id"] for row in annotation_rows]
    require(len(review_ids) == len(set(review_ids)), "duplicate review_id values in completed v0.3 review")
    require(set(review_ids) == set(launch_by_id), "completed v0.3 review IDs do not match launch packet")

    roster_by_id = validate_roster(roster_rows)
    release_usable = 0
    issue_rows = 0
    reviewer_ids: set[str] = set()

    for row in annotation_rows:
        row_id = row["review_id"]
        launch = launch_by_id[row_id]
        for field in STATIC_FIELDS:
            require(row.get(field, "") == launch.get(field, ""), f"{row_id} changed static launch field {field}")
        reviewer_id = row.get("reviewer_id", "").strip()
        require(reviewer_id, f"{row_id} missing reviewer_id")
        require(reviewer_id in roster_by_id, f"{row_id} reviewer_id {reviewer_id!r} is not in roster")
        require(roster_by_id[reviewer_id]["coverage_slice"] == row["coverage_slice"], f"{row_id} reviewer {reviewer_id} is not assigned to {row['coverage_slice']}")
        reviewer_ids.add(reviewer_id)

        values = {field: parse_bool(row.get(field), row_id=row_id, field=field) for field in BOOLEAN_FIELDS}
        expected_release = all(values[field] for field in COMPONENT_FIELDS)
        require(values["reviewer_release_usable"] == expected_release, f"{row_id} reviewer_release_usable must equal conjunction of component labels")
        issue_types = parse_issue_types(row.get("reviewer_issue_types", ""), row_id=row_id)
        if values["reviewer_release_usable"]:
            require(not issue_types, f"{row_id} is release-usable but lists issue types")
            release_usable += 1
        else:
            require(issue_types, f"{row_id} is not release-usable but has no issue types")
            issue_type_set = set(issue_types)
            for component_field, issue_type in COMPONENT_ISSUE_TYPES.items():
                if values[component_field]:
                    require(
                        issue_type not in issue_type_set,
                        f"{row_id} lists {issue_type} but {component_field} is TRUE",
                    )
                else:
                    require(
                        issue_type in issue_type_set,
                        f"{row_id} has {component_field}=FALSE but is missing {issue_type}",
                    )
            if "other" in issue_types:
                require(row.get("reviewer_notes", "").strip(), f"{row_id} uses other without reviewer_notes")
            issue_rows += 1

    counts = Counter(row["coverage_slice"] for row in annotation_rows)
    require(set(counts) == EXPECTED_SLICES, f"completed v0.3 review slices mismatch: {set(counts)}")
    require(all(count == 10 for count in counts.values()), f"completed v0.3 review slice counts mismatch: {counts}")
    return {
        "rows": len(annotation_rows),
        "reviewers": len(reviewer_ids),
        "release_usable": release_usable,
        "issue_rows": issue_rows,
        "release_usable_rate": release_usable / len(annotation_rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotations", type=Path, default=Path("data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv"))
    parser.add_argument("--launch-packet", type=Path, default=Path("data/coverage_native_review_v03/coverage_native_review_packet_v03.csv"))
    parser.add_argument("--reviewer-roster", type=Path, default=Path("data/coverage_native_review_v03/coverage_native_review_roster_v03.csv"))
    args = parser.parse_args()

    summary = validate_completed_reviews(
        annotation_rows=read_csv(args.annotations),
        launch_rows=read_csv(args.launch_packet),
        roster_rows=read_csv(args.reviewer_roster),
    )
    print(
        "completed v0.3 coverage native-review validation passed: "
        f"rows={summary['rows']}, "
        f"reviewers={summary['reviewers']}, "
        f"release_usable={summary['release_usable']}, "
        f"issue_rows={summary['issue_rows']}, "
        f"release_usable_rate={summary['release_usable_rate']:.3f}"
    )


if __name__ == "__main__":
    main()
