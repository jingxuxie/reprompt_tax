#!/usr/bin/env python
"""Validate generated human-audit review sheets."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


LANGUAGE_PAIRS = ("ar-en", "es-en", "hi-en")
PRIVATE_MARKERS = (
    "item_id",
    "auto_pass",
    "auto_language_pass",
    "auto_script_pass",
    "auto_preservation_pass",
    "auto_task_pass",
    "auto_register_locale_pass",
    "auto_failure_types",
)
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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sheet_filename(version: str, language_pair: str) -> str:
    return f"human_audit_review_sheet_{version}_{language_pair}.html"


def extract_rows(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r'<script id="audit-data" type="application/json">(.*?)</script>', text, flags=re.DOTALL)
    require(match is not None, f"{path} missing audit-data JSON")
    payload = match.group(1).replace("<\\/", "</")
    rows = json.loads(payload)
    require(isinstance(rows, list), f"{path} audit-data must be a list")
    return rows


def validate_sheet_text(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for marker in PRIVATE_MARKERS:
        require(marker not in text, f"{path} leaks private marker {marker}")
    for phrase in ("Download CSV", "human failure types", "same ID as roster"):
        require(phrase in text, f"{path} missing phrase {phrase!r}")
    for field in ANNOTATION_FIELDS:
        require(field in text, f"{path} missing annotation field {field}")


def validate_rows(packet_rows: list[dict[str, str]], out_dir: Path, version: str) -> None:
    packet_by_lang = {lang: [row for row in packet_rows if row["language_pair"] == lang] for lang in LANGUAGE_PAIRS}
    all_sheet_ids: list[str] = []
    for language_pair in LANGUAGE_PAIRS:
        path = out_dir / sheet_filename(version, language_pair)
        require(path.exists(), f"missing review sheet {path}")
        validate_sheet_text(path)
        rows = extract_rows(path)
        expected_rows = len(packet_by_lang[language_pair])
        require(len(rows) == expected_rows, f"{path} expected {expected_rows} rows, found {len(rows)}")
        require([row["audit_id"] for row in rows] == [row["audit_id"] for row in packet_by_lang[language_pair]], f"{path} audit IDs do not match packet slice")
        require(all(row["language_pair"] == language_pair for row in rows), f"{path} contains wrong language_pair rows")
        for row in rows:
            for field in ANNOTATION_FIELDS:
                require(row.get(field, "") == "", f"{path} row {row['audit_id']} annotation field {field} is not blank")
        all_sheet_ids.extend(row["audit_id"] for row in rows)

    packet_ids = [row["audit_id"] for row in packet_rows]
    require(sorted(all_sheet_ids) == sorted(packet_ids), "review sheets do not cover exactly the full packet")


def validate_index(out_dir: Path, version: str) -> None:
    path = out_dir / "index.html"
    require(path.exists(), f"missing review-sheet index {path}")
    text = path.read_text(encoding="utf-8")
    for language_pair in LANGUAGE_PAIRS:
        require(sheet_filename(version, language_pair) in text, f"index missing {language_pair} sheet link")
    require("private answer key is not needed" in text, "index missing answer-key privacy note")
    require("scripts/merge_review_exports.py" in text, "index missing merge-review guidance")


def validate_readme(out_dir: Path, version: str) -> None:
    path = out_dir / "README.md"
    require(path.exists(), f"missing review-sheet README {path}")
    text = path.read_text(encoding="utf-8")
    for phrase in (
        "generated from the blinded launch packet",
        f"human_audit_answer_key_{version}.csv",
        "merge_review_exports.py",
        "validate_completed_human_audit.py",
        "before making any human/native-speaker validation claim",
    ):
        require(phrase in text, f"README missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=Path("data/human_audit/human_audit_packet_v0.2.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("data/human_audit/review_sheets_v0.2"))
    parser.add_argument("--packet-version", default="v0.2")
    args = parser.parse_args()

    packet_rows = read_csv(args.packet)
    require(packet_rows, "packet is empty")
    validate_rows(packet_rows, args.out_dir, args.packet_version)
    validate_index(args.out_dir, args.packet_version)
    validate_readme(args.out_dir, args.packet_version)
    print(f"human-audit review-sheet validation passed for {args.out_dir}")


if __name__ == "__main__":
    main()
