#!/usr/bin/env python
"""Validate balanced-subsample robustness artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_FULL = {
    "all_models": {"n_items": "120", "n_model_item_pairs": "600", "full_delta_pp": "10.2", "full_improved_pairs": "67", "full_worsened_pairs": "6"},
    "gpt-4.1": {"n_items": "120", "n_model_item_pairs": "120", "full_delta_pp": "16.7", "full_improved_pairs": "20", "full_worsened_pairs": "0"},
    "gpt-4.1-mini": {"n_items": "120", "n_model_item_pairs": "120", "full_delta_pp": "3.3", "full_improved_pairs": "4", "full_worsened_pairs": "0"},
    "gpt-4.1-nano": {"n_items": "120", "n_model_item_pairs": "120", "full_delta_pp": "9.2", "full_improved_pairs": "12", "full_worsened_pairs": "1"},
    "gpt-5.4-mini": {"n_items": "120", "n_model_item_pairs": "120", "full_delta_pp": "5.0", "full_improved_pairs": "11", "full_worsened_pairs": "5"},
    "gpt-5.5": {"n_items": "120", "n_model_item_pairs": "120", "full_delta_pp": "16.7", "full_improved_pairs": "20", "full_worsened_pairs": "0"},
}

EXPECTED_K = {"1", "2", "3", "4", "5", "8", "10"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing balanced-subsample table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_full(path: Path) -> None:
    rows = read_csv(path)
    by_population = {row["population"]: row for row in rows}
    require(set(by_population) == set(EXPECTED_FULL), f"unexpected full-effect populations: {sorted(by_population)}")
    for population, expected in EXPECTED_FULL.items():
        row = by_population[population]
        for field, value in expected.items():
            require(row[field] == value, f"{population} {field} mismatch: expected {value}, got {row[field]}")


def check_simulations(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == len(EXPECTED_FULL) * len(EXPECTED_K), f"unexpected simulation row count: {len(rows)}")
    populations = {row["population"] for row in rows}
    require(populations == set(EXPECTED_FULL), f"unexpected simulation populations: {sorted(populations)}")
    for population in populations:
        pop_rows = [row for row in rows if row["population"] == population]
        require({row["k_per_cell"] for row in pop_rows} == EXPECTED_K, f"{population} missing k rows")
        for row in pop_rows:
            k = int(row["k_per_cell"])
            require(int(row["sample_items"]) == 12 * k, f"{population}/{k} sample item count mismatch")
            expected_pairs = 5 * 12 * k if population == "all_models" else 12 * k
            require(int(row["sample_model_item_pairs"]) == expected_pairs, f"{population}/{k} sample pair count mismatch")
            expected_reps = 1 if k == 10 else 2000
            require(int(row["simulation_reps"]) == expected_reps, f"{population}/{k} simulation reps mismatch")
            require(0 <= float(row["full_direction_recovered_fraction"]) <= 1, f"{population}/{k} invalid direction fraction")
            require(0 <= float(row["within_5pp_fraction"]) <= 1, f"{population}/{k} invalid within-5pp fraction")
            if k == 10:
                require(row["median_delta_pp"] == row["full_delta_pp"], f"{population}/10 should equal full delta")
                require(row["within_5pp_fraction"] == "1.0", f"{population}/10 should be within 5 pp")
    key = {(row["population"], row["k_per_cell"]): row for row in rows}
    require(float(key[("all_models", "4")]["full_direction_recovered_fraction"]) == 1.0, "48-item all-model pilots should recover positive direction")
    require(float(key[("gpt-5.5", "4")]["full_direction_recovered_fraction"]) == 1.0, "48-item GPT-5.5 pilots should recover positive direction")
    require(float(key[("gpt-4.1-mini", "4")]["within_5pp_fraction"]) < 1.0, "weak mini effect should show sampling instability")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing balanced-subsample report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "Balanced Subsample Robustness",
        "no-API diagnostic",
        "small pilots recover the full-run direction",
        "does not replace the full-run results or native/near-native validation",
        "At the 48-item balanced-pilot scale",
        "all-model aggregate recovers the full positive direction",
        "The GPT-5.5 headline is stable",
        "Weaker effects remain appropriately unstable",
        "full paper claims should remain anchored to the complete 120-item runs",
    ]
    for phrase in required:
        require(phrase in normalized, f"balanced-subsample report missing phrase: {phrase}")


def check_results_tex(path: Path) -> None:
    require(path.exists(), f"missing results section {path}")
    text = " ".join(path.read_text(encoding="utf-8").split())
    required = [
        "Balanced 48-item stratified pilots recover the all-model and \\texttt{gpt-5.5} positive directions in 100\\% of saved-trajectory simulations",
        "smaller-effect models remain less stable",
    ]
    for phrase in required:
        require(phrase in text, f"results section missing balanced-subsample phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/balanced_subsample_robustness_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/balanced_subsample_robustness_v02.md"))
    parser.add_argument("--results-tex", type=Path, default=Path("paper/sections/05_results.tex"))
    args = parser.parse_args()

    check_full(args.out_dir / "balanced_subsample_full_effects.csv")
    check_simulations(args.out_dir / "balanced_subsample_simulations.csv")
    check_report(args.report)
    check_results_tex(args.results_tex)
    print("balanced-subsample robustness validation passed")


if __name__ == "__main__":
    main()
