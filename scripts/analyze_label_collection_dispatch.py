#!/usr/bin/env python
"""Build a dispatch-readiness audit for sendable label-collection bundles."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
from typing import Any


OUT_DIR = Path("results/tables/label_collection_dispatch_v02")
OUT_MD = Path("paper/label_collection_dispatch_v02.md")

BUNDLE_MANIFEST = Path("results/label_collection_bundles_v02/label_collection_bundle_manifest.csv")
LAUNCH_SURFACES = Path("results/tables/label_collection_launch_pack_v02/label_collection_surfaces.csv")
CLAIM_GATES = Path("results/tables/completed_label_claim_gates_v02/completed_label_claim_gates.csv")

EXPECTED_SURFACE_COUNTS = {
    "current_model_human_audit_v02": {"bundles": 3, "rows": 48, "priority": 1},
    "human_audit_v02": {"bundles": 3, "rows": 72, "priority": 2},
    "coverage_native_review_v03": {"bundles": 6, "rows": 60, "priority": 3},
}

CLAIM_GATE_BY_SURFACE = {
    "current_model_human_audit_v02": "human_audit_v02_current_gpt5",
    "human_audit_v02": "human_audit_v02_gpt41_family",
    "coverage_native_review_v03": "coverage_native_review_v03",
}

RETURN_DIR_BY_SURFACE = {
    "current_model_human_audit_v02": Path("data/current_model_human_audit"),
    "human_audit_v02": Path("data/human_audit"),
    "coverage_native_review_v03": Path("data/coverage_native_review_v03"),
}

NEXT_ACTION_BY_SURFACE = {
    "current_model_human_audit_v02": "send three 16-row current-model slices and collect completed CSV exports plus qualified roster",
    "human_audit_v02": "send three 24-row original v0.2 slices and collect completed CSV exports plus qualified roster",
    "coverage_native_review_v03": "send six 10-row v0.3 coverage-review slices after reviewer availability is confirmed",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing dispatch input {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, f"refusing to write empty dispatch table {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_by_key(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    by_key = {row[key]: row for row in rows}
    require(len(by_key) == len(rows), f"duplicate {key} values")
    return by_key


def build_dispatch_rows(
    *,
    bundle_rows: list[dict[str, str]],
    launch_by_surface: dict[str, dict[str, str]],
    claim_by_surface: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in sorted(
        bundle_rows,
        key=lambda item: (EXPECTED_SURFACE_COUNTS[item["surface_id"]]["priority"], item["slice_id"]),
    ):
        surface_id = row["surface_id"]
        require(surface_id in EXPECTED_SURFACE_COUNTS, f"unexpected bundle surface {surface_id}")
        require(surface_id in launch_by_surface, f"{surface_id} missing launch-surface row")
        claim_surface = CLAIM_GATE_BY_SURFACE[surface_id]
        require(claim_surface in claim_by_surface, f"{surface_id} missing claim-gate row")

        bundle_path = Path(row["bundle_path"])
        require(bundle_path.exists(), f"missing reviewer bundle {bundle_path}")
        require(bundle_path.stat().st_size == int(row["bytes"]), f"bundle byte count mismatch: {bundle_path}")
        require(sha256_file(bundle_path) == row["sha256"], f"bundle sha256 mismatch: {bundle_path}")

        launch = launch_by_surface[surface_id]
        claim = claim_by_surface[claim_surface]
        return_path = RETURN_DIR_BY_SURFACE[surface_id] / row["expected_export_name"]
        ready = (
            launch["status"] == "launch_ready_needs_labels"
            and claim["claim_decision"] == "no_claim"
            and claim["status"] == "needs_labels"
        )
        rows.append(
            {
                "dispatch_priority": EXPECTED_SURFACE_COUNTS[surface_id]["priority"],
                "surface_id": surface_id,
                "slice_id": row["slice_id"],
                "mode": row["mode"],
                "title": row["title"],
                "expected_rows": row["expected_rows"],
                "bundle_path": row["bundle_path"],
                "bundle_bytes": row["bytes"],
                "bundle_sha256": row["sha256"],
                "expected_return_path": str(return_path),
                "expected_export_name": row["expected_export_name"],
                "launch_status": launch["status"],
                "claim_gate_surface": claim_surface,
                "claim_gate_status": claim["status"],
                "claim_decision": claim["claim_decision"],
                "ready_to_send": ready,
                "next_action": NEXT_ACTION_BY_SURFACE[surface_id],
            }
        )
    return rows


def build_summary_rows(dispatch_rows: list[dict[str, Any]], claim_by_surface: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for surface_id, expected in sorted(EXPECTED_SURFACE_COUNTS.items(), key=lambda item: item[1]["priority"]):
        surface_rows = [row for row in dispatch_rows if row["surface_id"] == surface_id]
        claim = claim_by_surface[CLAIM_GATE_BY_SURFACE[surface_id]]
        rows.append(
            {
                "dispatch_priority": expected["priority"],
                "surface_id": surface_id,
                "ready_bundles": sum(1 for row in surface_rows if row["ready_to_send"]),
                "expected_bundles": expected["bundles"],
                "reviewer_facing_rows": sum(int(row["expected_rows"]) for row in surface_rows),
                "expected_rows": expected["rows"],
                "total_bundle_bytes": sum(int(row["bundle_bytes"]) for row in surface_rows),
                "claim_gate_status": claim["status"],
                "claim_decision": claim["claim_decision"],
                "claim_required_action": claim["required_action"],
                "next_action": NEXT_ACTION_BY_SURFACE[surface_id],
            }
        )
    return rows


def write_markdown(path: Path, summary_rows: list[dict[str, Any]], dispatch_rows: list[dict[str, Any]]) -> None:
    total_bundles = len(dispatch_rows)
    total_ready = sum(1 for row in dispatch_rows if row["ready_to_send"])
    total_rows = sum(int(row["expected_rows"]) for row in dispatch_rows)
    total_bytes = sum(int(row["bundle_bytes"]) for row in dispatch_rows)
    lines = [
        "# Label Collection Dispatch Readiness",
        "",
        "This report audits the exact reviewer zip files that are safe to send",
        "for the remaining human/native-label collection. It is a dispatch",
        "manifest, not completed human/native validation.",
        "",
        "## Summary",
        "",
        f"- Ready reviewer bundles: {total_ready} / {total_bundles}",
        f"- Reviewer-facing rows across ready bundles: {total_rows}",
        f"- Total zip payload bytes: {total_bytes}",
        "- Claim gate status: no completed human/native validation claim is unlocked.",
        "- Send only these zip files or their contained blinded `slice_packet.csv` and",
        "  `review_sheet.html`; do not send answer keys, automatic labels, model names,",
        "  or prompt conditions.",
        "",
        "## Dispatch Priority",
        "",
        "| Priority | Surface | Ready bundles | Rows | Claim gate | Next action |",
        "|---:|---|---:|---:|---|---|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['dispatch_priority']} | {row['surface_id']} | "
            f"{row['ready_bundles']}/{row['expected_bundles']} | "
            f"{row['reviewer_facing_rows']} | {row['claim_gate_status']} / {row['claim_decision']} | "
            f"{row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Bundle Manifest",
            "",
            "| Surface | Slice | Rows | Expected return file | Bundle | SHA-256 |",
            "|---|---|---:|---|---|---|",
        ]
    )
    for row in dispatch_rows:
        lines.append(
            f"| {row['surface_id']} | {row['slice_id']} | {row['expected_rows']} | "
            f"`{row['expected_return_path']}` | `{row['bundle_path']}` | `{row['bundle_sha256']}` |"
        )
    lines.extend(
        [
            "",
            "After completed CSV exports and qualified rosters are returned, merge",
            "the slice exports with `scripts/merge_review_exports.py`, run the",
            "surface-specific completed-label validator, summarize labels, then rerun",
            "`scripts/analyze_completed_label_claim_gates.py` before changing any",
            "paper claim.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-manifest", type=Path, default=BUNDLE_MANIFEST)
    parser.add_argument("--launch-surfaces", type=Path, default=LAUNCH_SURFACES)
    parser.add_argument("--claim-gates", type=Path, default=CLAIM_GATES)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    bundle_rows = read_csv(args.bundle_manifest)
    launch_rows = read_csv(args.launch_surfaces)
    claim_rows = read_csv(args.claim_gates)
    launch_by_surface = load_by_key(launch_rows, "surface_id")
    claim_by_surface = load_by_key(claim_rows, "surface")

    dispatch_rows = build_dispatch_rows(
        bundle_rows=bundle_rows,
        launch_by_surface=launch_by_surface,
        claim_by_surface=claim_by_surface,
    )
    summary_rows = build_summary_rows(dispatch_rows, claim_by_surface)
    write_csv(args.out_dir / "label_collection_dispatch_manifest.csv", dispatch_rows)
    write_csv(args.out_dir / "label_collection_dispatch_summary.csv", summary_rows)
    write_markdown(args.out_md, summary_rows, dispatch_rows)
    print(f"wrote label-collection dispatch readiness to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
