#!/usr/bin/env python
"""Analyze double-reviewer agreement for v0.3 coverage native review."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

from summarize_human_audit import cohen_kappa
from validate_completed_coverage_native_review_v03 import (
    BOOLEAN_FIELDS,
    COMPONENT_FIELDS,
    EXPECTED_SLICES,
    STATIC_FIELDS,
    parse_bool,
    parse_issue_types,
    read_csv,
    require,
    validate_roster,
)


COMPONENTS = [
    ("prompt_clear", "reviewer_prompt_clear"),
    ("target_language_natural", "reviewer_target_language_natural"),
    ("script_expectation_valid", "reviewer_script_expectation_valid"),
    ("preservation_spans_valid", "reviewer_preservation_spans_valid"),
    ("known_bad_outputs_valid", "reviewer_known_bad_outputs_valid"),
    ("release_usable", "reviewer_release_usable"),
]

ADJUDICATION_FIELDS = [
    "adjudicator_id",
    "adjudicated_prompt_clear",
    "adjudicated_target_language_natural",
    "adjudicated_script_expectation_valid",
    "adjudicated_preservation_spans_valid",
    "adjudicated_known_bad_outputs_valid",
    "adjudicated_release_usable",
    "adjudicated_issue_types",
    "adjudication_notes",
]

REVIEWER_FIELDS = [
    "reviewer_id",
    *BOOLEAN_FIELDS,
    "reviewer_issue_types",
    "reviewer_notes",
]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def bool_text(value: bool) -> str:
    return "TRUE" if value else "FALSE"


def normalized_issue_types(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(sorted(parse_issue_types(row.get("reviewer_issue_types", ""), row_id=row["review_id"])))


def parse_review_values(row: dict[str, str]) -> dict[str, bool]:
    row_id = row["review_id"]
    values = {field: parse_bool(row.get(field), row_id=row_id, field=field) for field in BOOLEAN_FIELDS}
    expected_release = all(values[field] for field in COMPONENT_FIELDS)
    require(
        values["reviewer_release_usable"] == expected_release,
        f"{row_id} reviewer_release_usable must equal conjunction of component labels",
    )
    issue_types = parse_issue_types(row.get("reviewer_issue_types", ""), row_id=row_id)
    if values["reviewer_release_usable"]:
        require(not issue_types, f"{row_id} is release-usable but lists reviewer_issue_types")
    else:
        require(issue_types, f"{row_id} is not release-usable but has no reviewer_issue_types")
        if "other" in issue_types:
            require(row.get("reviewer_notes", "").strip(), f"{row_id} uses other without reviewer_notes")
    return values


def validate_reviewer_assignment(
    row: dict[str, str],
    *,
    roster_by_id: dict[str, dict[str, str]],
    reviewer_field: str = "reviewer_id",
) -> str:
    row_id = row["review_id"]
    reviewer_id = row.get(reviewer_field, "").strip()
    require(reviewer_id, f"{row_id} missing {reviewer_field}")
    require(reviewer_id in roster_by_id, f"{row_id} {reviewer_field} {reviewer_id!r} is not in roster")
    roster = roster_by_id[reviewer_id]
    require(roster["coverage_slice"].strip() == row["coverage_slice"], f"{row_id} reviewer {reviewer_id} is not assigned to {row['coverage_slice']}")
    if roster.get("language_pair", "").strip():
        require(roster["language_pair"].strip() == row["language_pair"], f"{row_id} reviewer {reviewer_id} language_pair mismatch")
    if roster.get("target_content_language", "").strip():
        require(
            roster["target_content_language"].strip() == row["content_language"],
            f"{row_id} reviewer {reviewer_id} target_content_language mismatch",
        )
    return reviewer_id


def validate_long_reviews(
    *,
    annotation_rows: list[dict[str, str]],
    launch_rows: list[dict[str, str]],
    roster_rows: list[dict[str, str]],
    min_reviewers_per_item: int = 2,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    require(len(launch_rows) == 60, f"expected 60 v0.3 launch rows, found {len(launch_rows)}")
    require(annotation_rows, "double-review file is empty")
    require(min_reviewers_per_item >= 2, "min_reviewers_per_item must be at least 2")

    fields = set(annotation_rows[0])
    missing_fields = [field for field in (*STATIC_FIELDS, *REVIEWER_FIELDS) if field not in fields]
    require(not missing_fields, f"double-review file missing fields: {missing_fields}")

    launch_by_id = {row["review_id"]: row for row in launch_rows}
    require(len(launch_by_id) == len(launch_rows), "duplicate review_id values in launch packet")
    unknown = sorted({row["review_id"] for row in annotation_rows} - set(launch_by_id))
    require(not unknown, f"double reviews contain review IDs not in launch packet: {unknown[:5]}")

    roster_by_id = validate_roster(roster_rows)
    rows_by_review: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen_pairs: set[tuple[str, str]] = set()
    reviewer_ids: set[str] = set()
    parsed_by_pair: dict[tuple[str, str], dict[str, bool]] = {}

    for row in annotation_rows:
        row_id = row["review_id"]
        launch = launch_by_id[row_id]
        for field in STATIC_FIELDS:
            require(row.get(field, "") == launch.get(field, ""), f"{row_id} changed static launch field {field}")
        reviewer_id = validate_reviewer_assignment(row, roster_by_id=roster_by_id)
        pair_key = (row_id, reviewer_id)
        require(pair_key not in seen_pairs, f"{row_id} has duplicate review from {reviewer_id}")
        seen_pairs.add(pair_key)
        reviewer_ids.add(reviewer_id)
        parsed_by_pair[pair_key] = parse_review_values(row)
        rows_by_review[row_id].append(row)

    missing = sorted(review_id for review_id in launch_by_id if len(rows_by_review[review_id]) < min_reviewers_per_item)
    require(
        not missing,
        f"{len(missing)} review IDs have fewer than {min_reviewers_per_item} reviews; first missing: {missing[:5]}",
    )

    counts = Counter(row["coverage_slice"] for row in launch_rows)
    require(set(counts) == EXPECTED_SLICES, f"v0.3 launch slices mismatch: {set(counts)}")
    require(all(count == 10 for count in counts.values()), f"v0.3 launch slice counts mismatch: {counts}")

    item_rows = [
        {
            "review_id": review_id,
            **launch_by_id[review_id],
            "review_n": len(rows_by_review[review_id]),
            "reviewer_ids": ";".join(sorted(row["reviewer_id"] for row in rows_by_review[review_id])),
        }
        for review_id in sorted(launch_by_id)
    ]
    summary = summarize_items(item_rows, rows_by_review, parsed_by_pair)
    by_slice = [
        {"coverage_slice": coverage_slice, **summarize_items(group, rows_by_review, parsed_by_pair)}
        for coverage_slice, group in grouped_items(item_rows, "coverage_slice").items()
    ]
    by_content_language = [
        {"content_language": content_language, **summarize_items(group, rows_by_review, parsed_by_pair)}
        for content_language, group in grouped_items(item_rows, "content_language").items()
    ]
    by_instruction_language = [
        {"instruction_language": instruction_language, **summarize_items(group, rows_by_review, parsed_by_pair)}
        for instruction_language, group in grouped_items(item_rows, "instruction_language").items()
    ]
    summary.update(
        {
            "review_items": len(launch_rows),
            "annotation_rows": len(annotation_rows),
            "reviewers": len(reviewer_ids),
            "min_reviews_per_item": min(len(rows_by_review[review_id]) for review_id in launch_by_id),
            "max_reviews_per_item": max(len(rows_by_review[review_id]) for review_id in launch_by_id),
            "items_with_min_reviews": sum(
                len(rows_by_review[review_id]) >= min_reviewers_per_item for review_id in launch_by_id
            ),
        }
    )
    adjudication = adjudication_rows(rows_by_review, parsed_by_pair)
    return summary, by_slice, by_content_language, by_instruction_language, adjudication


def grouped_items(item_rows: list[dict[str, Any]], field: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in item_rows:
        grouped[str(row[field])].append(row)
    return dict(sorted(grouped.items()))


def summarize_items(
    item_rows: list[dict[str, Any]],
    rows_by_review: dict[str, list[dict[str, str]]],
    parsed_by_pair: dict[tuple[str, str], dict[str, bool]],
) -> dict[str, Any]:
    component_pairs: dict[str, list[tuple[bool, bool]]] = {name: [] for name, _ in COMPONENTS}
    release_disagreement_items = 0
    component_disagreement_items = 0
    issue_type_disagreement_items = 0

    for item in item_rows:
        rows = rows_by_review[item["review_id"]]
        item_has_release_disagreement = False
        item_has_component_disagreement = False
        for left, right in combinations(rows, 2):
            left_values = parsed_by_pair[(left["review_id"], left["reviewer_id"])]
            right_values = parsed_by_pair[(right["review_id"], right["reviewer_id"])]
            for name, field in COMPONENTS:
                pair = (left_values[field], right_values[field])
                component_pairs[name].append(pair)
                if pair[0] != pair[1]:
                    item_has_component_disagreement = True
                    if name == "release_usable":
                        item_has_release_disagreement = True
        release_disagreement_items += int(item_has_release_disagreement)
        component_disagreement_items += int(item_has_component_disagreement)
        issue_type_disagreement_items += int(len({normalized_issue_types(row) for row in rows}) > 1)

    out: dict[str, Any] = {
        "items": len(item_rows),
        "items_with_release_disagreement": release_disagreement_items,
        "items_with_component_disagreement": component_disagreement_items,
        "items_with_issue_type_disagreement": issue_type_disagreement_items,
    }
    for name, pairs in component_pairs.items():
        out[f"{name}_pair_count"] = len(pairs)
        out[f"{name}_pairwise_agreement"] = round(sum(a == b for a, b in pairs) / len(pairs), 4) if pairs else ""
        kappa = cohen_kappa(pairs)
        out[f"{name}_pairwise_kappa"] = round(kappa, 4) if isinstance(kappa, float) else kappa
    return out


def adjudication_rows(
    rows_by_review: dict[str, list[dict[str, str]]],
    parsed_by_pair: dict[tuple[str, str], dict[str, bool]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for review_id, rows in sorted(rows_by_review.items()):
        disagreed_components: list[str] = []
        for name, field in COMPONENTS:
            values = {parsed_by_pair[(row["review_id"], row["reviewer_id"])][field] for row in rows}
            if len(values) > 1:
                disagreed_components.append(name)
        issue_type_values = {normalized_issue_types(row) for row in rows}
        if len(issue_type_values) > 1:
            disagreed_components.append("issue_types")
        if not disagreed_components:
            continue

        first = rows[0]
        base = {field: first.get(field, "") for field in STATIC_FIELDS}
        base.update(
            {
                "reviewer_ids": ";".join(row["reviewer_id"] for row in rows),
                "disagreed_components": ";".join(disagreed_components),
            }
        )
        for _, field in COMPONENTS:
            base[f"{field}_by_reviewer"] = ";".join(
                f"{row['reviewer_id']}={bool_text(parsed_by_pair[(row['review_id'], row['reviewer_id'])][field])}"
                for row in rows
            )
        base["reviewer_issue_types_by_reviewer"] = ";".join(
            f"{row['reviewer_id']}={row.get('reviewer_issue_types', '')}" for row in rows
        )
        base["reviewer_notes_by_reviewer"] = ";".join(
            f"{row['reviewer_id']}={row.get('reviewer_notes', '')}" for row in rows
        )
        base.update({field: "" for field in ADJUDICATION_FIELDS})
        out.append(base)
    return out


def write_markdown(path: Path, summary: dict[str, Any], adjudication_count: int) -> None:
    lines = [
        "# v0.3 Coverage Native-Review Inter-Reviewer And Adjudication Analysis",
        "",
        "This report is generated after completed independent native-review labels",
        "are available. It supports the stronger two-reviewer-plus-adjudication",
        "workflow for the synthetic v0.3 coverage scaffold; it is not completed",
        "native validation by itself.",
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
            "## Adjudication",
            "",
            f"Rows requiring adjudication: {adjudication_count}.",
            "",
            "Use the generated adjudication packet to assign final labels only",
            "for rows where independent reviewers disagree. Paper-facing v0.3",
            "claims remain blocked until completed labels, agreement analysis,",
            "and any adjudication records have all passed validation.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--launch-packet", type=Path, default=Path("data/coverage_native_review_v03/coverage_native_review_packet_v03.csv"))
    parser.add_argument("--reviewer-roster", type=Path, default=Path("data/coverage_native_review_v03/coverage_native_review_roster_v03.csv"))
    parser.add_argument("--min-reviewers-per-item", type=int, default=2)
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/coverage_native_review_v03_adjudication"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/coverage_native_review_adjudication_v03.md"))
    args = parser.parse_args()

    summary, by_slice, by_content_language, by_instruction_language, adjudication = validate_long_reviews(
        annotation_rows=read_csv(args.annotations),
        launch_rows=read_csv(args.launch_packet),
        roster_rows=read_csv(args.reviewer_roster),
        min_reviewers_per_item=args.min_reviewers_per_item,
    )
    write_csv(args.out_dir / "coverage_native_review_interreviewer_summary.csv", [summary])
    write_csv(args.out_dir / "coverage_native_review_interreviewer_by_slice.csv", by_slice)
    write_csv(args.out_dir / "coverage_native_review_interreviewer_by_content_language.csv", by_content_language)
    write_csv(args.out_dir / "coverage_native_review_interreviewer_by_instruction_language.csv", by_instruction_language)
    write_csv(args.out_dir / "coverage_native_review_adjudication_packet.csv", adjudication)
    write_markdown(args.out_md, summary, len(adjudication))
    print(
        "coverage native-review adjudication analysis passed: "
        f"items={summary['review_items']}, "
        f"annotation_rows={summary['annotation_rows']}, "
        f"reviewers={summary['reviewers']}, "
        f"adjudication_rows={len(adjudication)}"
    )


if __name__ == "__main__":
    main()
