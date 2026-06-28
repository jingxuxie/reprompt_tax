#!/usr/bin/env python
"""Build the full 120-item v0.2 three-model score file from saved shards."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_INPUTS = [
    Path("results/scores/openai_three_model_stress60_auto_scores.jsonl"),
    Path("results/scores/openai_three_model_stress_v02_new24_auto_scores.jsonl"),
    Path("results/scores/openai_nano_stress_v02_remaining36_auto_scores.jsonl"),
    Path("results/scores/openai_mini_gpt41_stress_v02_remaining36_auto_scores.jsonl"),
]

MODELS = ("gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano")
CONDITIONS = ("baseline", "contract")


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
    parser.add_argument("--out", type=Path, default=Path("results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl"))
    parser.add_argument("--input", type=Path, action="append", default=[])
    args = parser.parse_args()

    input_paths = args.input or DEFAULT_INPUTS
    benchmark_ids = {row["id"] for row in load_jsonl(args.benchmark)}
    rows: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    for path in input_paths:
        for row in load_jsonl(path):
            if row["item_id"] not in benchmark_ids:
                raise AssertionError(f"{path} contains item outside v0.2 benchmark: {row['item_id']}")
            key = row_key(row)
            if key in rows and rows[key] != row:
                raise AssertionError(f"conflicting duplicate score row for {key}")
            rows[key] = row

    first_turn_counts = Counter((row["model"], row["condition"]) for row in rows.values() if int(row["turn"]) == 0)
    expected_first_turn_counts = {(model, condition): 120 for model in MODELS for condition in CONDITIONS}
    if dict(first_turn_counts) != expected_first_turn_counts:
        raise AssertionError(f"unexpected first-turn coverage: {first_turn_counts}")

    trajectories = Counter(trajectory_key(row) for row in rows.values())
    missing = []
    for item_id in sorted(benchmark_ids):
        for model in MODELS:
            for condition in CONDITIONS:
                if (item_id, model, condition) not in trajectories:
                    missing.append((item_id, model, condition))
    if missing:
        raise AssertionError(f"missing trajectories: {missing[:10]}")

    ordered = sorted(rows.values(), key=lambda row: (row["model"], row["condition"], row["item_id"], int(row["turn"])))
    write_jsonl(args.out, ordered)
    print(f"wrote {len(ordered)} scored response rows to {args.out}")


if __name__ == "__main__":
    main()
