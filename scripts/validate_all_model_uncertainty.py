#!/usr/bin/env python
"""Validate all-five-model clustered uncertainty artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_ROWS = {
    ("overall", "all"): {
        "n_items": "120",
        "n_model_item_pairs": "600",
        "baseline_ftga_pct": "76.3",
        "contract_ftga_pct": "86.5",
        "delta_pp": "10.2",
        "cluster_bootstrap_ci_low_pp": "5.8",
        "cluster_bootstrap_ci_high_pp": "15.0",
        "net_positive_item_count": "24",
        "net_negative_item_count": "5",
        "net_tied_item_count": "91",
    },
    ("generation", "GPT-4.1 family"): {
        "delta_pp": "9.7",
        "cluster_bootstrap_ci_low_pp": "5.6",
        "cluster_bootstrap_ci_high_pp": "14.4",
        "net_positive_item_count": "22",
        "net_negative_item_count": "1",
    },
    ("generation", "GPT-5.x family"): {
        "delta_pp": "10.8",
        "cluster_bootstrap_ci_low_pp": "5.4",
        "cluster_bootstrap_ci_high_pp": "16.7",
        "net_positive_item_count": "21",
        "net_negative_item_count": "5",
    },
    ("task_family", "editing_preservation"): {
        "n_items": "30",
        "n_model_item_pairs": "150",
        "baseline_ftga_pct": "33.3",
        "contract_ftga_pct": "74.0",
        "delta_pp": "40.7",
        "cluster_bootstrap_ci_low_pp": "28.0",
        "cluster_bootstrap_ci_high_pp": "53.3",
        "net_positive_item_count": "20",
        "net_negative_item_count": "0",
    },
    ("language_pair", "hi-en"): {
        "delta_pp": "0.5",
        "cluster_bootstrap_ci_low_pp": "-2.0",
        "cluster_bootstrap_ci_high_pp": "3.5",
        "net_positive_item_count": "2",
        "net_negative_item_count": "2",
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing clustered uncertainty table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_table(path: Path) -> None:
    rows = {(row["stratum_type"], row["stratum"]): row for row in read_csv(path)}
    require(len(rows) == 10, f"expected 10 clustered uncertainty rows, found {len(rows)}")
    for key, expected in EXPECTED_ROWS.items():
        require(key in rows, f"missing clustered uncertainty row {key}")
        row = rows[key]
        for field, value in expected.items():
            require(row[field] == value, f"{key} {field} mismatch: expected {value}, got {row[field]}")
    for row in rows.values():
        require(row["bootstrap_samples"] == "10000", f"{row['stratum_type']}/{row['stratum']} bootstrap sample mismatch")
        require(row["bootstrap_seed"] == "20260629", f"{row['stratum_type']}/{row['stratum']} bootstrap seed mismatch")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing clustered uncertainty report {path}")
    text = " ".join(path.read_text(encoding="utf-8").split())
    required = [
        "All-Model Clustered Uncertainty",
        "resamples prompt items",
        "+10.2 pp [+5.8, +15.0]",
        "24 net-positive items versus 5 net-negative items",
        "+40.7 pp [+28.0, +53.3]",
        "Hindi-English is +0.5 pp [-2.0, +3.5]",
        "does not replace native/near-native validation",
    ]
    for phrase in required:
        require(phrase in text, f"clustered uncertainty report missing phrase: {phrase}")


def check_results_tex(path: Path) -> None:
    require(path.exists(), f"missing results section {path}")
    text = " ".join(path.read_text(encoding="utf-8").split())
    required = [
        "clustered bootstrap interval is +5.8 to +15.0 points",
        "Resampling prompt items",
    ]
    for phrase in required:
        require(phrase in text, f"results section missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--table", type=Path, default=Path("results/tables/all_model_uncertainty_v02/all_model_cluster_bootstrap.csv"))
    parser.add_argument("--report", type=Path, default=Path("paper/all_model_uncertainty_v02.md"))
    parser.add_argument("--results-tex", type=Path, default=Path("paper/sections/05_results.tex"))
    args = parser.parse_args()

    check_table(args.table)
    check_report(args.report)
    check_results_tex(args.results_tex)
    print("all-model clustered-uncertainty validation passed")


if __name__ == "__main__":
    main()
