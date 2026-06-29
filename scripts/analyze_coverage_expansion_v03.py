#!/usr/bin/env python
"""Audit the synthetic v0.3 coverage expansion scaffold."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


EXPECTED_ROWS = 60
EXPECTED_PER_SLICE = 10
EXPECTED_STATUS = "synthetic_scaffold_requires_native_validation"
PRIVACY_PATTERNS = {
    "email_address": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "url": re.compile(r"\b(?:https?://|www\.)\S+", re.IGNORECASE),
    "phone_like_number": re.compile(r"\b(?:\+?\d[\d ().-]{7,}\d)\b"),
    "ssn_like_number": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "placeholder_text": re.compile(r"\b(?:TODO|TBD|lorem ipsum|John Doe|Jane Doe)\b", re.IGNORECASE),
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON") from exc
            row["_line_no"] = line_no
            rows.append(row)
    return rows


def normalize_prompt(prompt: str) -> str:
    return re.sub(r"\W+", " ", prompt.lower()).strip()


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def privacy_hits(row: dict[str, Any]) -> list[str]:
    text = "\n".join(
        str(row.get(field, ""))
        for field in (
            "id",
            "user_prompt",
            "repair_prompt_1",
            "repair_prompt_2",
            "notes_for_annotators",
        )
    )
    return [name for name, pattern in PRIVACY_PATTERNS.items() if pattern.search(text)]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_rows(rows: list[dict[str, Any]]) -> None:
    require(len(rows) == EXPECTED_ROWS, f"expected {EXPECTED_ROWS} rows, found {len(rows)}")
    ids = [str(row.get("id", "")) for row in rows]
    require(len(ids) == len(set(ids)), "duplicate ids found")
    prompts = [str(row.get("user_prompt", "")) for row in rows]
    require(len(prompts) == len(set(prompts)), "duplicate prompts found")
    normalized = [normalize_prompt(prompt) for prompt in prompts]
    require(len(normalized) == len(set(normalized)), "normalized duplicate prompts found")

    slice_counts = Counter(row.get("coverage_slice") for row in rows)
    require(len(slice_counts) == 6, f"expected 6 coverage slices, found {len(slice_counts)}")
    for coverage_slice, count in slice_counts.items():
        require(count == EXPECTED_PER_SLICE, f"{coverage_slice} has {count} rows")

    for row in rows:
        row_id = row.get("id", f"line {row.get('_line_no', '?')}")
        for field in (
            "benchmark_version",
            "validation_status",
            "coverage_slice",
            "language_pair",
            "task_family",
            "user_prompt",
            "instruction_language",
            "content_language",
            "expected_response_language",
            "expected_script",
            "must_preserve_spans",
            "known_bad_outputs",
            "repair_prompt_1",
            "repair_prompt_2",
            "required_any_markers",
            "forbidden_markers",
            "notes_for_annotators",
            "stress_tag",
        ):
            require(field in row, f"{row_id} missing field {field}")
        require(row["task_family"] == "editing_preservation", f"{row_id} has unexpected task_family")
        require(row["validation_status"] == EXPECTED_STATUS, f"{row_id} has unexpected validation_status")
        require(row["expected_response_language"] != "English", f"{row_id} unexpectedly targets English output")
        require(row["must_preserve_spans"], f"{row_id} missing preservation spans")
        require(row["required_any_markers"], f"{row_id} missing required markers")
        require(row["known_bad_outputs"], f"{row_id} missing known-bad outputs")
        require(word_count(str(row["user_prompt"])) >= 8, f"{row_id} prompt is too short")
        hits = privacy_hits(row)
        require(not hits, f"{row_id} has privacy-like marker(s): {', '.join(hits)}")


def make_summary(rows: list[dict[str, Any]]) -> dict[str, int | float | str]:
    prompt_words = [word_count(str(row["user_prompt"])) for row in rows]
    preserve_counts = [len(row.get("must_preserve_spans") or []) for row in rows]
    return {
        "coverage_rows": len(rows),
        "benchmark_version": str(rows[0]["benchmark_version"]),
        "validation_status": EXPECTED_STATUS,
        "coverage_slices": len({row["coverage_slice"] for row in rows}),
        "language_pairs": len({row["language_pair"] for row in rows}),
        "task_families": len({row["task_family"] for row in rows}),
        "unique_user_prompts": len({row["user_prompt"] for row in rows}),
        "normalized_duplicate_prompts": len(rows) - len({normalize_prompt(row["user_prompt"]) for row in rows}),
        "rows_with_preservation_spans": sum(bool(row.get("must_preserve_spans")) for row in rows),
        "total_preservation_spans": sum(preserve_counts),
        "rows_requiring_native_validation": sum(row.get("validation_status") == EXPECTED_STATUS for row in rows),
        "model_result_rows": 0,
        "privacy_marker_hits": sum(len(privacy_hits(row)) for row in rows),
        "min_prompt_words": min(prompt_words),
        "mean_prompt_words": round(mean(prompt_words), 1),
        "max_prompt_words": max(prompt_words),
    }


def grouped(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[tuple(str(row[field]) for field in fields)].append(row)

    out: list[dict[str, Any]] = []
    for key, group in sorted(groups.items()):
        prompt_words = [word_count(str(row["user_prompt"])) for row in group]
        preserve_counts = [len(row.get("must_preserve_spans") or []) for row in group]
        result = {field: value for field, value in zip(fields, key)}
        result.update(
            {
                "n": len(group),
                "unique_user_prompts": len({row["user_prompt"] for row in group}),
                "rows_with_preservation_spans": sum(bool(row.get("must_preserve_spans")) for row in group),
                "total_preservation_spans": sum(preserve_counts),
                "rows_requiring_native_validation": sum(row.get("validation_status") == EXPECTED_STATUS for row in group),
                "mean_prompt_words": round(mean(prompt_words), 1),
            }
        )
        out.append(result)
    return out


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"cannot write empty CSV {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    by_slice = grouped(
        rows,
        (
            "coverage_slice",
            "language_pair",
            "instruction_language",
            "content_language",
            "expected_response_language",
            "expected_script",
        ),
    )

    lines = [
        "# Coverage Expansion v0.3 Scaffold",
        "",
        "Generated from `data/benchmark_stress_v0.3_expansion.jsonl`.",
        "",
        "This is a synthetic scaffold for non-English target-content editing coverage.",
        "It is not paper-facing model result evidence, and it requires native validation before claims.",
        "The v0.2 benchmark remains the original paper-facing stress pilot.",
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
            "| Slice | Pair | Instruction | Content | Expected response | Script | n | Preservation spans |",
            "|---|---|---|---|---|---|---:|---:|",
        ]
    )
    for row in by_slice:
        lines.append(
            "| "
            f"{row['coverage_slice']} | {row['language_pair']} | {row['instruction_language']} | "
            f"{row['content_language']} | {row['expected_response_language']} | {row['expected_script']} | "
            f"{row['n']} | {row['total_preservation_spans']} |"
        )

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- Treat this as benchmark-construction scaffolding only.",
            "- Do not merge these rows into headline v0.2 results without a native-speaker review pass.",
            "- Do not report model performance on this expansion until model outputs, scoring, and audit artifacts are generated.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, default=Path("data/benchmark_stress_v0.3_expansion.jsonl"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/coverage_expansion_v03"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/coverage_expansion_v03.md"))
    args = parser.parse_args()

    rows = load_jsonl(args.benchmark)
    validate_rows(rows)
    summary = make_summary(rows)
    by_slice = grouped(
        rows,
        (
            "coverage_slice",
            "language_pair",
            "instruction_language",
            "content_language",
            "expected_response_language",
            "expected_script",
        ),
    )
    by_content = grouped(rows, ("content_language", "expected_response_language", "expected_script"))
    privacy_rows = [{"privacy_marker_hits": summary["privacy_marker_hits"], "patterns_checked": len(PRIVACY_PATTERNS)}]

    write_csv(args.out_dir / "coverage_expansion_summary.csv", [summary])
    write_csv(args.out_dir / "coverage_expansion_by_slice.csv", by_slice)
    write_csv(args.out_dir / "coverage_expansion_by_content_language.csv", by_content)
    write_csv(args.out_dir / "coverage_expansion_privacy_scan.csv", privacy_rows)
    write_markdown(args.out_md, rows, summary)
    print(f"wrote coverage expansion audit for {len(rows)} rows to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
