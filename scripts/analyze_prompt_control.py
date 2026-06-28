#!/usr/bin/env python
"""Summarize the nano generic-helpfulness prompt control."""

from __future__ import annotations

import argparse
import csv
from math import comb
from pathlib import Path
from statistics import mean
from typing import Any


CONDITIONS = ["baseline", "generic_helpfulness", "contract"]
COMPARISONS = [
    ("baseline", "generic_helpfulness"),
    ("baseline", "contract"),
    ("generic_helpfulness", "contract"),
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


def pct(value: float) -> float:
    return 100.0 * value


def sign_test_p_value(improved: int, worsened: int) -> float:
    n = improved + worsened
    if n == 0:
        return 1.0
    k = min(improved, worsened)
    tail = sum(comb(n, i) for i in range(k + 1)) / (2**n)
    return min(1.0, 2.0 * tail)


def index_rows(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    indexed: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        if row["model"] != "gpt-4.1-nano":
            continue
        if row["condition"] not in CONDITIONS:
            continue
        indexed[(row["item_id"], row["condition"])] = row
    return indexed


def require_complete(indexed: dict[tuple[str, str], dict[str, str]], expected_items: int) -> list[str]:
    item_ids = sorted({item_id for item_id, _ in indexed})
    missing = []
    for item_id in item_ids:
        for condition in CONDITIONS:
            if (item_id, condition) not in indexed:
                missing.append(f"{item_id}:{condition}")
    if missing:
        raise AssertionError(f"missing paired prompt-control rows: {missing[:10]}")
    if len(item_ids) != expected_items:
        raise AssertionError(f"expected {expected_items} paired stress items, found {len(item_ids)}")
    return item_ids


def summarize(indexed: dict[tuple[str, str], dict[str, str]], item_ids: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for condition in CONDITIONS:
        rows = [indexed[(item_id, condition)] for item_id in item_ids]
        initially_failed = sum(1 for row in rows if int(row["initially_failed"]) == 1)
        out.append(
            {
                "model": "gpt-4.1-nano",
                "condition": condition,
                "n": len(rows),
                "ftga": mean(float(row["ftga"]) for row in rows),
                "mean_rtt": mean(float(row["rtt"]) for row in rows),
                "mean_token_tax": mean(float(row["token_tax"]) for row in rows),
                "unresolved_rate": mean(float(row["unresolved"]) for row in rows),
                "initially_failed_n": initially_failed,
            }
        )
    return out


def paired_effects(indexed: dict[tuple[str, str], dict[str, str]], item_ids: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for before, after in COMPARISONS:
        ftga_deltas = []
        rtt_reductions = []
        token_tax_reductions = []
        unresolved_reductions = []
        improved = 0
        worsened = 0
        tied = 0
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
        out.append(
            {
                "comparison": f"{after}_minus_{before}",
                "n_pairs": len(item_ids),
                "ftga_improved": improved,
                "ftga_worsened": worsened,
                "ftga_tied": tied,
                "ftga_sign_test_p": sign_test_p_value(improved, worsened),
                "delta_ftga_pp": pct(mean(ftga_deltas)),
                "rtt_reduction": mean(rtt_reductions),
                "token_tax_reduction": mean(token_tax_reductions),
                "unresolved_reduction_pp": pct(mean(unresolved_reductions)),
            }
        )
    return out


def fmt_pct(value: float) -> str:
    return f"{pct(value):.1f}%"


def fmt_pp(value: float) -> str:
    return f"{value:+.1f} pp"


def write_markdown(path: Path, summary_rows: list[dict[str, Any]], effect_rows: list[dict[str, Any]], *, n_items: int) -> None:
    by_condition = {row["condition"]: row for row in summary_rows}
    by_comparison = {row["comparison"]: row for row in effect_rows}
    lines = [
        "# Prompt-Control Diagnostic",
        "",
        "This is a single-model diagnostic on `gpt-4.1-nano`, not a paper-facing",
        "three-model claim. It tests whether a longer generic helpfulness prompt",
        f"explains the Global Interaction Contract result on the {n_items}-item stress pilot.",
        "",
        "## Aggregate Metrics",
        "",
        "| Condition | FTGA | Mean RTT | Token tax | Unresolved | Initial failures |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for condition in CONDITIONS:
        row = by_condition[condition]
        lines.append(
            "| "
            f"{condition} | "
            f"{fmt_pct(float(row['ftga']))} | "
            f"{float(row['mean_rtt']):.2f} | "
            f"{float(row['mean_token_tax']):.2f}x | "
            f"{fmt_pct(float(row['unresolved_rate']))} | "
            f"{row['initially_failed_n']} |"
        )
    lines.extend(
        [
            "",
            "## Paired Effects",
            "",
            "| Comparison | FTGA delta | Improved / worsened / tied | Sign-test p | RTT reduction | Token-tax reduction | Unresolved reduction |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for comparison in [
        "generic_helpfulness_minus_baseline",
        "contract_minus_baseline",
        "contract_minus_generic_helpfulness",
    ]:
        row = by_comparison[comparison]
        lines.append(
            "| "
            f"{comparison} | "
            f"{fmt_pp(float(row['delta_ftga_pp']))} | "
            f"{row['ftga_improved']} / {row['ftga_worsened']} / {row['ftga_tied']} | "
            f"{float(row['ftga_sign_test_p']):.4f} | "
            f"{float(row['rtt_reduction']):.2f} | "
            f"{float(row['token_tax_reduction']):.2f}x | "
            f"{fmt_pp(float(row['unresolved_reduction_pp']))} |"
        )
    generic = by_condition["generic_helpfulness"]
    contract = by_condition["contract"]
    baseline = by_condition["baseline"]
    contract_vs_generic = by_comparison["contract_minus_generic_helpfulness"]
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"The generic helpfulness prompt improves FTGA from {fmt_pct(float(baseline['ftga']))} to {fmt_pct(float(generic['ftga']))},",
            "so some mitigation benefit comes from generic instruction-following scaffolding.",
            f"The specific contract reaches {fmt_pct(float(contract['ftga']))} FTGA and has the lowest token tax.",
            f"Relative to generic helpfulness, the contract adds {fmt_pp(float(contract_vs_generic['delta_ftga_pp']))}",
            "FTGA with no additional mean RTT reduction. This diagnostic supports a conservative",
            "claim: the Global Interaction Contract beats generic helpfulness in this",
            "three-condition control, but this does not prove that every gain is specific",
            "to multilingual-contract wording or that the full contract is globally best.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--main-trajectories",
        type=Path,
        default=Path("results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv"),
    )
    parser.add_argument(
        "--control-trajectories",
        type=Path,
        default=Path("results/tables/openai_nano_stress_v02_full120_generic_helpfulness/trajectory_metrics.csv"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/openai_nano_stress_v02_full120_prompt_control"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/prompt_control_analysis.md"))
    parser.add_argument("--expected-items", type=int, default=120)
    args = parser.parse_args()

    indexed = index_rows(read_csv(args.main_trajectories) + read_csv(args.control_trajectories))
    item_ids = require_complete(indexed, args.expected_items)
    summary_rows = summarize(indexed, item_ids)
    effect_rows = paired_effects(indexed, item_ids)
    write_csv(args.out_dir / "prompt_control_summary.csv", summary_rows)
    write_csv(args.out_dir / "prompt_control_paired_effects.csv", effect_rows)
    write_markdown(args.out_md, summary_rows, effect_rows, n_items=len(item_ids))
    print(f"wrote prompt-control diagnostic to {args.out_md} and {args.out_dir}")


if __name__ == "__main__":
    main()
