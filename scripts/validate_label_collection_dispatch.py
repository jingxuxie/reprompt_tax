#!/usr/bin/env python
"""Validate label-collection dispatch-readiness artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
from collections import Counter
from pathlib import Path


EXPECTED_SURFACES = {
    "current_model_human_audit_v02": {"bundles": 3, "rows": 48, "priority": "1"},
    "human_audit_v02": {"bundles": 3, "rows": 72, "priority": "2"},
    "coverage_native_review_v03": {"bundles": 6, "rows": 60, "priority": "3"},
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing dispatch table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_manifest(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == sum(item["bundles"] for item in EXPECTED_SURFACES.values()), f"unexpected dispatch row count: {len(rows)}")
    counts = Counter(row["surface_id"] for row in rows)
    require(counts == Counter({surface_id: spec["bundles"] for surface_id, spec in EXPECTED_SURFACES.items()}), f"unexpected dispatch surface counts: {counts}")
    total_rows = 0
    expected_return_paths: set[str] = set()
    bundle_paths: set[str] = set()
    for row in rows:
        spec = EXPECTED_SURFACES[row["surface_id"]]
        require(row["dispatch_priority"] == spec["priority"], f"{row['surface_id']} priority mismatch")
        require(row["ready_to_send"] == "True", f"{row['surface_id']}:{row['slice_id']} is not ready to send")
        require(row["launch_status"] == "launch_ready_needs_labels", f"{row['surface_id']} launch status mismatch")
        require(row["claim_gate_status"] == "needs_labels", f"{row['surface_id']} claim gate status mismatch")
        require(row["claim_decision"] == "no_claim", f"{row['surface_id']} claim decision must remain no_claim")
        require(row["expected_export_name"] in row["expected_return_path"], f"{row['surface_id']} expected return path mismatch")
        require(row["expected_return_path"].endswith("_completed.csv"), f"{row['surface_id']} return path must be completed CSV")
        expected_return_paths.add(row["expected_return_path"])
        bundle_paths.add(row["bundle_path"])
        bundle_path = Path(row["bundle_path"])
        require(bundle_path.exists(), f"missing dispatch bundle {bundle_path}")
        require(bundle_path.stat().st_size == int(row["bundle_bytes"]), f"{bundle_path} byte count mismatch")
        require(sha256_file(bundle_path) == row["bundle_sha256"], f"{bundle_path} sha256 mismatch")
        total_rows += int(row["expected_rows"])
    require(len(expected_return_paths) == len(rows), "duplicate expected return paths")
    require(len(bundle_paths) == len(rows), "duplicate bundle paths")
    require(total_rows == sum(item["rows"] for item in EXPECTED_SURFACES.values()), f"unexpected dispatch reviewer rows: {total_rows}")


def check_summary(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == len(EXPECTED_SURFACES), f"unexpected dispatch summary count: {len(rows)}")
    by_surface = {row["surface_id"]: row for row in rows}
    require(set(by_surface) == set(EXPECTED_SURFACES), f"unexpected dispatch summary surfaces: {sorted(by_surface)}")
    for surface_id, spec in EXPECTED_SURFACES.items():
        row = by_surface[surface_id]
        require(row["dispatch_priority"] == spec["priority"], f"{surface_id} priority mismatch")
        require(row["ready_bundles"] == str(spec["bundles"]), f"{surface_id} ready bundle mismatch")
        require(row["expected_bundles"] == str(spec["bundles"]), f"{surface_id} expected bundle mismatch")
        require(row["reviewer_facing_rows"] == str(spec["rows"]), f"{surface_id} reviewer row mismatch")
        require(row["expected_rows"] == str(spec["rows"]), f"{surface_id} expected row mismatch")
        require(row["claim_gate_status"] == "needs_labels", f"{surface_id} should still need labels")
        require(row["claim_decision"] == "no_claim", f"{surface_id} should not unlock a claim")
        require("completed inputs" in row["claim_required_action"], f"{surface_id} missing completed-input blocker")
        require(row["next_action"], f"{surface_id} missing next action")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing dispatch report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "Label Collection Dispatch Readiness",
        "dispatch manifest, not completed human/native validation",
        "Ready reviewer bundles: 12 / 12",
        "Reviewer-facing rows across ready bundles: 180",
        "Claim gate status: no completed human/native validation claim is unlocked",
        "do not send answer keys, automatic labels, model names",
        "current_model_human_audit_v02",
        "human_audit_v02",
        "coverage_native_review_v03",
        "scripts/analyze_completed_label_claim_gates.py",
    ]
    for phrase in required:
        require(phrase in normalized, f"dispatch report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/label_collection_dispatch_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/label_collection_dispatch_v02.md"))
    args = parser.parse_args()

    check_manifest(args.out_dir / "label_collection_dispatch_manifest.csv")
    check_summary(args.out_dir / "label_collection_dispatch_summary.csv")
    check_report(args.report)
    print("label-collection dispatch validation passed")


if __name__ == "__main__":
    main()
