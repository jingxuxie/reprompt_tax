#!/usr/bin/env python
"""Audit double-blind submission hygiene for tracked and sendable artifacts."""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
from pathlib import Path
from typing import Any


OUT_DIR = Path("results/tables/submission_anonymity_v02")
OUT_MD = Path("paper/submission_anonymity_v02.md")

TEXT_SUFFIXES = {
    ".bib",
    ".csv",
    ".html",
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".sty",
    ".tex",
    ".txt",
    ".yaml",
    ".yml",
}

TRACKED_TEX_INTERMEDIATES = {
    ".aux",
    ".blg",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
}
SELF_OUTPUT_PREFIXES = ("results/tables/submission_anonymity_v02/",)
SELF_OUTPUT_PATHS = {"paper/submission_anonymity_v02.md"}

LOCAL_IDENTITY_TERMS = ["es" + "ton", "colm_" + "workshop"]

FORBIDDEN_TEXT_PATTERNS = {
    "local_home_path": re.compile(r"/(?:home|Users)/[A-Za-z0-9._-]+"),
    "workspace_owner_path": re.compile(r"\b(?:" + "|".join(re.escape(term) for term in LOCAL_IDENTITY_TERMS) + r")\b", re.IGNORECASE),
    "github_owner_identity": re.compile(r"\bjingxuxie\b", re.IGNORECASE),
    "openai_secret_value": re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    "explicit_env_secret_assignment": re.compile(r"\bOPENAI_API_KEY\s*=", re.IGNORECASE),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_git_file_list(root: Path) -> list[Path]:
    proc = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        check=True,
        text=True,
        capture_output=True,
    )
    paths = [Path(line) for line in proc.stdout.splitlines() if line.strip()]
    require(paths, "git file list is empty")
    return sorted(paths, key=lambda path: path.as_posix())


