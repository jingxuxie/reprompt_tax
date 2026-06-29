#!/usr/bin/env python
"""Analyze task-useful first-turn failures in RePromptTax outputs."""

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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def bool_value(row: dict[str, Any], field: str) -> bool:
    value = row[field]
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value)


def pct(numerator: int, denominator: int) -> float:
    return round(100.0 * numerator / denominator, 1) if denominator else 0.0


def first_turn_rows(rows: list[dict[str, Any]], expected_count: int | None) -> list[dict[str, Any]]:
    out = [row for row in rows if int(row["turn"]) == 0]
    if expected_count is not None:
        require(len(out) == expected_count, f"expected {expected_count} first-turn rows, found {len(out)}")
    for row in out:
        for field in ("item_id", "model", "condition", "task_family", "language_pair", "pass", *COMPONENTS):
            require(field in row, f"first-turn row missing {field}")
    return out


def group_rows(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> dict[tuple[str, ...], list[dict[str, Any]]]:
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[tuple(str(row[field]) for field in fields)].append(row)
    return groups


def is_failure(row: dict[str, Any]) -> bool:
    return not bool_value(row, "pass")


def is_task_useful_failure(row: dict[str, Any]) -> bool:
    return is_failure(row) and bool_value(row, "task_pass")


def is_task_and_preservation_useful_failure(row: dict[str, Any]) -> bool:
    return is_task_useful_failure(row) and bool_value(row, "preservation_pass")


def is_language_or_script_framing_failure(row: dict[str, Any]) -> bool:
    return (
        is_task_and_preservation_useful_failure(row)
        and bool_value(row, "register_locale_pass")
        and (not bool_value(row, "language_pass") or not bool_value(row, "script_pass"))
    )


def summary_rows(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for key, group in sorted(group_rows(rows, fields).items()):
        n = len(group)
        ftga_pass_n = sum(bool_value(row, "pass") for row in group)
        failure_n = n - ftga_pass_n
        task_useful_n = sum(is_task_useful_failure(row) for row in group)
        task_preserve_n = sum(is_task_and_preservation_useful_failure(row) for row in group)
        framing_n = sum(is_language_or_script_framing_failure(row) for row in group)
        task_noncompletion_n = sum(is_failure(row) and not bool_value(row, "task_pass") for row in group)
        base = {field: value for field, value in zip(fields, key)}
        base.update(
            {
                "n": n,
                "ftga_pass_n": ftga_pass_n,
                "ftga_pass_pct": pct(ftga_pass_n, n),
                "first_turn_failure_n": failure_n,
                "first_turn_failure_pct": pct(failure_n, n),
                "task_useful_contract_failure_n": task_useful_n,
                "task_useful_contract_failure_pct": pct(task_useful_n, n),
                "task_useful_share_of_failures_pct": pct(task_useful_n, failure_n),
                "task_and_preservation_useful_failure_n": task_preserve_n,
                "task_and_preservation_useful_failure_pct": pct(task_preserve_n, n),
                "language_or_script_framing_failure_n": framing_n,
                "language_or_script_framing_failure_pct": pct(framing_n, n),
                "task_noncompletion_failure_n": task_noncompletion_n,
                "task_noncompletion_failure_pct": pct(task_noncompletion_n, n),
            }
        )
        out.append(base)
    return out


def signature(row: dict[str, Any]) -> str:
    failed = []
    for component in COMPONENTS:
        if not bool_value(row, component):
            failed.append(component.removesuffix("_pass"))
    return "+".join(failed) if failed else "none"


def signature_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[tuple[str, str, str]] = Counter()
    denominators: Counter[tuple[str, str]] = Counter()
    for row in rows:
        if not is_task_useful_failure(row):
            continue
        key = (row["condition"], row["task_family"])
        denominators[key] += 1
        counts[(row["condition"], row["task_family"], signature(row))] += 1

    out: list[dict[str, Any]] = []
    for (condition, task_family, failure_signature), count in sorted(counts.items()):
        denom = denominators[(condition, task_family)]
        out.append(
            {
                "condition": condition,
                "task_family": task_family,
                "failure_signature": failure_signature,
                "count": count,
                "share_of_task_useful_failures_pct": pct(count, denom),
            }
        )
    return out


def family_summary_phrase(
    family_rows: list[dict[str, Any]],
    *,
    condition: str,
    max_items: int = 2,
) -> str:
    rows = [
        row
        for row in family_rows
        if row["condition"] == condition and int(row["task_useful_contract_failure_n"]) > 0
    ]
    rows.sort(key=lambda row: (-int(row["task_useful_contract_failure_n"]), row["task_family"]))
    if not rows:
        return "no task-useful failure rows"
    parts = [
        f"{FAMILY_LABELS.get(row['task_family'], row['task_family'])} ({int(row['task_useful_contract_failure_n'])})"
        for row in rows[:max_items]
    ]
    if len(rows) > max_items:
        parts.append(f"{len(rows) - max_items} other families")
    if len(parts) == 1:
        return f"{parts[0]} rows"
    return f"{', '.join(parts[:-1])}, and {parts[-1]} rows"


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if rows:
        fieldnames = list(rows[0].keys())
    elif fieldnames is None:
        fieldnames = []
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def row_by(rows: list[dict[str, Any]], **kwargs: str) -> dict[str, Any]:
    for row in rows:
        if all(str(row[key]) == value for key, value in kwargs.items()):
            return row
    raise AssertionError(f"missing row for {kwargs}")


def write_markdown(
    path: Path,
    *,
    scores_path: Path,
    overall_rows: list[dict[str, Any]],
    family_rows: list[dict[str, Any]],
    model_rows: list[dict[str, Any]],
    signatures: list[dict[str, Any]],
) -> None:
    baseline = row_by(overall_rows, condition="baseline")
    contract = row_by(overall_rows, condition="contract")
    baseline_family_phrase = family_summary_phrase(family_rows, condition="baseline")
    contract_family_phrase = family_summary_phrase(family_rows, condition="contract")

    lines = [
        "# Task-Useful Contract-Failure Diagnostic",
        "",
        f"Generated from first-turn rows in `{scores_path}`.",
        "",
        "This diagnostic asks whether first-turn failures are always task failures.",
        "A **task-useful contract failure** is a row where the automatic task",
        "component passes but full first-turn global alignment fails because at",
        "least one interaction-contract component fails. This is conservative",
        "automatic evidence for hidden repair burden, not a replacement for",
        "human/native-speaker validation.",
        "",
        "## Overall",
        "",
        "| Condition | First-turn failures | Task-useful contract failures | Share of failures | Task+preservation useful failures | Language/script framing failures |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in overall_rows:
        lines.append(
            "| "
            f"{row['condition']} | {row['first_turn_failure_n']} | "
            f"{row['task_useful_contract_failure_n']} ({row['task_useful_contract_failure_pct']:.1f}% of all rows) | "
            f"{row['task_useful_share_of_failures_pct']:.1f}% | "
            f"{row['task_and_preservation_useful_failure_n']} | "
            f"{row['language_or_script_framing_failure_n']} |"
        )

    lines.extend(
        [
            "",
            "## By Model And Condition",
            "",
            "| Model | Condition | Failures | Task-useful failures | Task+preservation useful | Task noncompletion failures |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in model_rows:
        lines.append(
            "| "
            f"{row['model']} | {row['condition']} | {row['first_turn_failure_n']} | "
            f"{row['task_useful_contract_failure_n']} | "
            f"{row['task_and_preservation_useful_failure_n']} | "
            f"{row['task_noncompletion_failure_n']} |"
        )

    lines.extend(
        [
            "",
            "## By Family And Condition",
            "",
            "| Condition | Task family | Failures | Task-useful failures | Task+preservation useful | Task noncompletion failures |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in family_rows:
        if row["first_turn_failure_n"] == 0:
            continue
        lines.append(
            "| "
            f"{row['condition']} | {FAMILY_LABELS.get(row['task_family'], row['task_family'])} | "
            f"{row['first_turn_failure_n']} | {row['task_useful_contract_failure_n']} | "
            f"{row['task_and_preservation_useful_failure_n']} | "
            f"{row['task_noncompletion_failure_n']} |"
        )

    lines.extend(
        [
            "",
            "## Task-Useful Failure Signatures",
            "",
            "| Condition | Task family | Failed components | Count | Share within task-useful failures |",
            "|---|---|---|---:|---:|",
        ]
    )
    for row in signatures:
        lines.append(
            "| "
            f"{row['condition']} | {FAMILY_LABELS.get(row['task_family'], row['task_family'])} | "
            f"{row['failure_signature']} | {row['count']} | "
            f"{row['share_of_task_useful_failures_pct']:.1f}% |"
        )
    if not signatures:
        lines.extend(["", "No task-useful first-turn failures were observed in this run."])

    lines.extend(["", "## Interpretation", ""])
    if contract["first_turn_failure_n"]:
        contract_clause = (
            f"Under the Global Interaction Contract this count falls to "
            f"{contract['task_useful_contract_failure_n']}/{contract['first_turn_failure_n']} failures."
        )
    else:
        contract_clause = "Under the Global Interaction Contract, there are no first-turn failures in this run."
    lines.extend(
        [
            f"Under baseline prompting, {baseline['task_useful_contract_failure_n']}/"
            f"{baseline['first_turn_failure_n']} first-turn failures are task-useful contract failures",
            f"({baseline['task_useful_share_of_failures_pct']:.1f}% of failures). {contract_clause}",
            "",
        ]
    )
    if baseline["task_useful_contract_failure_n"] or contract["task_useful_contract_failure_n"]:
        lines.extend(
            [
                f"The stricter task+preservation useful subset falls from {baseline['task_and_preservation_useful_failure_n']}",
                f"to {contract['task_and_preservation_useful_failure_n']}. This is the cleanest automatic",
                "slice for the paper's hidden-tax claim: the response has performed the task",
                "and preserved required spans, but still violates language or script framing.",
                "",
                "Most baseline task-useful failures are concentrated in",
                f"{baseline_family_phrase}. After",
                "the contract, residual task-useful failures are concentrated in",
                f"{contract_family_phrase},",
                "which keeps the mitigation claim bounded.",
            ]
        )
    else:
        lines.extend(
            [
                "This run does not show a hidden task-useful failure slice: all observed",
                "first-turn failures are task-noncompletion failures under the automatic",
                "scorer. The result should be read as a bounded pilot diagnostic, not as",
                "evidence that hidden repair burden is absent in the full benchmark.",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", type=Path, default=Path("results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/openai_three_model_stress_v02_full120"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/task_useful_failure_analysis_v02_full120.md"))
    parser.add_argument("--expected-first-turn-rows", type=int, default=None)
    args = parser.parse_args()

    rows = first_turn_rows(load_jsonl(args.scores), args.expected_first_turn_rows)
    overall_rows = summary_rows(rows, ("condition",))
    model_rows = summary_rows(rows, ("model", "condition"))
    family_rows = summary_rows(rows, ("condition", "task_family"))
    language_rows = summary_rows(rows, ("condition", "language_pair"))
    signatures = signature_rows(rows)

    write_csv(args.out_dir / "task_useful_failure_by_condition.csv", overall_rows)
    write_csv(args.out_dir / "task_useful_failure_by_model_condition.csv", model_rows)
    write_csv(args.out_dir / "task_useful_failure_by_family_condition.csv", family_rows)
    write_csv(args.out_dir / "task_useful_failure_by_language_condition.csv", language_rows)
    write_csv(
        args.out_dir / "task_useful_failure_signatures.csv",
        signatures,
        fieldnames=[
            "condition",
            "task_family",
            "failure_signature",
            "count",
            "share_of_task_useful_failures_pct",
        ],
    )
    write_markdown(
        args.out_md,
        scores_path=args.scores,
        overall_rows=overall_rows,
        family_rows=family_rows,
        model_rows=model_rows,
        signatures=signatures,
    )
    print(f"wrote task-useful failure analysis to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
