#!/usr/bin/env python
"""Validate sendable reviewer bundles for label collection."""

from __future__ import annotations

import argparse
import csv
import hashlib
import zipfile
from collections import Counter
from pathlib import Path


EXPECTED_COUNTS = {
    "human_audit_v02": 3,
    "current_model_human_audit_v02": 3,
    "coverage_native_review_v03": 6,
}
EXPECTED_ZIP_FILES = {
    "README.md",
    "review_instructions.md",
    "slice_packet.csv",
    "review_sheet.html",
}
PRIVATE_MARKERS = (
    "answer_key",
    "auto_pass",
    "auto_language_pass",
    "auto_script_pass",
    "auto_preservation_pass",
    "auto_task_pass",
    "auto_register_locale_pass",
    "auto_failure_types",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing bundle manifest {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_row_count(payload: str) -> int:
    rows = list(csv.DictReader(payload.splitlines()))
    return len(rows)


def check_bundle(row: dict[str, str]) -> None:
    bundle_path = Path(row["bundle_path"])
    require(bundle_path.exists(), f"missing reviewer bundle {bundle_path}")
    require(bundle_path.stat().st_size == int(row["bytes"]), f"bundle size mismatch for {bundle_path}")
    require(sha256_file(bundle_path) == row["sha256"], f"bundle sha256 mismatch for {bundle_path}")
    with zipfile.ZipFile(bundle_path) as zf:
        names = set(zf.namelist())
        require(names == EXPECTED_ZIP_FILES, f"{bundle_path} unexpected zip members: {sorted(names)}")
        for name in sorted(names):
            payload = zf.read(name).decode("utf-8")
            lowered = payload.lower()
            for marker in PRIVATE_MARKERS:
                require(marker not in lowered, f"{bundle_path}:{name} contains private marker {marker}")
        slice_packet = zf.read("slice_packet.csv").decode("utf-8")
        require(csv_row_count(slice_packet) == int(row["expected_rows"]), f"{bundle_path} row count mismatch")
        readme = zf.read("README.md").decode("utf-8")
        require(row["expected_export_name"] in readme, f"{bundle_path} README missing expected export filename")
        instructions = zf.read("review_instructions.md").decode("utf-8")
        require("Do not list" in instructions, f"{bundle_path} instructions missing reason-code guard")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing bundle report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    for phrase in (
        "Label Collection Reviewer Bundles",
        "sendable reviewer packages",
        "intentionally exclude",
        "answer keys",
        "automatic labels",
    ):
        require(phrase in normalized, f"bundle report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/label_collection_bundles_v02"))
    args = parser.parse_args()

    rows = read_csv(args.out_dir / "label_collection_bundle_manifest.csv")
    require(len(rows) == sum(EXPECTED_COUNTS.values()), f"unexpected bundle count: {len(rows)}")
    counts = Counter(row["surface_id"] for row in rows)
    require(counts == Counter(EXPECTED_COUNTS), f"unexpected bundles by surface: {counts}")
    for row in rows:
        check_bundle(row)
    check_report(args.out_dir / "label_collection_bundles.md")
    print(f"label-collection reviewer bundle validation passed for {args.out_dir}")


if __name__ == "__main__":
    main()
