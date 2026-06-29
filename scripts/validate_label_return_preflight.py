#!/usr/bin/env python
"""Validate the label-return preflight artifacts for the current no-label state."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


EXPECTED_FILE_COUNTS = {
    ("current_model_human_audit_v02", "minimum_single_label"): 3,
    ("current_model_human_audit_v02", "preferred_double_label"): 6,
    ("human_audit_v02", "minimum_single_label"): 3,
    ("human_audit_v02", "preferred_double_label"): 6,
    ("coverage_native_review_v03", "minimum_single_label"): 6,
    ("coverage_native_review_v03", "preferred_double_label"): 12,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing label-return preflight artifact {path}")
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    require(rows, f"empty label-return preflight artifact {path}")
    return rows


def check_files(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == sum(EXPECTED_FILE_COUNTS.values()), f"unexpected return file count: {len(rows)}")
    counts = Counter((row["surface_id"], row["workflow_mode"]) for row in rows)
    require(counts == Counter(EXPECTED_FILE_COUNTS), f"unexpected return files by workflow: {counts}")
    return_paths: set[str] = set()
    for row in rows:
        require(row["file_present"] == "False", f"{row['expected_return_path']} should not be present in the current no-label state")
        require(row["ready_for_merge_shape"] == "False", f"{row['expected_return_path']} should not be shape-ready")
        require(row["header_status"] == "missing_file", f"{row['expected_return_path']} should have missing-file header status")
        require(row["row_count_status"] == "missing_file", f"{row['expected_return_path']} should have missing-file row status")
        require(row["blocker"] == "missing returned CSV", f"{row['expected_return_path']} blocker mismatch")
        require(row["expected_return_path"].endswith("_completed.csv"), f"unexpected return filename {row['expected_return_path']}")
        if row["workflow_mode"] == "preferred_double_label":
            require("_reviewer" in row["expected_return_path"], f"double-label return path missing reviewer suffix: {row['expected_return_path']}")
        else:
            require("_reviewer" not in row["expected_return_path"], f"single-label return path should not use reviewer suffix: {row['expected_return_path']}")
        return_paths.add(row["expected_return_path"])
    require(len(return_paths) == len(rows), "duplicate expected return paths in preflight")


def check_summary(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == len(EXPECTED_FILE_COUNTS), f"unexpected preflight summary row count: {len(rows)}")
    by_key = {(row["surface_id"], row["workflow_mode"]): row for row in rows}
    require(set(by_key) == set(EXPECTED_FILE_COUNTS), f"unexpected preflight summary keys: {sorted(by_key)}")
    for key, expected_files in EXPECTED_FILE_COUNTS.items():
        row = by_key[key]
        require(row["expected_return_files"] == str(expected_files), f"{key} expected return count mismatch")
        require(row["present_return_files"] == "0", f"{key} should have zero returned files")
        require(row["shape_ready_return_files"] == "0", f"{key} should have zero shape-ready files")
        require(row["missing_return_files"] == str(expected_files), f"{key} missing return count mismatch")
        require(row["bad_shape_return_files"] == "0", f"{key} should have zero bad-shape present files")
        require(row["roster_present"] == "False", f"{key} should not have a filled roster in the current no-label state")
        require(row["ready_to_merge"] == "False", f"{key} should not be ready to merge")
        require(row["claim_decision"] == "no_claim_until_completed_label_validators_pass", f"{key} claim decision mismatch")
        require("collect" in row["next_action"], f"{key} next action should request missing returns")
        require("qualified reviewer roster" in row["next_action"], f"{key} next action should request roster")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing label-return preflight report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "Label Return Preflight",
        "operational support, not completed human/native validation",
        "Workflow surfaces checked: 6",
        "Expected return CSV files: 36",
        "Present return CSV files: 0",
        "Qualified roster files present: 0/6 workflow checks",
        "Workflows ready to merge: 0",
        "OpenAI API calls: 0",
        "no human/native-validation claim is unlocked",
        "minimum_single_label",
        "preferred_double_label",
        "missing returned CSV",
    ]
    for phrase in required:
        require(phrase in normalized, f"label-return preflight report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/label_return_preflight_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/label_return_preflight_v02.md"))
    args = parser.parse_args()

    check_files(args.out_dir / "label_return_preflight_files.csv")
    check_summary(args.out_dir / "label_return_preflight_summary.csv")
    check_report(args.report)
    print("label-return preflight validation passed")


if __name__ == "__main__":
    main()
