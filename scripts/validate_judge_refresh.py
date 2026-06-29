#!/usr/bin/env python
"""Validate GPT-5.5 judge-refresh artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


EXPECTED_SUMMARY = {
    "gpt41": {
        "judge_model": "gpt-4.1",
        "n": 72,
        "auto_agreement_n": 71,
        "auto_agreement_pct": 98.6,
        "auto_agreement_ci_low": 92.5,
        "auto_agreement_ci_high": 99.8,
        "auto_pass_n": 64,
        "judge_pass_n": 65,
        "auto_fail_judge_pass_n": 1,
        "auto_pass_judge_fail_n": 0,
        "judge_parse_error_n": 0,
        "input_tokens": 20607,
        "output_tokens": 5339,
        "total_tokens": 25946,
    },
    "gpt55": {
        "judge_model": "gpt-5.5",
        "n": 72,
        "auto_agreement_n": 70,
        "auto_agreement_pct": 97.2,
        "auto_agreement_ci_low": 90.4,
        "auto_agreement_ci_high": 99.2,
        "auto_pass_n": 64,
        "judge_pass_n": 62,
        "auto_fail_judge_pass_n": 0,
        "auto_pass_judge_fail_n": 2,
        "judge_parse_error_n": 0,
        "input_tokens": 20535,
        "output_tokens": 10512,
        "total_tokens": 31047,
    },
}

EXPECTED_PAIRWISE = {
    "judge_a": "gpt-4.1",
    "judge_b": "gpt-5.5",
    "n": 72,
    "pass_fail_agreement_n": 69,
    "pass_fail_agreement_pct": 95.8,
    "pass_fail_agreement_ci_low": 88.5,
    "pass_fail_agreement_ci_high": 98.6,
    "both_pass_n": 62,
    "both_fail_n": 7,
    "judge_a_pass_judge_b_fail_n": 3,
    "judge_a_fail_judge_b_pass_n": 0,
}

EXPECTED_DISAGREEMENTS = {
    "es_en_SA_007": {"auto_pass": False, "gpt41_judge_pass": True, "gpt55_judge_pass": False},
    "hi_en_SA_009": {"auto_pass": True, "gpt41_judge_pass": True, "gpt55_judge_pass": False},
    "hi_en_SC_008": {"auto_pass": True, "gpt41_judge_pass": True, "gpt55_judge_pass": False},
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


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return bool(value)


def compare_value(row: dict[str, str], field: str, expected: Any, context: str) -> None:
    if isinstance(expected, bool):
        actual: Any = bool_value(row[field])
    elif isinstance(expected, int):
        actual = int(row[field])
    elif isinstance(expected, float):
        actual = round(float(row[field]), 1)
        expected = round(expected, 1)
    else:
        actual = row[field]
    require(actual == expected, f"{context}/{field}: expected {expected}, got {actual}")


def check_raw_audit(path: Path) -> None:
    rows = load_jsonl(path)
    require(len(rows) == 72, f"expected 72 GPT-5.5 judge rows, found {len(rows)}")
    require(len({(row['item_id'], row['model'], row['condition'], int(row['turn'])) for row in rows}) == 72, "duplicate GPT-5.5 judge keys")
    require(all(row.get("judge_model") == "gpt-5.5" for row in rows), "unexpected judge model in GPT-5.5 audit")
    require(all(not row.get("judge_parse_error") for row in rows), "GPT-5.5 judge audit has parse errors")
    agree = sum(bool_value(row["auto_pass"]) == bool_value(row["judge_pass"]) for row in rows)
    require(agree == 70, f"expected 70/72 GPT-5.5 auto agreement, got {agree}/72")
    disagreements = [row["item_id"] for row in rows if bool_value(row["auto_pass"]) != bool_value(row["judge_pass"])]
    require(disagreements == ["hi_en_SA_009", "hi_en_SC_008"], f"unexpected GPT-5.5 disagreements: {disagreements}")


def check_summary(path: Path) -> None:
    rows = {row["judge_label"]: row for row in load_csv(path)}
    require(set(rows) == set(EXPECTED_SUMMARY), f"unexpected summary rows: {set(rows)}")
    for label, expected in EXPECTED_SUMMARY.items():
        for field, value in expected.items():
            compare_value(rows[label], field, value, f"summary/{label}")


def check_pairwise(path: Path) -> None:
    rows = load_csv(path)
    require(len(rows) == 1, f"expected one pairwise row, found {len(rows)}")
    for field, value in EXPECTED_PAIRWISE.items():
        compare_value(rows[0], field, value, "pairwise")


def check_disagreements(path: Path) -> None:
    rows = {row["item_id"]: row for row in load_csv(path)}
    require(set(rows) == set(EXPECTED_DISAGREEMENTS), f"unexpected disagreement rows: {set(rows)}")
    for item_id, expected in EXPECTED_DISAGREEMENTS.items():
        for field, value in expected.items():
            compare_value(rows[item_id], field, value, f"disagreement/{item_id}")


def check_report(path: Path) -> None:
    text = " ".join(path.read_text(encoding="utf-8").split())
    for phrase in (
        "with `gpt-5.5` and compares it with the saved `gpt-4.1` judge audit",
        "gpt-4.1` judge agrees with the automatic scorer on 71/72",
        "`gpt-5.5` judge agrees on 70/72",
        "two judges agree with each other on 69/72",
        "do not replace native/near-native validation",
    ):
        require(phrase in text, f"judge-refresh report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root
    table_dir = root / "results/tables/openai_three_model_stress_v02_full120_judge_refresh_gpt55"

    check_raw_audit(root / "results/scores/openai_three_model_stress_v02_full120_judge_gpt55_audit72.jsonl")
    check_summary(table_dir / "judge_refresh_summary.csv")
    check_pairwise(table_dir / "judge_refresh_pairwise_comparison.csv")
    check_disagreements(table_dir / "judge_refresh_disagreements.csv")
    check_report(root / "paper/judge_refresh_gpt55_v02_full120.md")
    print("judge-refresh validation passed")


if __name__ == "__main__":
    main()
