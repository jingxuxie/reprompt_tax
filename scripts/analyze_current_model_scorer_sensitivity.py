#!/usr/bin/env python
"""Analyze current-model first-turn scorer sensitivity to component checks."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SCORE_PATHS = [
    Path("results/scores/openai_gpt54mini_stress_v02_full120_auto_scores.jsonl"),
    Path("results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl"),
]
OUT_DIR = Path("results/tables/current_model_scorer_sensitivity_v02")
OUT_MD = Path("paper/current_model_scorer_sensitivity_v02.md")

COMPONENTS = (
    "language_pass",
    "script_pass",
    "preservation_pass",
    "task_pass",
    "register_locale_pass",
)
COMPONENT_LABELS = {
    "language_pass": "language",
    "script_pass": "script",
    "preservation_pass": "preservation",
    "task_pass": "task",
    "register_locale_pass": "register_locale",
}
FAMILY_LABELS = {
    "editing_preservation": "Editing preservation",
    "output_language_inference": "Output-language inference",
    "quote_preservation": "Quote preservation",
    "script_register_locale": "Script/register/locale",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


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


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def bool_value(row: dict[str, Any], field: str) -> bool:
    value = row[field]
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value)


def pct(numerator: int, denominator: int) -> float:
    return round(100.0 * numerator / denominator, 1) if denominator else 0.0


def first_turn_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        rows.extend(row for row in load_jsonl(path) if int(row["turn"]) == 0)
    require(len(rows) == 480, f"expected 480 current-model first-turn rows, found {len(rows)}")
    for row in rows:
        for field in ("item_id", "model", "condition", "task_family", "language_pair", "pass", *COMPONENTS):
            require(field in row, f"first-turn row missing {field}")
    return rows


def passes_without(row: dict[str, Any], relaxed_component: str) -> bool:
    return all(bool_value(row, component) for component in COMPONENTS if component != relaxed_component)


def group_rows(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> dict[tuple[str, ...], list[dict[str, Any]]]:
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[tuple(str(row[field]) for field in fields)].append(row)
    return groups


def ablation_summary(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for key, group in sorted(group_rows(rows, fields).items()):
        n = len(group)
        actual_pass_n = sum(bool_value(row, "pass") for row in group)
        base = {field: value for field, value in zip(fields, key)}
        base.update(
            {
                "n": n,
                "actual_ftga_n": actual_pass_n,
                "actual_ftga_pct": pct(actual_pass_n, n),
                "actual_fail_n": n - actual_pass_n,
            }
        )
        for component in COMPONENTS:
            relaxed_n = sum(passes_without(row, component) for row in group)
            sole_blocker_n = sum(
                (not bool_value(row, "pass"))
                and (not bool_value(row, component))
                and passes_without(row, component)
                for row in group
            )
            label = COMPONENT_LABELS[component]
            base[f"relax_{label}_ftga_n"] = relaxed_n
            base[f"relax_{label}_ftga_pct"] = pct(relaxed_n, n)
            base[f"relax_{label}_delta_pp"] = round(pct(relaxed_n, n) - pct(actual_pass_n, n), 1)
            base[f"sole_{label}_blocker_n"] = sole_blocker_n
        out.append(base)
    return out


def failure_signature(row: dict[str, Any]) -> str:
    failed = [COMPONENT_LABELS[component] for component in COMPONENTS if not bool_value(row, component)]
    return "+".join(failed) if failed else "none"


def failure_signature_rows(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> list[dict[str, Any]]:
    counts: Counter[tuple[str, ...]] = Counter()
    denominators: Counter[tuple[str, ...]] = Counter()
    for row in rows:
        if bool_value(row, "pass"):
            continue
        group_key = tuple(str(row[field]) for field in fields)
        denominators[group_key] += 1
        counts[(*group_key, failure_signature(row))] += 1

    out: list[dict[str, Any]] = []
    for key, count in sorted(counts.items()):
        group_key = key[:-1]
        signature = key[-1]
        denom = denominators[group_key]
        base = {field: value for field, value in zip(fields, group_key)}
        base.update(
            {
                "failure_signature": signature,
                "count": count,
                "share_of_first_turn_failures": round(count / denom, 3) if denom else "",
            }
        )
        out.append(base)
    return out


def top_signature_rows(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    signatures = failure_signature_rows(rows, ("model", "condition", "task_family"))
    signatures.sort(
        key=lambda row: (
            row["model"],
            row["condition"],
            row["task_family"],
            -int(row["count"]),
            row["failure_signature"],
        )
    )
    out: list[dict[str, Any]] = []
    seen: Counter[tuple[str, str, str]] = Counter()
    for row in signatures:
        key = (row["model"], row["condition"], row["task_family"])
        if seen[key] >= limit:
            continue
        seen[key] += 1
        out.append(row)
    return out


def row_by(rows: list[dict[str, Any]], **kwargs: str) -> dict[str, Any]:
    for row in rows:
        if all(str(row[key]) == value for key, value in kwargs.items()):
            return row
    raise AssertionError(f"missing row for {kwargs}")


def write_markdown(
    path: Path,
    *,
    overall_rows: list[dict[str, Any]],
    model_rows: list[dict[str, Any]],
    family_rows: list[dict[str, Any]],
    top_signatures: list[dict[str, Any]],
) -> None:
    g55_base = row_by(model_rows, model="gpt-5.5", condition="baseline")
    g55_contract = row_by(model_rows, model="gpt-5.5", condition="contract")
    g54_contract = row_by(model_rows, model="gpt-5.4-mini", condition="contract")
    lines = [
        "# Current-Model Scorer Sensitivity",
        "",
        "This diagnostic combines the saved full-120 `gpt-5.4-mini` and `gpt-5.5`",
        "score logs. Each counterfactual relaxes exactly one automatic component",
        "on first-turn rows while keeping all other components fixed. It makes no",
        "new API calls and does not replace native/near-native validation.",
        "",
        "## Overall Component Relaxation",
        "",
        "| Condition | Actual FTGA | Relax language | Relax script | Relax preservation | Relax task | Relax register/locale |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in overall_rows:
        lines.append(
            f"| {row['condition']} | {row['actual_ftga_pct']:.1f}% | "
            f"{row['relax_language_ftga_pct']:.1f}% ({row['relax_language_delta_pp']:+.1f}) | "
            f"{row['relax_script_ftga_pct']:.1f}% ({row['relax_script_delta_pp']:+.1f}) | "
            f"{row['relax_preservation_ftga_pct']:.1f}% ({row['relax_preservation_delta_pp']:+.1f}) | "
            f"{row['relax_task_ftga_pct']:.1f}% ({row['relax_task_delta_pp']:+.1f}) | "
            f"{row['relax_register_locale_ftga_pct']:.1f}% ({row['relax_register_locale_delta_pp']:+.1f}) |"
        )
    lines.extend(
        [
            "",
            "## By Model And Condition",
            "",
            "| Model | Condition | Actual FTGA | Relax language | Relax preservation | Relax task | Sole language blockers | Sole preservation blockers |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in model_rows:
        lines.append(
            f"| {row['model']} | {row['condition']} | {row['actual_ftga_pct']:.1f}% | "
            f"{row['relax_language_ftga_pct']:.1f}% ({row['relax_language_delta_pp']:+.1f}) | "
            f"{row['relax_preservation_ftga_pct']:.1f}% ({row['relax_preservation_delta_pp']:+.1f}) | "
            f"{row['relax_task_ftga_pct']:.1f}% ({row['relax_task_delta_pp']:+.1f}) | "
            f"{row['sole_language_blocker_n']} | {row['sole_preservation_blocker_n']} |"
        )
    lines.extend(
        [
            "",
            "## Family-Level Binding Checks",
            "",
            "| Model | Condition | Task family | Actual FTGA | Relax language delta | Relax preservation delta | Top sole blockers |",
            "|---|---|---|---:|---:|---:|---|",
        ]
    )
    for row in family_rows:
        sole_counts = [
            ("language", row["sole_language_blocker_n"]),
            ("script", row["sole_script_blocker_n"]),
            ("preservation", row["sole_preservation_blocker_n"]),
            ("task", row["sole_task_blocker_n"]),
            ("register_locale", row["sole_register_locale_blocker_n"]),
        ]
        top = "; ".join(f"{name}:{count}" for name, count in sole_counts if count)
        lines.append(
            f"| {row['model']} | {row['condition']} | {FAMILY_LABELS.get(row['task_family'], row['task_family'])} | "
            f"{row['actual_ftga_pct']:.1f}% | {row['relax_language_delta_pp']:+.1f} pp | "
            f"{row['relax_preservation_delta_pp']:+.1f} pp | {top or 'none'} |"
        )
    lines.extend(
        [
            "",
            "## Dominant Failure Signatures",
            "",
            "| Model | Condition | Task family | Failed components | Count | Share of first-turn failures |",
            "|---|---|---|---|---:|---:|",
        ]
    )
    for row in top_signatures:
        lines.append(
            f"| {row['model']} | {row['condition']} | {FAMILY_LABELS.get(row['task_family'], row['task_family'])} | "
            f"{row['failure_signature']} | {row['count']} | "
            f"{100 * float(row['share_of_first_turn_failures']):.1f}% |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"For `gpt-5.5` baseline, relaxing language alone moves FTGA from {g55_base['actual_ftga_pct']:.1f}% to {g55_base['relax_language_ftga_pct']:.1f}%,",
            f"consistent with wrapper/output-language failures. Under the contract, `gpt-5.5` is already near ceiling: relaxing language moves",
            f"FTGA from {g55_contract['actual_ftga_pct']:.1f}% to {g55_contract['relax_language_ftga_pct']:.1f}%.",
            "",
            f"For `gpt-5.4-mini` contract, relaxing preservation moves FTGA from {g54_contract['actual_ftga_pct']:.1f}% to {g54_contract['relax_preservation_ftga_pct']:.1f}%,",
            "which isolates the lower-cost model's residual literal-preservation boundary.",
            "",
            "The current-model headline is therefore not an artifact of a single fragile",
            "component: the flagship result is dominated by output-language wrapper",
            "failures under baseline, while the low-cost residual set includes distinct",
            "preservation failures that remain after the contract.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    parser.add_argument("--signature-limit", type=int, default=2)
    args = parser.parse_args()

    rows = first_turn_rows(SCORE_PATHS)
    overall_rows = ablation_summary(rows, ("condition",))
    model_rows = ablation_summary(rows, ("model", "condition"))
    family_rows = ablation_summary(rows, ("model", "condition", "task_family"))
    signatures = failure_signature_rows(rows, ("model", "condition", "task_family"))
    top_signatures = top_signature_rows(rows, args.signature_limit)

    write_csv(args.out_dir / "current_model_scorer_sensitivity_by_condition.csv", overall_rows)
    write_csv(args.out_dir / "current_model_scorer_sensitivity_by_model_condition.csv", model_rows)
    write_csv(args.out_dir / "current_model_scorer_sensitivity_by_model_family_condition.csv", family_rows)
    write_csv(args.out_dir / "current_model_scorer_sensitivity_failure_signatures.csv", signatures)
    write_csv(args.out_dir / "current_model_scorer_sensitivity_top_failure_signatures.csv", top_signatures)
    write_markdown(
        args.out_md,
        overall_rows=overall_rows,
        model_rows=model_rows,
        family_rows=family_rows,
        top_signatures=top_signatures,
    )
    print(f"wrote current-model scorer sensitivity to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
