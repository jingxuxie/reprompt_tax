#!/usr/bin/env python
"""Summarize current-model RePromptTax refresh experiments."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


HISTORICAL_TABLES = Path("results/tables/openai_three_model_stress_v02_full120")
GPT54_TABLES = Path("results/tables/openai_gpt54mini_stress_v02_full120")
GPT55_TABLES = Path("results/tables/openai_gpt55_stress_v02_full120")
GPT54_OUTPUTS = Path("results/model_outputs/openai_gpt54mini_stress_v02_full120.jsonl")
GPT55_OUTPUTS = Path("results/model_outputs/openai_gpt55_stress_v02_full120.jsonl")


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


def row_by(rows: list[dict[str, str]], **kwargs: str) -> dict[str, str]:
    for row in rows:
        if all(row[key] == value for key, value in kwargs.items()):
            return row
    raise AssertionError(f"missing row for {kwargs}")


def sign_p(sign_rows: list[dict[str, str]], model: str, metric: str) -> str:
    try:
        row = row_by(sign_rows, model=model, metric=metric)
    except AssertionError:
        return ""
    return row["two_sided_sign_p"]


def usage(path: Path) -> dict[str, int]:
    rows = load_jsonl(path)
    return {
        "api_calls": len(rows),
        "input_tokens": sum(int(row.get("input_tokens", 0)) for row in rows),
        "output_tokens": sum(int(row.get("output_tokens", 0)) for row in rows),
        "total_tokens": sum(int(row.get("input_tokens", 0)) + int(row.get("output_tokens", 0)) for row in rows),
    }


def result_row(
    *,
    generation: str,
    model: str,
    scope: str,
    metrics_rows: list[dict[str, str]],
    paired_rows: list[dict[str, str]],
    sign_rows: list[dict[str, str]],
) -> dict[str, Any]:
    baseline = row_by(metrics_rows, model=model, condition="baseline")
    contract = row_by(metrics_rows, model=model, condition="contract")
    paired = row_by(paired_rows, model=model)
    return {
        "model_generation": generation,
        "model": model,
        "scope": scope,
        "n_items": baseline["n"],
        "baseline_ftga_pct": round(100 * float(baseline["ftga"]), 1),
        "contract_ftga_pct": round(100 * float(contract["ftga"]), 1),
        "delta_ftga_pp": round(float(paired["delta_ftga_pp"]), 1),
        "baseline_mean_rtt": round(float(baseline["mean_rtt"]), 3),
        "contract_mean_rtt": round(float(contract["mean_rtt"]), 3),
        "rtt_reduction": round(float(paired["rtt_reduction"]), 3),
        "baseline_token_tax": round(float(baseline["mean_token_tax"]), 3),
        "contract_token_tax": round(float(contract["mean_token_tax"]), 3),
        "token_tax_reduction": round(float(paired["token_tax_reduction"]), 3),
        "baseline_unresolved_pct": round(100 * float(baseline["unresolved_rate"]), 1),
        "contract_unresolved_pct": round(100 * float(contract["unresolved_rate"]), 1),
        "unresolved_reduction_pp": round(float(paired["unresolved_reduction_pp"]), 1),
        "ftga_sign_p": sign_p(sign_rows, model, "ftga"),
        "token_tax_sign_p": sign_p(sign_rows, model, "token_tax"),
    }


def write_markdown(path: Path, rows: list[dict[str, Any]], usage_rows: list[dict[str, Any]]) -> None:
    g54 = row_by([{k: str(v) for k, v in row.items()} for row in rows], model="gpt-5.4-mini")
    g55 = row_by([{k: str(v) for k, v in row.items()} for row in rows], model="gpt-5.5")
    lines = [
        "# Current-Model Refresh",
        "",
        "This artifact summarizes the bounded current-model follow-up runs.",
        "`gpt-5.4-mini` and `gpt-5.5` are full 120-item baseline-vs-contract",
        "runs. The earlier GPT-5.5 40-item stratified/enriched pilot is retained",
        "only as a development smoke check, not as the paper-facing result.",
        "",
        "## Main Table",
        "",
        "| Generation | Model | Scope | N | Baseline FTGA | Contract FTGA | Delta | Baseline RTT | Contract RTT | Token-tax delta | Unresolved delta | FTGA sign p |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row['model_generation']} | {row['model']} | {row['scope']} | {row['n_items']} | "
            f"{row['baseline_ftga_pct']:.1f}% | {row['contract_ftga_pct']:.1f}% | "
            f"{row['delta_ftga_pp']:+.1f} pp | {row['baseline_mean_rtt']:.3f} | "
            f"{row['contract_mean_rtt']:.3f} | {row['token_tax_reduction']:+.3f}x | "
            f"{row['unresolved_reduction_pp']:+.1f} pp | {row['ftga_sign_p']} |"
        )

    lines.extend(
        [
            "",
            "## API Usage",
            "",
            "| Artifact | API calls | Input tokens | Output tokens | Total tokens |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in usage_rows:
        lines.append(
            "| "
            f"{row['artifact']} | {row['api_calls']} | {row['input_tokens']} | "
            f"{row['output_tokens']} | {row['total_tokens']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"On the full 120-item run, `gpt-5.4-mini` improves FTGA from {float(g54['baseline_ftga_pct']):.1f}% "
            f"to {float(g54['contract_ftga_pct']):.1f}% (+{float(g54['delta_ftga_pp']):.1f} pp) and reduces mean token tax "
            f"by {float(g54['token_tax_reduction']):.3f}x. The FTGA sign test is not decisive",
            f"(p={g54['ftga_sign_p']}), while token-tax reduction is stronger (p={g54['token_tax_sign_p']}).",
            f"The unresolved rate moves from {float(g54['baseline_unresolved_pct']):.1f}% to {float(g54['contract_unresolved_pct']):.1f}%,",
            "so the mitigation claim for this model should emphasize lower token burden and bounded FTGA gain, not universal repair improvement.",
            "",
            f"On the full 120-item GPT-5.5 run, FTGA rises from {float(g55['baseline_ftga_pct']):.1f}% to {float(g55['contract_ftga_pct']):.1f}% "
            f"(+{float(g55['delta_ftga_pp']):.1f} pp; sign-test p={g55['ftga_sign_p']}).",
            f"Mean RTT falls from {float(g55['baseline_mean_rtt']):.3f} to {float(g55['contract_mean_rtt']):.3f},",
            f"and token tax falls by {float(g55['token_tax_reduction']):.3f}x.",
            "The contract leaves two first-turn failures but no unresolved trajectories.",
            "This makes GPT-5.5 the cleanest headline current-model result: RePromptTax persists on the current flagship, and the contract sharply reduces it.",
            "",
            "A scorer-coverage fix added `data are insufficient` as an accepted correction for the three `*_SB_001` grammar items.",
            "That fix affects the GPT-5.5 runs, where the model used this valid correction; no saved GPT-4.1-family full-run output used this phrase.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/current_model_refresh_v02"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/current_model_refresh_v02.md"))
    args = parser.parse_args()

    historical_metrics = read_csv(HISTORICAL_TABLES / "metrics_summary.csv")
    historical_paired = read_csv(HISTORICAL_TABLES / "paired_contract_effects_by_model.csv")
    historical_sign = read_csv(HISTORICAL_TABLES / "paired_significance_by_model.csv")
    g54_metrics = read_csv(GPT54_TABLES / "metrics_summary.csv")
    g54_paired = read_csv(GPT54_TABLES / "paired_contract_effects_by_model.csv")
    g54_sign = read_csv(GPT54_TABLES / "paired_significance_by_model.csv")
    g55_metrics = read_csv(GPT55_TABLES / "metrics_summary.csv")
    g55_paired = read_csv(GPT55_TABLES / "paired_contract_effects_by_model.csv")
    g55_sign = read_csv(GPT55_TABLES / "paired_significance_by_model.csv")

    rows = [
        result_row(generation="GPT-4.1 family", model="gpt-4.1-nano", scope="full120", metrics_rows=historical_metrics, paired_rows=historical_paired, sign_rows=historical_sign),
        result_row(generation="GPT-4.1 family", model="gpt-4.1-mini", scope="full120", metrics_rows=historical_metrics, paired_rows=historical_paired, sign_rows=historical_sign),
        result_row(generation="GPT-4.1 family", model="gpt-4.1", scope="full120", metrics_rows=historical_metrics, paired_rows=historical_paired, sign_rows=historical_sign),
        result_row(generation="GPT-5.x family", model="gpt-5.4-mini", scope="full120", metrics_rows=g54_metrics, paired_rows=g54_paired, sign_rows=g54_sign),
        result_row(generation="GPT-5.x family", model="gpt-5.5", scope="full120", metrics_rows=g55_metrics, paired_rows=g55_paired, sign_rows=g55_sign),
    ]
    usage_rows = [
        {"artifact": "gpt-5.4-mini full120", **usage(GPT54_OUTPUTS)},
        {"artifact": "gpt-5.5 full120", **usage(GPT55_OUTPUTS)},
    ]

    write_csv(args.out_dir / "current_model_refresh_summary.csv", rows)
    write_csv(args.out_dir / "current_model_refresh_api_usage.csv", usage_rows)
    write_markdown(args.out_md, rows, usage_rows)
    print(f"wrote current-model refresh summary to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
