#!/usr/bin/env python
"""Validate completed-label claim-gate report."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_SURFACES = {
    "human_audit_v02_gpt41_family",
    "human_audit_v02_current_gpt5",
    "coverage_native_review_v03",
}
ALLOWED_STATUSES = {"needs_labels", "invalid_labels", "claim_blocked", "claim_ready"}
ALLOWED_DECISIONS = {"no_claim", "keep_conservative_boundary", "claim_ready"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing claim-gate table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_table(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == len(EXPECTED_SURFACES), f"expected {len(EXPECTED_SURFACES)} claim-gate rows, found {len(rows)}")
    surfaces = {row["surface"] for row in rows}
    require(surfaces == EXPECTED_SURFACES, f"unexpected claim-gate surfaces: {sorted(surfaces)}")
    for row in rows:
        require(row["status"] in ALLOWED_STATUSES, f"{row['surface']} has invalid status {row['status']}")
        require(row["claim_decision"] in ALLOWED_DECISIONS, f"{row['surface']} has invalid decision {row['claim_decision']}")
        require(row["required_action"], f"{row['surface']} missing required_action")
        if row["status"] == "claim_ready":
            require(row["claim_decision"] == "claim_ready", f"{row['surface']} ready status must unlock claim_ready decision")
        if row["status"] in {"needs_labels", "invalid_labels"}:
            require(row["claim_decision"] == "no_claim", f"{row['surface']} missing/invalid labels must not unlock claims")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing claim-gate report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    for phrase in (
        "Completed Label Claim Gates",
        "completed qualified human/native labels",
        "automatic-plus-LLM-judge claim boundary",
        "Claim-ready surfaces:",
    ):
        require(phrase in normalized, f"claim-gate report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--table", type=Path, default=Path("results/tables/completed_label_claim_gates_v02/completed_label_claim_gates.csv"))
    parser.add_argument("--report", type=Path, default=Path("paper/completed_label_claim_gates_v02.md"))
    args = parser.parse_args()

    check_table(args.table)
    check_report(args.report)
    print("completed-label claim-gate validation passed")


if __name__ == "__main__":
    main()
