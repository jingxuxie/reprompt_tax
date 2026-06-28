#!/usr/bin/env python
"""Analyze first-turn scorer sensitivity to individual component checks."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
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
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
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


def first_turn_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = [row for row in rows if int(row["turn"]) == 0]
    if len(out) != 720:
        raise ValueError(f"expected 720 first-turn rows, found {len(out)}")
    for row in out:
        for field in ("model", "condition", "task_family", "language_pair", "pass", *COMPONENTS):
            if field not in row:
                raise KeyError(f"first-turn row missing {field}")
    return out


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
        actual_fail_n = n - actual_pass_n
        base = {field: value for field, value in zip(fields, key)}
        base.update(
            {
                "n": n,
                "actual_ftga_n": actual_pass_n,
                "actual_ftga_pct": pct(actual_pass_n, n),
                "actual_fail_n": actual_fail_n,
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


def failure_signature_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[tuple[str, str, str]] = Counter()
    denominators: Counter[tuple[str, str]] = Counter()
    for row in rows:
        if bool_value(row, "pass"):
            continue
        key = (row["condition"], row["task_family"])
        denominators[key] += 1
        counts[(row["condition"], row["task_family"], failure_signature(row))] += 1

    out: list[dict[str, Any]] = []
    for (condition, family, signature), count in sorted(counts.items()):
        denom = denominators[(condition, family)]
        out.append(
            {
                "condition": condition,
                "task_family": family,
                "failure_signature": signature,
                "count": count,
                "share_of_first_turn_failures": round(count / denom, 3) if denom else "",
            }
        )
    return out


def top_signature_rows(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    signatures = failure_signature_rows(rows)
    signatures.sort(
        key=lambda row: (
            row["condition"],
            row["task_family"],
            -int(row["count"]),
            row["failure_signature"],
        )
    )
    out: list[dict[str, Any]] = []
    seen: Counter[tuple[str, str]] = Counter()
    for row in signatures:
        key = (row["condition"], row["task_family"])
        if seen[key] >= limit:
            continue
        seen[key] += 1
        out.append(row)
    return out


def write_markdown(
    path: Path,
    *,
    score_path: Path,
    overall_rows: list[dict[str, Any]],
    family_rows: list[dict[str, Any]],
    top_signatures: list[dict[str, Any]],
) -> None:
    by_condition = {row["condition"]: row for row in overall_rows}
    baseline = by_condition["baseline"]
    contract = by_condition["contract"]

    lines = [
        "# Scorer-Ablation Sensitivity",
        "",
        f"Generated from first-turn rows in `{score_path}`.",
        "Each counterfactual relaxes exactly one automatic component while keeping",
        "all other components fixed. This is a scorer-sensitivity diagnostic, not a",
        "replacement for human validation.",
        "",
        "## Overall Component Relaxation",
        "",
        "| Condition | Actual FTGA | Relax language | Relax script | Relax preservation | Relax task | Relax register/locale |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in overall_rows:
        lines.append(
            "| "
            f"{row['condition']} | {row['actual_ftga_pct']:.1f}% | "
            f"{row['relax_language_ftga_pct']:.1f}% (+{row['relax_language_delta_pp']:.1f}) | "
            f"{row['relax_script_ftga_pct']:.1f}% (+{row['relax_script_delta_pp']:.1f}) | "
            f"{row['relax_preservation_ftga_pct']:.1f}% (+{row['relax_preservation_delta_pp']:.1f}) | "
            f"{row['relax_task_ftga_pct']:.1f}% (+{row['relax_task_delta_pp']:.1f}) | "
            f"{row['relax_register_locale_ftga_pct']:.1f}% (+{row['relax_register_locale_delta_pp']:.1f}) |"
        )

    lines.extend(
        [
            "",
            "## Family-Level Binding Checks",
            "",
            "| Condition | Task family | Actual FTGA | Relax language delta | Relax preservation delta | Relax task delta | Top sole blocker counts |",
            "|---|---|---:|---:|---:|---:|---|",
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
            "| "
            f"{row['condition']} | {FAMILY_LABELS.get(row['task_family'], row['task_family'])} | "
            f"{row['actual_ftga_pct']:.1f}% | "
            f"{row['relax_language_delta_pp']:+.1f} pp | "
            f"{row['relax_preservation_delta_pp']:+.1f} pp | "
            f"{row['relax_task_delta_pp']:+.1f} pp | "
            f"{top or 'none'} |"
        )

    lines.extend(
        [
            "",
            "## Dominant Failure Signatures",
            "",
            "| Condition | Task family | Failed components | Count | Share of first-turn failures |",
            "|---|---|---|---:|---:|",
        ]
    )
    for row in top_signatures:
        lines.append(
            "| "
            f"{row['condition']} | {FAMILY_LABELS.get(row['task_family'], row['task_family'])} | "
            f"{row['failure_signature']} | {row['count']} | "
            f"{100 * float(row['share_of_first_turn_failures']):.1f}% |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Relaxing a single component produces only bounded changes because many",
            "first-turn failures violate multiple automatic checks at once. In baseline",
            f"rows, relaxing language alone would move FTGA from {baseline['actual_ftga_pct']:.1f}% to",
            f"{baseline['relax_language_ftga_pct']:.1f}%; relaxing task alone would move it to",
            f"{baseline['relax_task_ftga_pct']:.1f}%. Under the contract, the corresponding",
            f"counterfactuals are {contract['relax_language_ftga_pct']:.1f}% and",
            f"{contract['relax_task_ftga_pct']:.1f}%.",
            "",
            "The main scorer boundary is therefore not a single fragile rule. Editing",
            "failures often combine language, script, and task violations; preservation",
            "and script/register/locale failures remain distinct residual checks. This",
            "supports reporting the automatic scorer as a conservative diagnostic while",
            "keeping native/near-native human validation as the stronger claim gate.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", type=Path, default=Path("results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/openai_three_model_stress_v02_full120"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/scorer_ablation_sensitivity_v02_full120.md"))
    parser.add_argument("--signature-limit", type=int, default=2)
    args = parser.parse_args()

    rows = first_turn_rows(load_jsonl(args.scores))
    overall_rows = ablation_summary(rows, ("condition",))
    model_rows = ablation_summary(rows, ("model", "condition"))
    family_rows = ablation_summary(rows, ("condition", "task_family"))
    signatures = failure_signature_rows(rows)
    top_signatures = top_signature_rows(rows, args.signature_limit)

    write_csv(args.out_dir / "scorer_ablation_by_condition.csv", overall_rows)
    write_csv(args.out_dir / "scorer_ablation_by_model_condition.csv", model_rows)
    write_csv(args.out_dir / "scorer_ablation_by_family_condition.csv", family_rows)
    write_csv(args.out_dir / "scorer_ablation_failure_signatures.csv", signatures)
    write_csv(args.out_dir / "scorer_ablation_top_failure_signatures.csv", top_signatures)
    write_markdown(
        args.out_md,
        score_path=args.scores,
        overall_rows=overall_rows,
        family_rows=family_rows,
        top_signatures=top_signatures,
    )
    print(f"wrote scorer-ablation sensitivity analysis to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
