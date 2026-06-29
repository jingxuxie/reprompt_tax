#!/usr/bin/env python
"""Validate the deterministic v0.2 sentinel suite artifacts."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


EXPECTED_IDS = [
    "ar_en_SA_003",
    "ar_en_SA_001",
    "ar_en_SB_001",
    "ar_en_SC_001",
    "ar_en_SD_006",
    "ar_en_SD_008",
    "ar_en_SD_007",
    "es_en_SA_004",
    "es_en_SA_009",
    "es_en_SA_001",
    "es_en_SA_002",
    "es_en_SA_003",
    "es_en_SA_006",
    "es_en_SA_007",
    "es_en_SA_008",
    "es_en_SA_010",
    "es_en_SB_001",
    "es_en_SC_001",
    "es_en_SD_008",
    "es_en_SD_010",
    "hi_en_SA_001",
    "hi_en_SB_001",
    "hi_en_SC_003",
    "hi_en_SD_008",
]

EXPECTED_SUMMARY = {
    "baseline_fail_pairs": {"full_n": "142", "sentinel_n": "78", "coverage_pct": "54.9"},
    "contract_fix_pairs": {"full_n": "67", "sentinel_n": "26", "coverage_pct": "38.8"},
    "contract_regression_pairs": {"full_n": "6", "sentinel_n": "4", "coverage_pct": "66.7"},
    "contract_fail_pairs": {"full_n": "81", "sentinel_n": "56", "coverage_pct": "69.1"},
    "unresolved_flags": {"full_n": "34", "sentinel_n": "26", "coverage_pct": "76.5"},
    "current_contract_fail_pairs": {"full_n": "20", "sentinel_n": "19", "coverage_pct": "95.0"},
    "gpt55_contract_residual": {"full_n": "2", "sentinel_n": "2", "coverage_pct": "100.0"},
    "gpt54_contract_regression": {"full_n": "5", "sentinel_n": "4", "coverage_pct": "80.0"},
    "covered_cells": {"full_n": "12", "sentinel_n": "12", "coverage_pct": "100.0"},
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing sentinel table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_ids(path: Path) -> None:
    require(path.exists(), f"missing sentinel id file {path}")
    ids = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    require(ids == EXPECTED_IDS, f"unexpected sentinel ids: {ids}")
    require(len(ids) == len(set(ids)) == 24, "sentinel ids must be 24 unique rows")


def check_selected(path: Path) -> None:
    rows = read_csv(path)
    require([row["item_id"] for row in rows] == EXPECTED_IDS, "selected-item table order does not match id file")
    strata = Counter((row["language_pair"], row["task_family"]) for row in rows)
    require(len(strata) == 12, f"expected 12 strata, found {len(strata)}")
    require(all(count >= 1 for count in strata.values()), f"sentinel suite does not cover every stratum: {strata}")
    by_id = {row["item_id"]: row for row in rows}
    require(by_id["es_en_SA_004"]["gpt55_contract_residual"] == "1", "missing GPT-5.5 residual flag for es_en_SA_004")
    require(by_id["es_en_SA_009"]["gpt55_contract_residual"] == "1", "missing GPT-5.5 residual flag for es_en_SA_009")
    require(sum(int(row["gpt55_contract_residual"]) for row in rows) == 2, "expected exactly two GPT-5.5 residual sentinels")
    require(sum(int(row["gpt54_contract_regression"]) for row in rows) == 4, "expected four GPT-5.4-mini regression sentinels")


def check_scores(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == 120, f"expected 120 item score rows, found {len(rows)}")
    require(len({row["item_id"] for row in rows}) == 120, "duplicate item scores")


def check_summary(path: Path) -> None:
    rows = {row["metric"]: row for row in read_csv(path)}
    require(set(rows) == set(EXPECTED_SUMMARY), f"unexpected summary metrics: {sorted(rows)}")
    for metric, expected in EXPECTED_SUMMARY.items():
        for field, value in expected.items():
            require(rows[metric][field] == value, f"{metric}/{field}: expected {value}, got {rows[metric][field]}")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing sentinel report {path}")
    text = " ".join(path.read_text(encoding="utf-8").split())
    required = [
        "Sentinel Suite v0.2",
        "compact 24-item diagnostic suite",
        "top-ranked item from each language-pair/task-family cell",
        "captures 26 of 67 contract fix pairs",
        "all 2 GPT-5.5 contract residual items",
        "data/stress_v02_sentinel24_ids.txt",
        "not as a replacement for the full benchmark",
        "completed qualified human/native labels",
    ]
    for phrase in required:
        require(phrase in text, f"sentinel report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/sentinel_suite_v02"))
    parser.add_argument("--ids", type=Path, default=Path("data/stress_v02_sentinel24_ids.txt"))
    parser.add_argument("--report", type=Path, default=Path("paper/sentinel_suite_v02.md"))
    args = parser.parse_args()

    check_ids(args.ids)
    check_scores(args.out_dir / "sentinel_item_scores.csv")
    check_selected(args.out_dir / "sentinel_selected_items.csv")
    check_summary(args.out_dir / "sentinel_coverage_summary.csv")
    check_report(args.report)
    print("sentinel-suite validation passed")


if __name__ == "__main__":
    main()
