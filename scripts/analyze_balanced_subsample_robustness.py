#!/usr/bin/env python
"""Simulate balanced pilot subsamples from saved full-run trajectories."""

from __future__ import annotations

import argparse
import csv
import random
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any


TRAJECTORY_PATHS = [
    Path("results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv"),
    Path("results/tables/openai_gpt54mini_stress_v02_full120/trajectory_metrics.csv"),
    Path("results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv"),
]
OUT_DIR = Path("results/tables/balanced_subsample_robustness_v02")
OUT_MD = Path("paper/balanced_subsample_robustness_v02.md")

K_PER_CELL = [1, 2, 3, 4, 5, 8, 10]
STRATA_PER_DATASET = 12
ITEMS_PER_CELL = 10
SIMULATION_REPS = 2000
SIMULATION_SEED = 20260629


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing subsample input {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, f"refusing to write empty subsample table {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    require(ordered, "cannot compute percentile over empty values")
    pos = q * (len(ordered) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    weight = pos - lo
    return ordered[lo] * (1 - weight) + ordered[hi] * weight


def sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def paired_records(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        rows.extend(read_csv(path))

    by_pair: dict[tuple[str, str], dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_pair[(row["model"], row["item_id"])][row["condition"]] = row

    records: list[dict[str, Any]] = []
    for (model, item_id), by_condition in sorted(by_pair.items()):
        require({"baseline", "contract"} <= set(by_condition), f"missing baseline/contract pair for {model}/{item_id}")
        baseline = by_condition["baseline"]
        contract = by_condition["contract"]
        require(baseline["language_pair"] == contract["language_pair"], f"language mismatch for {model}/{item_id}")
        require(baseline["task_family"] == contract["task_family"], f"family mismatch for {model}/{item_id}")
        records.append(
            {
                "population": model,
                "model": model,
                "item_id": item_id,
                "language_pair": baseline["language_pair"],
                "task_family": baseline["task_family"],
                "stratum": f"{baseline['language_pair']}|{baseline['task_family']}",
                "delta": int(contract["ftga"]) - int(baseline["ftga"]),
            }
        )
    require(len(records) == 600, f"expected 600 model-item records, found {len(records)}")
    return records


def populations(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_population: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        by_population[row["model"]].append(row)
        by_population["all_models"].append({**row, "population": "all_models"})
    require(set(by_population) == {"all_models", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-5.4-mini", "gpt-5.5"}, f"unexpected populations {sorted(by_population)}")
    return dict(by_population)


def group_by_item(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_item[row["item_id"]].append(row)
    return dict(by_item)


def stratum_items(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    by_stratum: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        by_stratum[row["stratum"]].add(row["item_id"])
    require(len(by_stratum) == STRATA_PER_DATASET, f"expected {STRATA_PER_DATASET} strata, found {len(by_stratum)}")
    out = {stratum: sorted(items) for stratum, items in by_stratum.items()}
    for stratum, items in out.items():
        require(len(items) == ITEMS_PER_CELL, f"{stratum} expected {ITEMS_PER_CELL} items, found {len(items)}")
    return out


def delta_pp(rows: list[dict[str, Any]]) -> float:
    return 100 * mean(float(row["delta"]) for row in rows)


def full_summary(population: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter("improved" if row["delta"] > 0 else "worsened" if row["delta"] < 0 else "tied" for row in rows)
    items = sorted({row["item_id"] for row in rows})
    return {
        "population": population,
        "n_items": len(items),
        "n_model_item_pairs": len(rows),
        "full_delta_pp": round(delta_pp(rows), 1),
        "full_improved_pairs": counts["improved"],
        "full_worsened_pairs": counts["worsened"],
        "full_tied_pairs": counts["tied"],
    }


def simulate_population(
    population: str,
    rows: list[dict[str, Any]],
    *,
    reps: int,
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    full = full_summary(population, rows)
    full_delta = float(full["full_delta_pp"])
    full_direction = sign(full_delta)
    by_item = group_by_item(rows)
    by_stratum = stratum_items(rows)
    rng = random.Random(seed + sum(ord(ch) for ch in population))

    summary_rows: list[dict[str, Any]] = []
    for k in K_PER_CELL:
        sample_reps = 1 if k == ITEMS_PER_CELL else reps
        deltas: list[float] = []
        for _ in range(sample_reps):
            sampled_rows: list[dict[str, Any]] = []
            for stratum in sorted(by_stratum):
                sampled_items = by_stratum[stratum] if k == ITEMS_PER_CELL else rng.sample(by_stratum[stratum], k)
                for item_id in sampled_items:
                    sampled_rows.extend(by_item[item_id])
            deltas.append(delta_pp(sampled_rows))
        errors = [abs(value - full_delta) for value in deltas]
        summary_rows.append(
            {
                **full,
                "k_per_cell": k,
                "sample_items": k * STRATA_PER_DATASET,
                "sample_model_item_pairs": k * STRATA_PER_DATASET * (len(rows) // len({row["item_id"] for row in rows})),
                "simulation_reps": sample_reps,
                "mean_delta_pp": round(mean(deltas), 1),
                "median_delta_pp": round(median(deltas), 1),
                "p05_delta_pp": round(percentile(deltas, 0.05), 1),
                "p95_delta_pp": round(percentile(deltas, 0.95), 1),
                "min_delta_pp": round(min(deltas), 1),
                "max_delta_pp": round(max(deltas), 1),
                "positive_fraction": round(sum(1 for value in deltas if value > 0) / sample_reps, 3),
                "full_direction_recovered_fraction": round(sum(1 for value in deltas if sign(value) == full_direction) / sample_reps, 3),
                "within_5pp_fraction": round(sum(1 for value in errors if value <= 5.0) / sample_reps, 3),
                "median_abs_error_pp": round(median(errors), 1),
                "p95_abs_error_pp": round(percentile(errors, 0.95), 1),
                "simulation_seed": seed,
            }
        )
    return full, summary_rows


def build_rows(records: list[dict[str, Any]], *, reps: int, seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    full_rows: list[dict[str, Any]] = []
    simulation_rows: list[dict[str, Any]] = []
    for population, rows in sorted(populations(records).items()):
        full, simulated = simulate_population(population, rows, reps=reps, seed=seed)
        full_rows.append(full)
        simulation_rows.extend(simulated)
    return full_rows, simulation_rows


def row_by(rows: list[dict[str, Any]], *, population: str, k_per_cell: int) -> dict[str, Any]:
    matches = [row for row in rows if row["population"] == population and int(row["k_per_cell"]) == k_per_cell]
    require(len(matches) == 1, f"expected one simulation row for {population}/{k_per_cell}, found {len(matches)}")
    return matches[0]


def write_markdown(path: Path, full_rows: list[dict[str, Any]], simulation_rows: list[dict[str, Any]]) -> None:
    all_48 = row_by(simulation_rows, population="all_models", k_per_cell=4)
    g55_48 = row_by(simulation_rows, population="gpt-5.5", k_per_cell=4)
    g54_48 = row_by(simulation_rows, population="gpt-5.4-mini", k_per_cell=4)
    mini_48 = row_by(simulation_rows, population="gpt-4.1-mini", k_per_cell=4)

    lines = [
        "# Balanced Subsample Robustness",
        "",
        "This no-API diagnostic simulates balanced stratified pilots from the saved",
        "full 120-item paired trajectories. Each simulated sample chooses the same",
        "number of items from each language-pair/task-family cell, then recomputes",
        "the baseline-vs-contract first-turn alignment effect. It tests whether",
        "small pilots recover the full-run direction and approximate magnitude; it",
        "does not replace the full-run results or native/near-native validation.",
        "",
        "## Full-Run Effects",
        "",
        "| Population | Items | Model-item pairs | Full FTGA delta | Improved pairs | Worsened pairs | Tied pairs |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in full_rows:
        lines.append(
            f"| {row['population']} | {row['n_items']} | {row['n_model_item_pairs']} | "
            f"{row['full_delta_pp']:+.1f} pp | {row['full_improved_pairs']} | "
            f"{row['full_worsened_pairs']} | {row['full_tied_pairs']} |"
        )
    lines.extend(
        [
            "",
            "## Simulated Balanced Pilots",
            "",
            "| Population | Items | k/cell | Full delta | Median pilot delta | 5--95% pilot delta | Direction recovered | Within 5 pp | Median abs. error |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in simulation_rows:
        lines.append(
            f"| {row['population']} | {row['sample_items']} | {row['k_per_cell']} | "
            f"{row['full_delta_pp']:+.1f} pp | {row['median_delta_pp']:+.1f} pp | "
            f"[{row['p05_delta_pp']:+.1f}, {row['p95_delta_pp']:+.1f}] pp | "
            f"{100 * row['full_direction_recovered_fraction']:.1f}% | "
            f"{100 * row['within_5pp_fraction']:.1f}% | {row['median_abs_error_pp']:.1f} pp |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"At the 48-item balanced-pilot scale (four items per cell), the all-model aggregate recovers the full positive direction in "
            f"{100 * all_48['full_direction_recovered_fraction']:.1f}% of simulations and lands within 5 pp of the full +{all_48['full_delta_pp']:.1f} pp effect in "
            f"{100 * all_48['within_5pp_fraction']:.1f}% of simulations.",
            "",
            f"The GPT-5.5 headline is stable under the same 48-item design: the simulated direction is recovered in "
            f"{100 * g55_48['full_direction_recovered_fraction']:.1f}% of samples, with median pilot delta {g55_48['median_delta_pp']:+.1f} pp versus the full "
            f"{g55_48['full_delta_pp']:+.1f} pp effect.",
            "",
            f"Weaker effects remain appropriately unstable: at 48 items, `gpt-5.4-mini` recovers the positive direction in "
            f"{100 * g54_48['full_direction_recovered_fraction']:.1f}% of simulations and `gpt-4.1-mini` in "
            f"{100 * mini_48['full_direction_recovered_fraction']:.1f}%. This supports the current claim boundary: the flagship current-model result is robust, while smaller-effect models should remain bounded.",
            "",
            "Claim boundary: this artifact is a subsampling sensitivity check over saved automatic-score trajectories. It supports fast iteration and pilot design, but full paper claims should remain anchored to the complete 120-item runs and to completed human/native review when available.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    parser.add_argument("--simulation-reps", type=int, default=SIMULATION_REPS)
    parser.add_argument("--simulation-seed", type=int, default=SIMULATION_SEED)
    args = parser.parse_args()

    full_rows, simulation_rows = build_rows(paired_records(TRAJECTORY_PATHS), reps=args.simulation_reps, seed=args.simulation_seed)
    write_csv(args.out_dir / "balanced_subsample_full_effects.csv", full_rows)
    write_csv(args.out_dir / "balanced_subsample_simulations.csv", simulation_rows)
    write_markdown(args.out_md, full_rows, simulation_rows)
    print(f"wrote balanced-subsample robustness to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
