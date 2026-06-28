#!/usr/bin/env python
"""Paired sign-test sensitivity checks for RePromptTax mitigation effects."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


METRICS = [
    ("ftga", "contract_minus_baseline", "FTGA"),
    ("rtt", "baseline_minus_contract", "RTT reduction"),
    ("token_tax", "baseline_minus_contract", "Token-tax reduction"),
    ("unresolved", "baseline_minus_contract", "Unresolved reduction"),
]


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


def paired_items(rows: list[dict[str, str]]) -> dict[str, list[tuple[dict[str, str], dict[str, str]]]]:
    grouped: dict[str, dict[str, dict[str, dict[str, str]]]] = defaultdict(lambda: defaultdict(dict))
    for row in rows:
        grouped[row["model"]][row["item_id"]][row["condition"]] = row

    out: dict[str, list[tuple[dict[str, str], dict[str, str]]]] = {}
    for model, by_item in grouped.items():
        pairs = []
        for item_id, conditions in sorted(by_item.items()):
            if set(conditions) != {"baseline", "contract"}:
                raise ValueError(f"{model} {item_id} does not have exactly baseline and contract rows")
            pairs.append((conditions["baseline"], conditions["contract"]))
        out[model] = pairs
    return out


def sign_test_p(pos: int, neg: int) -> float:
    n = pos + neg
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(min(pos, neg) + 1)) / (2**n)
    return min(1.0, 2.0 * tail)


def paired_deltas(
    pairs: list[tuple[dict[str, str], dict[str, str]]],
    *,
    metric: str,
    direction: str,
) -> list[float]:
    deltas = []
    for baseline, contract in pairs:
        if direction == "contract_minus_baseline":
            deltas.append(float(contract[metric]) - float(baseline[metric]))
        elif direction == "baseline_minus_contract":
            deltas.append(float(baseline[metric]) - float(contract[metric]))
        else:
            raise ValueError(f"unknown direction: {direction}")
    return deltas


def summarize(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for model, pairs in sorted(paired_items(rows).items()):
        for metric, direction, label in METRICS:
            deltas = paired_deltas(pairs, metric=metric, direction=direction)
            pos = sum(delta > 1e-12 for delta in deltas)
            neg = sum(delta < -1e-12 for delta in deltas)
            zero = len(deltas) - pos - neg
            out.append(
                {
                    "model": model,
                    "metric": metric,
                    "label": label,
                    "direction": direction,
                    "n_pairs": len(deltas),
                    "positive_n": pos,
                    "negative_n": neg,
                    "tie_n": zero,
                    "mean_delta": sum(deltas) / len(deltas),
                    "two_sided_sign_p": sign_test_p(pos, neg),
                }
            )
    return out


def write_markdown(path: Path, rows: list[dict[str, Any]], trajectory_metrics: Path) -> None:
    lines = [
        "# RePromptTax Paired Sign-Test Sensitivity",
        "",
        f"Generated from `{trajectory_metrics}`.",
        "",
        "Positive counts mean the contract improved the paired item in the stated",
        "direction. Ties are excluded from the exact two-sided sign test.",
        "",
        "| Model | Metric | Direction | + | - | Ties | Mean delta | Sign-test p |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row['model']} | "
            f"{row['label']} | "
            f"{row['direction']} | "
            f"{row['positive_n']} | "
            f"{row['negative_n']} | "
            f"{row['tie_n']} | "
            f"{row['mean_delta']:.3f} | "
            f"{row['two_sided_sign_p']:.4f} |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trajectory-metrics", type=Path, default=Path("results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv"))
    parser.add_argument("--out-csv", type=Path, default=Path("results/tables/openai_three_model_stress_v02_full120/paired_significance_by_model.csv"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/paired_significance_v02_full120.md"))
    args = parser.parse_args()

    rows = summarize(read_csv(args.trajectory_metrics))
    write_csv(args.out_csv, rows)
    write_markdown(args.out_md, rows, args.trajectory_metrics)
    print(f"wrote paired sign-test sensitivity to {args.out_csv} and {args.out_md}")


if __name__ == "__main__":
    main()
