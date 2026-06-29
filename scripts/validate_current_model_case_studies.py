#!/usr/bin/env python
"""Validate current-model qualitative case-study artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED = {
    "gpt55_baseline_fixed_by_contract": {
        "model": "gpt-5.5",
        "condition": "baseline",
        "item_id": "es_en_SA_001",
        "rtt": "1",
        "unresolved": "0",
        "first_failure_types": "wrong_output_language,task_noncompletion",
        "final_pass": "True",
        "contrast_condition": "contract",
        "contrast_first_pass": "True",
        "snippet": "Claro. Una version",
    },
    "gpt55_contract_residual_repairs": {
        "model": "gpt-5.5",
        "condition": "contract",
        "item_id": "es_en_SA_004",
        "rtt": "1",
        "unresolved": "0",
        "first_failure_types": "wrong_output_language",
        "final_pass": "True",
        "contrast_condition": "",
        "contrast_first_pass": "",
        "snippet": "Tambien suena natural",
    },
    "gpt54mini_contract_quote_unresolved": {
        "model": "gpt-5.4-mini",
        "condition": "contract",
        "item_id": "hi_en_SC_003",
        "rtt": "3",
        "unresolved": "1",
        "first_failure_types": "wrong_output_language",
        "final_pass": "False",
        "contrast_condition": "",
        "contrast_first_pass": "",
        "snippet": "The document lists",
    },
    "gpt54mini_contract_literal_unresolved": {
        "model": "gpt-5.4-mini",
        "condition": "contract",
        "item_id": "ar_en_SD_008",
        "rtt": "3",
        "unresolved": "1",
        "first_failure_types": "preservation_failure",
        "final_pass": "False",
        "contrast_condition": "",
        "contrast_first_pass": "",
        "snippet": "QR-77",
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing case-study CSV {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def normalize_ascii(text: str) -> str:
    replacements = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "Á": "A",
        "É": "E",
        "Í": "I",
        "Ó": "O",
        "Ú": "U",
        "ñ": "n",
        "Ñ": "N",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def check_csv(path: Path) -> None:
    rows = {row["case_id"]: row for row in load_csv(path)}
    require(set(rows) == set(EXPECTED), f"unexpected case IDs: {sorted(rows)}")
    for case_id, expected in EXPECTED.items():
        row = rows[case_id]
        for field, value in expected.items():
            if field == "snippet":
                continue
            require(row[field] == value, f"{case_id} mismatch for {field}: expected {value}, got {row[field]}")
        combined = normalize_ascii(" ".join([row["first_response_excerpt"], row["final_response_excerpt"], row["contrast_first_response_excerpt"]]))
        require(expected["snippet"] in combined, f"{case_id} missing expected response snippet {expected['snippet']!r}")
        require(row["user_prompt_excerpt"], f"{case_id} missing user prompt excerpt")
        require(row["interpretation"], f"{case_id} missing interpretation")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing case-study report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "Current-Model Case Studies",
        "results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl",
        "results/scores/openai_gpt54mini_stress_v02_full120_auto_scores.jsonl",
        "gpt55_baseline_fixed_by_contract",
        "gpt55_contract_residual_repairs",
        "gpt54mini_contract_quote_unresolved",
        "gpt54mini_contract_literal_unresolved",
        "Matched `contract` first response excerpt",
        "do not replace native/near-native human validation",
    ]
    for phrase in required:
        require(phrase in normalized, f"case-study report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=Path("results/tables/current_model_case_studies_v02/current_model_case_studies.csv"))
    parser.add_argument("--report", type=Path, default=Path("paper/current_model_case_studies_v02.md"))
    args = parser.parse_args()

    check_csv(args.csv)
    check_report(args.report)
    print("current-model case-study validation passed")


if __name__ == "__main__":
    main()
