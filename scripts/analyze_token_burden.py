#!/usr/bin/env python
"""Summarize absolute token burden for RePromptTax trajectories."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
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
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def trajectory_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (row["item_id"], row["model"], row["condition"])


def trajectory_row(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: int(row["turn"]))
    first = ordered[0]
    rtt = 3
    for row in ordered:
        if bool(row["pass"]):
            rtt = int(row["turn"])
            break
    used = [row for row in ordered if int(row["turn"]) <= rtt] if rtt < 3 else ordered
    first_tokens = int(first["input_tokens"]) + int(first["output_tokens"])
    total_input_tokens = sum(int(row["input_tokens"]) for row in used)
    total_output_tokens = sum(int(row["output_tokens"]) for row in used)
    total_tokens = total_input_tokens + total_output_tokens
    return {
        "item_id": first["item_id"],
        "model": first["model"],
        "condition": first["condition"],
        "language_pair": first["language_pair"],
        "task_family": first["task_family"],
        "rtt": rtt,
        "resolved": int(rtt < 3),
        "initially_failed": int(not bool(first["pass"])),
        "first_turn_tokens": first_tokens,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens_until_stop": total_tokens,
        "extra_tokens_after_first": total_tokens - first_tokens,
        "token_tax": total_tokens / max(first_tokens, 1),
    }


def summarize(rows: list[dict[str, Any]], group_keys: list[str]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(str(row[key]) for key in group_keys)].append(row)

    out: list[dict[str, Any]] = []
    for key, values in sorted(grouped.items()):
        base = {name: value for name, value in zip(group_keys, key)}
        base.update(
            {
                "n": len(values),
                "mean_first_turn_tokens": mean(row["first_turn_tokens"] for row in values),
                "mean_total_tokens_until_stop": mean(row["total_tokens_until_stop"] for row in values),
                "mean_extra_tokens_after_first": mean(row["extra_tokens_after_first"] for row in values),
                "mean_total_input_tokens": mean(row["total_input_tokens"] for row in values),
                "mean_total_output_tokens": mean(row["total_output_tokens"] for row in values),
                "mean_token_tax": mean(row["token_tax"] for row in values),
                "total_tokens_until_stop": sum(row["total_tokens_until_stop"] for row in values),
                "total_extra_tokens_after_first": sum(row["extra_tokens_after_first"] for row in values),
            }
        )
        out.append(base)
    return out


def paired_effects(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {(row["item_id"], row["model"], row["condition"]): row for row in rows}
    models = sorted({row["model"] for row in rows})
    out = []
    for model in models:
        item_ids = sorted({row["item_id"] for row in rows if row["model"] == model})
        deltas = []
        total_token_reductions = []
        extra_token_reductions = []
        for item_id in item_ids:
            baseline = by_key[(item_id, model, "baseline")]
            contract = by_key[(item_id, model, "contract")]
            total_token_reductions.append(baseline["total_tokens_until_stop"] - contract["total_tokens_until_stop"])
            extra_token_reductions.append(baseline["extra_tokens_after_first"] - contract["extra_tokens_after_first"])
            deltas.append(baseline["token_tax"] - contract["token_tax"])
        out.append(
            {
                "model": model,
                "n_pairs": len(item_ids),
                "mean_total_tokens_baseline_minus_contract": mean(total_token_reductions),
                "mean_extra_tokens_baseline_minus_contract": mean(extra_token_reductions),
                "mean_token_tax_baseline_minus_contract": mean(deltas),
                "sum_total_tokens_baseline_minus_contract": sum(total_token_reductions),
                "sum_extra_tokens_baseline_minus_contract": sum(extra_token_reductions),
            }
        )
    return out


def fmt(value: float) -> str:
    return f"{value:.1f}"


def write_markdown(path: Path, summary_rows: list[dict[str, Any]], effect_rows: list[dict[str, Any]], scores_path: Path) -> None:
    lines = [
        "# Token-Burden Analysis",
        "",
        f"Generated from `{scores_path}`.",
        "",
        "This supplement reports absolute token burden in addition to the token-tax",
        "ratio used in the main paper. Tokens are the API usage counts saved with",
        "each response. For unresolved trajectories, totals include all three turns.",
        "",
        "## By Model And Condition",
        "",
        "| Model | Condition | Mean first-turn tokens | Mean total tokens | Mean extra tokens | Mean token tax | Total tokens |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            "| "
            f"{row['model']} | "
            f"{row['condition']} | "
            f"{fmt(float(row['mean_first_turn_tokens']))} | "
            f"{fmt(float(row['mean_total_tokens_until_stop']))} | "
            f"{fmt(float(row['mean_extra_tokens_after_first']))} | "
            f"{float(row['mean_token_tax']):.2f}x | "
            f"{int(row['total_tokens_until_stop'])} |"
        )

    lines.extend(
        [
            "",
            "## Paired Baseline Minus Contract Effects",
            "",
            "| Model | Mean total tokens | Mean extra tokens | Mean token tax | Sum total tokens |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in effect_rows:
        lines.append(
            "| "
            f"{row['model']} | "
            f"{fmt(float(row['mean_total_tokens_baseline_minus_contract']))} | "
            f"{fmt(float(row['mean_extra_tokens_baseline_minus_contract']))} | "
            f"{float(row['mean_token_tax_baseline_minus_contract']):.2f}x | "
            f"{int(row['sum_total_tokens_baseline_minus_contract'])} |"
        )
    lines.extend(
        [
            "",
            "Positive values mean the contract uses fewer tokens than baseline; negative",
            "values mean the longer contract prompt increases absolute token use. The",
            "contract lowers token-tax ratios for all three models, but absolute total",
            "tokens increase because the system prompt is longer. This is why the main",
            "paper treats token tax as a repair-burden metric rather than as an API-cost",
            "claim.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", type=Path, default=Path("results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/openai_three_model_stress_v02_full120"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/token_burden_analysis_v02_full120.md"))
    args = parser.parse_args()

    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in load_jsonl(args.scores):
        grouped[trajectory_key(row)].append(row)
    trajectories = [trajectory_row(rows) for rows in grouped.values()]
    summary_rows = summarize(trajectories, ["model", "condition"])
    language_rows = summarize(trajectories, ["model", "condition", "language_pair"])
    family_rows = summarize(trajectories, ["model", "condition", "task_family"])
    effect_rows = paired_effects(trajectories)

    write_csv(args.out_dir / "token_burden_trajectory_metrics.csv", trajectories)
    write_csv(args.out_dir / "token_burden_by_model.csv", summary_rows)
    write_csv(args.out_dir / "token_burden_by_language.csv", language_rows)
    write_csv(args.out_dir / "token_burden_by_family.csv", family_rows)
    write_csv(args.out_dir / "token_burden_paired_effects_by_model.csv", effect_rows)
    write_markdown(args.out_md, summary_rows, effect_rows, args.scores)
    print(f"wrote token-burden analysis to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
