#!/usr/bin/env python
"""Validate the 24-item v0.3 coverage-expansion pilot."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


EXPECTED_PILOT_IDS = {
    f"v03_{prefix}_EP_{idx:03d}"
    for prefix in ("en_es", "en_hi", "en_ar", "es_ar", "hi_hi", "ar_ar")
    for idx in range(1, 5)
}
EXPECTED_OUTPUT_ROWS = 58
EXPECTED_SCORE_ROWS = 58
EXPECTED_INPUT_TOKENS = 8007
EXPECTED_OUTPUT_TOKENS = 1958
EXPECTED_TOTAL_TOKENS = 9965
EXPECTED_FIRST_TURN_FAILURES = {
    ("v03_en_hi_EP_002", "baseline", "preservation_failure"),
    ("v03_en_ar_EP_004", "baseline", "preservation_failure"),
    ("v03_en_ar_EP_004", "contract", "preservation_failure"),
    ("v03_es_ar_EP_001", "baseline", "task_noncompletion"),
    ("v03_es_ar_EP_002", "baseline", "task_noncompletion"),
    ("v03_es_ar_EP_003", "baseline", "task_noncompletion"),
    ("v03_es_ar_EP_004", "baseline", "task_noncompletion"),
}
REPORT_PHRASES = (
    "24-item pilot",
    "not paper-facing model result evidence",
    "requires native validation before claims",
    "baseline | 24 | 75.0%",
    "contract | 24 | 95.8%",
    "Paired FTGA movement: 5 improved, 0 worsened, 19 tied",
    "spanish_instruction_arabic_quote | baseline | 4 | 0.0%",
    "spanish_instruction_arabic_quote | contract | 4 | 100.0%",
)


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
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON") from exc
    return rows


def load_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def validate_outputs(rows: list[dict[str, Any]]) -> None:
    require(len(rows) == EXPECTED_OUTPUT_ROWS, f"expected {EXPECTED_OUTPUT_ROWS} output rows, found {len(rows)}")
    require({row["item_id"] for row in rows} == EXPECTED_PILOT_IDS, "unexpected pilot output item IDs")
    require({row["model"] for row in rows} == {"gpt-5.4-mini"}, "unexpected pilot model")
    require({row["condition"] for row in rows} == {"baseline", "contract"}, "unexpected pilot conditions")
    require(sum(1 for row in rows if int(row["turn"]) == 0) == 48, "expected 48 first-turn output rows")
    require(sum(int(row["input_tokens"]) for row in rows) == EXPECTED_INPUT_TOKENS, "unexpected input-token total")
    require(sum(int(row["output_tokens"]) for row in rows) == EXPECTED_OUTPUT_TOKENS, "unexpected output-token total")


def validate_scores(rows: list[dict[str, Any]]) -> None:
    require(len(rows) == EXPECTED_SCORE_ROWS, f"expected {EXPECTED_SCORE_ROWS} score rows, found {len(rows)}")
    first_turns = [row for row in rows if int(row["turn"]) == 0]
    require(len(first_turns) == 48, f"expected 48 first-turn rows, found {len(first_turns)}")
    baseline_first = [row for row in first_turns if row["condition"] == "baseline"]
    contract_first = [row for row in first_turns if row["condition"] == "contract"]
    require(sum(bool(row["pass"]) for row in baseline_first) == 18, "unexpected baseline FTGA count")
    require(sum(bool(row["pass"]) for row in contract_first) == 23, "unexpected contract FTGA count")
    failures = {
        (row["item_id"], row["condition"], ";".join(row.get("failure_types") or []))
        for row in first_turns
        if not row["pass"]
    }
    require(failures == EXPECTED_FIRST_TURN_FAILURES, f"unexpected first-turn failures: {failures}")


def validate_tables(tables_dir: Path) -> None:
    summary = {row["condition"]: row for row in load_csv(tables_dir / "coverage_pilot_summary.csv")}
    require(set(summary) == {"baseline", "contract"}, "summary must have baseline and contract rows")
    expected = {
        "baseline": {
            "n": "24",
            "ftga": 0.75,
            "mean_rtt": 1 / 2.4,
            "unresolved_rate": 1 / 12,
            "repair_success_at_2": 2 / 3,
            "initially_failed_n": "6",
        },
        "contract": {
            "n": "24",
            "ftga": 23 / 24,
            "mean_rtt": 1 / 8,
            "unresolved_rate": 1 / 24,
            "repair_success_at_2": 0.0,
            "initially_failed_n": "1",
        },
    }
    for condition, expected_values in expected.items():
        row = summary[condition]
        require(row["n"] == expected_values["n"], f"{condition} n mismatch")
        require(abs(float(row["ftga"]) - expected_values["ftga"]) < 1e-12, f"{condition} ftga mismatch")
        require(abs(float(row["mean_rtt"]) - expected_values["mean_rtt"]) < 1e-12, f"{condition} rtt mismatch")
        require(abs(float(row["unresolved_rate"]) - expected_values["unresolved_rate"]) < 1e-12, f"{condition} unresolved mismatch")
        require(abs(float(row["repair_success_at_2"]) - expected_values["repair_success_at_2"]) < 1e-12, f"{condition} repair mismatch")
        require(row["initially_failed_n"] == expected_values["initially_failed_n"], f"{condition} failure count mismatch")

    by_slice = {
        (row["coverage_slice"], row["condition"]): row
        for row in load_csv(tables_dir / "coverage_pilot_by_slice.csv")
    }
    require(len(by_slice) == 12, "expected 12 by-slice rows")
    require(by_slice[("spanish_instruction_arabic_quote", "baseline")]["ftga"] == "0.0", "unexpected es-ar baseline FTGA")
    require(by_slice[("spanish_instruction_arabic_quote", "contract")]["ftga"] == "1.0", "unexpected es-ar contract FTGA")
    require(by_slice[("english_instruction_arabic_content", "contract")]["initially_failed_n"] == "1", "missing residual contract failure")

    paired = load_csv(tables_dir / "coverage_pilot_paired_items.csv")
    require(len(paired) == 24, "expected 24 paired pilot rows")
    require(sum(1 for row in paired if row["ftga_delta"] == "1") == 5, "expected 5 improved paired items")
    require(sum(1 for row in paired if row["ftga_delta"] == "-1") == 0, "expected 0 worsened paired items")

    failures = load_csv(tables_dir / "coverage_pilot_first_turn_failures.csv")
    require(len(failures) == 7, "expected seven first-turn failure rows")
    observed = {(row["item_id"], row["condition"], row["failure_types"]) for row in failures}
    require(observed == EXPECTED_FIRST_TURN_FAILURES, "failure table does not match expected failures")


def validate_report(path: Path) -> None:
    require(path.exists(), f"missing pilot report {path}")
    text = " ".join(path.read_text(encoding="utf-8").split())
    for phrase in REPORT_PHRASES:
        require(phrase in text, f"pilot report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs", type=Path, default=Path("results/model_outputs/openai_gpt54mini_stress_v03_pilot24.jsonl"))
    parser.add_argument("--scores", type=Path, default=Path("results/scores/openai_gpt54mini_stress_v03_pilot24_auto_scores.jsonl"))
    parser.add_argument("--tables-dir", type=Path, default=Path("results/tables/openai_gpt54mini_stress_v03_pilot24"))
    parser.add_argument("--report", type=Path, default=Path("paper/coverage_pilot_gpt54mini_v03.md"))
    args = parser.parse_args()
    validate_outputs(load_jsonl(args.outputs))
    validate_scores(load_jsonl(args.scores))
    validate_tables(args.tables_dir)
    validate_report(args.report)
    print("validated v0.3 coverage pilot")


if __name__ == "__main__":
    main()
