#!/usr/bin/env python
"""Analyze v0.3 coverage native-review launch readiness."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


REVIEW_FIELDS = (
    "reviewer_id",
    "reviewer_prompt_clear",
    "reviewer_target_language_natural",
    "reviewer_script_expectation_valid",
    "reviewer_preservation_spans_valid",
    "reviewer_known_bad_outputs_valid",
    "reviewer_release_usable",
    "reviewer_issue_types",
    "reviewer_notes",
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


def parse_list(value: str) -> list[Any]:
    parsed = json.loads(value or "[]")
    if not isinstance(parsed, list):
        raise AssertionError(f"expected JSON list, got {value!r}")
    return parsed


def count_by(rows: list[dict[str, str]], fields: tuple[str, ...]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(tuple(row[field] for field in fields), []).append(row)

    out: list[dict[str, Any]] = []
    for key, group_rows in sorted(grouped.items()):
        base = {field: value for field, value in zip(fields, key)}
        base.update(
            {
                "n": len(group_rows),
                "rows_with_preservation_spans": sum(bool(parse_list(row["must_preserve_spans"])) for row in group_rows),
                "total_preservation_spans": sum(len(parse_list(row["must_preserve_spans"])) for row in group_rows),
                "rows_with_required_markers": sum(bool(parse_list(row["required_any_markers"])) for row in group_rows),
                "rows_with_forbidden_markers": sum(bool(parse_list(row["forbidden_markers"])) for row in group_rows),
                "rows_with_known_bad_outputs": sum(bool(parse_list(row["known_bad_outputs"])) for row in group_rows),
            }
        )
        out.append(base)
    return out


def summary_row(rows: list[dict[str, str]]) -> dict[str, Any]:
    review_blank = all(row.get(field, "") == "" for row in rows for field in REVIEW_FIELDS)
    return {
        "review_rows": len(rows),
        "coverage_slices": len({row["coverage_slice"] for row in rows}),
        "language_pairs": len({row["language_pair"] for row in rows}),
        "instruction_languages": len({row["instruction_language"] for row in rows}),
        "content_languages": len({row["content_language"] for row in rows}),
        "task_families": len({row["task_family"] for row in rows}),
        "rows_per_slice_min": min(Counter(row["coverage_slice"] for row in rows).values()),
        "rows_per_slice_max": max(Counter(row["coverage_slice"] for row in rows).values()),
        "review_fields_blank": review_blank,
        "rows_requiring_native_review": len(rows),
        "validation_status": "launch_ready_but_not_completed_native_validation",
    }


def write_markdown(
    path: Path,
    summary: dict[str, Any],
    by_slice: list[dict[str, Any]],
    by_content_language: list[dict[str, Any]],
) -> None:
    lines = [
        "# v0.3 Coverage Native-Review Design",
        "",
        "This report analyzes the launch packet for native/near-native review of",
        "the 60 synthetic v0.3 rows. It is launch-ready but not completed native validation.",
        "Do not claim native validation has been completed from this artifact.",
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
            "## Coverage Slices",
            "",
            "| Slice | Language pair | Instruction | Content | Rows | Preserve rows | Preserve spans |",
            "|---|---|---|---|---:|---:|---:|",
        ]
    )
    for row in by_slice:
        lines.append(
            f"| {row['coverage_slice']} | {row['language_pair']} | "
            f"{row['instruction_language']} | {row['content_language']} | {row['n']} | "
            f"{row['rows_with_preservation_spans']} | {row['total_preservation_spans']} |"
        )

    lines.extend(
        [
            "",
            "## Target Content Languages",
            "",
            "| Content language | Rows | Preserve rows | Preserve spans | Known-bad rows |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in by_content_language:
        lines.append(
            f"| {row['content_language']} | {row['n']} | "
            f"{row['rows_with_preservation_spans']} | {row['total_preservation_spans']} | "
            f"{row['rows_with_known_bad_outputs']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The packet gives reviewers one row per synthetic v0.3 item and keeps all",
            "review fields blank. It is designed to collect prompt clarity, target-language",
            "naturalness, script expectation, preservation-span, known-bad-output, and",
            "release-usability judgments. Completed reviewer labels and a qualified roster",
            "are still required before v0.3 can support paper-facing benchmark claims.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=Path("data/coverage_native_review_v03/coverage_native_review_packet_v03.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/coverage_native_review_v03_design"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/coverage_native_review_design_v03.md"))
    args = parser.parse_args()

    rows = read_csv(args.packet)
    summary = summary_row(rows)
    by_slice = count_by(rows, ("coverage_slice", "language_pair", "instruction_language", "content_language"))
    by_language_pair = count_by(rows, ("language_pair",))
    by_content_language = count_by(rows, ("content_language",))
    by_instruction_language = count_by(rows, ("instruction_language",))

    write_csv(args.out_dir / "coverage_native_review_summary.csv", [summary])
    write_csv(args.out_dir / "coverage_native_review_by_slice.csv", by_slice)
    write_csv(args.out_dir / "coverage_native_review_by_language_pair.csv", by_language_pair)
    write_csv(args.out_dir / "coverage_native_review_by_content_language.csv", by_content_language)
    write_csv(args.out_dir / "coverage_native_review_by_instruction_language.csv", by_instruction_language)
    write_markdown(args.out_md, summary, by_slice, by_content_language)
    print(f"wrote v0.3 coverage native-review design audit to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
