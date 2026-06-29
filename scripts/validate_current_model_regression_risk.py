#!/usr/bin/env python
"""Validate current-model contract-regression risk artifacts."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


EXPECTED_SUMMARY = {
    "gpt-5.4-mini": {
        "n_pairs": 120,
        "both_pass_n": 91,
        "baseline_fail_contract_pass_n": 11,
        "baseline_pass_contract_fail_n": 5,
        "both_fail_n": 13,
        "ftga_regression_rate_pct": 4.2,
        "baseline_unresolved_contract_resolved_n": 1,
        "baseline_resolved_contract_unresolved_n": 4,
        "content_pass_on_contract_regression_n": 3,
        "content_unresolved_on_contract_regression_n": 1,
        "contract_regression_items": "ar_en_SD_006;ar_en_SD_007;es_en_SD_010;hi_en_SC_003;hi_en_SC_008",
    },
    "gpt-5.5": {
        "n_pairs": 120,
        "both_pass_n": 98,
        "baseline_fail_contract_pass_n": 20,
        "baseline_pass_contract_fail_n": 0,
        "both_fail_n": 2,
        "ftga_regression_rate_pct": 0.0,
        "baseline_unresolved_contract_resolved_n": 2,
        "baseline_resolved_contract_unresolved_n": 0,
        "content_pass_on_contract_regression_n": 0,
        "content_unresolved_on_contract_regression_n": 0,
        "contract_regression_items": "none",
    },
}

EXPECTED_REGRESSION_IDS = {
    "ar_en_SD_006",
    "ar_en_SD_007",
    "es_en_SD_010",
    "hi_en_SC_003",
    "hi_en_SC_008",
}
EXPECTED_CONTENT_PASS_REGRESSION_IDS = {"ar_en_SD_007", "hi_en_SC_003", "hi_en_SC_008"}
EXPECTED_RESOLVED_TO_UNRESOLVED_IDS = {
    "ar_en_SD_006",
    "ar_en_SD_008",
    "hi_en_SC_003",
    "hi_en_SC_008",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing current-model regression-risk table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def close(actual: str, expected: float, *, decimals: int = 1) -> bool:
    return round(float(actual), decimals) == round(float(expected), decimals)


def check_summary(path: Path) -> None:
    rows = {row["model"]: row for row in load_csv(path)}
    require(set(rows) == set(EXPECTED_SUMMARY), f"unexpected regression-risk models: {sorted(rows)}")
    for model, expected in EXPECTED_SUMMARY.items():
        row = rows[model]
        for field, expected_value in expected.items():
            if isinstance(expected_value, str):
                require(row[field] == expected_value, f"{model}/{field} expected {expected_value}, got {row[field]}")
            elif isinstance(expected_value, int):
                require(int(row[field]) == expected_value, f"{model}/{field} expected {expected_value}, got {row[field]}")
            else:
                require(close(row[field], expected_value), f"{model}/{field} expected {expected_value}, got {row[field]}")


def check_regression_cases(path: Path) -> None:
    rows = load_csv(path)
    require(len(rows) == 5, f"expected 5 contract-regression rows, found {len(rows)}")
    require({row["model"] for row in rows} == {"gpt-5.4-mini"}, "regression rows should only be gpt-5.4-mini")
    ids = {row["item_id"] for row in rows}
    require(ids == EXPECTED_REGRESSION_IDS, f"unexpected contract-regression ids: {sorted(ids)}")
    content_pass_ids = {row["item_id"] for row in rows if row["content_preservation_ftga"] == "1"}
    require(
        content_pass_ids == EXPECTED_CONTENT_PASS_REGRESSION_IDS,
        f"unexpected content-preservation pass ids: {sorted(content_pass_ids)}",
    )
    require(sum(int(row["contract_unresolved"]) for row in rows) == 3, "expected 3 unresolved contract regressions")
    require(
        sum(int(row["content_preservation_unresolved"]) for row in rows) == 1,
        "expected 1 unresolved content-preservation row among contract regressions",
    )
    family_counts = Counter(row["task_family"] for row in rows)
    require(
        family_counts == Counter({"script_register_locale": 3, "quote_preservation": 2}),
        f"unexpected regression family counts: {dict(family_counts)}",
    )


def check_resolved_to_unresolved(path: Path) -> None:
    rows = load_csv(path)
    require(len(rows) == 4, f"expected 4 resolved-to-unresolved rows, found {len(rows)}")
    require({row["model"] for row in rows} == {"gpt-5.4-mini"}, "unresolved-shift rows should only be gpt-5.4-mini")
    ids = {row["item_id"] for row in rows}
    require(ids == EXPECTED_RESOLVED_TO_UNRESOLVED_IDS, f"unexpected resolved-to-unresolved ids: {sorted(ids)}")
    require(
        sum(int(row["content_preservation_unresolved"]) for row in rows) == 2,
        "expected 2 content-preservation unresolved rows among resolved-to-unresolved shifts",
    )


def check_report(path: Path) -> None:
    require(path.exists(), f"missing current-model regression-risk report {path}")
    normalized = " ".join(path.read_text(encoding="utf-8").split())
    required = [
        "Current-Model Contract Regression Risk",
        "It uses saved full-120 trajectory metrics plus saved content-preservation rows; it makes no API calls",
        "`gpt-5.5` has 20 baseline-fail/contract-pass fixes, 0 first-turn regressions",
        "`gpt-5.4-mini` has 11 fixes but 5 first-turn regressions",
        "4 resolved-to-unresolved shifts",
        "not in output-language inference",
        "Content-preservation avoids first-turn failure on 3 of the 5",
        "not uniformly safer than the narrower preservation scaffold",
        "explicit regression risk",
    ]
    for phrase in required:
        require(phrase in normalized, f"current-model regression-risk report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tables-dir", type=Path, default=Path("results/tables/current_model_regression_risk_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/current_model_regression_risk_v02.md"))
    args = parser.parse_args()

    check_summary(args.tables_dir / "current_model_regression_risk_summary.csv")
    check_regression_cases(args.tables_dir / "current_model_contract_regression_cases.csv")
    check_resolved_to_unresolved(args.tables_dir / "current_model_resolved_to_unresolved_cases.csv")
    check_report(args.report)
    print("current-model regression-risk validation passed")


if __name__ == "__main__":
    main()
