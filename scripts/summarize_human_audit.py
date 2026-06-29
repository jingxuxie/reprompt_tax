#!/usr/bin/env python
"""Summarize completed human audit annotations."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


COMPONENTS = [
    ("pass", "human_pass", "auto_pass"),
    ("language", "human_language_pass", "auto_language_pass"),
    ("script", "human_script_pass", "auto_script_pass"),
    ("preservation", "human_preservation_pass", "auto_preservation_pass"),
    ("task", "human_task_pass", "auto_task_pass"),
    ("register_locale", "human_register_locale_pass", "auto_register_locale_pass"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_bool(value: Any) -> bool | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"1", "true", "t", "yes", "y", "pass", "passed"}:
        return True
    if text in {"0", "false", "f", "no", "n", "fail", "failed"}:
        return False
    if text == "":
        return None
    raise ValueError(f"cannot parse boolean annotation value: {value!r}")


def cohen_kappa(pairs: list[tuple[bool, bool]]) -> float | str:
    if not pairs:
        return ""
    n = len(pairs)
    agree = sum(a == b for a, b in pairs) / n
    a_counts = Counter(a for a, _ in pairs)
    b_counts = Counter(b for _, b in pairs)
    expected = sum((a_counts[label] / n) * (b_counts[label] / n) for label in (False, True))
    if expected == 1.0:
        return 1.0 if agree == 1.0 else 0.0
    return (agree - expected) / (1.0 - expected)


def merge_annotations(packet_rows: list[dict[str, str]], key_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    require(packet_rows, "annotation file is empty")
    require(key_rows, "answer-key file is empty")
    annotation_ids = [row["audit_id"] for row in packet_rows]
    key_ids = [row["audit_id"] for row in key_rows]
    require(len(annotation_ids) == len(set(annotation_ids)), "duplicate audit_id values in annotations")
    require(len(key_ids) == len(set(key_ids)), "duplicate audit_id values in answer key")
    require(set(annotation_ids) == set(key_ids), "annotations and answer key audit IDs differ")

    key_by_id = {row["audit_id"]: row for row in key_rows}
    merged: list[dict[str, Any]] = []
    for row in packet_rows:
        key = key_by_id[row["audit_id"]]
        merged.append({**key, **row})
    return merged


def ensure_completed(rows: list[dict[str, Any]]) -> None:
    required_fields = [human_field for _, human_field, _ in COMPONENTS]
    for row in rows:
        row_id = row["audit_id"]
        for field in required_fields:
            require(parse_bool(row.get(field)) is not None, f"{row_id} has incomplete {field}")
    require(rows, "no completed human-audit rows to summarize")


def completed_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        if parse_bool(row.get("human_pass")) is not None:
            out.append(row)
    return out


def summarize(rows: list[dict[str, Any]], group_keys: list[str]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(str(row.get(key, "")) for key in group_keys)].append(row)

    out: list[dict[str, Any]] = []
    for group, group_rows in sorted(grouped.items()):
        base = {key: value for key, value in zip(group_keys, group)}
        base["n"] = len(group_rows)
        for name, human_field, auto_field in COMPONENTS:
            pairs: list[tuple[bool, bool]] = []
            for row in group_rows:
                human = parse_bool(row.get(human_field))
                auto = parse_bool(row.get(auto_field))
                if human is not None and auto is not None:
                    pairs.append((human, auto))
            if pairs:
                base[f"{name}_agreement"] = sum(a == b for a, b in pairs) / len(pairs)
                base[f"{name}_kappa"] = cohen_kappa(pairs)
                base[f"{name}_human_pass_rate"] = sum(a for a, _ in pairs) / len(pairs)
                base[f"{name}_auto_pass_rate"] = sum(b for _, b in pairs) / len(pairs)
            else:
                base[f"{name}_agreement"] = ""
                base[f"{name}_kappa"] = ""
                base[f"{name}_human_pass_rate"] = ""
                base[f"{name}_auto_pass_rate"] = ""
        out.append(base)
    return out


def disagreement_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        human = parse_bool(row.get("human_pass"))
        auto = parse_bool(row.get("auto_pass"))
        if human is None or auto is None or human == auto:
            continue
        out.append(
            {
                "audit_id": row["audit_id"],
                "item_id": row["item_id"],
                "model": row["model"],
                "condition": row["condition"],
                "language_pair": row["language_pair"],
                "task_family": row["task_family"],
                "human_pass": human,
                "auto_pass": auto,
                "auto_failure_types": row.get("auto_failure_types", ""),
                "human_failure_types": row.get("human_failure_types", ""),
                "human_notes": row.get("human_notes", ""),
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--answer-key", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="summarize completed rows only; for debugging, not paper-facing completed audit claims",
    )
    args = parser.parse_args()

    rows = merge_annotations(read_csv(args.annotations), read_csv(args.answer_key))
    if args.allow_partial:
        done = completed_rows(rows)
    else:
        ensure_completed(rows)
        done = rows
    require(done, "no completed human-audit rows to summarize")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "human_audit_summary.csv", summarize(done, []))
    write_csv(args.out_dir / "human_audit_by_language.csv", summarize(done, ["language_pair"]))
    write_csv(args.out_dir / "human_audit_by_family.csv", summarize(done, ["task_family"]))
    write_csv(args.out_dir / "human_audit_by_model_condition.csv", summarize(done, ["model", "condition"]))
    write_csv(args.out_dir / "human_audit_by_annotator.csv", summarize(done, ["annotator_id", "language_pair"]))
    write_csv(args.out_dir / "human_audit_disagreements.csv", disagreement_rows(done))
    print(f"summarized {len(done)} completed human annotations out of {len(rows)} rows")


if __name__ == "__main__":
    main()
