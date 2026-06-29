#!/usr/bin/env python
"""Validate the tiny v0.3 coverage-expansion model smoke."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


EXPECTED_SMOKE_IDS = {
    "v03_en_es_EP_001",
    "v03_en_hi_EP_001",
    "v03_en_ar_EP_001",
    "v03_es_ar_EP_001",
    "v03_hi_hi_EP_001",
    "v03_ar_ar_EP_001",
}
EXPECTED_REPORT_PHRASES = (
    "six-item smoke",
    "not paper-facing model result evidence",
    "requires native validation before claims",
    "Do not merge it into the v0.2 headline tables",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


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


def load_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def validate_outputs(rows: list[dict[str, Any]]) -> None:
    args = validate_outputs.args
    require(len(rows) == args.expected_api_rows, f"expected {args.expected_api_rows} API response rows, found {len(rows)}")
    ids = {row["item_id"] for row in rows}
    require(ids == EXPECTED_SMOKE_IDS, f"unexpected smoke ids: {sorted(ids)}")
    require({row["model"] for row in rows} == {args.expected_model}, "unexpected smoke model")
    require({row["condition"] for row in rows} == {"baseline", "contract"}, "unexpected smoke conditions")
    require(sum(int(row["input_tokens"]) for row in rows) == args.expected_input_tokens, "unexpected smoke input-token total")
    require(sum(int(row["output_tokens"]) for row in rows) == args.expected_output_tokens, "unexpected smoke output-token total")


def validate_scores(rows: list[dict[str, Any]]) -> None:
    args = validate_scores.args
    expected_failure_types = [item for item in args.expected_failure_types.split(",") if item]
    require(len(rows) == args.expected_api_rows, f"expected {args.expected_api_rows} scored response rows, found {len(rows)}")
    first_turns = [row for row in rows if int(row["turn"]) == 0]
    require(len(first_turns) == 12, f"expected 12 first-turn rows, found {len(first_turns)}")
    baseline_first = [row for row in first_turns if row["condition"] == "baseline"]
    contract_first = [row for row in first_turns if row["condition"] == "contract"]
    require(sum(bool(row["pass"]) for row in baseline_first) == args.expected_baseline_first_turn_passes, "unexpected baseline FTGA count")
    require(sum(bool(row["pass"]) for row in contract_first) == args.expected_contract_first_turn_passes, "unexpected contract FTGA count")
    failures = [row for row in baseline_first if not row["pass"]]
    require(len(failures) == args.expected_first_turn_failure_count, "unexpected baseline first-turn failure count")
    if args.expected_first_turn_failure_count:
        require(failures[0]["item_id"] == args.expected_failure_item, "unexpected baseline failure item")
        require(failures[0]["failure_types"] == expected_failure_types, "unexpected baseline failure type")
        repair_rows = [row for row in rows if row["item_id"] == args.expected_failure_item and row["condition"] == "baseline" and int(row["turn"]) == 1]
        require(len(repair_rows) == args.expected_successful_repair_rows, "unexpected repair-row count")
        require(all(row["pass"] for row in repair_rows), "expected repair rows to pass")


def validate_tables(tables_dir: Path) -> None:
    args = validate_tables.args
    summary_rows = load_csv(tables_dir / "coverage_smoke_summary.csv")
    require(len(summary_rows) == 1, "expected one smoke summary row")
    summary = summary_rows[0]
    expected_summary = {
        "items": "6",
        "trajectories": "12",
        "api_response_rows": str(args.expected_api_rows),
        "scored_response_rows": str(args.expected_api_rows),
        "baseline_unresolved": "0",
        "contract_unresolved": "0",
        "input_tokens": str(args.expected_input_tokens),
        "output_tokens": str(args.expected_output_tokens),
        "total_tokens": str(args.expected_input_tokens + args.expected_output_tokens),
    }
    for field, expected in expected_summary.items():
        require(summary[field] == expected, f"smoke summary mismatch for {field}")
    expected_baseline_ftga = args.expected_baseline_first_turn_passes / 6
    expected_contract_ftga = args.expected_contract_first_turn_passes / 6
    require(abs(float(summary["baseline_ftga"]) - expected_baseline_ftga) < 1e-12, "unexpected baseline FTGA")
    require(abs(float(summary["contract_ftga"]) - expected_contract_ftga) < 1e-12, "unexpected contract FTGA")
    require(abs(float(summary["ftga_delta_pp"]) - 100 * (expected_contract_ftga - expected_baseline_ftga)) < 1e-9, "unexpected FTGA delta")
    require(abs(float(summary["baseline_mean_rtt"]) - args.expected_baseline_mean_rtt) < 1e-12, "unexpected baseline RTT")
    require(abs(float(summary["contract_mean_rtt"]) - args.expected_contract_mean_rtt) < 1e-12, "unexpected contract RTT")

    by_slice = load_csv(tables_dir / "coverage_smoke_by_slice.csv")
    require(len(by_slice) == 6, "expected six by-slice smoke rows")
    failure_rows = [row for row in by_slice if row["item_id"] == "v03_es_ar_EP_001"]
    require(len(failure_rows) == 1, "missing v03_es_ar_EP_001 slice row")
    require(failure_rows[0]["baseline_ftga"] == args.expected_es_ar_baseline_ftga, "unexpected es-ar baseline FTGA")
    require(failure_rows[0]["contract_ftga"] == "1", "expected contract pass in es-ar row")

    failures = load_csv(tables_dir / "coverage_smoke_first_turn_failures.csv")
    if args.expected_first_turn_failure_count:
        require(len(failures) == args.expected_first_turn_failure_count, "unexpected first-turn failure table row count")
        require(failures[0]["item_id"] == args.expected_failure_item, "unexpected failure-table item")
    else:
        require(len(failures) == 1 and failures[0]["item_id"] == "", "expected blank no-failure placeholder row")


def validate_report(path: Path) -> None:
    args = validate_report.args
    require(path.exists(), f"missing smoke report {path}")
    text = " ".join(path.read_text(encoding="utf-8").split())
    for phrase in EXPECTED_REPORT_PHRASES:
        require(phrase in text, f"smoke report missing phrase: {phrase}")
    expected_phrases = [
        f"model | {args.expected_model}",
        f"baseline_ftga | {100 * args.expected_baseline_first_turn_passes / 6:.1f}%",
        f"contract_ftga | {100 * args.expected_contract_first_turn_passes / 6:.1f}%",
        f"ftga_delta | {100 * (args.expected_contract_first_turn_passes - args.expected_baseline_first_turn_passes) / 6:.1f} pp",
    ]
    if args.expected_first_turn_failure_count:
        expected_phrases.append(args.expected_failure_item)
    else:
        expected_phrases.append("No first-turn failures in the smoke sample.")
    for phrase in expected_phrases:
        require(phrase in text, f"smoke report missing value: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs", type=Path, default=Path("results/model_outputs/openai_gpt54mini_stress_v03_smoke6.jsonl"))
    parser.add_argument("--scores", type=Path, default=Path("results/scores/openai_gpt54mini_stress_v03_smoke6_auto_scores.jsonl"))
    parser.add_argument("--tables-dir", type=Path, default=Path("results/tables/openai_gpt54mini_stress_v03_smoke6"))
    parser.add_argument("--report", type=Path, default=Path("paper/coverage_smoke_gpt54mini_v03.md"))
    parser.add_argument("--expected-model", default="gpt-5.4-mini")
    parser.add_argument("--expected-api-rows", type=int, default=13)
    parser.add_argument("--expected-input-tokens", type=int, default=1781)
    parser.add_argument("--expected-output-tokens", type=int, default=479)
    parser.add_argument("--expected-baseline-first-turn-passes", type=int, default=5)
    parser.add_argument("--expected-contract-first-turn-passes", type=int, default=6)
    parser.add_argument("--expected-first-turn-failure-count", type=int, default=1)
    parser.add_argument("--expected-successful-repair-rows", type=int, default=1)
    parser.add_argument("--expected-baseline-mean-rtt", type=float, default=1 / 6)
    parser.add_argument("--expected-contract-mean-rtt", type=float, default=0.0)
    parser.add_argument("--expected-es-ar-baseline-ftga", default="0")
    parser.add_argument("--expected-failure-item", default="v03_es_ar_EP_001")
    parser.add_argument("--expected-failure-types", default="task_noncompletion")
    args = parser.parse_args()
    validate_outputs.args = args
    validate_scores.args = args
    validate_tables.args = args
    validate_report.args = args
    validate_outputs(load_jsonl(args.outputs))
    validate_scores(load_jsonl(args.scores))
    validate_tables(args.tables_dir)
    validate_report(args.report)
    print("validated v0.3 coverage smoke")


if __name__ == "__main__":
    main()
