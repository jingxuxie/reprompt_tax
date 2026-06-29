#!/usr/bin/env python
"""Validate current-model prompt-mechanism artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ExpectedMechanism:
    label: str
    model: str
    tables_dir: Path
    report_path: Path
    content_outputs_path: Path
    summary: dict[str, dict[str, float | int]]
    paired: dict[str, dict[str, float | int]]
    usage: dict[str, dict[str, int]]
    expected_content_rows: int
    report_phrases: tuple[str, ...]


EXPECTED = [
    ExpectedMechanism(
        label="gpt54mini",
        model="gpt-5.4-mini",
        tables_dir=Path("results/tables/current_prompt_mechanism_gpt54mini_v02"),
        report_path=Path("paper/current_prompt_mechanism_gpt54mini_v02.md"),
        content_outputs_path=Path("results/model_outputs/openai_gpt54mini_stress_v02_full120_content_preservation.jsonl"),
        summary={
            "baseline": {
                "n_items": 120,
                "ftga_pct": 80.0,
                "mean_rtt": 0.25,
                "token_tax": 1.379,
                "unresolved_pct": 2.5,
                "initial_failures": 24,
            },
            "contract": {
                "n_items": 120,
                "ftga_pct": 85.0,
                "mean_rtt": 0.25,
                "token_tax": 1.241,
                "unresolved_pct": 5.0,
                "initial_failures": 18,
            },
            "content_preservation": {
                "n_items": 120,
                "ftga_pct": 85.8,
                "mean_rtt": 0.242,
                "token_tax": 1.252,
                "unresolved_pct": 5.0,
                "initial_failures": 17,
            },
        },
        paired={
            "contract_minus_baseline": {
                "n_pairs": 120,
                "ftga_improved": 11,
                "ftga_worsened": 5,
                "ftga_tied": 104,
                "ftga_sign_test_p": 0.210113525390625,
                "delta_ftga_pp": 5.0,
                "rtt_reduction": 0.0,
                "token_tax_reduction": 0.138,
                "unresolved_reduction_pp": -2.5,
            },
            "content_preservation_minus_baseline": {
                "n_pairs": 120,
                "ftga_improved": 11,
                "ftga_worsened": 4,
                "ftga_tied": 105,
                "ftga_sign_test_p": 0.11846923828125,
                "delta_ftga_pp": 5.8,
                "rtt_reduction": 0.008,
                "token_tax_reduction": 0.128,
                "unresolved_reduction_pp": -2.5,
            },
            "content_preservation_minus_contract": {
                "n_pairs": 120,
                "ftga_improved": 5,
                "ftga_worsened": 4,
                "ftga_tied": 111,
                "ftga_sign_test_p": 1.0,
                "delta_ftga_pp": 0.8,
                "rtt_reduction": 0.008,
                "token_tax_reduction": -0.01,
                "unresolved_reduction_pp": 0.0,
            },
        },
        usage={
            "baseline+contract": {"api_calls": 291, "input_tokens": 40286, "output_tokens": 8730, "total_tokens": 49016},
            "content_preservation": {"api_calls": 143, "input_tokens": 19353, "output_tokens": 2882, "total_tokens": 22235},
        },
        expected_content_rows=143,
        report_phrases=(
            "Content preservation improves FTGA from 80.0% to 85.8%",
            "Against the full contract, content preservation changes FTGA by +0.8 pp",
            "5 improved, 4 worsened items",
            "essentially tied with the full contract",
            "rather than clearly dominating it as in the earlier nano diagnostic",
        ),
    ),
    ExpectedMechanism(
        label="gpt55",
        model="gpt-5.5",
        tables_dir=Path("results/tables/current_prompt_mechanism_gpt55_v02"),
        report_path=Path("paper/current_prompt_mechanism_gpt55_v02.md"),
        content_outputs_path=Path("results/model_outputs/openai_gpt55_stress_v02_full120_content_preservation.jsonl"),
        summary={
            "baseline": {
                "n_items": 120,
                "ftga_pct": 81.7,
                "mean_rtt": 0.225,
                "token_tax": 1.278,
                "unresolved_pct": 1.7,
                "initial_failures": 22,
            },
            "contract": {
                "n_items": 120,
                "ftga_pct": 98.3,
                "mean_rtt": 0.017,
                "token_tax": 1.016,
                "unresolved_pct": 0.0,
                "initial_failures": 2,
            },
            "content_preservation": {
                "n_items": 120,
                "ftga_pct": 99.2,
                "mean_rtt": 0.008,
                "token_tax": 1.012,
                "unresolved_pct": 0.0,
                "initial_failures": 1,
            },
        },
        paired={
            "contract_minus_baseline": {
                "n_pairs": 120,
                "ftga_improved": 20,
                "ftga_worsened": 0,
                "ftga_tied": 100,
                "ftga_sign_test_p": 1.9073486328125e-06,
                "delta_ftga_pp": 16.7,
                "rtt_reduction": 0.208,
                "token_tax_reduction": 0.262,
                "unresolved_reduction_pp": 1.7,
            },
            "content_preservation_minus_baseline": {
                "n_pairs": 120,
                "ftga_improved": 22,
                "ftga_worsened": 1,
                "ftga_tied": 97,
                "ftga_sign_test_p": 5.7220458984375e-06,
                "delta_ftga_pp": 17.5,
                "rtt_reduction": 0.217,
                "token_tax_reduction": 0.267,
                "unresolved_reduction_pp": 1.7,
            },
            "content_preservation_minus_contract": {
                "n_pairs": 120,
                "ftga_improved": 2,
                "ftga_worsened": 1,
                "ftga_tied": 117,
                "ftga_sign_test_p": 1.0,
                "delta_ftga_pp": 0.8,
                "rtt_reduction": 0.008,
                "token_tax_reduction": 0.005,
                "unresolved_reduction_pp": 0.0,
            },
        },
        usage={
            "baseline+contract": {"api_calls": 267, "input_tokens": 34172, "output_tokens": 18995, "total_tokens": 53167},
            "content_preservation": {"api_calls": 121, "input_tokens": 15310, "output_tokens": 7691, "total_tokens": 23001},
        },
        expected_content_rows=121,
        report_phrases=(
            "Content preservation improves FTGA from 81.7% to 99.2%",
            "Against the full contract, content preservation changes FTGA by +0.8 pp",
            "2 improved, 1 worsened items",
            "the difference from the full contract is one net item",
            "mechanism evidence, not as a dominance claim",
        ),
    ),
]


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


def numeric(row: dict[str, str], field: str, expected: float | int) -> float | int:
    if isinstance(expected, int):
        return int(row[field])
    return round(float(row[field]), 12)


def check_summary(config: ExpectedMechanism) -> None:
    rows = {row["condition"]: row for row in load_csv(config.tables_dir / "current_prompt_mechanism_summary.csv")}
    require(set(rows) == set(config.summary), f"unexpected mechanism summary rows for {config.label}: {set(rows)}")
    for condition, expected in config.summary.items():
        row = rows[condition]
        require(row["model"] == config.model, f"unexpected model in {config.label}/{condition}: {row['model']}")
        for field, value in expected.items():
            actual = numeric(row, field, value)
            expected_rounded = value if isinstance(value, int) else round(value, 12)
            require(actual == expected_rounded, f"summary mismatch for {config.label}/{condition}/{field}: expected {value}, got {actual}")


def check_paired(config: ExpectedMechanism) -> None:
    rows = {row["comparison"]: row for row in load_csv(config.tables_dir / "current_prompt_mechanism_paired_effects.csv")}
    require(set(rows) == set(config.paired), f"unexpected mechanism paired rows for {config.label}: {set(rows)}")
    for comparison, expected in config.paired.items():
        row = rows[comparison]
        for field, value in expected.items():
            actual = numeric(row, field, value)
            expected_rounded = value if isinstance(value, int) else round(value, 12)
            require(actual == expected_rounded, f"paired mismatch for {config.label}/{comparison}/{field}: expected {value}, got {actual}")


def check_usage(config: ExpectedMechanism) -> None:
    rows = {row["artifact"]: row for row in load_csv(config.tables_dir / "current_prompt_mechanism_api_usage.csv")}
    require(set(rows) == set(config.usage), f"unexpected mechanism usage rows for {config.label}: {set(rows)}")
    for artifact, expected in config.usage.items():
        actual = {field: int(rows[artifact][field]) for field in expected}
        require(actual == expected, f"usage mismatch for {config.label}/{artifact}: expected {expected}, got {actual}")


def check_outputs(config: ExpectedMechanism) -> None:
    rows = load_jsonl(config.content_outputs_path)
    first_turn = [row for row in rows if int(row["turn"]) == 0]
    require(len(first_turn) == 120, f"expected 120 content-preservation first-turn rows for {config.label}, found {len(first_turn)}")
    require(
        len(rows) == config.expected_content_rows,
        f"expected {config.expected_content_rows} content-preservation response rows for {config.label}, found {len(rows)}",
    )
    require({row["condition"] for row in rows} == {"content_preservation"}, f"{config.label} content-preservation output has unexpected conditions")


def check_report(config: ExpectedMechanism) -> None:
    normalized = " ".join(config.report_path.read_text(encoding="utf-8").split())
    for phrase in config.report_phrases:
        require(phrase in normalized, f"{config.label} mechanism report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root

    for expected in EXPECTED:
        config = ExpectedMechanism(
            label=expected.label,
            model=expected.model,
            tables_dir=root / expected.tables_dir,
            report_path=root / expected.report_path,
            content_outputs_path=root / expected.content_outputs_path,
            summary=expected.summary,
            paired=expected.paired,
            usage=expected.usage,
            expected_content_rows=expected.expected_content_rows,
            report_phrases=expected.report_phrases,
        )
        check_summary(config)
        check_paired(config)
        check_usage(config)
        check_outputs(config)
        check_report(config)
    print("current prompt-mechanism validation passed")


if __name__ == "__main__":
    main()
