#!/usr/bin/env python
"""Evaluate whether completed human/native labels unlock stronger claims."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

from validate_completed_coverage_native_review_v03 import (
    read_csv as read_coverage_csv,
    validate_completed_reviews,
)
from validate_completed_human_audit import (
    parse_expected_models,
    read_csv as read_human_csv,
    validate_annotations,
)


OUT_DIR = Path("results/tables/completed_label_claim_gates_v02")
OUT_MD = Path("paper/completed_label_claim_gates_v02.md")

HUMAN_COMPONENT_PAIRS_PER_ROW = 5

SURFACES = [
    {
        "surface": "human_audit_v02_gpt41_family",
        "review_type": "human_audit",
        "annotations": Path("data/human_audit/human_audit_packet_v0.2_completed.csv"),
        "answer_key": Path("data/human_audit/human_audit_answer_key_v0.2.csv"),
        "roster": Path("data/human_audit/human_audit_annotator_roster_v0.2.csv"),
        "expected_models": "gpt-4.1,gpt-4.1-mini,gpt-4.1-nano",
        "expected_rows": 72,
        "min_reviewers": 3,
        "min_pass_agreements": 65,
        "min_component_agreements": 306,
        "claim_if_ready": "native/near-native audit supports the automatic scorer on sampled first-turn labels",
    },
    {
        "surface": "human_audit_v02_current_gpt5",
        "review_type": "human_audit",
        "annotations": Path("data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_completed.csv"),
        "answer_key": Path("data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv"),
        "roster": Path("data/current_model_human_audit/human_audit_annotator_roster_v0.2_current_gpt5.csv"),
        "expected_models": "gpt-5.4-mini,gpt-5.5",
        "expected_rows": 48,
        "min_reviewers": 3,
        "min_pass_agreements": 44,
        "min_component_agreements": 204,
        "claim_if_ready": "native/near-native audit supports the automatic scorer on sampled current-model labels",
    },
    {
        "surface": "coverage_native_review_v03",
        "review_type": "coverage_native_review",
        "annotations": Path("data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv"),
        "launch_packet": Path("data/coverage_native_review_v03/coverage_native_review_packet_v03.csv"),
        "roster": Path("data/coverage_native_review_v03/coverage_native_review_roster_v03.csv"),
        "expected_rows": 60,
        "min_reviewers": 6,
        "min_release_usable_rows": 60,
        "claim_if_ready": "v0.3 scaffold rows are native-review release usable; model performance still needs a pre-specified run",
    },
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, "claim-gate table cannot be empty")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "t", "yes", "y", "pass", "passed"}


def completed_inputs_missing(surface: dict[str, Any]) -> list[str]:
    paths = [surface["annotations"], surface["roster"]]
    if surface["review_type"] == "human_audit":
        paths.append(surface["answer_key"])
    else:
        paths.append(surface["launch_packet"])
    return [str(path) for path in paths if not Path(path).exists()]


def human_agreement_counts(annotation_rows: list[dict[str, str]], key_rows: list[dict[str, str]]) -> tuple[int, int]:
    key_by_id = {row["audit_id"]: row for row in key_rows}
    pass_agree = 0
    component_agree = 0
    component_fields = (
        ("human_language_pass", "auto_language_pass"),
        ("human_script_pass", "auto_script_pass"),
        ("human_preservation_pass", "auto_preservation_pass"),
        ("human_task_pass", "auto_task_pass"),
        ("human_register_locale_pass", "auto_register_locale_pass"),
    )
    for row in annotation_rows:
        key = key_by_id[row["audit_id"]]
        pass_agree += int(parse_bool(row["human_pass"]) == parse_bool(key["auto_pass"]))
        for human_field, auto_field in component_fields:
            component_agree += int(parse_bool(row[human_field]) == parse_bool(key[auto_field]))
    return pass_agree, component_agree


def no_claim_row(surface: dict[str, Any], *, status: str, reason: str) -> dict[str, Any]:
    return {
        "surface": surface["surface"],
        "review_type": surface["review_type"],
        "status": status,
        "claim_decision": "no_claim",
        "rows": "",
        "reviewers": "",
        "pass_agreements": "",
        "min_pass_agreements": surface.get("min_pass_agreements", ""),
        "component_agreements": "",
        "min_component_agreements": surface.get("min_component_agreements", ""),
        "release_usable_rows": "",
        "min_release_usable_rows": surface.get("min_release_usable_rows", ""),
        "required_action": reason,
    }


def evaluate_human_surface(surface: dict[str, Any]) -> dict[str, Any]:
    missing = completed_inputs_missing(surface)
    if missing:
        return no_claim_row(surface, status="needs_labels", reason="missing completed inputs: " + "; ".join(missing))
    try:
        annotation_rows = read_human_csv(surface["annotations"])
        key_rows = read_human_csv(surface["answer_key"])
        roster_rows = read_human_csv(surface["roster"])
        summary = validate_annotations(
            annotation_rows=annotation_rows,
            key_rows=key_rows,
            roster_rows=roster_rows,
            allow_smoke=False,
            expected_models=parse_expected_models(surface["expected_models"]),
        )
        pass_agree, component_agree = human_agreement_counts(annotation_rows, key_rows)
        claim_ready = (
            summary["rows"] == surface["expected_rows"]
            and summary["annotators"] >= surface["min_reviewers"]
            and pass_agree >= surface["min_pass_agreements"]
            and component_agree >= surface["min_component_agreements"]
        )
        missing_bits: list[str] = []
        if summary["annotators"] < surface["min_reviewers"]:
            missing_bits.append("reviewer minimum not met")
        if pass_agree < surface["min_pass_agreements"]:
            missing_bits.append("pass-agreement threshold not met")
        if component_agree < surface["min_component_agreements"]:
            missing_bits.append("component-agreement threshold not met")
        return {
            "surface": surface["surface"],
            "review_type": surface["review_type"],
            "status": "claim_ready" if claim_ready else "claim_blocked",
            "claim_decision": "claim_ready" if claim_ready else "keep_conservative_boundary",
            "rows": summary["rows"],
            "reviewers": summary["annotators"],
            "pass_agreements": pass_agree,
            "min_pass_agreements": surface["min_pass_agreements"],
            "component_agreements": component_agree,
            "min_component_agreements": surface["min_component_agreements"],
            "release_usable_rows": "",
            "min_release_usable_rows": "",
            "required_action": surface["claim_if_ready"] if claim_ready else "; ".join(missing_bits),
        }
    except Exception as exc:  # keep invalid completed labels from crashing the planning gate
        return no_claim_row(surface, status="invalid_labels", reason=str(exc))


def evaluate_coverage_surface(surface: dict[str, Any]) -> dict[str, Any]:
    missing = completed_inputs_missing(surface)
    if missing:
        return no_claim_row(surface, status="needs_labels", reason="missing completed inputs: " + "; ".join(missing))
    try:
        summary = validate_completed_reviews(
            annotation_rows=read_coverage_csv(surface["annotations"]),
            launch_rows=read_coverage_csv(surface["launch_packet"]),
            roster_rows=read_coverage_csv(surface["roster"]),
        )
        claim_ready = (
            summary["rows"] == surface["expected_rows"]
            and summary["reviewers"] >= surface["min_reviewers"]
            and summary["release_usable"] >= surface["min_release_usable_rows"]
            and summary["issue_rows"] == 0
        )
        missing_bits: list[str] = []
        if summary["reviewers"] < surface["min_reviewers"]:
            missing_bits.append("reviewer minimum not met")
        if summary["release_usable"] < surface["min_release_usable_rows"]:
            missing_bits.append("not all rows are release usable")
        if summary["issue_rows"]:
            missing_bits.append("unresolved issue rows remain")
        return {
            "surface": surface["surface"],
            "review_type": surface["review_type"],
            "status": "claim_ready" if claim_ready else "claim_blocked",
            "claim_decision": "claim_ready" if claim_ready else "keep_conservative_boundary",
            "rows": summary["rows"],
            "reviewers": summary["reviewers"],
            "pass_agreements": "",
            "min_pass_agreements": "",
            "component_agreements": "",
            "min_component_agreements": "",
            "release_usable_rows": summary["release_usable"],
            "min_release_usable_rows": surface["min_release_usable_rows"],
            "required_action": surface["claim_if_ready"] if claim_ready else "; ".join(missing_bits),
        }
    except Exception as exc:
        return no_claim_row(surface, status="invalid_labels", reason=str(exc))


def evaluate_surfaces() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for surface in SURFACES:
        if surface["review_type"] == "human_audit":
            rows.append(evaluate_human_surface(surface))
        else:
            rows.append(evaluate_coverage_surface(surface))
    return rows


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    ready = [row for row in rows if row["status"] == "claim_ready"]
    lines = [
        "# Completed Label Claim Gates",
        "",
        "This report evaluates whether completed qualified human/native labels",
        "unlock stronger paper claims. Missing labels keep the current conservative",
        "automatic-plus-LLM-judge claim boundary.",
        "",
        f"Claim-ready surfaces: {len(ready)} / {len(rows)}",
        "",
        "| Surface | Status | Decision | Rows | Reviewers | Required action |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['surface']} | {row['status']} | {row['claim_decision']} | "
            f"{row['rows']} | {row['reviewers']} | {row['required_action']} |"
        )
    if not ready:
        lines.extend(
            [
                "",
                "No completed human/native validation claim is unlocked in the current repo.",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    rows = evaluate_surfaces()
    write_csv(args.out_dir / "completed_label_claim_gates.csv", rows)
    write_markdown(args.out_md, rows)
    print(f"wrote completed-label claim gates to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
