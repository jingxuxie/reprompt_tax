#!/usr/bin/env python
"""Summarize completed v0.3 coverage native-review annotations."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from validate_completed_coverage_native_review_v03 import (
    BOOLEAN_FIELDS,
    parse_issue_types,
    validate_completed_reviews,
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "t", "yes", "y", "pass", "passed"}


def split_issue_types(value: str) -> list[str]:
    return parse_issue_types(value, row_id="coverage_native_review_summary")


def summarize_by(rows: list[dict[str, str]], fields: tuple[str, ...]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row[field] for field in fields)].append(row)

    out: list[dict[str, Any]] = []
    for key, group_rows in sorted(grouped.items()):
        base = {field: value for field, value in zip(fields, key)}
        base["n"] = len(group_rows)
        usable = sum(parse_bool(row["reviewer_release_usable"]) for row in group_rows)
        base["release_usable_n"] = usable
        base["issue_rows"] = len(group_rows) - usable
        base["release_usable_rate"] = round(usable / len(group_rows), 4)
        for field in BOOLEAN_FIELDS:
            base[f"{field}_rate"] = round(sum(parse_bool(row[field]) for row in group_rows) / len(group_rows), 4)
        out.append(base)
    return out


def issue_type_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    issue_rows = 0
    for row in rows:
        if parse_bool(row["reviewer_release_usable"]):
            continue
        issue_rows += 1
        counts.update(split_issue_types(row.get("reviewer_issue_types", "")))
    return [
        {"reviewer_issue_type": issue_type, "rows_with_type": count, "issue_rows": issue_rows}
        for issue_type, count in sorted(counts.items())
    ]


def nonusable_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        if parse_bool(row["reviewer_release_usable"]):
            continue
        out.append(
            {
                "review_id": row["review_id"],
                "item_id": row["item_id"],
                "coverage_slice": row["coverage_slice"],
                "language_pair": row["language_pair"],
                "reviewer_issue_types": row.get("reviewer_issue_types", ""),
                "reviewer_notes": row.get("reviewer_notes", ""),
            }
        )
    return out


def write_markdown(path: Path, summary: dict[str, Any], by_slice: list[dict[str, Any]], issues: list[dict[str, Any]]) -> None:
    lines = [
        "# v0.3 Coverage Native-Review Summary",
        "",
        "This report is generated only after completed qualified-reviewer labels",
        "pass validation.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in summary.items():
        lines.append(f"| {key} | {value} |")
    lines.extend(["", "## By Coverage Slice", "", "| Slice | Rows | Release usable | Issue rows | Release usable rate |", "|---|---:|---:|---:|---:|"])
    for row in by_slice:
        lines.append(
            f"| {row['coverage_slice']} | {row['n']} | {row['release_usable_n']} | "
            f"{row['issue_rows']} | {100 * row['release_usable_rate']:.1f}% |"
        )
    lines.extend(["", "## Issue Types", "", "| Issue type | Rows with type | Issue rows |", "|---|---:|---:|"])
    if issues:
        for row in issues:
            lines.append(f"| {row['reviewer_issue_type']} | {row['rows_with_type']} | {row['issue_rows']} |")
    else:
        lines.append("| none | 0 | 0 |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--launch-packet", type=Path, default=Path("data/coverage_native_review_v03/coverage_native_review_packet_v03.csv"))
    parser.add_argument("--reviewer-roster", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/coverage_native_review_v03"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/coverage_native_review_v03.md"))
    args = parser.parse_args()

    rows = read_csv(args.annotations)
    summary = validate_completed_reviews(
        annotation_rows=rows,
        launch_rows=read_csv(args.launch_packet),
        roster_rows=read_csv(args.reviewer_roster),
    )
    by_slice = summarize_by(rows, ("coverage_slice",))
    by_content_language = summarize_by(rows, ("content_language",))
    by_reviewer = summarize_by(rows, ("reviewer_id", "coverage_slice"))
    issues = issue_type_rows(rows)
    nonusable = nonusable_rows(rows)

    write_csv(args.out_dir / "coverage_native_review_summary.csv", [summary])
    write_csv(args.out_dir / "coverage_native_review_by_slice.csv", by_slice)
    write_csv(args.out_dir / "coverage_native_review_by_content_language.csv", by_content_language)
    write_csv(args.out_dir / "coverage_native_review_by_reviewer.csv", by_reviewer)
    write_csv(args.out_dir / "coverage_native_review_issue_types.csv", issues)
    write_csv(args.out_dir / "coverage_native_review_nonusable_rows.csv", nonusable)
    write_markdown(args.out_md, summary, by_slice, issues)
    print(f"summarized {summary['rows']} completed v0.3 coverage native-review rows")


if __name__ == "__main__":
    main()
