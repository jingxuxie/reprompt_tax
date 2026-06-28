#!/usr/bin/env python
"""Analyze RePromptTax effects by language pair."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


LANGUAGE_LABELS = {
    "ar-en": "Arabic-English",
    "es-en": "Spanish-English",
    "hi-en": "Hindi-English",
}


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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def pct(value: float) -> float:
    return round(100.0 * value, 1)


def sign_test_p(positive_n: int, negative_n: int) -> float:
    n = positive_n + negative_n
    if n == 0:
        return 1.0
    observed = min(positive_n, negative_n)
    lower_tail = sum(math.comb(n, k) for k in range(observed + 1)) / (2**n)
    return min(1.0, 2.0 * lower_tail)


def metrics_by_language(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[(row["model"], row["condition"], row["language_pair"])].append(row)

    out: list[dict[str, Any]] = []
    for (model, condition, language_pair), group in sorted(groups.items()):
        require(len(group) == 40, f"expected 40 trajectories for {model}/{condition}/{language_pair}")
        out.append(
            {
                "model": model,
                "condition": condition,
                "language_pair": language_pair,
                "n": len(group),
                "ftga_pct": pct(mean(float(row["ftga"]) for row in group)),
                "mean_rtt": round(mean(float(row["rtt"]) for row in group), 3),
                "mean_token_tax": round(mean(float(row["token_tax"]) for row in group), 3),
                "unresolved_pct": pct(mean(float(row["unresolved"]) for row in group)),
                "initially_failed_n": sum(int(float(row["initially_failed"])) for row in group),
            }
        )
    return out


def paired_effects_by_language(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str, str], dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_key[(row["model"], row["language_pair"], row["item_id"])][row["condition"]] = row

    groups: dict[tuple[str, str], list[tuple[dict[str, str], dict[str, str]]]] = defaultdict(list)
    for (model, language_pair, _item_id), conditions in by_key.items():
        if set(conditions) != {"baseline", "contract"}:
            raise AssertionError(f"missing paired condition for {model}/{language_pair}")
        groups[(model, language_pair)].append((conditions["baseline"], conditions["contract"]))

    out: list[dict[str, Any]] = []
    for (model, language_pair), pairs in sorted(groups.items()):
        require(len(pairs) == 40, f"expected 40 paired trajectories for {model}/{language_pair}")
        ftga_deltas = [float(contract["ftga"]) - float(baseline["ftga"]) for baseline, contract in pairs]
        positive_n = sum(delta > 0 for delta in ftga_deltas)
        negative_n = sum(delta < 0 for delta in ftga_deltas)
        out.append(
            {
                "model": model,
                "language_pair": language_pair,
                "n_pairs": len(pairs),
                "delta_ftga_pp": round(100.0 * mean(ftga_deltas), 1),
                "rtt_reduction": round(mean(float(baseline["rtt"]) - float(contract["rtt"]) for baseline, contract in pairs), 3),
                "token_tax_reduction": round(mean(float(baseline["token_tax"]) - float(contract["token_tax"]) for baseline, contract in pairs), 3),
                "unresolved_reduction_pp": round(100.0 * mean(float(baseline["unresolved"]) - float(contract["unresolved"]) for baseline, contract in pairs), 1),
                "ftga_improved_n": positive_n,
                "ftga_worsened_n": negative_n,
                "ftga_tied_n": sum(delta == 0 for delta in ftga_deltas),
                "ftga_sign_test_p": round(sign_test_p(positive_n, negative_n), 4),
            }
        )
    return out


def aggregate_by_language(effect_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in effect_rows:
        groups[row["language_pair"]].append(row)
    out: list[dict[str, Any]] = []
    for language_pair, group in sorted(groups.items()):
        out.append(
            {
                "language_pair": language_pair,
                "models": len(group),
                "mean_delta_ftga_pp": round(mean(float(row["delta_ftga_pp"]) for row in group), 1),
                "mean_rtt_reduction": round(mean(float(row["rtt_reduction"]) for row in group), 3),
                "mean_token_tax_reduction": round(mean(float(row["token_tax_reduction"]) for row in group), 3),
                "total_ftga_improved_n": sum(int(row["ftga_improved_n"]) for row in group),
                "total_ftga_worsened_n": sum(int(row["ftga_worsened_n"]) for row in group),
                "total_ftga_tied_n": sum(int(row["ftga_tied_n"]) for row in group),
            }
        )
    return out


def find_row(rows: list[dict[str, Any]], **kwargs: str) -> dict[str, Any]:
    for row in rows:
        if all(row[key] == value for key, value in kwargs.items()):
            return row
    raise AssertionError(f"missing row for {kwargs}")


def write_markdown(
    path: Path,
    metric_rows: list[dict[str, Any]],
    effect_rows: list[dict[str, Any]],
    aggregate_rows: list[dict[str, Any]],
) -> None:
    lines = [
        "# Language-Slice Analysis",
        "",
        "Generated from `results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv`.",
        "",
        "This supplement checks whether aggregate mitigation effects are concentrated",
        "in a single language pair. Each language-pair slice has 40 paired items per",
        "model. The analysis is still a synthetic stress-slice analysis, not a",
        "population-level statement about speakers of these languages.",
        "",
        "## Metrics By Model And Language",
        "",
        "| Model | Condition | Language pair | FTGA | Mean RTT | Token tax | Unresolved | Initial failures |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in metric_rows:
        lines.append(
            "| "
            f"{row['model']} | {row['condition']} | {row['language_pair']} | "
            f"{row['ftga_pct']:.1f}% | {row['mean_rtt']:.3f} | {row['mean_token_tax']:.3f} | "
            f"{row['unresolved_pct']:.1f}% | {row['initially_failed_n']} |"
        )

    lines.extend(
        [
            "",
            "## Paired Contract Minus Baseline Effects",
            "",
            "| Model | Language pair | FTGA delta | RTT reduction | Token-tax reduction | Unresolved reduction | FTGA + / - / tie | Sign p |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in effect_rows:
        lines.append(
            "| "
            f"{row['model']} | {row['language_pair']} | {row['delta_ftga_pp']:+.1f} pp | "
            f"{row['rtt_reduction']:.3f} | {row['token_tax_reduction']:.3f} | "
            f"{row['unresolved_reduction_pp']:+.1f} pp | "
            f"{row['ftga_improved_n']} / {row['ftga_worsened_n']} / {row['ftga_tied_n']} | "
            f"{row['ftga_sign_test_p']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Aggregate Across Models By Language Pair",
            "",
            "| Language pair | Models | Mean FTGA delta | Mean RTT reduction | Mean token-tax reduction | FTGA + / - / tie |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in aggregate_rows:
        lines.append(
            "| "
            f"{row['language_pair']} | {row['models']} | {row['mean_delta_ftga_pp']:+.1f} pp | "
            f"{row['mean_rtt_reduction']:.3f} | {row['mean_token_tax_reduction']:.3f} | "
            f"{row['total_ftga_improved_n']} / {row['total_ftga_worsened_n']} / {row['total_ftga_tied_n']} |"
        )

    gpt41_ar = find_row(effect_rows, model="gpt-4.1", language_pair="ar-en")
    gpt41_es = find_row(effect_rows, model="gpt-4.1", language_pair="es-en")
    nano_ar = find_row(effect_rows, model="gpt-4.1-nano", language_pair="ar-en")
    mini_es = find_row(effect_rows, model="gpt-4.1-mini", language_pair="es-en")
    hi_agg = find_row(aggregate_rows, language_pair="hi-en")
    ar_agg = find_row(aggregate_rows, language_pair="ar-en")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"The largest language-slice gains appear in {LANGUAGE_LABELS['ar-en']}:",
            f"averaged across models, FTGA increases by {ar_agg['mean_delta_ftga_pp']:+.1f} pp.",
            f"`gpt-4.1-nano` improves by {nano_ar['delta_ftga_pp']:+.1f} pp on this slice",
            f"({nano_ar['ftga_improved_n']} improved, {nano_ar['ftga_worsened_n']} worsened).",
            "",
            f"`gpt-4.1` improves by {gpt41_ar['delta_ftga_pp']:+.1f} pp on Arabic-English and",
            f"{gpt41_es['delta_ftga_pp']:+.1f} pp on Spanish-English, while Hindi-English",
            "has little room to improve because baseline FTGA is already high.",
            "",
            f"The main weak slice for the contract is Spanish-English on `gpt-4.1-mini`,",
            f"where FTGA delta is {mini_es['delta_ftga_pp']:+.1f} pp despite lower token tax.",
            f"Aggregated Hindi-English FTGA movement is {hi_agg['mean_delta_ftga_pp']:+.1f} pp.",
            "",
            "These language-slice results support the aggregate claim that the contract",
            "reduces burden in the stress pilot, but they also make the boundary clear:",
            "the mitigation is not uniformly strong across every model/language pair.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trajectory-metrics", type=Path, default=Path("results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/openai_three_model_stress_v02_full120"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/language_slice_analysis_v02_full120.md"))
    args = parser.parse_args()

    rows = read_csv(args.trajectory_metrics)
    require(len(rows) == 720, f"expected 720 trajectory rows, found {len(rows)}")
    metric_rows = metrics_by_language(rows)
    effect_rows = paired_effects_by_language(rows)
    aggregate_rows = aggregate_by_language(effect_rows)

    write_csv(args.out_dir / "language_slice_metrics.csv", metric_rows)
    write_csv(args.out_dir / "language_slice_paired_effects.csv", effect_rows)
    write_csv(args.out_dir / "language_slice_aggregate_effects.csv", aggregate_rows)
    write_markdown(args.out_md, metric_rows, effect_rows, aggregate_rows)
    print(f"wrote language-slice analysis to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
