#!/usr/bin/env python
"""Validate label-collection priority artifacts."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


EXPECTED_PRIORITY = {
    "current_model_human_audit_v02": {
        "priority_rank": "1",
        "packet_rows": "48",
        "reviewer_bundle_count": "3",
        "qualified_reviewer_slots": "3",
        "completion_threshold": "44/48 pass agreements; 204/240 component agreements",
        "claim_gate_surface": "human_audit_v02_current_gpt5",
    },
    "human_audit_v02": {
        "priority_rank": "2",
        "packet_rows": "72",
        "reviewer_bundle_count": "3",
        "qualified_reviewer_slots": "3",
        "completion_threshold": "65/72 pass agreements; 306/360 component agreements",
        "claim_gate_surface": "human_audit_v02_gpt41_family",
    },
    "coverage_native_review_v03": {
        "priority_rank": "3",
        "packet_rows": "60",
        "reviewer_bundle_count": "6",
        "qualified_reviewer_slots": "12",
        "completion_threshold": "60/60 release-usable rows",
        "claim_gate_surface": "coverage_native_review_v03",
    },
}

EXPECTED_SLICE_COUNTS = {
    "current_model_human_audit_v02": {"slices": 3, "rows": 48},
    "human_audit_v02": {"slices": 3, "rows": 72},
    "coverage_native_review_v03": {"slices": 6, "rows": 60},
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing label-priority table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_priority(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == len(EXPECTED_PRIORITY), f"unexpected priority row count: {len(rows)}")
    by_surface = {row["surface_id"]: row for row in rows}
    require(set(by_surface) == set(EXPECTED_PRIORITY), f"unexpected priority surfaces: {sorted(by_surface)}")
    ranks = [int(row["priority_rank"]) for row in rows]
    require(ranks == [1, 2, 3], f"priority rows are not in ranked order: {ranks}")
    for surface_id, expected in EXPECTED_PRIORITY.items():
        row = by_surface[surface_id]
        for field, value in expected.items():
            require(row[field] == value, f"{surface_id} {field} mismatch: expected {value}, got {row[field]}")
        require(row["claim_gate_status"] == "needs_labels", f"{surface_id} should still need labels")
        require(row["claim_decision"] == "no_claim", f"{surface_id} should not unlock a claim")
        require(row["preferred_independent_labels_per_item"] == "2", f"{surface_id} should prefer two independent labels")
        require(row["minimum_single_label_exports"] == expected["reviewer_bundle_count"], f"{surface_id} single-label export count mismatch")
        require(row["stronger_double_label_rows"] == str(int(expected["packet_rows"]) * 2), f"{surface_id} double-label row count mismatch")
        require("no_completed_human_or_native_validation_claim" in row["claim_boundary"], f"{surface_id} missing claim boundary")
        require(row["recommended_next_action"], f"{surface_id} missing next action")
        require(row["rationale"], f"{surface_id} missing rationale")


def check_slices(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == sum(item["slices"] for item in EXPECTED_SLICE_COUNTS.values()), f"unexpected slice row count: {len(rows)}")
    counts = Counter(row["surface_id"] for row in rows)
    require(counts == Counter({surface: spec["slices"] for surface, spec in EXPECTED_SLICE_COUNTS.items()}), f"slice counts mismatch: {counts}")
    for surface_id, spec in EXPECTED_SLICE_COUNTS.items():
        surface_rows = [row for row in rows if row["surface_id"] == surface_id]
        require(sum(int(row["expected_rows"]) for row in surface_rows) == spec["rows"], f"{surface_id} slice rows mismatch")
        require(all(row["bundle_ready"] == "True" for row in surface_rows), f"{surface_id} has unready bundles")
        require(len({row["expected_export_name"] for row in surface_rows}) == len(surface_rows), f"{surface_id} duplicate export names")
        for row in surface_rows:
            require(Path(row["bundle_path"]).exists(), f"missing bundle path {row['bundle_path']}")
            require(row["expected_export_name"].endswith("_completed.csv"), f"{surface_id} export should be completed CSV")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing label-priority report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "Label Collection Priority Audit",
        "no-API audit",
        "not completed human/native validation",
        "Prioritize `current_model_human_audit_v02` first",
        "three 16-row language bundles",
        "GPT-5.x current-model headline",
        "Collect `human_audit_v02` second",
        "Collect `coverage_native_review_v03` after the human audits",
        "Reviewer-facing rows: 180",
        "Ready reviewer bundles: 12",
        "Minimum completion path: one qualified completed export per slice",
        "Stronger path: two independent labels per item",
        "no completed human/native-validation claim is unlocked",
        "scripts/analyze_completed_label_claim_gates.py",
        "scripts/validate_completed_label_claim_gates.py",
    ]
    for phrase in required:
        require(phrase in normalized, f"label-priority report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/label_collection_priority_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/label_collection_priority_v02.md"))
    args = parser.parse_args()

    check_priority(args.out_dir / "label_collection_priority.csv")
    check_slices(args.out_dir / "label_collection_priority_by_slice.csv")
    check_report(args.report)
    print("label-collection priority validation passed")


if __name__ == "__main__":
    main()
