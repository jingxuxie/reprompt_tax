#!/usr/bin/env python
"""Item-cluster bootstrap intervals for all-five-model contract effects."""

from __future__ import annotations

import argparse
import csv
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable


TRAJECTORY_PATHS = [
    Path("results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv"),
    Path("results/tables/openai_gpt54mini_stress_v02_full120/trajectory_metrics.csv"),
    Path("results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv"),
]
OUT_DIR = Path("results/tables/all_model_uncertainty_v02")
OUT_MD = Path("paper/all_model_uncertainty_v02.md")
BOOTSTRAP_SEED = 20260629
BOOTSTRAP_SAMPLES = 10000


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing trajectory table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, f"refusing to write empty uncertainty table {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def generation(model: str) -> str:
    return "GPT-5.x family" if model.startswith("gpt-5") else "GPT-4.1 family"


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
                "baseline_ftga": int(baseline["ftga"]),
                "contract_ftga": int(contract["ftga"]),
                "delta": int(contract["ftga"]) - int(baseline["ftga"]),
            }
        )
    require(len(pairs) == 600, f"expected 600 paired model-item rows, found {len(pairs)}")
    return pairs


def percentile(sorted_values: list[float], q: float) -> float:
    require(sorted_values, "cannot compute percentile over empty values")
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = q * (len(sorted_values) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_values) - 1)
    weight = pos - lo
    return sorted_values[lo] * (1 - weight) + sorted_values[hi] * weight


def item_sign_counts(rows: list[dict[str, Any]]) -> tuple[int, int, int]:
    by_item: dict[str, int] = defaultdict(int)
    for row in rows:
        by_item[row["item_id"]] += int(row["delta"])
    counts = Counter("positive" if value > 0 else "negative" if value < 0 else "tie" for value in by_item.values())
    return counts["positive"], counts["negative"], counts["tie"]


def summarize(
    pairs: list[dict[str, Any]],
    *,
    stratum_type: str,
    stratum: str,
    predicate: Callable[[dict[str, Any]], bool],
    rng: random.Random,
    bootstrap_samples: int,
) -> dict[str, Any]:
    rows = [row for row in pairs if predicate(row)]
    require(rows, f"empty stratum {stratum_type}/{stratum}")
    item_ids = sorted({row["item_id"] for row in rows})
    by_item = {item_id: [row for row in rows if row["item_id"] == item_id] for item_id in item_ids}
    n_pairs = len(rows)
    baseline = sum(row["baseline_ftga"] for row in rows) / n_pairs
    contract = sum(row["contract_ftga"] for row in rows) / n_pairs
    delta = contract - baseline
    boot_deltas: list[float] = []
    for _ in range(bootstrap_samples):
        sampled_rows: list[dict[str, Any]] = []
        for item_id in rng.choices(item_ids, k=len(item_ids)):
            sampled_rows.extend(by_item[item_id])
        boot_deltas.append(sum(row["delta"] for row in sampled_rows) / len(sampled_rows))
    boot_deltas.sort()
    positive_items, negative_items, tied_items = item_sign_counts(rows)
    return {
        "stratum_type": stratum_type,
        "stratum": stratum,
        "n_items": len(item_ids),
        "n_model_item_pairs": n_pairs,
        "baseline_ftga_pct": round(100 * baseline, 1),
        "contract_ftga_pct": round(100 * contract, 1),
        "delta_pp": round(100 * delta, 1),
        "cluster_bootstrap_ci_low_pp": round(100 * percentile(boot_deltas, 0.025), 1),
        "cluster_bootstrap_ci_high_pp": round(100 * percentile(boot_deltas, 0.975), 1),
        "net_positive_item_count": positive_items,
        "net_negative_item_count": negative_items,
        "net_tied_item_count": tied_items,
        "bootstrap_samples": bootstrap_samples,
        "bootstrap_seed": BOOTSTRAP_SEED,
    }


