#!/usr/bin/env python
"""Rank incomplete label-collection surfaces by claim payoff and burden."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Any


OUT_DIR = Path("results/tables/label_collection_priority_v02")
OUT_MD = Path("paper/label_collection_priority_v02.md")

LAUNCH_SURFACES = Path("results/tables/label_collection_launch_pack_v02/label_collection_surfaces.csv")
BUNDLE_MANIFEST = Path("results/label_collection_bundles_v02/label_collection_bundle_manifest.csv")
ACCEPTANCE_RULES = Path("results/tables/human_audit_acceptance_rules_v02/human_audit_acceptance_rules.csv")
CLAIM_GATES = Path("results/tables/completed_label_claim_gates_v02/completed_label_claim_gates.csv")


CLAIM_GATE_BY_SURFACE = {
    "current_model_human_audit_v02": "human_audit_v02_current_gpt5",
    "human_audit_v02": "human_audit_v02_gpt41_family",
    "coverage_native_review_v03": "coverage_native_review_v03",
}

PRIORITY = {
    "current_model_human_audit_v02": {
        "priority_rank": 1,
        "collection_phase": "collect_first",
        "direct_paper_payoff": "native/near-native validation for the GPT-5.x current-model headline",
        "recommended_next_action": "send three 16-row current-model language bundles and collect a qualified roster",
        "rationale": "smallest human-audit surface and directly tied to the strongest GPT-5.5 result",
    },
    "human_audit_v02": {
        "priority_rank": 2,
        "collection_phase": "collect_second",
        "direct_paper_payoff": "native/near-native validation for the original v0.2 automatic-scorer story",
        "recommended_next_action": "send three 24-row original v0.2 language bundles after current-model labels are underway",
        "rationale": "broader historical model-family validation, but more rows than the current-model audit",
    },
    "coverage_native_review_v03": {
        "priority_rank": 3,
        "collection_phase": "collect_after_human_audits_or_with_extra_reviewers",
        "direct_paper_payoff": "native review of the v0.3 coverage scaffold before any v0.3 benchmark-evidence claim",
        "recommended_next_action": "send six 10-row coverage-slice bundles only when qualified reviewers cover all slices",
        "rationale": "validates benchmark expansion, but does not by itself unlock a model-performance result",
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing label-priority input {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, f"refusing to write empty priority table {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def by_key(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    keyed = {row[key]: row for row in rows}
    require(len(keyed) == len(rows), f"duplicate {key} values")
    return keyed


def threshold_summary(rule: dict[str, str]) -> str:
    rows = int(rule["expected_rows"])
    if rule["review_type"] == "native_review_scaffold_release":
        return f"{rule['min_release_usable_rows']}/{rows} release-usable rows"
    return f"{rule['min_pass_agreements']}/{rows} pass agreements; {rule['min_component_agreements']}/{rows * 5} component agreements"


def build_priority_rows(
    *,
    launch_by_surface: dict[str, dict[str, str]],
    bundles_by_surface: dict[str, list[dict[str, str]]],
    rules_by_claim: dict[str, dict[str, str]],
    gates_by_claim: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for surface_id, meta in sorted(PRIORITY.items(), key=lambda item: item[1]["priority_rank"]):
        require(surface_id in launch_by_surface, f"missing launch row for {surface_id}")
        claim_surface = CLAIM_GATE_BY_SURFACE[surface_id]
        require(claim_surface in rules_by_claim, f"missing acceptance rule for {claim_surface}")
        require(claim_surface in gates_by_claim, f"missing claim gate for {claim_surface}")
        launch = launch_by_surface[surface_id]
        rule = rules_by_claim[claim_surface]
        gate = gates_by_claim[claim_surface]
        bundles = bundles_by_surface[surface_id]
        reviewer_rows = sum(int(row["expected_rows"]) for row in bundles)
        packet_rows = int(launch["packet_rows"])
        require(packet_rows == int(rule["expected_rows"]), f"{surface_id} row count mismatch between launch pack and rules")
        require(reviewer_rows == packet_rows, f"{surface_id} bundle rows do not cover packet rows")
        rows.append(
            {
                "priority_rank": meta["priority_rank"],
                "surface_id": surface_id,
                "claim_gate_surface": claim_surface,
                "collection_phase": meta["collection_phase"],
                "packet_rows": packet_rows,
                "reviewer_bundle_count": len(bundles),
                "reviewer_facing_rows": reviewer_rows,
                "qualified_reviewer_slots": int(launch["roster_template_slots"]),
                "preferred_independent_labels_per_item": int(launch["preferred_independent_labels_per_item"]),
                "minimum_single_label_exports": len(bundles),
                "stronger_double_label_rows": packet_rows * 2,
                "completion_threshold": threshold_summary(rule),
                "claim_gate_status": gate["status"],
                "claim_decision": gate["claim_decision"],
                "direct_paper_payoff": meta["direct_paper_payoff"],
                "recommended_next_action": meta["recommended_next_action"],
                "rationale": meta["rationale"],
                "claim_boundary": "no_completed_human_or_native_validation_claim_until_finalized_labels_pass_gates",
            }
        )
    return rows


def build_slice_rows(
    *,
    priority_rows: list[dict[str, Any]],
    bundles_by_surface: dict[str, list[dict[str, str]]],
) -> list[dict[str, Any]]:
    priority_by_surface = {row["surface_id"]: row for row in priority_rows}
    rows: list[dict[str, Any]] = []
    for surface_id, priority in sorted(priority_by_surface.items(), key=lambda item: int(item[1]["priority_rank"])):
        for bundle in sorted(bundles_by_surface[surface_id], key=lambda row: row["slice_id"]):
            bundle_path = Path(bundle["bundle_path"])
            rows.append(
                {
                    "priority_rank": priority["priority_rank"],
                    "surface_id": surface_id,
                    "slice_id": bundle["slice_id"],
                    "title": bundle["title"],
                    "expected_rows": int(bundle["expected_rows"]),
                    "expected_export_name": bundle["expected_export_name"],
                    "bundle_path": bundle["bundle_path"],
                    "bundle_ready": bundle_path.exists(),
                    "collection_phase": priority["collection_phase"],
                }
            )
    return rows


def write_markdown(path: Path, priority_rows: list[dict[str, Any]], slice_rows: list[dict[str, Any]]) -> None:
    total_rows = sum(int(row["packet_rows"]) for row in priority_rows)
    total_bundles = sum(int(row["reviewer_bundle_count"]) for row in priority_rows)
    first = priority_rows[0]
    lines = [
        "# Label Collection Priority Audit",
        "",
        "This no-API audit ranks the incomplete human/native label surfaces by",
        "claim payoff and collection burden. It is a collection plan, not completed",
        "human/native validation.",
        "",
        "## Recommendation",
        "",
        f"Prioritize `{first['surface_id']}` first: it has {first['packet_rows']} rows",
        "across three 16-row language bundles and is the smallest label surface that",
        "can directly support the GPT-5.x current-model headline if its completed",
        "labels pass the pre-specified gates.",
        "",
        "Collect `human_audit_v02` second to validate the original v0.2 scorer story.",
        "Collect `coverage_native_review_v03` after the human audits, or in parallel",
        "only if qualified reviewers are available for all six coverage slices; it",
        "checks scaffold release usability but still does not create a v0.3 model",
        "performance claim by itself.",
        "",
        "## Summary",
        "",
        f"- Incomplete label surfaces: {len(priority_rows)}",
        f"- Reviewer-facing rows: {total_rows}",
        f"- Ready reviewer bundles: {total_bundles}",
        "- Minimum completion path: one qualified completed export per slice plus",
        "  the matching filled roster, followed by the completed-label validator.",
        "- Stronger path: two independent labels per item, adjudicate only",
        "  disagreements, finalize one row per item, then rerun claim gates.",
        "- Claim boundary: no completed human/native-validation claim is unlocked",
        "  until finalized labels pass validators and thresholds.",
        "",
        "## Priority Table",
        "",
        "| Rank | Surface | Rows | Bundles | Threshold | Claim payoff | Next action |",
        "|---:|---|---:|---:|---|---|---|",
    ]
    for row in priority_rows:
        lines.append(
            f"| {row['priority_rank']} | {row['surface_id']} | {row['packet_rows']} | "
            f"{row['reviewer_bundle_count']} | {row['completion_threshold']} | "
            f"{row['direct_paper_payoff']} | {row['recommended_next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Slice Checklist",
            "",
            "| Rank | Surface | Slice | Rows | Expected return file | Bundle ready |",
            "|---:|---|---|---:|---|---|",
        ]
    )
    for row in slice_rows:
        lines.append(
            f"| {row['priority_rank']} | {row['surface_id']} | {row['slice_id']} | "
            f"{row['expected_rows']} | `{row['expected_export_name']}` | {row['bundle_ready']} |"
        )
    lines.extend(
        [
            "",
            "After any completed labels arrive, merge exports with",
            "`scripts/merge_review_exports.py`, validate the finalized labels, summarize",
            "them, then rerun `scripts/analyze_completed_label_claim_gates.py` and",
            "`scripts/validate_completed_label_claim_gates.py` before changing paper",
            "claims.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--launch-surfaces", type=Path, default=LAUNCH_SURFACES)
    parser.add_argument("--bundle-manifest", type=Path, default=BUNDLE_MANIFEST)
    parser.add_argument("--acceptance-rules", type=Path, default=ACCEPTANCE_RULES)
    parser.add_argument("--claim-gates", type=Path, default=CLAIM_GATES)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    launch_by_surface = by_key(read_csv(args.launch_surfaces), "surface_id")
    rules_by_claim = by_key(read_csv(args.acceptance_rules), "surface")
    gates_by_claim = by_key(read_csv(args.claim_gates), "surface")
    bundles_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(args.bundle_manifest):
        bundles_by_surface[row["surface_id"]].append(row)

    require(set(bundles_by_surface) == set(PRIORITY), f"unexpected bundle surfaces: {sorted(bundles_by_surface)}")
    priority_rows = build_priority_rows(
        launch_by_surface=launch_by_surface,
        bundles_by_surface=bundles_by_surface,
        rules_by_claim=rules_by_claim,
        gates_by_claim=gates_by_claim,
    )
    slice_rows = build_slice_rows(priority_rows=priority_rows, bundles_by_surface=bundles_by_surface)
    write_csv(args.out_dir / "label_collection_priority.csv", priority_rows)
    write_csv(args.out_dir / "label_collection_priority_by_slice.csv", slice_rows)
    write_markdown(args.out_md, priority_rows, slice_rows)
    print(f"wrote label-collection priority audit to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
