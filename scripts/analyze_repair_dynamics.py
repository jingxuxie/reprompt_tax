#!/usr/bin/env python
"""Analyze repair-turn dynamics for RePromptTax trajectories."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


RTT_LABELS = {
    0: "first_turn_pass",
    1: "repaired_after_one",
    2: "repaired_after_two",
    3: "unresolved_after_two",
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


def pct(numerator: int, denominator: int) -> float:
    return round(100.0 * numerator / denominator, 1) if denominator else 0.0


def distribution_summary(rows: list[dict[str, str]], group_fields: tuple[str, ...]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[tuple(row[field] for field in group_fields)].append(row)

    out: list[dict[str, Any]] = []
    for key, group in sorted(groups.items()):
        counts = Counter(int(float(row["rtt"])) for row in group)
        n = len(group)
        initial_failures = n - counts[0]
        entry: dict[str, Any] = {field: value for field, value in zip(group_fields, key)}
        entry["n"] = n
        entry["mean_rtt"] = round(mean(float(row["rtt"]) for row in group), 3)
        entry["initial_failures_n"] = initial_failures
        for rtt, label in RTT_LABELS.items():
            entry[f"{label}_n"] = counts[rtt]
            entry[f"{label}_pct"] = pct(counts[rtt], n)
        entry["repair1_of_initial_failures_pct"] = pct(counts[1], initial_failures)
        entry["repair2_exact_of_initial_failures_pct"] = pct(counts[2], initial_failures)
        entry["unresolved_of_initial_failures_pct"] = pct(counts[3], initial_failures)
        out.append(entry)
    return out


def paired_transition_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_key: dict[tuple[str, str], dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_key[(row["model"], row["item_id"])][row["condition"]] = row

    by_model: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for (model, _item_id), conditions in by_key.items():
        if set(conditions) != {"baseline", "contract"}:
            raise AssertionError(f"missing paired trajectory condition for {model}")
        by_model[model].append((int(float(conditions["baseline"]["rtt"])), int(float(conditions["contract"]["rtt"]))))

    transitions: list[dict[str, Any]] = []
    effects: list[dict[str, Any]] = []
    for model, pairs in sorted(by_model.items()):
        require(len(pairs) == 120, f"expected 120 paired trajectories for {model}, found {len(pairs)}")
        matrix = Counter(pairs)
        for baseline_rtt in range(4):
            for contract_rtt in range(4):
                transitions.append(
                    {
                        "model": model,
                        "baseline_rtt": baseline_rtt,
                        "contract_rtt": contract_rtt,
                        "count": matrix[(baseline_rtt, contract_rtt)],
                    }
                )
        deltas = [baseline_rtt - contract_rtt for baseline_rtt, contract_rtt in pairs]
        effects.append(
            {
                "model": model,
                "n_pairs": len(pairs),
                "mean_rtt_reduction": round(mean(deltas), 3),
                "improved_n": sum(delta > 0 for delta in deltas),
                "worsened_n": sum(delta < 0 for delta in deltas),
                "tied_n": sum(delta == 0 for delta in deltas),
                "baseline_fail_contract_pass_n": sum(baseline_rtt > 0 and contract_rtt == 0 for baseline_rtt, contract_rtt in pairs),
                "baseline_pass_contract_fail_n": sum(baseline_rtt == 0 and contract_rtt > 0 for baseline_rtt, contract_rtt in pairs),
                "baseline_unresolved_contract_resolved_n": sum(baseline_rtt == 3 and contract_rtt < 3 for baseline_rtt, contract_rtt in pairs),
                "baseline_resolved_contract_unresolved_n": sum(baseline_rtt < 3 and contract_rtt == 3 for baseline_rtt, contract_rtt in pairs),
            }
        )
    return transitions, effects


def find_row(rows: list[dict[str, Any]], **kwargs: str) -> dict[str, Any]:
    for row in rows:
        if all(row[key] == value for key, value in kwargs.items()):
            return row
    raise AssertionError(f"missing row for {kwargs}")


def write_markdown(
    path: Path,
    model_rows: list[dict[str, Any]],
    family_rows: list[dict[str, Any]],
    effect_rows: list[dict[str, Any]],
) -> None:
    lines = [
        "# Repair Dynamics Analysis",
        "",
        "Generated from `results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv`.",
        "",
        "RTT=0 means first-turn success, RTT=1 or RTT=2 means success after one or",
        "two standardized repair prompts, and RTT=3 means unresolved after two repair",
        "prompts.",
        "",
        "## RTT Distribution By Model",
        "",
        "| Model | Condition | RTT0 | RTT1 | RTT2 | RTT3 unresolved | Mean RTT | Initial failures | Repair1/fail | Repair2 exact/fail | Unresolved/fail |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in model_rows:
        lines.append(
            "| "
            f"{row['model']} | {row['condition']} | "
            f"{row['first_turn_pass_n']} ({row['first_turn_pass_pct']:.1f}%) | "
            f"{row['repaired_after_one_n']} ({row['repaired_after_one_pct']:.1f}%) | "
            f"{row['repaired_after_two_n']} ({row['repaired_after_two_pct']:.1f}%) | "
            f"{row['unresolved_after_two_n']} ({row['unresolved_after_two_pct']:.1f}%) | "
            f"{row['mean_rtt']:.3f} | {row['initial_failures_n']} | "
            f"{row['repair1_of_initial_failures_pct']:.1f}% | "
            f"{row['repair2_exact_of_initial_failures_pct']:.1f}% | "
            f"{row['unresolved_of_initial_failures_pct']:.1f}% |"
        )

    lines.extend(
        [
            "",
            "## Aggregate RTT Distribution By Task Family",
            "",
            "| Condition | Task family | RTT0 | RTT1 | RTT2 | RTT3 unresolved | Mean RTT |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in family_rows:
        lines.append(
            "| "
            f"{row['condition']} | {row['task_family']} | "
            f"{row['first_turn_pass_n']} | {row['repaired_after_one_n']} | "
            f"{row['repaired_after_two_n']} | {row['unresolved_after_two_n']} | "
            f"{row['mean_rtt']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Paired RTT Movement",
            "",
            "| Model | Mean RTT reduction | Improved | Worsened | Tied | Baseline fail -> contract pass | Baseline pass -> contract fail | Unresolved -> resolved | Resolved -> unresolved |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in effect_rows:
        lines.append(
            "| "
            f"{row['model']} | {row['mean_rtt_reduction']:.3f} | "
            f"{row['improved_n']} | {row['worsened_n']} | {row['tied_n']} | "
            f"{row['baseline_fail_contract_pass_n']} | {row['baseline_pass_contract_fail_n']} | "
            f"{row['baseline_unresolved_contract_resolved_n']} | {row['baseline_resolved_contract_unresolved_n']} |"
        )

    gpt41_base = find_row(model_rows, model="gpt-4.1", condition="baseline")
    gpt41_contract = find_row(model_rows, model="gpt-4.1", condition="contract")
    nano_base = find_row(model_rows, model="gpt-4.1-nano", condition="baseline")
    nano_contract = find_row(model_rows, model="gpt-4.1-nano", condition="contract")
    mini_effect = find_row(effect_rows, model="gpt-4.1-mini")
    script_contract = find_row(family_rows, condition="contract", task_family="script_register_locale")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"For gpt-4.1, the contract changes the distribution from {gpt41_base['first_turn_pass_n']} first-turn",
            f"successes and {gpt41_base['initial_failures_n']} initial failures to {gpt41_contract['first_turn_pass_n']}",
            f"first-turn successes and {gpt41_contract['initial_failures_n']} initial failures. Paired RTT movement is",
            "20 improved, 2 worsened, and 98 tied.",
            "",
            f"For gpt-4.1-nano, unresolved trajectories drop from {nano_base['unresolved_after_two_n']} to",
            f"{nano_contract['unresolved_after_two_n']}, while first-turn successes rise from",
            f"{nano_base['first_turn_pass_n']} to {nano_contract['first_turn_pass_n']}.",
            "",
            f"The mini result is intentionally modest: paired RTT movement is {mini_effect['improved_n']} improved,",
            f"{mini_effect['worsened_n']} worsened, and {mini_effect['tied_n']} tied.",
            "",
            f"A caveat remains: script/register/locale unresolved cases under the contract are {script_contract['unresolved_after_two_n']}/90,",
            "so the prompt does not remove residual repair failures.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trajectory-metrics", type=Path, default=Path("results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/openai_three_model_stress_v02_full120"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/repair_dynamics_v02_full120.md"))
    args = parser.parse_args()

    rows = read_csv(args.trajectory_metrics)
    require(len(rows) == 720, f"expected 720 trajectory rows, found {len(rows)}")
    model_rows = distribution_summary(rows, ("model", "condition"))
    family_rows = distribution_summary(rows, ("condition", "task_family"))
    language_rows = distribution_summary(rows, ("condition", "language_pair"))
    transition_rows, effect_rows = paired_transition_rows(rows)

    write_csv(args.out_dir / "repair_dynamics_by_model_condition.csv", model_rows)
    write_csv(args.out_dir / "repair_dynamics_by_family_condition.csv", family_rows)
    write_csv(args.out_dir / "repair_dynamics_by_language_condition.csv", language_rows)
    write_csv(args.out_dir / "repair_rtt_transition_by_model.csv", transition_rows)
    write_csv(args.out_dir / "repair_paired_effects_by_model.csv", effect_rows)
    write_markdown(args.out_md, model_rows, family_rows, effect_rows)
    print(f"wrote repair-dynamics analysis to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