def build_rows(pairs: list[dict[str, Any]], *, bootstrap_samples: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    strata: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
        ("overall", "all", lambda row: True),
    ]
    for gen in ("GPT-4.1 family", "GPT-5.x family"):
        strata.append(("generation", gen, lambda row, gen=gen: row["generation"] == gen))
    for family in ("editing_preservation", "output_language_inference", "quote_preservation", "script_register_locale"):
        strata.append(("task_family", family, lambda row, family=family: row["task_family"] == family))
    for lang in ("ar-en", "es-en", "hi-en"):
        strata.append(("language_pair", lang, lambda row, lang=lang: row["language_pair"] == lang))
    return [
        summarize(
            pairs,
            stratum_type=stratum_type,
            stratum=stratum,
            predicate=predicate,
            rng=rng,
            bootstrap_samples=bootstrap_samples,
        )
        for stratum_type, stratum, predicate in strata
    ]


def row_by(rows: list[dict[str, Any]], *, stratum_type: str, stratum: str) -> dict[str, Any]:
    matches = [row for row in rows if row["stratum_type"] == stratum_type and row["stratum"] == stratum]
    require(len(matches) == 1, f"expected one row for {stratum_type}/{stratum}, found {len(matches)}")
    return matches[0]


def fmt_interval(row: dict[str, Any]) -> str:
    return f"{row['delta_pp']:+.1f} pp [{row['cluster_bootstrap_ci_low_pp']:+.1f}, {row['cluster_bootstrap_ci_high_pp']:+.1f}]"


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    overall = row_by(rows, stratum_type="overall", stratum="all")
    editing = row_by(rows, stratum_type="task_family", stratum="editing_preservation")
    ar_en = row_by(rows, stratum_type="language_pair", stratum="ar-en")
    es_en = row_by(rows, stratum_type="language_pair", stratum="es-en")
    hi_en = row_by(rows, stratum_type="language_pair", stratum="hi-en")

    lines = [
        "# All-Model Clustered Uncertainty",
        "",
        "This artifact estimates item-cluster bootstrap intervals for the",
        "first-turn contract effect across all five full 120-item runs. It uses",
        "saved trajectory metrics only and makes no API calls. The bootstrap",
        "resamples prompt items, keeping all selected model rows for each item,",
        "so it is a repeated-prompt sensitivity check rather than a population",
        "confidence interval.",
        "",
        "## Cluster Bootstrap Table",
        "",
        "| Stratum type | Stratum | Items | Pairs | Baseline FTGA | Contract FTGA | Delta, 95% interval | Net-positive items | Net-negative items |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['stratum_type']} | {row['stratum']} | {row['n_items']} | "
            f"{row['n_model_item_pairs']} | {row['baseline_ftga_pct']}% | "
            f"{row['contract_ftga_pct']}% | {fmt_interval(row)} | "
            f"{row['net_positive_item_count']} | {row['net_negative_item_count']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"Across all five full-run models, baseline FTGA is {overall['baseline_ftga_pct']:.1f}% and contract FTGA is {overall['contract_ftga_pct']:.1f}%, "
            f"for a {fmt_interval(overall)} item-cluster bootstrap interval. "
            f"The prompt-level movement is {overall['net_positive_item_count']} net-positive items versus {overall['net_negative_item_count']} net-negative items.",
            "",
            f"The editing-preservation family remains the dominant and most stable slice: its effect is {fmt_interval(editing)} with "
            f"{editing['net_positive_item_count']} net-positive items and {editing['net_negative_item_count']} net-negative items.",
            "",
            f"Language-pair uncertainty is heterogeneous: Arabic-English is {fmt_interval(ar_en)}, Spanish-English is {fmt_interval(es_en)}, "
            f"and Hindi-English is {fmt_interval(hi_en)}. This supports the current caveat that Hindi-English is near ceiling in this synthetic pilot.",
            "",
            "Claim boundary: this is automatic-score uncertainty over a synthetic stress pilot. It strengthens the robustness story under prompt resampling, but it does not replace native/near-native validation.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    parser.add_argument("--bootstrap-samples", type=int, default=BOOTSTRAP_SAMPLES)
    parser.add_argument("--bootstrap-seed", type=int, default=BOOTSTRAP_SEED)
    args = parser.parse_args()

    rows = build_rows(paired_rows(TRAJECTORY_PATHS), bootstrap_samples=args.bootstrap_samples, seed=args.bootstrap_seed)
    write_csv(args.out_dir / "all_model_cluster_bootstrap.csv", rows)
    write_markdown(args.out_md, rows)
    print(f"wrote all-model clustered uncertainty to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