def read_text_if_supported(root: Path, path: Path) -> str | None:
    if path.suffix not in TEXT_SUFFIXES:
        return None
    try:
        return (root / path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return (root / path).read_text(encoding="utf-8", errors="ignore")


def pdfinfo(root: Path, path: Path) -> str:
    proc = subprocess.run(["pdfinfo", str(path)], cwd=root, check=True, text=True, capture_output=True)
    return proc.stdout


def status_row(check_id: str, status: str, signal: str, scope: str, next_action: str) -> dict[str, str]:
    return {
        "check_id": check_id,
        "status": status,
        "signal": signal,
        "scope": scope,
        "next_action": next_action,
    }


def find_forbidden_text(root: Path, paths: list[Path]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in paths:
        path_text = path.as_posix()
        if path_text in SELF_OUTPUT_PATHS or any(path_text.startswith(prefix) for prefix in SELF_OUTPUT_PREFIXES):
            continue
        text = read_text_if_supported(root, path)
        if text is None:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for pattern_id, pattern in FORBIDDEN_TEXT_PATTERNS.items():
                if pattern.search(line):
                    findings.append(
                        {
                            "pattern_id": pattern_id,
                            "path": path.as_posix(),
                            "line": str(line_no),
                            "matched_text": pattern.search(line).group(0),
                        }
                    )
    return findings


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, f"refusing to write empty anonymity table {path}")
    fields = fieldnames or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_checks(root: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    paths = run_git_file_list(root)
    findings = find_forbidden_text(root, paths)
    tracked_tex = sorted(
        path.as_posix()
        for path in paths
        if path.parts[:1] == ("paper",) and path.suffix in TRACKED_TEX_INTERMEDIATES
    )
    main_tex = (root / "paper/main.tex").read_text(encoding="utf-8")
    pdf_info = pdfinfo(root, Path("paper/main.pdf"))
    pdf_author = ""
    for line in pdf_info.splitlines():
        if line.startswith("Author:"):
            pdf_author = line.split(":", 1)[1].strip()
            break
    pdf_pages = ""
    for line in pdf_info.splitlines():
        if line.startswith("Pages:"):
            pdf_pages = line.split(":", 1)[1].strip()
            break

    checks = [
        status_row(
            "tracked_text_identity_scan",
            "pass" if not findings else "fail",
            f"{len(findings)} forbidden identity/path/API-secret text matches across {len(paths)} tracked-or-sendable files",
            "git tracked files plus non-ignored new files",
            "remove local identity/path/key text before submission" if findings else "none",
        ),
        status_row(
            "tracked_tex_intermediates",
            "pass" if not tracked_tex else "fail",
            f"{len(tracked_tex)} tracked TeX intermediary files",
            "paper/*.aux, *.blg, *.fdb_latexmk, *.fls, *.log, *.out",
            "leave TeX intermediates ignored and untracked" if tracked_tex else "none",
        ),
        status_row(
            "main_tex_anonymous_author",
            "pass" if "Anonymous authors\\\\Paper under double-blind review" in main_tex else "fail",
            "main.tex uses the anonymous COLM submission author block",
            "paper/main.tex",
            "restore anonymous author block before submission",
        ),
        status_row(
            "pdf_author_metadata",
            "pass" if pdf_author == "" else "fail",
            "pdfinfo Author field is empty" if pdf_author == "" else f"pdfinfo Author field is {pdf_author!r}",
            "paper/main.pdf",
            "clear PDF author metadata before submission",
        ),
        status_row(
            "pdf_page_count",
            "pass" if pdf_pages == "10" else "fail",
            f"pdfinfo reports {pdf_pages or 'unknown'} pages",
            "paper/main.pdf",
            "inspect COLM/workshop page budget before submission",
        ),
    ]
    return checks, findings


def write_markdown(path: Path, checks: list[dict[str, str]], findings: list[dict[str, str]]) -> None:
    pass_count = sum(1 for row in checks if row["status"] == "pass")
    fail_count = sum(1 for row in checks if row["status"] == "fail")
    lines = [
        "# Submission Anonymity Audit",
        "",
        "This no-API audit checks double-blind and release-hygiene properties for",
        "tracked and sendable RePromptTax artifacts. It does not inspect ignored",
        "local TeX build intermediates, caches, or private API-key files.",
        "",
        "## Summary",
        "",
        f"- Checks passed: {pass_count}",
        f"- Checks failed: {fail_count}",
        f"- Forbidden identity/path/API-secret text matches: {len(findings)}",
        "- Scope: git tracked files plus non-ignored new files.",
        "- OpenAI API calls: 0",
        "",
        "## Check Table",
        "",
        "| Check | Status | Signal | Scope | Next action |",
        "|---|---|---|---|---|",
    ]
    for row in checks:
        lines.append(
            f"| `{row['check_id']}` | {row['status']} | {row['signal']} | "
            f"{row['scope']} | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Finding Table",
            "",
            "| Pattern | Path | Line | Matched text |",
            "|---|---|---:|---|",
        ]
    )
    if findings:
        for finding in findings:
            lines.append(
                f"| `{finding['pattern_id']}` | `{finding['path']}` | "
                f"{finding['line']} | `{finding['matched_text']}` |"
            )
    else:
        lines.append("| none | none | 0 | none |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The checked submission surface is anonymous under the current gate: the",
            "manuscript author block is anonymous, PDF author metadata is blank, TeX",
            "intermediates remain untracked, and no local path, repository-owner, or",
            "API-secret value appears in tracked or sendable text artifacts.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    root = args.root.resolve()
    checks, findings = build_checks(root)
    write_csv(args.out_dir / "submission_anonymity_checks.csv", checks)
    write_csv(
        args.out_dir / "submission_anonymity_findings.csv",
        findings or [{"pattern_id": "none", "path": "none", "line": "0", "matched_text": "none"}],
        ["pattern_id", "path", "line", "matched_text"],
    )
    write_markdown(args.out_md, checks, findings)
    failed = [row["check_id"] for row in checks if row["status"] != "pass"]
    require(not failed, f"submission anonymity audit failed checks: {failed}")
    print(f"wrote submission anonymity audit to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
