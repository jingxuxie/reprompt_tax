#!/usr/bin/env python
"""Analyze FTGA versus absolute token burden across the full five-model set."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


SCORE_ARTIFACTS = [
    Path("results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl"),
    Path("results/scores/openai_gpt54mini_stress_v02_full120_auto_scores.jsonl"),
    Path("results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl"),
]

MODEL_GENERATION = {
    "gpt-4.1-nano": "GPT-4.1 family",
    "gpt-4.1-mini": "GPT-4.1 family",
    "gpt-4.1": "GPT-4.1 family",
    "gpt-5.4-mini": "GPT-5.x family",
    "gpt-5.5": "GPT-5.x family",
}


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
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
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
        "model_generation": MODEL_GENERATION[first["model"]],
        "model": first["model"],
        "condition": first["condition"],
        "language_pair": first["language_pair"],
        "task_family": first["task_family"],
        "ftga": int(bool(first["pass"])),
        "rtt": rtt,
        "unresolved": int(rtt == 3),
        "first_turn_tokens": first_tokens,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens_until_stop": total_tokens,
        "extra_tokens_after_first": total_tokens - first_tokens,
        "token_tax": total_tokens / max(first_tokens, 1),
    }


def summarize_by_model(trajectories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in trajectories:
        grouped[(row["model"], row["condition"])].append(row)
    out: list[dict[str, Any]] = []
    for (model, condition), rows in sorted(grouped.items()):
        out.append(
            {
                "model_generation": MODEL_GENERATION[model],
                "model": model,
                "condition": condition,
                "n": len(rows),
                "ftga_pct": round(100 * mean(row["ftga"] for row in rows), 1),
                "mean_rtt": round(mean(row["rtt"] for row in rows), 3),
                "unresolved_pct": round(100 * mean(row["unresolved"] for row in rows), 1),
                "mean_first_turn_tokens": round(mean(row["first_turn_tokens"] for row in rows), 3),
                "mean_total_tokens_until_stop": round(mean(row["total_tokens_until_stop"] for row in rows), 3),
                "mean_extra_tokens_after_first": round(mean(row["extra_tokens_after_first"] for row in rows), 3),
                "mean_token_tax": round(mean(row["token_tax"] for row in rows), 6),
                "total_tokens_until_stop": sum(row["total_tokens_until_stop"] for row in rows),
            }
        )
    return out


def paired_effects(trajectories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {(row["item_id"], row["model"], row["condition"]): row for row in trajectories}
    out: list[dict[str, Any]] = []
    for model in sorted(MODEL_GENERATION):
        item_ids = sorted({row["item_id"] for row in trajectories if row["model"] == model})
        rows = []
        for item_id in item_ids:
            baseline = by_key[(item_id, model, "baseline")]
            contract = by_key[(item_id, model, "contract")]
            rows.append(
                {
                    "delta_ftga": contract["ftga"] - baseline["ftga"],
                    "rtt_reduction": baseline["rtt"] - contract["rtt"],
                    "unresolved_reduction": baseline["unresolved"] - contract["unresolved"],
                    "token_tax_reduction": baseline["token_tax"] - contract["token_tax"],
                    "total_token_reduction": baseline["total_tokens_until_stop"] - contract["total_tokens_until_stop"],
                    "extra_token_reduction": baseline["extra_tokens_after_first"] - contract["extra_tokens_after_first"],
                }
            )
        out.append(
            {
                "model_generation": MODEL_GENERATION[model],
                "model": model,
                "n_pairs": len(item_ids),
                "delta_ftga_pp": round(100 * mean(row["delta_ftga"] for row in rows), 1),
                "rtt_reduction": round(mean(row["rtt_reduction"] for row in rows), 3),
                "unresolved_reduction_pp": round(100 * mean(row["unresolved_reduction"] for row in rows), 1),
                "token_tax_reduction": round(mean(row["token_tax_reduction"] for row in rows), 6),
                "mean_total_tokens_baseline_minus_contract": round(mean(row["total_token_reduction"] for row in rows), 3),
                "mean_extra_tokens_baseline_minus_contract": round(mean(row["extra_token_reduction"] for row in rows), 3),
                "sum_total_tokens_baseline_minus_contract": sum(row["total_token_reduction"] for row in rows),
            }
        )
    return out


def fmt(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}"


def row_by(rows: list[dict[str, Any]], *, model: str, condition: str | None = None) -> dict[str, Any]:
    for row in rows:
        if row["model"] == model and (condition is None or row.get("condition") == condition):
            return row
    raise AssertionError(f"missing row for {model}/{condition}")


def write_markdown(path: Path, summary_rows: list[dict[str, Any]], effect_rows: list[dict[str, Any]]) -> None:
    g55_contract = row_by(summary_rows, model="gpt-5.5", condition="contract")
    g55_effect = row_by(effect_rows, model="gpt-5.5")
    g54_effect = row_by(effect_rows, model="gpt-5.4-mini")
    lines = [
        "# Efficiency Tradeoff Analysis",
        "",
        "This supplement combines first-turn global alignment with absolute saved",
        "token counts across the five full 120-item runs. It reports provider",
        "token counts only; it is not a dollar-cost estimate.",
        "",
        "## Model-Condition Surface",
        "",
        "| Generation | Model | Condition | FTGA | Mean RTT | Unresolved | Mean first-turn tokens | Mean total tokens | Mean token tax | Total tokens |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['model_generation']} | {row['model']} | {row['condition']} | "
            f"{row['ftga_pct']:.1f}% | {row['mean_rtt']:.3f} | {row['unresolved_pct']:.1f}% | "
            f"{row['mean_first_turn_tokens']:.1f} | {row['mean_total_tokens_until_stop']:.1f} | "
            f"{row['mean_token_tax']:.3f}x | {row['total_tokens_until_stop']} |"
        )

    lines.extend(
        [
            "",
            "## Paired Baseline Minus Contract Effects",
            "",
            "Positive token-tax reduction means lower normalized repair burden. Positive",
            "total-token reduction would mean fewer absolute tokens; negative values mean",
            "the longer contract uses more absolute tokens.",
            "",
            "| Generation | Model | FTGA delta | RTT reduction | Token-tax reduction | Mean total-token reduction | Mean extra-token reduction | Sum total-token reduction |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in effect_rows:
        lines.append(
            f"| {row['model_generation']} | {row['model']} | {row['delta_ftga_pp']:+.1f} pp | "
            f"{row['rtt_reduction']:+.3f} | {row['token_tax_reduction']:+.3f}x | "
            f"{row['mean_total_tokens_baseline_minus_contract']:+.1f} | "
            f"{row['mean_extra_tokens_baseline_minus_contract']:+.1f} | "
            f"{row['sum_total_tokens_baseline_minus_contract']:+d} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The Global Interaction Contract lowers normalized token tax for every full-run model,",
            "but it increases absolute total tokens for every full-run model because the system prompt is longer.",
            "This keeps the paper's token-tax claim scoped to repair burden rather than API-cost savings.",
            "",
            f"`gpt-5.5` contract is the strongest alignment point: {g55_contract['ftga_pct']:.1f}% FTGA, "
            f"{g55_contract['mean_rtt']:.3f} mean RTT, and {g55_contract['mean_token_tax']:.3f}x token tax.",
            f"However, compared with its baseline, it still uses {abs(g55_effect['mean_total_tokens_baseline_minus_contract']):.1f} more",
            "absolute tokens per item on average while saving",
            f"{g55_effect['mean_extra_tokens_baseline_minus_contract']:.1f} repair tokens after the first turn.",
            "",
            f"`gpt-5.4-mini` shows the lower-cost-current-model boundary: token tax falls by {g54_effect['token_tax_reduction']:.3f}x,",
            f"but absolute total tokens increase by {abs(g54_effect['mean_total_tokens_baseline_minus_contract']):.1f} per item",
            "and unresolved trajectories increase. This supports a deployment-diagnostic framing rather than a simple cost-saving claim.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/efficiency_tradeoff_v02"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/efficiency_tradeoff_v02.md"))
    args = parser.parse_args()

    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for path in SCORE_ARTIFACTS:
        for row in load_jsonl(path):
            grouped[trajectory_key(row)].append(row)
    trajectories = [trajectory_row(rows) for rows in grouped.values()]
    summary_rows = summarize_by_model(trajectories)
    effect_rows = paired_effects(trajectories)
    write_csv(args.out_dir / "efficiency_tradeoff_trajectory_metrics.csv", trajectories)
    write_csv(args.out_dir / "efficiency_tradeoff_by_model_condition.csv", summary_rows)
    write_csv(args.out_dir / "efficiency_tradeoff_paired_effects.csv", effect_rows)
    write_markdown(args.out_md, summary_rows, effect_rows)
    print(f"wrote efficiency tradeoff analysis to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
