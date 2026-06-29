#!/usr/bin/env python
"""Select a compact diagnostic sentinel suite from saved full-run trajectories."""

from __future__ import annotations

import argparse
import ast
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


TRAJECTORY_PATHS = [
    Path("results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv"),
    Path("results/tables/openai_gpt54mini_stress_v02_full120/trajectory_metrics.csv"),
    Path("results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv"),
]
BENCHMARK_PATH = Path("data/benchmark_stress_v0.2.jsonl")
OUT_DIR = Path("results/tables/sentinel_suite_v02")
OUT_MD = Path("paper/sentinel_suite_v02.md")
OUT_IDS = Path("data/stress_v02_sentinel24_ids.txt")

EXPECTED_MODELS = {"gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-5.4-mini", "gpt-5.5"}
SENTINEL_SIZE = 24


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing sentinel input {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, f"refusing to write empty sentinel table {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_benchmark(path: Path) -> dict[str, dict[str, Any]]:
    require(path.exists(), f"missing benchmark {path}")
    rows: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            item_id = row["id"]
            require(item_id not in rows, f"duplicate benchmark item {item_id} at line {line_no}")
            rows[item_id] = row
    require(len(rows) == 120, f"expected 120 benchmark rows, found {len(rows)}")
    return rows


def parse_failure_types(value: str) -> list[str]:
    if value in {"", "[]"}:
        return []
    parsed = ast.literal_eval(value)
    require(isinstance(parsed, list), f"expected list-like failure types, got {value}")
    return [str(item) for item in parsed]


def transition(baseline_ftga: int, contract_ftga: int) -> str:
    if baseline_ftga == 0 and contract_ftga == 1:
        return "fix"
    if baseline_ftga == 1 and contract_ftga == 0:
        return "regression"
    if baseline_ftga == 0 and contract_ftga == 0:
        return "both_fail"
    return "both_pass"


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
        require(baseline["task_family"] == contract["task_family"], f"task-family mismatch for {model}/{item_id}")
        baseline_ftga = int(baseline["ftga"])
        contract_ftga = int(contract["ftga"])
        pairs.append(
            {
                "item_id": item_id,
                "model": model,
                "language_pair": baseline["language_pair"],
                "task_family": baseline["task_family"],
                "baseline_ftga": baseline_ftga,
                "contract_ftga": contract_ftga,
                "baseline_unresolved": int(baseline["unresolved"]),
                "contract_unresolved": int(contract["unresolved"]),
                "transition": transition(baseline_ftga, contract_ftga),
                "baseline_failure_types": parse_failure_types(baseline["first_failure_types"]),
                "contract_failure_types": parse_failure_types(contract["first_failure_types"]),
            }
        )
    require(len(pairs) == 600, f"expected 600 paired model-item rows, found {len(pairs)}")
    require({row["model"] for row in pairs} == EXPECTED_MODELS, f"unexpected models: {sorted({row['model'] for row in pairs})}")
    return pairs


def item_rows(pairs: list[dict[str, Any]], benchmark: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pairs:
        grouped[row["item_id"]].append(row)

    rows: list[dict[str, Any]] = []
    for item_id, group in sorted(grouped.items()):
        require(len(group) == 5, f"expected five model rows for {item_id}, found {len(group)}")
        require(item_id in benchmark, f"trajectory item missing benchmark row: {item_id}")
        bench = benchmark[item_id]
        language_pair = group[0]["language_pair"]
        task_family = group[0]["task_family"]
        require(all(row["language_pair"] == language_pair for row in group), f"language mismatch inside {item_id}")
        require(all(row["task_family"] == task_family for row in group), f"family mismatch inside {item_id}")
        require(bench["language_pair"] == language_pair, f"benchmark language mismatch for {item_id}")
        require(bench["task_family"] == task_family, f"benchmark family mismatch for {item_id}")

        transition_counts = Counter(row["transition"] for row in group)
        baseline_fail_pairs = sum(1 for row in group if row["baseline_ftga"] == 0)
        contract_fail_pairs = sum(1 for row in group if row["contract_ftga"] == 0)
        unresolved_pairs = sum(row["baseline_unresolved"] + row["contract_unresolved"] for row in group)
        current_contract_fail_pairs = sum(1 for row in group if row["model"].startswith("gpt-5") and row["contract_ftga"] == 0)
        gpt55_contract_fail = any(row["model"] == "gpt-5.5" and row["contract_ftga"] == 0 for row in group)
        gpt54_regression = any(row["model"] == "gpt-5.4-mini" and row["transition"] == "regression" for row in group)
        failure_types = Counter(
            failure_type
            for row in group
            for failure_type in [*row["baseline_failure_types"], *row["contract_failure_types"]]
        )
        score = (
            10 * int(gpt55_contract_fail)
            + 8 * current_contract_fail_pairs
            + 6 * transition_counts["regression"]
            + 4 * transition_counts["fix"]
            + 3 * contract_fail_pairs
            + 2 * unresolved_pairs
            + baseline_fail_pairs
        )
        reasons: list[str] = []
        if gpt55_contract_fail:
            reasons.append("gpt-5.5 contract residual")
        if current_contract_fail_pairs:
            reasons.append(f"{current_contract_fail_pairs} GPT-5.x contract fail pairs")
        if transition_counts["regression"]:
            reasons.append(f"{transition_counts['regression']} contract regressions")
        if transition_counts["fix"]:
            reasons.append(f"{transition_counts['fix']} contract fixes")
        if unresolved_pairs:
            reasons.append(f"{unresolved_pairs} unresolved trajectory flags")
        if not reasons and baseline_fail_pairs:
            reasons.append(f"{baseline_fail_pairs} baseline fail pairs")
        rows.append(
            {
                "item_id": item_id,
                "language_pair": language_pair,
                "task_family": task_family,
                "stress_tag": bench.get("stress_tag", ""),
                "selection_score": score,
                "baseline_fail_pairs": baseline_fail_pairs,
                "contract_fail_pairs": contract_fail_pairs,
                "contract_fix_pairs": transition_counts["fix"],
                "contract_regression_pairs": transition_counts["regression"],
                "both_fail_pairs": transition_counts["both_fail"],
                "unresolved_flags": unresolved_pairs,
                "current_contract_fail_pairs": current_contract_fail_pairs,
                "gpt55_contract_residual": int(gpt55_contract_fail),
                "gpt54_contract_regression": int(gpt54_regression),
                "failure_type_signature": ";".join(f"{key}:{value}" for key, value in sorted(failure_types.items())),
                "selection_rationale": "; ".join(reasons) if reasons else "balanced cell representative",
            }
        )
    require(len(rows) == 120, f"expected 120 item rows, found {len(rows)}")
    return rows


def select_sentinel(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_stratum: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_stratum[(row["language_pair"], row["task_family"])].append(row)
    require(len(by_stratum) == 12, f"expected 12 strata, found {len(by_stratum)}")
    selected_by_id: dict[str, dict[str, Any]] = {}
    for stratum, group in sorted(by_stratum.items()):
        require(len(group) == 10, f"{stratum} expected 10 items, found {len(group)}")
        ranked = sorted(group, key=lambda row: (-int(row["selection_score"]), row["item_id"]))
        for rank, row in enumerate(ranked, start=1):
            row["stratum_rank"] = rank
        selected_by_id[ranked[0]["item_id"]] = ranked[0]

    for row in sorted(rows, key=lambda item: (-int(item["selection_score"]), item["item_id"])):
        if len(selected_by_id) >= SENTINEL_SIZE:
            break
        selected_by_id.setdefault(row["item_id"], row)

    selected = sorted(
        selected_by_id.values(),
        key=lambda row: (row["language_pair"], row["task_family"], int(row["stratum_rank"]), row["item_id"]),
    )
    require(len(selected) == SENTINEL_SIZE, f"expected {SENTINEL_SIZE} sentinel rows, found {len(selected)}")
    return selected


def coverage_summary(all_rows: list[dict[str, Any]], selected_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected_ids = {row["item_id"] for row in selected_rows}

    def total(field: str, rows: list[dict[str, Any]]) -> int:
        return sum(int(row[field]) for row in rows)

    metrics = [
        ("baseline_fail_pairs", "Baseline first-turn failure pairs"),
        ("contract_fix_pairs", "Contract fix pairs"),
        ("contract_regression_pairs", "Contract regression pairs"),
        ("contract_fail_pairs", "Contract first-turn failure pairs"),
        ("unresolved_flags", "Unresolved trajectory flags"),
        ("current_contract_fail_pairs", "GPT-5.x contract failure pairs"),
        ("gpt55_contract_residual", "GPT-5.5 contract residual items"),
        ("gpt54_contract_regression", "GPT-5.4-mini contract-regression items"),
    ]
    rows: list[dict[str, Any]] = []
    for field, label in metrics:
        full_n = total(field, all_rows)
        selected_n = total(field, selected_rows)
        rows.append(
            {
                "metric": field,
                "label": label,
                "full_n": full_n,
                "sentinel_n": selected_n,
                "coverage_pct": round(100 * selected_n / full_n, 1) if full_n else 0.0,
            }
        )

    strata = Counter((row["language_pair"], row["task_family"]) for row in selected_rows)
    rows.append(
        {
            "metric": "covered_cells",
            "label": "Language-family cells with at least one selected item",
            "full_n": 12,
            "sentinel_n": len(strata),
            "coverage_pct": 100.0 if len(strata) == 12 and all(count >= 1 for count in strata.values()) else 0.0,
        }
    )
    return rows


def write_ids(path: Path, selected_rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(row["item_id"] for row in selected_rows) + "\n", encoding="utf-8")


def pct(row: dict[str, Any]) -> str:
    return f"{float(row['coverage_pct']):.1f}%"


def write_markdown(path: Path, selected_rows: list[dict[str, Any]], summary_rows: list[dict[str, Any]]) -> None:
    by_metric = {row["metric"]: row for row in summary_rows}
    lines = [
        "# Sentinel Suite v0.2",
        "",
        "This no-API artifact selects a compact 24-item diagnostic suite from the",
        "paper-facing 120-item stress benchmark. It is intended for future fast",
        "model checks and reviewer inspection, not as a replacement for the full",
        "benchmark or native/near-native validation.",
        "",
        "## Selection Rule",
        "",
        "The suite first selects the top-ranked item from each language-pair/task-family",
        "cell so every stratum is represented, then fills the remaining slots by",
        "global saved full-run diagnostic density. The score prioritizes GPT-5.5",
        "contract residuals, GPT-5.x contract failures, contract regressions,",
        "contract fixes, remaining contract failures, unresolved trajectories, and",
        "baseline first-turn failures. Ties are broken by item ID, making the suite",
        "deterministic.",
        "",
        "## Coverage Summary",
        "",
        "| Signal | Full set | Sentinel set | Coverage |",
        "|---|---:|---:|---:|",
    ]
    for metric in (
        "baseline_fail_pairs",
        "contract_fix_pairs",
        "contract_regression_pairs",
        "contract_fail_pairs",
        "unresolved_flags",
        "current_contract_fail_pairs",
        "gpt55_contract_residual",
        "gpt54_contract_regression",
        "covered_cells",
    ):
        row = by_metric[metric]
        lines.append(f"| {row['label']} | {row['full_n']} | {row['sentinel_n']} | {pct(row)} |")

    lines.extend(
        [
            "",
            "## Selected Items",
            "",
            "| Item | Language | Family | Score | Fixes | Regressions | Contract failures | Rationale |",
            "|---|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in selected_rows:
        lines.append(
            f"| `{row['item_id']}` | {row['language_pair']} | {row['task_family']} | "
            f"{row['selection_score']} | {row['contract_fix_pairs']} | "
            f"{row['contract_regression_pairs']} | {row['contract_fail_pairs']} | "
            f"{row['selection_rationale']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"The 24-item suite covers all 12 language-family cells and captures "
            f"{by_metric['contract_fix_pairs']['sentinel_n']} of {by_metric['contract_fix_pairs']['full_n']} "
            f"contract fix pairs ({pct(by_metric['contract_fix_pairs'])}). It also captures "
            f"{by_metric['contract_regression_pairs']['sentinel_n']} of {by_metric['contract_regression_pairs']['full_n']} "
            f"contract regression pairs and all {by_metric['gpt55_contract_residual']['full_n']} GPT-5.5 contract residual items.",
            "",
            "Use `data/stress_v02_sentinel24_ids.txt` as an item-id file for future",
            "smoke runs when a full 120-item model refresh is too expensive. Any",
            "paper-facing model claim should still be confirmed on the full benchmark",
            "and, for cultural/register claims, by completed qualified human/native labels.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    parser.add_argument("--out-ids", type=Path, default=OUT_IDS)
    args = parser.parse_args()

    benchmark = load_benchmark(BENCHMARK_PATH)
    pairs = paired_rows(TRAJECTORY_PATHS)
    rows = item_rows(pairs, benchmark)
    selected = select_sentinel(rows)
    summary = coverage_summary(rows, selected)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "sentinel_item_scores.csv", sorted(rows, key=lambda row: row["item_id"]))
    write_csv(args.out_dir / "sentinel_selected_items.csv", selected)
    write_csv(args.out_dir / "sentinel_coverage_summary.csv", summary)
    write_ids(args.out_ids, selected)
    write_markdown(args.out_md, selected, summary)
    print(f"wrote sentinel suite to {args.out_md}, {args.out_dir}, and {args.out_ids}")


if __name__ == "__main__":
    main()
