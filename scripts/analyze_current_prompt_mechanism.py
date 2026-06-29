#!/usr/bin/env python
"""Summarize current-model prompt-mechanism diagnostics."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from math import comb
from pathlib import Path
from statistics import mean
from typing import Any


CONDITIONS = ["baseline", "contract", "content_preservation"]
COMPARISONS = [
    ("baseline", "contract"),
    ("baseline", "content_preservation"),
    ("contract", "content_preservation"),
]


@dataclass(frozen=True)
class MechanismConfig:
    label: str
    model: str
    base_tables: Path
    content_tables: Path
    base_outputs: Path
    content_outputs: Path
    out_dir: Path
    out_md: Path


CONFIGS = [
    MechanismConfig(
        label="gpt54mini",
        model="gpt-5.4-mini",
        base_tables=Path("results/tables/openai_gpt54mini_stress_v02_full120"),
        content_tables=Path("results/tables/openai_gpt54mini_stress_v02_full120_content_preservation"),
        base_outputs=Path("results/model_outputs/openai_gpt54mini_stress_v02_full120.jsonl"),
        content_outputs=Path("results/model_outputs/openai_gpt54mini_stress_v02_full120_content_preservation.jsonl"),
        out_dir=Path("results/tables/current_prompt_mechanism_gpt54mini_v02"),
        out_md=Path("paper/current_prompt_mechanism_gpt54mini_v02.md"),
    ),
    MechanismConfig(
        label="gpt55",
        model="gpt-5.5",
        base_tables=Path("results/tables/openai_gpt55_stress_v02_full120"),
        content_tables=Path("results/tables/openai_gpt55_stress_v02_full120_content_preservation"),
        base_outputs=Path("results/model_outputs/openai_gpt55_stress_v02_full120.jsonl"),
        content_outputs=Path("results/model_outputs/openai_gpt55_stress_v02_full120_content_preservation.jsonl"),
        out_dir=Path("results/tables/current_prompt_mechanism_gpt55_v02"),
        out_md=Path("paper/current_prompt_mechanism_gpt55_v02.md"),
    ),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


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


def row_by(rows: list[dict[str, str]], **kwargs: str) -> dict[str, str]:
    for row in rows:
        if all(row[key] == value for key, value in kwargs.items()):
            return row
    raise AssertionError(f"missing row for {kwargs}")


def sign_test_p_value(improved: int, worsened: int) -> float:
    n = improved + worsened
    if n == 0:
        return 1.0
    k = min(improved, worsened)
    tail = sum(comb(n, i) for i in range(k + 1)) / (2**n)
    return min(1.0, 2.0 * tail)


def summary_rows(config: MechanismConfig, base_metrics: list[dict[str, str]], content_metrics: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for condition in CONDITIONS:
        source = content_metrics if condition == "content_preservation" else base_metrics
        row = row_by(source, model=config.model, condition=condition)
        rows.append(
            {
                "model": config.model,
                "condition": condition,
                "n_items": int(row["n"]),
                "ftga_pct": round(100.0 * float(row["ftga"]), 1),
                "mean_rtt": round(float(row["mean_rtt"]), 3),
                "token_tax": round(float(row["mean_token_tax"]), 3),
                "unresolved_pct": round(100.0 * float(row["unresolved_rate"]), 1),
                "initial_failures": int(row["initially_failed_n"]),
            }
        )
    return rows


def family_rows(config: MechanismConfig, base_family: list[dict[str, str]], content_family: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for condition in CONDITIONS:
        source = content_family if condition == "content_preservation" else base_family
        for row in source:
            if row["model"] != config.model or row["condition"] != condition:
                continue
            rows.append(
                {
                    "model": config.model,
                    "condition": condition,
                    "task_family": row["task_family"],
                    "n_items": int(row["n"]),
                    "ftga_pct": round(100.0 * float(row["ftga"]), 1),
                    "mean_rtt": round(float(row["mean_rtt"]), 3),
                    "token_tax": round(float(row["mean_token_tax"]), 3),
                    "unresolved_pct": round(100.0 * float(row["unresolved_rate"]), 1),
                    "initial_failures": int(row["initially_failed_n"]),
                }
            )
    return rows


def indexed_trajectories(
    config: MechanismConfig,
    base_rows: list[dict[str, str]],
    content_rows: list[dict[str, str]],
) -> dict[tuple[str, str], dict[str, str]]:
    indexed: dict[tuple[str, str], dict[str, str]] = {}
    for row in [*base_rows, *content_rows]:
        if row["model"] != config.model or row["condition"] not in CONDITIONS:
            continue
        key = (row["item_id"], row["condition"])
        if key in indexed:
            raise AssertionError(f"duplicate trajectory row for {key}")
        indexed[key] = row
    item_ids = sorted({item_id for item_id, _ in indexed})
    if len(item_ids) != 120:
        raise AssertionError(f"expected 120 items for {config.model}, found {len(item_ids)}")
    missing = [
        (item_id, condition)
        for item_id in item_ids
        for condition in CONDITIONS
        if (item_id, condition) not in indexed
    ]
    if missing:
        raise AssertionError(f"missing trajectory rows for {config.model}: {missing[:10]}")
    return indexed


def paired_rows(indexed: dict[tuple[str, str], dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    item_ids = sorted({item_id for item_id, _ in indexed})
    for before, after in COMPARISONS:
        ftga_deltas: list[float] = []
        rtt_reductions: list[float] = []
        token_tax_reductions: list[float] = []
        unresolved_reductions: list[float] = []
        improved = worsened = tied = 0
        for item_id in item_ids:
            before_row = indexed[(item_id, before)]
            after_row = indexed[(item_id, after)]
            ftga_delta = float(after_row["ftga"]) - float(before_row["ftga"])
            if ftga_delta > 0:
                improved += 1
            elif ftga_delta < 0:
                worsened += 1
            else:
                tied += 1
            ftga_deltas.append(ftga_delta)
            rtt_reductions.append(float(before_row["rtt"]) - float(after_row["rtt"]))
            token_tax_reductions.append(float(before_row["token_tax"]) - float(after_row["token_tax"]))
            unresolved_reductions.append(float(before_row["unresolved"]) - float(after_row["unresolved"]))
        rows.append(
            {
                "comparison": f"{after}_minus_{before}",
                "n_pairs": len(item_ids),
                "ftga_improved": improved,
                "ftga_worsened": worsened,
                "ftga_tied": tied,
                "ftga_sign_test_p": sign_test_p_value(improved, worsened),
                "delta_ftga_pp": round(100.0 * mean(ftga_deltas), 1),
                "rtt_reduction": round(mean(rtt_reductions), 3),
                "token_tax_reduction": round(mean(token_tax_reductions), 3),
                "unresolved_reduction_pp": round(100.0 * mean(unresolved_reductions), 1),
            }
        )
    return rows


def usage_rows(config: MechanismConfig) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for label, path, condition in [
        ("baseline+contract", config.base_outputs, ""),
        ("content_preservation", config.content_outputs, "content_preservation"),
    ]:
        data = load_jsonl(path)
        if condition:
            data = [row for row in data if row.get("condition") == condition]
        rows.append(
            {
                "artifact": label,
                "api_calls": len(data),
                "input_tokens": sum(int(row.get("input_tokens", 0)) for row in data),
                "output_tokens": sum(int(row.get("output_tokens", 0)) for row in data),
                "total_tokens": sum(int(row.get("input_tokens", 0)) + int(row.get("output_tokens", 0)) for row in data),
            }
        )
    return rows


def table_row(rows: list[dict[str, Any]], condition: str) -> dict[str, Any]:
    for row in rows:
        if row["condition"] == condition:
            return row
    raise AssertionError(f"missing condition {condition}")


def comparison_row(rows: list[dict[str, Any]], comparison: str) -> dict[str, Any]:
    for row in rows:
        if row["comparison"] == comparison:
            return row
    raise AssertionError(f"missing comparison {comparison}")


def interpretation_lines(
    *,
    config: MechanismConfig,
    baseline: dict[str, Any],
    contract: dict[str, Any],
    content: dict[str, Any],
    content_vs_contract: dict[str, Any],
    content_vs_baseline: dict[str, Any],
) -> list[str]:
    common = [
        (
            f"Content preservation improves FTGA from {baseline['ftga_pct']:.1f}% "
            f"to {content['ftga_pct']:.1f}% (+{content_vs_baseline['delta_ftga_pp']:.1f} pp), "
            f"close to the full contract's {contract['ftga_pct']:.1f}%."
        ),
        f"Against the full contract, content preservation changes FTGA by {content_vs_contract['delta_ftga_pp']:+.1f} pp",
        f"({content_vs_contract['ftga_improved']} improved, {content_vs_contract['ftga_worsened']} worsened items),",
        f"with {content_vs_contract['token_tax_reduction']:+.3f}x token-tax reduction.",
    ]
    if config.label == "gpt54mini":
        return [
            *common,
            "The mechanism claim should therefore be softened: on this current low-cost model,",
            "the narrower content-preservation prompt is essentially tied with the full contract,",
            "rather than clearly dominating it as in the earlier nano diagnostic.",
        ]
    return [
        *common,
        "For GPT-5.5, the narrower prompt matches or slightly exceeds the full contract on",
        "auto-scored FTGA while using marginally less token tax; the difference from the full",
        "contract is one net item and should be presented as mechanism evidence, not as a",
        "dominance claim. This supports the interpretation that literal content-preservation",
        "language accounts for most of the current-model gain on this stress benchmark.",
    ]


def write_markdown(
    path: Path,
    *,
    config: MechanismConfig,
    summary: list[dict[str, Any]],
    families: list[dict[str, Any]],
    paired: list[dict[str, Any]],
    usage: list[dict[str, Any]],
) -> None:
    baseline = table_row(summary, "baseline")
    contract = table_row(summary, "contract")
    content = table_row(summary, "content_preservation")
    content_vs_contract = comparison_row(paired, "content_preservation_minus_contract")
    content_vs_baseline = comparison_row(paired, "content_preservation_minus_baseline")

    lines = [
        "# Current-Model Prompt Mechanism Diagnostic",
        "",
        "This artifact compares the full Global Interaction Contract with the narrower",
        "content-preservation prompt on the full 120-item stress benchmark for",
        f"`{config.model}`. Baseline and contract rows reuse the current-model refresh run;",
        "the content-preservation row is a new one-condition follow-up.",
        "",
        "## Summary",
        "",
        "| Condition | FTGA | Mean RTT | Token tax | Unresolved | First-turn failures |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            "| "
            f"{row['condition']} | {row['ftga_pct']:.1f}% | {row['mean_rtt']:.3f} | "
            f"{row['token_tax']:.3f}x | {row['unresolved_pct']:.1f}% | {row['initial_failures']} |"
        )

    lines.extend(
        [
            "",
            "## Paired Effects",
            "",
            "| Comparison | FTGA delta | Improved | Worsened | Tied | Sign p | RTT reduction | Token-tax reduction | Unresolved reduction |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in paired:
        lines.append(
            "| "
            f"{row['comparison']} | {row['delta_ftga_pp']:+.1f} pp | {row['ftga_improved']} | "
            f"{row['ftga_worsened']} | {row['ftga_tied']} | {row['ftga_sign_test_p']:.6g} | "
            f"{row['rtt_reduction']:+.3f} | {row['token_tax_reduction']:+.3f}x | "
            f"{row['unresolved_reduction_pp']:+.1f} pp |"
        )

    lines.extend(
        [
            "",
            "## Family FTGA",
            "",
            "| Family | Baseline | Contract | Content preservation |",
            "|---|---:|---:|---:|",
        ]
    )
    family_names = sorted({row["task_family"] for row in families})
    for family in family_names:
        rows = {(row["condition"], row["task_family"]): row for row in families}
        lines.append(
            "| "
            f"{family} | {rows[('baseline', family)]['ftga_pct']:.1f}% | "
            f"{rows[('contract', family)]['ftga_pct']:.1f}% | "
            f"{rows[('content_preservation', family)]['ftga_pct']:.1f}% |"
        )

    lines.extend(
        [
            "",
            "## API Usage",
            "",
            "| Artifact | API calls | Input tokens | Output tokens | Total tokens |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in usage:
        lines.append(
            "| "
            f"{row['artifact']} | {row['api_calls']} | {row['input_tokens']} | "
            f"{row['output_tokens']} | {row['total_tokens']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            *interpretation_lines(
                config=config,
                baseline=baseline,
                contract=contract,
                content=content,
                content_vs_contract=content_vs_contract,
                content_vs_baseline=content_vs_baseline,
            ),
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def analyze_config(config: MechanismConfig) -> None:
    base_metrics = read_csv(config.base_tables / "metrics_summary.csv")
    content_metrics = read_csv(config.content_tables / "metrics_summary.csv")
    base_family = read_csv(config.base_tables / "metrics_by_family.csv")
    content_family = read_csv(config.content_tables / "metrics_by_family.csv")
    indexed = indexed_trajectories(
        config,
        read_csv(config.base_tables / "trajectory_metrics.csv"),
        read_csv(config.content_tables / "trajectory_metrics.csv"),
    )

    summary = summary_rows(config, base_metrics, content_metrics)
    families = family_rows(config, base_family, content_family)
    paired = paired_rows(indexed)
    usage = usage_rows(config)

    write_csv(config.out_dir / "current_prompt_mechanism_summary.csv", summary)
    write_csv(config.out_dir / "current_prompt_mechanism_by_family.csv", families)
    write_csv(config.out_dir / "current_prompt_mechanism_paired_effects.csv", paired)
    write_csv(config.out_dir / "current_prompt_mechanism_api_usage.csv", usage)
    write_markdown(config.out_md, config=config, summary=summary, families=families, paired=paired, usage=usage)
    print(f"wrote current prompt-mechanism diagnostic for {config.model} to {config.out_dir} and {config.out_md}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--models",
        nargs="+",
        choices=["all", *[config.label for config in CONFIGS]],
        default=["all"],
        help="which current-model mechanism diagnostics to generate",
    )
    args = parser.parse_args()

    labels = {config.label for config in CONFIGS} if "all" in args.models else set(args.models)
    for config in CONFIGS:
        if config.label in labels:
            analyze_config(config)


if __name__ == "__main__":
    main()
