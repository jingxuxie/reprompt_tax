#!/usr/bin/env python
"""Regression tests for reviewer-export merge tooling."""

from __future__ import annotations

import csv
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from merge_review_exports import merge_exports, read_csv_with_fields
from validate_completed_coverage_native_review_v03 import validate_completed_reviews
from validate_completed_human_audit import validate_annotations


HUMAN_ANNOTATORS = {
    "ar-en": "ar_native_1",
    "es-en": "es_native_1",
    "hi-en": "hi_native_1",
}


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def require_raises(fn, expected_fragment: str) -> None:
    try:
        fn()
    except AssertionError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected error containing {expected_fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected AssertionError containing {expected_fragment!r}")


def human_roster_rows() -> list[dict[str, str]]:
    return [
        {
            "annotator_id": "ar_native_1",
            "language_pair": "ar-en",
            "native_or_near_native": "TRUE",
            "can_validate_script": "TRUE",
            "qualification_notes": "Fixture qualified Arabic reviewer.",
            "conflict_of_interest": "FALSE",
            "notes": "",
        },
        {
            "annotator_id": "es_native_1",
            "language_pair": "es-en",
            "native_or_near_native": "TRUE",
            "can_validate_script": "TRUE",
            "qualification_notes": "Fixture qualified Spanish reviewer.",
            "conflict_of_interest": "FALSE",
            "notes": "",
        },
        {
            "annotator_id": "hi_native_1",
            "language_pair": "hi-en",
            "native_or_near_native": "TRUE",
            "can_validate_script": "TRUE",
            "qualification_notes": "Fixture qualified Hindi reviewer.",
            "conflict_of_interest": "FALSE",
            "notes": "",
        },
    ]


def completed_human_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out = []
    for row in rows:
        completed = dict(row)
        completed.update(
            {
                "annotator_id": HUMAN_ANNOTATORS[row["language_pair"]],
                "human_pass": "TRUE",
                "human_language_pass": "TRUE",
                "human_script_pass": "TRUE",
                "human_preservation_pass": "TRUE",
                "human_task_pass": "TRUE",
                "human_register_locale_pass": "TRUE",
                "human_failure_types": "",
                "human_notes": "",
            }
        )
        out.append(completed)
    return out


def coverage_roster_rows(launch_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for coverage_slice in sorted({row["coverage_slice"] for row in launch_rows}):
        representative = next(row for row in launch_rows if row["coverage_slice"] == coverage_slice)
        rows.append(
            {
                "reviewer_id": f"{coverage_slice}_reviewer",
                "coverage_slice": coverage_slice,
                "can_validate_instruction_language": "TRUE",
                "can_validate_target_language": "TRUE",
                "can_validate_script": "TRUE",
                "qualification_notes": "Fixture qualified coverage reviewer.",
                "conflict_of_interest": "FALSE",
                "language_pair": representative["language_pair"],
                "target_content_language": representative["content_language"],
                "notes": "",
            }
        )
    return rows


def completed_coverage_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out = []
    for row in rows:
        completed = dict(row)
        completed.update(
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
        out.append(completed)
    return out


def test_human_merge(tmp: Path) -> None:
    launch_fields, launch_rows = read_csv_with_fields(Path("data/human_audit/human_audit_packet_v0.2.csv"))
    _, key_rows = read_csv_with_fields(Path("data/human_audit/human_audit_answer_key_v0.2.csv"))
    batches = []
    for language_pair in sorted(HUMAN_ANNOTATORS):
        rows = completed_human_rows([row for row in launch_rows if row["language_pair"] == language_pair])
        path = tmp / f"{language_pair}.csv"
        write_csv(path, rows, launch_fields)
        batches.append((path, launch_fields, rows))
    merged = merge_exports(
        mode="human_audit",
        launch_rows=launch_rows,
        launch_fields=launch_fields,
        export_batches=batches,
        labels_per_item=1,
    )
    require(len(merged) == len(launch_rows), "human merge row count mismatch")
    require([row["audit_id"] for row in merged] == [row["audit_id"] for row in launch_rows], "human merge order mismatch")
    summary = validate_annotations(
        annotation_rows=merged,
        key_rows=key_rows,
        roster_rows=human_roster_rows(),
        allow_smoke=False,
    )
    require(summary["rows"] == 72 and summary["annotators"] == 3, f"unexpected human validation summary: {summary}")

    bad_reason = deepcopy(batches)
    bad_rows = deepcopy(bad_reason[0][2])
    bad_rows[0]["human_pass"] = "FALSE"
    bad_rows[0]["human_language_pass"] = "FALSE"
    bad_rows[0]["human_failure_types"] = "other"
    bad_rows[0]["human_notes"] = "Fixture reason."
    bad_reason[0] = (bad_reason[0][0], bad_reason[0][1], bad_rows)
    require_raises(
        lambda: merge_exports(
            mode="human_audit",
            launch_rows=launch_rows,
            launch_fields=launch_fields,
            export_batches=bad_reason,
            labels_per_item=1,
        ),
        "missing wrong_output_language",
    )


def test_coverage_merge(tmp: Path) -> None:
    launch_fields, launch_rows = read_csv_with_fields(Path("data/coverage_native_review_v03/coverage_native_review_packet_v03.csv"))
    batches = []
    for coverage_slice in sorted({row["coverage_slice"] for row in launch_rows}):
        rows = completed_coverage_rows([row for row in launch_rows if row["coverage_slice"] == coverage_slice])
        path = tmp / f"{coverage_slice}.csv"
        write_csv(path, rows, launch_fields)
        batches.append((path, launch_fields, rows))
    merged = merge_exports(
        mode="coverage_native_review",
        launch_rows=launch_rows,
        launch_fields=launch_fields,
        export_batches=batches,
        labels_per_item=1,
    )
    require(len(merged) == len(launch_rows), "coverage merge row count mismatch")
    summary = validate_completed_reviews(
        annotation_rows=merged,
        launch_rows=launch_rows,
        roster_rows=coverage_roster_rows(launch_rows),
    )
    require(summary["rows"] == 60 and summary["reviewers"] == 6, f"unexpected coverage validation summary: {summary}")

    bad_static = deepcopy(batches)
    bad_rows = deepcopy(bad_static[0][2])
    bad_rows[0]["user_prompt"] = "edited prompt should be rejected"
    bad_static[0] = (bad_static[0][0], bad_static[0][1], bad_rows)
    require_raises(
        lambda: merge_exports(
            mode="coverage_native_review",
            launch_rows=launch_rows,
            launch_fields=launch_fields,
            export_batches=bad_static,
            labels_per_item=1,
        ),
        "changed static field user_prompt",
    )


def main() -> None:
    with TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        test_human_merge(tmp / "human")
        test_coverage_merge(tmp / "coverage")
    print("review-export merge regression tests passed")


if __name__ == "__main__":
    main()
