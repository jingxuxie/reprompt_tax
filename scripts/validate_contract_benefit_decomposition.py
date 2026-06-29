#!/usr/bin/env python
"""Validate contract-benefit decomposition artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_OVERALL = {
    "n_pairs": "600",
    "both_pass": "452",
    "both_fail": "75",
    "fixes": "67",
    "regressions": "6",
    "net_first_turn_gain": "61",
}

EXPECTED_FAMILY = {
    "editing_preservation": {"n_pairs": "150", "fixes": "61", "regressions": "0", "net_first_turn_gain": "61"},
    "output_language_inference": {"n_pairs": "150", "fixes": "1", "regressions": "0", "net_first_turn_gain": "1"},
    "quote_preservation": {"n_pairs": "150", "fixes": "1", "regressions": "2", "net_first_turn_gain": "-1"},
    "script_register_locale": {"n_pairs": "150", "fixes": "4", "regressions": "4", "net_first_turn_gain": "0"},
}

EXPECTED_GENERATION = {
    "GPT-4.1 family": {"n_pairs": "360", "fixes": "36", "regressions": "1", "net_first_turn_gain": "35"},
    "GPT-5.x family": {"n_pairs": "240", "fixes": "31", "regressions": "5", "net_first_turn_gain": "26"},
}

EXPECTED_LANGUAGE = {
    "ar-en": {"n_pairs": "200", "fixes": "43", "regressions": "2", "net_first_turn_gain": "41"},
    "es-en": {"n_pairs": "200", "fixes": "20", "regressions": "1", "net_first_turn_gain": "19"},
    "hi-en": {"n_pairs": "200", "fixes": "4", "regressions": "3", "net_first_turn_gain": "1"},
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing decomposition table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_fields(row: dict[str, str], expected: dict[str, str], *, label: str) -> None:
    for field, value in expected.items():
        require(row[field] == value, f"{label} {field} mismatch: expected {value}, got {row[field]}")


def check_keyed(path: Path, key: str, expected: dict[str, dict[str, str]]) -> None:
    rows = {row[key]: row for row in read_csv(path)}
    require(set(rows) == set(expected), f"{path} unexpected keys: {sorted(rows)}")
    for label, expected_fields in expected.items():
        check_fields(rows[label], expected_fields, label=label)


def check_report(path: Path) -> None:
    require(path.exists(), f"missing decomposition report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "Contract Benefit Decomposition",
        "67 first-turn fixes and 6 first-turn regressions",
        "net first-turn gain of 61",
        "Editing preservation accounts for 61 of 67 fixes",
        "91.0%",
        "zero regressions",
        "exactly equals the overall +61 net first-turn gain",
        "does not unlock native/near-native validation claims",
    ]
    for phrase in required:
        require(phrase in normalized, f"decomposition report missing phrase: {phrase}")


def check_main_tex(path: Path) -> None:
    require(path.exists(), f"missing paper TeX {path}")
    text = " ".join(path.read_text(encoding="utf-8").split())
    for phrase in (
        "61 of 67 contract fixes",
        "all +61 net first-turn gain",
    ):
        require(phrase in text, f"main TeX missing decomposition phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/contract_benefit_decomposition_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/contract_benefit_decomposition_v02.md"))
    parser.add_argument("--main-tex", type=Path, default=Path("paper/sections/05_results.tex"))
    args = parser.parse_args()

    overall_rows = read_csv(args.out_dir / "contract_benefit_overall.csv")
    require(len(overall_rows) == 1, "expected one overall decomposition row")
    check_fields(overall_rows[0], EXPECTED_OVERALL, label="overall")
    check_keyed(args.out_dir / "contract_benefit_by_family.csv", "task_family", EXPECTED_FAMILY)
    check_keyed(args.out_dir / "contract_benefit_by_generation.csv", "generation", EXPECTED_GENERATION)
    check_keyed(args.out_dir / "contract_benefit_by_language.csv", "language_pair", EXPECTED_LANGUAGE)
    check_report(args.report)
    check_main_tex(args.main_tex)
    print("contract-benefit decomposition validation passed")


if __name__ == "__main__":
    main()
