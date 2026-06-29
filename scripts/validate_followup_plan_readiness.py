#!/usr/bin/env python
"""Validate the follow-up plan readiness audit."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


EXPECTED_STATUSES = {
    "current_model_refresh": "complete_paper_facing",
    "main_results_metrics": "complete_paper_facing",
    "family_level_failure_story": "complete_paper_facing",
    "language_slice_caveat": "complete_paper_facing",
    "token_burden_caveat": "complete_paper_facing",
    "prompt_mechanism": "complete_paper_facing",
    "repair_realism": "complete_supporting",
    "judge_refresh": "complete_supporting",
    "label_collection_operations": "complete_supporting",
    "original_human_audit_labels": "launch_ready_needs_labels",
    "current_model_human_audit_labels": "launch_ready_needs_labels",
    "v03_coverage_native_review": "launch_ready_needs_labels",
    "v03_coverage_model_smokes": "bounded_diagnostic_not_headline",
    "related_work_and_limitations": "complete_paper_facing",
    "artifact_manifest_claim_checklist": "complete_paper_facing",
    "collaborator_validated_language_pair": "not_started_requires_validator",
}

EXPECTED_STATUS_COUNTS = {
    "complete_paper_facing": 8,
    "complete_supporting": 3,
    "launch_ready_needs_labels": 3,
    "bounded_diagnostic_not_headline": 1,
    "not_started_requires_validator": 1,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing readiness CSV {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_csv(path: Path) -> None:
    rows = load_csv(path)
    require(len(rows) == len(EXPECTED_STATUSES), f"expected {len(EXPECTED_STATUSES)} readiness rows, found {len(rows)}")
    by_item = {row["plan_item"]: row for row in rows}
    require(set(by_item) == set(EXPECTED_STATUSES), f"unexpected readiness items: {sorted(by_item)}")
    for item, status in EXPECTED_STATUSES.items():
        row = by_item[item]
        require(row["status"] == status, f"status mismatch for {item}: expected {status}, got {row['status']}")
        require(row["evidence"], f"{item} missing evidence")
        require(row["validation_signal"], f"{item} missing validation signal")
        require(row["next_step"], f"{item} missing next step")
    counts = Counter(row["status"] for row in rows)
    require(dict(counts) == EXPECTED_STATUS_COUNTS, f"unexpected readiness status counts: {counts}")
    require(
        "98.3 FTGA" in by_item["current_model_refresh"]["validation_signal"],
        "current-model readiness row missing GPT-5.5 headline value",
    )
    require(
        "60 synthetic rows" in by_item["v03_coverage_native_review"]["validation_signal"],
        "v0.3 native-review row missing coverage-row count",
    )
    require(
        "collect qualified native/near-native labels" in by_item["original_human_audit_labels"]["next_step"],
        "human-audit row missing native-label next step",
    )
    require(
        "12 minimum single-label assignments" in by_item["label_collection_operations"]["validation_signal"],
        "label-collection operations row missing minimum assignment count",
    )
    require(
        "24 preferred double-label reviewer assignments" in by_item["label_collection_operations"]["validation_signal"],
        "label-collection operations row missing double-label assignment count",
    )


def check_markdown(path: Path) -> None:
    require(path.exists(), f"missing readiness report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "Follow-up Plan Readiness Audit",
        "complete_paper_facing | 8",
        "complete_supporting | 3",
        "launch_ready_needs_labels | 3",
        "Three launch-ready annotation surfaces remain incomplete",
        "original 72-row v0.2 human-audit packet",
        "48-row current-model human-audit packet",
        "60-row v0.3 native-review packet",
        "paper/label_collection_launch_pack_v02.md",
        "all reviewer-facing files, roster templates, finalization commands, and claim gates",
        "paper/label_collection_operator_handoff_v02.md",
        "reviewer1/reviewer2 double-label return filenames",
        "Do not claim native/near-native validation has been completed",
        "The v0.3 model-output smokes remain bounded diagnostics",
        "Current recommendation: submit with the GPT-5.5 current-model headline",
    ]
    for phrase in required:
        require(phrase in normalized, f"readiness report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=Path("results/tables/followup_plan_readiness_v02/followup_plan_readiness.csv"))
    parser.add_argument("--report", type=Path, default=Path("paper/followup_plan_readiness_v02.md"))
    args = parser.parse_args()

    check_csv(args.csv)
    check_markdown(args.report)
    print("follow-up plan readiness validation passed")


if __name__ == "__main__":
    main()
