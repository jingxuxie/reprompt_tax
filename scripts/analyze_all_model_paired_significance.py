#!/usr/bin/env python
"""All-five-model paired significance checks for contract effects."""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable


TRAJECTORY_PATHS = [
    Path("results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv"),
    Path("results/tables/openai_gpt54mini_stress_v02_full120/trajectory_metrics.csv"),
    Path("results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv"),
]
OUT_DIR = Path("results/tables/all_model_paired_significance_v02")
OUT_MD = Path("paper/all_model_paired_significance_v02.md")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing trajectory table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, f"refusing to write empty paired-significance table {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def generation(model: str) -> str:
    return "GPT-5.x family" if model.startswith("gpt-5") else "GPT-4.1 family"


def transition(baseline_ftga: int, contract_ftga: int) -> str:
    if baseline_ftga == 0 and contract_ftga == 1:
        return "fix"
    if baseline_ftga == 1 and contract_ftga == 0:
        return "regression"
    if baseline_ftga == 0 and contract_ftga == 0:
        return "both_fail"
    return "both_pass"


def sign_test_p(positive_n: int, negative_n: int) -> float:
    n = positive_n + negative_n
    if n == 0:
        return 1.0
    tail_count = sum(math.comb(n, k) for k in range(min(positive_n, negative_n) + 1))
    return min(1.0, 2.0 * tail_count / (2**n))


def format_p(value: float) -> str:
    if value < 0.0001:
        return f"{value:.2e}"
    return f"{value:.4f}"


