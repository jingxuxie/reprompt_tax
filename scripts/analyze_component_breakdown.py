#!/usr/bin/env python
"""Analyze first-turn scorer components for paper-facing RePromptTax outputs."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


COMPONENTS = (
    "language_pass",
    "script_pass",
    "preservation_pass",
    "task_pass",
    "register_locale_pass",
)
COMPONENT_LABELS = {
    "language_pass": "Language",
    "script_pass": "Script",
    "preservation_pass": "Preservation",
    "task_pass": "Task",
    "register_locale_pass": "Register/locale",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON") from exc
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def pct(numerator: int, denominator: int) -> float:
    return round(100.0 * numerator / denominator, 1)


def bool_value(row: dict[str, Any], field: str) -> bool:
    value = row[field]
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return bool(value)


def first_turn_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = [row for row in rows if int(row["turn"]) == 0]
    require(bool(out), "no first-turn rows found")
    for row in out:
        for field in ("item_id", "model", "condition", "task_family", "language_pair", *COMPONENTS):
            require(field in row, f"first-turn row missing {field}")
    return out


def group_summary(rows: list[dict[str, Any]], key_fields: tuple[str, ...]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[tuple(str(row[field]) for field in key_fields)].append(row)

    out: list[dict[str, Any]] = []
    for key, group in sorted(groups.items()):
        summary = {field: value for field, value in zip(key_fields, key)}
        summary["n"] = len(group)
        summary["ftga_pass_n"] = sum(bool_value(row, "pass") for row in group)
        summary["ftga_pass_pct"] = pct(int(summary["ftga_pass_n"]), len(group))
        for component in COMPONENTS:
            pass_n = sum(bool_value(row, component) for row in group)
            summary[f"{component}_n"] = pass_n
            summary[f"{component}_pct"] = pct(pass_n, len(group))
        out.append(summary)
    return out


def paired_effects_by_model(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        by_key[(row["model"], row["item_id"])][row["condition"]] = row

    by_model: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for (model, _item_id), conditions in by_key.items():
        if "baseline" in conditions and "contract" in conditions:
            by_model[model].append((conditions["baseline"], conditions["contract"]))

    out: list[dict[str, Any]] = []
    for model, pairs in sorted(by_model.items()):
        require(len(pairs) == 120, f"expected 120 paired first-turn rows for {model}, found {len(pairs)}")
        for component in ("pass", *COMPONENTS):
            deltas = [
                int(bool_value(contract, component)) - int(bool_value(baseline, component))
                for baseline, contract in pairs
            ]
            out.append(
                {
                    "model": model,
                    "component": "ftga_pass" if component == "pass" else component,
                    "n_pairs": len(pairs),
                    "delta_pp": round(100.0 * sum(deltas) / len(pairs), 1),
                    "improved_n": sum(delta > 0 for delta in deltas),
                    "worsened_n": sum(delta < 0 for delta in deltas),
                    "tied_n": sum(delta == 0 for delta in deltas),
                }
            )
    return out


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"cannot write empty CSV {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def find_row(rows: list[dict[str, Any]], **kwargs: str) -> dict[str, Any]:
    for row in rows:
        if all(row[key] == value for key, value in kwargs.items()):
            return row
    raise AssertionError(f"missing row for {kwargs}")


def write_markdown(
    path: Path,
    model_rows: list[dict[str, Any]],
    family_rows: list[dict[str, Any]],
    paired_rows: list[dict[str, Any]],
) -> None:
    lines = [
        "# Scorer Component Breakdown",
        "",
        "Generated from first-turn rows in",
        "`results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl`.",
        "",
        "Each component is a conservative automatic check. Component pass rates are",
        "not independent human judgments; they show which rule families drive the",
        "automatic first-turn global-alignment score.",
        "",
        "## By Model And Condition",
        "",
        "| Model | Condition | FTGA | Language | Script | Preservation | Task | Register/locale |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in model_rows:
        lines.append(
            "| "
            f"{row['model']} | {row['condition']} | {row['ftga_pass_pct']:.1f}% | "
            f"{row['language_pass_pct']:.1f}% | {row['script_pass_pct']:.1f}% | "
            f"{row['preservation_pass_pct']:.1f}% | {row['task_pass_pct']:.1f}% | "
            f"{row['register_locale_pass_pct']:.1f}% |"
        )

    lines.extend(
        [
            "",
            "## Aggregate By Task Family",
            "",
            "| Condition | Task family | FTGA | Language | Script | Preservation | Task | Register/locale |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in family_rows:
        lines.append(
            "| "
            f"{row['condition']} | {row['task_family']} | {row['ftga_pass_pct']:.1f}% | "
            f"{row['language_pass_pct']:.1f}% | {row['script_pass_pct']:.1f}% | "
            f"{row['preservation_pass_pct']:.1f}% | {row['task_pass_pct']:.1f}% | "
            f"{row['register_locale_pass_pct']:.1f}% |"
        )

    lines.extend(
        [
            "",
            "## Paired Contract Minus Baseline Effects",
            "",
            "| Model | Component | Delta | Improved | Worsened | Tied |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    display_components = ("language_pass", "script_pass", "preservation_pass", "task_pass", "register_locale_pass")
    for row in paired_rows:
        component = row["component"]
        if component not in display_components:
            continue
        label = COMPONENT_LABELS[component]
        lines.append(
            "| "
            f"{row['model']} | {label} | {row['delta_pp']:+.1f} pp | "
            f"{row['improved_n']} | {row['worsened_n']} | {row['tied_n']} |"
        )

    gpt41 = find_row(paired_rows, model="gpt-4.1", component="language_pass")
    nano_task = find_row(paired_rows, model="gpt-4.1-nano", component="task_pass")
    preservation = find_row(paired_rows, model="gpt-4.1-mini", component="preservation_pass")
    family_edit_base = find_row(family_rows, condition="baseline", task_family="editing_preservation")
    family_edit_contract = find_row(family_rows, condition="contract", task_family="editing_preservation")
    family_script_contract = find_row(family_rows, condition="contract", task_family="script_register_locale")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"The largest component-level movement is language alignment: gpt-4.1 gains {gpt41['delta_pp']:+.1f} pp",
            "on paired first-turn language checks under the contract. The contract also",
            f"improves nano task completion by {nano_task['delta_pp']:+.1f} pp.",
            "",
            "At the task-family level, editing-preservation is where component changes",
            f"matter most: language pass rate rises from {family_edit_base['language_pass_pct']:.1f}% to",
            f"{family_edit_contract['language_pass_pct']:.1f}%, and script pass rate rises from",
            f"{family_edit_base['script_pass_pct']:.1f}% to {family_edit_contract['script_pass_pct']:.1f}%.",
            "",
            "The analysis also marks a boundary: preservation pass rates barely move",
            f"for some models (for example, mini preservation delta is {preservation['delta_pp']:+.1f} pp),",
            "and script/register/locale preservation remains below saturation",
            f"({family_script_contract['preservation_pass_pct']:.1f}% under contract). Register/locale checks",
            "are saturated under the current rule set, so they should not be presented",
            "as evidence that nuanced register judgments are solved.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", type=Path, default=Path("results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/openai_three_model_stress_v02_full120"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/component_breakdown_v02_full120.md"))
    args = parser.parse_args()

    rows = first_turn_rows(load_jsonl(args.scores))
    require(len(rows) == 720, f"expected 720 first-turn rows, found {len(rows)}")

    model_rows = group_summary(rows, ("model", "condition"))
    family_rows = group_summary(rows, ("condition", "task_family"))
    language_rows = group_summary(rows, ("condition", "language_pair"))
    paired_rows = paired_effects_by_model(rows)

    write_csv(args.out_dir / "component_pass_by_model_condition.csv", model_rows)
    write_csv(args.out_dir / "component_pass_by_family_condition.csv", family_rows)
    write_csv(args.out_dir / "component_pass_by_language_condition.csv", language_rows)
    write_csv(args.out_dir / "component_paired_effects_by_model.csv", paired_rows)
    write_markdown(args.out_md, model_rows, family_rows, paired_rows)
    print(f"wrote component breakdown to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
