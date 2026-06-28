#!/usr/bin/env python
"""Analyze cross-model item hardness for the RePromptTax stress run."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


MODELS = ("gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano")
CONDITIONS = ("baseline", "contract")
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


def condition_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    rows = sorted(rows, key=lambda row: row["model"])
    models = [row["model"] for row in rows]
    if models != sorted(MODELS):
        raise ValueError(f"expected one row per model, got {models}")
    failed = [row["model"] for row in rows if int(row["ftga"]) == 0]
    unresolved = [row["model"] for row in rows if int(row["unresolved"]) == 1]
    return {
        "fail_n": len(failed),
        "pass_n": len(rows) - len(failed),
        "unresolved_n": len(unresolved),
        "failure_models": ";".join(failed),
        "unresolved_models": ";".join(unresolved),
        "mean_rtt": mean(float(row["rtt"]) for row in rows),
        "mean_token_tax": mean(float(row["token_tax"]) for row in rows),
    }


def item_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    meta: dict[str, dict[str, str]] = {}
    for row in rows:
        item_id = row["item_id"]
        grouped[item_id][row["condition"]].append(row)
        meta[item_id] = {
            "language_pair": row["language_pair"],
            "task_family": row["task_family"],
        }

    out: list[dict[str, Any]] = []
    for item_id in sorted(grouped):
        if set(grouped[item_id]) != set(CONDITIONS):
            raise ValueError(f"{item_id} does not have both baseline and contract rows")
        baseline = condition_summary(grouped[item_id]["baseline"])
        contract = condition_summary(grouped[item_id]["contract"])
        out.append(
            {
                "item_id": item_id,
                **meta[item_id],
                "baseline_fail_models_n": baseline["fail_n"],
                "contract_fail_models_n": contract["fail_n"],
                "fail_models_reduction": baseline["fail_n"] - contract["fail_n"],
                "baseline_failure_models": baseline["failure_models"],
                "contract_failure_models": contract["failure_models"],
                "baseline_unresolved_models_n": baseline["unresolved_n"],
                "contract_unresolved_models_n": contract["unresolved_n"],
                "baseline_unresolved_models": baseline["unresolved_models"],
                "contract_unresolved_models": contract["unresolved_models"],
                "baseline_mean_rtt": round(baseline["mean_rtt"], 3),
                "contract_mean_rtt": round(contract["mean_rtt"], 3),
                "mean_rtt_reduction": round(baseline["mean_rtt"] - contract["mean_rtt"], 3),
                "baseline_mean_token_tax": round(baseline["mean_token_tax"], 3),
                "contract_mean_token_tax": round(contract["mean_token_tax"], 3),
                "mean_token_tax_reduction": round(baseline["mean_token_tax"] - contract["mean_token_tax"], 3),
            }
        )
    return out


def summarize_items(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    return {
        "items": n,
        "baseline_all_models_pass": sum(row["baseline_fail_models_n"] == 0 for row in rows),
        "baseline_any_model_fail": sum(row["baseline_fail_models_n"] > 0 for row in rows),
        "baseline_all_models_fail": sum(row["baseline_fail_models_n"] == len(MODELS) for row in rows),
        "contract_all_models_pass": sum(row["contract_fail_models_n"] == 0 for row in rows),
        "contract_any_model_fail": sum(row["contract_fail_models_n"] > 0 for row in rows),
        "contract_all_models_fail": sum(row["contract_fail_models_n"] == len(MODELS) for row in rows),
        "fewer_fail_models_under_contract": sum(row["fail_models_reduction"] > 0 for row in rows),
        "more_fail_models_under_contract": sum(row["fail_models_reduction"] < 0 for row in rows),
        "same_fail_models_under_contract": sum(row["fail_models_reduction"] == 0 for row in rows),
        "lower_mean_rtt_under_contract": sum(row["mean_rtt_reduction"] > 0 for row in rows),
        "higher_mean_rtt_under_contract": sum(row["mean_rtt_reduction"] < 0 for row in rows),
        "same_mean_rtt_under_contract": sum(row["mean_rtt_reduction"] == 0 for row in rows),
        "baseline_any_unresolved": sum(row["baseline_unresolved_models_n"] > 0 for row in rows),
        "contract_any_unresolved": sum(row["contract_unresolved_models_n"] > 0 for row in rows),
    }


def by_family(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["task_family"]].append(row)
    out: list[dict[str, Any]] = []
    for family, family_rows in sorted(grouped.items()):
        summary = summarize_items(family_rows)
        out.append({"task_family": family, **summary})
    return out


def hardest_rows(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    selected = [
        row
        for row in rows
        if row["contract_fail_models_n"] > 0 or row["contract_unresolved_models_n"] > 0
    ]
    selected.sort(
        key=lambda row: (
            -row["contract_fail_models_n"],
            -row["contract_unresolved_models_n"],
            -row["baseline_fail_models_n"],
            row["task_family"],
            row["language_pair"],
            row["item_id"],
        )
    )
    fields = [
        "item_id",
        "language_pair",
        "task_family",
        "baseline_fail_models_n",
        "contract_fail_models_n",
        "fail_models_reduction",
        "contract_failure_models",
        "contract_unresolved_models_n",
        "contract_unresolved_models",
        "mean_rtt_reduction",
    ]
    return [{field: row[field] for field in fields} for row in selected[:limit]]


def pct(count: int, denom: int) -> str:
    return f"{100.0 * count / denom:.1f}%"


def write_markdown(
    path: Path,
    *,
    trajectory_metrics: Path,
    summary: dict[str, Any],
    family_rows: list[dict[str, Any]],
    hardest: list[dict[str, Any]],
) -> None:
    n = int(summary["items"])
    lines = [
        "# Item-Consistency Analysis",
        "",
        f"Generated from `{trajectory_metrics}`. This diagnostic aggregates over the",
        "three evaluated models to separate systematic hard items from scattered",
        "single-model failures. It is item-level evidence for the stress pilot, not",
        "a population-level claim.",
        "",
        "## Overall",
        "",
        "| Metric | Items | Share |",
        "|---|---:|---:|",
        f"| Baseline all-model pass | {summary['baseline_all_models_pass']} | {pct(summary['baseline_all_models_pass'], n)} |",
        f"| Baseline any-model fail | {summary['baseline_any_model_fail']} | {pct(summary['baseline_any_model_fail'], n)} |",
        f"| Baseline all-model fail | {summary['baseline_all_models_fail']} | {pct(summary['baseline_all_models_fail'], n)} |",
        f"| Contract all-model pass | {summary['contract_all_models_pass']} | {pct(summary['contract_all_models_pass'], n)} |",
        f"| Contract any-model fail | {summary['contract_any_model_fail']} | {pct(summary['contract_any_model_fail'], n)} |",
        f"| Contract all-model fail | {summary['contract_all_models_fail']} | {pct(summary['contract_all_models_fail'], n)} |",
        f"| Fewer failing models under contract | {summary['fewer_fail_models_under_contract']} | {pct(summary['fewer_fail_models_under_contract'], n)} |",
        f"| More failing models under contract | {summary['more_fail_models_under_contract']} | {pct(summary['more_fail_models_under_contract'], n)} |",
        f"| Lower mean RTT under contract | {summary['lower_mean_rtt_under_contract']} | {pct(summary['lower_mean_rtt_under_contract'], n)} |",
        f"| Contract has any unresolved model | {summary['contract_any_unresolved']} | {pct(summary['contract_any_unresolved'], n)} |",
        "",
        "## By Task Family",
        "",
        "| Task family | Items | Baseline any fail | Contract any fail | Baseline all fail | Contract all fail | Fewer failing models | More failing models |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in family_rows:
        items = int(row["items"])
        lines.append(
            "| "
            f"{FAMILY_LABELS.get(row['task_family'], row['task_family'])} | "
            f"{items} | "
            f"{row['baseline_any_model_fail']} ({pct(row['baseline_any_model_fail'], items)}) | "
            f"{row['contract_any_model_fail']} ({pct(row['contract_any_model_fail'], items)}) | "
            f"{row['baseline_all_models_fail']} | "
            f"{row['contract_all_models_fail']} | "
            f"{row['fewer_fail_models_under_contract']} | "
            f"{row['more_fail_models_under_contract']} |"
        )

    lines.extend(
        [
            "",
            "## Hardest Residual Items",
            "",
            "| Item | Language | Family | Baseline fail models | Contract fail models | Reduction | Contract failure models | Contract unresolved models | RTT reduction |",
            "|---|---|---|---:|---:|---:|---|---|---:|",
        ]
    )
    for row in hardest:
        lines.append(
            "| "
            f"{row['item_id']} | {row['language_pair']} | {FAMILY_LABELS.get(row['task_family'], row['task_family'])} | "
            f"{row['baseline_fail_models_n']} | {row['contract_fail_models_n']} | {row['fail_models_reduction']} | "
            f"{row['contract_failure_models'] or 'none'} | {row['contract_unresolved_models'] or 'none'} | "
            f"{row['mean_rtt_reduction']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The stress set contains both systematic and model-specific failures. Under",
            f"baseline prompting, {summary['baseline_any_model_fail']}/{n} items fail for at least",
            f"one model and {summary['baseline_all_models_fail']}/{n} fail for all three models.",
            "The contract shifts the distribution but does not eliminate hard cases:",
            f"{summary['contract_any_model_fail']}/{n} items still fail for at least one model,",
            f"while {summary['contract_all_models_fail']}/{n} fail for all three models.",
            f"Fewer models fail under the contract on {summary['fewer_fail_models_under_contract']}/{n}",
            f"items, while more models fail on {summary['more_fail_models_under_contract']}/{n}.",
            "This supports the conservative claim boundary: the mitigation reduces",
            "interaction burden on the pilot, but residual item-level failures remain.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--trajectory-metrics",
        type=Path,
        default=Path("results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("results/tables/openai_three_model_stress_v02_full120"),
    )
    parser.add_argument("--out-md", type=Path, default=Path("paper/item_consistency_analysis_v02_full120.md"))
    parser.add_argument("--hardest-limit", type=int, default=12)
    args = parser.parse_args()

    rows = read_csv(args.trajectory_metrics)
    items = item_rows(rows)
    summary = summarize_items(items)
    family_rows = by_family(items)
    hardest = hardest_rows(items, args.hardest_limit)

    write_csv(args.out_dir / "item_consistency_by_item.csv", items)
    write_csv(args.out_dir / "item_consistency_summary.csv", [summary])
    write_csv(args.out_dir / "item_consistency_by_family.csv", family_rows)
    write_csv(args.out_dir / "item_consistency_hardest_items.csv", hardest)
    write_markdown(
        args.out_md,
        trajectory_metrics=args.trajectory_metrics,
        summary=summary,
        family_rows=family_rows,
        hardest=hardest,
    )
    print(f"wrote item-consistency analysis to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
