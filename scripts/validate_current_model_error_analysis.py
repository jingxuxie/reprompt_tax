#!/usr/bin/env python
"""Validate current-model residual error analysis artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any


EXPECTED_SUMMARY = {
    ("gpt-5.4-mini", "baseline"): {"first_turn_failures": 24, "unresolved": 3},
    ("gpt-5.4-mini", "contract"): {"first_turn_failures": 18, "unresolved": 6},
    ("gpt-5.5", "baseline"): {"first_turn_failures": 22, "unresolved": 2},
    ("gpt-5.5", "contract"): {"first_turn_failures": 2, "unresolved": 0},
}

EXPECTED_TRANSITIONS = {
    "gpt-5.4-mini": {
        "both_pass": 91,
        "baseline_fail_contract_pass": 11,
        "baseline_pass_contract_fail": 5,
        "both_fail": 13,
    },
    "gpt-5.5": {
        "both_pass": 98,
        "baseline_fail_contract_pass": 20,
        "baseline_pass_contract_fail": 0,
        "both_fail": 2,
    },
}

EXPECTED_CONTRACT_FAMILY_FAILURES = {
    ("gpt-5.4-mini", "editing_preservation"): 10,
    ("gpt-5.4-mini", "quote_preservation"): 2,
    ("gpt-5.4-mini", "script_register_locale"): 6,
    ("gpt-5.5", "editing_preservation"): 2,
}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_summary(path: Path) -> None:
    rows = {(row["model"], row["condition"]): row for row in load_csv(path)}
    for key, expected in EXPECTED_SUMMARY.items():
        require(key in rows, f"missing current-model error summary row {key}")
        for field, expected_value in expected.items():
            actual = int(rows[key][field])
            require(actual == expected_value, f"summary mismatch for {key}/{field}: expected {expected_value}, got {actual}")


def check_transitions(path: Path) -> None:
    rows = {row["model"]: row for row in load_csv(path)}
    for model, expected in EXPECTED_TRANSITIONS.items():
        require(model in rows, f"missing paired-transition row for {model}")
        for field, expected_value in expected.items():
            actual = int(rows[model][field])
            require(actual == expected_value, f"transition mismatch for {model}/{field}: expected {expected_value}, got {actual}")


def check_family(path: Path) -> None:
    rows = {
        (row["model"], row["task_family"]): row
        for row in load_csv(path)
        if row["condition"] == "contract"
    }
    for key, expected_failures in EXPECTED_CONTRACT_FAMILY_FAILURES.items():
        require(key in rows, f"missing contract family row {key}")
        actual = int(rows[key]["first_turn_failures"])
        require(actual == expected_failures, f"family mismatch for {key}: expected {expected_failures}, got {actual}")


def check_contract_cases(path: Path) -> None:
    rows = load_csv(path)
    require(len(rows) == 20, f"expected 20 current-model contract residual cases, found {len(rows)}")
    g55_rows = [row for row in rows if row["model"] == "gpt-5.5"]
    require(len(g55_rows) == 2, f"expected two GPT-5.5 contract residual cases, found {len(g55_rows)}")
    require({row["item_id"] for row in g55_rows} == {"es_en_SA_004", "es_en_SA_009"}, "unexpected GPT-5.5 residual item IDs")
    require(all(row["unresolved"] == "0" for row in g55_rows), "GPT-5.5 contract residual cases should repair in one turn")


def check_report(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required_phrases = [
        "makes no new API calls",
        "`gpt-5.5` has 22 baseline first-turn failures",
        "Under the contract it has only 2 first-turn failures and 0 unresolved trajectories",
        "Both contract residuals are Spanish-English editing-preservation rows",
        "`gpt-5.4-mini` is more mixed",
        "the low-cost current-model claim should emphasize bounded FTGA and token-tax improvement",
        "it does not eliminate first-turn misalignment",
    ]
    for phrase in required_phrases:
        require(phrase in normalized, f"current-model residual report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root
    table_dir = root / "results/tables/current_model_error_analysis_v02"

    check_summary(table_dir / "current_model_error_summary.csv")
    check_transitions(table_dir / "current_model_paired_transitions.csv")
    check_family(table_dir / "current_model_error_by_family.csv")
    check_contract_cases(table_dir / "current_model_contract_residual_cases.csv")
    check_report(root / "paper/current_model_error_analysis_v02.md")
    print("current-model residual error validation passed")


if __name__ == "__main__":
    main()
