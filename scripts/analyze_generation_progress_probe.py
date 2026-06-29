#!/usr/bin/env python
"""Analyze item-level progress from GPT-4.1-family to GPT-5.x-family runs."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Any


TRAJECTORY_PATHS = [
    Path("results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv"),
    Path("results/tables/openai_gpt54mini_stress_v02_full120/trajectory_metrics.csv"),
    Path("results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv"),
]

GENERATION_MODELS = {
    "GPT-4.1 family": ["gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1"],
    "GPT-5.x family": ["gpt-5.4-mini", "gpt-5.5"],
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
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def pct(numerator: int, denominator: int) -> float:
    return round(100 * numerator / denominator, 1) if denominator else 0.0


def group_by_item(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["item_id"], []).append(row)
    return grouped


def fail_count(rows: list[dict[str, str]]) -> int:
    return sum(row["ftga"] == "0" for row in rows)


def summarize_generation_condition(
    generation: str,
    models: list[str],
    condition: str,
    rows: list[dict[str, str]],
) -> dict[str, Any]:
    sub = [row for row in rows if row["model"] in models and row["condition"] == condition]
    by_item = group_by_item(sub)
    failures = fail_count(sub)
    any_fail_items = sum(fail_count(item_rows) > 0 for item_rows in by_item.values())
    all_fail_items = sum(fail_count(item_rows) == len(models) for item_rows in by_item.values())
    return {
        "generation": generation,
        "condition": condition,
        "model_count": len(models),
        "item_count": len(by_item),
        "model_item_pairs": len(sub),
        "first_turn_failures": failures,
        "failure_pair_pct": pct(failures, len(sub)),
        "any_fail_items": any_fail_items,
        "all_fail_items": all_fail_items,
        "mean_failures_per_item": round(failures / len(by_item), 3),
        "unresolved_pairs": sum(row["unresolved"] == "1" for row in sub),
    }


def summarize_generation_family(
    generation: str,
    models: list[str],
    condition: str,
    family: str,
    rows: list[dict[str, str]],
) -> dict[str, Any]:
    sub = [
        row
        for row in rows
        if row["model"] in models and row["condition"] == condition and row["task_family"] == family
    ]
    by_item = group_by_item(sub)
    failures = fail_count(sub)
    return {
        "generation": generation,
        "condition": condition,
        "task_family": family,
        "model_item_pairs": len(sub),
        "first_turn_failures": failures,
        "failure_pair_pct": pct(failures, len(sub)),
        "any_fail_items": sum(fail_count(item_rows) > 0 for item_rows in by_item.values()),
        "all_fail_items": sum(fail_count(item_rows) == len(models) for item_rows in by_item.values()),
        "unresolved_pairs": sum(row["unresolved"] == "1" for row in sub),
    }


def rows_for(rows: list[dict[str, str]], *, item_id: str, condition: str, models: list[str]) -> list[dict[str, str]]:
    return [row for row in rows if row["item_id"] == item_id and row["condition"] == condition and row["model"] in models]


def row_for(rows: list[dict[str, str]], *, item_id: str, condition: str, model: str) -> dict[str, str]:
    matches = [row for row in rows if row["item_id"] == item_id and row["condition"] == condition and row["model"] == model]
    if len(matches) != 1:
        raise AssertionError(f"expected one row for {item_id}/{model}/{condition}, found {len(matches)}")
    return matches[0]


def item_progress_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    item_meta = {}
    for row in rows:
        item_meta[row["item_id"]] = {
            "language_pair": row["language_pair"],
            "task_family": row["task_family"],
        }
    out: list[dict[str, Any]] = []
    old_models = GENERATION_MODELS["GPT-4.1 family"]
    current_models = GENERATION_MODELS["GPT-5.x family"]
    for item_id in sorted(item_meta):
        old_baseline = rows_for(rows, item_id=item_id, condition="baseline", models=old_models)
        old_contract = rows_for(rows, item_id=item_id, condition="contract", models=old_models)
        current_baseline = rows_for(rows, item_id=item_id, condition="baseline", models=current_models)
        current_contract = rows_for(rows, item_id=item_id, condition="contract", models=current_models)
        g55_baseline = row_for(rows, item_id=item_id, condition="baseline", model="gpt-5.5")
        g55_contract = row_for(rows, item_id=item_id, condition="contract", model="gpt-5.5")
        old_baseline_fail_count = fail_count(old_baseline)
        old_contract_fail_count = fail_count(old_contract)
        current_baseline_fail_count = fail_count(current_baseline)
        current_contract_fail_count = fail_count(current_contract)
        out.append(
            {
                "item_id": item_id,
                **item_meta[item_id],
                "gpt41_baseline_fail_count": old_baseline_fail_count,
                "gpt41_contract_fail_count": old_contract_fail_count,
                "gpt5x_baseline_fail_count": current_baseline_fail_count,
                "gpt5x_contract_fail_count": current_contract_fail_count,
                "gpt55_baseline_pass": int(g55_baseline["ftga"] == "1"),
                "gpt55_contract_pass": int(g55_contract["ftga"] == "1"),
                "old_all_baseline_fail_gpt55_baseline_pass": int(old_baseline_fail_count == len(old_models) and g55_baseline["ftga"] == "1"),
                "old_any_baseline_fail_gpt55_baseline_pass": int(old_baseline_fail_count > 0 and g55_baseline["ftga"] == "1"),
                "old_any_baseline_fail_gpt55_contract_pass": int(old_baseline_fail_count > 0 and g55_contract["ftga"] == "1"),
                "old_all_contract_fail_gpt55_contract_pass": int(old_contract_fail_count == len(old_models) and g55_contract["ftga"] == "1"),
                "both_current_models_contract_fail": int(current_contract_fail_count == len(current_models)),
            }
        )
    return out


def category_rows(item_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    categories = [
        ("gpt41_baseline_any_fail_items", lambda row: row["gpt41_baseline_fail_count"] > 0),
        ("gpt41_baseline_all_fail_items", lambda row: row["gpt41_baseline_fail_count"] == 3),
        ("gpt41_contract_all_fail_items", lambda row: row["gpt41_contract_fail_count"] == 3),
        ("gpt5x_baseline_both_fail_items", lambda row: row["gpt5x_baseline_fail_count"] == 2),
        ("gpt5x_contract_both_fail_items", lambda row: row["gpt5x_contract_fail_count"] == 2),
        ("gpt41_all_baseline_fail_gpt55_baseline_pass", lambda row: row["old_all_baseline_fail_gpt55_baseline_pass"] == 1),
        ("gpt41_any_baseline_fail_gpt55_baseline_pass", lambda row: row["old_any_baseline_fail_gpt55_baseline_pass"] == 1),
        ("gpt41_any_baseline_fail_gpt55_contract_pass", lambda row: row["old_any_baseline_fail_gpt55_contract_pass"] == 1),
        ("gpt41_all_contract_fail_gpt55_contract_pass", lambda row: row["old_all_contract_fail_gpt55_contract_pass"] == 1),
    ]
    out: list[dict[str, Any]] = []
    for category, predicate in categories:
        matches = [row for row in item_rows if predicate(row)]
        families = Counter(row["task_family"] for row in matches)
        out.append(
            {
                "category": category,
                "item_count": len(matches),
                "editing_preservation": families.get("editing_preservation", 0),
                "output_language_inference": families.get("output_language_inference", 0),
                "quote_preservation": families.get("quote_preservation", 0),
                "script_register_locale": families.get("script_register_locale", 0),
                "item_ids": ";".join(row["item_id"] for row in matches),
            }
        )
    return out


def row_by(rows: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
    for row in rows:
        if all(row[key] == value for key, value in kwargs.items()):
            return row
    raise AssertionError(f"missing row for {kwargs}")


def write_markdown(
    path: Path,
    summary_rows: list[dict[str, Any]],
    category_summary: list[dict[str, Any]],
    item_rows: list[dict[str, Any]],
) -> None:
    old_base = row_by(summary_rows, generation="GPT-4.1 family", condition="baseline")
    old_contract = row_by(summary_rows, generation="GPT-4.1 family", condition="contract")
    cur_base = row_by(summary_rows, generation="GPT-5.x family", condition="baseline")
    cur_contract = row_by(summary_rows, generation="GPT-5.x family", condition="contract")
    cat = {row["category"]: row for row in category_summary}
    current_contract_both_fail = [
        row for row in item_rows if row["both_current_models_contract_fail"] == 1
    ]
    lines = [
        "# Generation Progress Probe",
        "",
        "This artifact compares item-level first-turn failures across the saved",
        "GPT-4.1-family and GPT-5.x-family full 120-item runs. It is a progress",
        "probe over one benchmark, not a broad model leaderboard or population-level",
        "claim.",
        "",
        "## Generation Summary",
        "",
        "| Generation | Condition | Model-item pairs | Failure pairs | Any-fail items | All-model fail items | Unresolved pairs |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['generation']} | {row['condition']} | {row['model_item_pairs']} | "
            f"{row['first_turn_failures']} ({row['failure_pair_pct']:.1f}%) | "
            f"{row['any_fail_items']} | {row['all_fail_items']} | {row['unresolved_pairs']} |"
        )

    lines.extend(
        [
            "",
            "## Cross-Generation Item Movement",
            "",
            "| Category | Items | Editing | Output-language | Quote | Script/register/locale |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in category_summary:
        lines.append(
            f"| {row['category']} | {row['item_count']} | {row['editing_preservation']} | "
            f"{row['output_language_inference']} | {row['quote_preservation']} | {row['script_register_locale']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"Under baseline prompting, GPT-4.1-family models fail {old_base['first_turn_failures']}/{old_base['model_item_pairs']} "
            f"model-item pairs ({old_base['failure_pair_pct']:.1f}%), with {old_base['any_fail_items']}/120 items failing for at least one model "
            f"and {old_base['all_fail_items']}/120 failing for all three. GPT-5.x-family baseline runs lower the normalized failure-pair rate to "
            f"{cur_base['first_turn_failures']}/{cur_base['model_item_pairs']} ({cur_base['failure_pair_pct']:.1f}%), with "
            f"{cur_base['any_fail_items']}/120 any-fail items and {cur_base['all_fail_items']}/120 both-model fail items.",
            "",
            f"Under the contract, the GPT-5.x-family failure-pair rate falls to {cur_contract['first_turn_failures']}/{cur_contract['model_item_pairs']} "
            f"({cur_contract['failure_pair_pct']:.1f}%), compared with {old_contract['first_turn_failures']}/{old_contract['model_item_pairs']} "
            f"({old_contract['failure_pair_pct']:.1f}%) for GPT-4.1-family contract rows. The current-family all-model-fail set shrinks to "
            f"{cur_contract['all_fail_items']} items.",
            "",
            f"`gpt-5.5` baseline passes {cat['gpt41_all_baseline_fail_gpt55_baseline_pass']['item_count']} of the "
            f"{cat['gpt41_baseline_all_fail_items']['item_count']} items that all GPT-4.1-family baselines fail, and passes "
            f"{cat['gpt41_any_baseline_fail_gpt55_baseline_pass']['item_count']} of the {cat['gpt41_baseline_any_fail_items']['item_count']} items "
            "where at least one GPT-4.1-family baseline fails.",
            f"With the contract, `gpt-5.5` passes {cat['gpt41_any_baseline_fail_gpt55_contract_pass']['item_count']} of those "
            f"{cat['gpt41_baseline_any_fail_items']['item_count']} older-family baseline-hard items and all "
            f"{cat['gpt41_all_contract_fail_gpt55_contract_pass']['item_count']} items that all GPT-4.1-family contract rows fail.",
            "",
            "The two items that both current models still fail under the contract are "
            + ", ".join(f"`{row['item_id']}`" for row in current_contract_both_fail)
            + ". Both are Spanish-English editing-preservation rows.",
            "This supports the progress-probe framing: the benchmark distinguishes model generations and prompt conditions while retaining a small residual hard set.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/generation_progress_probe_v02"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/generation_progress_probe_v02.md"))
    args = parser.parse_args()

    rows: list[dict[str, str]] = []
    for path in TRAJECTORY_PATHS:
        rows.extend(read_csv(path))

    summary_rows: list[dict[str, Any]] = []
    family_rows: list[dict[str, Any]] = []
    families = sorted({row["task_family"] for row in rows})
    for generation, models in GENERATION_MODELS.items():
        for condition in ["baseline", "contract"]:
            summary_rows.append(summarize_generation_condition(generation, models, condition, rows))
            for family in families:
                family_rows.append(summarize_generation_family(generation, models, condition, family, rows))

    item_rows = item_progress_rows(rows)
    categories = category_rows(item_rows)
    write_csv(args.out_dir / "generation_progress_summary.csv", summary_rows)
    write_csv(args.out_dir / "generation_progress_by_family.csv", family_rows)
    write_csv(args.out_dir / "generation_progress_item_matrix.csv", item_rows)
    write_csv(args.out_dir / "generation_progress_categories.csv", categories)
    write_markdown(args.out_md, summary_rows, categories, item_rows)
    print(f"wrote generation progress probe to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
