#!/usr/bin/env python
"""Validate all-five-model paired significance artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_ROWS = {
    ("model_item", "overall", "all"): {
        "n_units": "600",
        "positive_n": "67",
        "negative_n": "6",
        "tie_n": "527",
        "net_gain_units": "61",
        "delta_pp": "10.2",
    },
    ("item_cluster", "overall", "all"): {
        "n_units": "120",
        "positive_n": "24",
        "negative_n": "5",
        "tie_n": "91",
        "net_gain_units": "61",
        "delta_pp": "10.2",
    },
    ("model_item", "generation", "GPT-4.1 family"): {
        "n_units": "360",
        "positive_n": "36",
        "negative_n": "1",
        "net_gain_units": "35",
        "delta_pp": "9.7",
    },
    ("item_cluster", "generation", "GPT-4.1 family"): {
        "n_units": "120",
        "positive_n": "22",
        "negative_n": "1",
        "net_gain_units": "35",
        "delta_pp": "9.7",
    },
    ("model_item", "generation", "GPT-5.x family"): {
        "n_units": "240",
        "positive_n": "31",
        "negative_n": "5",
        "net_gain_units": "26",
        "delta_pp": "10.8",
    },
    ("item_cluster", "generation", "GPT-5.x family"): {
        "n_units": "120",
        "positive_n": "21",
        "negative_n": "5",
        "net_gain_units": "26",
        "delta_pp": "10.8",
    },
    ("model_item", "task_family", "editing_preservation"): {
        "n_units": "150",
        "positive_n": "61",
        "negative_n": "0",
        "net_gain_units": "61",
        "delta_pp": "40.7",
    },
    ("item_cluster", "task_family", "editing_preservation"): {
        "n_units": "30",
        "positive_n": "20",
        "negative_n": "0",
        "net_gain_units": "61",
        "delta_pp": "40.7",
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing paired-significance table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_table(path: Path) -> None:
    rows = {(row["unit"], row["stratum_type"], row["stratum"]): row for row in read_csv(path)}
    require(len(rows) == 20, f"expected 20 all-model paired-significance rows, found {len(rows)}")
    for key, expected in EXPECTED_ROWS.items():
        require(key in rows, f"missing paired-significance row {key}")
        row = rows[key]
        for field, value in expected.items():
            require(row[field] == value, f"{key} {field} mismatch: expected {value}, got {row[field]}")
    require(float(rows[("model_item", "overall", "all")]["two_sided_sign_p"]) < 1e-12, "overall model-item p-value too large")
    require(float(rows[("item_cluster", "overall", "all")]["two_sided_sign_p"]) < 0.001, "overall item-cluster p-value too large")
    require(float(rows[("item_cluster", "task_family", "editing_preservation")]["two_sided_sign_p"]) < 0.00001, "editing item-cluster p-value too large")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing paired-significance report {path}")
    text = " ".join(path.read_text(encoding="utf-8").split())
    required = [
        "All-Model Paired Significance",
        "67 first-turn fixes and 6 regressions",
        "24 | 5 | 91",
        "0.0005",
        "61 model-item fixes and 0 regressions",
        "item-cluster row addresses repeated-item dependence",
        "does not replace native/near-native validation",
    ]
    for phrase in required:
        require(phrase in text, f"paired-significance report missing phrase: {phrase}")


def check_results_tex(path: Path) -> None:
    require(path.exists(), f"missing results section {path}")
    text = " ".join(path.read_text(encoding="utf-8").split())
    required = [
        "All-five paired sign tests remain positive",
        "67 fixes vs. 6 regressions",
        "24 net-positive vs. 5 net-negative items",
    ]
    for phrase in required:
        require(phrase in text, f"results section missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--table", type=Path, default=Path("results/tables/all_model_paired_significance_v02/all_model_paired_significance.csv"))
    parser.add_argument("--report", type=Path, default=Path("paper/all_model_paired_significance_v02.md"))
    parser.add_argument("--results-tex", type=Path, default=Path("paper/sections/05_results.tex"))
    args = parser.parse_args()

    check_table(args.table)
    check_report(args.report)
    check_results_tex(args.results_tex)
    print("all-model paired-significance validation passed")


if __name__ == "__main__":
    main()
