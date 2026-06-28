#!/usr/bin/env python
"""Generate family-level failure-mode analysis for the RePromptTax stress run."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Any


FAMILY_LABELS = {
    "editing_preservation": "Editing preservation",
    "output_language_inference": "Output-language inference",
    "quote_preservation": "Quote preservation",
    "script_register_locale": "Script/register/locale",
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


def pct(value: str | float) -> float:
    return round(100.0 * float(value), 1)


def flt(value: str | float) -> float:
    return round(float(value), 2)


def top_failures(
    rows: list[dict[str, str]],
    *,
    model: str,
    condition: str,
    task_family: str,
) -> str:
    selected = [
        row
        for row in rows
        if row["model"] == model
        and row["condition"] == condition
        and row["task_family"] == task_family
    ]
    selected.sort(key=lambda row: (-int(row["count"]), row["failure_type"]))
    if not selected:
        return ""
    return "; ".join(f"{row['failure_type']}:{row['count']}" for row in selected)


def family_effect_rows(
    *,
    metrics_rows: list[dict[str, str]],
    paired_rows: list[dict[str, str]],
    failure_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    metrics = {
        (row["model"], row["condition"], row["task_family"]): row
        for row in metrics_rows
    }
    paired = {
        (row["model"], row["task_family"]): row
        for row in paired_rows
    }

    out: list[dict[str, Any]] = []
    keys = sorted(paired)
    for model, task_family in keys:
        baseline = metrics[(model, "baseline", task_family)]
        contract = metrics[(model, "contract", task_family)]
        effect = paired[(model, task_family)]
        out.append(
            {
                "model": model,
                "task_family": task_family,
                "n_pairs": int(effect["n_pairs"]),
                "baseline_ftga_pct": pct(baseline["ftga"]),
                "contract_ftga_pct": pct(contract["ftga"]),
                "delta_ftga_pp": round(float(effect["delta_ftga_pp"]), 1),
                "delta_ftga_ci_low": round(float(effect["delta_ftga_pp_ci_low"]), 1),
                "delta_ftga_ci_high": round(float(effect["delta_ftga_pp_ci_high"]), 1),
                "baseline_mean_rtt": flt(baseline["mean_rtt"]),
                "contract_mean_rtt": flt(contract["mean_rtt"]),
                "rtt_reduction": flt(effect["rtt_reduction"]),
                "baseline_token_tax": flt(baseline["mean_token_tax"]),
                "contract_token_tax": flt(contract["mean_token_tax"]),
                "token_tax_reduction": flt(effect["token_tax_reduction"]),
                "baseline_unresolved_pct": pct(baseline["unresolved_rate"]),
                "contract_unresolved_pct": pct(contract["unresolved_rate"]),
                "baseline_initial_failures": int(baseline["initially_failed_n"]),
                "contract_initial_failures": int(contract["initially_failed_n"]),
                "baseline_failure_types": top_failures(
                    failure_rows,
                    model=model,
                    condition="baseline",
                    task_family=task_family,
                ),
                "contract_failure_types": top_failures(
                    failure_rows,
                    model=model,
                    condition="contract",
                    task_family=task_family,
                ),
            }
        )
    return out


def aggregate_family_rows(metrics_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in metrics_rows:
        grouped[(row["condition"], row["task_family"])].append(row)

    out: list[dict[str, Any]] = []
    for (condition, task_family), rows in sorted(grouped.items()):
        n = sum(int(row["n"]) for row in rows)
        out.append(
            {
                "condition": condition,
                "task_family": task_family,
                "n": n,
                "ftga_pct": round(
                    sum(float(row["ftga"]) * int(row["n"]) for row in rows) * 100.0 / n,
                    1,
                ),
                "mean_rtt": round(
                    sum(float(row["mean_rtt"]) * int(row["n"]) for row in rows) / n,
                    2,
                ),
                "mean_token_tax": round(
                    sum(float(row["mean_token_tax"]) * int(row["n"]) for row in rows) / n,
                    2,
                ),
                "initial_failures": sum(int(row["initially_failed_n"]) for row in rows),
            }
        )
    return out


def aggregate_failure_rows(
    *,
    metrics_rows: list[dict[str, str]],
    failure_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    denominators: dict[tuple[str, str], int] = defaultdict(int)
    for row in metrics_rows:
        denominators[(row["condition"], row["task_family"])] += int(row["initially_failed_n"])

    counts: dict[tuple[str, str, str], int] = defaultdict(int)
    for row in failure_rows:
        key = (row["condition"], row["task_family"], row["failure_type"])
        counts[key] += int(row["count"])

    out: list[dict[str, Any]] = []
    for (condition, task_family, failure_type), count in sorted(counts.items()):
        denom = denominators[(condition, task_family)]
        out.append(
            {
                "condition": condition,
                "task_family": task_family,
                "failure_type": failure_type,
                "count": count,
                "initial_failure_denominator": denom,
                "share_of_initial_failures": round(count / denom, 3) if denom else "",
            }
        )
    return out


def by_key(rows: list[dict[str, Any]], *keys: str) -> dict[tuple[Any, ...], dict[str, Any]]:
    return {tuple(row[key] for key in keys): row for row in rows}


def write_markdown(
    path: Path,
    *,
    tables_dir: Path,
    family_effects: list[dict[str, Any]],
    aggregate_families: list[dict[str, Any]],
    aggregate_failures: list[dict[str, Any]],
) -> None:
    effects = by_key(family_effects, "model", "task_family")
    family_by_condition = by_key(aggregate_families, "condition", "task_family")

    lines = [
        "# RePromptTax Failure-Mode Analysis",
        "",
        f"Generated from `{tables_dir}/`.",
        "",
        "## Family-Level Burden",
        "",
        "| Task family | Baseline FTGA | Contract FTGA | Baseline failures | Contract failures | Baseline RTT | Contract RTT |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for family in FAMILY_LABELS:
        baseline = family_by_condition[("baseline", family)]
        contract = family_by_condition[("contract", family)]
        lines.append(
            "| "
            f"{FAMILY_LABELS[family]} | "
            f"{baseline['ftga_pct']:.1f}% | "
            f"{contract['ftga_pct']:.1f}% | "
            f"{baseline['initial_failures']}/{baseline['n']} | "
            f"{contract['initial_failures']}/{contract['n']} | "
            f"{baseline['mean_rtt']:.2f} | "
            f"{contract['mean_rtt']:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Main Interpretations",
            "",
        ]
    )

    gpt41_edit = effects[("gpt-4.1", "editing_preservation")]
    mini_edit = effects[("gpt-4.1-mini", "editing_preservation")]
    nano_edit = effects[("gpt-4.1-nano", "editing_preservation")]
    nano_quote = effects[("gpt-4.1-nano", "quote_preservation")]
    output_baseline = family_by_condition[("baseline", "output_language_inference")]
    output_contract = family_by_condition[("contract", "output_language_inference")]

    lines.extend(
        [
            "- Editing preservation is the dominant baseline burden: across models, "
            "baseline first-turn failures occur in "
            f"{family_by_condition[('baseline', 'editing_preservation')]['initial_failures']}/"
            f"{family_by_condition[('baseline', 'editing_preservation')]['n']} "
            "editing-preservation trajectories, and aggregate FTGA is "
            f"{family_by_condition[('baseline', 'editing_preservation')]['ftga_pct']:.1f}%.",
            "- The contract improves editing-preservation FTGA by "
            f"{gpt41_edit['delta_ftga_pp']:.1f} pp for gpt-4.1, "
            f"{mini_edit['delta_ftga_pp']:.1f} pp for gpt-4.1-mini, and "
            f"{nano_edit['delta_ftga_pp']:.1f} pp for gpt-4.1-nano.",
            "- Output-language inference is saturated in this pilot: aggregate FTGA is "
            f"{output_baseline['ftga_pct']:.1f}% in baseline and "
            f"{output_contract['ftga_pct']:.1f}% under the contract.",
            "- Nano quote-preservation remains a capability boundary: first-turn FTGA is "
            f"{nano_quote['baseline_ftga_pct']:.1f}% in baseline and "
            f"{nano_quote['contract_ftga_pct']:.1f}% under the contract, but mean RTT falls from "
            f"{nano_quote['baseline_mean_rtt']:.2f} to {nano_quote['contract_mean_rtt']:.2f}.",
            "",
            "## Aggregated First-Turn Failure Types",
            "",
            "| Condition | Task family | Failure type | Count | Share of initial failures |",
            "|---|---|---|---:|---:|",
        ]
    )
    for row in aggregate_failures:
        lines.append(
            "| "
            f"{row['condition']} | "
            f"{FAMILY_LABELS[row['task_family']]} | "
            f"{row['failure_type']} | "
            f"{row['count']} | "
            f"{100.0 * float(row['share_of_initial_failures']):.1f}% |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tables-dir", type=Path, default=Path("results/tables/openai_three_model_stress_v02_full120"))
    parser.add_argument("--paper-out", type=Path, default=Path("paper/failure_mode_analysis_v02_full120.md"))
    args = parser.parse_args()

    metrics_rows = read_csv(args.tables_dir / "metrics_by_family.csv")
    paired_rows = read_csv(args.tables_dir / "paired_contract_effects_by_family.csv")
    failure_rows = read_csv(args.tables_dir / "failure_types_by_family.csv")

    family_effects = family_effect_rows(
        metrics_rows=metrics_rows,
        paired_rows=paired_rows,
        failure_rows=failure_rows,
    )
    aggregate_families = aggregate_family_rows(metrics_rows)
    aggregate_failures = aggregate_failure_rows(
        metrics_rows=metrics_rows,
        failure_rows=failure_rows,
    )

    write_csv(args.tables_dir / "family_effect_summary.csv", family_effects)
    write_csv(args.tables_dir / "failure_type_summary.csv", aggregate_failures)
    write_markdown(
        args.paper_out,
        tables_dir=args.tables_dir,
        family_effects=family_effects,
        aggregate_families=aggregate_families,
        aggregate_failures=aggregate_failures,
    )
    print(f"wrote failure-mode analysis to {args.paper_out}")


if __name__ == "__main__":
    main()
