#!/usr/bin/env python
"""Command-shaped dry run for reviewer return intake.

This test creates temporary synthetic completed reviewer exports for each
currently incomplete label surface, then runs the same merge, validation, and
summary commands that real qualified reviewer returns will use. It never writes
tracked completed-label files and does not support any completed-label claim.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
HUMAN_ANNOTATORS = {
    "ar-en": "ar_native_1",
    "es-en": "es_native_1",
    "hi-en": "hi_native_1",
}
HUMAN_BOOLEAN_FIELDS = (
    "human_pass",
    "human_language_pass",
    "human_script_pass",
    "human_preservation_pass",
    "human_task_pass",
    "human_register_locale_pass",
)
REVIEW_BOOLEAN_FIELDS = (
    "reviewer_prompt_clear",
    "reviewer_target_language_natural",
    "reviewer_script_expectation_valid",
    "reviewer_preservation_spans_valid",
    "reviewer_known_bad_outputs_valid",
    "reviewer_release_usable",
)


def read_csv_with_fields(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    if not fieldnames:
        raise AssertionError(f"{path} has no CSV header")
    return fieldnames, rows


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run_cmd(command: list[str], expected_stdout: str) -> None:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        raise AssertionError(
            f"command failed with exit {proc.returncode}: {' '.join(command)}\n"
            f"stdout:\n{proc.stdout}\n"
            f"stderr:\n{proc.stderr}"
        )
    if expected_stdout not in proc.stdout:
        raise AssertionError(
            f"command stdout missing {expected_stdout!r}: {' '.join(command)}\n"
            f"stdout:\n{proc.stdout}\n"
            f"stderr:\n{proc.stderr}"
        )


def completed_human_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out = []
    for row in rows:
        completed = dict(row)
        completed["annotator_id"] = HUMAN_ANNOTATORS[row["language_pair"]]
        for field in HUMAN_BOOLEAN_FIELDS:
            completed[field] = "TRUE"
        completed["human_failure_types"] = ""
        completed["human_notes"] = ""
        out.append(completed)
    return out


def human_roster_rows() -> list[dict[str, str]]:
    return [
        {
            "annotator_id": "ar_native_1",
            "language_pair": "ar-en",
            "native_or_near_native": "TRUE",
            "can_validate_script": "TRUE",
            "qualification_notes": "Dry-run qualified Arabic reviewer fixture.",
            "conflict_of_interest": "FALSE",
            "notes": "",
        },
        {
            "annotator_id": "es_native_1",
            "language_pair": "es-en",
            "native_or_near_native": "TRUE",
            "can_validate_script": "TRUE",
            "qualification_notes": "Dry-run qualified Spanish reviewer fixture.",
            "conflict_of_interest": "FALSE",
            "notes": "",
        },
        {
            "annotator_id": "hi_native_1",
            "language_pair": "hi-en",
            "native_or_near_native": "TRUE",
            "can_validate_script": "TRUE",
            "qualification_notes": "Dry-run qualified Hindi reviewer fixture.",
            "conflict_of_interest": "FALSE",
            "notes": "",
        },
    ]


def completed_coverage_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out = []
    for row in rows:
        completed = dict(row)
        completed["reviewer_id"] = f"{row['coverage_slice']}_reviewer"
        for field in REVIEW_BOOLEAN_FIELDS:
            completed[field] = "TRUE"
        completed["reviewer_issue_types"] = ""
        completed["reviewer_notes"] = ""
        out.append(completed)
    return out


def coverage_roster_rows(launch_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for coverage_slice in sorted({row["coverage_slice"] for row in launch_rows}):
        representative = next(row for row in launch_rows if row["coverage_slice"] == coverage_slice)
        rows.append(
            {
                "reviewer_id": f"{coverage_slice}_reviewer",
                "coverage_slice": coverage_slice,
                "can_validate_instruction_language": "TRUE",
                "can_validate_target_language": "TRUE",
                "can_validate_script": "TRUE",
                "qualification_notes": "Dry-run qualified coverage reviewer fixture.",
                "conflict_of_interest": "FALSE",
                "language_pair": representative["language_pair"],
                "target_content_language": representative["content_language"],
                "notes": "",
            }
        )
    return rows


def run_human_surface(
    *,
    tmp: Path,
    name: str,
    launch_packet: Path,
    answer_key: Path,
    expected_models: str | None = None,
) -> None:
    launch_fields, launch_rows = read_csv_with_fields(launch_packet)
    input_paths = []
    for language_pair in sorted(HUMAN_ANNOTATORS):
        rows = completed_human_rows([row for row in launch_rows if row["language_pair"] == language_pair])
        path = tmp / f"{name}_{language_pair}_return.csv"
        write_csv(path, rows, launch_fields)
        input_paths.append(path)

    roster_path = tmp / f"{name}_roster.csv"
    write_csv(
        roster_path,
        human_roster_rows(),
        [
            "annotator_id",
            "language_pair",
            "native_or_near_native",
            "can_validate_script",
            "qualification_notes",
            "conflict_of_interest",
            "notes",
        ],
    )
    merged_path = tmp / f"{name}_completed.csv"
    summary_dir = tmp / f"{name}_summary"

    run_cmd(
        [
            sys.executable,
            "scripts/merge_review_exports.py",
            "--mode",
            "human_audit",
            "--launch-packet",
            str(launch_packet),
            "--out",
            str(merged_path),
            "--inputs",
            *[str(path) for path in input_paths],
        ],
        "merged review exports",
    )

    validate_cmd = [
        sys.executable,
        "scripts/validate_completed_human_audit.py",
        "--annotations",
        str(merged_path),
        "--answer-key",
        str(answer_key),
        "--annotator-roster",
        str(roster_path),
    ]
    if expected_models is not None:
        validate_cmd.extend(["--expected-models", expected_models])
    run_cmd(validate_cmd, "completed human-audit validation passed")

    run_cmd(
        [
            sys.executable,
            "scripts/summarize_human_audit.py",
            "--annotations",
            str(merged_path),
            "--answer-key",
            str(answer_key),
            "--out-dir",
            str(summary_dir),
        ],
        "summarized",
    )


def run_coverage_surface(*, tmp: Path) -> None:
    launch_packet = Path("data/coverage_native_review_v03/coverage_native_review_packet_v03.csv")
    launch_fields, launch_rows = read_csv_with_fields(launch_packet)
    input_paths = []
    for coverage_slice in sorted({row["coverage_slice"] for row in launch_rows}):
        rows = completed_coverage_rows([row for row in launch_rows if row["coverage_slice"] == coverage_slice])
        path = tmp / f"coverage_{coverage_slice}_return.csv"
        write_csv(path, rows, launch_fields)
        input_paths.append(path)

    roster_path = tmp / "coverage_roster.csv"
    write_csv(
        roster_path,
        coverage_roster_rows(launch_rows),
        [
            "reviewer_id",
            "coverage_slice",
            "can_validate_instruction_language",
            "can_validate_target_language",
            "can_validate_script",
            "qualification_notes",
            "conflict_of_interest",
            "language_pair",
            "target_content_language",
            "notes",
        ],
    )
    merged_path = tmp / "coverage_completed.csv"
    summary_dir = tmp / "coverage_summary"
    summary_md = tmp / "coverage_summary.md"

    run_cmd(
        [
            sys.executable,
            "scripts/merge_review_exports.py",
            "--mode",
            "coverage_native_review",
            "--launch-packet",
            str(launch_packet),
            "--out",
            str(merged_path),
            "--inputs",
            *[str(path) for path in input_paths],
        ],
        "merged review exports",
    )
    run_cmd(
        [
            sys.executable,
            "scripts/validate_completed_coverage_native_review_v03.py",
            "--annotations",
            str(merged_path),
            "--launch-packet",
            str(launch_packet),
            "--reviewer-roster",
            str(roster_path),
        ],
        "completed v0.3 coverage native-review validation passed",
    )
    run_cmd(
        [
            sys.executable,
            "scripts/summarize_coverage_native_review_v03.py",
            "--annotations",
            str(merged_path),
            "--launch-packet",
            str(launch_packet),
            "--reviewer-roster",
            str(roster_path),
            "--out-dir",
            str(summary_dir),
            "--out-md",
            str(summary_md),
        ],
        "summarized 60 completed v0.3 coverage native-review rows",
    )


def main() -> None:
    with TemporaryDirectory(prefix="reprompt_tax_label_intake_") as tmp_name:
        tmp = Path(tmp_name)
        run_human_surface(
            tmp=tmp,
            name="human_audit_v02",
            launch_packet=Path("data/human_audit/human_audit_packet_v0.2.csv"),
            answer_key=Path("data/human_audit/human_audit_answer_key_v0.2.csv"),
        )
        run_human_surface(
            tmp=tmp,
            name="current_model_human_audit_v02",
            launch_packet=Path("data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv"),
            answer_key=Path("data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv"),
            expected_models="gpt-5.4-mini,gpt-5.5",
        )
        run_coverage_surface(tmp=tmp)
    print("label-intake dry-run tests passed")


if __name__ == "__main__":
    main()
