#!/usr/bin/env python
"""Validate current-model scorer-sensitivity artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_MODEL_ROWS = {
    ("gpt-5.4-mini", "baseline"): {
        "actual_ftga_pct": 80.0,
        "relax_language_ftga_pct": 80.8,
        "relax_preservation_ftga_pct": 82.5,
        "sole_language_blocker_n": 1,
        "sole_preservation_blocker_n": 3,
    },
    ("gpt-5.4-mini", "contract"): {
        "actual_ftga_pct": 85.0,
        "relax_language_ftga_pct": 88.3,
        "relax_preservation_ftga_pct": 89.2,
        "sole_language_blocker_n": 4,
        "sole_preservation_blocker_n": 5,
    },
    ("gpt-5.5", "baseline"): {
        "actual_ftga_pct": 81.7,
        "relax_language_ftga_pct": 82.5,
        "relax_preservation_ftga_pct": 81.7,
        "sole_language_blocker_n": 1,
        "sole_preservation_blocker_n": 0,
    },
    ("gpt-5.5", "contract"): {
        "actual_ftga_pct": 98.3,
        "relax_language_ftga_pct": 100.0,
        "relax_preservation_ftga_pct": 98.3,
        "sole_language_blocker_n": 2,
        "sole_preservation_blocker_n": 0,
    },
}

EXPECTED_FAMILY_ROWS = {
    ("gpt-5.4-mini", "contract", "script_register_locale"): {
        "actual_ftga_pct": 80.0,
        "relax_preservation_delta_pp": 16.7,
        "sole_preservation_blocker_n": 5,
    },
    ("gpt-5.4-mini", "contract", "quote_preservation"): {
        "actual_ftga_pct": 93.3,
        "relax_language_delta_pp": 6.7,
        "sole_language_blocker_n": 2,
    },
    ("gpt-5.5", "contract", "editing_preservation"): {
        "actual_ftga_pct": 93.3,
        "relax_language_delta_pp": 6.7,
        "sole_language_blocker_n": 2,
    },
}

EXPECTED_SIGNATURES = {
    ("gpt-5.5", "contract", "editing_preservation", "language"): 2,
    ("gpt-5.4-mini", "contract", "script_register_locale", "preservation"): 5,
    ("gpt-5.4-mini", "contract", "quote_preservation", "language"): 2,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing current-model scorer-sensitivity table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def close(actual: str, expected: float, *, decimals: int = 1) -> bool:
    return round(float(actual), decimals) == round(float(expected), decimals)


def check_condition(path: Path) -> None:
    rows = {row["condition"]: row for row in load_csv(path)}
    require(set(rows) == {"baseline", "contract"}, f"unexpected condition rows: {sorted(rows)}")
    require(rows["baseline"]["n"] == "240", "baseline condition should have 240 current-model first-turn rows")
    require(rows["contract"]["n"] == "240", "contract condition should have 240 current-model first-turn rows")
    require(close(rows["baseline"]["actual_ftga_pct"], 80.8), "baseline current-model FTGA mismatch")
    require(close(rows["contract"]["actual_ftga_pct"], 91.7), "contract current-model FTGA mismatch")
    require(close(rows["contract"]["relax_language_ftga_pct"], 94.2), "contract relax-language FTGA mismatch")
    require(close(rows["contract"]["relax_preservation_ftga_pct"], 93.8), "contract relax-preservation FTGA mismatch")


def check_model_condition(path: Path) -> None:
    rows = {(row["model"], row["condition"]): row for row in load_csv(path)}
    require(set(rows) == set(EXPECTED_MODEL_ROWS), f"unexpected model-condition rows: {sorted(rows)}")
    for key, expected in EXPECTED_MODEL_ROWS.items():
        row = rows[key]
        require(row["n"] == "120", f"{key} should have 120 first-turn rows")
        for field, value in expected.items():
            if field.endswith("_n"):
                require(int(row[field]) == int(value), f"{key} mismatch for {field}: expected {value}, got {row[field]}")
            else:
                require(close(row[field], value), f"{key} mismatch for {field}: expected {value}, got {row[field]}")


def check_family(path: Path) -> None:
    rows = {(row["model"], row["condition"], row["task_family"]): row for row in load_csv(path)}
    require(len(rows) == 16, f"expected 16 model-condition-family rows, found {len(rows)}")
    for key, expected in EXPECTED_FAMILY_ROWS.items():
        row = rows[key]
        for field, value in expected.items():
            if field.endswith("_n"):
                require(int(row[field]) == int(value), f"{key} mismatch for {field}: expected {value}, got {row[field]}")
            else:
                require(close(row[field], value), f"{key} mismatch for {field}: expected {value}, got {row[field]}")


def check_signatures(path: Path) -> None:
    rows = {
        (row["model"], row["condition"], row["task_family"], row["failure_signature"]): row
        for row in load_csv(path)
    }
    for key, count in EXPECTED_SIGNATURES.items():
        require(key in rows, f"missing top failure signature {key}")
        require(int(rows[key]["count"]) == count, f"signature {key} expected count {count}, got {rows[key]['count']}")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing current-model scorer-sensitivity report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "Current-Model Scorer Sensitivity",
        "does not replace native/near-native validation",
        "gpt-5.5 | contract | 98.3%",
        "gpt-5.4-mini | contract | 85.0%",
        "relaxing language moves FTGA from 98.3% to 100.0%",
        "relaxing preservation moves FTGA from 85.0% to 89.2%",
        "not an artifact of a single fragile component",
        "low-cost residual set includes distinct preservation failures",
    ]
    for phrase in required:
        require(phrase in normalized, f"current-model scorer-sensitivity report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tables-dir", type=Path, default=Path("results/tables/current_model_scorer_sensitivity_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/current_model_scorer_sensitivity_v02.md"))
    args = parser.parse_args()

    check_condition(args.tables_dir / "current_model_scorer_sensitivity_by_condition.csv")
    check_model_condition(args.tables_dir / "current_model_scorer_sensitivity_by_model_condition.csv")
    check_family(args.tables_dir / "current_model_scorer_sensitivity_by_model_family_condition.csv")
    check_signatures(args.tables_dir / "current_model_scorer_sensitivity_top_failure_signatures.csv")
    check_report(args.report)
    print("current-model scorer-sensitivity validation passed")


if __name__ == "__main__":
    main()
