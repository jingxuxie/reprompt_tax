#!/usr/bin/env python
"""Validate the human/native-review threshold-rationale report."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED = {
    ("human_audit_v02_gpt41_family", "overall_pass_agreement"): {
        "threshold_count": "65",
        "denominator": "72",
        "threshold_rate_pct": "90.3",
    },
    ("human_audit_v02_gpt41_family", "component_agreement"): {
        "threshold_count": "306",
        "denominator": "360",
        "threshold_rate_pct": "85.0",
    },
    ("human_audit_v02_current_gpt5", "overall_pass_agreement"): {
        "threshold_count": "44",
        "denominator": "48",
        "threshold_rate_pct": "91.7",
    },
    ("human_audit_v02_current_gpt5", "component_agreement"): {
        "threshold_count": "204",
        "denominator": "240",
        "threshold_rate_pct": "85.0",
    },
    ("coverage_native_review_v03", "release_usable_rows"): {
        "threshold_count": "60",
        "denominator": "60",
        "threshold_rate_pct": "100.0",
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing threshold-rationale table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_table(path: Path) -> None:
    rows = read_csv(path)
    by_key = {(row["surface"], row["metric"]): row for row in rows}
    require(set(by_key) == set(EXPECTED), f"unexpected threshold-rationale rows: {sorted(by_key)}")
    for key, expected in EXPECTED.items():
        row = by_key[key]
        for field, value in expected.items():
            require(row[field] == value, f"{key} {field} mismatch: expected {value}, got {row[field]}")
        for field in ("wilson_95_low_pct", "wilson_95_high_pct", "rationale"):
            require(row[field], f"{key} missing {field}")
        require(float(row["wilson_95_low_pct"]) <= float(row["threshold_rate_pct"]), f"{key} Wilson lower bound exceeds point estimate")
        require(float(row["wilson_95_high_pct"]) >= float(row["threshold_rate_pct"]), f"{key} Wilson upper bound below point estimate")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing threshold-rationale report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "Human/Native Review Threshold Rationale",
        "It does not report completed labels",
        "65/72",
        "306/360",
        "44/48",
        "204/240",
        "60/60",
        "Wilson 95% interval",
        "Passing these thresholds is necessary but not sufficient",
        "qualified rosters",
        "claim-gate analyzer",
    ]
    for phrase in required:
        require(phrase in normalized, f"threshold-rationale report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--table", type=Path, default=Path("results/tables/human_audit_threshold_rationale_v02/human_audit_threshold_rationale.csv"))
    parser.add_argument("--report", type=Path, default=Path("paper/human_audit_threshold_rationale_v02.md"))
    args = parser.parse_args()

    check_table(args.table)
    check_report(args.report)
    print("human/native-review threshold-rationale validation passed")


if __name__ == "__main__":
    main()
