#!/usr/bin/env python
"""Generate reviewer qualification requirements for pending human/native labels."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Any


OUT_DIR = Path("results/tables/reviewer_qualification_requirements_v02")
OUT_MD = Path("paper/reviewer_qualification_requirements_v02.md")

SURFACES = [
    {
        "surface_id": "current_model_human_audit_v02",
        "priority": "1",
        "surface_label": "Current-model GPT-5.x human/native audit",
        "roster_template": Path("data/current_model_human_audit/human_audit_annotator_roster_template_v0.2_current_gpt5.csv"),
        "completed_roster": Path("data/current_model_human_audit/human_audit_annotator_roster_v0.2_current_gpt5.csv"),
        "id_field": "annotator_id",
        "slice_field": "language_pair",
        "validator": "scripts/validate_completed_human_audit.py",
        "require_native_or_near_native": "True",
        "require_can_validate_instruction_language": "not_applicable",
        "require_can_validate_target_language": "not_applicable",
        "require_can_validate_script": "True",
        "expected_slots": 6,
        "expected_slices": {"ar-en": 2, "es-en": 2, "hi-en": 2},
    },
    {
        "surface_id": "human_audit_v02",
        "priority": "2",
        "surface_label": "Original v0.2 human/native audit",
        "roster_template": Path("data/human_audit/human_audit_annotator_roster_template_v0.2.csv"),
        "completed_roster": Path("data/human_audit/human_audit_annotator_roster_v0.2.csv"),
        "id_field": "annotator_id",
        "slice_field": "language_pair",
        "validator": "scripts/validate_completed_human_audit.py",
        "require_native_or_near_native": "True",
        "require_can_validate_instruction_language": "not_applicable",
        "require_can_validate_target_language": "not_applicable",
        "require_can_validate_script": "True",
        "expected_slots": 6,
        "expected_slices": {"ar-en": 2, "es-en": 2, "hi-en": 2},
    },
    {
        "surface_id": "coverage_native_review_v03",
        "priority": "3",
        "surface_label": "v0.3 coverage native review",
        "roster_template": Path("data/coverage_native_review_v03/coverage_native_review_roster_template_v03.csv"),
        "completed_roster": Path("data/coverage_native_review_v03/coverage_native_review_roster_v03.csv"),
        "id_field": "reviewer_id",
        "slice_field": "coverage_slice",
        "validator": "scripts/validate_completed_coverage_native_review_v03.py",
        "require_native_or_near_native": "not_applicable",
        "require_can_validate_instruction_language": "True",
        "require_can_validate_target_language": "True",
        "require_can_validate_script": "True",
        "expected_slots": 12,
        "expected_slices": {
            "arabic_instruction_arabic_filenames": 2,
            "english_instruction_arabic_content": 2,
            "english_instruction_hindi_content": 2,
            "english_instruction_spanish_content": 2,
            "hindi_english_instruction_hindi_devanagari": 2,
            "spanish_instruction_arabic_quote": 2,
        },
    },
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing reviewer qualification input {path}")
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    require(rows, f"empty reviewer qualification input {path}")
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, f"refusing to write empty qualification table {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def expected_language(row: dict[str, str]) -> str:
    return row.get("language_pair", "").strip()


def expected_content_language(row: dict[str, str]) -> str:
    return row.get("target_content_language", "").strip()


def build_requirement_rows() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for surface in SURFACES:
        rows = read_csv(surface["roster_template"])
        require(len(rows) == surface["expected_slots"], f"{surface['surface_id']} roster template row count mismatch")
        counts = Counter(row[surface["slice_field"]].strip() for row in rows)
        require(dict(counts) == surface["expected_slices"], f"{surface['surface_id']} roster template slice counts mismatch: {counts}")
        for index, row in enumerate(rows, start=1):
            reviewer_id = row[surface["id_field"]].strip()
            require(reviewer_id.startswith("replace_with_"), f"{surface['surface_id']} template has non-placeholder reviewer ID {reviewer_id}")
            slot = row[surface["slice_field"]].strip()
            out.append(
                {
                    "dispatch_priority": surface["priority"],
                    "surface_id": surface["surface_id"],
                    "surface_label": surface["surface_label"],
                    "slot_order": index,
                    "slot_id": slot,
                    "template_reviewer_id": reviewer_id,
                    "roster_template": str(surface["roster_template"]),
                    "completed_roster": str(surface["completed_roster"]),
                    "completed_roster_present": "True" if surface["completed_roster"].exists() else "False",
                    "expected_language_pair": expected_language(row),
                    "expected_target_content_language": expected_content_language(row),
                    "require_native_or_near_native": surface["require_native_or_near_native"],
                    "require_can_validate_instruction_language": surface["require_can_validate_instruction_language"],
                    "require_can_validate_target_language": surface["require_can_validate_target_language"],
                    "require_can_validate_script": surface["require_can_validate_script"],
                    "require_qualification_notes": "True",
                    "require_no_conflict_of_interest": "True",
                    "completed_roster_validator": surface["validator"],
                    "claim_boundary": "no_human_or_native_validation_claim_until_completed_labels_and_qualified_rosters_pass",
                }
            )
    return out


def build_summary_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for surface in SURFACES:
        surface_rows = [row for row in rows if row["surface_id"] == surface["surface_id"]]
        completed_roster_present = any(row["completed_roster_present"] == "True" for row in surface_rows)
        out.append(
            {
                "dispatch_priority": surface["priority"],
                "surface_id": surface["surface_id"],
                "surface_label": surface["surface_label"],
                "reviewer_slots": len(surface_rows),
                "unique_slices": len({row["slot_id"] for row in surface_rows}),
                "requires_native_or_near_native_slots": sum(row["require_native_or_near_native"] == "True" for row in surface_rows),
                "requires_instruction_language_slots": sum(row["require_can_validate_instruction_language"] == "True" for row in surface_rows),
                "requires_target_language_slots": sum(row["require_can_validate_target_language"] == "True" for row in surface_rows),
                "requires_script_slots": sum(row["require_can_validate_script"] == "True" for row in surface_rows),
                "completed_roster_present": "True" if completed_roster_present else "False",
                "qualification_claim_status": "requirements_defined_labels_absent",
                "next_action": "fill qualified rosters with real reviewer IDs, qualification notes, TRUE competency fields, and FALSE conflict fields before validating labels",
            }
        )
    return out


def write_markdown(path: Path, rows: list[dict[str, Any]], summary_rows: list[dict[str, Any]]) -> None:
    completed_rosters = sum(row["completed_roster_present"] == "True" for row in summary_rows)
    lines = [
        "# Reviewer Qualification Requirements",
        "",
        "This no-API audit makes the qualification requirements for pending",
        "human/native labels explicit before any returned labels are merged. It",
        "does not certify completed human/native validation.",
        "",
        "## Summary",
        "",
        f"- Surfaces checked: {len(summary_rows)}",
        f"- Reviewer qualification slots: {len(rows)}",
        f"- Completed qualified rosters present: {completed_rosters}/{len(summary_rows)}",
        "- OpenAI API calls: 0",
        "- Claim boundary: no human/native-validation claim is unlocked until",
        "  completed labels and qualified rosters pass their completed-label validators.",
        "",
        "## Surface Requirements",
        "",
        "| Priority | Surface | Slots | Slices | Native/near-native slots | Target-language slots | Script slots | Completed roster present | Status |",
        "|---:|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['dispatch_priority']} | `{row['surface_id']}` | {row['reviewer_slots']} | "
            f"{row['unique_slices']} | {row['requires_native_or_near_native_slots']} | "
            f"{row['requires_target_language_slots']} | {row['requires_script_slots']} | "
            f"{row['completed_roster_present']} | {row['qualification_claim_status']} |"
        )
    lines.extend(
        [
            "",
            "## Slot Requirements",
            "",
            "| Surface | Slot | Template reviewer ID | Language pair | Target content language | Native/near-native | Instruction language | Target language | Script | No conflict | Validator |",
            "|---|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['surface_id']}` | `{row['slot_id']}` | `{row['template_reviewer_id']}` | "
            f"{row['expected_language_pair']} | {row['expected_target_content_language']} | "
            f"{row['require_native_or_near_native']} | {row['require_can_validate_instruction_language']} | "
            f"{row['require_can_validate_target_language']} | {row['require_can_validate_script']} | "
            f"{row['require_no_conflict_of_interest']} | `{row['completed_roster_validator']}` |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    rows = build_requirement_rows()
    summary_rows = build_summary_rows(rows)
    write_csv(args.out_dir / "reviewer_qualification_requirements.csv", rows)
    write_csv(args.out_dir / "reviewer_qualification_summary.csv", summary_rows)
    write_markdown(args.out_md, rows, summary_rows)
    print(f"wrote reviewer qualification requirements to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
