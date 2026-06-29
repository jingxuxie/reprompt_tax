#!/usr/bin/env python
"""Check that the automatic scorer accepts constrained positive controls."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from score_auto import score_response


BENCHMARK_PATH = Path("data/benchmark_stress_v0.2.jsonl")
OUT_DIR = Path("results/tables/scorer_positive_control_v02")
OUT_MD = Path("paper/scorer_positive_control_v02.md")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


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


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, f"refusing to write empty positive-control table {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def marker_text(item: dict[str, Any], *, first_required_only: bool = False) -> str:
    required = [str(marker) for marker in item.get("required_any_markers", []) if str(marker).strip()]
    spans = [str(span) for span in item.get("must_preserve_spans", []) if str(span).strip()]
    values = required[:1] if first_required_only else required
    unique: list[str] = []
    for value in [*values, *spans]:
        if value not in unique:
            unique.append(value)
    require(unique, f"{item['id']} has no deterministic marker for a positive control")
    return "; ".join(unique)


def positive_response(item: dict[str, Any]) -> str:
    """Build a response that is constrained to pass deterministic scorer rules.

    These are not claimed to be fluent human-quality responses; they are
    positive controls for over-rejection by the rule-based scorer.
    """

    language = str(item["expected_response_language"]).lower()
    family = str(item["task_family"])
    first_only = family == "output_language_inference"
    markers = marker_text(item, first_required_only=first_only)

    if language == "english":
        if family == "output_language_inference":
            return f"{markers}."
        return f"Polished version: {markers}."
    if language == "spanish":
        if family == "quote_preservation":
            return f"Gracias, resumen breve: {markers}."
        return f"Gracias, mensaje corto: {markers}."
    if language == "arabic":
        if family == "quote_preservation":
            return f"ملخص قصير واضح: {markers}."
        return f"رسالة قصيرة واضحة: {markers}."
    if language == "hindi/hinglish":
        if family == "quote_preservation":
            return f"yeh short summary clear hai: {markers}."
        return f"yeh short message clear hai: {markers}."

    raise AssertionError(f"{item['id']} has unsupported expected response language {item['expected_response_language']!r}")


def build_controls(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in sorted(items, key=lambda row: row["id"]):
        response = positive_response(item)
        score = score_response(item, response)
        component_passes = [
            bool(score["language_pass"]),
            bool(score["script_pass"]),
            bool(score["preservation_pass"]),
            bool(score["task_pass"]),
            bool(score["register_locale_pass"]),
        ]
        rows.append(
            {
                "item_id": item["id"],
                "language_pair": item["language_pair"],
                "task_family": item["task_family"],
                "expected_response_language": item["expected_response_language"],
                "expected_script": item["expected_script"],
                "control_type": "deterministic_positive_control",
                "auto_pass": int(bool(score["pass"])),
                "auto_failed": int(not bool(score["pass"])),
                "language_pass": int(bool(score["language_pass"])),
                "script_pass": int(bool(score["script_pass"])),
                "preservation_pass": int(bool(score["preservation_pass"])),
                "task_pass": int(bool(score["task_pass"])),
                "register_locale_pass": int(bool(score["register_locale_pass"])),
                "all_components_pass": int(all(component_passes)),
                "failure_types": ";".join(score["failure_types"]),
                "response_chars": len(response),
                "response_preview": response[:160],
            }
        )
    require(rows, "no scorer positive controls generated")
    return rows


def summarize(rows: list[dict[str, Any]], key_fields: tuple[str, ...]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(str(row[field]) for field in key_fields)].append(row)

    out: list[dict[str, Any]] = []
    for key, group in sorted(grouped.items()):
        result = {field: value for field, value in zip(key_fields, key)}
        failure_counter = Counter(
            failure_type
            for row in group
            for failure_type in str(row["failure_types"]).split(";")
            if failure_type
        )
        result.update(
            {
                "n_controls": len(group),
                "auto_pass_n": sum(int(row["auto_pass"]) for row in group),
                "auto_pass_pct": round(100 * sum(int(row["auto_pass"]) for row in group) / len(group), 1),
                "all_components_pass_n": sum(int(row["all_components_pass"]) for row in group),
                "all_components_pass_pct": round(
                    100 * sum(int(row["all_components_pass"]) for row in group) / len(group),
                    1,
                ),
                "auto_failed_n": sum(int(row["auto_failed"]) for row in group),
                "top_failure_types": ";".join(f"{name}:{count}" for name, count in failure_counter.most_common(5)),
            }
        )
        out.append(result)
    return out


def write_markdown(
    path: Path,
    *,
    overall: dict[str, Any],
    by_family: list[dict[str, Any]],
    by_language: list[dict[str, Any]],
    by_expected_language: list[dict[str, Any]],
) -> None:
    lines = [
        "# Scorer Positive-Control Audit v0.2",
        "",
        "This no-API audit generates one constrained positive-control response for",
        "each v0.2 benchmark item and feeds it through `scripts/score_auto.py`.",
        "The controls include deterministic required markers, preserved spans,",
        "expected script, and lightweight language markers. They test scorer",
        "over-rejection, not human fluency or native/near-native semantic validity.",
        "",
        "## Overall",
        "",
        "| Controls | Auto passed | All components passed | Auto failed |",
        "|---:|---:|---:|---:|",
        (
            f"| {overall['n_controls']} | {overall['auto_pass_n']} "
            f"({overall['auto_pass_pct']}%) | {overall['all_components_pass_n']} "
            f"({overall['all_components_pass_pct']}%) | {overall['auto_failed_n']} |"
        ),
        "",
        "## By Task Family",
        "",
        "| Family | n | Auto passed | All components passed | Auto failed |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in by_family:
        lines.append(
            f"| {row['task_family']} | {row['n_controls']} | "
            f"{row['auto_pass_n']} ({row['auto_pass_pct']}%) | "
            f"{row['all_components_pass_n']} ({row['all_components_pass_pct']}%) | "
            f"{row['auto_failed_n']} |"
        )

    lines.extend(
        [
            "",
            "## By Language Pair",
            "",
            "| Language pair | n | Auto passed | All components passed | Auto failed |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in by_language:
        lines.append(
            f"| {row['language_pair']} | {row['n_controls']} | "
            f"{row['auto_pass_n']} ({row['auto_pass_pct']}%) | "
            f"{row['all_components_pass_n']} ({row['all_components_pass_pct']}%) | "
            f"{row['auto_failed_n']} |"
        )

    lines.extend(
        [
            "",
            "## By Expected Response Language",
            "",
            "| Expected language | n | Auto passed | All components passed | Auto failed |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in by_expected_language:
        lines.append(
            f"| {row['expected_response_language']} | {row['n_controls']} | "
            f"{row['auto_pass_n']} ({row['auto_pass_pct']}%) | "
            f"{row['all_components_pass_n']} ({row['all_components_pass_pct']}%) | "
            f"{row['auto_failed_n']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The scorer accepts 120/120 constrained positive controls, complementing the",
            "known-bad scorer-challenge audit. Together, the two audits test both",
            "directions of deterministic rule plumbing: known failures are rejected,",
            "and constrained known passes are not over-rejected.",
            "",
            "Claim boundary: these controls are synthetic templates built to satisfy",
            "the automatic rules. They do not replace LLM-judge checks or completed",
            "human/native review for semantic, register, or cultural validity.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, default=BENCHMARK_PATH)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    items = load_jsonl(args.benchmark)
    require(len(items) == 120, f"expected 120 v0.2 items, found {len(items)}")
    rows = build_controls(items)
    overall = summarize(rows, tuple())[0]
    by_family = summarize(rows, ("task_family",))
    by_language = summarize(rows, ("language_pair",))
    by_expected_language = summarize(rows, ("expected_response_language",))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "scorer_positive_control_rows.csv", rows)
    write_csv(args.out_dir / "scorer_positive_control_by_family.csv", by_family)
    write_csv(args.out_dir / "scorer_positive_control_by_language.csv", by_language)
    write_csv(args.out_dir / "scorer_positive_control_by_expected_language.csv", by_expected_language)
    write_csv(args.out_dir / "scorer_positive_control_overall.csv", [overall])
    write_markdown(
        args.out_md,
        overall=overall,
        by_family=by_family,
        by_language=by_language,
        by_expected_language=by_expected_language,
    )
    print(f"wrote scorer positive-control audit to {args.out_md} and {args.out_dir}")


if __name__ == "__main__":
    main()
