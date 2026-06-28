#!/usr/bin/env python
"""Build the full 120-item v0.2 generic-helpfulness control score file."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_INPUTS = [
    Path("results/scores/openai_nano_stress60_generic_helpfulness_auto_scores.jsonl"),
    Path("results/scores/openai_nano_stress_v02_new60_generic_helpfulness_auto_scores.jsonl"),
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def row_key(row: dict[str, Any]) -> tuple[str, str, str, int]:
    return (row["item_id"], row["model"], row["condition"], int(row["turn"]))


def trajectory_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (row["item_id"], row["model"], row["condition"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, default=Path("data/benchmark_stress_v0.2.jsonl"))
    parser.add_argument("--out", type=Path, default=Path("results/scores/openai_nano_stress_v02_full120_generic_helpfulness_auto_scores.jsonl"))
    parser.add_argument("--input", type=Path, action="append", default=[])
    args = parser.parse_args()

    input_paths = args.input or DEFAULT_INPUTS
    benchmark_ids = {row["id"] for row in load_jsonl(args.benchmark)}
    rows: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    for path in input_paths:
        for row in load_jsonl(path):
            if row["item_id"] not in benchmark_ids:
                raise AssertionError(f"{path} contains item outside v0.2 benchmark: {row['item_id']}")
            if row["model"] != "gpt-4.1-nano":
                raise AssertionError(f"{path} contains non-nano row: {row['model']}")
            if row["condition"] != "generic_helpfulness":
                raise AssertionError(f"{path} contains non-control row: {row['condition']}")
            key = row_key(row)
            if key in rows and rows[key] != row:
                raise AssertionError(f"conflicting duplicate score row for {key}")
            rows[key] = row

    first_turn_count = Counter(row["condition"] for row in rows.values() if int(row["turn"]) == 0)
    if dict(first_turn_count) != {"generic_helpfulness": 120}:
        raise AssertionError(f"unexpected first-turn coverage: {first_turn_count}")

    trajectories = Counter(trajectory_key(row) for row in rows.values())
    missing = [
        item_id
        for item_id in sorted(benchmark_ids)
        if (item_id, "gpt-4.1-nano", "generic_helpfulness") not in trajectories
    ]
    if missing:
        raise AssertionError(f"missing generic-helpfulness trajectories: {missing[:10]}")

    ordered = sorted(rows.values(), key=lambda row: (row["item_id"], int(row["turn"])))
    write_jsonl(args.out, ordered)
    print(f"wrote {len(ordered)} scored response rows to {args.out}")


if __name__ == "__main__":
    main()
