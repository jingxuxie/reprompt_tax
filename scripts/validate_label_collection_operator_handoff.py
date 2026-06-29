#!/usr/bin/env python
"""Validate the label-collection operator handoff artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
from collections import Counter
from pathlib import Path


EXPECTED_SURFACES = {
    "current_model_human_audit_v02": {"assignments": 3, "rows": 48, "priority": "1"},
    "human_audit_v02": {"assignments": 3, "rows": 72, "priority": "2"},
    "coverage_native_review_v03": {"assignments": 6, "rows": 60, "priority": "3"},
}
EXPECTED_DOUBLE_SURFACES = {
    surface_id: {
        "assignments": spec["assignments"] * 2,
        "rows": spec["rows"] * 2,
        "priority": spec["priority"],
    }
    for surface_id, spec in EXPECTED_SURFACES.items()
}

EXPECTED_COMMAND_ROLES = {
    "merge_single_label_exports",
    "validate_finalized_labels",
    "summarize_finalized_labels",
    "merge_double_label_exports",
    "analyze_double_labels",
    "finalize_adjudicated_labels",
}

PRIVATE_OUTGOING_MARKERS = (
    "answer_key",
    "automatic label",
    "automatic labels",
    "auto_pass",
    "model names",
    "prompt conditions",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing operator handoff table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_dispatch_assignments(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == sum(spec["assignments"] for spec in EXPECTED_SURFACES.values()), f"unexpected assignment count: {len(rows)}")
    counts = Counter(row["surface_id"] for row in rows)
    require(counts == Counter({surface: spec["assignments"] for surface, spec in EXPECTED_SURFACES.items()}), f"unexpected assignment surfaces: {counts}")
    row_counts = Counter()
    return_paths: set[str] = set()
    reviewer_slots: set[str] = set()
    for row in rows:
        spec = EXPECTED_SURFACES[row["surface_id"]]
        require(row["dispatch_priority"] == spec["priority"], f"{row['surface_id']} priority mismatch")
        require(row["workflow_mode"] == "minimum_single_label", f"{row['surface_id']} minimum assignment mode mismatch")
        require(row["reviewer_index"] == "1", f"{row['surface_id']} minimum assignment should use reviewer index 1")
        require(row["expected_return_path"].endswith("_completed.csv"), f"{row['surface_id']} return path is not completed CSV")
        require("_reviewer" not in row["expected_return_path"], f"{row['surface_id']} minimum return path should not use reviewer suffix")
        require(row["expected_export_name"] in row["expected_return_path"], f"{row['surface_id']} return/export mismatch")
        require(row["claim_boundary"] == "do_not_claim_completed_human_or_native_validation_until_finalized_labels_pass_gates", "claim boundary mismatch")
        bundle_path = Path(row["attach_bundle_path"])
        require(bundle_path.exists(), f"missing bundle {bundle_path}")
        require(sha256_file(bundle_path) == row["bundle_sha256"], f"bundle sha256 mismatch for {bundle_path}")
        lowered = row["outgoing_message"].lower()
        for marker in PRIVATE_OUTGOING_MARKERS:
            require(marker not in lowered, f"outgoing message leaks private marker {marker}")
        require(row["expected_export_name"] in row["outgoing_message"], f"{row['surface_id']} message missing expected export name")
        row_counts[row["surface_id"]] += int(row["rows"])
        return_paths.add(row["expected_return_path"])
        reviewer_slots.add(row["reviewer_slot"])
    require(len(return_paths) == len(rows), "duplicate expected return paths")
    require(len(reviewer_slots) == len(rows), "duplicate reviewer slots")
    require(row_counts == Counter({surface: spec["rows"] for surface, spec in EXPECTED_SURFACES.items()}), f"unexpected handoff row counts: {row_counts}")


def merge_double_commands(return_rows: list[dict[str, str]]) -> dict[str, str]:
    commands: dict[str, str] = {}
    for row in return_rows:
        if row["workflow_role"] == "merge_double_label_exports":
            commands[row["surface_id"]] = row["command"]
    require(set(commands) == set(EXPECTED_SURFACES), f"missing double-label merge commands: {sorted(commands)}")
    return commands


def check_double_label_assignments(path: Path, return_intake_path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == sum(spec["assignments"] for spec in EXPECTED_DOUBLE_SURFACES.values()), f"unexpected double-label assignment count: {len(rows)}")
    counts = Counter(row["surface_id"] for row in rows)
    require(
        counts == Counter({surface: spec["assignments"] for surface, spec in EXPECTED_DOUBLE_SURFACES.items()}),
        f"unexpected double-label assignment surfaces: {counts}",
    )
    commands = merge_double_commands(read_csv(return_intake_path))
    row_counts = Counter()
    per_slice_reviewers = Counter((row["surface_id"], row["slice_id"]) for row in rows)
    return_paths: set[str] = set()
    reviewer_slots: set[str] = set()
    for row in rows:
        spec = EXPECTED_DOUBLE_SURFACES[row["surface_id"]]
        require(row["dispatch_priority"] == spec["priority"], f"{row['surface_id']} priority mismatch")
        require(row["workflow_mode"] == "preferred_double_label", f"{row['surface_id']} double-label assignment mode mismatch")
        require(row["reviewer_index"] in {"1", "2"}, f"{row['surface_id']} double-label reviewer index mismatch")
        require(f"_reviewer{row['reviewer_index']}_completed.csv" in row["expected_return_path"], f"{row['surface_id']} double-label return path missing reviewer suffix")
        require(row["expected_export_name"] in row["expected_return_path"], f"{row['surface_id']} return/export mismatch")
        require(row["expected_return_path"] in commands[row["surface_id"]], f"{row['surface_id']} double-label merge command missing {row['expected_return_path']}")
        require(row["claim_boundary"] == "do_not_claim_completed_human_or_native_validation_until_finalized_labels_pass_gates", "claim boundary mismatch")
        bundle_path = Path(row["attach_bundle_path"])
        require(bundle_path.exists(), f"missing bundle {bundle_path}")
        require(sha256_file(bundle_path) == row["bundle_sha256"], f"bundle sha256 mismatch for {bundle_path}")
        lowered = row["outgoing_message"].lower()
        for marker in PRIVATE_OUTGOING_MARKERS:
            require(marker not in lowered, f"double-label outgoing message leaks private marker {marker}")
        require(row["expected_export_name"] in row["outgoing_message"], f"{row['surface_id']} message missing expected export name")
        row_counts[row["surface_id"]] += int(row["rows"])
        return_paths.add(row["expected_return_path"])
        reviewer_slots.add(row["reviewer_slot"])
    require(all(count == 2 for count in per_slice_reviewers.values()), f"each double-label slice should have two reviewer assignments: {per_slice_reviewers}")
    require(len(return_paths) == len(rows), "duplicate double-label expected return paths")
    require(len(reviewer_slots) == len(rows), "duplicate double-label reviewer slots")
    require(row_counts == Counter({surface: spec["rows"] for surface, spec in EXPECTED_DOUBLE_SURFACES.items()}), f"unexpected double-label row counts: {row_counts}")


def check_return_intake(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == len(EXPECTED_SURFACES) * len(EXPECTED_COMMAND_ROLES), f"unexpected return-intake row count: {len(rows)}")
    by_surface = Counter(row["surface_id"] for row in rows)
    require(all(count == len(EXPECTED_COMMAND_ROLES) for count in by_surface.values()), f"unexpected command counts by surface: {by_surface}")
    for surface_id, spec in EXPECTED_SURFACES.items():
        surface_rows = [row for row in rows if row["surface_id"] == surface_id]
        require(surface_rows, f"missing return-intake rows for {surface_id}")
        require({row["workflow_role"] for row in surface_rows} == EXPECTED_COMMAND_ROLES, f"{surface_id} command role mismatch")
        require(
            [row["step_order"] for row in sorted(surface_rows, key=lambda row: int(row["step_order"]))] == ["1", "2", "3", "4", "5", "6"],
            f"{surface_id} step order mismatch",
        )
        for row in surface_rows:
            require(row["dispatch_priority"] == spec["priority"], f"{surface_id} priority mismatch")
            require(row["claim_gate_status_before_labels"] == "needs_labels", f"{surface_id} should need labels before returns")
            require(row["claim_decision_before_labels"] == "no_claim", f"{surface_id} should remain no_claim before returns")
            if row["workflow_role"] in {"merge_single_label_exports", "validate_finalized_labels", "summarize_finalized_labels"}:
                require("missing completed inputs" in row["required_before_running"], f"{surface_id} missing completed-input blocker")
            require(row["command"].startswith("conda run -n reprompt_tax python scripts/"), f"{surface_id} command must be reproducible")
            if row["workflow_role"] == "merge_double_label_exports":
                require("--labels-per-item 2" in row["command"], f"{surface_id} double-label merge missing labels-per-item")
                require("_double_completed.csv" in row["command"], f"{surface_id} double-label merge missing double-completed output")
                require("reviewer1/reviewer2 completed slice exports" in row["required_before_running"], f"{surface_id} double-label merge missing reviewer-return prerequisite")
            if row["workflow_role"] == "analyze_double_labels":
                require("merge_double_label_exports" in row["required_before_running"], f"{surface_id} analyze-double row missing double-merge prerequisite")
            if row["workflow_role"] == "finalize_adjudicated_labels":
                require("filled adjudication packet" in row["required_before_running"], f"{surface_id} finalize row missing adjudication prerequisite")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing operator handoff report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "Label Collection Operator Handoff",
        "operational support, not completed human/native validation",
        "Minimum single-label reviewer assignments: 12",
        "Minimum reviewer-facing rows to collect: 180",
        "Preferred double-label reviewer assignments: 24",
        "Preferred double-label row judgments to collect: 360",
        "Preferred Double-Label Send Checklist",
        "reviewer1/reviewer2 return filenames",
        "First priority: current-model human/native audit",
        "OpenAI API calls: 0",
        "no human/native-validation claim is unlocked",
        "merge_double_label_exports",
        "current_model_human_audit_v02",
        "human_audit_v02",
        "coverage_native_review_v03",
        "analyze_double_labels",
        "finalize_adjudicated_labels",
    ]
    for phrase in required:
        require(phrase in normalized, f"operator handoff report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/label_collection_operator_handoff_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/label_collection_operator_handoff_v02.md"))
    args = parser.parse_args()

    check_dispatch_assignments(args.out_dir / "operator_dispatch_assignments.csv")
    check_double_label_assignments(
        args.out_dir / "operator_double_label_assignments.csv",
        args.out_dir / "operator_return_intake.csv",
    )
    check_return_intake(args.out_dir / "operator_return_intake.csv")
    check_report(args.report)
    print("label-collection operator handoff validation passed")


if __name__ == "__main__":
    main()
