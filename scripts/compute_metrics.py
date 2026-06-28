#!/usr/bin/env python
"""Compute RePromptTax aggregate metrics from scored response logs."""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    idx = min(len(values) - 1, max(0, round(q * (len(values) - 1))))
    return values[idx]


def trajectory_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: row["turn"])
    pass_by_turn = {row["turn"]: bool(row["pass"]) for row in ordered}
    rtt = 3
    for turn in range(3):
        if pass_by_turn.get(turn, False):
            rtt = turn
            break

    first_tokens = ordered[0]["input_tokens"] + ordered[0]["output_tokens"]
    if rtt < 3:
        used_rows = [row for row in ordered if row["turn"] <= rtt]
    else:
        used_rows = ordered
    total_tokens = sum(row["input_tokens"] + row["output_tokens"] for row in used_rows)
    token_tax = total_tokens / max(first_tokens, 1)

    first_failure_types = []
    for row in ordered:
        if row["turn"] == 0:
            first_failure_types = row.get("failure_types", [])
            break

    first = ordered[0]
    return {
        "item_id": first["item_id"],
        "model": first["model"],
        "condition": first["condition"],
        "language_pair": first["language_pair"],
        "task_family": first["task_family"],
        "ftga": 1 if pass_by_turn.get(0, False) else 0,
        "rtt": rtt,
        "resolved": 1 if rtt < 3 else 0,
        "unresolved": 1 if rtt == 3 else 0,
        "initially_failed": 0 if pass_by_turn.get(0, False) else 1,
        "repair_success_1": 1 if (not pass_by_turn.get(0, False) and pass_by_turn.get(1, False)) else 0,
        "repair_success_2": 1 if (not pass_by_turn.get(0, False) and rtt in (1, 2)) else 0,
        "token_tax": token_tax,
        "first_failure_types": first_failure_types,
    }


def summarize(groups: dict[tuple[Any, ...], list[dict[str, Any]]], key_names: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, values in sorted(groups.items()):
        n = len(values)
        initially_failed = sum(row["initially_failed"] for row in values)
        repair_1_num = sum(row["repair_success_1"] for row in values)
        repair_2_num = sum(row["repair_success_2"] for row in values)
        row = {name: value for name, value in zip(key_names, key)}
        row.update(
            {
                "n": n,
                "ftga": mean(row["ftga"] for row in values),
                "mean_rtt": mean(row["rtt"] for row in values),
                "unresolved_rate": mean(row["unresolved"] for row in values),
                "repair_success_at_1": repair_1_num / initially_failed if initially_failed else "",
                "repair_success_at_2": repair_2_num / initially_failed if initially_failed else "",
                "mean_token_tax": mean(row["token_tax"] for row in values),
                "initially_failed_n": initially_failed,
            }
        )
        ci = bootstrap_ci(values)
        row.update(ci)
        rows.append(row)
    return rows


def bootstrap_ci(values: list[dict[str, Any]], samples: int = 1000, seed: int = 7) -> dict[str, float]:
    if not values:
        return {}
    rng = random.Random(seed)
    ftga_vals: list[float] = []
    rtt_vals: list[float] = []
    n = len(values)
    for _ in range(samples):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        ftga_vals.append(mean(row["ftga"] for row in sample))
        rtt_vals.append(mean(row["rtt"] for row in sample))
    return {
        "ftga_ci_low": quantile(ftga_vals, 0.025),
        "ftga_ci_high": quantile(ftga_vals, 0.975),
        "mean_rtt_ci_low": quantile(rtt_vals, 0.025),
        "mean_rtt_ci_high": quantile(rtt_vals, 0.975),
    }


def failure_type_rows(trajectories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[tuple[str, str, str, str], int] = defaultdict(int)
    denominators: dict[tuple[str, str, str], int] = defaultdict(int)
    for row in trajectories:
        if not row["initially_failed"]:
            continue
        base = (row["model"], row["condition"], row["task_family"])
        denominators[base] += 1
        failure_types = row["first_failure_types"] or ["unknown"]
        for failure_type in failure_types:
            counts[(*base, failure_type)] += 1

    out: list[dict[str, Any]] = []
    for (model, condition, family, failure_type), count in sorted(counts.items()):
        denom = denominators[(model, condition, family)]
        out.append(
            {
                "model": model,
                "condition": condition,
                "task_family": family,
                "failure_type": failure_type,
                "count": count,
                "share_of_initial_failures": count / denom if denom else 0,
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    score_rows = load_jsonl(args.scores)
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in score_rows:
        key = (row["item_id"], row["model"], row["condition"])
        grouped[key].append(row)

    trajectories = [trajectory_metrics(rows) for rows in grouped.values()]
    args.out_dir.mkdir(parents=True, exist_ok=True)

    write_csv(args.out_dir / "trajectory_metrics.csv", trajectories)

    by_model: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    by_family: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    by_language: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in trajectories:
        by_model[(row["model"], row["condition"])].append(row)
        by_family[(row["model"], row["condition"], row["task_family"])].append(row)
        by_language[(row["model"], row["condition"], row["language_pair"])].append(row)

    write_csv(args.out_dir / "metrics_summary.csv", summarize(by_model, ["model", "condition"]))
    write_csv(args.out_dir / "metrics_by_family.csv", summarize(by_family, ["model", "condition", "task_family"]))
    write_csv(args.out_dir / "metrics_by_language.csv", summarize(by_language, ["model", "condition", "language_pair"]))
    write_csv(args.out_dir / "failure_types_by_family.csv", failure_type_rows(trajectories))

    print(f"wrote metrics for {len(trajectories)} trajectories to {args.out_dir}")


if __name__ == "__main__":
    main()
