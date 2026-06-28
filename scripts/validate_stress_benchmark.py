#!/usr/bin/env python
"""Validate RePromptTax stress benchmark structure and balance."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


LANGUAGE_PAIRS = ("es-en", "hi-en", "ar-en")
TASK_FAMILIES = (
    "editing_preservation",
    "output_language_inference",
    "quote_preservation",
    "script_register_locale",
)
REQUIRED_FIELDS = (
    "id",
    "language_pair",
    "task_family",
    "user_prompt",
    "expected_response_language",
    "expected_script",
    "repair_prompt_1",
    "repair_prompt_2",
    "required_any_markers",
    "forbidden_markers",
    "stress_tag",
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON") from exc
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate(rows: list[dict[str, Any]], expected_per_cell: int) -> None:
    expected_total = len(LANGUAGE_PAIRS) * len(TASK_FAMILIES) * expected_per_cell
    require(len(rows) == expected_total, f"expected {expected_total} rows, found {len(rows)}")

    ids = [row.get("id") for row in rows]
    require(len(ids) == len(set(ids)), "duplicate ids found")

    counts = Counter((row.get("language_pair"), row.get("task_family")) for row in rows)
    expected_counts = {(pair, family): expected_per_cell for pair in LANGUAGE_PAIRS for family in TASK_FAMILIES}
    require(dict(counts) == expected_counts, f"unexpected language/task cell counts: {counts}")

    for row in rows:
        row_id = row.get("id", "<missing id>")
        for field in REQUIRED_FIELDS:
            require(field in row, f"{row_id} missing field {field}")
        require(row["language_pair"] in LANGUAGE_PAIRS, f"{row_id} has unknown language_pair")
        require(row["task_family"] in TASK_FAMILIES, f"{row_id} has unknown task_family")
        require(isinstance(row["required_any_markers"], list), f"{row_id} required_any_markers must be a list")
        require(isinstance(row["forbidden_markers"], list), f"{row_id} forbidden_markers must be a list")
        if row["task_family"] in {"quote_preservation", "script_register_locale"}:
            require(row.get("must_preserve_spans"), f"{row_id} missing preserved spans")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument("--expected-per-cell", type=int, required=True)
    args = parser.parse_args()
    rows = load_jsonl(args.benchmark)
    validate(rows, args.expected_per_cell)
    print(f"validated {len(rows)} rows in {args.benchmark}")


if __name__ == "__main__":
    main()
