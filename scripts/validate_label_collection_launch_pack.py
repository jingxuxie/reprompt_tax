#!/usr/bin/env python
"""Validate the consolidated label-collection launch pack."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


EXPECTED_SURFACES = {
    "human_audit_v02": {"rows": "72", "slots": "3", "sheets": "3"},
    "current_model_human_audit_v02": {"rows": "48", "slots": "3", "sheets": "3"},
    "coverage_native_review_v03": {"rows": "60", "slots": "12", "sheets": "6"},
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing launch-pack table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_surfaces(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == len(EXPECTED_SURFACES), f"expected {len(EXPECTED_SURFACES)} launch surfaces, found {len(rows)}")
    by_id = {row["surface_id"]: row for row in rows}
    require(set(by_id) == set(EXPECTED_SURFACES), f"unexpected launch surfaces: {sorted(by_id)}")
    for surface_id, expected in EXPECTED_SURFACES.items():
        row = by_id[surface_id]
        require(row["status"] == "launch_ready_needs_labels", f"{surface_id} has unexpected status {row['status']}")
        require(row["packet_rows"] == expected["rows"], f"{surface_id} row count mismatch")
        require(row["roster_template_slots"] == expected["slots"], f"{surface_id} roster slot mismatch")
        require(row["review_sheet_count"] == expected["sheets"], f"{surface_id} sheet count mismatch")
        require(row["preferred_independent_labels_per_item"] == "2", f"{surface_id} should prefer two independent labels")
        require("do_not_claim_completed" in row["claim_boundary"], f"{surface_id} missing claim boundary")
        for field in ("packet", "roster_template", "review_sheet_index", "launch_checklist", "design_report", "validator", "summarizer"):
            require(row[field], f"{surface_id} missing {field}")


def check_files(path: Path) -> None:
    rows = read_csv(path)
    counts = Counter(row["surface_id"] for row in rows)
    require(set(counts) == set(EXPECTED_SURFACES), f"file table has unexpected surfaces: {counts}")
    require(all(count >= 6 for count in counts.values()), f"each surface should list core files: {counts}")
    for row in rows:
        require(row["exists"] == "True", f"{row['path']} not marked present")
        require(Path(row["path"]).exists(), f"launch-pack file missing on disk: {row['path']}")
        require(int(row["bytes"]) > 0, f"launch-pack file is empty: {row['path']}")


def check_commands(path: Path) -> None:
    rows = read_csv(path)
    counts = Counter(row["surface_id"] for row in rows)
    require(counts == Counter({surface_id: 5 for surface_id in EXPECTED_SURFACES}), f"unexpected command counts: {counts}")
    roles_by_surface: dict[str, set[str]] = {surface_id: set() for surface_id in EXPECTED_SURFACES}
    commands_by_surface_role: dict[tuple[str, str], str] = {}
    for row in rows:
        roles_by_surface[row["surface_id"]].add(row["command_role"])
        require(row["command"].startswith("conda run -n reprompt_tax python scripts/"), f"unexpected command prefix: {row['command']}")
        commands_by_surface_role[(row["surface_id"], row["command_role"])] = row["command"]
    expected_roles = {
        "merge_single_label_exports",
        "validate_finalized_labels",
        "summarize_finalized_labels",
        "analyze_double_labels",
        "finalize_adjudicated_labels",
    }
    for surface_id, roles in roles_by_surface.items():
        require(roles == expected_roles, f"{surface_id} command roles mismatch: {roles}")

    required_fragments = {
        ("human_audit_v02", "analyze_double_labels"): [
            "--answer-key data/human_audit/human_audit_answer_key_v0.2.csv",
            "--annotator-roster data/human_audit/human_audit_annotator_roster_v0.2.csv",
            "--out-dir results/tables/human_audit_v0.2_adjudication",
            "--out-md paper/human_audit_adjudication_v02.md",
        ],
        ("human_audit_v02", "finalize_adjudicated_labels"): [
            "--answer-key data/human_audit/human_audit_answer_key_v0.2.csv",
            "--annotator-roster data/human_audit/human_audit_annotator_roster_v0.2.csv",
            "--source-out results/tables/human_audit_v0.2_adjudication/human_audit_final_label_sources.csv",
        ],
        ("current_model_human_audit_v02", "analyze_double_labels"): [
            "--answer-key data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv",
            "--annotator-roster data/current_model_human_audit/human_audit_annotator_roster_v0.2_current_gpt5.csv",
            "--expected-models gpt-5.4-mini,gpt-5.5",
            "--out-dir results/tables/current_model_human_audit_v0.2_adjudication",
            "--out-md paper/human_audit_adjudication_v02_current_gpt5.md",
        ],
        ("current_model_human_audit_v02", "finalize_adjudicated_labels"): [
            "--answer-key data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv",
            "--annotator-roster data/current_model_human_audit/human_audit_annotator_roster_v0.2_current_gpt5.csv",
            "--expected-models gpt-5.4-mini,gpt-5.5",
            "--source-out results/tables/current_model_human_audit_v0.2_adjudication/human_audit_final_label_sources.csv",
        ],
        ("coverage_native_review_v03", "analyze_double_labels"): [
            "--launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv",
            "--reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv",
            "--out-dir results/tables/coverage_native_review_v03_adjudication",
            "--out-md paper/coverage_native_review_adjudication_v03.md",
        ],
        ("coverage_native_review_v03", "finalize_adjudicated_labels"): [
            "--launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv",
            "--reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv",
            "--source-out results/tables/coverage_native_review_v03_adjudication/coverage_native_review_final_label_sources.csv",
        ],
    }
    for key, fragments in required_fragments.items():
        command = commands_by_surface_role[key]
        for fragment in fragments:
            require(fragment in command, f"{key[0]} {key[1]} missing command fragment: {fragment}")


def check_markdown(path: Path) -> None:
    require(path.exists(), f"missing launch-pack report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "Label Collection Launch Pack",
        "Surfaces ready for label collection: 3",
        "Reviewer-facing packet rows: 180",
        "Roster template slots: 18",
        "Sendable reviewer bundles",
        "not completed human/native validation",
        "do not claim completed human/native validation",
        "build_label_collection_bundles.py",
        "validate_label_collection_bundles.py",
        "Merge returned slice exports with `scripts/merge_review_exports.py`",
        "analyze_completed_label_claim_gates.py",
        "validate_completed_label_claim_gates.py",
        "two-reviewer adjudication finalization",
        "completed-label validators reject missing or contradictory reason codes",
        "Keep answer keys and automatic labels away from reviewers",
    ]
    for phrase in required:
        require(phrase in normalized, f"launch-pack report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/label_collection_launch_pack_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/label_collection_launch_pack_v02.md"))
    args = parser.parse_args()

    check_surfaces(args.out_dir / "label_collection_surfaces.csv")
    check_files(args.out_dir / "label_collection_files.csv")
    check_commands(args.out_dir / "label_collection_commands.csv")
    check_markdown(args.report)
    print("label-collection launch-pack validation passed")


if __name__ == "__main__":
    main()
