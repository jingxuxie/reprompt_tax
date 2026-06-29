#!/usr/bin/env python
"""Summarize uncertainty for current-model paired mitigation effects."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any


CURRENT_MODEL_DIRS = {
    "gpt-5.4-mini": Path("results/tables/openai_gpt54mini_stress_v02_full120"),
    "gpt-5.5": Path("results/tables/openai_gpt55_stress_v02_full120"),
}
OUT_DIR = Path("results/tables/current_model_uncertainty_v02")
OUT_MD = Path("paper/current_model_uncertainty_v02.md")


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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def row_by(rows: list[dict[str, str]], **kwargs: str) -> dict[str, str]:
    for row in rows:
        if all(row[key] == value for key, value in kwargs.items()):
            return row
    raise AssertionError(f"missing row for {kwargs}")


def pvalue(sign_rows: list[dict[str, str]], metric: str) -> float:
    return float(row_by(sign_rows, metric=metric)["two_sided_sign_p"])


def sign_count(sign_rows: list[dict[str, str]], metric: str, field: str) -> int:
    return int(row_by(sign_rows, metric=metric)[field])


def summarize_model(model: str, table_dir: Path) -> dict[str, Any]:
    paired_rows = read_csv(table_dir / "paired_contract_effects_by_model.csv")
    sign_rows = read_csv(table_dir / "paired_significance_by_model.csv")
    paired = row_by(paired_rows, model=model)
    require(int(paired["n_pairs"]) == 120, f"{model} should have 120 paired items")

    if model == "gpt-5.5":
        claim_scope = "headline_current_model_effect"
    elif model == "gpt-5.4-mini":
        claim_scope = "bounded_token_tax_effect_directional_ftga"
    else:
        raise AssertionError(f"unexpected current model: {model}")

    return {
        "model": model,
        "n_pairs": int(paired["n_pairs"]),
        "ftga_delta_pp": round(float(paired["delta_ftga_pp"]), 1),
        "ftga_ci_low_pp": round(float(paired["delta_ftga_pp_ci_low"]), 1),
        "ftga_ci_high_pp": round(float(paired["delta_ftga_pp_ci_high"]), 1),
        "ftga_improved_n": sign_count(sign_rows, "ftga", "positive_n"),
        "ftga_worsened_n": sign_count(sign_rows, "ftga", "negative_n"),
        "ftga_tie_n": sign_count(sign_rows, "ftga", "tie_n"),
        "ftga_sign_p": pvalue(sign_rows, "ftga"),
        "rtt_reduction": round(float(paired["rtt_reduction"]), 3),
        "rtt_ci_low": round(float(paired["rtt_reduction_ci_low"]), 3),
        "rtt_ci_high": round(float(paired["rtt_reduction_ci_high"]), 3),
        "rtt_improved_n": sign_count(sign_rows, "rtt", "positive_n"),
        "rtt_worsened_n": sign_count(sign_rows, "rtt", "negative_n"),
        "rtt_tie_n": sign_count(sign_rows, "rtt", "tie_n"),
        "rtt_sign_p": pvalue(sign_rows, "rtt"),
        "token_tax_reduction": round(float(paired["token_tax_reduction"]), 3),
        "token_tax_ci_low": round(float(paired["token_tax_reduction_ci_low"]), 3),
        "token_tax_ci_high": round(float(paired["token_tax_reduction_ci_high"]), 3),
        "token_tax_improved_n": sign_count(sign_rows, "token_tax", "positive_n"),
        "token_tax_worsened_n": sign_count(sign_rows, "token_tax", "negative_n"),
        "token_tax_tie_n": sign_count(sign_rows, "token_tax", "tie_n"),
        "token_tax_sign_p": pvalue(sign_rows, "token_tax"),
        "unresolved_reduction_pp": round(float(paired["unresolved_reduction_pp"]), 1),
        "unresolved_ci_low_pp": round(float(paired["unresolved_reduction_pp_ci_low"]), 1),
        "unresolved_ci_high_pp": round(float(paired["unresolved_reduction_pp_ci_high"]), 1),
        "unresolved_improved_n": sign_count(sign_rows, "unresolved", "positive_n"),
        "unresolved_worsened_n": sign_count(sign_rows, "unresolved", "negative_n"),
        "unresolved_tie_n": sign_count(sign_rows, "unresolved", "tie_n"),
        "unresolved_sign_p": pvalue(sign_rows, "unresolved"),
        "claim_scope": claim_scope,
    }


def fmt_signed(value: float, decimals: int = 1) -> str:
    return f"{value:+.{decimals}f}"


def fmt_p(value: float) -> str:
    if value < 0.0001:
        return f"{value:.7f}"
    return f"{value:.4f}"


def sign_summary(row: dict[str, Any], prefix: str) -> str:
    return (
        f"{row[f'{prefix}_improved_n']} improved / "
        f"{row[f'{prefix}_worsened_n']} worsened / "
        f"{row[f'{prefix}_tie_n']} tied; p={fmt_p(float(row[f'{prefix}_sign_p']))}"
    )


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    by_model = {row["model"]: row for row in rows}
    require(set(by_model) == set(CURRENT_MODEL_DIRS), f"unexpected current-model rows: {sorted(by_model)}")
    g54 = by_model["gpt-5.4-mini"]
    g55 = by_model["gpt-5.5"]

    lines = [
        "# Current-Model Uncertainty And Claim Scope",
        "",
        "This diagnostic combines paired bootstrap intervals from",
        "`paired_contract_effects_by_model.csv` with exact paired sign tests from",
        "`paired_significance_by_model.csv` for the two full-120 GPT-5.x refresh",
        "runs. It makes no API calls. The intervals are item-bootstrap intervals",
        "over the 120 synthetic paired items, not population confidence intervals,",
        "and they do not replace native/near-native validation.",
        "",
        "## Model-Level Effects",
        "",
        "| Model | FTGA delta, 95% interval | FTGA sign test | RTT reduction, 95% interval | Token-tax reduction, 95% interval | Unresolved reduction, 95% interval | Claim scope |",
        "|---|---:|---|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row['model']} | "
            f"{fmt_signed(row['ftga_delta_pp'])} pp "
            f"[{fmt_signed(row['ftga_ci_low_pp'])}, {fmt_signed(row['ftga_ci_high_pp'])}] | "
            f"{sign_summary(row, 'ftga')} | "
            f"{fmt_signed(row['rtt_reduction'], 3)} "
            f"[{fmt_signed(row['rtt_ci_low'], 3)}, {fmt_signed(row['rtt_ci_high'], 3)}] | "
            f"{fmt_signed(row['token_tax_reduction'], 3)}x "
            f"[{fmt_signed(row['token_tax_ci_low'], 3)}, {fmt_signed(row['token_tax_ci_high'], 3)}] | "
            f"{fmt_signed(row['unresolved_reduction_pp'])} pp "
            f"[{fmt_signed(row['unresolved_ci_low_pp'])}, {fmt_signed(row['unresolved_ci_high_pp'])}] | "
            f"{row['claim_scope']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"The `gpt-5.5` headline survives both bootstrap and exact paired sign-test checks: FTGA improves by "
            f"{g55['ftga_delta_pp']:.1f} pp with a [{g55['ftga_ci_low_pp']:.1f}, {g55['ftga_ci_high_pp']:.1f}] pp item-bootstrap interval, "
            f"and the paired FTGA sign test has {g55['ftga_improved_n']} improved, {g55['ftga_worsened_n']} worsened, "
            f"{g55['ftga_tie_n']} tied items (p={fmt_p(float(g55['ftga_sign_p']))}). "
            f"RTT and token-tax reductions are also one-sided in the observed paired signs.",
            "",
            f"The `gpt-5.4-mini` FTGA interval crosses zero: FTGA improves by {g54['ftga_delta_pp']:.1f} pp, "
            f"but the interval is [{g54['ftga_ci_low_pp']:.1f}, {g54['ftga_ci_high_pp']:.1f}] pp and the paired sign test is "
            f"{g54['ftga_improved_n']} improved versus {g54['ftga_worsened_n']} worsened (p={fmt_p(float(g54['ftga_sign_p']))}). "
            f"The token-tax interval remains positive for `gpt-5.4-mini` "
            f"([{g54['token_tax_ci_low']:.3f}, {g54['token_tax_ci_high']:.3f}]x; p={fmt_p(float(g54['token_tax_sign_p']))}), "
            "so the lower-cost current-model claim should emphasize token-burden reduction and directional FTGA, not universal repair improvement.",
            "",
            "Claim boundary: this artifact strengthens the current-model statistical sensitivity story, but it remains automatic-scoring evidence on a synthetic stress pilot. Native/near-native audit labels are still required before stronger human-validation claims.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    rows = [summarize_model(model, table_dir) for model, table_dir in CURRENT_MODEL_DIRS.items()]
    write_csv(args.out_dir / "current_model_uncertainty.csv", rows)
    write_markdown(args.out_md, rows)
    print(f"wrote current-model uncertainty to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
