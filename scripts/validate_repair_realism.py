#!/usr/bin/env python
"""Validate repair-realism diagnostic artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


EXPECTED_SUMMARY = {
    "standard_saved": {
        "n": 24,
        "repair_success_n": 24,
        "repair_success_pct": 100.0,
        "task_pass_n": 24,
        "language_pass_n": 24,
        "preservation_pass_n": 24,
        "mean_total_tokens": 181.7,
    },
    "terse_keep_english": {
        "n": 24,
        "repair_success_n": 24,
        "repair_success_pct": 100.0,
        "task_pass_n": 24,
        "language_pass_n": 24,
        "preservation_pass_n": 24,
        "mean_total_tokens": 189.1,
    },
    "frustrated_dont_translate": {
        "n": 24,
        "repair_success_n": 17,
        "repair_success_pct": 70.8,
        "task_pass_n": 24,
        "language_pass_n": 17,
        "preservation_pass_n": 24,
        "mean_total_tokens": 184.5,
    },
    "explicit_contract": {
        "n": 24,
        "repair_success_n": 5,
        "repair_success_pct": 20.8,
        "task_pass_n": 17,
        "language_pass_n": 5,
        "preservation_pass_n": 24,
        "mean_total_tokens": 192.4,
    },
}

EXPECTED_PAIRED = {
    "terse_keep_english_minus_standard_saved": {
        "repair_success_improved": 0,
        "repair_success_worsened": 0,
        "repair_success_tied": 24,
        "delta_success_pp": 0.0,
        "mean_total_token_delta": 7.5,
    },
    "frustrated_dont_translate_minus_standard_saved": {
        "repair_success_improved": 0,
        "repair_success_worsened": 7,
        "repair_success_tied": 17,
        "delta_success_pp": -29.2,
        "mean_total_token_delta": 2.9,
    },
    "explicit_contract_minus_standard_saved": {
        "repair_success_improved": 0,
        "repair_success_worsened": 19,
        "repair_success_tied": 5,
        "delta_success_pp": -79.2,
        "mean_total_token_delta": 10.7,
    },
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_raw(path: Path) -> None:
    rows = load_jsonl(path)
    require(len(rows) == 96, f"expected 96 repair-realism rows, found {len(rows)}")
    keys = {(row["item_id"], row["model"], row["condition"], row["repair_variant"]) for row in rows}
    require(len(keys) == 96, "duplicate repair-realism rows")
    variants = {row["repair_variant"] for row in rows}
    require(variants == set(EXPECTED_SUMMARY), f"unexpected repair variants: {variants}")
    api_rows = [row for row in rows if row["source"] == "repair_variant_api"]
    standard_rows = [row for row in rows if row["source"] == "saved_main_trajectory"]
    require(len(api_rows) == 72, f"expected 72 API repair-variant rows, found {len(api_rows)}")
    require(len(standard_rows) == 24, f"expected 24 saved standard repair rows, found {len(standard_rows)}")
    require(sum(int(row["input_tokens"]) for row in api_rows) == 9009, "unexpected repair-realism API input tokens")
    require(sum(int(row["output_tokens"]) for row in api_rows) == 4576, "unexpected repair-realism API output tokens")


def compare(row: dict[str, str], field: str, expected: float | int, context: str) -> None:
    if isinstance(expected, int):
        actual: float | int = int(row[field])
    else:
        actual = round(float(row[field]), 1)
        expected = round(expected, 1)
    require(actual == expected, f"{context}/{field}: expected {expected}, got {actual}")


def check_summary(path: Path) -> None:
    rows = {row["repair_variant"]: row for row in load_csv(path)}
    require(set(rows) == set(EXPECTED_SUMMARY), f"unexpected repair summary variants: {set(rows)}")
    for variant, expected in EXPECTED_SUMMARY.items():
        for field, value in expected.items():
            compare(rows[variant], field, value, f"summary/{variant}")


def check_paired(path: Path) -> None:
    rows = {row["comparison"]: row for row in load_csv(path)}
    require(set(rows) == set(EXPECTED_PAIRED), f"unexpected repair paired rows: {set(rows)}")
    for comparison, expected in EXPECTED_PAIRED.items():
        for field, value in expected.items():
            compare(rows[comparison], field, value, f"paired/{comparison}")


def check_report(path: Path) -> None:
    text = " ".join(path.read_text(encoding="utf-8").split())
    for phrase in (
        "baseline editing-preservation first-turn failures",
        "standard | 24 | 24/24 (100.0%)",
        "terse | 24 | 24/24 (100.0%)",
        "frustrated | 24 | 17/24 (70.8%)",
        "explicit | 24 | 5/24 (20.8%)",
        "small interaction-realism diagnostic",
    ):
        require(phrase in text, f"repair-realism report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root
    table_dir = root / "results/tables/openai_three_model_stress_v02_repair_realism_editing_baseline24"

    check_raw(root / "results/scores/openai_three_model_stress_v02_repair_realism_editing_baseline24.jsonl")
    check_summary(table_dir / "repair_realism_summary.csv")
    check_paired(table_dir / "repair_realism_paired_effects.csv")
    check_report(root / "paper/repair_realism_editing_baseline24.md")
    print("repair-realism validation passed")


if __name__ == "__main__":
    main()
