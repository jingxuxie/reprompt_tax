#!/usr/bin/env python
"""Analyze the tiny v0.3 coverage-expansion model smoke."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def trajectory(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: int(row["turn"]))
    first = ordered[0]
    rtt = 3
    for row in ordered:
        if row["pass"]:
            rtt = int(row["turn"])
            break
    return {
        "item_id": first["item_id"],
        "model": first["model"],
        "condition": first["condition"],
        "ftga": 1 if bool(first["pass"]) else 0,
        "rtt": rtt,
        "unresolved": 1 if rtt == 3 else 0,
        "first_failure_types": ";".join(first.get("failure_types") or []),
        "turns": len(ordered),
    }


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(rows, f"cannot write empty CSV {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def summarize(
    *,
    scores: list[dict[str, Any]],
    trajectories: list[dict[str, Any]],
    model_output_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    by_condition: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in trajectories:
        by_condition[row["condition"]].append(row)

    baseline = by_condition["baseline"]
    contract = by_condition["contract"]
    return {
        "model": trajectories[0]["model"],
        "benchmark": "v0.3 coverage expansion smoke",
        "items": len({row["item_id"] for row in trajectories}),
        "trajectories": len(trajectories),
        "api_response_rows": len(model_output_rows),
        "scored_response_rows": len(scores),
        "baseline_ftga": sum(row["ftga"] for row in baseline) / len(baseline),
        "contract_ftga": sum(row["ftga"] for row in contract) / len(contract),
        "ftga_delta_pp": 100 * (sum(row["ftga"] for row in contract) / len(contract) - sum(row["ftga"] for row in baseline) / len(baseline)),
        "baseline_mean_rtt": sum(row["rtt"] for row in baseline) / len(baseline),
        "contract_mean_rtt": sum(row["rtt"] for row in contract) / len(contract),
        "baseline_unresolved": sum(row["unresolved"] for row in baseline),
        "contract_unresolved": sum(row["unresolved"] for row in contract),
        "input_tokens": sum(int(row["input_tokens"]) for row in model_output_rows),
        "output_tokens": sum(int(row["output_tokens"]) for row in model_output_rows),
        "total_tokens": sum(int(row["input_tokens"]) + int(row["output_tokens"]) for row in model_output_rows),
    }


def analyze(
    *,
    benchmark_rows: list[dict[str, Any]],
    scores: list[dict[str, Any]],
    model_output_rows: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    benchmark = {row["id"]: row for row in benchmark_rows}
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in scores:
        grouped[(row["item_id"], row["model"], row["condition"])].append(row)
    trajectories = [trajectory(rows) for rows in grouped.values()]
    require(len(trajectories) == 12, f"expected 12 smoke trajectories, found {len(trajectories)}")

    by_item: dict[str, dict[str, Any]] = {}
    for row in trajectories:
        by_item.setdefault(row["item_id"], {"item_id": row["item_id"]})
        by_item[row["item_id"]][f"{row['condition']}_ftga"] = row["ftga"]
        by_item[row["item_id"]][f"{row['condition']}_rtt"] = row["rtt"]
        by_item[row["item_id"]][f"{row['condition']}_first_failure_types"] = row["first_failure_types"]

    by_slice: list[dict[str, Any]] = []
    for item_id, row in sorted(by_item.items(), key=lambda item: benchmark[item[0]]["coverage_slice"]):
        item = benchmark[item_id]
        by_slice.append(
            {
                "coverage_slice": item["coverage_slice"],
                "item_id": item_id,
                "language_pair": item["language_pair"],
                "expected_response_language": item["expected_response_language"],
                "baseline_ftga": row.get("baseline_ftga", ""),
                "contract_ftga": row.get("contract_ftga", ""),
                "baseline_rtt": row.get("baseline_rtt", ""),
                "contract_rtt": row.get("contract_rtt", ""),
                "baseline_first_failure_types": row.get("baseline_first_failure_types", ""),
                "contract_first_failure_types": row.get("contract_first_failure_types", ""),
            }
        )

    first_turn_failures: list[dict[str, Any]] = []
    for row in scores:
        if int(row["turn"]) != 0 or row["pass"]:
            continue
        item = benchmark[row["item_id"]]
        first_turn_failures.append(
            {
                "item_id": row["item_id"],
                "coverage_slice": item["coverage_slice"],
                "condition": row["condition"],
                "failure_types": ";".join(row.get("failure_types") or []),
                "response_snippet": str(row["response"]).replace("\n", " ")[:220],
            }
        )

    summary = summarize(scores=scores, trajectories=trajectories, model_output_rows=model_output_rows)
    return summary, by_slice, first_turn_failures


def write_markdown(path: Path, summary: dict[str, Any], by_slice: list[dict[str, Any]], failures: list[dict[str, Any]]) -> None:
    model_name = str(summary["model"])
    lines = [
        f"# {model_name} v0.3 Coverage Smoke",
        "",
        "This six-item smoke uses one row from each synthetic v0.3 coverage-expansion slice.",
        "It is not paper-facing model result evidence and requires native validation before claims.",
        "The purpose is to verify that non-English target-content rows are runnable, scoreable, and worth a bounded follow-up.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| model | {summary['model']} |",
        f"| items | {summary['items']} |",
        f"| trajectories | {summary['trajectories']} |",
        f"| api_response_rows | {summary['api_response_rows']} |",
        f"| baseline_ftga | {pct(float(summary['baseline_ftga']))} |",
        f"| contract_ftga | {pct(float(summary['contract_ftga']))} |",
        f"| ftga_delta | {summary['ftga_delta_pp']:.1f} pp |",
        f"| baseline_mean_rtt | {summary['baseline_mean_rtt']:.3f} |",
        f"| contract_mean_rtt | {summary['contract_mean_rtt']:.3f} |",
        f"| baseline_unresolved | {summary['baseline_unresolved']} |",
        f"| contract_unresolved | {summary['contract_unresolved']} |",
        f"| total_tokens | {summary['total_tokens']} |",
        "",
        "## By Coverage Slice",
        "",
        "| Slice | Pair | Expected | Baseline FTGA | Contract FTGA | Baseline RTT | Contract RTT |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in by_slice:
        lines.append(
            "| "
            f"{row['coverage_slice']} | {row['language_pair']} | {row['expected_response_language']} | "
            f"{row['baseline_ftga']} | {row['contract_ftga']} | {row['baseline_rtt']} | {row['contract_rtt']} |"
        )

    lines.extend(
        [
            "",
            "## First-Turn Failures",
            "",
        ]
    )
    if failures:
        lines.extend(["| Item | Slice | Condition | Failure types | Snippet |", "|---|---|---|---|---|"])
        for row in failures:
            lines.append(
                "| "
                f"{row['item_id']} | {row['coverage_slice']} | {row['condition']} | "
                f"{row['failure_types']} | {row['response_snippet']} |"
            )
    else:
        lines.append("No first-turn failures in the smoke sample.")

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- Treat this as a six-item smoke, not as a benchmark result.",
            "- Do not merge it into the v0.2 headline tables.",
            "- Do not report v0.3 performance claims until native validation and a larger pre-specified run are complete.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, default=Path("data/benchmark_stress_v0.3_expansion.jsonl"))
    parser.add_argument("--scores", type=Path, default=Path("results/scores/openai_gpt54mini_stress_v03_smoke6_auto_scores.jsonl"))
    parser.add_argument("--outputs", type=Path, default=Path("results/model_outputs/openai_gpt54mini_stress_v03_smoke6.jsonl"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/openai_gpt54mini_stress_v03_smoke6"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/coverage_smoke_gpt54mini_v03.md"))
    args = parser.parse_args()

    summary, by_slice, failures = analyze(
        benchmark_rows=load_jsonl(args.benchmark),
        scores=load_jsonl(args.scores),
        model_output_rows=load_jsonl(args.outputs),
    )
    write_csv(args.out_dir / "coverage_smoke_summary.csv", [summary])
    write_csv(args.out_dir / "coverage_smoke_by_slice.csv", by_slice)
    write_csv(args.out_dir / "coverage_smoke_first_turn_failures.csv", failures or [{"item_id": "", "coverage_slice": "", "condition": "", "failure_types": "", "response_snippet": ""}])
    write_markdown(args.out_md, summary, by_slice, failures)
    print(f"wrote v0.3 coverage smoke analysis to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
