#!/usr/bin/env python
"""Validate completed RePromptTax human audit annotations."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


BOOLEAN_FIELDS = (
    "human_pass",
    "human_language_pass",
    "human_script_pass",
    "human_preservation_pass",
    "human_task_pass",
    "human_register_locale_pass",
)

ROSTER_FIELDS = (
    "annotator_id",
    "language_pair",
    "native_or_near_native",
    "can_validate_script",
    "qualification_notes",
    "conflict_of_interest",
)

FAILURE_TYPES = {
    "wrong_output_language",
    "script_mismatch",
    "preservation_failure",
    "task_noncompletion",
    "register_locale_mismatch",
    "other",
}

PRIVATE_FIELDS = {
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


def parse_optional_bool(value: Any, *, row_id: str, field: str) -> bool:
    text = str(value).strip().lower()
    if text == "":
        raise AssertionError(f"{row_id} field {field} must be completed, got blank")
    return parse_bool(value, row_id=row_id, field=field)


def parse_failure_types(value: str, *, row_id: str) -> list[str]:
    text = value.strip()
    if not text:
        items: list[str] = []
    elif text.startswith("["):
        parsed = json.loads(text)
        require(isinstance(parsed, list), f"{row_id} human_failure_types JSON must be a list")
        items = [str(item).strip() for item in parsed if str(item).strip()]
    else:
        items = [item.strip() for item in text.split(",") if item.strip()]
    unknown = sorted(set(items) - FAILURE_TYPES)
    require(not unknown, f"{row_id} has unknown human_failure_types: {unknown}")
    return items


def validate_roster(roster_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    require(roster_rows, "annotator roster is empty")
    fields = set(roster_rows[0])
    missing = [field for field in ROSTER_FIELDS if field not in fields]
    require(not missing, f"annotator roster missing fields: {missing}")
    by_id: dict[str, dict[str, str]] = {}
    for row in roster_rows:
        annotator_id = row["annotator_id"].strip()
        require(annotator_id, "annotator roster has blank annotator_id")
        require(not annotator_id.startswith("replace_with_"), f"annotator roster still contains placeholder ID {annotator_id}")
        require(annotator_id not in by_id, f"duplicate annotator_id in roster: {annotator_id}")
        language_pair = row["language_pair"].strip()
        require(language_pair in {"ar-en", "es-en", "hi-en"}, f"{annotator_id} has unsupported language_pair {language_pair!r}")
        native = parse_optional_bool(row["native_or_near_native"], row_id=annotator_id, field="native_or_near_native")
        script = parse_optional_bool(row["can_validate_script"], row_id=annotator_id, field="can_validate_script")
        conflict = parse_optional_bool(row["conflict_of_interest"], row_id=annotator_id, field="conflict_of_interest")
        require(native, f"{annotator_id} is not marked native_or_near_native")
        require(script, f"{annotator_id} is not marked can_validate_script")
        require(not conflict, f"{annotator_id} is marked conflict_of_interest")
        require(row.get("qualification_notes", "").strip(), f"{annotator_id} missing qualification_notes")
        by_id[annotator_id] = row
    return by_id


def validate_annotations(
    *,
    annotation_rows: list[dict[str, str]],
    key_rows: list[dict[str, str]],
    roster_rows: list[dict[str, str]] | None,
    allow_smoke: bool,
) -> dict[str, Any]:
    require(len(annotation_rows) == 72, f"expected 72 completed annotation rows, found {len(annotation_rows)}")
    require(len(key_rows) == 72, f"expected 72 answer-key rows, found {len(key_rows)}")
    require(annotation_rows, "completed annotation file is empty")
    require(not PRIVATE_FIELDS.intersection(annotation_rows[0].keys()), "completed annotation file leaks private answer-key fields")

    annotation_ids = [row["audit_id"] for row in annotation_rows]
    key_ids = [row["audit_id"] for row in key_rows]
    require(len(annotation_ids) == len(set(annotation_ids)), "duplicate audit_id values in completed annotations")
    require(set(annotation_ids) == set(key_ids), "completed annotations and answer key audit IDs differ")

    key_by_id = {row["audit_id"]: row for row in key_rows}
    roster_by_id = validate_roster(roster_rows or []) if not allow_smoke else {}
    pass_pairs: list[tuple[bool, bool]] = []
    all_component_pairs: list[tuple[bool, bool]] = []
    human_failures = 0
    auto_failures = 0
    annotator_ids: set[str] = set()

    for row in annotation_rows:
        row_id = row["audit_id"]
        key = key_by_id[row_id]
        for field in ("language_pair", "task_family"):
            require(row[field] == key[field], f"{row_id} packet/key mismatch for {field}")
        if not allow_smoke:
            require(not row.get("human_notes", "").startswith("SMOKE ONLY:"), f"{row_id} is marked smoke-only")
            annotator_id = row.get("annotator_id", "").strip()
            require(annotator_id, f"{row_id} missing annotator_id")
            require(annotator_id in roster_by_id, f"{row_id} annotator_id {annotator_id!r} is not in roster")
            require(
                roster_by_id[annotator_id]["language_pair"].strip() == row["language_pair"],
                f"{row_id} annotator {annotator_id} is not qualified for {row['language_pair']}",
            )
            annotator_ids.add(annotator_id)

        values = {field: parse_bool(row.get(field), row_id=row_id, field=field) for field in BOOLEAN_FIELDS}
        expected_pass = all(values[field] for field in BOOLEAN_FIELDS if field != "human_pass")
        require(values["human_pass"] == expected_pass, f"{row_id} human_pass must equal conjunction of component labels")
        failure_types = parse_failure_types(row.get("human_failure_types", ""), row_id=row_id)
        if values["human_pass"]:
            require(not failure_types, f"{row_id} passes but lists human_failure_types")
        else:
            require(failure_types, f"{row_id} fails but has no human_failure_types")
            if row.get("human_notes", "").strip() == "":
                require("other" not in failure_types, f"{row_id} uses other without human_notes")

        human_failures += 0 if values["human_pass"] else 1
        auto_pass = parse_bool(key["auto_pass"], row_id=row_id, field="auto_pass")
        auto_failures += 0 if auto_pass else 1
        pass_pairs.append((values["human_pass"], auto_pass))

        component_map = {
            "human_language_pass": "auto_language_pass",
            "human_script_pass": "auto_script_pass",
            "human_preservation_pass": "auto_preservation_pass",
            "human_task_pass": "auto_task_pass",
            "human_register_locale_pass": "auto_register_locale_pass",
        }
        for human_field, auto_field in component_map.items():
            all_component_pairs.append((values[human_field], parse_bool(key[auto_field], row_id=row_id, field=auto_field)))

    strata = Counter((key["model"], key["condition"], key["task_family"], key["language_pair"]) for key in key_rows)
    require(len(strata) == 72, f"expected 72 model/condition/family/language strata, found {len(strata)}")
    require(all(count == 1 for count in strata.values()), f"answer key strata not balanced: {strata}")

    pass_agree = sum(human == auto for human, auto in pass_pairs)
    component_agree = sum(human == auto for human, auto in all_component_pairs)
    return {
        "rows": len(annotation_rows),
        "annotators": len(annotator_ids),
        "human_failures": human_failures,
        "auto_failures": auto_failures,
        "pass_agreement": pass_agree / len(pass_pairs),
        "component_agreement": component_agree / len(all_component_pairs),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--answer-key", type=Path, default=Path("data/human_audit/human_audit_answer_key_v0.2.csv"))
    parser.add_argument("--annotator-roster", type=Path, default=Path("data/human_audit/human_audit_annotator_roster_v0.2.csv"))
    parser.add_argument("--allow-smoke", action="store_true", help="Allow smoke-only completed files for plumbing tests, not paper claims.")
    args = parser.parse_args()

    summary = validate_annotations(
        annotation_rows=read_csv(args.annotations),
        key_rows=read_csv(args.answer_key),
        roster_rows=None if args.allow_smoke else read_csv(args.annotator_roster),
        allow_smoke=args.allow_smoke,
    )
    print(
        "completed human-audit validation passed: "
        f"rows={summary['rows']}, "
        f"annotators={summary['annotators']}, "
        f"human_failures={summary['human_failures']}, "
        f"auto_failures={summary['auto_failures']}, "
        f"pass_agreement={summary['pass_agreement']:.3f}, "
        f"component_agreement={summary['component_agreement']:.3f}"
    )


if __name__ == "__main__":
    main()
