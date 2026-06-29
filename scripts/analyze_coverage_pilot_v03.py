#!/usr/bin/env python
"""Analyze the 24-item v0.3 coverage-expansion pilot."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


CONDITIONS = ("baseline", "contract")


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


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"cannot write empty CSV {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def trajectory(rows: list[dict[str, Any]], benchmark: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: int(row["turn"]))
    first = ordered[0]
    rtt = 3
    for row in ordered:
        if row["pass"]:
            rtt = int(row["turn"])
            break
    first_tokens = int(first["input_tokens"]) + int(first["output_tokens"])
    used = [row for row in ordered if int(row["turn"]) <= rtt] if rtt < 3 else ordered
    total_tokens = sum(int(row["input_tokens"]) + int(row["output_tokens"]) for row in used)
    item = benchmark[first["item_id"]]
    return {
        "item_id": first["item_id"],
        "coverage_slice": item["coverage_slice"],
        "language_pair": item["language_pair"],
        "expected_response_language": item["expected_response_language"],
        "model": first["model"],
        "condition": first["condition"],
        "ftga": 1 if bool(first["pass"]) else 0,
        "rtt": rtt,
        "unresolved": 1 if rtt == 3 else 0,
        "token_tax": total_tokens / max(first_tokens, 1),
        "first_failure_types": ";".join(first.get("failure_types") or []),
        "turns": len(ordered),
    }


def grouped_summary(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(str(row[field]) for field in fields)].append(row)

    out: list[dict[str, Any]] = []
    for key, group in sorted(grouped.items()):
        initially_failed = sum(1 - row["ftga"] for row in group)
        repaired = sum(1 for row in group if row["ftga"] == 0 and row["rtt"] in (1, 2))
        result = {field: value for field, value in zip(fields, key)}
        result.update(
            {
                "n": len(group),
                "ftga": sum(row["ftga"] for row in group) / len(group),
                "mean_rtt": sum(row["rtt"] for row in group) / len(group),
                "unresolved_rate": sum(row["unresolved"] for row in group) / len(group),
                "repair_success_at_2": repaired / initially_failed if initially_failed else "",
                "mean_token_tax": sum(float(row["token_tax"]) for row in group) / len(group),
                "initially_failed_n": initially_failed,
            }
        )
        out.append(result)
    return out


def paired_items(trajectories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_item: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in trajectories:
        by_item[row["item_id"]][row["condition"]] = row
    out: list[dict[str, Any]] = []
    for item_id, pair in sorted(by_item.items()):
        if set(pair) != set(CONDITIONS):
            continue
        baseline = pair["baseline"]
        contract = pair["contract"]
        out.append(
            {
                "item_id": item_id,
                "coverage_slice": baseline["coverage_slice"],
                "language_pair": baseline["language_pair"],
                "baseline_ftga": baseline["ftga"],
                "contract_ftga": contract["ftga"],
                "ftga_delta": contract["ftga"] - baseline["ftga"],
                "baseline_rtt": baseline["rtt"],
                "contract_rtt": contract["rtt"],
                "rtt_delta": baseline["rtt"] - contract["rtt"],
                "baseline_first_failure_types": baseline["first_failure_types"],
                "contract_first_failure_types": contract["first_failure_types"],
            }
        )
    return out


def first_turn_failures(scores: list[dict[str, Any]], benchmark: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in scores:
        if int(row["turn"]) != 0 or row["pass"]:
            continue
        item = benchmark[row["item_id"]]
        out.append(
            {
                "item_id": row["item_id"],
                "coverage_slice": item["coverage_slice"],
                "condition": row["condition"],
                "failure_types": ";".join(row.get("failure_types") or []),
                "response_snippet": str(row["response"]).replace("\n", " ")[:220],
            }
        )
    return out


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def write_markdown(
    *,
    path: Path,
    summary: list[dict[str, Any]],
    by_slice: list[dict[str, Any]],
    paired: list[dict[str, Any]],
    failures: list[dict[str, Any]],
    raw_rows: list[dict[str, Any]],
) -> None:
    summary_by_condition = {row["condition"]: row for row in summary}
    baseline = summary_by_condition["baseline"]
    contract = summary_by_condition["contract"]
    improved = sum(1 for row in paired if row["ftga_delta"] > 0)
    worsened = sum(1 for row in paired if row["ftga_delta"] < 0)
    tied = sum(1 for row in paired if row["ftga_delta"] == 0)
    input_tokens = sum(int(row["input_tokens"]) for row in raw_rows)
    output_tokens = sum(int(row["output_tokens"]) for row in raw_rows)

    lines = [
        "# GPT-5.4-mini v0.3 Coverage Pilot",
        "",
        "This 24-item pilot uses four rows from each synthetic v0.3 coverage-expansion slice.",
        "It reuses the six saved smoke rows and adds 18 new rows; it is not paper-facing model result evidence.",
        "The v0.3 scaffold still requires native validation before claims.",
        "",
        "## Summary",
        "",
        "| Condition | n | FTGA | Mean RTT | Unresolved | Repair@2 | Mean token tax | Initially failed |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        repair = "" if row["repair_success_at_2"] == "" else pct(float(row["repair_success_at_2"]))
        lines.append(
            "| "
            f"{row['condition']} | {row['n']} | {pct(float(row['ftga']))} | "
            f"{float(row['mean_rtt']):.3f} | {pct(float(row['unresolved_rate']))} | {repair} | "
            f"{float(row['mean_token_tax']):.3f} | {row['initially_failed_n']} |"
        )
    lines.extend(
        [
            "",
            f"Paired FTGA movement: {improved} improved, {worsened} worsened, {tied} tied out of {len(paired)} items.",
            f"Saved API rows: {len(raw_rows)} ({input_tokens} input tokens, {output_tokens} output tokens).",
            "",
            "## By Coverage Slice",
            "",
            "| Slice | Condition | n | FTGA | Mean RTT | Initially failed |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in by_slice:
        lines.append(
            "| "
            f"{row['coverage_slice']} | {row['condition']} | {row['n']} | {pct(float(row['ftga']))} | "
            f"{float(row['mean_rtt']):.3f} | {row['initially_failed_n']} |"
        )

    lines.extend(
        [
            "",
            "## First-Turn Failures",
            "",
            "| Item | Slice | Condition | Failure types | Snippet |",
            "|---|---|---|---|---|",
        ]
    )
    for row in failures:
        lines.append(
            "| "
            f"{row['item_id']} | {row['coverage_slice']} | {row['condition']} | "
            f"{row['failure_types']} | {row['response_snippet']} |"
        )

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- Treat this as a 24-item synthetic v0.3 pilot, not as a headline benchmark result.",
            "- Do not merge it into the v0.2 paper-facing tables.",
            "- Do not report v0.3 performance claims until native validation is complete.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, default=Path("data/benchmark_stress_v0.3_expansion.jsonl"))
    parser.add_argument("--scores", type=Path, default=Path("results/scores/openai_gpt54mini_stress_v03_pilot24_auto_scores.jsonl"))
    parser.add_argument("--outputs", type=Path, default=Path("results/model_outputs/openai_gpt54mini_stress_v03_pilot24.jsonl"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/openai_gpt54mini_stress_v03_pilot24"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/coverage_pilot_gpt54mini_v03.md"))
    args = parser.parse_args()

    benchmark = {row["id"]: row for row in load_jsonl(args.benchmark)}
    scores = load_jsonl(args.scores)
    raw_rows = load_jsonl(args.outputs)
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in scores:
        grouped[(row["item_id"], row["model"], row["condition"])].append(row)
    trajectories = [trajectory(rows, benchmark) for rows in grouped.values()]
    require(len(trajectories) == 48, f"expected 48 pilot trajectories, found {len(trajectories)}")
    require({row["item_id"] for row in trajectories} == {row["item_id"] for row in raw_rows}, "score/output item IDs differ")

    summary = grouped_summary(trajectories, ("condition",))
    by_slice = grouped_summary(trajectories, ("coverage_slice", "condition"))
    paired = paired_items(trajectories)
    failures = first_turn_failures(scores, benchmark)
    write_csv(args.out_dir / "coverage_pilot_summary.csv", summary)
    write_csv(args.out_dir / "coverage_pilot_by_slice.csv", by_slice)
    write_csv(args.out_dir / "coverage_pilot_paired_items.csv", paired)
    write_csv(args.out_dir / "coverage_pilot_first_turn_failures.csv", failures)
    write_markdown(path=args.out_md, summary=summary, by_slice=by_slice, paired=paired, failures=failures, raw_rows=raw_rows)
    print(f"wrote v0.3 coverage pilot analysis to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
