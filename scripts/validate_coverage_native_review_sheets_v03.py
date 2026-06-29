#!/usr/bin/env python
"""Validate generated v0.3 coverage native-review sheets."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

from make_coverage_native_review_packet_v03 import EXPECTED_SLICES, REVIEW_FIELDS
from make_coverage_native_review_sheets_v03 import sheet_filename


PRIVATE_MARKERS = (
    "auto_pass",
    "auto_language_pass",
    "auto_script_pass",
    "auto_preservation_pass",
    "auto_task_pass",
    "auto_register_locale_pass",
    "auto_failure_types",
    "validation_status",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def extract_rows(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r'<script id="review-data" type="application/json">(.*?)</script>', text, flags=re.DOTALL)
    require(match is not None, f"{path} missing review-data JSON")
    payload = match.group(1).replace("<\\/", "</")
    rows = json.loads(payload)
    require(isinstance(rows, list), f"{path} review-data must be a list")
    return rows


def validate_sheet_text(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for marker in PRIVATE_MARKERS:
        require(marker not in text, f"{path} leaks private marker {marker}")
    for phrase in ("Download CSV", "reviewer issue types", "same ID as roster"):
        require(phrase in text, f"{path} missing phrase {phrase!r}")
    for field in REVIEW_FIELDS:
        require(field in text, f"{path} missing review field {field}")


def validate_rows(packet_rows: list[dict[str, str]], out_dir: Path) -> None:
    packet_by_slice = {coverage_slice: [row for row in packet_rows if row["coverage_slice"] == coverage_slice] for coverage_slice in EXPECTED_SLICES}
    all_sheet_ids: list[str] = []
    for coverage_slice in EXPECTED_SLICES:
        path = out_dir / sheet_filename(coverage_slice)
        require(path.exists(), f"missing native-review sheet {path}")
        validate_sheet_text(path)
        rows = extract_rows(path)
        expected_rows = packet_by_slice[coverage_slice]
        require(len(rows) == len(expected_rows), f"{path} expected {len(expected_rows)} rows, found {len(rows)}")
        require([row["review_id"] for row in rows] == [row["review_id"] for row in expected_rows], f"{path} review IDs do not match packet slice")
        require(all(row["coverage_slice"] == coverage_slice for row in rows), f"{path} contains wrong coverage_slice rows")
        for row in rows:
            for field in REVIEW_FIELDS:
                require(row.get(field, "") == "", f"{path} row {row['review_id']} review field {field} is not blank")
        all_sheet_ids.extend(row["review_id"] for row in rows)

    packet_ids = [row["review_id"] for row in packet_rows]
    require(sorted(all_sheet_ids) == sorted(packet_ids), "native-review sheets do not cover exactly the full packet")


def validate_index(out_dir: Path) -> None:
    path = out_dir / "index.html"
    require(path.exists(), f"missing native-review sheet index {path}")
    text = path.read_text(encoding="utf-8")
    for coverage_slice in EXPECTED_SLICES:
        require(sheet_filename(coverage_slice) in text, f"index missing {coverage_slice} sheet link")
    require("two independent reviewers per slice" in text, "index missing independent-review guidance")
    require("scripts/merge_review_exports.py" in text, "index missing merge-review guidance")


def validate_readme(out_dir: Path) -> None:
    path = out_dir / "README.md"
    require(path.exists(), f"missing native-review sheet README {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    for phrase in (
        "generated from the v0.3 coverage native-review",
        "merge_review_exports.py",
        "coverage_native_review_packet_v03_double_completed.csv",
        "analyze_coverage_native_review_adjudication.py",
        "validate_completed_coverage_native_review_v03.py",
        "before making any completed-native-validation claim",
    ):
        require(phrase in normalized, f"README missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=Path("data/coverage_native_review_v03/coverage_native_review_packet_v03.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("data/coverage_native_review_v03/review_sheets_v03"))
    args = parser.parse_args()

    packet_rows = read_csv(args.packet)
    require(packet_rows, "v0.3 coverage native-review packet is empty")
    validate_rows(packet_rows, args.out_dir)
    validate_index(args.out_dir)
    validate_readme(args.out_dir)
    print(f"coverage native-review sheet validation passed for {args.out_dir}")


if __name__ == "__main__":
    main()
