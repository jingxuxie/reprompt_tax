#!/usr/bin/env python
"""Validate the v0.3 coverage native-review launch packet."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


EXPECTED_SLICES = (
    "arabic_instruction_arabic_filenames",
    "english_instruction_arabic_content",
    "english_instruction_hindi_content",
    "english_instruction_spanish_content",
    "hindi_english_instruction_hindi_devanagari",
    "spanish_instruction_arabic_quote",
)
EXPECTED_ROWS = 60
EXPECTED_PER_SLICE = 10

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

REQUIRED_FIELDS = (
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
    "notes_for_reviewers",
    *REVIEW_FIELDS,
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def parse_json_list(value: str, *, row_id: str, field: str) -> list[Any]:
    try:
        parsed = json.loads(value or "[]")
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{row_id} has invalid JSON in {field}") from exc
    require(isinstance(parsed, list), f"{row_id} field {field} must be a JSON list")
    return parsed


def validate_packet(packet_rows: list[dict[str, str]], benchmark_rows: list[dict[str, Any]]) -> None:
    require(len(packet_rows) == EXPECTED_ROWS, f"expected {EXPECTED_ROWS} review rows, found {len(packet_rows)}")
    require(packet_rows, "review packet is empty")
    fields = set(packet_rows[0])
    missing = [field for field in REQUIRED_FIELDS if field not in fields]
    require(not missing, f"review packet missing fields: {missing}")

    review_ids = [row["review_id"] for row in packet_rows]
    item_ids = [row["item_id"] for row in packet_rows]
    require(len(review_ids) == len(set(review_ids)), "duplicate review_id values")
    require(len(item_ids) == len(set(item_ids)), "duplicate item_id values")
    require(review_ids == sorted(review_ids), "review_id values are not sorted")

    benchmark_by_id = {row["id"]: row for row in benchmark_rows}
    require(set(item_ids) == set(benchmark_by_id), "review packet item IDs do not match v0.3 benchmark")

    counts = Counter(row["coverage_slice"] for row in packet_rows)
    require(dict(counts) == {coverage_slice: EXPECTED_PER_SLICE for coverage_slice in EXPECTED_SLICES}, f"unexpected slice counts: {counts}")

    for row in packet_rows:
        review_id = row["review_id"]
        benchmark_row = benchmark_by_id[row["item_id"]]
        for field in (
            "coverage_slice",
            "language_pair",
            "instruction_language",
            "content_language",
            "task_family",
            "user_prompt",
            "expected_response_language",
            "expected_script",
        ):
            source_field = "id" if field == "item_id" else field
            require(str(row[field]) == str(benchmark_row[source_field]), f"{review_id} mismatch for {field}")
        require(row["coverage_slice"] in EXPECTED_SLICES, f"{review_id} unexpected coverage_slice")
        require(row["task_family"] == "editing_preservation", f"{review_id} unexpected task_family")
        require(benchmark_row["validation_status"] == "synthetic_scaffold_requires_native_validation", f"{review_id} benchmark row missing native-validation status")
        for field in ("must_preserve_spans", "required_any_markers", "forbidden_markers", "known_bad_outputs"):
            parsed = parse_json_list(row[field], row_id=review_id, field=field)
            require(parsed, f"{review_id} field {field} should not be empty")
        for field in REVIEW_FIELDS:
            require(row.get(field, "") == "", f"{review_id} review field {field} is not blank")
        require("requires native validation before claims" in row["notes_for_reviewers"], f"{review_id} missing native-validation note")


def validate_slice_files(out_dir: Path, packet_rows: list[dict[str, str]]) -> None:
    for coverage_slice in EXPECTED_SLICES:
        path = out_dir / f"coverage_native_review_v03_{coverage_slice}.csv"
        require(path.exists(), f"missing slice packet {path}")
        rows = read_csv(path)
        expected = [row for row in packet_rows if row["coverage_slice"] == coverage_slice]
        require(rows == expected, f"slice packet {path} does not match full packet subset")


def validate_roster_template(out_dir: Path) -> None:
    path = out_dir / "coverage_native_review_roster_template_v03.csv"
    require(path.exists(), f"missing roster template {path}")
    rows = read_csv(path)
    require(len(rows) == 2 * len(EXPECTED_SLICES), f"expected two roster template rows per slice, found {len(rows)}")
    require({row["coverage_slice"] for row in rows} == set(EXPECTED_SLICES), "roster template slices mismatch")
    counts = Counter(row["coverage_slice"] for row in rows)
    require(all(count == 2 for count in counts.values()), f"roster template should have two reviewer slots per slice: {counts}")
    for row in rows:
        require(row["reviewer_id"].startswith("replace_with_"), f"roster template still needs placeholder reviewer ID for {row['coverage_slice']}")
        for field in (
            "can_validate_instruction_language",
            "can_validate_target_language",
            "can_validate_script",
            "qualification_notes",
            "conflict_of_interest",
        ):
            require(row.get(field, "") == "", f"roster template field {field} should be blank before completion")


def validate_text_files(out_dir: Path) -> None:
    manifest = out_dir / "coverage_native_review_manifest_v03.md"
    checklist = out_dir / "coverage_native_review_launch_checklist_v03.md"
    require(manifest.exists(), f"missing manifest {manifest}")
    require(checklist.exists(), f"missing checklist {checklist}")
    manifest_text = manifest.read_text(encoding="utf-8")
    checklist_text = checklist.read_text(encoding="utf-8")
    for phrase in (
        "not completed native validation",
        "Do not claim native validation has been completed",
        "merge_review_exports.py",
        "matching `reviewer_issue_types` code",
        "60-row synthetic",
    ):
        require(phrase in manifest_text or phrase in checklist_text, f"native-review docs missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, default=Path("data/benchmark_stress_v0.3_expansion.jsonl"))
    parser.add_argument("--out-dir", type=Path, default=Path("data/coverage_native_review_v03"))
    args = parser.parse_args()

    packet_path = args.out_dir / "coverage_native_review_packet_v03.csv"
    require(packet_path.exists(), f"missing review packet {packet_path}")
    packet_rows = read_csv(packet_path)
    benchmark_rows = load_jsonl(args.benchmark)
    validate_packet(packet_rows, benchmark_rows)
    validate_slice_files(args.out_dir, packet_rows)
    validate_roster_template(args.out_dir)
    validate_text_files(args.out_dir)
    print("validated v0.3 coverage native-review launch packet")


if __name__ == "__main__":
    main()
