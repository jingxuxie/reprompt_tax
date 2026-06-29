#!/usr/bin/env python
"""Summarize paper-facing API usage and artifact provenance."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_MODEL_ARTIFACTS = [
    (
        "main_evaluation",
        Path("results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl"),
    ),
    (
        "prompt_control",
        Path("results/scores/openai_nano_stress_v02_full120_generic_helpfulness_auto_scores.jsonl"),
    ),
    (
        "prompt_ablation_content_preservation",
        Path("results/scores/openai_nano_stress_v02_full120_content_preservation_auto_scores.jsonl"),
    ),
    (
        "coverage_pilot_v03_gpt54mini",
        Path("results/scores/openai_gpt54mini_stress_v03_pilot24_auto_scores.jsonl"),
    ),
    (
        "coverage_smoke_v03_gpt55",
        Path("results/scores/openai_gpt55_stress_v03_smoke6_auto_scores.jsonl"),
    ),
]
DEFAULT_JUDGE_ARTIFACTS = [
    (
        "judge_audit",
        Path("results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl"),
    ),
    (
        "judge_refresh_gpt55",
        Path("results/scores/openai_three_model_stress_v02_full120_judge_gpt55_audit72.jsonl"),
    ),
]
DEFAULT_REPAIR_ARTIFACTS = [
    (
        "repair_realism_editing_baseline24",
        Path("results/scores/openai_three_model_stress_v02_repair_realism_editing_baseline24.jsonl"),
    ),
]


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


def iso_range(values: list[str]) -> tuple[str, str]:
    require(bool(values), "cannot summarize empty timestamp list")
    parsed = [datetime.fromisoformat(value) for value in values]
    return min(parsed).isoformat(), max(parsed).isoformat()


def add_model_rows(
    *,
    rows: list[dict[str, Any]],
    artifact_label: str,
    rel_path: Path,
    artifact_rows: list[dict[str, Any]],
    group_rows: dict[tuple[str, str, str], list[dict[str, Any]]],
) -> None:
    require(bool(rows), f"{rel_path} has no rows")
    for row in rows:
        for field in ("item_id", "model", "condition", "turn", "input_tokens", "output_tokens", "created_at"):
            require(field in row, f"{rel_path} row missing {field}")
        group_rows[(artifact_label, row["model"], row["condition"])].append(row)

    timestamps = [str(row["created_at"]) for row in rows]
    start, end = iso_range(timestamps)
    trajectories = {(row["item_id"], row["model"], row["condition"]) for row in rows}
    first_turns = [row for row in rows if int(row["turn"]) == 0]
    artifact_rows.append(
        {
            "artifact_label": artifact_label,
            "artifact_kind": "model_responses",
            "path": str(rel_path),
            "api_response_rows": len(rows),
            "first_turn_rows": len(first_turns),
            "trajectories": len(trajectories),
            "input_tokens": sum(int(row["input_tokens"]) for row in rows),
            "output_tokens": sum(int(row["output_tokens"]) for row in rows),
            "total_tokens": sum(int(row["input_tokens"]) + int(row["output_tokens"]) for row in rows),
            "created_at_start": start,
            "created_at_end": end,
        }
    )


def add_judge_rows(
    *,
    rows: list[dict[str, Any]],
    artifact_label: str,
    rel_path: Path,
    artifact_rows: list[dict[str, Any]],
    judge_group_rows: dict[tuple[str, str], list[dict[str, Any]]],
) -> None:
    require(bool(rows), f"{rel_path} has no rows")
    for row in rows:
        for field in ("judge_model", "judge_input_tokens", "judge_output_tokens", "created_at"):
            require(field in row, f"{rel_path} row missing {field}")
        judge_group_rows[(artifact_label, row["judge_model"])].append(row)

    timestamps = [str(row["created_at"]) for row in rows]
    start, end = iso_range(timestamps)
    artifact_rows.append(
        {
            "artifact_label": artifact_label,
            "artifact_kind": "judge_audit",
            "path": str(rel_path),
            "api_response_rows": len(rows),
            "first_turn_rows": len(rows),
            "trajectories": len({(row["item_id"], row["model"], row["condition"], row["turn"]) for row in rows}),
            "input_tokens": sum(int(row["judge_input_tokens"]) for row in rows),
            "output_tokens": sum(int(row["judge_output_tokens"]) for row in rows),
            "total_tokens": sum(int(row["judge_input_tokens"]) + int(row["judge_output_tokens"]) for row in rows),
            "created_at_start": start,
            "created_at_end": end,
        }
    )


def add_repair_rows(
    *,
    rows: list[dict[str, Any]],
    artifact_label: str,
    rel_path: Path,
    artifact_rows: list[dict[str, Any]],
    repair_group_rows: dict[tuple[str, str, str], list[dict[str, Any]]],
) -> None:
    api_rows = [row for row in rows if row.get("source") == "repair_variant_api"]
    require(bool(api_rows), f"{rel_path} has no repair-variant API rows")
    for row in api_rows:
        for field in ("item_id", "model", "condition", "repair_variant", "input_tokens", "output_tokens", "created_at"):
            require(field in row, f"{rel_path} row missing {field}")
        repair_group_rows[(artifact_label, row["model"], row["repair_variant"])].append(row)

    timestamps = [str(row["created_at"]) for row in api_rows]
    start, end = iso_range(timestamps)
    artifact_rows.append(
        {
            "artifact_label": artifact_label,
            "artifact_kind": "repair_variant_responses",
            "path": str(rel_path),
            "api_response_rows": len(api_rows),
            "first_turn_rows": 0,
            "trajectories": len({(row["item_id"], row["model"], row["condition"], row["repair_variant"]) for row in api_rows}),
            "input_tokens": sum(int(row["input_tokens"]) for row in api_rows),
            "output_tokens": sum(int(row["output_tokens"]) for row in api_rows),
            "total_tokens": sum(int(row["input_tokens"]) + int(row["output_tokens"]) for row in api_rows),
            "created_at_start": start,
            "created_at_end": end,
        }
    )


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"cannot write empty CSV {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def summarize_model_groups(group_rows: dict[tuple[str, str, str], list[dict[str, Any]]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for (artifact_label, model, condition), rows in sorted(group_rows.items()):
        start, end = iso_range([str(row["created_at"]) for row in rows])
        trajectories = {(row["item_id"], row["model"], row["condition"]) for row in rows}
        out.append(
            {
                "artifact_label": artifact_label,
                "model": model,
                "condition": condition,
                "api_response_rows": len(rows),
                "first_turn_rows": sum(1 for row in rows if int(row["turn"]) == 0),
                "trajectories": len(trajectories),
                "input_tokens": sum(int(row["input_tokens"]) for row in rows),
                "output_tokens": sum(int(row["output_tokens"]) for row in rows),
                "total_tokens": sum(int(row["input_tokens"]) + int(row["output_tokens"]) for row in rows),
                "created_at_start": start,
                "created_at_end": end,
            }
        )
    return out


def summarize_judge_groups(judge_group_rows: dict[tuple[str, str], list[dict[str, Any]]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for (artifact_label, judge_model), rows in sorted(judge_group_rows.items()):
        start, end = iso_range([str(row["created_at"]) for row in rows])
        out.append(
            {
                "artifact_label": artifact_label,
                "judge_model": judge_model,
                "api_response_rows": len(rows),
                "input_tokens": sum(int(row["judge_input_tokens"]) for row in rows),
                "output_tokens": sum(int(row["judge_output_tokens"]) for row in rows),
                "total_tokens": sum(int(row["judge_input_tokens"]) + int(row["judge_output_tokens"]) for row in rows),
                "created_at_start": start,
                "created_at_end": end,
            }
        )
    return out


def summarize_repair_groups(repair_group_rows: dict[tuple[str, str, str], list[dict[str, Any]]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for (artifact_label, model, repair_variant), rows in sorted(repair_group_rows.items()):
        start, end = iso_range([str(row["created_at"]) for row in rows])
        out.append(
            {
                "artifact_label": artifact_label,
                "model": model,
                "repair_variant": repair_variant,
                "api_response_rows": len(rows),
                "input_tokens": sum(int(row["input_tokens"]) for row in rows),
                "output_tokens": sum(int(row["output_tokens"]) for row in rows),
                "total_tokens": sum(int(row["input_tokens"]) + int(row["output_tokens"]) for row in rows),
                "created_at_start": start,
                "created_at_end": end,
            }
        )
    return out


def summary_row(artifact_rows: list[dict[str, Any]]) -> dict[str, Any]:
    starts = [str(row["created_at_start"]) for row in artifact_rows]
    ends = [str(row["created_at_end"]) for row in artifact_rows]
    return {
        "tracked_api_artifacts": len(artifact_rows),
        "api_response_rows": sum(int(row["api_response_rows"]) for row in artifact_rows),
        "model_response_rows": sum(int(row["api_response_rows"]) for row in artifact_rows if row["artifact_kind"] == "model_responses"),
        "repair_variant_response_rows": sum(int(row["api_response_rows"]) for row in artifact_rows if row["artifact_kind"] == "repair_variant_responses"),
        "judge_response_rows": sum(int(row["api_response_rows"]) for row in artifact_rows if row["artifact_kind"] == "judge_audit"),
        "trajectories_or_judged_rows": sum(int(row["trajectories"]) for row in artifact_rows),
        "input_tokens": sum(int(row["input_tokens"]) for row in artifact_rows),
        "output_tokens": sum(int(row["output_tokens"]) for row in artifact_rows),
        "total_tokens": sum(int(row["total_tokens"]) for row in artifact_rows),
        "created_at_start": min(starts),
        "created_at_end": max(ends),
    }


def write_markdown(
    path: Path,
    summary: dict[str, Any],
    artifact_rows: list[dict[str, Any]],
    model_rows: list[dict[str, Any]],
    judge_rows: list[dict[str, Any]],
    repair_rows: list[dict[str, Any]],
) -> None:
    lines = [
        "# Experiment Ledger",
        "",
        "Generated from saved score, smoke, and judge-audit artifacts.",
        "",
        "This ledger reports API response rows and saved token usage only. It does",
        "not estimate dollar cost because provider prices change over time. Historical",
        "diagnostic shards are excluded to avoid double-counting rows that were merged",
        "into aggregate score files. The v0.3 pilot and GPT-5.5 smoke are included for API accounting",
        "but is not a paper-facing benchmark result.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in summary.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(
        [
            "",
            "## By Artifact",
            "",
            "| Label | Kind | API rows | First-turn rows | Trajectories/judged rows | Input tokens | Output tokens | Total tokens |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in artifact_rows:
        lines.append(
            "| "
            f"{row['artifact_label']} | {row['artifact_kind']} | {row['api_response_rows']} | "
            f"{row['first_turn_rows']} | {row['trajectories']} | {row['input_tokens']} | "
            f"{row['output_tokens']} | {row['total_tokens']} |"
        )

    lines.extend(
        [
            "",
            "## Model Response Usage",
            "",
            "| Artifact | Model | Condition | API rows | First-turn rows | Trajectories | Input tokens | Output tokens | Total tokens |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in model_rows:
        lines.append(
            "| "
            f"{row['artifact_label']} | {row['model']} | {row['condition']} | "
            f"{row['api_response_rows']} | {row['first_turn_rows']} | {row['trajectories']} | "
            f"{row['input_tokens']} | {row['output_tokens']} | {row['total_tokens']} |"
        )

    lines.extend(
        [
            "",
            "## Judge Audit Usage",
            "",
            "| Artifact | Judge model | API rows | Input tokens | Output tokens | Total tokens |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in judge_rows:
        lines.append(
            "| "
            f"{row['artifact_label']} | {row['judge_model']} | {row['api_response_rows']} | "
            f"{row['input_tokens']} | {row['output_tokens']} | {row['total_tokens']} |"
        )

    lines.extend(
        [
            "",
            "## Repair Variant Usage",
            "",
            "| Artifact | Model | Repair variant | API rows | Input tokens | Output tokens | Total tokens |",
            "|---|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in repair_rows:
        lines.append(
            "| "
            f"{row['artifact_label']} | {row['model']} | {row['repair_variant']} | "
            f"{row['api_response_rows']} | {row['input_tokens']} | {row['output_tokens']} | {row['total_tokens']} |"
        )

    model_response_rows = sum(int(row["api_response_rows"]) for row in artifact_rows if row["artifact_kind"] == "model_responses")
    repair_response_rows = sum(int(row["api_response_rows"]) for row in artifact_rows if row["artifact_kind"] == "repair_variant_responses")
    judge_response_rows = sum(int(row["api_response_rows"]) for row in artifact_rows if row["artifact_kind"] == "judge_audit")
    main = next(row for row in artifact_rows if row["artifact_label"] == "main_evaluation")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"The tracked artifact package contains {model_response_rows:,} saved model-response API rows",
            "for the main evaluation plus nano prompt-control, prompt-ablation, v0.3 pilot, and GPT-5.5 smoke diagnostics,",
            f"{repair_response_rows:,} repair-variant API rows, and {judge_response_rows:,} saved",
            "judge-audit API rows. The main evaluation covers",
            f"{main['first_turn_rows']} first-turn trajectories; additional rows are standardized",
            "repair turns emitted only when the first turn failed. Token counts are",
            "provider-reported usage stored with each saved response.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/experiment_ledger_v02"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/experiment_ledger_v02.md"))
    args = parser.parse_args()

    artifact_rows: list[dict[str, Any]] = []
    model_group_rows: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    judge_group_rows: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    repair_group_rows: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)

    for label, path in DEFAULT_MODEL_ARTIFACTS:
        add_model_rows(
            rows=load_jsonl(path),
            artifact_label=label,
            rel_path=path,
            artifact_rows=artifact_rows,
            group_rows=model_group_rows,
        )
    for label, path in DEFAULT_JUDGE_ARTIFACTS:
        add_judge_rows(
            rows=load_jsonl(path),
            artifact_label=label,
            rel_path=path,
            artifact_rows=artifact_rows,
            judge_group_rows=judge_group_rows,
        )
    for label, path in DEFAULT_REPAIR_ARTIFACTS:
        add_repair_rows(
            rows=load_jsonl(path),
            artifact_label=label,
            rel_path=path,
            artifact_rows=artifact_rows,
            repair_group_rows=repair_group_rows,
        )

    model_rows = summarize_model_groups(model_group_rows)
    judge_rows = summarize_judge_groups(judge_group_rows)
    repair_rows = summarize_repair_groups(repair_group_rows)
    summary = summary_row(artifact_rows)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "experiment_ledger_summary.csv", [summary])
    write_csv(args.out_dir / "api_usage_by_artifact.csv", artifact_rows)
    write_csv(args.out_dir / "api_usage_by_model_condition.csv", model_rows)
    write_csv(args.out_dir / "api_usage_by_judge.csv", judge_rows)
    write_csv(args.out_dir / "api_usage_by_repair_variant.csv", repair_rows)
    write_markdown(args.out_md, summary, artifact_rows, model_rows, judge_rows, repair_rows)
    print(f"wrote experiment ledger to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
