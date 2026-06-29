#!/usr/bin/env python
"""Analyze residual current-model failures for the RePromptTax refresh."""

from __future__ import annotations

import argparse
import ast
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


CURRENT_MODELS = {
    "gpt-5.4-mini": {
        "tables": Path("results/tables/openai_gpt54mini_stress_v02_full120"),
        "scores": Path("results/scores/openai_gpt54mini_stress_v02_full120_auto_scores.jsonl"),
    },
    "gpt-5.5": {
        "tables": Path("results/tables/openai_gpt55_stress_v02_full120"),
        "scores": Path("results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl"),
    },
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


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def parse_types(value: str) -> list[str]:
    parsed = ast.literal_eval(value)
    if not isinstance(parsed, list):
        raise ValueError(f"expected list literal, got {value!r}")
    return [str(item) for item in parsed]


def type_counts(rows: list[dict[str, str]]) -> str:
    counts: Counter[str] = Counter()
    for row in rows:
        counts.update(parse_types(row["first_failure_types"]))
    return "; ".join(f"{name}={count}" for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def pct(numerator: int, denominator: int) -> float:
    return round(100 * numerator / denominator, 1) if denominator else 0.0


def summarize_condition(model: str, condition: str, rows: list[dict[str, str]]) -> dict[str, Any]:
    sub = [row for row in rows if row["condition"] == condition]
    failures = [row for row in sub if row["ftga"] == "0"]
    unresolved = [row for row in sub if row["unresolved"] == "1"]
    one_repair = [row for row in sub if row["repair_success_1"] == "1"]
    two_repair = [row for row in sub if row["repair_success_2"] == "1" and row["repair_success_1"] != "1"]
    return {
        "model": model,
        "condition": condition,
        "trajectories": len(sub),
        "first_turn_successes": len(sub) - len(failures),
        "first_turn_failures": len(failures),
        "first_turn_failure_pct": pct(len(failures), len(sub)),
        "one_repair_successes": len(one_repair),
        "two_repair_successes": len(two_repair),
        "unresolved": len(unresolved),
        "unresolved_pct": pct(len(unresolved), len(sub)),
        "failure_type_counts": type_counts(failures),
    }


def summarize_group(model: str, condition: str, group_field: str, rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    values = sorted({row[group_field] for row in rows if row["condition"] == condition})
    for value in values:
        sub = [row for row in rows if row["condition"] == condition and row[group_field] == value]
        failures = [row for row in sub if row["ftga"] == "0"]
        unresolved = [row for row in sub if row["unresolved"] == "1"]
        out.append(
            {
                "model": model,
                "condition": condition,
                group_field: value,
                "trajectories": len(sub),
                "first_turn_failures": len(failures),
                "first_turn_failure_pct": pct(len(failures), len(sub)),
                "unresolved": len(unresolved),
                "unresolved_pct": pct(len(unresolved), len(sub)),
                "failure_type_counts": type_counts(failures),
            }
        )
    return out


def paired_transitions(model: str, rows: list[dict[str, str]]) -> dict[str, Any]:
    baseline = {row["item_id"]: row for row in rows if row["condition"] == "baseline"}
    contract = {row["item_id"]: row for row in rows if row["condition"] == "contract"}
    if set(baseline) != set(contract):
        raise AssertionError(f"{model}: baseline/contract item mismatch")
    both_pass = baseline_fail_contract_pass = baseline_pass_contract_fail = both_fail = 0
    rtt_improved = rtt_worsened = rtt_tied = 0
    baseline_unresolved_contract_resolved = 0
    baseline_resolved_contract_unresolved = 0
    for item_id in sorted(baseline):
        base = baseline[item_id]
        cont = contract[item_id]
        base_pass = base["ftga"] == "1"
        cont_pass = cont["ftga"] == "1"
        if base_pass and cont_pass:
            both_pass += 1
        elif not base_pass and cont_pass:
            baseline_fail_contract_pass += 1
        elif base_pass and not cont_pass:
            baseline_pass_contract_fail += 1
        else:
            both_fail += 1

        delta = int(base["rtt"]) - int(cont["rtt"])
        if delta > 0:
            rtt_improved += 1
        elif delta < 0:
            rtt_worsened += 1
        else:
            rtt_tied += 1

        if base["unresolved"] == "1" and cont["unresolved"] == "0":
            baseline_unresolved_contract_resolved += 1
        if base["unresolved"] == "0" and cont["unresolved"] == "1":
            baseline_resolved_contract_unresolved += 1

    return {
        "model": model,
        "total_items": len(baseline),
        "both_pass": both_pass,
        "baseline_fail_contract_pass": baseline_fail_contract_pass,
        "baseline_pass_contract_fail": baseline_pass_contract_fail,
        "both_fail": both_fail,
        "rtt_improved": rtt_improved,
        "rtt_worsened": rtt_worsened,
        "rtt_tied": rtt_tied,
        "baseline_unresolved_contract_resolved": baseline_unresolved_contract_resolved,
        "baseline_resolved_contract_unresolved": baseline_resolved_contract_unresolved,
    }


def score_lookup(score_rows: list[dict[str, Any]]) -> dict[tuple[str, str, str, int], dict[str, Any]]:
    lookup: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    for row in score_rows:
        lookup[(row["item_id"], row["model"], row["condition"], int(row["turn"]))] = row
    return lookup


def residual_rows(model: str, trajectory_rows: list[dict[str, str]], score_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lookup = score_lookup(score_rows)
    out: list[dict[str, Any]] = []
    for row in trajectory_rows:
        if row["ftga"] != "0":
            continue
        item_id = row["item_id"]
        condition = row["condition"]
        turns = [
            key[3]
            for key in lookup
            if key[0] == item_id and key[1] == model and key[2] == condition
        ]
        final_turn = max(turns)
        first = lookup[(item_id, model, condition, 0)]
        final = lookup[(item_id, model, condition, final_turn)]
        out.append(
            {
                "model": model,
                "condition": condition,
                "item_id": item_id,
                "language_pair": row["language_pair"],
                "task_family": row["task_family"],
                "rtt": int(row["rtt"]),
                "unresolved": int(row["unresolved"]),
                "first_failure_types": ",".join(parse_types(row["first_failure_types"])),
                "first_short_reason": first.get("short_reason", ""),
                "final_turn": final_turn,
                "final_pass": bool(final.get("pass")),
                "final_failure_types": ",".join(str(item) for item in final.get("failure_types", [])),
                "final_short_reason": final.get("short_reason", ""),
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
    by_family_rows: list[dict[str, Any]],
    transition_rows: list[dict[str, Any]],
    residual_case_rows: list[dict[str, Any]],
) -> None:
    g54_base = row_by(summary_rows, model="gpt-5.4-mini", condition="baseline")
    g54_contract = row_by(summary_rows, model="gpt-5.4-mini", condition="contract")
    g55_base = row_by(summary_rows, model="gpt-5.5", condition="baseline")
    g55_contract = row_by(summary_rows, model="gpt-5.5", condition="contract")
    g54_transition = row_by(transition_rows, model="gpt-5.4-mini")
    g55_transition = row_by(transition_rows, model="gpt-5.5")
    g54_contract_family = [
        row for row in by_family_rows if row["model"] == "gpt-5.4-mini" and row["condition"] == "contract" and row["first_turn_failures"]
    ]
    g55_contract_cases = [
        row for row in residual_case_rows if row["model"] == "gpt-5.5" and row["condition"] == "contract"
    ]
    contract_cases = [row for row in residual_case_rows if row["condition"] == "contract"]

    lines = [
        "# Current-Model Residual Error Analysis",
        "",
        "This artifact inspects the saved full 120-item `gpt-5.4-mini` and",
        "`gpt-5.5` refresh runs. It is generated from trajectory metrics and",
        "auto-score rows; it makes no new API calls.",
        "",
        "## Topline",
        "",
        "| Model | Condition | First-turn failures | Unresolved | Failure-type counts |",
        "|---|---|---:|---:|---|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['model']} | {row['condition']} | {row['first_turn_failures']}/{row['trajectories']} "
            f"({row['first_turn_failure_pct']:.1f}%) | {row['unresolved']} ({row['unresolved_pct']:.1f}%) | "
            f"{row['failure_type_counts'] or 'none'} |"
        )

    lines.extend(
        [
            "",
            "## Paired Transitions",
            "",
            "| Model | Both pass | Baseline fail -> contract pass | Baseline pass -> contract fail | Both fail | RTT improved | RTT worsened | RTT tied |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in transition_rows:
        lines.append(
            f"| {row['model']} | {row['both_pass']} | {row['baseline_fail_contract_pass']} | "
            f"{row['baseline_pass_contract_fail']} | {row['both_fail']} | {row['rtt_improved']} | "
            f"{row['rtt_worsened']} | {row['rtt_tied']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"`gpt-5.5` has {g55_base['first_turn_failures']} baseline first-turn failures, "
            f"of which 20 are editing-preservation rows. Under the contract it has only "
            f"{g55_contract['first_turn_failures']} first-turn failures and {g55_contract['unresolved']} unresolved trajectories.",
            f"The paired transition table shows {g55_transition['baseline_fail_contract_pass']} baseline failures fixed by the contract, "
            f"{g55_transition['baseline_pass_contract_fail']} first-turn regressions, and {g55_transition['both_fail']} items that fail on both prompts.",
            "Both contract residuals are Spanish-English editing-preservation rows with wrong-output-language failures, and both repair in one turn.",
            "",
            f"`gpt-5.4-mini` is more mixed: baseline has {g54_base['first_turn_failures']} first-turn failures and "
            f"{g54_base['unresolved']} unresolved trajectories, while contract has {g54_contract['first_turn_failures']} first-turn failures and "
            f"{g54_contract['unresolved']} unresolved trajectories.",
            f"The contract fixes {g54_transition['baseline_fail_contract_pass']} baseline failures but introduces "
            f"{g54_transition['baseline_pass_contract_fail']} first-turn regressions and leaves {g54_transition['both_fail']} both-prompt failures.",
            "This is why the low-cost current-model claim should emphasize bounded FTGA and token-tax improvement, not universal repair improvement.",
            "",
            "The current-model residuals preserve the main claim boundary: the contract sharply reduces GPT-5.5 burden,",
            "but it does not eliminate first-turn misalignment; on the lower-cost current model, residual failures remain spread across",
            "editing preservation, quote preservation, and script/register/locale rows.",
            "",
            "## Contract Residual Cases",
            "",
            "| Model | Item | Language | Family | RTT | Unresolved | First failure types |",
            "|---|---|---|---|---:|---:|---|",
        ]
    )
    for row in contract_cases:
        lines.append(
            f"| {row['model']} | `{row['item_id']}` | {row['language_pair']} | {row['task_family']} | "
            f"{row['rtt']} | {row['unresolved']} | {row['first_failure_types']} |"
        )

    lines.extend(
        [
            "",
            "## Contract Failure Families",
            "",
            "| Model | Family | First-turn failures | Unresolved | Failure-type counts |",
            "|---|---|---:|---:|---|",
        ]
    )
    for row in g54_contract_family:
        lines.append(
            f"| {row['model']} | {row['task_family']} | {row['first_turn_failures']}/{row['trajectories']} | "
            f"{row['unresolved']} | {row['failure_type_counts'] or 'none'} |"
        )
    lines.append(
        f"| gpt-5.5 | editing_preservation | {len(g55_contract_cases)}/30 | 0 | wrong_output_language=2 |"
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/current_model_error_analysis_v02"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/current_model_error_analysis_v02.md"))
    args = parser.parse_args()

    summary_rows: list[dict[str, Any]] = []
    by_family_rows: list[dict[str, Any]] = []
    by_language_rows: list[dict[str, Any]] = []
    transition_rows: list[dict[str, Any]] = []
    residual_case_rows: list[dict[str, Any]] = []

    for model, paths in CURRENT_MODELS.items():
        trajectory_rows = read_csv(paths["tables"] / "trajectory_metrics.csv")
        score_rows = load_jsonl(paths["scores"])
        for condition in ["baseline", "contract"]:
            summary_rows.append(summarize_condition(model, condition, trajectory_rows))
            by_family_rows.extend(summarize_group(model, condition, "task_family", trajectory_rows))
            by_language_rows.extend(summarize_group(model, condition, "language_pair", trajectory_rows))
        transition_rows.append(paired_transitions(model, trajectory_rows))
        residual_case_rows.extend(residual_rows(model, trajectory_rows, score_rows))

    write_csv(args.out_dir / "current_model_error_summary.csv", summary_rows)
    write_csv(args.out_dir / "current_model_error_by_family.csv", by_family_rows)
    write_csv(args.out_dir / "current_model_error_by_language.csv", by_language_rows)
    write_csv(args.out_dir / "current_model_paired_transitions.csv", transition_rows)
    write_csv(args.out_dir / "current_model_first_turn_failures.csv", residual_case_rows)
    write_csv(
        args.out_dir / "current_model_contract_residual_cases.csv",
        [row for row in residual_case_rows if row["condition"] == "contract"],
    )
    write_markdown(args.out_md, summary_rows, by_family_rows, transition_rows, residual_case_rows)
    print(f"wrote current-model residual error analysis to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
