#!/usr/bin/env python
"""Preflight expected human/native label returns before merge commands run."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Any


OUT_DIR = Path("results/tables/label_return_preflight_v02")
OUT_MD = Path("paper/label_return_preflight_v02.md")
SINGLE_ASSIGNMENTS = Path("results/tables/label_collection_operator_handoff_v02/operator_dispatch_assignments.csv")
DOUBLE_ASSIGNMENTS = Path("results/tables/label_collection_operator_handoff_v02/operator_double_label_assignments.csv")

SURFACE_CONFIG = {
    "current_model_human_audit_v02": {
        "surface_label": "Current-model GPT-5.x human/native audit",
        "launch_packet": Path("data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv"),
        "roster_path": Path("data/current_model_human_audit/human_audit_annotator_roster_v0.2_current_gpt5.csv"),
        "priority": "1",
    },
    "human_audit_v02": {
        "surface_label": "Original v0.2 human/native audit",
        "launch_packet": Path("data/human_audit/human_audit_packet_v0.2.csv"),
        "roster_path": Path("data/human_audit/human_audit_annotator_roster_v0.2.csv"),
        "priority": "2",
    },
    "coverage_native_review_v03": {
        "surface_label": "v0.3 coverage native review",
        "launch_packet": Path("data/coverage_native_review_v03/coverage_native_review_packet_v03.csv"),
        "roster_path": Path("data/coverage_native_review_v03/coverage_native_review_roster_v03.csv"),
        "priority": "3",
    },
}

WORKFLOW_LABELS = {
    "minimum_single_label": "minimum single-label workflow",
    "preferred_double_label": "preferred double-label workflow",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing label-return preflight input {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_csv_header_and_count(path: Path) -> tuple[list[str], int]:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    return fieldnames, len(rows)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, f"refusing to write empty preflight table {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def bool_text(value: bool) -> str:
    return "True" if value else "False"


def load_launch_headers() -> dict[str, list[str]]:
    headers: dict[str, list[str]] = {}
    for surface_id, config in SURFACE_CONFIG.items():
        launch_path = config["launch_packet"]
        header, count = read_csv_header_and_count(launch_path)
        require(header, f"{launch_path} has no header")
        require(count > 0, f"{launch_path} has no rows")
        headers[surface_id] = header
    return headers


def file_status(row: dict[str, str], *, expected_header: list[str]) -> dict[str, Any]:
    path = Path(row["expected_return_path"])
    expected_rows = int(row["rows"])
    if not path.exists():
        return {
            "dispatch_priority": row["dispatch_priority"],
            "surface_id": row["surface_id"],
            "slice_id": row["slice_id"],
            "workflow_mode": row["workflow_mode"],
            "reviewer_index": row["reviewer_index"],
            "expected_rows": expected_rows,
            "expected_return_path": row["expected_return_path"],
            "file_present": "False",
            "observed_rows": "",
            "header_status": "missing_file",
            "row_count_status": "missing_file",
            "ready_for_merge_shape": "False",
            "blocker": "missing returned CSV",
        }

    header, observed_rows = read_csv_header_and_count(path)
    header_ok = header == expected_header
    rows_ok = observed_rows == expected_rows
    ready = header_ok and rows_ok
    blockers: list[str] = []
    if not header_ok:
        blockers.append("header differs from launch packet")
    if not rows_ok:
        blockers.append(f"expected {expected_rows} rows, found {observed_rows}")
    return {
        "dispatch_priority": row["dispatch_priority"],
        "surface_id": row["surface_id"],
        "slice_id": row["slice_id"],
        "workflow_mode": row["workflow_mode"],
        "reviewer_index": row["reviewer_index"],
        "expected_rows": expected_rows,
        "expected_return_path": row["expected_return_path"],
        "file_present": "True",
        "observed_rows": observed_rows,
        "header_status": "ok" if header_ok else "mismatch",
        "row_count_status": "ok" if rows_ok else "mismatch",
        "ready_for_merge_shape": bool_text(ready),
        "blocker": "none" if ready else "; ".join(blockers),
    }


def build_file_rows(single_rows: list[dict[str, str]], double_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    headers = load_launch_headers()
    out: list[dict[str, Any]] = []
    for row in [*single_rows, *double_rows]:
        surface_id = row["surface_id"]
        require(surface_id in SURFACE_CONFIG, f"unknown surface {surface_id}")
        out.append(file_status(row, expected_header=headers[surface_id]))
    return out


def next_action_for_group(*, missing: int, bad_shape: int, roster_present: bool, ready: bool) -> str:
    if ready:
        return "run the merge command, then completed-label validation and summaries before any claim update"
    blockers: list[str] = []
    if missing:
        blockers.append(f"collect {missing} missing return file(s)")
    if bad_shape:
        blockers.append(f"fix {bad_shape} return file(s) with header or row-count mismatch")
    if not roster_present:
        blockers.append("create the filled qualified reviewer roster")
    return "; ".join(blockers)


def build_summary_rows(file_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_group: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in file_rows:
        by_group[(row["surface_id"], row["workflow_mode"])].append(row)

    out: list[dict[str, Any]] = []
    for surface_id, config in SURFACE_CONFIG.items():
        for workflow_mode in WORKFLOW_LABELS:
            rows = by_group[(surface_id, workflow_mode)]
            require(rows, f"missing preflight group {surface_id}:{workflow_mode}")
            expected = len(rows)
            present = sum(row["file_present"] == "True" for row in rows)
            shape_ready = sum(row["ready_for_merge_shape"] == "True" for row in rows)
            missing = expected - present
            bad_shape = present - shape_ready
            roster_path = config["roster_path"]
            roster_present = roster_path.exists()
            ready = missing == 0 and bad_shape == 0 and roster_present
            out.append(
                {
                    "dispatch_priority": config["priority"],
                    "surface_id": surface_id,
                    "surface_label": config["surface_label"],
                    "workflow_mode": workflow_mode,
                    "workflow_label": WORKFLOW_LABELS[workflow_mode],
                    "expected_return_files": expected,
                    "present_return_files": present,
                    "shape_ready_return_files": shape_ready,
                    "missing_return_files": missing,
                    "bad_shape_return_files": bad_shape,
                    "roster_path": str(roster_path),
                    "roster_present": bool_text(roster_present),
                    "ready_to_merge": bool_text(ready),
                    "claim_decision": "no_claim_until_completed_label_validators_pass",
                    "next_action": next_action_for_group(
                        missing=missing,
                        bad_shape=bad_shape,
                        roster_present=roster_present,
                        ready=ready,
                    ),
                }
            )
    return out


def write_markdown(path: Path, file_rows: list[dict[str, Any]], summary_rows: list[dict[str, Any]]) -> None:
    present_files = sum(row["file_present"] == "True" for row in file_rows)
    ready_workflows = sum(row["ready_to_merge"] == "True" for row in summary_rows)
    present_rosters = sum(row["roster_present"] == "True" for row in summary_rows)
    lines = [
        "# Label Return Preflight",
        "",
        "This no-API preflight checks whether expected reviewer return files and",
        "qualified roster files are present before merge and completed-label",
        "validation commands run. It is operational support, not completed",
        "human/native validation.",
        "",
        "## Summary",
        "",
        f"- Workflow surfaces checked: {len(summary_rows)}",
        f"- Expected return CSV files: {len(file_rows)}",
        f"- Present return CSV files: {present_files}",
        f"- Qualified roster files present: {present_rosters}/{len(summary_rows)} workflow checks",
        f"- Workflows ready to merge: {ready_workflows}",
        "- OpenAI API calls: 0",
        "- Claim boundary: no human/native-validation claim is unlocked until",
        "  merge, completed-label validation, summaries, and claim gates pass.",
        "",
        "## Workflow Preflight",
        "",
        "| Priority | Surface | Workflow | Expected returns | Present | Roster present | Ready to merge | Next action |",
        "|---:|---|---|---:|---:|---|---|---|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['dispatch_priority']} | `{row['surface_id']}` | {row['workflow_mode']} | "
            f"{row['expected_return_files']} | {row['present_return_files']} | {row['roster_present']} | "
            f"{row['ready_to_merge']} | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Return File Checklist",
            "",
            "| Surface | Workflow | Slice | Reviewer | Expected return | Present | Shape ready | Blocker |",
            "|---|---|---|---:|---|---|---|---|",
        ]
    )
    for row in file_rows:
        lines.append(
            f"| `{row['surface_id']}` | {row['workflow_mode']} | `{row['slice_id']}` | "
            f"{row['reviewer_index']} | `{row['expected_return_path']}` | {row['file_present']} | "
            f"{row['ready_for_merge_shape']} | {row['blocker']} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--single-assignments", type=Path, default=SINGLE_ASSIGNMENTS)
    parser.add_argument("--double-assignments", type=Path, default=DOUBLE_ASSIGNMENTS)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    single_rows = read_csv(args.single_assignments)
    double_rows = read_csv(args.double_assignments)
    file_rows = build_file_rows(single_rows, double_rows)
    summary_rows = build_summary_rows(file_rows)
    write_csv(args.out_dir / "label_return_preflight_files.csv", file_rows)
    write_csv(args.out_dir / "label_return_preflight_summary.csv", summary_rows)
    write_markdown(args.out_md, file_rows, summary_rows)
    print(f"wrote label-return preflight to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
