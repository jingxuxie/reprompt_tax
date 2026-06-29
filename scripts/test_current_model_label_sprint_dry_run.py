#!/usr/bin/env python
"""Command-shaped dry run for the current-model double-label sprint.

This test creates temporary synthetic reviewer1/reviewer2 returns for the
current GPT-5.x human-audit packet, forces one real disagreement, and runs the
same merge, adjudication-analysis, adjudicated-finalization, validation, and
summary commands that completed qualified labels will use. It never writes the
tracked completed-label files and does not support any completed-label claim.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
LAUNCH_PACKET = Path("data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv")
ANSWER_KEY = Path("data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv")
EXPECTED_MODELS = "gpt-5.4-mini,gpt-5.5"
TRACKED_COMPLETED_OUTPUTS = (
    Path("data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_completed.csv"),
    Path("data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_double_completed.csv"),
    Path("results/tables/current_model_human_audit_v0.2_adjudication/human_audit_adjudication_packet.csv"),
    Path("results/tables/current_model_human_audit_v0.2_adjudication/human_audit_final_label_sources.csv"),
)

ANNOTATORS = {
    "ar-en": ("ar_native_1", "ar_native_2", "ar_adjudicator"),
    "es-en": ("es_native_1", "es_native_2", "es_adjudicator"),
    "hi-en": ("hi_native_1", "hi_native_2", "hi_adjudicator"),
}
BOOLEAN_FIELDS = (
    "human_pass",
    "human_language_pass",
    "human_script_pass",
    "human_preservation_pass",
    "human_task_pass",
    "human_register_locale_pass",
)
ADJUDICATED_BOOLEAN_FIELDS = (
    "adjudicated_pass",
    "adjudicated_language_pass",
    "adjudicated_script_pass",
    "adjudicated_preservation_pass",
    "adjudicated_task_pass",
    "adjudicated_register_locale_pass",
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


def run_cmd(command: list[str], expected_stdout: str) -> str:
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
    return proc.stdout


def completed_rows(rows: list[dict[str, str]], *, reviewer_index: int) -> list[dict[str, str]]:
    out = []
    for row in rows:
        completed = dict(row)
        completed["annotator_id"] = ANNOTATORS[row["language_pair"]][reviewer_index]
        for field in BOOLEAN_FIELDS:
            completed[field] = "TRUE"
        completed["human_failure_types"] = ""
        completed["human_notes"] = ""
        out.append(completed)
    return out


def inject_disagreement(rows: list[dict[str, str]]) -> None:
    first = next(row for row in rows if row["audit_id"] == "rpt_audit_001")
    first["human_pass"] = "FALSE"
    first["human_language_pass"] = "FALSE"
    first["human_failure_types"] = "wrong_output_language"
    first["human_notes"] = "Dry-run disagreement."


def roster_rows() -> list[dict[str, str]]:
    rows = []
    for language_pair, (reviewer_1, reviewer_2, adjudicator) in ANNOTATORS.items():
        for annotator_id in (reviewer_1, reviewer_2, adjudicator):
            rows.append(
                {
                    "annotator_id": annotator_id,
                    "language_pair": language_pair,
                    "native_or_near_native": "TRUE",
                    "can_validate_script": "TRUE",
                    "qualification_notes": "Dry-run qualified current-model sprint fixture.",
                    "conflict_of_interest": "FALSE",
                    "notes": "",
                }
            )
    return rows


def fill_adjudication_packet(packet_path: Path) -> None:
    fieldnames, rows = read_csv_with_fields(packet_path)
    if len(rows) != 1 or rows[0]["audit_id"] != "rpt_audit_001":
        raise AssertionError(f"expected one rpt_audit_001 adjudication row, got {rows}")
    language_pair = rows[0]["language_pair"]
    rows[0]["adjudicator_id"] = ANNOTATORS[language_pair][2]
    for field in ADJUDICATED_BOOLEAN_FIELDS:
        rows[0][field] = "TRUE"
    rows[0]["adjudicated_failure_types"] = ""
    rows[0]["adjudication_notes"] = "Dry-run final label follows reviewer 1."
    write_csv(packet_path, rows, fieldnames)


def assert_source_mix(source_path: Path) -> None:
    _, rows = read_csv_with_fields(source_path)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["final_label_source"]] = counts.get(row["final_label_source"], 0) + 1
    if counts != {"adjudicated": 1, "consensus": 47}:
        raise AssertionError(f"unexpected final-label source mix: {counts}")


def assert_tracked_outputs_unchanged(before: dict[Path, bool]) -> None:
    after = {path: (ROOT / path).exists() for path in before}
    if after != before:
        raise AssertionError(f"dry run changed tracked completed-label output presence: before={before}, after={after}")


def main() -> None:
    tracked_before = {path: (ROOT / path).exists() for path in TRACKED_COMPLETED_OUTPUTS}
    launch_fields, launch_rows = read_csv_with_fields(ROOT / LAUNCH_PACKET)
    with TemporaryDirectory(prefix="reprompt_tax_current_model_sprint_") as tmp_name:
        tmp = Path(tmp_name)
        input_paths = []
        for language_pair in sorted(ANNOTATORS):
            language_rows = [row for row in launch_rows if row["language_pair"] == language_pair]
            for reviewer_index in (0, 1):
                rows = completed_rows(language_rows, reviewer_index=reviewer_index)
                if language_pair == "ar-en" and reviewer_index == 1:
                    inject_disagreement(rows)
                path = tmp / f"current_model_{language_pair}_reviewer{reviewer_index + 1}.csv"
                write_csv(path, rows, launch_fields)
                input_paths.append(path)

        roster_path = tmp / "current_model_roster.csv"
        write_csv(
            roster_path,
            roster_rows(),
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

        double_completed_path = tmp / "current_model_double_completed.csv"
        adjudication_dir = tmp / "current_model_adjudication"
        adjudication_md = tmp / "current_model_adjudication.md"
        adjudication_packet = adjudication_dir / "human_audit_adjudication_packet.csv"
        completed_path = tmp / "current_model_completed.csv"
        source_path = adjudication_dir / "final_label_sources.csv"
        summary_dir = tmp / "current_model_summary"

        run_cmd(
            [
                sys.executable,
                "scripts/merge_review_exports.py",
                "--mode",
                "human_audit",
                "--launch-packet",
                str(LAUNCH_PACKET),
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
                str(ANSWER_KEY),
                "--annotator-roster",
                str(roster_path),
                "--expected-models",
                EXPECTED_MODELS,
                "--out-dir",
                str(adjudication_dir),
                "--out-md",
                str(adjudication_md),
            ],
            "human-audit adjudication analysis passed",
        )
        fill_adjudication_packet(adjudication_packet)
        run_cmd(
            [
                sys.executable,
                "scripts/finalize_human_audit_adjudication.py",
                "--annotations",
                str(double_completed_path),
                "--answer-key",
                str(ANSWER_KEY),
                "--annotator-roster",
                str(roster_path),
                "--expected-models",
                EXPECTED_MODELS,
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
                str(ANSWER_KEY),
                "--annotator-roster",
                str(roster_path),
                "--expected-models",
                EXPECTED_MODELS,
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
                str(ANSWER_KEY),
                "--out-dir",
                str(summary_dir),
            ],
            "summarized",
        )
        assert_source_mix(source_path)

    assert_tracked_outputs_unchanged(tracked_before)
    print("current-model label sprint dry-run tests passed")


if __name__ == "__main__":
    main()
