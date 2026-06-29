#!/usr/bin/env python
"""Command-shaped dry runs for remaining double-label intake surfaces.

This test covers the original v0.2 human audit and the v0.3 coverage
native-review packet. For each surface it creates temporary synthetic
reviewer1/reviewer2 returns, forces one disagreement, and runs the real
merge, adjudication-analysis, adjudicated-finalization, validation, and summary
commands. It never writes tracked completed-label files and does not support
any completed-label claim.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]

HUMAN_LAUNCH_PACKET = Path("data/human_audit/human_audit_packet_v0.2.csv")
HUMAN_ANSWER_KEY = Path("data/human_audit/human_audit_answer_key_v0.2.csv")
HUMAN_ANNOTATORS = {
    "ar-en": ("ar_v02_native_1", "ar_v02_native_2", "ar_v02_adjudicator"),
    "es-en": ("es_v02_native_1", "es_v02_native_2", "es_v02_adjudicator"),
    "hi-en": ("hi_v02_native_1", "hi_v02_native_2", "hi_v02_adjudicator"),
}
HUMAN_BOOLEAN_FIELDS = (
    "human_pass",
    "human_language_pass",
    "human_script_pass",
    "human_preservation_pass",
    "human_task_pass",
    "human_register_locale_pass",
)
HUMAN_ADJUDICATED_BOOLEAN_FIELDS = (
    "adjudicated_pass",
    "adjudicated_language_pass",
    "adjudicated_script_pass",
    "adjudicated_preservation_pass",
    "adjudicated_task_pass",
    "adjudicated_register_locale_pass",
)

COVERAGE_LAUNCH_PACKET = Path("data/coverage_native_review_v03/coverage_native_review_packet_v03.csv")
COVERAGE_BOOLEAN_FIELDS = (
    "reviewer_prompt_clear",
    "reviewer_target_language_natural",
    "reviewer_script_expectation_valid",
    "reviewer_preservation_spans_valid",
    "reviewer_known_bad_outputs_valid",
    "reviewer_release_usable",
)
COVERAGE_ADJUDICATED_BOOLEAN_FIELDS = (
    "adjudicated_prompt_clear",
    "adjudicated_target_language_natural",
    "adjudicated_script_expectation_valid",
    "adjudicated_preservation_spans_valid",
    "adjudicated_known_bad_outputs_valid",
    "adjudicated_release_usable",
)

TRACKED_COMPLETED_OUTPUTS = (
    Path("data/human_audit/human_audit_packet_v0.2_completed.csv"),
    Path("data/human_audit/human_audit_packet_v0.2_double_completed.csv"),
    Path("results/tables/human_audit_v0.2_adjudication/human_audit_adjudication_packet.csv"),
    Path("results/tables/human_audit_v0.2_adjudication/human_audit_final_label_sources.csv"),
    Path("data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv"),
    Path("data/coverage_native_review_v03/coverage_native_review_packet_v03_double_completed.csv"),
    Path("data/coverage_native_review_v03/coverage_native_review_packet_v03_adjudicated_completed.csv"),
    Path("results/tables/coverage_native_review_v03_adjudication/coverage_native_review_adjudication_packet.csv"),
    Path("results/tables/coverage_native_review_v03_adjudication/coverage_native_review_final_label_sources.csv"),
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


def assert_source_mix(source_path: Path, *, id_field: str, expected: dict[str, int]) -> None:
    _, rows = read_csv_with_fields(source_path)
    if any(not row.get(id_field) for row in rows):
        raise AssertionError(f"{source_path} contains a blank {id_field}")
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["final_label_source"]] = counts.get(row["final_label_source"], 0) + 1
    if counts != expected:
        raise AssertionError(f"unexpected final-label source mix for {source_path}: {counts}")


def assert_tracked_outputs_unchanged(before: dict[Path, bool]) -> None:
    after = {path: (ROOT / path).exists() for path in before}
    if after != before:
        raise AssertionError(f"dry run changed tracked completed-label output presence: before={before}, after={after}")


def human_completed_rows(rows: list[dict[str, str]], *, reviewer_index: int) -> list[dict[str, str]]:
    out = []
    for row in rows:
        completed = dict(row)
        completed["annotator_id"] = HUMAN_ANNOTATORS[row["language_pair"]][reviewer_index]
        for field in HUMAN_BOOLEAN_FIELDS:
            completed[field] = "TRUE"
        completed["human_failure_types"] = ""
        completed["human_notes"] = ""
        out.append(completed)
    return out


def inject_human_disagreement(rows: list[dict[str, str]]) -> None:
    first = next(row for row in rows if row["audit_id"] == "rpt_audit_001")
    first["human_pass"] = "FALSE"
    first["human_language_pass"] = "FALSE"
    first["human_failure_types"] = "wrong_output_language"
    first["human_notes"] = "Dry-run original-audit disagreement."


def human_roster_rows() -> list[dict[str, str]]:
    rows = []
    for language_pair, annotators in HUMAN_ANNOTATORS.items():
        for annotator_id in annotators:
            rows.append(
                {
                    "annotator_id": annotator_id,
                    "language_pair": language_pair,
                    "native_or_near_native": "TRUE",
                    "can_validate_script": "TRUE",
                    "qualification_notes": "Dry-run qualified original-audit fixture.",
                    "conflict_of_interest": "FALSE",
                    "notes": "",
                }
            )
    return rows


def fill_human_adjudication_packet(packet_path: Path) -> None:
    fieldnames, rows = read_csv_with_fields(packet_path)
    if len(rows) != 1 or rows[0]["audit_id"] != "rpt_audit_001":
        raise AssertionError(f"expected one rpt_audit_001 adjudication row, got {rows}")
    language_pair = rows[0]["language_pair"]
    rows[0]["adjudicator_id"] = HUMAN_ANNOTATORS[language_pair][2]
    for field in HUMAN_ADJUDICATED_BOOLEAN_FIELDS:
        rows[0][field] = "TRUE"
    rows[0]["adjudicated_failure_types"] = ""
    rows[0]["adjudication_notes"] = "Dry-run final label follows reviewer 1."
    write_csv(packet_path, rows, fieldnames)


def run_human_audit_surface(tmp: Path) -> None:
    launch_fields, launch_rows = read_csv_with_fields(ROOT / HUMAN_LAUNCH_PACKET)
    input_paths = []
    for language_pair in sorted(HUMAN_ANNOTATORS):
        language_rows = [row for row in launch_rows if row["language_pair"] == language_pair]
        for reviewer_index in (0, 1):
            rows = human_completed_rows(language_rows, reviewer_index=reviewer_index)
            if language_pair == "ar-en" and reviewer_index == 1:
                inject_human_disagreement(rows)
            path = tmp / f"human_v02_{language_pair}_reviewer{reviewer_index + 1}.csv"
            write_csv(path, rows, launch_fields)
            input_paths.append(path)

    roster_path = tmp / "human_v02_roster.csv"
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

    double_completed_path = tmp / "human_v02_double_completed.csv"
    adjudication_dir = tmp / "human_v02_adjudication"
    adjudication_md = tmp / "human_v02_adjudication.md"
    adjudication_packet = adjudication_dir / "human_audit_adjudication_packet.csv"
    completed_path = tmp / "human_v02_completed.csv"
    source_path = adjudication_dir / "final_label_sources.csv"
    summary_dir = tmp / "human_v02_summary"

    run_cmd(
        [
            sys.executable,
            "scripts/merge_review_exports.py",
            "--mode",
            "human_audit",
            "--launch-packet",
            str(HUMAN_LAUNCH_PACKET),
            "--out",
            str(double_completed_path),
            "--labels-per-item",
            "2",
            "--inputs",
            *[str(path) for path in input_paths],
        ],
        "merged review exports",
    )
    run_cmd(
        [
            sys.executable,
            "scripts/analyze_human_audit_adjudication.py",
            "--annotations",
            str(double_completed_path),
            "--answer-key",
            str(HUMAN_ANSWER_KEY),
            "--annotator-roster",
            str(roster_path),
            "--out-dir",
            str(adjudication_dir),
            "--out-md",
            str(adjudication_md),
        ],
        "human-audit adjudication analysis passed",
    )
    fill_human_adjudication_packet(adjudication_packet)
    run_cmd(
        [
            sys.executable,
            "scripts/finalize_human_audit_adjudication.py",
            "--annotations",
            str(double_completed_path),
            "--answer-key",
            str(HUMAN_ANSWER_KEY),
            "--annotator-roster",
            str(roster_path),
            "--adjudication",
            str(adjudication_packet),
            "--out",
            str(completed_path),
            "--source-out",
            str(source_path),
        ],
        "finalized adjudicated human-audit labels",
    )
    run_cmd(
        [
            sys.executable,
            "scripts/validate_completed_human_audit.py",
            "--annotations",
            str(completed_path),
            "--answer-key",
            str(HUMAN_ANSWER_KEY),
            "--annotator-roster",
            str(roster_path),
        ],
        "completed human-audit validation passed",
    )
    run_cmd(
        [
            sys.executable,
            "scripts/summarize_human_audit.py",
            "--annotations",
            str(completed_path),
            "--answer-key",
            str(HUMAN_ANSWER_KEY),
            "--out-dir",
            str(summary_dir),
        ],
        "summarized",
    )
    assert_source_mix(source_path, id_field="audit_id", expected={"adjudicated": 1, "consensus": 71})


def coverage_reviewer_id(coverage_slice: str, role: str) -> str:
    return f"{coverage_slice}_{role}"


def coverage_completed_rows(rows: list[dict[str, str]], *, reviewer_index: int) -> list[dict[str, str]]:
    out = []
    role = f"reviewer{reviewer_index + 1}"
    for row in rows:
        completed = dict(row)
        completed["reviewer_id"] = coverage_reviewer_id(row["coverage_slice"], role)
        for field in COVERAGE_BOOLEAN_FIELDS:
            completed[field] = "TRUE"
        completed["reviewer_issue_types"] = ""
        completed["reviewer_notes"] = ""
        out.append(completed)
    return out


def inject_coverage_disagreement(rows: list[dict[str, str]]) -> None:
    first = next(row for row in rows if row["review_id"] == "rpt_v03_native_001")
    first["reviewer_prompt_clear"] = "FALSE"
    first["reviewer_release_usable"] = "FALSE"
    first["reviewer_issue_types"] = "ambiguous_instruction"
    first["reviewer_notes"] = "Dry-run coverage-review disagreement."


def coverage_roster_rows(launch_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for coverage_slice in sorted({row["coverage_slice"] for row in launch_rows}):
        representative = next(row for row in launch_rows if row["coverage_slice"] == coverage_slice)
        for role in ("reviewer1", "reviewer2", "adjudicator"):
            rows.append(
                {
                    "reviewer_id": coverage_reviewer_id(coverage_slice, role),
                    "coverage_slice": coverage_slice,
                    "language_pair": representative["language_pair"],
                    "target_content_language": representative["content_language"],
                    "can_validate_instruction_language": "TRUE",
                    "can_validate_target_language": "TRUE",
                    "can_validate_script": "TRUE",
                    "qualification_notes": "Dry-run qualified v0.3 coverage native-review fixture.",
                    "conflict_of_interest": "FALSE",
                    "notes": "",
                }
            )
    return rows


def fill_coverage_adjudication_packet(packet_path: Path) -> None:
    fieldnames, rows = read_csv_with_fields(packet_path)
    if len(rows) != 1 or rows[0]["review_id"] != "rpt_v03_native_001":
        raise AssertionError(f"expected one rpt_v03_native_001 adjudication row, got {rows}")
    coverage_slice = rows[0]["coverage_slice"]
    rows[0]["adjudicator_id"] = coverage_reviewer_id(coverage_slice, "adjudicator")
    for field in COVERAGE_ADJUDICATED_BOOLEAN_FIELDS:
        rows[0][field] = "TRUE"
    rows[0]["adjudicated_issue_types"] = ""
    rows[0]["adjudication_notes"] = "Dry-run final label follows reviewer 1."
    write_csv(packet_path, rows, fieldnames)


def run_coverage_surface(tmp: Path) -> None:
    launch_fields, launch_rows = read_csv_with_fields(ROOT / COVERAGE_LAUNCH_PACKET)
    input_paths = []
    for coverage_slice in sorted({row["coverage_slice"] for row in launch_rows}):
        slice_rows = [row for row in launch_rows if row["coverage_slice"] == coverage_slice]
        for reviewer_index in (0, 1):
            rows = coverage_completed_rows(slice_rows, reviewer_index=reviewer_index)
            if coverage_slice == "arabic_instruction_arabic_filenames" and reviewer_index == 1:
                inject_coverage_disagreement(rows)
            path = tmp / f"coverage_v03_{coverage_slice}_reviewer{reviewer_index + 1}.csv"
            write_csv(path, rows, launch_fields)
            input_paths.append(path)

    roster_path = tmp / "coverage_v03_roster.csv"
    write_csv(
        roster_path,
        coverage_roster_rows(launch_rows),
        [
            "reviewer_id",
            "coverage_slice",
            "language_pair",
            "target_content_language",
            "can_validate_instruction_language",
            "can_validate_target_language",
            "can_validate_script",
            "qualification_notes",
            "conflict_of_interest",
            "notes",
        ],
    )

    double_completed_path = tmp / "coverage_v03_double_completed.csv"
    adjudication_dir = tmp / "coverage_v03_adjudication"
    adjudication_md = tmp / "coverage_v03_adjudication.md"
    adjudication_packet = adjudication_dir / "coverage_native_review_adjudication_packet.csv"
    completed_path = tmp / "coverage_v03_completed.csv"
    source_path = adjudication_dir / "final_label_sources.csv"
    summary_dir = tmp / "coverage_v03_summary"
    summary_md = tmp / "coverage_v03_summary.md"

    run_cmd(
        [
            sys.executable,
            "scripts/merge_review_exports.py",
            "--mode",
            "coverage_native_review",
            "--launch-packet",
            str(COVERAGE_LAUNCH_PACKET),
            "--out",
            str(double_completed_path),
            "--labels-per-item",
            "2",
            "--inputs",
            *[str(path) for path in input_paths],
        ],
        "merged review exports",
    )
    run_cmd(
        [
            sys.executable,
            "scripts/analyze_coverage_native_review_adjudication.py",
            "--annotations",
            str(double_completed_path),
            "--launch-packet",
            str(COVERAGE_LAUNCH_PACKET),
            "--reviewer-roster",
            str(roster_path),
            "--out-dir",
            str(adjudication_dir),
            "--out-md",
            str(adjudication_md),
        ],
        "coverage native-review adjudication analysis passed",
    )
    fill_coverage_adjudication_packet(adjudication_packet)
    run_cmd(
        [
            sys.executable,
            "scripts/finalize_coverage_native_review_adjudication.py",
            "--annotations",
            str(double_completed_path),
            "--launch-packet",
            str(COVERAGE_LAUNCH_PACKET),
            "--reviewer-roster",
            str(roster_path),
            "--adjudication",
            str(adjudication_packet),
            "--out",
            str(completed_path),
            "--source-out",
            str(source_path),
        ],
        "finalized adjudicated v0.3 coverage native-review labels",
    )
    run_cmd(
        [
            sys.executable,
            "scripts/validate_completed_coverage_native_review_v03.py",
            "--annotations",
            str(completed_path),
            "--launch-packet",
            str(COVERAGE_LAUNCH_PACKET),
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
            str(completed_path),
            "--launch-packet",
            str(COVERAGE_LAUNCH_PACKET),
            "--reviewer-roster",
            str(roster_path),
            "--out-dir",
            str(summary_dir),
            "--out-md",
            str(summary_md),
        ],
        "summarized 60 completed v0.3 coverage native-review rows",
    )
    assert_source_mix(source_path, id_field="review_id", expected={"adjudicated": 1, "consensus": 59})


def main() -> None:
    tracked_before = {path: (ROOT / path).exists() for path in TRACKED_COMPLETED_OUTPUTS}
    with TemporaryDirectory(prefix="reprompt_tax_label_adjudication_") as tmp_name:
        tmp = Path(tmp_name)
        run_human_audit_surface(tmp)
        run_coverage_surface(tmp)
    assert_tracked_outputs_unchanged(tracked_before)
    print("label-adjudication intake dry-run tests passed")


if __name__ == "__main__":
    main()
