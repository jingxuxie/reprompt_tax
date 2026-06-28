#!/usr/bin/env python
"""Compute paired baseline-vs-contract effect sizes from trajectory metrics."""

from __future__ import annotations

import argparse
import csv
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def quantile(values: list[float], q: float) -> float:
    values = sorted(values)
    idx = min(len(values) - 1, max(0, round(q * (len(values) - 1))))
    return values[idx]


def row_key(row: dict[str, str], group_fields: list[str]) -> tuple[str, ...]:
    return tuple(row[field] for field in group_fields)


def paired_items(rows: list[dict[str, str]], group_fields: list[str]) -> dict[tuple[str, ...], list[tuple[dict[str, str], dict[str, str]]]]:
    grouped: dict[tuple[str, ...], dict[str, dict[str, dict[str, str]]]] = defaultdict(lambda: defaultdict(dict))
    for row in rows:
        key = row_key(row, group_fields)
        grouped[key][row["item_id"]][row["condition"]] = row

    out: dict[tuple[str, ...], list[tuple[dict[str, str], dict[str, str]]]] = {}
    for key, by_item in grouped.items():
        pairs: list[tuple[dict[str, str], dict[str, str]]] = []
        for item_id, conditions in sorted(by_item.items()):
            if set(conditions) != {"baseline", "contract"}:
                raise ValueError(f"{key} {item_id} does not have exactly baseline and contract rows")
            pairs.append((conditions["baseline"], conditions["contract"]))
        out[key] = pairs
    return out


def effects_for_pairs(pairs: list[tuple[dict[str, str], dict[str, str]]]) -> dict[str, float]:
    return {
        "delta_ftga_pp": 100.0 * mean(float(contract["ftga"]) - float(baseline["ftga"]) for baseline, contract in pairs),
        "rtt_reduction": mean(float(baseline["rtt"]) - float(contract["rtt"]) for baseline, contract in pairs),
        "token_tax_reduction": mean(float(baseline["token_tax"]) - float(contract["token_tax"]) for baseline, contract in pairs),
        "unresolved_reduction_pp": 100.0 * mean(float(baseline["unresolved"]) - float(contract["unresolved"]) for baseline, contract in pairs),
    }


def bootstrap_effects(
    pairs: list[tuple[dict[str, str], dict[str, str]]],
    *,
    samples: int,
    seed: int,
) -> dict[str, tuple[float, float]]:
    rng = random.Random(seed)
    draws: dict[str, list[float]] = defaultdict(list)
    n = len(pairs)
    for _ in range(samples):
        sample = [pairs[rng.randrange(n)] for _ in range(n)]
        effects = effects_for_pairs(sample)
        for key, value in effects.items():
            draws[key].append(value)
    return {key: (quantile(values, 0.025), quantile(values, 0.975)) for key, values in draws.items()}


def summarize(rows: list[dict[str, str]], group_fields: list[str], samples: int, seed: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for key, pairs in sorted(paired_items(rows, group_fields).items()):
        effects = effects_for_pairs(pairs)
        intervals = bootstrap_effects(pairs, samples=samples, seed=seed)
        row: dict[str, Any] = {field: value for field, value in zip(group_fields, key)}
        row["n_pairs"] = len(pairs)
        for effect_name, value in effects.items():
            low, high = intervals[effect_name]
            row[effect_name] = value
            row[f"{effect_name}_ci_low"] = low
            row[f"{effect_name}_ci_high"] = high
        out.append(row)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trajectory-metrics", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()

    rows = read_csv(args.trajectory_metrics)
    write_csv(
        args.out_dir / "paired_contract_effects_by_model.csv",
        summarize(rows, ["model"], args.bootstrap_samples, args.seed),
    )
    write_csv(
        args.out_dir / "paired_contract_effects_by_family.csv",
        summarize(rows, ["model", "task_family"], args.bootstrap_samples, args.seed),
    )
    print(f"wrote paired effects to {args.out_dir}")


if __name__ == "__main__":
    main()
