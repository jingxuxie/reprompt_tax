#!/usr/bin/env python
"""Validate the prompt-family scorecard artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_SCORECARD = {
    "gpt-4.1-nano": {
        "tested_conditions": "baseline;content_preservation;contract;generic_helpfulness",
        "best_ftga_condition": "content_preservation",
        "baseline_ftga_pct": "67.5",
        "contract_ftga_pct": "76.7",
        "content_preservation_ftga_pct": "80.0",
        "content_minus_contract_delta_pp": "3.3",
        "content_minus_contract_improved": "7",
        "content_minus_contract_worsened": "3",
        "content_minus_contract_tied": "110",
        "generic_helpfulness_ftga_pct": "75.0",
        "claim_boundary": "single_model_generic_control_only",
    },
    "gpt-5.4-mini": {
        "tested_conditions": "baseline;content_preservation;contract",
        "best_ftga_condition": "content_preservation",
        "baseline_ftga_pct": "80.0",
        "contract_ftga_pct": "85.0",
        "content_preservation_ftga_pct": "85.8",
        "content_minus_contract_delta_pp": "0.8",
        "content_minus_contract_improved": "5",
        "content_minus_contract_worsened": "4",
        "content_minus_contract_tied": "111",
        "generic_helpfulness_ftga_pct": "",
        "claim_boundary": "generic_not_tested_current_models",
    },
    "gpt-5.5": {
        "tested_conditions": "baseline;content_preservation;contract",
        "best_ftga_condition": "content_preservation",
        "baseline_ftga_pct": "81.7",
        "contract_ftga_pct": "98.3",
        "content_preservation_ftga_pct": "99.2",
        "content_minus_contract_delta_pp": "0.8",
        "content_minus_contract_improved": "2",
        "content_minus_contract_worsened": "1",
        "content_minus_contract_tied": "117",
        "generic_helpfulness_ftga_pct": "",
        "claim_boundary": "generic_not_tested_current_models",
    },
}


EXPECTED_COMPARISONS = {
    ("gpt-4.1-nano", "content_preservation_minus_baseline"): {"delta_ftga_pp": "12.5", "ftga_improved": "16", "ftga_worsened": "1"},
    ("gpt-4.1-nano", "contract_minus_baseline"): {"delta_ftga_pp": "9.2", "ftga_improved": "12", "ftga_worsened": "1"},
    ("gpt-5.4-mini", "content_preservation_minus_contract"): {"delta_ftga_pp": "0.8", "ftga_improved": "5", "ftga_worsened": "4"},
    ("gpt-5.5", "content_preservation_minus_contract"): {"delta_ftga_pp": "0.8", "ftga_improved": "2", "ftga_worsened": "1"},
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing prompt-family table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_scorecard(path: Path) -> None:
    rows = {row["model"]: row for row in read_csv(path)}
    require(set(rows) == set(EXPECTED_SCORECARD), f"unexpected scorecard models: {sorted(rows)}")
    for model, expected in EXPECTED_SCORECARD.items():
        row = rows[model]
        for field, value in expected.items():
            require(row[field] == value, f"{model} {field} mismatch: expected {value}, got {row[field]}")


def check_comparisons(path: Path) -> None:
    rows = {(row["model"], row["comparison"]): row for row in read_csv(path)}
    for key, expected in EXPECTED_COMPARISONS.items():
        require(key in rows, f"missing prompt comparison {key}")
        row = rows[key]
        for field, value in expected.items():
            require(row[field] == value, f"{key} {field} mismatch: expected {value}, got {row[field]}")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing prompt-family report {path}")
    text = " ".join(path.read_text(encoding="utf-8").split())
    required = [
        "Prompt-Family Scorecard",
        "makes no API calls",
        "content-preservation scaffold is the highest-FTGA tested prompt",
        "80.0% on `gpt-4.1-nano`, 85.8% on `gpt-5.4-mini`, and 99.2% on `gpt-5.5`",
        "The two current-model margins are one net item or essentially tied",
        "generic-helpfulness was only tested for `gpt-4.1-nano`",
        "does not claim the narrow prompt is universally best",
    ]
    for phrase in required:
        require(phrase in text, f"prompt-family report missing phrase: {phrase}")


def check_results_tex(path: Path) -> None:
    require(path.exists(), f"missing results section {path}")
    text = " ".join(path.read_text(encoding="utf-8").split())
    required = [
        "The prompt-family scorecard puts the same pattern in one table",
        "content preservation is highest-FTGA in all three tested models",
        "generic-helpfulness was not run on the current models",
    ]
    for phrase in required:
        require(phrase in text, f"results section missing prompt-family phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/prompt_family_scorecard_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/prompt_family_scorecard_v02.md"))
    parser.add_argument("--results-tex", type=Path, default=Path("paper/sections/05_results.tex"))
    args = parser.parse_args()

    check_scorecard(args.out_dir / "prompt_family_model_scorecard.csv")
    check_comparisons(args.out_dir / "prompt_family_paired_comparisons.csv")
    check_report(args.report)
    check_results_tex(args.results_tex)
    print("prompt-family scorecard validation passed")


if __name__ == "__main__":
    main()
