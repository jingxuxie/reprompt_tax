#!/usr/bin/env python
"""Analyze double-annotation agreement and build human-audit adjudication packets."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

from summarize_human_audit import cohen_kappa
from validate_completed_human_audit import (
    BOOLEAN_FIELDS,
    DEFAULT_MODELS,
    PRIVATE_FIELDS,
    expected_row_count,
    parse_bool,
    parse_expected_models,
    parse_failure_types,
    read_csv,
    require,
    validate_roster,
)


COMPONENTS = [
    ("pass", "human_pass"),
    ("language", "human_language_pass"),
    ("script", "human_script_pass"),
    ("preservation", "human_preservation_pass"),
    ("task", "human_task_pass"),
    ("register_locale", "human_register_locale_pass"),
]

ADJUDICATION_FIELDS = [
    "adjudicator_id",
    "adjudicated_pass",
    "adjudicated_language_pass",
    "adjudicated_script_pass",
    "adjudicated_preservation_pass",
    "adjudicated_task_pass",
    "adjudicated_register_locale_pass",
    "adjudicated_failure_types",
    "adjudication_notes",
]

PUBLIC_CONTEXT_FIELDS = [
    "audit_id",
    "language_pair",
    "task_family",
    "user_prompt",
    "assistant_response",
    "expected_response_language",
    "expected_script",
    "must_preserve_spans",
    "register_requirement",
    "locale_requirement",
    "known_bad_outputs",
    "notes_for_annotators",
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


def normalized_failure_types(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(sorted(parse_failure_types(row.get("human_failure_types", ""), row_id=row["audit_id"])))


def parse_human_values(row: dict[str, str]) -> dict[str, bool]:
    row_id = row["audit_id"]
    values = {field: parse_bool(row.get(field), row_id=row_id, field=field) for field in BOOLEAN_FIELDS}
    expected_pass = all(values[field] for field in BOOLEAN_FIELDS if field != "human_pass")
    require(values["human_pass"] == expected_pass, f"{row_id} human_pass must equal conjunction of component labels")
    failure_types = parse_failure_types(row.get("human_failure_types", ""), row_id=row_id)
    if values["human_pass"]:
        require(not failure_types, f"{row_id} passes but lists human_failure_types")
    else:
        require(failure_types, f"{row_id} fails but has no human_failure_types")
        if "other" in failure_types:
            require(row.get("human_notes", "").strip(), f"{row_id} uses other without human_notes")
    return values


def validate_long_annotations(
    *,
    annotation_rows: list[dict[str, str]],
    key_rows: list[dict[str, str]],
    roster_rows: list[dict[str, str]],
    expected_models: tuple[str, ...] = DEFAULT_MODELS,
    min_annotators_per_item: int = 2,
    allow_smoke: bool = False,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    expected_items = expected_row_count(expected_models)
    require(len(key_rows) == expected_items, f"expected {expected_items} answer-key rows, found {len(key_rows)}")
    require(annotation_rows, "double-annotation file is empty")
    require(min_annotators_per_item >= 2, "min_annotators_per_item must be at least 2")
    require(not PRIVATE_FIELDS.intersection(annotation_rows[0].keys()), "double-annotation file leaks private answer-key fields")

    key_by_id = {row["audit_id"]: row for row in key_rows}
    require(len(key_by_id) == len(key_rows), "duplicate audit_id values in answer key")
    unknown = sorted({row["audit_id"] for row in annotation_rows} - set(key_by_id))
    require(not unknown, f"double annotations contain audit IDs not in answer key: {unknown[:5]}")

    roster_by_id = validate_roster(roster_rows)
    rows_by_audit: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen_pairs: set[tuple[str, str]] = set()
    annotator_ids: set[str] = set()
    parsed_by_pair: dict[tuple[str, str], dict[str, bool]] = {}

    for row in annotation_rows:
        row_id = row["audit_id"]
        key = key_by_id[row_id]
        for field in ("language_pair", "task_family"):
            require(row[field] == key[field], f"{row_id} packet/key mismatch for {field}")
        if not allow_smoke:
            require(not row.get("human_notes", "").startswith("SMOKE ONLY:"), f"{row_id} is marked smoke-only")
        annotator_id = row.get("annotator_id", "").strip()
        require(annotator_id, f"{row_id} missing annotator_id")
        require(annotator_id in roster_by_id, f"{row_id} annotator_id {annotator_id!r} is not in roster")
        require(
            roster_by_id[annotator_id]["language_pair"].strip() == row["language_pair"],
            f"{row_id} annotator {annotator_id} is not qualified for {row['language_pair']}",
        )
        pair_key = (row_id, annotator_id)
        require(pair_key not in seen_pairs, f"{row_id} has duplicate annotation from {annotator_id}")
        seen_pairs.add(pair_key)
        annotator_ids.add(annotator_id)
        parsed_by_pair[pair_key] = parse_human_values(row)
        rows_by_audit[row_id].append(row)

    missing = sorted(audit_id for audit_id in key_by_id if len(rows_by_audit[audit_id]) < min_annotators_per_item)
    require(
        not missing,
        f"{len(missing)} audit IDs have fewer than {min_annotators_per_item} annotations; first missing: {missing[:5]}",
    )

    strata = Counter((key["model"], key["condition"], key["task_family"], key["language_pair"]) for key in key_rows)
    expected_strata = {
        (model, condition, family, language_pair): 1
        for model in expected_models
        for condition in ("baseline", "contract")
        for family in ("editing_preservation", "output_language_inference", "quote_preservation", "script_register_locale")
        for language_pair in ("ar-en", "es-en", "hi-en")
    }
    require(dict(strata) == expected_strata, f"answer key strata not balanced for expected models {expected_models}: {strata}")

    item_rows = [
        {
            "audit_id": audit_id,
            **key_by_id[audit_id],
            "annotation_n": len(rows),
            "annotator_ids": ";".join(sorted(row["annotator_id"] for row in rows)),
        }
        for audit_id, rows in sorted(rows_by_audit.items())
    ]
    summary = summarize_items(item_rows, rows_by_audit, parsed_by_pair)
    by_language = [
        {"language_pair": language_pair, **summarize_items(group, rows_by_audit, parsed_by_pair)}
        for language_pair, group in grouped_items(item_rows, "language_pair").items()
    ]
    by_family = [
        {"task_family": family, **summarize_items(group, rows_by_audit, parsed_by_pair)}
        for family, group in grouped_items(item_rows, "task_family").items()
    ]
    summary.update(
        {
            "audit_items": expected_items,
            "annotation_rows": len(annotation_rows),
            "annotators": len(annotator_ids),
            "min_annotations_per_item": min(len(rows) for rows in rows_by_audit.values()),
            "max_annotations_per_item": max(len(rows) for rows in rows_by_audit.values()),
            "items_with_min_annotations": sum(
                len(rows_by_audit[audit_id]) >= min_annotators_per_item for audit_id in key_by_id
            ),
        }
    )
    adjudication = adjudication_rows(rows_by_audit, parsed_by_pair)
    return summary, by_language, by_family, adjudication


def grouped_items(item_rows: list[dict[str, Any]], field: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in item_rows:
        grouped[str(row[field])].append(row)
    return dict(sorted(grouped.items()))


def summarize_items(
    item_rows: list[dict[str, Any]],
    rows_by_audit: dict[str, list[dict[str, str]]],
    parsed_by_pair: dict[tuple[str, str], dict[str, bool]],
) -> dict[str, Any]:
    component_pairs: dict[str, list[tuple[bool, bool]]] = {name: [] for name, _ in COMPONENTS}
    pass_disagreement_items = 0
    component_disagreement_items = 0

    for item in item_rows:
        rows = rows_by_audit[item["audit_id"]]
        item_has_pass_disagreement = False
        item_has_component_disagreement = False
        for left, right in combinations(rows, 2):
            left_values = parsed_by_pair[(left["audit_id"], left["annotator_id"])]
            right_values = parsed_by_pair[(right["audit_id"], right["annotator_id"])]
            for name, field in COMPONENTS:
                pair = (left_values[field], right_values[field])
                component_pairs[name].append(pair)
                if pair[0] != pair[1]:
                    item_has_component_disagreement = True
                    if name == "pass":
                        item_has_pass_disagreement = True
        pass_disagreement_items += int(item_has_pass_disagreement)
        component_disagreement_items += int(item_has_component_disagreement)

    out: dict[str, Any] = {
        "items": len(item_rows),
        "items_with_pass_disagreement": pass_disagreement_items,
        "items_with_component_disagreement": component_disagreement_items,
    }
    for name, pairs in component_pairs.items():
        out[f"{name}_pair_count"] = len(pairs)
        out[f"{name}_pairwise_agreement"] = round(sum(a == b for a, b in pairs) / len(pairs), 4) if pairs else ""
        kappa = cohen_kappa(pairs)
        out[f"{name}_pairwise_kappa"] = round(kappa, 4) if isinstance(kappa, float) else kappa
    return out


def adjudication_rows(
    rows_by_audit: dict[str, list[dict[str, str]]],
    parsed_by_pair: dict[tuple[str, str], dict[str, bool]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for audit_id, rows in sorted(rows_by_audit.items()):
        disagreed_components: list[str] = []
        for name, field in COMPONENTS:
            values = {parsed_by_pair[(row["audit_id"], row["annotator_id"])][field] for row in rows}
            if len(values) > 1:
                disagreed_components.append(name)
        failure_type_values = {normalized_failure_types(row) for row in rows}
        if len(failure_type_values) > 1:
            disagreed_components.append("failure_types")
        if not disagreed_components:
            continue

        first = rows[0]
        base = {field: first.get(field, "") for field in PUBLIC_CONTEXT_FIELDS}
        base.update(
            {
                "annotator_ids": ";".join(row["annotator_id"] for row in rows),
                "disagreed_components": ";".join(disagreed_components),
            }
        )
        for _, field in COMPONENTS:
            base[f"{field}_by_annotator"] = ";".join(
                f"{row['annotator_id']}={bool_text(parsed_by_pair[(row['audit_id'], row['annotator_id'])][field])}"
                for row in rows
            )
        base["human_failure_types_by_annotator"] = ";".join(
            f"{row['annotator_id']}={row.get('human_failure_types', '')}" for row in rows
        )
        base["human_notes_by_annotator"] = ";".join(
            f"{row['annotator_id']}={row.get('human_notes', '')}" for row in rows
        )
        base.update({field: "" for field in ADJUDICATION_FIELDS})
        out.append(base)
    return out


def write_markdown(path: Path, summary: dict[str, Any], adjudication_count: int) -> None:
    lines = [
        "# Human Audit Inter-Annotator And Adjudication Analysis",
        "",
        "This report is generated after completed independent human-audit labels",
        "are available. It supports the stronger two-annotator-plus-adjudication",
        "workflow described in the follow-up plan; it is not a substitute for",
        "qualified native/near-native labels.",
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
            "for rows where independent annotators disagree. Keep final paper",
            "claims bounded until the completed-label validator, this agreement",
            "analysis, and any adjudication records have all been inspected.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--answer-key", type=Path, default=Path("data/human_audit/human_audit_answer_key_v0.2.csv"))
    parser.add_argument("--annotator-roster", type=Path, default=Path("data/human_audit/human_audit_annotator_roster_v0.2.csv"))
    parser.add_argument("--expected-models", default=",".join(DEFAULT_MODELS))
    parser.add_argument("--min-annotators-per-item", type=int, default=2)
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/human_audit_v0.2_adjudication"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/human_audit_adjudication_v02.md"))
    parser.add_argument("--allow-smoke", action="store_true", help="Allow smoke-only labels for plumbing tests, not claims.")
    args = parser.parse_args()

    summary, by_language, by_family, adjudication = validate_long_annotations(
        annotation_rows=read_csv(args.annotations),
        key_rows=read_csv(args.answer_key),
        roster_rows=read_csv(args.annotator_roster),
        expected_models=parse_expected_models(args.expected_models),
        min_annotators_per_item=args.min_annotators_per_item,
        allow_smoke=args.allow_smoke,
    )
    write_csv(args.out_dir / "human_audit_interannotator_summary.csv", [summary])
    write_csv(args.out_dir / "human_audit_interannotator_by_language.csv", by_language)
    write_csv(args.out_dir / "human_audit_interannotator_by_family.csv", by_family)
    write_csv(args.out_dir / "human_audit_adjudication_packet.csv", adjudication)
    write_markdown(args.out_md, summary, len(adjudication))
    print(
        "human-audit adjudication analysis passed: "
        f"items={summary['audit_items']}, "
        f"annotation_rows={summary['annotation_rows']}, "
        f"annotators={summary['annotators']}, "
        f"adjudication_rows={len(adjudication)}"
    )


if __name__ == "__main__":
    main()
