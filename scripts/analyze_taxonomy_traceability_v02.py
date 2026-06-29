#!/usr/bin/env python
"""Trace aggregate repair-cue categories to benchmark and scorer surfaces."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


SUMMARY_PATH = Path("results/discovery/wildchat_20k_repair_cues/summary.json")
CATEGORY_PATH = Path("results/discovery/wildchat_20k_repair_cues/cue_category_conversation_counts.csv")
BENCHMARK_PATH = Path("data/benchmark_stress_v0.2.jsonl")
OUT_DIR = Path("results/tables/taxonomy_traceability_v02")
OUT_MD = Path("paper/taxonomy_traceability_v02.md")


CATEGORY_MAPPING: dict[str, dict[str, Any]] = {
    "generic_repair": {
        "benchmark_families": ["all"],
        "scorer_or_metric_surface": "rtt;repair_at_1;repair_at_2;unresolved_rate",
        "direct_scorer_component": False,
        "traceability_note": "Generic repair cues motivate the multi-turn repair-tax metrics rather than a single deterministic failure component.",
    },
    "preservation_failure": {
        "benchmark_families": ["quote_preservation", "script_register_locale"],
        "scorer_or_metric_surface": "preservation_failure;task_noncompletion",
        "direct_scorer_component": True,
        "traceability_note": "Literal-span preservation rows directly exercise exact preservation and related task-completion checks.",
    },
    "register_locale_mismatch": {
        "benchmark_families": ["script_register_locale"],
        "scorer_or_metric_surface": "register_locale_mismatch",
        "direct_scorer_component": True,
        "traceability_note": "Script/register/locale rows directly exercise register and locale constraints where deterministic checks are possible.",
    },
    "script_mismatch": {
        "benchmark_families": ["script_register_locale"],
        "scorer_or_metric_surface": "script_mismatch;wrong_output_language",
        "direct_scorer_component": True,
        "traceability_note": "Script/register/locale rows directly exercise Latin, Arabic, and Devanagari script expectations.",
    },
    "unwanted_translation": {
        "benchmark_families": ["editing_preservation", "quote_preservation"],
        "scorer_or_metric_surface": "wrong_output_language;preservation_failure;task_noncompletion",
        "direct_scorer_component": True,
        "traceability_note": "Editing and quote-preservation rows stress cases where translating transparent content is a failure.",
    },
    "wrong_output_language": {
        "benchmark_families": ["editing_preservation", "output_language_inference"],
        "scorer_or_metric_surface": "wrong_output_language;script_mismatch",
        "direct_scorer_component": True,
        "traceability_note": "Editing-preservation and output-language-inference rows directly exercise expected output-language decisions.",
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing input table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, f"refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    require(path.exists(), f"missing benchmark {path}")
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


def build_traceability_rows(
    *,
    summary: dict[str, Any],
    category_rows: list[dict[str, str]],
    benchmark_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    family_counts = Counter(row["task_family"] for row in benchmark_rows)
    require(family_counts == Counter({"editing_preservation": 30, "output_language_inference": 30, "quote_preservation": 30, "script_register_locale": 30}), f"unexpected benchmark family counts: {family_counts}")
    require(set(summary["category_counts"]) == set(CATEGORY_MAPPING), "summary categories do not match traceability mapping")

    by_category = {row["category"]: row for row in category_rows}
    require(set(by_category) == set(CATEGORY_MAPPING), "category table does not match traceability mapping")

    out: list[dict[str, Any]] = []
    for category, mapping in sorted(CATEGORY_MAPPING.items()):
        families = list(mapping["benchmark_families"])
        if families == ["all"]:
            item_count = len(benchmark_rows)
            family_text = "all_v0.2_task_families"
        else:
            item_count = sum(family_counts[family] for family in families)
            family_text = ";".join(families)
        category_row = by_category[category]
        out.append(
            {
                "cue_category": category,
                "cue_hits": int(category_row["cue_hits"]),
                "unique_conversations": int(category_row["unique_conversations"]),
                "benchmark_surface": family_text,
                "benchmark_item_count": item_count,
                "scorer_or_metric_surface": mapping["scorer_or_metric_surface"],
                "direct_scorer_component": int(bool(mapping["direct_scorer_component"])),
                "traceability_note": mapping["traceability_note"],
            }
        )
    return out


def build_overview(summary: dict[str, Any], rows: list[dict[str, Any]], benchmark_rows: list[dict[str, Any]]) -> dict[str, Any]:
    mapped_categories = sum(1 for row in rows if row["benchmark_item_count"] > 0)
    direct_components = sum(int(row["direct_scorer_component"]) for row in rows)
    mapped_families = {
        family
        for row in rows
        for family in str(row["benchmark_surface"]).split(";")
        if family and family != "all_v0.2_task_families"
    }
    return {
        "dataset": summary["dataset"],
        "conversations_scanned": summary["conversations_scanned"],
        "multiturn_conversations": summary["multiturn_conversations"],
        "conversations_with_repair_cues": summary["conversations_with_repair_cues"],
        "cue_hits_total": summary["cue_hits_total"],
        "raw_text_written": summary["raw_text_written"],
        "cue_categories": len(rows),
        "mapped_categories": mapped_categories,
        "categories_with_direct_scorer_component": direct_components,
        "categories_mapped_to_repair_metrics": len(rows) - direct_components,
        "benchmark_items": len(benchmark_rows),
        "benchmark_families": len(mapped_families),
        "not_prevalence_estimate": 1,
    }


def write_markdown(path: Path, overview: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Taxonomy Traceability Audit v0.2",
        "",
        "This no-API audit links aggregate WildChat repair-cue categories to the",
        "synthetic benchmark families, deterministic scorer components, and repair",
        "metric surfaces used by RePromptTax-Stress-v0.2. It uses only aggregate",
        "cue counts, hashed metadata summaries, and benchmark schema fields; it",
        "does not inspect or release raw WildChat text and is not a prevalence",
        "estimate.",
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
            "## Category Mapping",
            "",
            "| Cue category | Cue hits | Unique conversations | Benchmark surface | Items | Scorer or metric surface |",
            "|---|---:|---:|---|---:|---|",
        ]
    )
    for row in rows:
        lines.append(
            "| "
            f"{row['cue_category']} | {row['cue_hits']} | {row['unique_conversations']} | "
            f"{row['benchmark_surface']} | {row['benchmark_item_count']} | "
            f"{row['scorer_or_metric_surface']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "All six discovery cue categories are mapped to at least one benchmark,",
            "scorer, or metric surface. Five of six categories map to deterministic",
            "scorer components; `generic_repair` maps to the multi-turn repair-tax",
            "metrics rather than a scorer component. This supports taxonomy",
            "traceability, not real-world prevalence or native-speaker validity.",
            "",
            "The mapping also clarifies the benchmark boundary: public-chat cues",
            "motivate the taxonomy, while the paper-facing claims remain anchored to",
            "the synthetic 120-item stress pilot, deterministic scorer audits,",
            "LLM-judge sanity checks, and future completed human/native labels.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, default=SUMMARY_PATH)
    parser.add_argument("--category-table", type=Path, default=CATEGORY_PATH)
    parser.add_argument("--benchmark", type=Path, default=BENCHMARK_PATH)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    require(summary["raw_text_written"] is False, "summary says raw WildChat text was written")
    category_rows = read_csv(args.category_table)
    benchmark_rows = load_jsonl(args.benchmark)
    require(len(benchmark_rows) == 120, f"expected 120 benchmark rows, found {len(benchmark_rows)}")

    traceability_rows = build_traceability_rows(summary=summary, category_rows=category_rows, benchmark_rows=benchmark_rows)
    overview = build_overview(summary, traceability_rows, benchmark_rows)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "taxonomy_traceability_by_category.csv", traceability_rows)
    write_csv(args.out_dir / "taxonomy_traceability_overview.csv", [overview])
    write_markdown(args.out_md, overview, traceability_rows)
    print(f"wrote taxonomy traceability audit to {args.out_md} and {args.out_dir}")


if __name__ == "__main__":
    main()
