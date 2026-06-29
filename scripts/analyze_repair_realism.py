#!/usr/bin/env python
"""Analyze repair-prompt wording sensitivity."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from math import comb
from pathlib import Path
from statistics import mean
from typing import Any


VARIANT_LABELS = {
    "standard_saved": "standard",
    "terse_keep_english": "terse",
    "frustrated_dont_translate": "frustrated",
    "explicit_contract": "explicit",
}


APOLOGY_RE = re.compile(r"\b(sorry|apolog(?:y|ize|ise|ies)|my mistake|i meant|you're right)\b", re.IGNORECASE)


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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return bool(value)


def sign_test_p(improved: int, worsened: int) -> float:
    n = improved + worsened
    if n == 0:
        return 1.0
    k = min(improved, worsened)
    return min(1.0, 2.0 * sum(comb(n, i) for i in range(k + 1)) / (2**n))


def repair_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (row["item_id"], row["model"], row["condition"])


def validate_rows(rows: list[dict[str, Any]], expected_sample_size: int) -> None:
    variants = set(VARIANT_LABELS)
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[repair_key(row)].append(row)
    require(len(grouped) == expected_sample_size, f"expected {expected_sample_size} sampled failures, found {len(grouped)}")
    for key, group in grouped.items():
        seen = {row["repair_variant"] for row in group}
        require(seen == variants, f"{key} missing repair variants: {seen}")


def row_apology_without_task(row: dict[str, Any]) -> bool:
    return bool(APOLOGY_RE.search(str(row.get("response", "")))) and not bool_value(row.get("task_pass"))


def summary_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["repair_variant"]].append(row)
    out: list[dict[str, Any]] = []
    for variant in sorted(groups, key=lambda value: list(VARIANT_LABELS).index(value)):
        group = groups[variant]
        n = len(group)
        passed = sum(bool_value(row["pass"]) for row in group)
        task_passed = sum(bool_value(row["task_pass"]) for row in group)
        language_passed = sum(bool_value(row["language_pass"]) for row in group)
        preservation_passed = sum(bool_value(row["preservation_pass"]) for row in group)
        out.append(
            {
                "repair_variant": variant,
                "label": VARIANT_LABELS[variant],
                "n": n,
                "repair_success_n": passed,
                "repair_success_pct": round(100.0 * passed / n, 1),
                "task_pass_n": task_passed,
                "task_pass_pct": round(100.0 * task_passed / n, 1),
                "language_pass_n": language_passed,
                "language_pass_pct": round(100.0 * language_passed / n, 1),
                "preservation_pass_n": preservation_passed,
                "preservation_pass_pct": round(100.0 * preservation_passed / n, 1),
                "apology_without_task_n": sum(row_apology_without_task(row) for row in group),
                "mean_input_tokens": round(mean(int(row["input_tokens"]) for row in group), 1),
                "mean_output_tokens": round(mean(int(row["output_tokens"]) for row in group), 1),
                "mean_total_tokens": round(mean(int(row["input_tokens"]) + int(row["output_tokens"]) for row in group), 1),
            }
        )
    return out


def by_model_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["model"], row["repair_variant"])].append(row)
    out: list[dict[str, Any]] = []
    for (model, variant), group in sorted(groups.items()):
        n = len(group)
        passed = sum(bool_value(row["pass"]) for row in group)
        out.append(
            {
                "model": model,
                "repair_variant": variant,
                "label": VARIANT_LABELS[variant],
                "n": n,
                "repair_success_n": passed,
                "repair_success_pct": round(100.0 * passed / n, 1),
                "mean_total_tokens": round(mean(int(row["input_tokens"]) + int(row["output_tokens"]) for row in group), 1),
            }
        )
    return out


def paired_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        grouped[repair_key(row)][row["repair_variant"]] = row
    out: list[dict[str, Any]] = []
    for variant in ("terse_keep_english", "frustrated_dont_translate", "explicit_contract"):
        improved = worsened = tied = 0
        token_delta: list[int] = []
        for variants in grouped.values():
            standard = variants["standard_saved"]
            alternate = variants[variant]
            standard_pass = bool_value(standard["pass"])
            alternate_pass = bool_value(alternate["pass"])
            if alternate_pass and not standard_pass:
                improved += 1
            elif standard_pass and not alternate_pass:
                worsened += 1
            else:
                tied += 1
            token_delta.append(
                (int(alternate["input_tokens"]) + int(alternate["output_tokens"]))
                - (int(standard["input_tokens"]) + int(standard["output_tokens"]))
            )
        out.append(
            {
                "comparison": f"{variant}_minus_standard_saved",
                "n_pairs": len(grouped),
                "repair_success_improved": improved,
                "repair_success_worsened": worsened,
                "repair_success_tied": tied,
                "repair_success_sign_p": sign_test_p(improved, worsened),
                "delta_success_pp": round(100.0 * (improved - worsened) / len(grouped), 1),
                "mean_total_token_delta": round(mean(token_delta), 1),
            }
        )
    return out


def disagreement_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        grouped[repair_key(row)][row["repair_variant"]] = row
    out: list[dict[str, Any]] = []
    for key, variants in sorted(grouped.items()):
        standard_pass = bool_value(variants["standard_saved"]["pass"])
        for variant in ("terse_keep_english", "frustrated_dont_translate", "explicit_contract"):
            alternate = variants[variant]
            alternate_pass = bool_value(alternate["pass"])
            if standard_pass == alternate_pass:
                continue
            out.append(
                {
                    "item_id": key[0],
                    "model": key[1],
                    "condition": key[2],
                    "language_pair": alternate["language_pair"],
                    "repair_variant": variant,
                    "standard_pass": standard_pass,
                    "variant_pass": alternate_pass,
                    "standard_failure_types": json.dumps(variants["standard_saved"].get("failure_types", []), ensure_ascii=False),
                    "variant_failure_types": json.dumps(alternate.get("failure_types", []), ensure_ascii=False),
                    "variant_response": str(alternate.get("response", "")).replace("\n", " ")[:240],
                }
            )
    return out


def write_markdown(
    path: Path,
    summary: list[dict[str, Any]],
    paired: list[dict[str, Any]],
    by_model: list[dict[str, Any]],
    disagreements: list[dict[str, Any]],
) -> None:
    standard = next(row for row in summary if row["repair_variant"] == "standard_saved")
    explicit = next(row for row in summary if row["repair_variant"] == "explicit_contract")
    terse = next(row for row in summary if row["repair_variant"] == "terse_keep_english")
    lines = [
        "# Repair-Realism Diagnostic",
        "",
        "This diagnostic compares the saved standardized first repair prompt against",
        "three user-like one-turn repair prompts on a deterministic 24-item sample of",
        "baseline editing-preservation first-turn failures. The sample is balanced",
        "across the three GPT-4.1-family models and Arabic-English/Spanish-English",
        "editing failures.",
        "",
        "## Summary",
        "",
        "| Repair prompt | n | Success | Task pass | Language pass | Preservation pass | Apology without task | Mean tokens |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            "| "
            f"{row['label']} | {row['n']} | {row['repair_success_n']}/{row['n']} ({row['repair_success_pct']:.1f}%) | "
            f"{row['task_pass_n']}/{row['n']} ({row['task_pass_pct']:.1f}%) | "
            f"{row['language_pass_n']}/{row['n']} ({row['language_pass_pct']:.1f}%) | "
            f"{row['preservation_pass_n']}/{row['n']} ({row['preservation_pass_pct']:.1f}%) | "
            f"{row['apology_without_task_n']} | {row['mean_total_tokens']:.1f} |"
        )
    lines.extend(
        [
            "",
            "## Paired Effects Against Standard Repair",
            "",
            "| Comparison | Improved | Worsened | Tied | Sign p | Success delta | Mean token delta |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in paired:
        lines.append(
            "| "
            f"{row['comparison']} | {row['repair_success_improved']} | {row['repair_success_worsened']} | "
            f"{row['repair_success_tied']} | {row['repair_success_sign_p']:.6g} | "
            f"{row['delta_success_pp']:+.1f} pp | {row['mean_total_token_delta']:+.1f} |"
        )
    lines.extend(
        [
            "",
            "## By Model",
            "",
            "| Model | Repair prompt | n | Success | Mean tokens |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for row in by_model:
        lines.append(
            "| "
            f"{row['model']} | {row['label']} | {row['n']} | "
            f"{row['repair_success_n']}/{row['n']} ({row['repair_success_pct']:.1f}%) | "
            f"{row['mean_total_tokens']:.1f} |"
        )
    lines.extend(["", "## Variant Disagreements", ""])
    if not disagreements:
        lines.append("No repair-success disagreements against the saved standard repair.")
    else:
        lines.extend(
            [
                "| Item | Model | Language | Variant | Standard pass | Variant pass | Variant failures | Response excerpt |",
                "|---|---|---|---|---:|---:|---|---|",
            ]
        )
        for row in disagreements:
            response = row["variant_response"].replace("|", "/")
            lines.append(
                "| "
                f"{row['item_id']} | {row['model']} | {row['language_pair']} | {VARIANT_LABELS[row['repair_variant']]} | "
                f"{row['standard_pass']} | {row['variant_pass']} | {row['variant_failure_types']} | {response} |"
            )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"The saved standardized repair succeeds on {standard['repair_success_n']}/{standard['n']} sampled failures.",
            f"The explicit user-like contract repair succeeds on {explicit['repair_success_n']}/{explicit['n']},",
            f"while the terse repair succeeds on {terse['repair_success_n']}/{terse['n']}.",
            "This is a small interaction-realism diagnostic, not a replacement for a",
            "full user study. It shows whether RTT conclusions are sensitive to the",
            "wording of the first repair prompt on the dominant editing-preservation",
            "failure mode.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("results/scores/openai_three_model_stress_v02_repair_realism_editing_baseline24.jsonl"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/openai_three_model_stress_v02_repair_realism_editing_baseline24"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/repair_realism_editing_baseline24.md"))
    parser.add_argument("--expected-sample-size", type=int, default=24)
    args = parser.parse_args()

    rows = load_jsonl(args.input)
    validate_rows(rows, args.expected_sample_size)
    summary = summary_rows(rows)
    by_model = by_model_rows(rows)
    paired = paired_rows(rows)
    disagreements = disagreement_rows(rows)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "repair_realism_summary.csv", summary)
    write_csv(args.out_dir / "repair_realism_by_model.csv", by_model)
    write_csv(args.out_dir / "repair_realism_paired_effects.csv", paired)
    write_csv(args.out_dir / "repair_realism_disagreements.csv", disagreements)
    write_markdown(args.out_md, summary, paired, by_model, disagreements)
    print(f"wrote repair-realism analysis to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
