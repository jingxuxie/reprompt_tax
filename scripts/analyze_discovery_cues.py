#!/usr/bin/env python
"""Analyze hashed repair-cue discovery metadata without raw text."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def read_csv(path: Path) -> list[dict[str, str]]:
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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def category_summary(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for category in sorted({row["category"] for row in rows}):
        category_rows = [row for row in rows if row["category"] == category]
        conversations = {row["conversation_hash"] for row in category_rows}
        row_languages = Counter(row["row_language"] for row in category_rows)
        message_languages = Counter(row["message_language"] for row in category_rows)
        out.append(
            {
                "category": category,
                "cue_hits": len(category_rows),
                "unique_conversations": len(conversations),
                "top_row_language": row_languages.most_common(1)[0][0],
                "top_row_language_hits": row_languages.most_common(1)[0][1],
                "top_message_language": message_languages.most_common(1)[0][0],
                "top_message_language_hits": message_languages.most_common(1)[0][1],
            }
        )
    return out


def language_category_rows(rows: list[dict[str, str]], language_field: str) -> list[dict[str, Any]]:
    counts = Counter((row[language_field], row["category"]) for row in rows)
    out: list[dict[str, Any]] = []
    for (language, category), count in sorted(counts.items()):
        out.append({"language_field": language_field, "language": language, "category": category, "cue_hits": count})
    return out


def cue_pattern_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    counts = Counter((row["category"], row["cue_pattern"]) for row in rows)
    out: list[dict[str, Any]] = []
    for (category, pattern), count in sorted(counts.items(), key=lambda item: (-item[1], item[0][0], item[0][1])):
        out.append({"category": category, "cue_pattern": pattern, "cue_hits": count})
    return out


def repeated_conversation_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    by_conversation: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_conversation[row["conversation_hash"]].append(row)
    out: list[dict[str, Any]] = []
    for conversation_hash, conversation_rows in sorted(by_conversation.items()):
        if len(conversation_rows) < 2:
            continue
        categories = Counter(row["category"] for row in conversation_rows)
        out.append(
            {
                "conversation_hash": conversation_hash,
                "cue_hits": len(conversation_rows),
                "unique_categories": len(categories),
                "categories": ";".join(f"{category}:{count}" for category, count in sorted(categories.items())),
                "row_languages": ";".join(sorted({row["row_language"] for row in conversation_rows})),
                "message_languages": ";".join(sorted({row["message_language"] for row in conversation_rows})),
            }
        )
    return out


def overview_row(summary: dict[str, Any], rows: list[dict[str, str]], repeated_rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "dataset": summary["dataset"],
        "split": summary["split"],
        "conversations_scanned": summary["conversations_scanned"],
        "user_turns_scanned": summary["user_turns_scanned"],
        "multiturn_conversations": summary["multiturn_conversations"],
        "conversations_with_repair_cues": summary["conversations_with_repair_cues"],
        "cue_hits_total": summary["cue_hits_total"],
        "metadata_rows": len(rows),
        "unique_conversations_in_metadata": len({row["conversation_hash"] for row in rows}),
        "repeated_cue_conversations": len(repeated_rows),
        "max_cue_hits_in_conversation": max(Counter(row["conversation_hash"] for row in rows).values()),
        "raw_text_written": summary["raw_text_written"],
    }


def write_markdown(
    path: Path,
    overview: dict[str, Any],
    category_rows: list[dict[str, Any]],
    pattern_rows: list[dict[str, Any]],
    repeated_rows: list[dict[str, Any]],
) -> None:
    lines = [
        "# Discovery Cue Analysis",
        "",
        "Generated from `results/discovery/wildchat_20k_repair_cues/summary.json`",
        "and `results/discovery/wildchat_20k_repair_cues/hit_metadata_hashed.csv`.",
        "",
        "This analysis uses only aggregate counts and hashed metadata. It writes no",
        "raw user or assistant text and must not be interpreted as a representative",
        "prevalence estimate.",
        "",
        "## Overview",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in overview.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(
        [
            "",
            "## Categories",
            "",
            "| Category | Cue hits | Unique conversations | Top row language | Top message language |",
            "|---|---:|---:|---|---|",
        ]
    )
    for row in category_rows:
        lines.append(
            "| "
            f"{row['category']} | {row['cue_hits']} | {row['unique_conversations']} | "
            f"{row['top_row_language']} ({row['top_row_language_hits']}) | "
            f"{row['top_message_language']} ({row['top_message_language_hits']}) |"
        )

    lines.extend(
        [
            "",
            "## Top Cue Patterns",
            "",
            "| Category | Cue pattern | Hits |",
            "|---|---|---:|",
        ]
    )
    for row in pattern_rows[:12]:
        pattern = str(row["cue_pattern"]).replace("|", "/")
        lines.append(f"| {row['category']} | `{pattern}` | {row['cue_hits']} |")

    lines.extend(
        [
            "",
            "## Repeated Cue Conversations",
            "",
            f"{overview['repeated_cue_conversations']} hashed conversations contain two or more cue hits; ",
            f"the maximum is {overview['max_cue_hits_in_conversation']} cue hits in one conversation.",
            "",
            "## Interpretation",
            "",
            "The cue scan supports the taxonomy used in the synthetic stress benchmark:",
            "generic repair, wrong output language, preservation, unwanted translation,",
            "script, and register/locale cues all occur in a bounded public-chat slice.",
            "Wrong-output-language cues are the most multilingual-looking category in",
            "the metadata, while generic repair cues are mostly English. Because the",
            "method is regex-based and no raw turns are inspected in this artifact, the",
            "result should be treated only as motivation for the benchmark taxonomy.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, default=Path("results/discovery/wildchat_20k_repair_cues/summary.json"))
    parser.add_argument("--metadata", type=Path, default=Path("results/discovery/wildchat_20k_repair_cues/hit_metadata_hashed.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/discovery/wildchat_20k_repair_cues"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/discovery_cue_analysis.md"))
    args = parser.parse_args()

    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    rows = read_csv(args.metadata)
    require(len(rows) == int(summary["cue_hits_total"]), "metadata row count does not match summary cue_hits_total")
    require(len({row["conversation_hash"] for row in rows}) == int(summary["conversations_with_repair_cues"]), "metadata conversation count does not match summary")
    require(not bool(summary["raw_text_written"]), "summary says raw text was written")

    category_rows = category_summary(rows)
    pattern_rows = cue_pattern_rows(rows)
    repeated_rows = repeated_conversation_rows(rows)
    language_rows = language_category_rows(rows, "row_language") + language_category_rows(rows, "message_language")
    overview = overview_row(summary, rows, repeated_rows)

    write_csv(args.out_dir / "cue_category_conversation_counts.csv", category_rows)
    write_csv(args.out_dir / "cue_pattern_counts.csv", pattern_rows)
    write_csv(args.out_dir / "cue_language_category_counts.csv", language_rows)
    write_csv(args.out_dir / "repeated_cue_conversations_hashed.csv", repeated_rows)
    write_csv(args.out_dir / "cue_discovery_overview.csv", [overview])
    write_markdown(args.out_md, overview, category_rows, pattern_rows, repeated_rows)
    print(f"wrote discovery cue analysis to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
