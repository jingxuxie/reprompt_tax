#!/usr/bin/env python
"""Merge saved v0.3 smoke rows with remaining pilot rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CONDITIONS = ("baseline", "contract")


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


def load_ids(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", type=Path, default=Path("results/model_outputs/openai_gpt54mini_stress_v03_smoke6.jsonl"))
    parser.add_argument("--remaining", type=Path, default=Path("results/model_outputs/openai_gpt54mini_stress_v03_pilot24_remaining18.jsonl"))
    parser.add_argument("--pilot-ids", type=Path, default=Path("data/stress_v03_pilot24_ids.txt"))
    parser.add_argument("--out", type=Path, default=Path("results/model_outputs/openai_gpt54mini_stress_v03_pilot24.jsonl"))
    args = parser.parse_args()

    pilot_ids = load_ids(args.pilot_ids)
    require(len(pilot_ids) == 24, f"expected 24 pilot IDs, found {len(pilot_ids)}")
    require(len(pilot_ids) == len(set(pilot_ids)), "duplicate pilot IDs")
    pilot_order = {item_id: idx for idx, item_id in enumerate(pilot_ids)}
    rows = load_jsonl(args.smoke) + load_jsonl(args.remaining)
    rows = [row for row in rows if row["item_id"] in pilot_order]

    key_turns = {(row["item_id"], row["model"], row["condition"], int(row["turn"])) for row in rows}
    require(len(key_turns) == len(rows), "duplicate item/model/condition/turn rows after merge")
    require({row["model"] for row in rows} == {"gpt-5.4-mini"}, "unexpected model in pilot rows")
    require({row["condition"] for row in rows} == set(CONDITIONS), "unexpected conditions in pilot rows")

    trajectory_keys = {(row["item_id"], row["model"], row["condition"]) for row in rows}
    expected_trajectory_keys = {(item_id, "gpt-5.4-mini", condition) for item_id in pilot_ids for condition in CONDITIONS}
    require(trajectory_keys == expected_trajectory_keys, "merged rows do not cover every pilot item/condition")
    first_turns = {(row["item_id"], row["condition"]) for row in rows if int(row["turn"]) == 0}
    require(first_turns == {(item_id, condition) for item_id in pilot_ids for condition in CONDITIONS}, "missing first-turn rows")

    rows.sort(key=lambda row: (pilot_order[row["item_id"]], CONDITIONS.index(row["condition"]), int(row["turn"])))
    write_jsonl(args.out, rows)
    print(f"wrote {len(rows)} merged v0.3 pilot rows to {args.out}")


if __name__ == "__main__":
    main()
