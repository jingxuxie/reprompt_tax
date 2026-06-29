#!/usr/bin/env python
"""Analyze the blinded human-audit packet design before annotation."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ANNOTATION_FIELDS = (
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


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def parse_bool(value: str) -> bool:
    text = value.strip().lower()
    if text in {"true", "1", "yes", "pass"}:
        return True
    if text in {"false", "0", "no", "fail"}:
        return False
    raise AssertionError(f"cannot parse boolean value {value!r}")


def parse_json_list(value: str, *, row_id: str, field: str) -> list[str]:
    try:
        parsed = json.loads(value or "[]")
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{row_id} has invalid JSON in {field}") from exc
    require(isinstance(parsed, list), f"{row_id} {field} must be a JSON list")
    require(all(isinstance(item, str) for item in parsed), f"{row_id} {field} must contain strings")
    return parsed


def merged_rows(packet_rows: list[dict[str, str]], key_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    key_by_id = {row["audit_id"]: row for row in key_rows}
    require(len(key_by_id) == len(key_rows), "answer key has duplicate audit_id values")
    require(set(key_by_id) == {row["audit_id"] for row in packet_rows}, "packet and answer-key audit IDs differ")

    out: list[dict[str, str]] = []
    for packet_row in packet_rows:
        key_row = key_by_id[packet_row["audit_id"]]
        for field in ("language_pair", "task_family"):
            require(packet_row[field] == key_row[field], f"{packet_row['audit_id']} packet/key mismatch for {field}")
        out.append({**key_row, **packet_row})
    return out


def count_by(rows: list[dict[str, str]], fields: tuple[str, ...]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = {}
    for row in rows:
        key = tuple(row[field] for field in fields)
        grouped.setdefault(key, []).append(row)

    out: list[dict[str, Any]] = []
    for key, group_rows in sorted(grouped.items()):
        auto_pass = sum(parse_bool(row["auto_pass"]) for row in group_rows)
        base = {field: value for field, value in zip(fields, key)}
        base.update(
            {
                "n": len(group_rows),
                "auto_pass_n": auto_pass,
                "auto_fail_n": len(group_rows) - auto_pass,
                "auto_pass_rate": round(auto_pass / len(group_rows), 4),
            }
        )
        out.append(base)
    return out


def failure_type_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    failed_rows = 0
    for row in rows:
        if parse_bool(row["auto_pass"]):
            continue
        failed_rows += 1
        failure_types = parse_json_list(row.get("auto_failure_types", ""), row_id=row["audit_id"], field="auto_failure_types")
        require(failure_types, f"{row['audit_id']} auto-fail row has no auto_failure_types")
        counts.update(failure_types)
    return [
        {
            "auto_failure_type": failure_type,
            "sampled_failure_rows_with_type": count,
            "sampled_auto_fail_rows": failed_rows,
        }
        for failure_type, count in sorted(counts.items())
    ]


def design_summary(packet_rows: list[dict[str, str]], key_rows: list[dict[str, str]], rows: list[dict[str, str]]) -> dict[str, Any]:
    packet_fields = set(packet_rows[0]) if packet_rows else set()
    annotation_blank = all(row.get(field, "") == "" for row in packet_rows for field in ANNOTATION_FIELDS)
    auto_pass = sum(parse_bool(row["auto_pass"]) for row in rows)
    return {
        "packet_rows": len(packet_rows),
        "answer_key_rows": len(key_rows),
        "language_pairs": len({row["language_pair"] for row in rows}),
        "task_families": len({row["task_family"] for row in rows}),
        "models": len({row["model"] for row in rows}),
        "conditions": len({row["condition"] for row in rows}),
        "model_condition_language_family_strata": len({(row["model"], row["condition"], row["language_pair"], row["task_family"]) for row in rows}),
        "first_turn_only": all(row["turn"] == "0" for row in rows),
        "packet_private_fields_present": bool(PRIVATE_FIELDS.intersection(packet_fields)),
        "annotation_fields_blank": annotation_blank,
        "auto_pass_rows": auto_pass,
        "auto_fail_rows": len(rows) - auto_pass,
        "auto_pass_rate": round(auto_pass / len(rows), 4),
    }


def write_markdown(
    path: Path,
    title: str,
    summary: dict[str, Any],
    by_language: list[dict[str, Any]],
    by_family: list[dict[str, Any]],
    by_model_condition: list[dict[str, Any]],
    by_failure_type: list[dict[str, Any]],
) -> None:
    lines = [
        f"# {title}",
        "",
        "Generated from the blinded launch packet and private answer key. This is",
        "a design-readiness audit only; it is not completed human validation.",
        "",
        "## Overview",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in summary.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(
        [
            "",
            "## Language Coverage",
            "",
            "| Language pair | Rows | Auto pass | Auto fail | Auto pass rate |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in by_language:
        lines.append(
            f"| {row['language_pair']} | {row['n']} | {row['auto_pass_n']} | "
            f"{row['auto_fail_n']} | {100 * row['auto_pass_rate']:.1f}% |"
        )

    lines.extend(
        [
            "",
            "## Task-Family Coverage",
            "",
            "| Task family | Rows | Auto pass | Auto fail | Auto pass rate |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in by_family:
        lines.append(
            f"| {row['task_family']} | {row['n']} | {row['auto_pass_n']} | "
            f"{row['auto_fail_n']} | {100 * row['auto_pass_rate']:.1f}% |"
        )

    lines.extend(
        [
            "",
            "## Model-Condition Coverage",
            "",
            "| Model | Condition | Rows | Auto pass | Auto fail | Auto pass rate |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in by_model_condition:
        lines.append(
            f"| {row['model']} | {row['condition']} | {row['n']} | {row['auto_pass_n']} | "
            f"{row['auto_fail_n']} | {100 * row['auto_pass_rate']:.1f}% |"
        )

    lines.extend(
        [
            "",
            "## Auto-Failure Coverage",
            "",
            "| Auto failure type | Sampled rows with type | Sampled auto-fail rows |",
            "|---|---:|---:|",
        ]
    )
    for row in by_failure_type:
        lines.append(
            f"| {row['auto_failure_type']} | {row['sampled_failure_rows_with_type']} | "
            f"{row['sampled_auto_fail_rows']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The packet covers one first-turn response for every model, condition,",
            "language-pair, and task-family stratum: "
            f"{summary['model_condition_language_family_strata']} strata total. The annotator",
            "packet contains no private model, condition, item-id, or automatic-label",
            "fields, and all annotation fields, including `annotator_id`, are blank.",
            "The launch package includes an annotator roster template so completed",
            "validation can tie every filled row to a qualified language/script",
            "annotator. The answer key shows that the sample includes both automatic",
            "passes and automatic failures, so the completed audit can test agreement",
            "rather than only confirm easy cases.",
            "",
            "Completed native/near-native annotation is still required before widening",
            "the paper claim beyond automatic scoring plus LLM-judge audit.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=Path("data/human_audit/human_audit_packet_v0.2.csv"))
    parser.add_argument("--answer-key", type=Path, default=Path("data/human_audit/human_audit_answer_key_v0.2.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/human_audit_v0.2_design"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/human_audit_design_audit_v02.md"))
    parser.add_argument("--expected-models", default="gpt-4.1,gpt-4.1-mini,gpt-4.1-nano")
    parser.add_argument("--title", default="Human Audit Design Audit")
    args = parser.parse_args()
    expected_models = tuple(model.strip() for model in args.expected_models.split(",") if model.strip())
    require(bool(expected_models), "expected at least one model")
    expected_rows = 3 * 4 * 2 * len(expected_models)

    packet_rows = read_csv(args.packet)
    key_rows = read_csv(args.answer_key)
    rows = merged_rows(packet_rows, key_rows)
    summary = design_summary(packet_rows, key_rows, rows)
    require(summary["packet_rows"] == expected_rows, f"expected {expected_rows} packet rows, found {summary['packet_rows']}")
    require(summary["answer_key_rows"] == expected_rows, f"expected {expected_rows} answer-key rows, found {summary['answer_key_rows']}")
    require(summary["model_condition_language_family_strata"] == expected_rows, "expected one row per model/condition/language/family stratum")
    require(summary["first_turn_only"] is True, "human audit should cover first-turn rows only")
    require(summary["packet_private_fields_present"] is False, "packet leaks private fields")
    require(summary["annotation_fields_blank"] is True, "packet annotation fields are not blank")

    by_language = count_by(rows, ("language_pair",))
    by_family = count_by(rows, ("task_family",))
    by_language_family = count_by(rows, ("language_pair", "task_family"))
    by_model_condition = count_by(rows, ("model", "condition"))
    by_failure_type = failure_type_rows(rows)

    write_csv(args.out_dir / "human_audit_design_summary.csv", [summary])
    write_csv(args.out_dir / "human_audit_design_by_language.csv", by_language)
    write_csv(args.out_dir / "human_audit_design_by_family.csv", by_family)
    write_csv(args.out_dir / "human_audit_design_by_language_family.csv", by_language_family)
    write_csv(args.out_dir / "human_audit_design_by_model_condition.csv", by_model_condition)
    write_csv(args.out_dir / "human_audit_design_by_auto_failure_type.csv", by_failure_type)
    write_markdown(args.out_md, args.title, summary, by_language, by_family, by_model_condition, by_failure_type)
    print(f"wrote human-audit design analysis to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
