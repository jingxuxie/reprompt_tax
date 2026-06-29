#!/usr/bin/env python
"""Validate all-five-model efficiency tradeoff artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_SUMMARY = {
    ("gpt-5.5", "contract"): {
        "ftga_pct": 98.3,
        "mean_rtt": 0.017,
        "mean_total_tokens_until_stop": 278.758,
        "mean_token_tax": 1.016492,
        "total_tokens_until_stop": 33451,
    },
    ("gpt-5.4-mini", "contract"): {
        "ftga_pct": 85.0,
        "mean_total_tokens_until_stop": 280.033,
        "mean_token_tax": 1.241365,
        "total_tokens_until_stop": 33604,
    },
    ("gpt-4.1-mini", "baseline"): {
        "ftga_pct": 75.8,
        "mean_total_tokens_until_stop": 120.917,
        "mean_token_tax": 1.431533,
        "total_tokens_until_stop": 14510,
    },
}

EXPECTED_EFFECTS = {
    "gpt-5.5": {
        "delta_ftga_pp": 16.7,
        "token_tax_reduction": 0.261926,
        "mean_total_tokens_baseline_minus_contract": -114.458,
        "mean_extra_tokens_baseline_minus_contract": 36.808,
        "sum_total_tokens_baseline_minus_contract": -13735,
    },
    "gpt-5.4-mini": {
        "delta_ftga_pp": 5.0,
        "token_tax_reduction": 0.137730,
        "mean_total_tokens_baseline_minus_contract": -151.600,
        "mean_extra_tokens_baseline_minus_contract": -9.467,
        "sum_total_tokens_baseline_minus_contract": -18192,
    },
    "gpt-4.1-nano": {
        "delta_ftga_pp": 9.2,
        "token_tax_reduction": 0.351340,
        "mean_total_tokens_baseline_minus_contract": -168.833,
        "sum_total_tokens_baseline_minus_contract": -20260,
    },
}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def close(actual: str, expected: float, *, decimals: int = 3) -> bool:
    return round(float(actual), decimals) == round(float(expected), decimals)


def check_summary(path: Path) -> None:
    rows = {(row["model"], row["condition"]): row for row in load_csv(path)}
    require(len(rows) == 10, f"expected 10 model-condition rows, found {len(rows)}")
    for key, expected in EXPECTED_SUMMARY.items():
        require(key in rows, f"missing efficiency summary row {key}")
        row = rows[key]
        for field, value in expected.items():
            if field == "total_tokens_until_stop":
                require(int(row[field]) == int(value), f"summary mismatch for {key}/{field}: expected {value}, got {row[field]}")
            else:
                require(close(row[field], value), f"summary mismatch for {key}/{field}: expected {value}, got {row[field]}")


def check_effects(path: Path) -> None:
    rows = {row["model"]: row for row in load_csv(path)}
    require(len(rows) == 5, f"expected 5 paired-effect rows, found {len(rows)}")
    for model, expected in EXPECTED_EFFECTS.items():
        require(model in rows, f"missing efficiency effect row for {model}")
        row = rows[model]
        for field, value in expected.items():
            if field == "sum_total_tokens_baseline_minus_contract":
                require(int(row[field]) == int(value), f"effect mismatch for {model}/{field}: expected {value}, got {row[field]}")
            else:
                require(close(row[field], value), f"effect mismatch for {model}/{field}: expected {value}, got {row[field]}")
    require(all(float(row["token_tax_reduction"]) > 0 for row in rows.values()), "all models should reduce normalized token tax")
    require(all(float(row["mean_total_tokens_baseline_minus_contract"]) < 0 for row in rows.values()), "all contracts should use more absolute total tokens")


def check_report(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "it is not a dollar-cost estimate",
        "The Global Interaction Contract lowers normalized token tax for every full-run model",
        "it increases absolute total tokens for every full-run model",
        "`gpt-5.5` contract is the strongest alignment point: 98.3% FTGA",
        "it still uses 114.5 more absolute tokens per item on average",
        "`gpt-5.4-mini` shows the lower-cost-current-model boundary",
        "deployment-diagnostic framing rather than a simple cost-saving claim",
    ]
    for phrase in required:
        require(phrase in normalized, f"efficiency report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root
    out_dir = root / "results/tables/efficiency_tradeoff_v02"
    check_summary(out_dir / "efficiency_tradeoff_by_model_condition.csv")
    check_effects(out_dir / "efficiency_tradeoff_paired_effects.csv")
    check_report(root / "paper/efficiency_tradeoff_v02.md")
    print("efficiency tradeoff validation passed")


if __name__ == "__main__":
    main()
