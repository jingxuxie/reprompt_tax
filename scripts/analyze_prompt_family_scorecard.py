#!/usr/bin/env python
"""Build a cross-model prompt-family scorecard from saved diagnostics."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any


OUT_DIR = Path("results/tables/prompt_family_scorecard_v02")
OUT_MD = Path("paper/prompt_family_scorecard_v02.md")


NANO_DIR = Path("results/tables/openai_nano_stress_v02_full120_prompt_ablation")
CURRENT_DIRS = {
    "gpt-5.4-mini": Path("results/tables/current_prompt_mechanism_gpt54mini_v02"),
    "gpt-5.5": Path("results/tables/current_prompt_mechanism_gpt55_v02"),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing prompt scorecard input {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, f"refusing to write empty prompt scorecard table {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def pct_from_fraction(value: str) -> float:
    return round(100 * float(value), 1)


def as_float(value: str) -> float:
    return round(float(value), 3)


def normalize_summary_row(row: dict[str, str], *, source: str) -> dict[str, Any]:
    if source == "nano":
        return {
            "model": row["model"],
            "condition": row["condition"],
            "n_items": int(row["n"]),
            "ftga_pct": pct_from_fraction(row["ftga"]),
            "mean_rtt": as_float(row["mean_rtt"]),
            "token_tax": as_float(row["mean_token_tax"]),
            "unresolved_pct": pct_from_fraction(row["unresolved_rate"]),
            "initial_failures": int(row["initially_failed_n"]),
            "prompt_scope": "nano_four_condition_diagnostic",
        }
    return {
        "model": row["model"],
        "condition": row["condition"],
        "n_items": int(row["n_items"]),
        "ftga_pct": as_float(row["ftga_pct"]),
        "mean_rtt": as_float(row["mean_rtt"]),
        "token_tax": as_float(row["token_tax"]),
        "unresolved_pct": as_float(row["unresolved_pct"]),
        "initial_failures": int(row["initial_failures"]),
        "prompt_scope": "current_model_three_condition_diagnostic",
    }


def normalize_family_row(row: dict[str, str], *, source: str) -> dict[str, Any]:
    if source == "nano":
        return {
            "model": row["model"],
            "condition": row["condition"],
            "task_family": row["task_family"],
            "n_items": int(row["n"]),
            "ftga_pct": pct_from_fraction(row["ftga"]),
            "mean_rtt": as_float(row["mean_rtt"]),
            "token_tax": as_float(row["mean_token_tax"]),
            "unresolved_pct": pct_from_fraction(row["unresolved_rate"]),
        }
    return {
        "model": row["model"],
        "condition": row["condition"],
        "task_family": row["task_family"],
        "n_items": int(row["n_items"]),
        "ftga_pct": as_float(row["ftga_pct"]),
        "mean_rtt": as_float(row["mean_rtt"]),
        "token_tax": as_float(row["token_tax"]),
        "unresolved_pct": as_float(row["unresolved_pct"]),
    }


def summary_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [
        normalize_summary_row(row, source="nano")
        for row in read_csv(NANO_DIR / "prompt_ablation_summary.csv")
    ]
    for table_dir in CURRENT_DIRS.values():
        rows.extend(
            normalize_summary_row(row, source="current")
            for row in read_csv(table_dir / "current_prompt_mechanism_summary.csv")
        )
    return rows


def family_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [
        normalize_family_row(row, source="nano")
        for row in read_csv(NANO_DIR / "prompt_ablation_by_family.csv")
    ]
    for table_dir in CURRENT_DIRS.values():
        rows.extend(
            normalize_family_row(row, source="current")
            for row in read_csv(table_dir / "current_prompt_mechanism_by_family.csv")
        )
    return rows


def comparison_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for model, table_dir, source in [
        ("gpt-4.1-nano", NANO_DIR, "nano"),
        ("gpt-5.4-mini", CURRENT_DIRS["gpt-5.4-mini"], "current"),
        ("gpt-5.5", CURRENT_DIRS["gpt-5.5"], "current"),
    ]:
        filename = "prompt_ablation_paired_effects.csv" if source == "nano" else "current_prompt_mechanism_paired_effects.csv"
        for row in read_csv(table_dir / filename):
            comparison = row["comparison"]
            if comparison not in {"content_preservation_minus_baseline", "contract_minus_baseline", "content_preservation_minus_contract", "contract_minus_content_preservation"}:
                continue
            delta = float(row["delta_ftga_pp"])
            improved = int(row["ftga_improved"])
            worsened = int(row["ftga_worsened"])
            if comparison == "contract_minus_content_preservation":
                comparison = "content_preservation_minus_contract"
                delta = -delta
                improved, worsened = worsened, improved
            rows.append(
                {
                    "model": model,
                    "comparison": comparison,
                    "n_pairs": int(row["n_pairs"]),
                    "delta_ftga_pp": round(delta, 1),
                    "ftga_improved": improved,
                    "ftga_worsened": worsened,
                    "ftga_tied": int(row["ftga_tied"]),
                    "ftga_sign_test_p": f"{float(row['ftga_sign_test_p']):.12g}",
                    "rtt_reduction": as_float(row["rtt_reduction"]),
                    "token_tax_reduction": as_float(row["token_tax_reduction"]),
                    "unresolved_reduction_pp": round(float(row["unresolved_reduction_pp"]), 1),
                }
            )
    return rows


def model_scorecard(summary: list[dict[str, Any]], comparisons: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_model: dict[str, list[dict[str, Any]]] = {}
    for row in summary:
        by_model.setdefault(row["model"], []).append(row)
    comp = {(row["model"], row["comparison"]): row for row in comparisons}
    rows: list[dict[str, Any]] = []
    for model, model_rows in sorted(by_model.items()):
        best = max(model_rows, key=lambda row: (row["ftga_pct"], -row["mean_rtt"], -row["token_tax"]))
        baseline = next(row for row in model_rows if row["condition"] == "baseline")
        contract = next(row for row in model_rows if row["condition"] == "contract")
        content = next(row for row in model_rows if row["condition"] == "content_preservation")
        content_vs_contract = comp[(model, "content_preservation_minus_contract")]
        generic = next((row for row in model_rows if row["condition"] == "generic_helpfulness"), None)
        rows.append(
            {
                "model": model,
                "tested_conditions": ";".join(row["condition"] for row in sorted(model_rows, key=lambda row: row["condition"])),
                "best_ftga_condition": best["condition"],
                "best_ftga_pct": best["ftga_pct"],
                "baseline_ftga_pct": baseline["ftga_pct"],
                "contract_ftga_pct": contract["ftga_pct"],
                "content_preservation_ftga_pct": content["ftga_pct"],
                "content_minus_contract_delta_pp": content_vs_contract["delta_ftga_pp"],
                "content_minus_contract_improved": content_vs_contract["ftga_improved"],
                "content_minus_contract_worsened": content_vs_contract["ftga_worsened"],
                "content_minus_contract_tied": content_vs_contract["ftga_tied"],
                "generic_helpfulness_ftga_pct": "" if generic is None else generic["ftga_pct"],
                "claim_boundary": "generic_not_tested_current_models" if generic is None else "single_model_generic_control_only",
            }
        )
    return rows


def row_by(rows: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
    matches = [row for row in rows if all(row[key] == value for key, value in kwargs.items())]
    require(len(matches) == 1, f"expected one row for {kwargs}, found {len(matches)}")
    return matches[0]


def write_markdown(
    path: Path,
    *,
    summary: list[dict[str, Any]],
    family: list[dict[str, Any]],
    comparisons: list[dict[str, Any]],
    scorecard: list[dict[str, Any]],
) -> None:
    nano = row_by(scorecard, model="gpt-4.1-nano")
    g54 = row_by(scorecard, model="gpt-5.4-mini")
    g55 = row_by(scorecard, model="gpt-5.5")
    nano_edit = row_by(family, model="gpt-4.1-nano", condition="content_preservation", task_family="editing_preservation")
    g55_edit = row_by(family, model="gpt-5.5", condition="content_preservation", task_family="editing_preservation")

    lines = [
        "# Prompt-Family Scorecard",
        "",
        "This artifact consolidates the saved prompt-control and prompt-mechanism",
        "diagnostics. It makes no API calls. It compares only prompts that were",
        "already run: baseline, full Global Interaction Contract, the narrower",
        "content-preservation scaffold, and the generic-helpfulness control where",
        "available.",
        "",
        "## Model Scorecard",
        "",
        "| Model | Tested conditions | Best FTGA prompt | Baseline FTGA | Contract FTGA | Content-preservation FTGA | Content minus contract | Boundary |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for row in scorecard:
        lines.append(
            f"| {row['model']} | {row['tested_conditions']} | {row['best_ftga_condition']} | "
            f"{row['baseline_ftga_pct']}% | {row['contract_ftga_pct']}% | "
            f"{row['content_preservation_ftga_pct']}% | {row['content_minus_contract_delta_pp']:+.1f} pp "
            f"({row['content_minus_contract_improved']}/{row['content_minus_contract_worsened']}/"
            f"{row['content_minus_contract_tied']}) | {row['claim_boundary']} |"
        )

    lines.extend(
        [
            "",
            "## Aggregate Prompt Metrics",
            "",
            "| Model | Condition | FTGA | Mean RTT | Token tax | Unresolved | Initial failures |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in summary:
        lines.append(
            f"| {row['model']} | {row['condition']} | {row['ftga_pct']}% | {row['mean_rtt']:.3f} | "
            f"{row['token_tax']:.3f}x | {row['unresolved_pct']}% | {row['initial_failures']} |"
        )

    lines.extend(
        [
            "",
            "## Paired Prompt Comparisons",
            "",
            "| Model | Comparison | FTGA delta | Improved | Worsened | Tied | Sign p | RTT reduction | Token-tax reduction |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in comparisons:
        lines.append(
            f"| {row['model']} | {row['comparison']} | {row['delta_ftga_pp']:+.1f} pp | "
            f"{row['ftga_improved']} | {row['ftga_worsened']} | {row['ftga_tied']} | "
            f"{float(row['ftga_sign_test_p']):.4g} | {row['rtt_reduction']:+.3f} | "
            f"{row['token_tax_reduction']:+.3f}x |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"Across the three models with saved content-preservation rows, the content-preservation scaffold is the highest-FTGA tested prompt: "
            f"{nano['content_preservation_ftga_pct']}% on `gpt-4.1-nano`, {g54['content_preservation_ftga_pct']}% on `gpt-5.4-mini`, "
            f"and {g55['content_preservation_ftga_pct']}% on `gpt-5.5`.",
            "",
            f"The margins over the full contract are model-dependent: +{nano['content_minus_contract_delta_pp']:.1f} pp on nano, "
            f"+{g54['content_minus_contract_delta_pp']:.1f} pp on `gpt-5.4-mini`, and +{g55['content_minus_contract_delta_pp']:.1f} pp on `gpt-5.5`. "
            "The two current-model margins are one net item or essentially tied, so they should be framed as mechanism evidence rather than prompt dominance.",
            "",
            f"The family slice reinforces the mechanism claim: content preservation reaches {nano_edit['ftga_pct']}% editing-preservation FTGA on nano and "
            f"{g55_edit['ftga_pct']}% on `gpt-5.5`, while non-editing families are often saturated or sparse.",
            "",
            "Claim boundary: generic-helpfulness was only tested for `gpt-4.1-nano`; the current-model prompt comparison is baseline, contract, and content-preservation only. This artifact does not claim the narrow prompt is universally best.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    summary = summary_rows()
    family = family_rows()
    comparisons = comparison_rows()
    scorecard = model_scorecard(summary, comparisons)

    write_csv(args.out_dir / "prompt_family_summary.csv", summary)
    write_csv(args.out_dir / "prompt_family_by_family.csv", family)
    write_csv(args.out_dir / "prompt_family_paired_comparisons.csv", comparisons)
    write_csv(args.out_dir / "prompt_family_model_scorecard.csv", scorecard)
    write_markdown(args.out_md, summary=summary, family=family, comparisons=comparisons, scorecard=scorecard)
    print(f"wrote prompt-family scorecard to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