def paired_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        rows.extend(read_csv(path))
    by_pair: dict[tuple[str, str], dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_pair[(row["model"], row["item_id"])][row["condition"]] = row

    pairs: list[dict[str, Any]] = []
    for (model, item_id), by_condition in sorted(by_pair.items()):
        require({"baseline", "contract"} <= set(by_condition), f"missing baseline/contract pair for {model}/{item_id}")
        baseline = by_condition["baseline"]
        contract = by_condition["contract"]
        require(baseline["language_pair"] == contract["language_pair"], f"language mismatch for {model}/{item_id}")
        require(baseline["task_family"] == contract["task_family"], f"family mismatch for {model}/{item_id}")
        pairs.append(
            {
                "model": model,
                "generation": generation(model),
                "item_id": item_id,
                "language_pair": baseline["language_pair"],
                "task_family": baseline["task_family"],
                "transition": transition(int(baseline["ftga"]), int(contract["ftga"])),
            }
        )
    require(len(pairs) == 600, f"expected 600 paired model-item rows, found {len(pairs)}")
    return pairs


def model_item_summary(
    pairs: list[dict[str, Any]],
    *,
    stratum_type: str,
    stratum: str,
    predicate: Callable[[dict[str, Any]], bool],
) -> dict[str, Any]:
    sub = [row for row in pairs if predicate(row)]
    counts = Counter(row["transition"] for row in sub)
    fixes = counts["fix"]
    regressions = counts["regression"]
    p_value = sign_test_p(fixes, regressions)
    return {
        "unit": "model_item",
        "stratum_type": stratum_type,
        "stratum": stratum,
        "n_units": len(sub),
        "both_pass": counts["both_pass"],
        "both_fail": counts["both_fail"],
        "positive_n": fixes,
        "negative_n": regressions,
        "tie_n": counts["both_pass"] + counts["both_fail"],
        "net_gain_units": fixes - regressions,
        "delta_pp": round(100 * (fixes - regressions) / len(sub), 1) if sub else 0.0,
        "two_sided_sign_p": f"{p_value:.12g}",
        "two_sided_sign_p_display": format_p(p_value),
    }


def item_cluster_summary(
    pairs: list[dict[str, Any]],
    *,
    stratum_type: str,
    stratum: str,
    predicate: Callable[[dict[str, Any]], bool],
) -> dict[str, Any]:
    sub = [row for row in pairs if predicate(row)]
    by_item: dict[str, Counter[str]] = defaultdict(Counter)
    for row in sub:
        by_item[row["item_id"]][row["transition"]] += 1
    positive = negative = tied = 0
    net_sum = 0
    for counts in by_item.values():
        net = counts["fix"] - counts["regression"]
        net_sum += net
        if net > 0:
            positive += 1
        elif net < 0:
            negative += 1
        else:
            tied += 1
    p_value = sign_test_p(positive, negative)
    return {
        "unit": "item_cluster",
        "stratum_type": stratum_type,
        "stratum": stratum,
        "n_units": len(by_item),
        "both_pass": "",
        "both_fail": "",
        "positive_n": positive,
        "negative_n": negative,
        "tie_n": tied,
        "net_gain_units": net_sum,
        "delta_pp": round(100 * net_sum / len(sub), 1) if sub else 0.0,
        "two_sided_sign_p": f"{p_value:.12g}",
        "two_sided_sign_p_display": format_p(p_value),
    }


def build_rows(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    strata: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
        ("overall", "all", lambda row: True),
    ]
    for gen in ("GPT-4.1 family", "GPT-5.x family"):
        strata.append(("generation", gen, lambda row, gen=gen: row["generation"] == gen))
    for family in ("editing_preservation", "output_language_inference", "quote_preservation", "script_register_locale"):
        strata.append(("task_family", family, lambda row, family=family: row["task_family"] == family))
    for lang in ("ar-en", "es-en", "hi-en"):
        strata.append(("language_pair", lang, lambda row, lang=lang: row["language_pair"] == lang))

    rows: list[dict[str, Any]] = []
    for stratum_type, stratum, predicate in strata:
        rows.append(model_item_summary(pairs, stratum_type=stratum_type, stratum=stratum, predicate=predicate))
        rows.append(item_cluster_summary(pairs, stratum_type=stratum_type, stratum=stratum, predicate=predicate))
    return rows


def row_by(rows: list[dict[str, Any]], *, unit: str, stratum_type: str, stratum: str) -> dict[str, Any]:
    matches = [row for row in rows if row["unit"] == unit and row["stratum_type"] == stratum_type and row["stratum"] == stratum]
    require(len(matches) == 1, f"expected one row for {unit}/{stratum_type}/{stratum}, found {len(matches)}")
    return matches[0]


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    overall_model_item = row_by(rows, unit="model_item", stratum_type="overall", stratum="all")
    overall_item = row_by(rows, unit="item_cluster", stratum_type="overall", stratum="all")
    editing_model_item = row_by(rows, unit="model_item", stratum_type="task_family", stratum="editing_preservation")
    editing_item = row_by(rows, unit="item_cluster", stratum_type="task_family", stratum="editing_preservation")

    lines = [
        "# All-Model Paired Significance",
        "",
        "This artifact tests the first-turn contract effect across all five full",
        "120-item model runs. It uses saved trajectory metrics only and makes no",
        "API calls.",
        "",
        "The model-item unit treats each model-item pair as one paired comparison.",
        "The item-cluster unit is more conservative: for each prompt item, it sums",
        "fixes minus regressions across models and then runs a sign test over",
        "net-positive versus net-negative items.",
        "",
        "## Headline Sensitivity",
        "",
        "| Unit | Stratum | N | Positive | Negative | Ties | Net gain | Delta | Sign-test p |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        (
            f"| model_item | all | {overall_model_item['n_units']} | {overall_model_item['positive_n']} | "
            f"{overall_model_item['negative_n']} | {overall_model_item['tie_n']} | "
            f"{overall_model_item['net_gain_units']} | {overall_model_item['delta_pp']} pp | "
            f"{overall_model_item['two_sided_sign_p_display']} |"
        ),
        (
            f"| item_cluster | all | {overall_item['n_units']} | {overall_item['positive_n']} | "
            f"{overall_item['negative_n']} | {overall_item['tie_n']} | "
            f"{overall_item['net_gain_units']} | {overall_item['delta_pp']} pp | "
            f"{overall_item['two_sided_sign_p_display']} |"
        ),
        (
            f"| model_item | editing_preservation | {editing_model_item['n_units']} | "
            f"{editing_model_item['positive_n']} | {editing_model_item['negative_n']} | "
            f"{editing_model_item['tie_n']} | {editing_model_item['net_gain_units']} | "
            f"{editing_model_item['delta_pp']} pp | {editing_model_item['two_sided_sign_p_display']} |"
        ),
        (
            f"| item_cluster | editing_preservation | {editing_item['n_units']} | "
            f"{editing_item['positive_n']} | {editing_item['negative_n']} | "
            f"{editing_item['tie_n']} | {editing_item['net_gain_units']} | "
            f"{editing_item['delta_pp']} pp | {editing_item['two_sided_sign_p_display']} |"
        ),
        "",
        "## Full Table",
        "",
        "| Unit | Stratum type | Stratum | N | Positive | Negative | Ties | Net gain | Delta | Sign-test p |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['unit']} | {row['stratum_type']} | {row['stratum']} | "
            f"{row['n_units']} | {row['positive_n']} | {row['negative_n']} | "
            f"{row['tie_n']} | {row['net_gain_units']} | {row['delta_pp']} pp | "
            f"{row['two_sided_sign_p_display']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "At the model-item unit, the contract yields 67 first-turn fixes and 6",
            "regressions across 600 paired model-item comparisons, a +10.2 pp net",
            "first-turn gain with an exact two-sided sign-test p-value below 0.0001.",
            "",
            "The more conservative item-cluster sensitivity reaches the same",
            "direction: net-positive items substantially outnumber net-negative",
            "items, and the exact sign test remains below 0.0001.",
            "",
            "Editing preservation is the statistically decisive family: it has 61",
            "model-item fixes and 0 regressions, and every net-moving editing item",
            "moves in the positive direction. Other task families are sparse or",
            "balanced, so they should not be described as independently decisive.",
            "",
            "Claim boundary: this is still automatic-score evidence on a synthetic",
            "stress pilot. The item-cluster row addresses repeated-item dependence",
            "inside this pilot, but it does not replace native/near-native validation.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    rows = build_rows(paired_rows(TRAJECTORY_PATHS))
    write_csv(args.out_dir / "all_model_paired_significance.csv", rows)
    write_markdown(args.out_md, rows)
    print(f"wrote all-model paired significance to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
