#!/usr/bin/env python
"""Validate the v0.3 coverage expansion scaffold and audit outputs."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from run_models import failing_dry_response, passing_dry_response
from score_auto import score_response


EXPECTED_ROWS = 60
EXPECTED_PER_SLICE = 10
EXPECTED_SLICES = {
    "english_instruction_spanish_content": ("en-es", "Spanish", "Latin"),
    "english_instruction_hindi_content": ("en-hi", "Hindi", "Devanagari"),
    "english_instruction_arabic_content": ("en-ar", "Arabic", "Arabic"),
    "spanish_instruction_arabic_quote": ("es-ar", "Arabic", "Arabic"),
    "hindi_english_instruction_hindi_devanagari": ("hi-hi", "Hindi", "Devanagari"),
    "arabic_instruction_arabic_filenames": ("ar-ar", "Arabic", "Arabic"),
}
EXPECTED_STATUS = "synthetic_scaffold_requires_native_validation"
REQUIRED_REPORT_PHRASES = (
    "synthetic scaffold",
    "not paper-facing model result",
    "requires native validation before claims",
    "v0.2 benchmark remains the original paper-facing stress pilot",
)
PRIVACY_PATTERNS = {
    "email_address": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "url": re.compile(r"\b(?:https?://|www\.)\S+", re.IGNORECASE),
    "phone_like_number": re.compile(r"\b(?:\+?\d[\d ().-]{7,}\d)\b"),
    "ssn_like_number": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "placeholder_text": re.compile(r"\b(?:TODO|TBD|lorem ipsum|John Doe|Jane Doe)\b", re.IGNORECASE),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON") from exc
            row["_line_no"] = line_no
            rows.append(row)
    return rows


def normalize_prompt(prompt: str) -> str:
    return re.sub(r"\W+", " ", prompt.lower()).strip()


def privacy_hits(row: dict[str, Any]) -> list[str]:
    text = "\n".join(
        str(row.get(field, ""))
        for field in (
            "id",
            "user_prompt",
            "repair_prompt_1",
            "repair_prompt_2",
            "notes_for_annotators",
        )
    )
    return [name for name, pattern in PRIVACY_PATTERNS.items() if pattern.search(text)]


def validate_rows(rows: list[dict[str, Any]]) -> None:
    require(len(rows) == EXPECTED_ROWS, f"expected {EXPECTED_ROWS} rows, found {len(rows)}")
    ids = [str(row.get("id", "")) for row in rows]
    require(len(ids) == len(set(ids)), "duplicate ids found")
    prompts = [str(row.get("user_prompt", "")) for row in rows]
    require(len(prompts) == len(set(prompts)), "duplicate user prompts found")
    normalized = [normalize_prompt(prompt) for prompt in prompts]
    require(len(normalized) == len(set(normalized)), "normalized duplicate user prompts found")

    counts = Counter(row.get("coverage_slice") for row in rows)
    require(set(counts) == set(EXPECTED_SLICES), f"unexpected coverage slices: {sorted(counts)}")
    for coverage_slice, count in counts.items():
        require(count == EXPECTED_PER_SLICE, f"{coverage_slice} expected {EXPECTED_PER_SLICE}, found {count}")

    for row in rows:
        row_id = row.get("id", f"line {row.get('_line_no', '?')}")
        for field in (
            "benchmark_version",
            "validation_status",
            "coverage_slice",
            "language_pair",
            "task_family",
            "user_prompt",
            "instruction_language",
            "content_language",
            "expected_response_language",
            "expected_script",
            "must_preserve_spans",
            "known_bad_outputs",
            "repair_prompt_1",
            "repair_prompt_2",
            "required_any_markers",
            "forbidden_markers",
            "notes_for_annotators",
            "stress_tag",
        ):
            require(field in row, f"{row_id} missing field {field}")
        pair, expected_language, expected_script = EXPECTED_SLICES[row["coverage_slice"]]
        require(row["language_pair"] == pair, f"{row_id} has wrong language_pair")
        require(row["expected_response_language"] == expected_language, f"{row_id} has wrong expected language")
        require(row["expected_script"] == expected_script, f"{row_id} has wrong expected script")
        require(row["task_family"] == "editing_preservation", f"{row_id} has wrong task family")
        require(row["validation_status"] == EXPECTED_STATUS, f"{row_id} has wrong validation_status")
        require(row["stress_tag"] == "non_english_target_content_preservation", f"{row_id} has wrong stress_tag")
        require(isinstance(row["must_preserve_spans"], list) and row["must_preserve_spans"], f"{row_id} missing spans")
        require(isinstance(row["required_any_markers"], list) and row["required_any_markers"], f"{row_id} missing markers")
        require(isinstance(row["known_bad_outputs"], list) and row["known_bad_outputs"], f"{row_id} missing bad-output notes")
        require("requires native validation before claims" in row["notes_for_annotators"], f"{row_id} missing native-validation note")
        hits = privacy_hits(row)
        require(not hits, f"{row_id} has privacy-like marker(s): {', '.join(hits)}")
        passing_score = score_response(row, passing_dry_response(row))
        require(passing_score["pass"], f"{row_id} passing dry response does not pass scorer: {passing_score}")
        failing_score = score_response(row, failing_dry_response(row))
        require(not failing_score["pass"], f"{row_id} failing dry response unexpectedly passes scorer")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def validate_tables(tables_dir: Path) -> None:
    summary_rows = read_csv_rows(tables_dir / "coverage_expansion_summary.csv")
    require(len(summary_rows) == 1, "summary table must have one row")
    summary = summary_rows[0]
    require(summary["coverage_rows"] == str(EXPECTED_ROWS), "summary has wrong row count")
    require(summary["coverage_slices"] == "6", "summary has wrong slice count")
    require(summary["rows_requiring_native_validation"] == str(EXPECTED_ROWS), "summary has wrong native-validation count")
    require(summary["model_result_rows"] == "0", "summary must report zero model rows")
    require(summary["privacy_marker_hits"] == "0", "summary has privacy hits")

    by_slice = read_csv_rows(tables_dir / "coverage_expansion_by_slice.csv")
    require(len(by_slice) == len(EXPECTED_SLICES), "by-slice table has wrong number of rows")
    for row in by_slice:
        require(row["n"] == str(EXPECTED_PER_SLICE), f"{row['coverage_slice']} has wrong n")
        require(row["rows_requiring_native_validation"] == str(EXPECTED_PER_SLICE), "missing native-validation slice count")

    by_content = read_csv_rows(tables_dir / "coverage_expansion_by_content_language.csv")
    require(by_content, "by-content table is empty")
    privacy = read_csv_rows(tables_dir / "coverage_expansion_privacy_scan.csv")
    require(privacy and privacy[0]["privacy_marker_hits"] == "0", "privacy table has hits")


def validate_report(path: Path) -> None:
    require(path.exists(), f"missing report {path}")
    text = " ".join(path.read_text(encoding="utf-8").lower().split())
    for phrase in REQUIRED_REPORT_PHRASES:
        require(phrase in text, f"report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, default=Path("data/benchmark_stress_v0.3_expansion.jsonl"))
    parser.add_argument("--tables-dir", type=Path, default=Path("results/tables/coverage_expansion_v03"))
    parser.add_argument("--report", type=Path, default=Path("paper/coverage_expansion_v03.md"))
    args = parser.parse_args()
    validate_rows(load_jsonl(args.benchmark))
    validate_tables(args.tables_dir)
    validate_report(args.report)
    print("validated v0.3 coverage expansion scaffold")


if __name__ == "__main__":
    main()
