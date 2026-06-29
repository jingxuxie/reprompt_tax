#!/usr/bin/env python
"""Validate current-model heterogeneity artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_STRATA = {
    ("gpt-5.5", "language_pair", "ar-en"): {"delta_ftga_pp": 25.0, "fixed_n": 10, "regressed_n": 0},
    ("gpt-5.5", "language_pair", "es-en"): {"delta_ftga_pp": 20.0, "fixed_n": 8, "regressed_n": 0},
    ("gpt-5.5", "language_pair", "hi-en"): {"delta_ftga_pp": 5.0, "fixed_n": 2, "regressed_n": 0},
    ("gpt-5.5", "task_family", "editing_preservation"): {"delta_ftga_pp": 60.0, "fixed_n": 18, "regressed_n": 0},
    ("gpt-5.5", "task_family", "quote_preservation"): {"delta_ftga_pp": 0.0, "fixed_n": 0, "regressed_n": 0},
    ("gpt-5.4-mini", "language_pair", "ar-en"): {"delta_ftga_pp": 17.5, "fixed_n": 9, "regressed_n": 2},
    ("gpt-5.4-mini", "language_pair", "es-en"): {"delta_ftga_pp": 0.0, "fixed_n": 1, "regressed_n": 1},
    ("gpt-5.4-mini", "language_pair", "hi-en"): {"delta_ftga_pp": -2.5, "fixed_n": 1, "regressed_n": 2},
    ("gpt-5.4-mini", "task_family", "editing_preservation"): {"delta_ftga_pp": 33.4, "fixed_n": 10, "regressed_n": 0},
    ("gpt-5.4-mini", "task_family", "quote_preservation"): {"delta_ftga_pp": -6.7, "fixed_n": 0, "regressed_n": 2},
    ("gpt-5.4-mini", "task_family", "script_register_locale"): {"delta_ftga_pp": -6.7, "fixed_n": 1, "regressed_n": 3},
}

EXPECTED_LEAVE_ONE = {
    ("gpt-5.5", "language_pair", "ar-en"): {"delta_ftga_pp": 12.5, "leave_one_signal": "positive_remaining_effect"},
    ("gpt-5.5", "language_pair", "es-en"): {"delta_ftga_pp": 15.0, "leave_one_signal": "positive_remaining_effect"},
    ("gpt-5.5", "language_pair", "hi-en"): {"delta_ftga_pp": 22.5, "leave_one_signal": "positive_remaining_effect"},
    ("gpt-5.5", "task_family", "editing_preservation"): {"delta_ftga_pp": 2.2, "leave_one_signal": "positive_remaining_effect"},
    ("gpt-5.4-mini", "language_pair", "ar-en"): {"delta_ftga_pp": -1.3, "leave_one_signal": "negative_remaining_ftga_effect"},
    ("gpt-5.4-mini", "task_family", "editing_preservation"): {"delta_ftga_pp": -4.5, "leave_one_signal": "negative_remaining_ftga_effect"},
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing current-model heterogeneity table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def close(actual: str, expected: float, *, decimals: int = 1) -> bool:
    return round(float(actual), decimals) == round(float(expected), decimals)


def check_strata(path: Path) -> None:
    rows = {(row["model"], row["stratum_type"], row["stratum"]): row for row in load_csv(path)}
    require(len(rows) == 14, f"expected 14 current-model stratum rows, found {len(rows)}")
    for key, expected in EXPECTED_STRATA.items():
        require(key in rows, f"missing stratum row {key}")
        row = rows[key]
        require(row["n_pairs"] in {"30", "40"}, f"{key} should have 30 or 40 paired rows")
        for field, value in expected.items():
            if field.endswith("_n"):
                require(int(row[field]) == int(value), f"{key}/{field} expected {value}, got {row[field]}")
            else:
                require(close(row[field], value), f"{key}/{field} expected {value}, got {row[field]}")


def check_leave_one(path: Path) -> None:
    rows = {(row["model"], row["left_out_type"], row["left_out_stratum"]): row for row in load_csv(path)}
    require(len(rows) == 14, f"expected 14 leave-one rows, found {len(rows)}")
    for key, expected in EXPECTED_LEAVE_ONE.items():
        require(key in rows, f"missing leave-one row {key}")
        row = rows[key]
        require(row["n_pairs"] in {"80", "90"}, f"{key} should keep 80 or 90 paired rows")
        require(close(row["delta_ftga_pp"], expected["delta_ftga_pp"]), f"{key} delta mismatch")
        require(row["leave_one_signal"] == expected["leave_one_signal"], f"{key} signal mismatch")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing current-model heterogeneity report {path}")
    normalized = " ".join(path.read_text(encoding="utf-8").split())
    required = [
        "Current-Model Heterogeneity",
        "It makes no API calls",
        "ar-en moves +25.0 pp, es-en moves +20.0 pp, and hi-en moves +5.0 pp",
        "not a single-language artifact",
        "Editing preservation moves +60.0 pp",
        "removing editing preservation leaves only a +2.2 pp FTGA effect",
        "not a uniform gain over all task types",
        "ar-en moves +17.5 pp, es-en moves +0.0 pp, and hi-en moves -2.5 pp",
        "Removing ar-en leaves a -1.3 pp FTGA effect",
        "removing editing preservation leaves -4.5 pp",
        "do not replace native/near-native validation",
    ]
    for phrase in required:
        require(phrase in normalized, f"current-model heterogeneity report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tables-dir", type=Path, default=Path("results/tables/current_model_heterogeneity_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/current_model_heterogeneity_v02.md"))
    args = parser.parse_args()

    check_strata(args.tables_dir / "current_model_heterogeneity_by_stratum.csv")
    check_leave_one(args.tables_dir / "current_model_heterogeneity_leave_one.csv")
    check_report(args.report)
    print("current-model heterogeneity validation passed")


if __name__ == "__main__":
    main()
