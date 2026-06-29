#!/usr/bin/env python
"""Validate generation-progress probe artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_SUMMARY = {
    ("GPT-4.1 family", "baseline"): {
        "model_item_pairs": 360,
        "first_turn_failures": 96,
        "any_fail_items": 40,
        "all_fail_items": 27,
        "unresolved_pairs": 11,
    },
    ("GPT-4.1 family", "contract"): {
        "model_item_pairs": 360,
        "first_turn_failures": 61,
        "any_fail_items": 35,
        "all_fail_items": 8,
        "unresolved_pairs": 12,
    },
    ("GPT-5.x family", "baseline"): {
        "model_item_pairs": 240,
        "first_turn_failures": 46,
        "any_fail_items": 26,
        "all_fail_items": 20,
        "unresolved_pairs": 5,
    },
    ("GPT-5.x family", "contract"): {
        "model_item_pairs": 240,
        "first_turn_failures": 20,
        "any_fail_items": 18,
        "all_fail_items": 2,
        "unresolved_pairs": 6,
    },
}

EXPECTED_CATEGORIES = {
    "gpt41_baseline_any_fail_items": 40,
    "gpt41_baseline_all_fail_items": 27,
    "gpt41_contract_all_fail_items": 8,
    "gpt5x_baseline_both_fail_items": 20,
    "gpt5x_contract_both_fail_items": 2,
    "gpt41_all_baseline_fail_gpt55_baseline_pass": 7,
    "gpt41_any_baseline_fail_gpt55_baseline_pass": 19,
    "gpt41_any_baseline_fail_gpt55_contract_pass": 38,
    "gpt41_all_contract_fail_gpt55_contract_pass": 8,
}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_summary(path: Path) -> None:
    rows = {(row["generation"], row["condition"]): row for row in load_csv(path)}
    for key, expected in EXPECTED_SUMMARY.items():
        require(key in rows, f"missing generation summary row {key}")
        for field, expected_value in expected.items():
            actual = int(rows[key][field])
            require(actual == expected_value, f"summary mismatch for {key}/{field}: expected {expected_value}, got {actual}")


def check_categories(path: Path) -> None:
    rows = {row["category"]: row for row in load_csv(path)}
    for category, expected_count in EXPECTED_CATEGORIES.items():
        require(category in rows, f"missing category row {category}")
        actual = int(rows[category]["item_count"])
        require(actual == expected_count, f"category mismatch for {category}: expected {expected_count}, got {actual}")
    both_current = rows["gpt5x_contract_both_fail_items"]["item_ids"].split(";")
    require(both_current == ["es_en_SA_004", "es_en_SA_009"], f"unexpected current-family contract hard set: {both_current}")


def check_item_matrix(path: Path) -> None:
    rows = {row["item_id"]: row for row in load_csv(path)}
    require(len(rows) == 120, f"expected 120 item rows, found {len(rows)}")
    for item_id in ["es_en_SA_004", "es_en_SA_009"]:
        require(item_id in rows, f"missing residual item {item_id}")
        row = rows[item_id]
        require(row["gpt5x_contract_fail_count"] == "2", f"{item_id} should fail for both GPT-5.x contract rows")
        require(row["gpt55_contract_pass"] == "0", f"{item_id} should fail GPT-5.5 contract")


def check_report(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "not a broad model leaderboard or population-level claim",
        "GPT-4.1-family models fail 96/360 model-item pairs",
        "GPT-5.x-family baseline runs lower the normalized failure-pair rate to 46/240",
        "Under the contract, the GPT-5.x-family failure-pair rate falls to 20/240",
        "`gpt-5.5` baseline passes 7 of the 27 items that all GPT-4.1-family baselines fail",
        "With the contract, `gpt-5.5` passes 38 of those 40 older-family baseline-hard items",
        "The two items that both current models still fail under the contract are `es_en_SA_004`, `es_en_SA_009`",
    ]
    for phrase in required:
        require(phrase in normalized, f"generation-progress report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root
    out_dir = root / "results/tables/generation_progress_probe_v02"
    check_summary(out_dir / "generation_progress_summary.csv")
    check_categories(out_dir / "generation_progress_categories.csv")
    check_item_matrix(out_dir / "generation_progress_item_matrix.csv")
    check_report(root / "paper/generation_progress_probe_v02.md")
    print("generation-progress probe validation passed")


if __name__ == "__main__":
    main()
