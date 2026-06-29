#!/usr/bin/env python
"""Validate current-model uncertainty artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_ROWS = {
    "gpt-5.4-mini": {
        "n_pairs": 120,
        "ftga_delta_pp": 5.0,
        "ftga_ci_low_pp": -0.8,
        "ftga_ci_high_pp": 11.7,
        "ftga_improved_n": 11,
        "ftga_worsened_n": 5,
        "ftga_tie_n": 104,
        "ftga_sign_p": 0.210113525390625,
        "rtt_reduction": 0.0,
        "rtt_ci_low": -0.117,
        "rtt_ci_high": 0.117,
        "token_tax_reduction": 0.138,
        "token_tax_ci_low": 0.010,
        "token_tax_ci_high": 0.269,
        "token_tax_improved_n": 23,
        "token_tax_worsened_n": 6,
        "token_tax_tie_n": 91,
        "token_tax_sign_p": 0.002315700054168701,
        "unresolved_reduction_pp": -2.5,
        "unresolved_ci_low_pp": -6.7,
        "unresolved_ci_high_pp": 0.8,
        "claim_scope": "bounded_token_tax_effect_directional_ftga",
    },
    "gpt-5.5": {
        "n_pairs": 120,
        "ftga_delta_pp": 16.7,
        "ftga_ci_low_pp": 10.0,
        "ftga_ci_high_pp": 24.2,
        "ftga_improved_n": 20,
        "ftga_worsened_n": 0,
        "ftga_tie_n": 100,
        "ftga_sign_p": 1.9073486328125e-06,
        "rtt_reduction": 0.208,
        "rtt_ci_low": 0.125,
        "rtt_ci_high": 0.308,
        "token_tax_reduction": 0.262,
        "token_tax_ci_low": 0.164,
        "token_tax_ci_high": 0.374,
        "token_tax_improved_n": 22,
        "token_tax_worsened_n": 0,
        "token_tax_tie_n": 98,
        "token_tax_sign_p": 4.76837158203125e-07,
        "unresolved_reduction_pp": 1.7,
        "unresolved_ci_low_pp": 0.0,
        "unresolved_ci_high_pp": 4.2,
        "claim_scope": "headline_current_model_effect",
    },
}

INT_FIELDS = {
    "n_pairs",
    "ftga_improved_n",
    "ftga_worsened_n",
    "ftga_tie_n",
    "token_tax_improved_n",
    "token_tax_worsened_n",
    "token_tax_tie_n",
}
STRING_FIELDS = {"claim_scope"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing current-model uncertainty table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def close(actual: str, expected: float, *, decimals: int = 3) -> bool:
    return round(float(actual), decimals) == round(float(expected), decimals)


def check_table(path: Path) -> None:
    rows = {row["model"]: row for row in load_csv(path)}
    require(set(rows) == set(EXPECTED_ROWS), f"unexpected current-model uncertainty rows: {sorted(rows)}")
    for model, expected in EXPECTED_ROWS.items():
        row = rows[model]
        for field, expected_value in expected.items():
            if field in STRING_FIELDS:
                require(row[field] == expected_value, f"{model}/{field} expected {expected_value}, got {row[field]}")
            elif field in INT_FIELDS:
                require(int(row[field]) == int(expected_value), f"{model}/{field} expected {expected_value}, got {row[field]}")
            else:
                require(close(row[field], float(expected_value)), f"{model}/{field} expected {expected_value}, got {row[field]}")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing current-model uncertainty report {path}")
    normalized = " ".join(path.read_text(encoding="utf-8").split())
    required = [
        "Current-Model Uncertainty And Claim Scope",
        "item-bootstrap intervals over the 120 synthetic paired items",
        "do not replace native/near-native validation",
        "gpt-5.5` headline survives both bootstrap and exact paired sign-test checks",
        "FTGA improves by 16.7 pp with a [10.0, 24.2] pp item-bootstrap interval",
        "20 improved, 0 worsened, 100 tied items",
        "gpt-5.4-mini` FTGA interval crosses zero",
        "FTGA improves by 5.0 pp, but the interval is [-0.8, 11.7] pp",
        "The token-tax interval remains positive for `gpt-5.4-mini`",
        "Native/near-native audit labels are still required",
    ]
    for phrase in required:
        require(phrase in normalized, f"current-model uncertainty report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tables-dir", type=Path, default=Path("results/tables/current_model_uncertainty_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/current_model_uncertainty_v02.md"))
    args = parser.parse_args()

    check_table(args.tables_dir / "current_model_uncertainty.csv")
    check_report(args.report)
    print("current-model uncertainty validation passed")


if __name__ == "__main__":
    main()
