#!/usr/bin/env python
"""Finalize double-annotated human-audit labels after adjudication."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

from analyze_human_audit_adjudication import (
    ADJUDICATION_FIELDS,
    COMPONENTS,
    adjudication_rows,
    normalized_failure_types,
    parse_human_values,
    validate_long_annotations,
    write_csv,
)
from validate_completed_human_audit import (
    BOOLEAN_FIELDS,
    DEFAULT_MODELS,
    parse_bool,
    parse_expected_models,
    parse_failure_types,
    read_csv,
    require,
    validate_annotations,
)


ADJUDICATED_COMPONENTS = {
    "adjudicated_pass": "human_pass",
    "adjudicated_language_pass": "human_language_pass",
    "adjudicated_script_pass": "human_script_pass",
    "adjudicated_preservation_pass": "human_preservation_pass",
    "adjudicated_task_pass": "human_task_pass",
    "adjudicated_register_locale_pass": "human_register_locale_pass",
}


def read_optional_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def bool_text(value: bool) -> str:
    return "TRUE" if value else "FALSE"


def validate_adjudication_row(row: dict[str, str], *, expected_row: dict[str, Any], roster_by_id: dict[str, dict[str, str]]) -> dict[str, bool]:
    row_id = row["audit_id"]
    for field in ("language_pair", "task_family"):
        require(row.get(field, "") == expected_row.get(field, ""), f"{row_id} adjudication mismatch for {field}")
    missing = [field for field in ADJUDICATION_FIELDS if field not in row]
    require(not missing, f"{row_id} adjudication row missing fields: {missing}")
    adjudicator_id = row["adjudicator_id"].strip()
    require(adjudicator_id, f"{row_id} missing adjudicator_id")
    require(adjudicator_id in roster_by_id, f"{row_id} adjudicator_id {adjudicator_id!r} is not in roster")
    require(
        roster_by_id[adjudicator_id]["language_pair"].strip() == row["language_pair"],
        f"{row_id} adjudicator {adjudicator_id} is not qualified for {row['language_pair']}",
    )
    values = {
        human_field: parse_bool(row.get(adjudicated_field), row_id=row_id, field=adjudicated_field)
        for adjudicated_field, human_field in ADJUDICATED_COMPONENTS.items()
    }
    expected_pass = all(values[field] for field in BOOLEAN_FIELDS if field != "human_pass")
    require(values["human_pass"] == expected_pass, f"{row_id} adjudicated_pass must equal conjunction of adjudicated components")
    failure_types = parse_failure_types(row.get("adjudicated_failure_types", ""), row_id=row_id)
    if values["human_pass"]:
        require(not failure_types, f"{row_id} adjudicated pass lists failure types")
    else:
        require(failure_types, f"{row_id} adjudicated fail has no failure types")
        if "other" in failure_types:
            require(row.get("adjudication_notes", "").strip(), f"{row_id} uses other without adjudication_notes")
    return values


def finalize_labels(
    *,
    annotation_rows: list[dict[str, str]],
    key_rows: list[dict[str, str]],
    roster_rows: list[dict[str, str]],
    adjudication_rows_input: list[dict[str, str]],
    expected_models: tuple[str, ...] = DEFAULT_MODELS,
    allow_smoke: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    _, _, _, expected_adjudication = validate_long_annotations(
        annotation_rows=annotation_rows,
        key_rows=key_rows,
        roster_rows=roster_rows,
        expected_models=expected_models,
        allow_smoke=allow_smoke,
    )
    expected_by_id = {row["audit_id"]: row for row in expected_adjudication}
    adjudication_by_id = {row["audit_id"]: row for row in adjudication_rows_input}
    require(len(adjudication_by_id) == len(adjudication_rows_input), "duplicate audit_id values in adjudication packet")
    require(
        set(adjudication_by_id) == set(expected_by_id),
        f"completed adjudication IDs must equal required disagreement IDs: expected={sorted(expected_by_id)}, got={sorted(adjudication_by_id)}",
    )

    roster_by_id = {row["annotator_id"]: row for row in roster_rows}
    rows_by_audit: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in annotation_rows:
        rows_by_audit[row["audit_id"]].append(row)

    final_rows: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []
    for audit_id, rows in sorted(rows_by_audit.items()):
        first = dict(rows[0])
        source = {
            "audit_id": audit_id,
            "source_annotator_ids": ";".join(row["annotator_id"] for row in rows),
        }
        if audit_id in adjudication_by_id:
            adjudication = adjudication_by_id[audit_id]
            values = validate_adjudication_row(adjudication, expected_row=expected_by_id[audit_id], roster_by_id=roster_by_id)
            first["annotator_id"] = adjudication["adjudicator_id"].strip()
            for field in BOOLEAN_FIELDS:
                first[field] = bool_text(values[field])
            first["human_failure_types"] = adjudication.get("adjudicated_failure_types", "")
            notes = adjudication.get("adjudication_notes", "").strip()
            first["human_notes"] = f"ADJUDICATED: {notes}" if notes else "ADJUDICATED"
            source.update({"final_label_source": "adjudicated", "adjudicator_id": first["annotator_id"]})
        else:
            values_by_field = {
                field: {parse_human_values(row)[field] for row in rows}
                for _, field in COMPONENTS
            }
            for field, values in values_by_field.items():
                require(len(values) == 1, f"{audit_id} has unresolved component disagreement for {field}")
                first[field] = bool_text(next(iter(values)))
            failure_type_values = {normalized_failure_types(row) for row in rows}
            require(len(failure_type_values) == 1, f"{audit_id} has unresolved failure-type disagreement")
            first["human_failure_types"] = ",".join(next(iter(failure_type_values)))
            first["human_notes"] = "CONSENSUS: " + ";".join(row["annotator_id"] for row in rows)
            source.update({"final_label_source": "consensus", "adjudicator_id": ""})
        final_rows.append(first)
        source_rows.append(source)

    validate_annotations(
        annotation_rows=final_rows,
        key_rows=key_rows,
        roster_rows=roster_rows,
        allow_smoke=allow_smoke,
        expected_models=expected_models,
    )
    return final_rows, source_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--answer-key", type=Path, default=Path("data/human_audit/human_audit_answer_key_v0.2.csv"))
    parser.add_argument("--annotator-roster", type=Path, default=Path("data/human_audit/human_audit_annotator_roster_v0.2.csv"))
    parser.add_argument("--adjudication", type=Path, required=True)
    parser.add_argument("--expected-models", default=",".join(DEFAULT_MODELS))
    parser.add_argument("--out", type=Path, default=Path("data/human_audit/human_audit_packet_v0.2_adjudicated_completed.csv"))
    parser.add_argument("--source-out", type=Path, default=Path("results/tables/human_audit_v0.2_adjudication/human_audit_final_label_sources.csv"))
    parser.add_argument("--allow-smoke", action="store_true", help="Allow smoke-only labels for plumbing tests, not claims.")
    args = parser.parse_args()

    final_rows, source_rows = finalize_labels(
        annotation_rows=read_csv(args.annotations),
        key_rows=read_csv(args.answer_key),
        roster_rows=read_csv(args.annotator_roster),
        adjudication_rows_input=read_optional_csv(args.adjudication),
        expected_models=parse_expected_models(args.expected_models),
        allow_smoke=args.allow_smoke,
    )
    write_csv(args.out, final_rows)
    write_csv(args.source_out, source_rows)
    print(
        "finalized adjudicated human-audit labels: "
        f"rows={len(final_rows)}, "
        f"adjudicated={sum(row['final_label_source'] == 'adjudicated' for row in source_rows)}, "
        f"consensus={sum(row['final_label_source'] == 'consensus' for row in source_rows)}"
    )


if __name__ == "__main__":
    main()
