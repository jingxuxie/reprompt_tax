#!/usr/bin/env python
"""Validate the submission anonymity audit artifact."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXPECTED_CHECKS = {
    "tracked_text_identity_scan",
    "tracked_tex_intermediates",
    "main_tex_anonymous_author",
    "pdf_author_metadata",
    "pdf_page_count",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing anonymity audit table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    require(rows, f"empty anonymity audit table {path}")
    return rows


def check_tables(out_dir: Path) -> None:
    checks = read_csv(out_dir / "submission_anonymity_checks.csv")
    by_id = {row["check_id"]: row for row in checks}
    require(set(by_id) == EXPECTED_CHECKS, f"unexpected anonymity checks: {sorted(by_id)}")
    for check_id, row in by_id.items():
        require(row["status"] == "pass", f"{check_id} did not pass: {row}")
        require(row["signal"], f"{check_id} missing signal")
        require(row["scope"], f"{check_id} missing scope")
    require("0 forbidden identity/path/API-secret text matches" in by_id["tracked_text_identity_scan"]["signal"], "identity scan should have zero findings")
    require("0 tracked TeX intermediary files" in by_id["tracked_tex_intermediates"]["signal"], "TeX intermediary check should be zero")
    require("anonymous COLM submission author block" in by_id["main_tex_anonymous_author"]["signal"], "main.tex anonymity signal missing")
    require("Author field is empty" in by_id["pdf_author_metadata"]["signal"], "PDF author metadata should be empty")
    require("10 pages" in by_id["pdf_page_count"]["signal"], "PDF page-count signal mismatch")

    findings = read_csv(out_dir / "submission_anonymity_findings.csv")
    require(len(findings) == 1, f"expected one sentinel finding row, found {len(findings)}")
    require(findings[0] == {"pattern_id": "none", "path": "none", "line": "0", "matched_text": "none"}, "findings table should contain only the none sentinel")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing anonymity audit report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required = [
        "Submission Anonymity Audit",
        "no-API audit",
        "Checks passed: 5",
        "Checks failed: 0",
        "Forbidden identity/path/API-secret text matches: 0",
        "git tracked files plus non-ignored new files",
        "OpenAI API calls: 0",
        "tracked_text_identity_scan",
        "tracked_tex_intermediates",
        "main_tex_anonymous_author",
        "pdf_author_metadata",
        "pdf_page_count",
        "manuscript author block is anonymous",
        "PDF author metadata is blank",
        "TeX intermediates remain untracked",
        "no local path, repository-owner, or API-secret value appears",
    ]
    for phrase in required:
        require(phrase in normalized, f"anonymity audit report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/submission_anonymity_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/submission_anonymity_v02.md"))
    args = parser.parse_args()

    check_tables(args.out_dir)
    check_report(args.report)
    print("submission anonymity audit validation passed")


if __name__ == "__main__":
    main()
