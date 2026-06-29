#!/usr/bin/env python
"""Validate current-model refresh artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


EXPECTED_SUMMARY = {
    ("gpt-5.4-mini", "full120"): {
        "n_items": 120,
        "baseline_ftga_pct": 80.0,
        "contract_ftga_pct": 85.0,
        "delta_ftga_pp": 5.0,
        "baseline_mean_rtt": 0.25,
        "contract_mean_rtt": 0.25,
        "token_tax_reduction": 0.138,
        "baseline_unresolved_pct": 2.5,
        "contract_unresolved_pct": 5.0,
        "ftga_sign_p": 0.210113525390625,
        "token_tax_sign_p": 0.002315700054168701,
    },
    ("gpt-5.5", "full120"): {
        "n_items": 120,
        "baseline_ftga_pct": 81.7,
        "contract_ftga_pct": 98.3,
        "delta_ftga_pp": 16.7,
        "baseline_mean_rtt": 0.225,
        "contract_mean_rtt": 0.017,
        "token_tax_reduction": 0.262,
        "baseline_unresolved_pct": 1.7,
        "contract_unresolved_pct": 0.0,
        "ftga_sign_p": 1.9073486328125e-06,
        "token_tax_sign_p": 4.76837158203125e-07,
    },
}

EXPECTED_USAGE = {
    "gpt-5.4-mini full120": {"api_calls": 291, "input_tokens": 40286, "output_tokens": 8730, "total_tokens": 49016},
    "gpt-5.5 full120": {"api_calls": 267, "input_tokens": 34172, "output_tokens": 18995, "total_tokens": 53167},
}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_summary(path: Path) -> None:
    rows = {(row["model"], row["scope"]): row for row in load_csv(path)}
    for key, expected in EXPECTED_SUMMARY.items():
        require(key in rows, f"missing current-model summary row {key}")
        row = rows[key]
        for field, expected_value in expected.items():
            actual = int(row[field]) if field == "n_items" else round(float(row[field]), 12)
            expected_rounded = expected_value if field == "n_items" else round(float(expected_value), 12)
            require(actual == expected_rounded, f"summary mismatch for {key}/{field}: expected {expected_value}, got {actual}")


def check_usage(path: Path) -> None:
    rows = {row["artifact"]: row for row in load_csv(path)}
    for artifact, expected in EXPECTED_USAGE.items():
        require(artifact in rows, f"missing usage row {artifact}")
        actual = {field: int(rows[artifact][field]) for field in expected}
        require(actual == expected, f"usage mismatch for {artifact}: expected {expected}, got {actual}")


def check_benchmark_marker(path: Path) -> None:
    target_ids = {"es_en_SB_001", "hi_en_SB_001", "ar_en_SB_001"}
    rows = {row["id"]: row for row in load_jsonl(path) if row["id"] in target_ids}
    require(set(rows) == target_ids, f"missing benchmark rows for insufficient marker check: {set(rows)}")
    for item_id, row in rows.items():
        markers = row.get("required_any_markers", [])
        require("data are insufficient" in markers, f"{item_id} missing accepted marker: data are insufficient")


def check_report(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "The earlier GPT-5.5 40-item stratified/enriched pilot is retained only as a development smoke check",
        "`gpt-5.4-mini` improves FTGA from 80.0% to 85.0%",
        "The unresolved rate moves from 2.5% to 5.0%",
        "FTGA rises from 81.7% to 98.3%",
        "The contract leaves two first-turn failures but no unresolved trajectories.",
        "A scorer-coverage fix added `data are insufficient`",
    ]
    for phrase in required:
        require(phrase in normalized, f"current-model report missing phrase: {phrase}")


def check_gpt55_scores(path: Path) -> None:
    rows = load_jsonl(path)
    first_turn_failures = [
        row
        for row in rows
        if row["model"] == "gpt-5.5" and row["condition"] == "contract" and int(row["turn"]) == 0 and not row["pass"]
    ]
    unresolved = [
        row
        for row in rows
        if row["model"] == "gpt-5.5" and row["condition"] == "contract" and int(row["turn"]) == 2 and not row["pass"]
    ]
    require(len(first_turn_failures) == 2, f"expected two GPT-5.5 contract first-turn failures, found {len(first_turn_failures)}")
    require(not unresolved, f"expected zero GPT-5.5 contract unresolved failures, found {len(unresolved)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root

    check_summary(root / "results/tables/current_model_refresh_v02/current_model_refresh_summary.csv")
    check_usage(root / "results/tables/current_model_refresh_v02/current_model_refresh_api_usage.csv")
    check_benchmark_marker(root / "data/benchmark_stress_v0.2.jsonl")
    check_report(root / "paper/current_model_refresh_v02.md")
    check_gpt55_scores(root / "results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl")
    print("current-model refresh validation passed")


if __name__ == "__main__":
    main()
