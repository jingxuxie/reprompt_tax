#!/usr/bin/env python
"""Validate scorer positive-control audit artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_OVERALL = {
    "n_controls": "120",
    "auto_pass_n": "120",
    "auto_pass_pct": "100.0",
    "all_components_pass_n": "120",
    "all_components_pass_pct": "100.0",
    "auto_failed_n": "0",
}

EXPECTED_BY_FAMILY = {
    "editing_preservation": {"n_controls": "30"},
    "output_language_inference": {"n_controls": "30"},
    "quote_preservation": {"n_controls": "30"},
    "script_register_locale": {"n_controls": "30"},
}

EXPECTED_BY_LANGUAGE = {
    "ar-en": {"n_controls": "40"},
    "es-en": {"n_controls": "40"},
    "hi-en": {"n_controls": "40"},
}

EXPECTED_BY_EXPECTED_LANGUAGE = {
    "Arabic": {"n_controls": "20"},
    "English": {"n_controls": "60"},
    "Hindi/Hinglish": {"n_controls": "20"},
    "Spanish": {"n_controls": "20"},
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing scorer positive-control table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_fields(row: dict[str, str], expected: dict[str, str], *, label: str) -> None:
    for field, value in expected.items():
        require(row[field] == value, f"{label}/{field}: expected {value}, got {row[field]}")


def check_keyed(path: Path, key: str, expected: dict[str, dict[str, str]]) -> None:
    rows = {row[key]: row for row in read_csv(path)}
    require(set(rows) == set(expected), f"{path} unexpected keys: {sorted(rows)}")
    for label, fields in expected.items():
        check_fields(rows[label], fields, label=label)
        require(rows[label]["auto_pass_pct"] == "100.0", f"{label} did not pass all controls")
        require(rows[label]["all_components_pass_pct"] == "100.0", f"{label} did not pass all components")
        require(rows[label]["auto_failed_n"] == "0", f"{label} has unexpected auto failures")


def check_rows(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == 120, f"expected 120 positive-control rows, found {len(rows)}")
    require(len({row["item_id"] for row in rows}) == 120, "duplicate positive-control item IDs")
    require(sum(row["auto_pass"] == "1" for row in rows) == 120, "not all positive controls pass")
    require(sum(row["all_components_pass"] == "1" for row in rows) == 120, "not all components pass")
    require(sum(row["auto_failed"] == "1" for row in rows) == 0, "positive controls contain auto failures")
    require(not any(row["failure_types"].strip() for row in rows), "positive controls contain failure types")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing scorer positive-control report {path}")
    text = " ".join(path.read_text(encoding="utf-8").split())
    for phrase in (
        "Scorer Positive-Control Audit v0.2",
        "120 | 120 (100.0%) | 120 (100.0%) | 0",
        "test scorer over-rejection",
        "accepts 120/120 constrained positive controls",
        "known failures are rejected, and constrained known passes are not over-rejected",
        "do not replace LLM-judge checks or completed human/native review",
    ):
        require(phrase in text, f"scorer positive-control report missing phrase: {phrase}")


def check_main_tex(path: Path) -> None:
    require(path.exists(), f"missing paper TeX {path}")
    text = " ".join(path.read_text(encoding="utf-8").split())
    for phrase in (
        "a positive-control audit accepts all 120 constrained pass templates",
        "testing scorer over-rejection",
        "rather than semantic or native-speaker validity",
    ):
        require(phrase in text, f"main TeX missing scorer positive-control phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/scorer_positive_control_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/scorer_positive_control_v02.md"))
    parser.add_argument("--main-tex", type=Path, default=Path("paper/sections/05_results.tex"))
    args = parser.parse_args()

    overall_rows = read_csv(args.out_dir / "scorer_positive_control_overall.csv")
    require(len(overall_rows) == 1, "expected one overall row")
    check_fields(overall_rows[0], EXPECTED_OVERALL, label="overall")
    check_keyed(args.out_dir / "scorer_positive_control_by_family.csv", "task_family", EXPECTED_BY_FAMILY)
    check_keyed(args.out_dir / "scorer_positive_control_by_language.csv", "language_pair", EXPECTED_BY_LANGUAGE)
    check_keyed(
        args.out_dir / "scorer_positive_control_by_expected_language.csv",
        "expected_response_language",
        EXPECTED_BY_EXPECTED_LANGUAGE,
    )
    check_rows(args.out_dir / "scorer_positive_control_rows.csv")
    check_report(args.report)
    check_main_tex(args.main_tex)
    print("scorer positive-control validation passed")


if __name__ == "__main__":
    main()
