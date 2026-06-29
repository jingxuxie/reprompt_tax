#!/usr/bin/env python
"""Summarize LLM judge audit results."""

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
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def boolish(value: Any) -> bool:
    return bool(value)


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    agree = sum(boolish(row["auto_pass"]) == boolish(row["judge_pass"]) for row in rows)
    auto_pass = sum(boolish(row["auto_pass"]) for row in rows)
    judge_pass = sum(boolish(row["judge_pass"]) for row in rows)
    auto_fail_judge_pass = sum((not boolish(row["auto_pass"])) and boolish(row["judge_pass"]) for row in rows)
    auto_pass_judge_fail = sum(boolish(row["auto_pass"]) and (not boolish(row["judge_pass"])) for row in rows)
    return {
        "n": n,
        "agreement": agree / n if n else 0,
        "auto_pass_rate": auto_pass / n if n else 0,
        "judge_pass_rate": judge_pass / n if n else 0,
        "auto_fail_judge_pass": auto_fail_judge_pass,
        "auto_pass_judge_fail": auto_pass_judge_fail,
    }


def group_rows(rows: list[dict[str, Any]], keys: list[str]) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row.get(key, "") for key in keys)].append(row)
    out: list[dict[str, Any]] = []
    for group_key, group in sorted(grouped.items()):
        entry = {key: value for key, value in zip(keys, group_key)}
        entry.update(summarize_group(group))
        out.append(entry)
    return out


def disagreement_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        if boolish(row["auto_pass"]) == boolish(row["judge_pass"]):
            continue
        out.append(
            {
                "item_id": row["item_id"],
                "model": row["model"],
                "condition": row["condition"],
                "turn": row["turn"],
                "task_family": row.get("task_family", ""),
                "language_pair": row.get("language_pair", ""),
                "auto_pass": row["auto_pass"],
                "judge_pass": row["judge_pass"],
                "auto_failure_types": json.dumps(row.get("auto_failure_types", []), ensure_ascii=False),
                "judge_failure_types": json.dumps(row.get("judge_failure_types", []), ensure_ascii=False),
                "judge_short_reason": row.get("judge_short_reason", ""),
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    rows = load_jsonl(args.audit)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "judge_audit_summary.csv", [summarize_group(rows)])
    write_csv(args.out_dir / "judge_audit_by_model_condition.csv", group_rows(rows, ["model", "condition"]))
    write_csv(args.out_dir / "judge_audit_by_family.csv", group_rows(rows, ["task_family"]))
    write_csv(args.out_dir / "judge_audit_disagreements.csv", disagreement_rows(rows))

    print(f"summarized {len(rows)} judge rows to {args.out_dir}")


if __name__ == "__main__":
    main()
