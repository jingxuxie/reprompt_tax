#!/usr/bin/env python
"""Merge reviewer CSV exports into completed-label packets.

The static HTML review sheets export one CSV per language or coverage slice.
This script combines those exports into the exact one-row-per-item or
two-rows-per-item packet expected by the completed-label validators, while
checking that static launch fields were not edited and no rows are missing.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


HUMAN_FIELDS = (
    "annotator_id",
    "human_pass",
    "human_language_pass",
    "human_script_pass",
    "human_preservation_pass",
    "human_task_pass",
    "human_register_locale_pass",
    "human_failure_types",
    "human_notes",
)
HUMAN_BOOLEAN_FIELDS = (
    "human_pass",
    "human_language_pass",
    "human_script_pass",
    "human_preservation_pass",
    "human_task_pass",
    "human_register_locale_pass",
)
HUMAN_COMPONENT_FAILURE_TYPES = {
    "human_language_pass": "wrong_output_language",
    "human_script_pass": "script_mismatch",
    "human_preservation_pass": "preservation_failure",
    "human_task_pass": "task_noncompletion",
    "human_register_locale_pass": "register_locale_mismatch",
}
HUMAN_PRIVATE_FIELDS = {
    "item_id",
    "model",
    "condition",
    "turn",
    "auto_pass",
    "auto_language_pass",
    "auto_script_pass",
    "auto_preservation_pass",
    "auto_task_pass",
    "auto_register_locale_pass",
    "auto_failure_types",
}
HUMAN_FAILURE_TYPES = set(HUMAN_COMPONENT_FAILURE_TYPES.values()) | {"other"}

REVIEW_FIELDS = (
    "reviewer_id",
    "reviewer_prompt_clear",
    "reviewer_target_language_natural",
    "reviewer_script_expectation_valid",
    "reviewer_preservation_spans_valid",
    "reviewer_known_bad_outputs_valid",
    "reviewer_release_usable",
    "reviewer_issue_types",
    "reviewer_notes",
)
REVIEW_BOOLEAN_FIELDS = (
    "reviewer_prompt_clear",
    "reviewer_target_language_natural",
    "reviewer_script_expectation_valid",
    "reviewer_preservation_spans_valid",
    "reviewer_known_bad_outputs_valid",
    "reviewer_release_usable",
)
REVIEW_COMPONENT_ISSUE_TYPES = {
    "reviewer_prompt_clear": "ambiguous_instruction",
    "reviewer_target_language_natural": "unnatural_target_text",
    "reviewer_script_expectation_valid": "script_expectation_problem",
    "reviewer_preservation_spans_valid": "preservation_span_problem",
    "reviewer_known_bad_outputs_valid": "known_bad_output_problem",
}
REVIEW_ISSUE_TYPES = set(REVIEW_COMPONENT_ISSUE_TYPES.values()) | {
    "wrong_expected_language",
    "privacy_or_safety_issue",
    "cultural_or_locale_issue",
    "other",
}


MODES = {
    "human_audit": {
        "id_field": "audit_id",
        "assignee_field": "annotator_id",
        "completed_fields": HUMAN_FIELDS,
        "boolean_fields": HUMAN_BOOLEAN_FIELDS,
        "overall_field": "human_pass",
        "reason_field": "human_failure_types",
        "notes_field": "human_notes",
        "component_reason_types": HUMAN_COMPONENT_FAILURE_TYPES,
        "allowed_reason_types": HUMAN_FAILURE_TYPES,
        "private_fields": HUMAN_PRIVATE_FIELDS,
    },
    "coverage_native_review": {
        "id_field": "review_id",
        "assignee_field": "reviewer_id",
        "completed_fields": REVIEW_FIELDS,
        "boolean_fields": REVIEW_BOOLEAN_FIELDS,
        "overall_field": "reviewer_release_usable",
        "reason_field": "reviewer_issue_types",
        "notes_field": "reviewer_notes",
        "component_reason_types": REVIEW_COMPONENT_ISSUE_TYPES,
        "allowed_reason_types": REVIEW_ISSUE_TYPES,
        "private_fields": set(),
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv_with_fields(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    require(fieldnames, f"{path} has no CSV header")
    require(all(None not in row for row in rows), f"{path} has malformed CSV rows")
    return fieldnames, rows


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_bool(value: str, *, row_id: str, field: str) -> bool:
    text = str(value).strip().lower()
    if text in {"1", "true", "t", "yes", "y", "pass", "passed"}:
        return True
    if text in {"0", "false", "f", "no", "n", "fail", "failed"}:
        return False
    raise AssertionError(f"{row_id} field {field} must be a completed boolean, got {value!r}")


def parse_reasons(value: str, *, row_id: str, field: str, allowed: set[str]) -> list[str]:
    text = value.strip()
    if not text:
        items: list[str] = []
    elif text.startswith("["):
        parsed = json.loads(text)
        require(isinstance(parsed, list), f"{row_id} {field} JSON must be a list")
        items = [str(item).strip() for item in parsed if str(item).strip()]
    else:
        items = [item.strip() for item in text.split(",") if item.strip()]
    unknown = sorted(set(items) - allowed)
    require(not unknown, f"{row_id} has unknown {field}: {unknown}")
    return items


def validate_completed_fields(row: dict[str, str], *, mode_config: dict[str, Any], allow_incomplete: bool) -> None:
    row_id = row[mode_config["id_field"]]
    assignee_field = mode_config["assignee_field"]
    require(row.get(assignee_field, "").strip(), f"{row_id} missing {assignee_field}")
    if allow_incomplete:
        return

    values = {
        field: parse_bool(row.get(field, ""), row_id=row_id, field=field)
        for field in mode_config["boolean_fields"]
    }
    component_fields = [field for field in mode_config["boolean_fields"] if field != mode_config["overall_field"]]
    expected_overall = all(values[field] for field in component_fields)
    require(
        values[mode_config["overall_field"]] == expected_overall,
        f"{row_id} {mode_config['overall_field']} must equal conjunction of component labels",
    )

    reasons = parse_reasons(
        row.get(mode_config["reason_field"], ""),
        row_id=row_id,
        field=mode_config["reason_field"],
        allowed=mode_config["allowed_reason_types"],
    )
    reason_set = set(reasons)
    if values[mode_config["overall_field"]]:
        require(not reasons, f"{row_id} passes but lists {mode_config['reason_field']}")
        return

    require(reasons, f"{row_id} fails but has no {mode_config['reason_field']}")
    for component_field, reason in mode_config["component_reason_types"].items():
        if values[component_field]:
            require(reason not in reason_set, f"{row_id} lists {reason} but {component_field} is TRUE")
        else:
            require(reason in reason_set, f"{row_id} has {component_field}=FALSE but is missing {reason}")
    if "other" in reason_set:
        require(row.get(mode_config["notes_field"], "").strip(), f"{row_id} uses other without {mode_config['notes_field']}")


def merge_exports(
    *,
    mode: str,
    launch_rows: list[dict[str, str]],
    launch_fields: list[str],
    export_batches: list[tuple[Path, list[str], list[dict[str, str]]]],
    labels_per_item: int,
    allow_incomplete: bool = False,
) -> list[dict[str, str]]:
    require(labels_per_item >= 1, "labels_per_item must be positive")
    mode_config = MODES[mode]
    id_field = mode_config["id_field"]
    completed_fields = set(mode_config["completed_fields"])
    static_fields = [field for field in launch_fields if field not in completed_fields]
    launch_by_id = {row[id_field]: row for row in launch_rows}
    require(len(launch_by_id) == len(launch_rows), f"launch packet has duplicate {id_field} values")

    merged: list[dict[str, str]] = []
    for path, fields, rows in export_batches:
        require(fields == launch_fields, f"{path} header must exactly match launch packet header")
        private = sorted(mode_config["private_fields"].intersection(fields))
        require(not private, f"{path} leaks private fields: {private}")
        for row_index, row in enumerate(rows, start=2):
            row_id = row.get(id_field, "")
            require(row_id, f"{path}:{row_index} missing {id_field}")
            require(row_id in launch_by_id, f"{path}:{row_index} unknown {id_field} {row_id!r}")
            launch = launch_by_id[row_id]
            for field in static_fields:
                require(row.get(field, "") == launch.get(field, ""), f"{path}:{row_index} changed static field {field} for {row_id}")
            validate_completed_fields(row, mode_config=mode_config, allow_incomplete=allow_incomplete)
            merged.append(dict(row))

    counts = Counter(row[id_field] for row in merged)
    expected_counts = {row_id: labels_per_item for row_id in launch_by_id}
    require(dict(counts) == expected_counts, f"merged exports do not have exactly {labels_per_item} label row(s) per item")

    by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in merged:
        by_id[row[id_field]].append(row)
    if labels_per_item > 1:
        assignee_field = mode_config["assignee_field"]
        for row_id, rows in by_id.items():
            assignees = [row[assignee_field].strip() for row in rows]
            require(len(assignees) == len(set(assignees)), f"{row_id} has duplicate {assignee_field} values")

    ordered_rows: list[dict[str, str]] = []
    for launch_row in launch_rows:
        ordered_rows.extend(by_id[launch_row[id_field]])
    return ordered_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=sorted(MODES), required=True)
    parser.add_argument("--launch-packet", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--inputs", nargs="+", type=Path, required=True)
    parser.add_argument("--labels-per-item", type=int, default=1)
    parser.add_argument("--allow-incomplete", action="store_true", help="merge partial returns without requiring filled boolean labels")
    args = parser.parse_args()

    launch_fields, launch_rows = read_csv_with_fields(args.launch_packet)
    export_batches = [(path, *read_csv_with_fields(path)) for path in args.inputs]
    merged = merge_exports(
        mode=args.mode,
        launch_rows=launch_rows,
        launch_fields=launch_fields,
        export_batches=export_batches,
        labels_per_item=args.labels_per_item,
        allow_incomplete=args.allow_incomplete,
    )
    write_csv(args.out, merged, launch_fields)
    print(
        "merged review exports: "
        f"mode={args.mode}, "
        f"rows={len(merged)}, "
        f"items={len(launch_rows)}, "
        f"labels_per_item={args.labels_per_item}, "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
