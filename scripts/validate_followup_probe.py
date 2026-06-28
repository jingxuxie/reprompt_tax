#!/usr/bin/env python
"""Validate non-paper-facing RePromptTax follow-up probe artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


EXPECTED_IDS = 24
EXPECTED_SCORE_ROWS = 182
EXPECTED_TRAJECTORIES = 144
EXPECTED_UNRESOLVED = {
    ("gpt-4.1-nano", "baseline", "ar_en_SD_006"),
    ("gpt-4.1-nano", "contract", "ar_en_SD_006"),
    ("gpt-4.1", "contract", "ar_en_SD_006"),
}
EXPECTED_METRICS = {
    ("gpt-4.1", "baseline"): {"ftga": 70.8, "mean_rtt": 0.29, "unresolved_rate": 0.0, "repair_success_at_1": 100.0, "repair_success_at_2": 100.0},
    ("gpt-4.1", "contract"): {"ftga": 91.7, "mean_rtt": 0.17, "unresolved_rate": 4.2, "repair_success_at_1": 50.0, "repair_success_at_2": 50.0},
    ("gpt-4.1-mini", "baseline"): {"ftga": 70.8, "mean_rtt": 0.29, "unresolved_rate": 0.0, "repair_success_at_1": 100.0, "repair_success_at_2": 100.0},
    ("gpt-4.1-mini", "contract"): {"ftga": 75.0, "mean_rtt": 0.25, "unresolved_rate": 0.0, "repair_success_at_1": 100.0, "repair_success_at_2": 100.0},
    ("gpt-4.1-nano", "baseline"): {"ftga": 70.8, "mean_rtt": 0.38, "unresolved_rate": 4.2, "repair_success_at_1": 85.7, "repair_success_at_2": 85.7},
    ("gpt-4.1-nano", "contract"): {"ftga": 83.3, "mean_rtt": 0.25, "unresolved_rate": 4.2, "repair_success_at_1": 75.0, "repair_success_at_2": 75.0},
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def rounded_percent(value: str) -> float:
    return round(float(value) * 100.0, 1)


def rounded_float(value: str) -> float:
    return round(float(value), 2)


def check_v02_extends_v01(v01_path: Path, v02_path: Path) -> None:
    v01 = load_jsonl(v01_path)
    v02_first_five = []
    for row in load_jsonl(v02_path):
        idx = int(row["id"].rsplit("_", 1)[1])
        if idx <= 5:
            v02_first_five.append(row)
    require(v01 == v02_first_five, "v0.2 first-five-per-cell subset no longer exactly matches v0.1")


def check_probe_ids(path: Path) -> None:
    ids = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    require(len(ids) == EXPECTED_IDS, f"expected {EXPECTED_IDS} probe ids, found {len(ids)}")
    require(len(ids) == len(set(ids)), "duplicate probe ids")
    counts = Counter(item_id.rsplit("_", 1)[0] for item_id in ids)
    require(all(count == 2 for count in counts.values()), f"expected two new ids per cell prefix, found {counts}")
    require(all(int(item_id.rsplit("_", 1)[1]) in (6, 7) for item_id in ids), "probe ids should use v0.2 new items 006 and 007")


def check_scores(path: Path) -> None:
    rows = load_jsonl(path)
    require(len(rows) == EXPECTED_SCORE_ROWS, f"expected {EXPECTED_SCORE_ROWS} score rows, found {len(rows)}")
    first_turn = Counter((row["model"], row["condition"], row["turn"]) for row in rows if row["turn"] == 0)
    expected_first_turn = {
        (model, condition, 0): EXPECTED_IDS
        for model in ("gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1")
        for condition in ("baseline", "contract")
    }
    require(dict(first_turn) == expected_first_turn, f"unexpected first-turn coverage: {first_turn}")

    for row in rows:
        if row["item_id"] == "hi_en_SD_007" and row["condition"] == "contract" and row["turn"] == 0:
            require(row["pass"], f"{row['model']} contract hi_en_SD_007 should pass after Hinglish marker fix")


def check_metrics(summary_path: Path, trajectory_path: Path) -> None:
    summary_rows = load_csv(summary_path)
    require(len(summary_rows) == 6, f"expected 6 metric rows, found {len(summary_rows)}")
    for row in summary_rows:
        key = (row["model"], row["condition"])
        require(key in EXPECTED_METRICS, f"unexpected metric row {key}")
        expected = EXPECTED_METRICS[key]
        actual = {
            "ftga": rounded_percent(row["ftga"]),
            "mean_rtt": rounded_float(row["mean_rtt"]),
            "unresolved_rate": rounded_percent(row["unresolved_rate"]),
            "repair_success_at_1": None if row["repair_success_at_1"] == "" else rounded_percent(row["repair_success_at_1"]),
            "repair_success_at_2": None if row["repair_success_at_2"] == "" else rounded_percent(row["repair_success_at_2"]),
        }
        require(actual == expected, f"metric mismatch for {key}: expected {expected}, got {actual}")

    trajectories = load_csv(trajectory_path)
    require(len(trajectories) == EXPECTED_TRAJECTORIES, f"expected {EXPECTED_TRAJECTORIES} trajectories, found {len(trajectories)}")
    unresolved = {
        (row["model"], row["condition"], row["item_id"])
        for row in trajectories
        if row["unresolved"] == "1"
    }
    require(unresolved == EXPECTED_UNRESOLVED, f"unexpected unresolved trajectories: {unresolved}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root

    check_v02_extends_v01(root / "data/benchmark_stress_v0.1.jsonl", root / "data/benchmark_stress_v0.2.jsonl")
    check_probe_ids(root / "data/stress_v02_new_balanced_24_ids.txt")
    check_scores(root / "results/scores/openai_three_model_stress_v02_new24_auto_scores.jsonl")
    check_metrics(
        root / "results/tables/openai_three_model_stress_v02_new24/metrics_summary.csv",
        root / "results/tables/openai_three_model_stress_v02_new24/trajectory_metrics.csv",
    )
    print("follow-up probe validation passed")


if __name__ == "__main__":
    main()
