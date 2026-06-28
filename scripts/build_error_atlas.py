#!/usr/bin/env python
"""Build a compact first-turn failure atlas for the RePromptTax stress run."""

from __future__ import annotations

import argparse
import ast
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


FAMILY_LABELS = {
    "editing_preservation": "Editing preservation",
    "output_language_inference": "Output-language inference",
    "quote_preservation": "Quote preservation",
    "script_register_locale": "Script/register/locale",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def parse_failure_types(value: str | list[str]) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if not value:
        return []
    parsed = ast.literal_eval(value)
    if not isinstance(parsed, list):
        raise ValueError(f"expected list-like failure types, got {value!r}")
    return [str(item) for item in parsed]


def clean_excerpt(text: str, max_chars: int = 180) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 3].rstrip() + "..."


def md_cell(text: str) -> str:
    return str(text).replace("|", "\\|")


def build_rows(score_rows: list[dict[str, Any]], trajectory_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    trajectories = {
        (row["item_id"], row["model"], row["condition"]): row
        for row in trajectory_rows
    }

    rows: list[dict[str, Any]] = []
    for score in score_rows:
        if int(score["turn"]) != 0 or bool(score["pass"]):
            continue
        key = (score["item_id"], score["model"], score["condition"])
        trajectory = trajectories[key]
        failure_types = parse_failure_types(score.get("failure_types", []))
        rows.append(
            {
                "item_id": score["item_id"],
                "language_pair": score["language_pair"],
                "task_family": score["task_family"],
                "model": score["model"],
                "condition": score["condition"],
                "rtt": int(trajectory["rtt"]),
                "unresolved": int(trajectory["unresolved"]),
                "failure_types": ";".join(failure_types),
                "short_reason": score.get("short_reason", ""),
                "response_excerpt": clean_excerpt(score.get("response", "")),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            row["task_family"],
            row["language_pair"],
            row["item_id"],
            row["model"],
            row["condition"],
        ),
    )


def count_rows(rows: list[dict[str, Any]], *fields: str) -> list[dict[str, Any]]:
    counts = Counter(tuple(row[field] for field in fields) for row in rows)
    out = []
    for key, count in sorted(counts.items()):
        out.append({field: value for field, value in zip(fields, key)} | {"count": count})
    return out


def unresolved_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row["unresolved"]]


def write_markdown(path: Path, rows: list[dict[str, Any]], scores_path: Path) -> None:
    by_family = count_rows(rows, "task_family")
    by_model_condition = count_rows(rows, "model", "condition")
    unresolved = unresolved_rows(rows)

    lines = [
        "# RePromptTax First-Turn Error Atlas",
        "",
        f"Generated from `{scores_path}`.",
        "",
        "This atlas lists first-turn failures only. It is intended for paper writing,",
        "manual inspection, and audit triage; it is not an additional evaluation run.",
        "",
        "## Summary",
        "",
        f"- First-turn failures: {len(rows)}",
        f"- Unresolved after two repair prompts: {len(unresolved)}",
        "",
        "### Failures by Task Family",
        "",
        "| Task family | Failures |",
        "|---|---:|",
    ]
    for row in by_family:
        lines.append(f"| {FAMILY_LABELS[row['task_family']]} | {row['count']} |")

    lines.extend(["", "### Failures by Model and Condition", "", "| Model | Condition | Failures |", "|---|---|---:|"])
    for row in by_model_condition:
        lines.append(f"| {row['model']} | {row['condition']} | {row['count']} |")

    lines.extend(["", "### Unresolved Cases", "", "| Item | Model | Condition | Family | Failure types |", "|---|---|---|---|---|"])
    for row in unresolved:
        lines.append(
            "| "
            f"{row['item_id']} | "
            f"{row['model']} | "
            f"{row['condition']} | "
            f"{FAMILY_LABELS[row['task_family']]} | "
            f"{md_cell(row['failure_types'])} |"
        )

    lines.extend(
        [
            "",
            "## Atlas",
            "",
            "| Item | Lang | Family | Model | Condition | RTT | Failure types | Response excerpt |",
            "|---|---|---|---|---|---:|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            "| "
            f"{row['item_id']} | "
            f"{row['language_pair']} | "
            f"{FAMILY_LABELS[row['task_family']]} | "
            f"{row['model']} | "
            f"{row['condition']} | "
            f"{row['rtt']} | "
            f"{md_cell(row['failure_types'])} | "
            f"{md_cell(row['response_excerpt'])} |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", type=Path, default=Path("results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl"))
    parser.add_argument("--trajectories", type=Path, default=Path("results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv"))
    parser.add_argument("--out-csv", type=Path, default=Path("results/tables/openai_three_model_stress_v02_full120/first_turn_error_atlas.csv"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/error_atlas_v02_full120.md"))
    args = parser.parse_args()

    rows = build_rows(load_jsonl(args.scores), load_csv(args.trajectories))
    write_csv(args.out_csv, rows)
    write_markdown(args.out_md, rows, args.scores)
    print(f"wrote {len(rows)} first-turn failures to {args.out_csv} and {args.out_md}")


if __name__ == "__main__":
    main()
