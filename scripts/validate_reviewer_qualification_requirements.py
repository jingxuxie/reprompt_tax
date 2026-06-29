#!/usr/bin/env python
"""Validate reviewer qualification requirement artifacts."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


EXPECTED_SURFACE_ROWS = {
    "current_model_human_audit_v02": {
        "slots": 6,
        "slices": 3,
        "native_slots": 6,
        "instruction_slots": 0,
        "target_slots": 0,
        "script_slots": 6,
        "priority": "1",
        "validator": "scripts/validate_completed_human_audit.py",
    },
    "human_audit_v02": {
        "slots": 6,
        "slices": 3,
        "native_slots": 6,
        "instruction_slots": 0,
        "target_slots": 0,
        "script_slots": 6,
        "priority": "2",
        "validator": "scripts/validate_completed_human_audit.py",
    },
    "coverage_native_review_v03": {
        "slots": 12,
        "slices": 6,
        "native_slots": 0,
        "instruction_slots": 12,
        "target_slots": 12,
        "script_slots": 12,
        "priority": "3",
        "validator": "scripts/validate_completed_coverage_native_review_v03.py",
    },
}

EXPECTED_HUMAN_SLICES = {"ar-en": 2, "es-en": 2, "hi-en": 2}
EXPECTED_COVERAGE_SLICES = {
    "arabic_instruction_arabic_filenames": 2,
    "english_instruction_arabic_content": 2,
    "english_instruction_hindi_content": 2,
    "english_instruction_spanish_content": 2,
    "hindi_english_instruction_hindi_devanagari": 2,
    "spanish_instruction_arabic_quote": 2,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing reviewer qualification artifact {path}")
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    require(rows, f"empty reviewer qualification artifact {path}")
    return rows


def check_requirements(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == 24, f"unexpected qualification requirement row count: {len(rows)}")
    counts = Counter(row["surface_id"] for row in rows)
    require(counts == Counter({surface: spec["slots"] for surface, spec in EXPECTED_SURFACE_ROWS.items()}), f"unexpected qualification rows by surface: {counts}")
    for surface_id, spec in EXPECTED_SURFACE_ROWS.items():
        surface_rows = [row for row in rows if row["surface_id"] == surface_id]
        require(all(row["dispatch_priority"] == spec["priority"] for row in surface_rows), f"{surface_id} priority mismatch")
        require(all(row["template_reviewer_id"].startswith("replace_with_") for row in surface_rows), f"{surface_id} template IDs should remain placeholders before launch")
        require(all(row["require_qualification_notes"] == "True" for row in surface_rows), f"{surface_id} must require qualification notes")
        require(all(row["require_no_conflict_of_interest"] == "True" for row in surface_rows), f"{surface_id} must require no conflict")
        require(all(row["completed_roster_present"] == "False" for row in surface_rows), f"{surface_id} should not have completed roster in current no-label state")
        require(all(row["completed_roster_validator"] == spec["validator"] for row in surface_rows), f"{surface_id} validator mismatch")
        require(all(row["claim_boundary"] == "no_human_or_native_validation_claim_until_completed_labels_and_qualified_rosters_pass" for row in surface_rows), f"{surface_id} claim boundary mismatch")
        if surface_id == "coverage_native_review_v03":
            slice_counts = Counter(row["slot_id"] for row in surface_rows)
            require(slice_counts == Counter(EXPECTED_COVERAGE_SLICES), f"coverage slice counts mismatch: {slice_counts}")
            require(all(row["require_native_or_near_native"] == "not_applicable" for row in surface_rows), "coverage native flag should be not applicable")
            require(all(row["require_can_validate_instruction_language"] == "True" for row in surface_rows), "coverage must require instruction-language validation")
            require(all(row["require_can_validate_target_language"] == "True" for row in surface_rows), "coverage must require target-language validation")
            require(all(row["require_can_validate_script"] == "True" for row in surface_rows), "coverage must require script validation")
            require(all(row["expected_target_content_language"] for row in surface_rows), "coverage rows need target content language")
        else:
            slice_counts = Counter(row["slot_id"] for row in surface_rows)
            require(slice_counts == Counter(EXPECTED_HUMAN_SLICES), f"{surface_id} language-pair counts mismatch: {slice_counts}")
            require(all(row["require_native_or_near_native"] == "True" for row in surface_rows), f"{surface_id} must require native/near-native reviewers")
            require(all(row["require_can_validate_instruction_language"] == "not_applicable" for row in surface_rows), f"{surface_id} instruction language should be not applicable")
            require(all(row["require_can_validate_target_language"] == "not_applicable" for row in surface_rows), f"{surface_id} target language should be not applicable")
            require(all(row["require_can_validate_script"] == "True" for row in surface_rows), f"{surface_id} must require script validation")


def check_summary(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == 3, f"unexpected qualification summary row count: {len(rows)}")
    by_surface = {row["surface_id"]: row for row in rows}
    require(set(by_surface) == set(EXPECTED_SURFACE_ROWS), f"unexpected qualification summary surfaces: {sorted(by_surface)}")
    for surface_id, spec in EXPECTED_SURFACE_ROWS.items():
        row = by_surface[surface_id]
        require(row["dispatch_priority"] == spec["priority"], f"{surface_id} priority mismatch")
        require(row["reviewer_slots"] == str(spec["slots"]), f"{surface_id} slot count mismatch")
        require(row["unique_slices"] == str(spec["slices"]), f"{surface_id} slice count mismatch")
        require(row["requires_native_or_near_native_slots"] == str(spec["native_slots"]), f"{surface_id} native slot count mismatch")
        require(row["requires_instruction_language_slots"] == str(spec["instruction_slots"]), f"{surface_id} instruction slot count mismatch")
        require(row["requires_target_language_slots"] == str(spec["target_slots"]), f"{surface_id} target slot count mismatch")
        require(row["requires_script_slots"] == str(spec["script_slots"]), f"{surface_id} script slot count mismatch")
        require(row["completed_roster_present"] == "False", f"{surface_id} should not have completed roster yet")
        require(row["qualification_claim_status"] == "requirements_defined_labels_absent", f"{surface_id} status mismatch")
        require("qualified rosters" in row["next_action"], f"{surface_id} next action should name qualified rosters")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing reviewer qualification report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "Reviewer Qualification Requirements",
        "does not certify completed human/native validation",
        "Surfaces checked: 3",
        "Reviewer qualification slots: 24",
        "Completed qualified rosters present: 0/3",
        "OpenAI API calls: 0",
        "no human/native-validation claim is unlocked",
        "current_model_human_audit_v02",
        "human_audit_v02",
        "coverage_native_review_v03",
        "scripts/validate_completed_human_audit.py",
        "scripts/validate_completed_coverage_native_review_v03.py",
    ]
    for phrase in required:
        require(phrase in normalized, f"reviewer qualification report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/reviewer_qualification_requirements_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/reviewer_qualification_requirements_v02.md"))
    args = parser.parse_args()

    check_requirements(args.out_dir / "reviewer_qualification_requirements.csv")
    check_summary(args.out_dir / "reviewer_qualification_summary.csv")
    check_report(args.report)
    print("reviewer qualification requirements validation passed")


if __name__ == "__main__":
    main()
