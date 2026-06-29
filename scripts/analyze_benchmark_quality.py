#!/usr/bin/env python
"""Audit release-facing benchmark quality for RePromptTax-Stress-v0.2."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


LANGUAGE_PAIRS = ("es-en", "hi-en", "ar-en")
TASK_FAMILIES = (
    "editing_preservation",
    "output_language_inference",
    "quote_preservation",
    "script_register_locale",
)
STRESS_TAGS = (
    "implicit_content_language",
    "correction_only",
    "translatable_quoted_heading",
    "literal_locale_span",
)

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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


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


def check_rows(rows: list[dict[str, Any]], expected_per_cell: int) -> None:
    expected_total = len(LANGUAGE_PAIRS) * len(TASK_FAMILIES) * expected_per_cell
    require(len(rows) == expected_total, f"expected {expected_total} rows, found {len(rows)}")

    ids = [str(row.get("id", "")) for row in rows]
    require(len(ids) == len(set(ids)), "duplicate benchmark ids found")

    prompts = [str(row.get("user_prompt", "")) for row in rows]
    require(len(prompts) == len(set(prompts)), "exact duplicate user prompts found")
    normalized_prompts = [normalize_prompt(prompt) for prompt in prompts]
    require(len(normalized_prompts) == len(set(normalized_prompts)), "normalized duplicate user prompts found")

    counts = Counter((row.get("language_pair"), row.get("task_family")) for row in rows)
    for pair in LANGUAGE_PAIRS:
        for family in TASK_FAMILIES:
            require(counts[(pair, family)] == expected_per_cell, f"unexpected count for {pair}/{family}")

    stress_counts = Counter(row.get("stress_tag") for row in rows)
    for tag in STRESS_TAGS:
        require(stress_counts[tag] == expected_per_cell * len(LANGUAGE_PAIRS), f"unexpected count for stress_tag={tag}")

    for row in rows:
        row_id = row.get("id", f"line {row.get('_line_no', '?')}")
        require(row.get("language_pair") in LANGUAGE_PAIRS, f"{row_id} unknown language_pair")
        require(row.get("task_family") in TASK_FAMILIES, f"{row_id} unknown task_family")
        require(row.get("stress_tag") in STRESS_TAGS, f"{row_id} unknown stress_tag")
        require(str(row.get("user_prompt", "")).strip(), f"{row_id} missing user_prompt")
        require(str(row.get("repair_prompt_1", "")).strip(), f"{row_id} missing repair_prompt_1")
        require(str(row.get("repair_prompt_2", "")).strip(), f"{row_id} missing repair_prompt_2")
        require(row.get("known_bad_outputs"), f"{row_id} missing known_bad_outputs")
        require(row.get("required_any_markers"), f"{row_id} missing required_any_markers")
        require(str(row.get("notes_for_annotators", "")).strip(), f"{row_id} missing notes_for_annotators")
        require(word_count(str(row["user_prompt"])) >= 8, f"{row_id} prompt is too short to be realistic")
        if row["task_family"] in {"quote_preservation", "script_register_locale"}:
            require(row.get("must_preserve_spans"), f"{row_id} missing preservation spans")
        else:
            require(not row.get("must_preserve_spans"), f"{row_id} has unexpected preservation spans")
        hits = privacy_hits(row)
        require(not hits, f"{row_id} has privacy-like marker(s): {', '.join(hits)}")


def make_summary(rows: list[dict[str, Any]]) -> dict[str, str | int | float]:
    prompt_words = [word_count(str(row["user_prompt"])) for row in rows]
    preserve_counts = [len(row.get("must_preserve_spans") or []) for row in rows]
    forbidden_counts = [len(row.get("forbidden_markers") or []) for row in rows]
    return {
        "benchmark_rows": len(rows),
        "language_pairs": len({row["language_pair"] for row in rows}),
        "task_families": len({row["task_family"] for row in rows}),
        "stress_tags": len({row["stress_tag"] for row in rows}),
        "unique_user_prompts": len({row["user_prompt"] for row in rows}),
        "normalized_duplicate_prompts": len(rows) - len({normalize_prompt(row["user_prompt"]) for row in rows}),
        "rows_with_required_markers": sum(bool(row.get("required_any_markers")) for row in rows),
        "rows_with_known_bad_outputs": sum(bool(row.get("known_bad_outputs")) for row in rows),
        "rows_with_forbidden_markers": sum(bool(row.get("forbidden_markers")) for row in rows),
        "rows_with_preservation_spans": sum(bool(row.get("must_preserve_spans")) for row in rows),
        "total_preservation_spans": sum(preserve_counts),
        "total_forbidden_markers": sum(forbidden_counts),
        "privacy_marker_hits": sum(len(privacy_hits(row)) for row in rows),
        "min_prompt_words": min(prompt_words),
        "mean_prompt_words": round(mean(prompt_words), 1),
        "max_prompt_words": max(prompt_words),
    }


def group_rows(rows: list[dict[str, Any]], key_fields: tuple[str, ...]) -> list[dict[str, str | int | float]]:
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[tuple(str(row[field]) for field in key_fields)].append(row)

    out: list[dict[str, str | int | float]] = []
    for key, group in sorted(groups.items()):
        prompt_words = [word_count(str(row["user_prompt"])) for row in group]
        preserve_counts = [len(row.get("must_preserve_spans") or []) for row in group]
        row: dict[str, str | int | float] = {field: value for field, value in zip(key_fields, key)}
        row.update(
            {
                "n": len(group),
                "unique_user_prompts": len({item["user_prompt"] for item in group}),
                "rows_with_required_markers": sum(bool(item.get("required_any_markers")) for item in group),
                "rows_with_known_bad_outputs": sum(bool(item.get("known_bad_outputs")) for item in group),
                "rows_with_forbidden_markers": sum(bool(item.get("forbidden_markers")) for item in group),
                "rows_with_preservation_spans": sum(bool(item.get("must_preserve_spans")) for item in group),
                "total_preservation_spans": sum(preserve_counts),
                "min_prompt_words": min(prompt_words),
                "mean_prompt_words": round(mean(prompt_words), 1),
                "max_prompt_words": max(prompt_words),
            }
        )
        out.append(row)
    return out


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"cannot write empty CSV {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, Any]], summary: dict[str, str | int | float]) -> None:
    family_rows = group_rows(rows, ("task_family",))
    language_rows = group_rows(rows, ("language_pair",))
    tag_counts = Counter(row["stress_tag"] for row in rows)

    lines = [
        "# Benchmark Quality Audit",
        "",
        "Generated from `data/benchmark_stress_v0.2.jsonl`.",
        "",
        "This audit checks release-facing benchmark hygiene: balance, duplicate",
        "prompts, scoring-marker coverage, preservation-span coverage, prompt",
        "lengths, and privacy-like markers. It is not a substitute for native",
        "speaker validation of semantic or register judgments.",
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
            "## By Task Family",
            "",
            "| Family | n | Required markers | Known-bad outputs | Forbidden markers | Rows with preservation spans | Total preservation spans | Mean prompt words |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in family_rows:
        lines.append(
            "| "
            f"{row['task_family']} | {row['n']} | {row['rows_with_required_markers']} | "
            f"{row['rows_with_known_bad_outputs']} | {row['rows_with_forbidden_markers']} | "
            f"{row['rows_with_preservation_spans']} | {row['total_preservation_spans']} | "
            f"{row['mean_prompt_words']} |"
        )

    lines.extend(
        [
            "",
            "## By Language Pair",
            "",
            "| Language pair | n | Unique prompts | Rows with preservation spans | Mean prompt words |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in language_rows:
        lines.append(
            "| "
            f"{row['language_pair']} | {row['n']} | {row['unique_user_prompts']} | "
            f"{row['rows_with_preservation_spans']} | {row['mean_prompt_words']} |"
        )

    lines.extend(["", "## Stress Tags", "", "| Stress tag | n |", "|---|---:|"])
    for tag, count in sorted(tag_counts.items()):
        lines.append(f"| {tag} | {count} |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The released stress pilot is balanced across the planned 3 x 4 design,",
            "contains no exact or normalized duplicate user prompts, and contains no",
            "email, URL, phone-like, SSN-like, or placeholder privacy markers under",
            "the audit regexes. All rows include required scoring markers and",
            "known-bad-output notes. Preservation spans are intentionally present",
            "only in quote-preservation and script/register/locale items.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, default=Path("data/benchmark_stress_v0.2.jsonl"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/benchmark_quality_v02"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/benchmark_quality_audit_v02.md"))
    parser.add_argument("--expected-per-cell", type=int, default=10)
    args = parser.parse_args()

    rows = load_jsonl(args.benchmark)
    check_rows(rows, args.expected_per_cell)

    summary = make_summary(rows)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "benchmark_quality_summary.csv", [summary])
    write_csv(args.out_dir / "benchmark_quality_by_family.csv", group_rows(rows, ("task_family",)))
    write_csv(args.out_dir / "benchmark_quality_by_language.csv", group_rows(rows, ("language_pair",)))
    write_csv(
        args.out_dir / "benchmark_quality_by_language_family.csv",
        group_rows(rows, ("language_pair", "task_family")),
    )
    write_markdown(args.out_md, rows, summary)
    print(f"wrote benchmark-quality audit to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
