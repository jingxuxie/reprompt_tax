#!/usr/bin/env python
"""Validate scorer challenge audit artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_OVERALL = {
    "n_challenges": "390",
    "auto_failed_n": "390",
    "auto_failed_pct": "100.0",
    "expected_signal_detected_n": "390",
    "expected_signal_detected_pct": "100.0",
    "auto_pass_n": "0",
}

EXPECTED_BY_TYPE = {
    "forbidden_marker": {"n_challenges": "60", "auto_failed_n": "60", "expected_signal_detected_n": "60"},
    "required_marker_omission": {"n_challenges": "120", "auto_failed_n": "120", "expected_signal_detected_n": "120"},
    "wrong_script": {"n_challenges": "120", "auto_failed_n": "120", "expected_signal_detected_n": "120"},
    "preservation_drop": {"n_challenges": "60", "auto_failed_n": "60", "expected_signal_detected_n": "60"},
    "overformal_register": {"n_challenges": "30", "auto_failed_n": "30", "expected_signal_detected_n": "30"},
}

EXPECTED_BY_FAMILY = {
    "editing_preservation": {"n_challenges": "90"},
    "output_language_inference": {"n_challenges": "60"},
    "quote_preservation": {"n_challenges": "90"},
    "script_register_locale": {"n_challenges": "150"},
}

EXPECTED_BY_LANGUAGE = {
    "ar-en": {"n_challenges": "130"},
    "es-en": {"n_challenges": "130"},
    "hi-en": {"n_challenges": "130"},
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing scorer challenge table {path}")
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
        require(rows[label]["auto_failed_pct"] == "100.0", f"{label} did not fail all challenges")
        require(rows[label]["expected_signal_detected_pct"] == "100.0", f"{label} did not detect all expected signals")
        require(rows[label]["auto_pass_n"] == "0", f"{label} has unexpected auto passes")


def check_rows(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == 390, f"expected 390 challenge rows, found {len(rows)}")
    require(sum(row["auto_pass"] == "1" for row in rows) == 0, "challenge rows contain auto passes")
    require(sum(row["expected_signal_detected"] == "1" for row in rows) == 390, "not all expected signals detected")
    require(len({(row["item_id"], row["challenge_type"]) for row in rows}) == 390, "duplicate item/challenge rows")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing scorer challenge report {path}")
    text = " ".join(path.read_text(encoding="utf-8").split())
    for phrase in (
        "Scorer Challenge Audit v0.2",
        "390 | 390 (100.0%) | 390 (100.0%) | 0",
        "forbidden markers, omitted required markers, wrong script/language",
        "stress test, not native/near-native validation",
        "human/native review gates remain necessary",
    ):
        require(phrase in text, f"scorer challenge report missing phrase: {phrase}")


def check_main_tex(path: Path) -> None:
    require(path.exists(), f"missing paper TeX {path}")
    text = " ".join(path.read_text(encoding="utf-8").split())
    for phrase in (
        "synthetic scorer-challenge audit over 390 known-bad",
        "fails all probes and detects every expected failure signal",
        "rather than human/native validation",
    ):
        require(phrase in text, f"main TeX missing scorer challenge phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/scorer_challenge_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/scorer_challenge_v02.md"))
    parser.add_argument("--main-tex", type=Path, default=Path("paper/sections/05_results.tex"))
    args = parser.parse_args()

    overall_rows = read_csv(args.out_dir / "scorer_challenge_overall.csv")
    require(len(overall_rows) == 1, "expected one overall row")
    check_fields(overall_rows[0], EXPECTED_OVERALL, label="overall")
    check_keyed(args.out_dir / "scorer_challenge_by_type.csv", "challenge_type", EXPECTED_BY_TYPE)
    check_keyed(args.out_dir / "scorer_challenge_by_family.csv", "task_family", EXPECTED_BY_FAMILY)
    check_keyed(args.out_dir / "scorer_challenge_by_language.csv", "language_pair", EXPECTED_BY_LANGUAGE)
    check_rows(args.out_dir / "scorer_challenge_rows.csv")
    check_report(args.report)
    check_main_tex(args.main_tex)
    print("scorer-challenge validation passed")


if __name__ == "__main__":
    main()
