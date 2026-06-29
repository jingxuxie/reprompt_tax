#!/usr/bin/env python
"""Validate the current-model human-audit label sprint artifact."""

from __future__ import annotations

import argparse
import csv
import hashlib
import shlex
from collections import Counter
from pathlib import Path


EXPECTED_LANGUAGES = {"ar-en", "es-en", "hi-en"}
PRIVATE_MARKERS = (
    "answer_key",
    "auto_pass",
    "automatic label",
    "automatic labels",
    "baseline",
    "contract",
    "gpt-5.4",
    "gpt-5.5",
    "prompt condition",
    "prompt conditions",
)
EXPECTED_STEPS = [
    "screen_reviewers",
    "fill_roster",
    "send_bundles",
    "merge_double_labels",
    "analyze_disagreements",
    "finalize_adjudicated_labels",
    "validate_finalized_labels",
    "summarize_finalized_labels",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing current-model label sprint table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command_arg(command: str, flag: str) -> str:
    parts = shlex.split(command)
    if flag not in parts:
        return ""
    index = parts.index(flag)
    if index + 1 >= len(parts):
        return ""
    return parts[index + 1]


def check_slots(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == 6, f"expected 6 current-model reviewer slots, found {len(rows)}")
    require({row["language_pair"] for row in rows} == EXPECTED_LANGUAGES, "language-pair set mismatch")
    per_language = Counter(row["language_pair"] for row in rows)
    require(all(count == 2 for count in per_language.values()), f"expected two reviewers per language pair: {per_language}")
    reviewer_indices = Counter((row["language_pair"], row["reviewer_index"]) for row in rows)
    require(all(count == 1 for count in reviewer_indices.values()), "duplicate reviewer slot")
    require({row["reviewer_index"] for row in rows} == {"1", "2"}, "reviewer indices must be 1 and 2")
    require(sum(int(row["rows_to_label"]) for row in rows) == 96, "expected 96 preferred row judgments")
    for row in rows:
        require(row["surface_id"] == "current_model_human_audit_v02", "sprint must only cover current-model audit")
        require(row["rows_to_label"] == "16", f"{row['language_pair']} should have 16 rows per reviewer")
        require(f"_reviewer{row['reviewer_index']}_completed.csv" in row["expected_return_path"], "return path missing reviewer suffix")
        require(row["expected_export_name"] in row["expected_return_path"], "return path/export-name mismatch")
        require(row["expected_return_path"].startswith("data/current_model_human_audit/"), "return path must stay in current-model audit data dir")
        require(row["roster_template"].endswith("human_audit_annotator_roster_template_v0.2_current_gpt5.csv"), "wrong roster template")
        require(row["completed_roster"].endswith("human_audit_annotator_roster_v0.2_current_gpt5.csv"), "wrong completed roster")
        require("native_or_near_native=TRUE" in row["required_roster_values"], "missing native qualification requirement")
        require("can_validate_script=TRUE" in row["required_roster_values"], "missing script qualification requirement")
        require("conflict_of_interest=FALSE" in row["required_roster_values"], "missing conflict requirement")
        require(row["claim_boundary"] == "no_current_model_human_validation_claim_until_completed_labels_and_roster_pass_gates", "claim boundary mismatch")
        bundle = Path(row["bundle_path"])
        require(bundle.exists(), f"missing bundle {bundle}")
        require(sha256_file(bundle) == row["bundle_sha256"], f"bundle sha256 mismatch for {bundle}")


def check_screener(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == 15, f"expected 15 screener rows, found {len(rows)}")
    require({row["language_pair"] for row in rows} == EXPECTED_LANGUAGES, "screener language mismatch")
    per_language = Counter(row["language_pair"] for row in rows)
    require(all(count == 5 for count in per_language.values()), f"expected five screener questions per language: {per_language}")
    required_questions = {
        "native_or_near_native",
        "script_validation",
        "qualification_notes",
        "conflict_of_interest",
        "no_external_tools",
    }
    for language_pair in EXPECTED_LANGUAGES:
        questions = {row["question_id"] for row in rows if row["language_pair"] == language_pair}
        require(questions == required_questions, f"{language_pair} screener questions mismatch: {questions}")
    required_fields = {row["roster_field"] for row in rows}
    for field in {"native_or_near_native", "can_validate_script", "qualification_notes", "conflict_of_interest", "reviewer_attestation"}:
        require(field in required_fields, f"screener missing roster/attestation field {field}")


def check_messages(path: Path) -> None:
    rows = read_csv(path)
    require(len(rows) == 6, f"expected 6 sprint messages, found {len(rows)}")
    require({row["language_pair"] for row in rows} == EXPECTED_LANGUAGES, "message language mismatch")
    per_language = Counter(row["language_pair"] for row in rows)
    require(all(count == 2 for count in per_language.values()), f"expected two messages per language: {per_language}")
    return_paths: set[str] = set()
    for row in rows:
        body = row["body"].lower()
        for marker in PRIVATE_MARKERS:
            require(marker not in body, f"message leaks private marker {marker}")
        require("blinded reprompttax review bundle" in body, "message must identify blinded review bundle")
        require("do not use machine translation" in body, "message must forbid machine translation decision aids")
        require(row["expected_return_path"].startswith("data/current_model_human_audit/"), "message return path outside current-model audit")
        require(row["attach_bundle_path"].startswith("results/label_collection_bundles_v02/current_model_human_audit_v02/"), "wrong bundle path")
        require(row["expected_return_path"] in body, "message body should include exact expected return path")
        return_paths.add(row["expected_return_path"])
    require(len(return_paths) == 6, "duplicate message return paths")


def check_return_plan(path: Path) -> None:
    rows = read_csv(path)
    require([row["step_id"] for row in rows] == EXPECTED_STEPS, "return-plan step sequence mismatch")
    require([row["step_order"] for row in rows] == [str(index) for index in range(1, 9)], "return-plan order mismatch")
    command_by_step = {row["step_id"]: row["command"] for row in rows}
    require("--labels-per-item 2" in command_by_step["merge_double_labels"], "double-label merge command missing labels-per-item 2")
    require("_double_completed.csv" in command_by_step["merge_double_labels"], "double-label merge command missing double-completed output")
    require("scripts/analyze_human_audit_adjudication.py" in command_by_step["analyze_disagreements"], "missing adjudication-analysis command")
    require("scripts/finalize_human_audit_adjudication.py" in command_by_step["finalize_adjudicated_labels"], "missing adjudication-finalization command")
    require("scripts/validate_completed_human_audit.py" in command_by_step["validate_finalized_labels"], "missing finalized-label validator")
    require("scripts/summarize_human_audit.py" in command_by_step["summarize_finalized_labels"], "missing finalized-label summarizer")
    require("--expected-models" not in command_by_step["summarize_finalized_labels"], "summarize_human_audit command uses unsupported --expected-models")
    require(
        command_arg(command_by_step["finalize_adjudicated_labels"], "--out")
        == command_arg(command_by_step["validate_finalized_labels"], "--annotations"),
        "finalization output must match validator annotations",
    )
    for row in rows:
        if row["command"]:
            require(row["command"].startswith("conda run -n reprompt_tax python scripts/"), f"non-reproducible command in {row['step_id']}")
            require("current_model_human_audit" in row["command"], f"{row['step_id']} command must stay on current-model audit")


def check_report(path: Path) -> None:
    require(path.exists(), f"missing current-model label sprint report {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required_phrases = [
        "Current-Model Label Sprint",
        "smallest external-label task",
        "operational collection plan, not completed human/native validation",
        "Unique audit rows: 48",
        "Preferred reviewer slots: 6",
        "Preferred row judgments: 96",
        "Fallback minimum path: one qualified reviewer per language pair",
        "two independent reviewers per language pair",
        "OpenAI API calls: 0",
        "do not claim current-model human/native validation",
        "merge_double_labels",
        "validate_finalized_labels",
        "This artifact does not report completed labels",
    ]
    for phrase in required_phrases:
        require(phrase in normalized, f"current-model label sprint report missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/current_model_label_sprint_v02"))
    parser.add_argument("--report", type=Path, default=Path("paper/current_model_label_sprint_v02.md"))
    args = parser.parse_args()

    check_slots(args.out_dir / "current_model_label_sprint_slots.csv")
    check_screener(args.out_dir / "current_model_label_sprint_screener.csv")
    check_messages(args.out_dir / "current_model_label_sprint_messages.csv")
    check_return_plan(args.out_dir / "current_model_label_sprint_return_plan.csv")
    check_report(args.report)
    print("current-model label sprint validation passed")


if __name__ == "__main__":
    main()
