#!/usr/bin/env python
"""Write pre-specified acceptance rules for future human/native-review labels."""

from __future__ import annotations

import argparse
import csv
from math import ceil
from pathlib import Path
from typing import Any


OUT_DIR = Path("results/tables/human_audit_acceptance_rules_v02")
OUT_CSV = OUT_DIR / "human_audit_acceptance_rules.csv"
OUT_MD = Path("paper/human_audit_acceptance_rules_v02.md")

FIELDS = [
    "surface",
    "review_type",
    "launch_packet",
    "answer_or_launch_key",
    "roster_path",
    "expected_rows",
    "min_qualified_reviewers",
    "minimum_gate",
    "min_pass_agreements",
    "min_component_agreements",
    "min_release_usable_rows",
    "claim_if_pass",
    "claim_if_fail",
    "completion_validator",
    "summary_command",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def count_csv_rows(path: Path) -> int:
    require(path.exists(), f"missing launch packet {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return sum(1 for _ in csv.DictReader(f))


def check_path(path: str) -> str:
    require(Path(path).exists(), f"missing acceptance-rule path {path}")
    return path


def human_audit_row(
    *,
    surface: str,
    launch_packet: str,
    answer_key: str,
    roster_path: str,
    expected_models: str,
    out_dir: str,
    expected_rows: int,
) -> dict[str, Any]:
    rows = count_csv_rows(Path(launch_packet))
    require(rows == expected_rows, f"{surface} expected {expected_rows} rows, found {rows}")
    component_pairs = rows * 5
    return {
        "surface": surface,
        "review_type": "human_audit_completed_labels",
        "launch_packet": check_path(launch_packet),
        "answer_or_launch_key": check_path(answer_key),
        "roster_path": roster_path,
        "expected_rows": rows,
        "min_qualified_reviewers": 3,
        "minimum_gate": "completed-validator passes; pass agreement >=90%; component agreement >=85%; disagreements inspected before widening claims",
        "min_pass_agreements": ceil(0.90 * rows),
        "min_component_agreements": ceil(0.85 * component_pairs),
        "min_release_usable_rows": "",
        "claim_if_pass": "native/near-native audit supports the automatic scorer on sampled first-turn labels",
        "claim_if_fail": "report disagreement pattern and keep the automatic-plus-LLM-judge claim boundary",
        "completion_validator": (
            "conda run -n reprompt_tax python scripts/validate_completed_human_audit.py "
            f"--annotations {launch_packet.removesuffix('.csv')}_completed.csv "
            f"--answer-key {answer_key} --annotator-roster {roster_path} "
            f"--expected-models {expected_models}"
        ),
        "summary_command": (
            "conda run -n reprompt_tax python scripts/summarize_human_audit.py "
            f"--annotations {launch_packet.removesuffix('.csv')}_completed.csv "
            f"--answer-key {answer_key} --out-dir {out_dir}"
        ),
    }


def coverage_review_row() -> dict[str, Any]:
    launch_packet = "data/coverage_native_review_v03/coverage_native_review_packet_v03.csv"
    rows = count_csv_rows(Path(launch_packet))
    require(rows == 60, f"v0.3 native-review expected 60 rows, found {rows}")
    return {
        "surface": "coverage_native_review_v03",
        "review_type": "native_review_scaffold_release",
        "launch_packet": check_path(launch_packet),
        "answer_or_launch_key": check_path(launch_packet),
        "roster_path": "data/coverage_native_review_v03/coverage_native_review_roster_v03.csv",
        "expected_rows": rows,
        "min_qualified_reviewers": 6,
        "minimum_gate": "completed native-review validator passes; all rows release usable; zero unresolved issue rows before v0.3 performance claims",
        "min_pass_agreements": "",
        "min_component_agreements": "",
        "min_release_usable_rows": rows,
        "claim_if_pass": "v0.3 scaffold rows are native-review release usable; model performance still needs a pre-specified run",
        "claim_if_fail": "revise failed rows and relaunch native review before using v0.3 as paper-facing benchmark evidence",
        "completion_validator": (
            "conda run -n reprompt_tax python scripts/validate_completed_coverage_native_review_v03.py "
            "--annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv "
            "--launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv "
            "--reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv"
        ),
        "summary_command": (
            "conda run -n reprompt_tax python scripts/summarize_coverage_native_review_v03.py "
            "--annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv "
            "--launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv "
            "--reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv"
        ),
    }


def build_rows() -> list[dict[str, Any]]:
    return [
        human_audit_row(
            surface="human_audit_v02_gpt41_family",
            launch_packet="data/human_audit/human_audit_packet_v0.2.csv",
            answer_key="data/human_audit/human_audit_answer_key_v0.2.csv",
            roster_path="data/human_audit/human_audit_annotator_roster_v0.2.csv",
            expected_models="gpt-4.1,gpt-4.1-mini,gpt-4.1-nano",
            out_dir="results/tables/human_audit_v0.2",
            expected_rows=72,
        ),
        human_audit_row(
            surface="human_audit_v02_current_gpt5",
            launch_packet="data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv",
            answer_key="data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv",
            roster_path="data/current_model_human_audit/human_audit_annotator_roster_v0.2_current_gpt5.csv",
            expected_models="gpt-5.4-mini,gpt-5.5",
            out_dir="results/tables/human_audit_v0.2_current_gpt5",
            expected_rows=48,
        ),
        coverage_review_row(),
    ]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Human/Native Review Acceptance Rules",
        "",
        "These rules pre-specify what future completed labels must show before",
        "the paper can widen claims beyond automatic scoring plus LLM-judge",
        "sanity checks. They are not completed human validation.",
        "",
        "## Claim Gates",
        "",
        "| Surface | Rows | Reviewer minimum | Acceptance rule | Claim if pass | Claim if fail |",
        "|---|---:|---:|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['surface']} | {row['expected_rows']} | {row['min_qualified_reviewers']} | "
            f"{row['minimum_gate']} | {row['claim_if_pass']} | {row['claim_if_fail']} |"
        )
    lines.extend(
        [
            "",
            "## Numeric Thresholds",
            "",
            "| Surface | Pass agreements | Component agreements | Release-usable rows |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['surface']} | {row['min_pass_agreements']} | "
            f"{row['min_component_agreements']} | {row['min_release_usable_rows']} |"
        )
    lines.extend(
        [
            "",
            "## Required Commands",
            "",
        ]
    )
    for row in rows:
        lines.extend(
            [
                f"### {row['surface']}",
                "",
                "Validate completed labels:",
                "",
                "```bash",
                str(row["completion_validator"]),
                "```",
                "",
                "Summarize completed labels:",
                "",
                "```bash",
                str(row["summary_command"]),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Non-Negotiable Boundaries",
            "",
            "- A smoke-completed file never unlocks a paper claim.",
            "- Passing validation alone is necessary but not sufficient for a stronger claim; the quantitative thresholds above must also pass.",
            "- Completed-label validation requires every failed component to carry its matching failure or issue code, and rejects codes that contradict passing components.",
            "- If any v0.3 coverage row is not release usable, revise the scaffold and rerun native review before claiming v0.3 benchmark evidence.",
            "- If human-audit agreement misses threshold, report the disagreement pattern and keep the current conservative claim boundary.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-csv", type=Path, default=OUT_CSV)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    rows = build_rows()
    write_csv(args.out_csv, rows)
    write_markdown(args.out_md, rows)
    print(f"wrote human/native-review acceptance rules to {args.out_md} and {args.out_csv}")


if __name__ == "__main__":
    main()
