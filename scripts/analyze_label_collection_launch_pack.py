#!/usr/bin/env python
"""Build a consolidated launch pack for all human/native label surfaces."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any


OUT_DIR = Path("results/tables/label_collection_launch_pack_v02")
OUT_MD = Path("paper/label_collection_launch_pack_v02.md")

SURFACES = [
    {
        "surface_id": "human_audit_v02",
        "claim_surface": "Original v0.2 human/native audit",
        "packet": Path("data/human_audit/human_audit_packet_v0.2.csv"),
        "roster_template": Path("data/human_audit/human_audit_annotator_roster_template_v0.2.csv"),
        "sheet_dir": Path("data/human_audit/review_sheets_v0.2"),
        "sheet_prefix": "human_audit_review_sheet_v0.2_",
        "sheet_count": 3,
        "launch_checklist": Path("data/human_audit/human_audit_launch_checklist_v0.2.md"),
        "design_report": Path("paper/human_audit_design_audit_v02.md"),
        "completed_path": Path("data/human_audit/human_audit_packet_v0.2_completed.csv"),
        "double_completed_path": Path("data/human_audit/human_audit_packet_v0.2_double_completed.csv"),
        "adjudication_packet": Path("results/tables/human_audit_v0.2_adjudication/human_audit_adjudication_packet.csv"),
        "finalized_path": Path("data/human_audit/human_audit_packet_v0.2_adjudicated_completed.csv"),
        "validator": "scripts/validate_completed_human_audit.py",
        "summarizer": "scripts/summarize_human_audit.py",
        "adjudication_analyzer": "scripts/analyze_human_audit_adjudication.py",
        "adjudication_finalizer": "scripts/finalize_human_audit_adjudication.py",
        "expected_rows": 72,
        "minimum_reviewer_slots": 3,
        "preferred_independent_labels_per_item": 2,
        "status": "launch_ready_needs_labels",
    },
    {
        "surface_id": "current_model_human_audit_v02",
        "claim_surface": "Current-model GPT-5.x human/native audit",
        "packet": Path("data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv"),
        "roster_template": Path("data/current_model_human_audit/human_audit_annotator_roster_template_v0.2_current_gpt5.csv"),
        "sheet_dir": Path("data/current_model_human_audit/review_sheets_v0.2_current_gpt5"),
        "sheet_prefix": "human_audit_review_sheet_v0.2_current_gpt5_",
        "sheet_count": 3,
        "launch_checklist": Path("data/current_model_human_audit/human_audit_launch_checklist_v0.2_current_gpt5.md"),
        "design_report": Path("paper/current_model_human_audit_design_v02.md"),
        "completed_path": Path("data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_completed.csv"),
        "double_completed_path": Path("data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_double_completed.csv"),
        "adjudication_packet": Path("results/tables/current_model_human_audit_v0.2_adjudication/human_audit_adjudication_packet.csv"),
        "finalized_path": Path("data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_adjudicated_completed.csv"),
        "validator": "scripts/validate_completed_human_audit.py",
        "summarizer": "scripts/summarize_human_audit.py",
        "adjudication_analyzer": "scripts/analyze_human_audit_adjudication.py",
        "adjudication_finalizer": "scripts/finalize_human_audit_adjudication.py",
        "expected_rows": 48,
        "minimum_reviewer_slots": 3,
        "preferred_independent_labels_per_item": 2,
        "status": "launch_ready_needs_labels",
    },
    {
        "surface_id": "coverage_native_review_v03",
        "claim_surface": "v0.3 coverage native review",
        "packet": Path("data/coverage_native_review_v03/coverage_native_review_packet_v03.csv"),
        "roster_template": Path("data/coverage_native_review_v03/coverage_native_review_roster_template_v03.csv"),
        "sheet_dir": Path("data/coverage_native_review_v03/review_sheets_v03"),
        "sheet_prefix": "coverage_native_review_sheet_v03_",
        "sheet_count": 6,
        "launch_checklist": Path("data/coverage_native_review_v03/coverage_native_review_launch_checklist_v03.md"),
        "design_report": Path("paper/coverage_native_review_design_v03.md"),
        "completed_path": Path("data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv"),
        "double_completed_path": Path("data/coverage_native_review_v03/coverage_native_review_packet_v03_double_completed.csv"),
        "adjudication_packet": Path("results/tables/coverage_native_review_v03_adjudication/coverage_native_review_adjudication_packet.csv"),
        "finalized_path": Path("data/coverage_native_review_v03/coverage_native_review_packet_v03_adjudicated_completed.csv"),
        "validator": "scripts/validate_completed_coverage_native_review_v03.py",
        "summarizer": "scripts/summarize_coverage_native_review_v03.py",
        "adjudication_analyzer": "scripts/analyze_coverage_native_review_adjudication.py",
        "adjudication_finalizer": "scripts/finalize_coverage_native_review_adjudication.py",
        "expected_rows": 60,
        "minimum_reviewer_slots": 12,
        "preferred_independent_labels_per_item": 2,
        "status": "launch_ready_needs_labels",
    },
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


def count_sheet_files(sheet_dir: Path, sheet_prefix: str) -> int:
    require(sheet_dir.exists(), f"missing review sheet directory {sheet_dir}")
    return len([path for path in sheet_dir.glob("*.html") if path.name.startswith(sheet_prefix)])


def build_surface_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for surface in SURFACES:
        packet_rows = read_csv(surface["packet"])
        roster_rows = read_csv(surface["roster_template"])
        sheet_count = count_sheet_files(surface["sheet_dir"], surface["sheet_prefix"])
        require(len(packet_rows) == surface["expected_rows"], f"{surface['surface_id']} expected {surface['expected_rows']} packet rows, found {len(packet_rows)}")
        require(len(roster_rows) >= surface["minimum_reviewer_slots"], f"{surface['surface_id']} roster template has too few slots")
        require(sheet_count == surface["sheet_count"], f"{surface['surface_id']} expected {surface['sheet_count']} review sheets, found {sheet_count}")
        rows.append(
            {
                "surface_id": surface["surface_id"],
                "claim_surface": surface["claim_surface"],
                "status": surface["status"],
                "packet_rows": len(packet_rows),
                "roster_template_slots": len(roster_rows),
                "review_sheet_count": sheet_count,
                "preferred_independent_labels_per_item": surface["preferred_independent_labels_per_item"],
                "packet": str(surface["packet"]),
                "roster_template": str(surface["roster_template"]),
                "review_sheet_index": str(surface["sheet_dir"] / "index.html"),
                "launch_checklist": str(surface["launch_checklist"]),
                "design_report": str(surface["design_report"]),
                "completed_path": str(surface["completed_path"]),
                "double_completed_path": str(surface["double_completed_path"]),
                "adjudication_packet": str(surface["adjudication_packet"]),
                "finalized_path": str(surface["finalized_path"]),
                "validator": surface["validator"],
                "summarizer": surface["summarizer"],
                "adjudication_analyzer": surface["adjudication_analyzer"],
                "adjudication_finalizer": surface["adjudication_finalizer"],
                "claim_boundary": "do_not_claim_completed_human_or_native_validation_until_finalized_labels_pass_gates",
            }
        )
    return rows


def build_file_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for surface in SURFACES:
        files = [
            ("packet", surface["packet"]),
            ("roster_template", surface["roster_template"]),
            ("review_sheet_index", surface["sheet_dir"] / "index.html"),
            ("review_sheet_readme", surface["sheet_dir"] / "README.md"),
            ("launch_checklist", surface["launch_checklist"]),
            ("design_report", surface["design_report"]),
        ]
        for role, path in files:
            require(path.exists(), f"missing {surface['surface_id']} launch-pack file {path}")
            rows.append(
                {
                    "surface_id": surface["surface_id"],
                    "file_role": role,
                    "path": str(path),
                    "exists": True,
                    "bytes": path.stat().st_size,
                }
            )
    return rows


def build_command_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for surface in SURFACES:
        if surface["surface_id"] == "human_audit_v02":
            merge_args = "--mode human_audit --launch-packet data/human_audit/human_audit_packet_v0.2.csv --out data/human_audit/human_audit_packet_v0.2_completed.csv --inputs data/human_audit/human_audit_packet_v0.2_ar-en_completed.csv data/human_audit/human_audit_packet_v0.2_es-en_completed.csv data/human_audit/human_audit_packet_v0.2_hi-en_completed.csv"
            validate_args = "--annotations data/human_audit/human_audit_packet_v0.2_completed.csv --answer-key data/human_audit/human_audit_answer_key_v0.2.csv --annotator-roster data/human_audit/human_audit_annotator_roster_v0.2.csv"
            summarize_args = "--annotations data/human_audit/human_audit_packet_v0.2_completed.csv --answer-key data/human_audit/human_audit_answer_key_v0.2.csv --out-dir results/tables/human_audit_v0.2"
        elif surface["surface_id"] == "current_model_human_audit_v02":
            merge_args = "--mode human_audit --launch-packet data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv --out data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_completed.csv --inputs data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_ar-en_completed.csv data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_es-en_completed.csv data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_hi-en_completed.csv"
            validate_args = "--annotations data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_completed.csv --answer-key data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv --annotator-roster data/current_model_human_audit/human_audit_annotator_roster_v0.2_current_gpt5.csv --expected-models gpt-5.4-mini,gpt-5.5"
            summarize_args = "--annotations data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_completed.csv --answer-key data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv --out-dir results/tables/human_audit_v0.2_current_gpt5 --expected-models gpt-5.4-mini,gpt-5.5"
        else:
            merge_args = "--mode coverage_native_review --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv --out data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv --inputs data/coverage_native_review_v03/coverage_native_review_v03_arabic_instruction_arabic_filenames_completed.csv data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_arabic_content_completed.csv data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_hindi_content_completed.csv data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_spanish_content_completed.csv data/coverage_native_review_v03/coverage_native_review_v03_hindi_english_instruction_hindi_devanagari_completed.csv data/coverage_native_review_v03/coverage_native_review_v03_spanish_instruction_arabic_quote_completed.csv"
            validate_args = "--annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv"
            summarize_args = validate_args + " --out-dir results/tables/coverage_native_review_v03 --out-md paper/coverage_native_review_v03.md"
        rows.extend(
            [
                {
                    "surface_id": surface["surface_id"],
                    "command_role": "merge_single_label_exports",
                    "command": f"conda run -n reprompt_tax python scripts/merge_review_exports.py {merge_args}",
                },
                {
                    "surface_id": surface["surface_id"],
                    "command_role": "validate_finalized_labels",
                    "command": f"conda run -n reprompt_tax python {surface['validator']} {validate_args}",
                },
                {
                    "surface_id": surface["surface_id"],
                    "command_role": "summarize_finalized_labels",
                    "command": f"conda run -n reprompt_tax python {surface['summarizer']} {summarize_args}",
                },
                {
                    "surface_id": surface["surface_id"],
                    "command_role": "analyze_double_labels",
                    "command": f"conda run -n reprompt_tax python {surface['adjudication_analyzer']} --annotations {surface['double_completed_path']}",
                },
                {
                    "surface_id": surface["surface_id"],
                    "command_role": "finalize_adjudicated_labels",
                    "command": f"conda run -n reprompt_tax python {surface['adjudication_finalizer']} --annotations {surface['double_completed_path']} --adjudication {surface['adjudication_packet']} --out {surface['finalized_path']}",
                },
            ]
        )
    return rows


def write_markdown(path: Path, surface_rows: list[dict[str, Any]], command_rows: list[dict[str, Any]]) -> None:
    total_rows = sum(int(row["packet_rows"]) for row in surface_rows)
    total_slots = sum(int(row["roster_template_slots"]) for row in surface_rows)
    lines = [
        "# Label Collection Launch Pack",
        "",
        "This launch pack consolidates the human/native review surfaces that remain",
        "incomplete in the follow-up plan. It is operational scaffolding, not completed",
        "human/native validation.",
        "",
        "## Summary",
        "",
        f"- Surfaces ready for label collection: {len(surface_rows)}",
        f"- Reviewer-facing packet rows: {total_rows}",
        f"- Roster template slots: {total_slots}",
        "- Sendable reviewer bundles: `results/label_collection_bundles_v02`",
        "- Claim boundary: do not claim completed human/native validation until",
        "  finalized labels pass the relevant completed-label validator and summary gate.",
        "",
        "## Surfaces",
        "",
        "| Surface | Status | Rows | Roster slots | Sheets | Final validator |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in surface_rows:
        lines.append(
            f"| {row['claim_surface']} | {row['status']} | {row['packet_rows']} | "
            f"{row['roster_template_slots']} | {row['review_sheet_count']} | `{row['validator']}` |"
        )
    lines.extend(
        [
            "",
            "## Completion Rules",
            "",
            "- Build sendable reviewer zip files with",
            "  `scripts/build_label_collection_bundles.py`, then validate them with",
            "  `scripts/validate_label_collection_bundles.py` before sending.",
            "- Merge returned slice exports with `scripts/merge_review_exports.py`",
            "  before running finalized-label validation.",
            "- Use one completed row per item only after single-review finalization or",
            "  two-reviewer adjudication finalization.",
            "- For the preferred stronger workflow, concatenate independent labels into",
            "  the `double_completed_path`, run the adjudication analyzer, fill only",
            "  disagreement rows, then run the finalizer.",
            "- Ensure failed component fields carry their matching failure or issue",
            "  code; the completed-label validators reject missing or contradictory",
            "  reason codes.",
            "- Keep answer keys and automatic labels away from reviewers; send only the",
            "  slice CSV or static review sheet for the relevant language/slice.",
            "- After finalized-label summaries are produced, run",
            "  `scripts/analyze_completed_label_claim_gates.py` and",
            "  `scripts/validate_completed_label_claim_gates.py` before updating",
            "  any paper claim.",
            "",
            "## Commands",
            "",
            "| Surface | Role | Command |",
            "|---|---|---|",
        ]
    )
    for row in command_rows:
        lines.append(f"| {row['surface_id']} | {row['command_role']} | `{row['command']}` |")
    lines.extend(
        [
            "",
            "## Reviewer Bundle Commands",
            "",
            "```bash",
            "conda run -n reprompt_tax python scripts/build_label_collection_bundles.py",
            "conda run -n reprompt_tax python scripts/validate_label_collection_bundles.py",
            "```",
            "",
            "## Claim Gate Commands",
            "",
            "```bash",
            "conda run -n reprompt_tax python scripts/analyze_completed_label_claim_gates.py",
            "conda run -n reprompt_tax python scripts/validate_completed_label_claim_gates.py",
            "```",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    surface_rows = build_surface_rows()
    file_rows = build_file_rows()
    command_rows = build_command_rows()
    write_csv(args.out_dir / "label_collection_surfaces.csv", surface_rows)
    write_csv(args.out_dir / "label_collection_files.csv", file_rows)
    write_csv(args.out_dir / "label_collection_commands.csv", command_rows)
    write_markdown(args.out_md, surface_rows, command_rows)
    print(f"wrote label collection launch pack to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
