#!/usr/bin/env python
"""Validate taxonomy traceability audit artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_OVERVIEW = {
    "dataset": "allenai/WildChat",
    "conversations_scanned": "20000",
    "multiturn_conversations": "10681",
    "conversations_with_repair_cues": "172",
    "cue_hits_total": "219",
    "raw_text_written": "False",
    "cue_categories": "6",
    "mapped_categories": "6",
    "categories_with_direct_scorer_component": "5",
    "categories_mapped_to_repair_metrics": "1",
    "benchmark_items": "120",
    "benchmark_families": "4",
    "not_prevalence_estimate": "1",
}

EXPECTED_CATEGORIES = {
    "generic_repair": {
        "cue_hits": "93",
        "unique_conversations": "81",
        "benchmark_surface": "all_v0.2_task_families",
        "benchmark_item_count": "120",
        "direct_scorer_component": "0",
    },
    "preservation_failure": {
        "cue_hits": "25",
        "unique_conversations": "18",
        "benchmark_surface": "quote_preservation;script_register_locale",
        "benchmark_item_count": "60",
        "direct_scorer_component": "1",
    },
    "register_locale_mismatch": {
        "cue_hits": "16",
        "unique_conversations": "13",
        "benchmark_surface": "script_register_locale",
        "benchmark_item_count": "30",
        "direct_scorer_component": "1",
    },
    "script_mismatch": {
        "cue_hits": "4",
        "unique_conversations": "2",
        "benchmark_surface": "script_register_locale",
        "benchmark_item_count": "30",
        "direct_scorer_component": "1",
    },
    "unwanted_translation": {
        "cue_hits": "13",
        "unique_conversations": "13",
        "benchmark_surface": "editing_preservation;quote_preservation",
        "benchmark_item_count": "60",
        "direct_scorer_component": "1",
    },
    "wrong_output_language": {
        "cue_hits": "68",
        "unique_conversations": "48",
        "benchmark_surface": "editing_preservation;output_language_inference",
        "benchmark_item_count": "60",
        "direct_scorer_component": "1",
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing taxonomy traceability table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_overview(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == 1, "expected one taxonomy traceability overview row")
    row = rows[0]
    for field, expected in EXPECTED_OVERVIEW.items():
        require(row[field] == expected, f"overview/{field}: expected {expected}, got {row[field]}")


def check_categories(path: Path) -> None:
    rows = {row["cue_category"]: row for row in read_csv(path)}
    require(set(rows) == set(EXPECTED_CATEGORIES), f"unexpected taxonomy categories: {sorted(rows)}")
    for category, expected_fields in EXPECTED_CATEGORIES.items():
        row = rows[category]
        for field, expected in expected_fields.items():
            require(row[field] == expected, f"{category}/{field}: expected {expected}, got {row[field]}")
        require(row["scorer_or_metric_surface"].strip(), f"{category} missing scorer_or_metric_surface")
        require(row["traceability_note"].strip(), f"{category} missing traceability note")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing taxonomy traceability report {path}")
    text = " ".join(path.read_text(encoding="utf-8").split())
    for phrase in (
        "Taxonomy Traceability Audit v0.2",
        "does not inspect or release raw WildChat text",
        "is not a prevalence estimate",
        "All six discovery cue categories are mapped",
        "Five of six categories map to deterministic scorer components",
        "`generic_repair` maps to the multi-turn repair-tax metrics",
        "taxonomy traceability, not real-world prevalence or native-speaker validity",
    ):
        require(phrase in text, f"taxonomy traceability report missing phrase: {phrase}")


def check_main_tex(path: Path) -> None:
    require(path.exists(), f"missing main TeX {path}")
    text = " ".join(path.read_text(encoding="utf-8").split())
    for phrase in (
        "A traceability audit maps all six cue categories",
        "five categories map to deterministic scorer components",
        "generic repair maps to repair-tax metrics",
    ):
        require(phrase in text, f"main TeX missing taxonomy traceability phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/taxonomy_traceability_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/taxonomy_traceability_v02.md"))
    parser.add_argument("--main-tex", type=Path, default=Path("paper/sections/03_benchmark_construction.tex"))
    args = parser.parse_args()

    check_overview(args.out_dir / "taxonomy_traceability_overview.csv")
    check_categories(args.out_dir / "taxonomy_traceability_by_category.csv")
    check_report(args.report)
    check_main_tex(args.main_tex)
    print("taxonomy traceability validation passed")


if __name__ == "__main__":
    main()
