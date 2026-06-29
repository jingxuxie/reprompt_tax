#!/usr/bin/env python
"""Analyze current-model effect heterogeneity across language pairs and task families."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


CURRENT_TRAJECTORIES = {
    "gpt-5.4-mini": Path("results/tables/openai_gpt54mini_stress_v02_full120/trajectory_metrics.csv"),
    "gpt-5.5": Path("results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv"),
}
OUT_DIR = Path("results/tables/current_model_heterogeneity_v02")
OUT_MD = Path("paper/current_model_heterogeneity_v02.md")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


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


def pct(numerator: float, denominator: float) -> float:
    return round(100.0 * numerator / denominator, 1) if denominator else 0.0


def paired_rows(path: Path, model: str) -> list[tuple[dict[str, str], dict[str, str]]]:
    by_item: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in read_csv(path):
        require(row["model"] == model, f"{path} contains unexpected model {row['model']}")
        by_item[row["item_id"]][row["condition"]] = row

    pairs: list[tuple[dict[str, str], dict[str, str]]] = []
    for item_id, conditions in sorted(by_item.items()):
        require(set(conditions) == {"baseline", "contract"}, f"{model}/{item_id} missing paired conditions")
        pairs.append((conditions["baseline"], conditions["contract"]))
    require(len(pairs) == 120, f"{model} should have 120 paired items, found {len(pairs)}")
    return pairs


def summarize_pairs(
    *,
    model: str,
    pairs: list[tuple[dict[str, str], dict[str, str]]],
    extra: dict[str, Any],
) -> dict[str, Any]:
    n = len(pairs)
    baseline_pass = sum(int(float(baseline["ftga"])) for baseline, _ in pairs)
    contract_pass = sum(int(float(contract["ftga"])) for _, contract in pairs)
    fixed = sum(float(baseline["ftga"]) == 0.0 and float(contract["ftga"]) == 1.0 for baseline, contract in pairs)
    regressed = sum(float(baseline["ftga"]) == 1.0 and float(contract["ftga"]) == 0.0 for baseline, contract in pairs)
    both_pass = sum(float(baseline["ftga"]) == 1.0 and float(contract["ftga"]) == 1.0 for baseline, contract in pairs)
    both_fail = sum(float(baseline["ftga"]) == 0.0 and float(contract["ftga"]) == 0.0 for baseline, contract in pairs)
    baseline_rtt = mean(float(baseline["rtt"]) for baseline, _ in pairs)
    contract_rtt = mean(float(contract["rtt"]) for _, contract in pairs)
    baseline_token_tax = mean(float(baseline["token_tax"]) for baseline, _ in pairs)
    contract_token_tax = mean(float(contract["token_tax"]) for _, contract in pairs)

    row: dict[str, Any] = {
        "model": model,
        **extra,
        "n_pairs": n,
        "baseline_ftga_pct": pct(baseline_pass, n),
        "contract_ftga_pct": pct(contract_pass, n),
        "delta_ftga_pp": round(pct(contract_pass, n) - pct(baseline_pass, n), 1),
        "baseline_fail_n": n - baseline_pass,
        "contract_fail_n": n - contract_pass,
        "fixed_n": fixed,
        "regressed_n": regressed,
        "both_pass_n": both_pass,
        "both_fail_n": both_fail,
        "rtt_reduction": round(baseline_rtt - contract_rtt, 3),
        "token_tax_reduction": round(baseline_token_tax - contract_token_tax, 3),
    }
    return row


def stratum_rows(
    model: str,
    pairs: list[tuple[dict[str, str], dict[str, str]]],
    *,
    field: str,
    stratum_type: str,
) -> list[dict[str, Any]]:
    groups: dict[str, list[tuple[dict[str, str], dict[str, str]]]] = defaultdict(list)
    for baseline, contract in pairs:
        require(baseline[field] == contract[field], f"{model}/{baseline['item_id']} mismatched {field}")
        groups[baseline[field]].append((baseline, contract))
    return [
        summarize_pairs(model=model, pairs=group, extra={"stratum_type": stratum_type, "stratum": stratum})
        for stratum, group in sorted(groups.items())
    ]


def leave_one_rows(
    model: str,
    pairs: list[tuple[dict[str, str], dict[str, str]]],
    *,
    field: str,
    stratum_type: str,
) -> list[dict[str, Any]]:
    strata = sorted({baseline[field] for baseline, _ in pairs})
    rows: list[dict[str, Any]] = []
    for left_out in strata:
        kept = [(baseline, contract) for baseline, contract in pairs if baseline[field] != left_out]
        row = summarize_pairs(
            model=model,
            pairs=kept,
            extra={"left_out_type": stratum_type, "left_out_stratum": left_out},
        )
        if row["delta_ftga_pp"] > 0:
            row["leave_one_signal"] = "positive_remaining_effect"
        elif row["delta_ftga_pp"] == 0:
            row["leave_one_signal"] = "no_remaining_ftga_effect"
        else:
            row["leave_one_signal"] = "negative_remaining_ftga_effect"
        rows.append(row)
    return rows


def fmt_signed(value: float, decimals: int = 1) -> str:
    return f"{value:+.{decimals}f}"


def row_by(rows: list[dict[str, Any]], **kwargs: str) -> dict[str, Any]:
    for row in rows:
        if all(str(row[key]) == value for key, value in kwargs.items()):
            return row
    raise AssertionError(f"missing row for {kwargs}")


def write_markdown(
    path: Path,
    *,
    stratum_rows_all: list[dict[str, Any]],
    leave_one_rows_all: list[dict[str, Any]],
) -> None:
    g55_ar = row_by(stratum_rows_all, model="gpt-5.5", stratum_type="language_pair", stratum="ar-en")
    g55_es = row_by(stratum_rows_all, model="gpt-5.5", stratum_type="language_pair", stratum="es-en")
    g55_hi = row_by(stratum_rows_all, model="gpt-5.5", stratum_type="language_pair", stratum="hi-en")
    g55_edit = row_by(stratum_rows_all, model="gpt-5.5", stratum_type="task_family", stratum="editing_preservation")
    g55_without_edit = row_by(
        leave_one_rows_all,
        model="gpt-5.5",
        left_out_type="task_family",
        left_out_stratum="editing_preservation",
    )
    g54_ar = row_by(stratum_rows_all, model="gpt-5.4-mini", stratum_type="language_pair", stratum="ar-en")
    g54_es = row_by(stratum_rows_all, model="gpt-5.4-mini", stratum_type="language_pair", stratum="es-en")
    g54_hi = row_by(stratum_rows_all, model="gpt-5.4-mini", stratum_type="language_pair", stratum="hi-en")
    g54_without_ar = row_by(
        leave_one_rows_all,
        model="gpt-5.4-mini",
        left_out_type="language_pair",
        left_out_stratum="ar-en",
    )
    g54_without_edit = row_by(
        leave_one_rows_all,
        model="gpt-5.4-mini",
        left_out_type="task_family",
        left_out_stratum="editing_preservation",
    )

    lines = [
        "# Current-Model Heterogeneity",
        "",
        "This diagnostic uses saved full-120 trajectory metrics for `gpt-5.4-mini`",
        "and `gpt-5.5`. It makes no API calls. It asks whether the current-model",
        "refresh headline is broad across language pairs and whether it is",
        "concentrated in a single task family.",
        "",
        "## Stratum Effects",
        "",
        "| Model | Stratum type | Stratum | N | Baseline FTGA | Contract FTGA | Delta | Fixed | Regressed | RTT reduction | Token-tax reduction |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in stratum_rows_all:
        lines.append(
            "| "
            f"{row['model']} | {row['stratum_type']} | {row['stratum']} | {row['n_pairs']} | "
            f"{row['baseline_ftga_pct']:.1f}% | {row['contract_ftga_pct']:.1f}% | "
            f"{fmt_signed(row['delta_ftga_pp'])} pp | {row['fixed_n']} | {row['regressed_n']} | "
            f"{fmt_signed(row['rtt_reduction'], 3)} | {fmt_signed(row['token_tax_reduction'], 3)}x |"
        )

    lines.extend(
        [
            "",
            "## Leave-One-Stratum FTGA Checks",
            "",
            "| Model | Left-out type | Left-out stratum | Kept N | Baseline FTGA | Contract FTGA | Delta | Signal |",
            "|---|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in leave_one_rows_all:
        lines.append(
            "| "
            f"{row['model']} | {row['left_out_type']} | {row['left_out_stratum']} | {row['n_pairs']} | "
            f"{row['baseline_ftga_pct']:.1f}% | {row['contract_ftga_pct']:.1f}% | "
            f"{fmt_signed(row['delta_ftga_pp'])} pp | {row['leave_one_signal']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"The `gpt-5.5` effect is broad across language pairs: ar-en moves {fmt_signed(g55_ar['delta_ftga_pp'])} pp, "
            f"es-en moves {fmt_signed(g55_es['delta_ftga_pp'])} pp, and hi-en moves {fmt_signed(g55_hi['delta_ftga_pp'])} pp. "
            "Every leave-one-language check remains positive, so the current flagship headline is not a single-language artifact.",
            "",
            f"The same `gpt-5.5` effect is task-family concentrated. Editing preservation moves {fmt_signed(g55_edit['delta_ftga_pp'])} pp, "
            f"and removing editing preservation leaves only a {fmt_signed(g55_without_edit['delta_ftga_pp'])} pp FTGA effect because the other families are near ceiling. "
            "This supports a precise paper claim: the benchmark exposes a multilingual editing-preservation burden on the flagship model, not a uniform gain over all task types.",
            "",
            f"The lower-cost `gpt-5.4-mini` result is not robust across strata: ar-en moves {fmt_signed(g54_ar['delta_ftga_pp'])} pp, "
            f"es-en moves {fmt_signed(g54_es['delta_ftga_pp'])} pp, and hi-en moves {fmt_signed(g54_hi['delta_ftga_pp'])} pp. "
            f"Removing ar-en leaves a {fmt_signed(g54_without_ar['delta_ftga_pp'])} pp FTGA effect, and removing editing preservation leaves "
            f"{fmt_signed(g54_without_edit['delta_ftga_pp'])} pp. The lower-cost current-model claim should remain bounded to token burden and directional aggregate FTGA.",
            "",
            "Claim boundary: these are synthetic-pilot automatic-score slices. They should guide paper wording and reviewer discussion, but they do not replace native/near-native validation.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    all_strata: list[dict[str, Any]] = []
    all_leave_one: list[dict[str, Any]] = []
    for model, path in CURRENT_TRAJECTORIES.items():
        pairs = paired_rows(path, model)
        all_strata.extend(stratum_rows(model, pairs, field="language_pair", stratum_type="language_pair"))
        all_strata.extend(stratum_rows(model, pairs, field="task_family", stratum_type="task_family"))
        all_leave_one.extend(leave_one_rows(model, pairs, field="language_pair", stratum_type="language_pair"))
        all_leave_one.extend(leave_one_rows(model, pairs, field="task_family", stratum_type="task_family"))

    write_csv(args.out_dir / "current_model_heterogeneity_by_stratum.csv", all_strata)
    write_csv(args.out_dir / "current_model_heterogeneity_leave_one.csv", all_leave_one)
    write_markdown(args.out_md, stratum_rows_all=all_strata, leave_one_rows_all=all_leave_one)
    print(f"wrote current-model heterogeneity to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
