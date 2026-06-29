#!/usr/bin/env python
"""Generate a focused sprint plan for the current-model human audit labels."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Any


OUT_DIR = Path("results/tables/current_model_label_sprint_v02")
OUT_MD = Path("paper/current_model_label_sprint_v02.md")
SURFACE_ID = "current_model_human_audit_v02"
ASSIGNMENTS = Path("results/tables/label_collection_operator_handoff_v02/operator_double_label_assignments.csv")
RETURN_INTAKE = Path("results/tables/label_collection_operator_handoff_v02/operator_return_intake.csv")
QUALIFICATION_REQUIREMENTS = Path("results/tables/reviewer_qualification_requirements_v02/reviewer_qualification_requirements.csv")

LANGUAGE_LABELS = {
    "ar-en": {"name": "Arabic-English", "target_language": "Arabic", "script": "Arabic script"},
    "es-en": {"name": "Spanish-English", "target_language": "Spanish", "script": "Latin-script Spanish"},
    "hi-en": {"name": "Hindi-English", "target_language": "Hindi", "script": "Devanagari Hindi"},
}
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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing sprint input {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_csv_header_and_count(path: Path) -> tuple[list[str], int]:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    return fieldnames, len(rows)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(rows, f"refusing to write empty sprint table {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def surface_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out = [row for row in rows if row.get("surface_id") == SURFACE_ID]
    require(out, f"missing rows for {SURFACE_ID}")
    return out


def command_by_role(rows: list[dict[str, str]]) -> dict[str, str]:
    out = {}
    for row in surface_rows(rows):
        role = row["workflow_role"]
        require(role not in out, f"duplicate current-model return role {role}")
        out[role] = row["command"]
    return out


def qualification_by_slot(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    out: dict[tuple[str, str], dict[str, str]] = {}
    per_language_counter: defaultdict[str, int] = defaultdict(int)
    for row in surface_rows(rows):
        language_pair = row["expected_language_pair"]
        per_language_counter[language_pair] += 1
        reviewer_index = str(per_language_counter[language_pair])
        out[(language_pair, reviewer_index)] = row
    return out


def build_message(row: dict[str, str]) -> str:
    return (
        "Please complete the attached blinded RePromptTax review bundle. "
        f"It contains {row['rows_to_label']} rows for {LANGUAGE_LABELS[row['language_pair']]['name']}. "
        "Use only your own language judgment, do not use machine translation or other external tools to decide labels, "
        "fill every TRUE/FALSE field, add the required reason code for any failed component, "
        f"and save the completed CSV exactly at {row['expected_return_path']}. "
        "Do not add columns or edit static prompt and response fields."
    )


def build_slots(assignments: list[dict[str, str]], qualifications: list[dict[str, str]]) -> list[dict[str, Any]]:
    qual_by_slot = qualification_by_slot(qualifications)
    rows = []
    for assignment in sorted(
        surface_rows(assignments),
        key=lambda row: (row["slice_id"], int(row["reviewer_index"])),
    ):
        require(assignment["workflow_mode"] == "preferred_double_label", "current-model sprint uses the preferred double-label path")
        key = (assignment["slice_id"], assignment["reviewer_index"])
        require(key in qual_by_slot, f"missing qualification slot for {key}")
        qual = qual_by_slot[key]
        rows.append(
            {
                "surface_id": SURFACE_ID,
                "language_pair": assignment["slice_id"],
                "reviewer_index": assignment["reviewer_index"],
                "reviewer_slot": assignment["reviewer_slot"],
                "rows_to_label": assignment["rows"],
                "target_language": LANGUAGE_LABELS[assignment["slice_id"]]["target_language"],
                "required_script": LANGUAGE_LABELS[assignment["slice_id"]]["script"],
                "bundle_path": assignment["attach_bundle_path"],
                "bundle_sha256": assignment["bundle_sha256"],
                "expected_return_path": assignment["expected_return_path"],
                "expected_export_name": assignment["expected_export_name"],
                "roster_template": qual["roster_template"],
                "completed_roster": qual["completed_roster"],
                "template_reviewer_id": qual["template_reviewer_id"],
                "required_roster_values": "native_or_near_native=TRUE; can_validate_script=TRUE; conflict_of_interest=FALSE; qualification_notes nonempty",
                "claim_boundary": "no_current_model_human_validation_claim_until_completed_labels_and_roster_pass_gates",
            }
        )
    return rows


def build_screener() -> list[dict[str, Any]]:
    rows = []
    for language_pair, spec in LANGUAGE_LABELS.items():
        rows.extend(
            [
                {
                    "language_pair": language_pair,
                    "question_id": "native_or_near_native",
                    "question": f"Can you make native or near-native judgments for {spec['target_language']} text in this review task?",
                    "required_response": "TRUE",
                    "roster_field": "native_or_near_native",
                    "disqualifying_response": "FALSE or blank",
                },
                {
                    "language_pair": language_pair,
                    "question_id": "script_validation",
                    "question": f"Can you reliably validate {spec['script']} in short assistant responses?",
                    "required_response": "TRUE",
                    "roster_field": "can_validate_script",
                    "disqualifying_response": "FALSE or blank",
                },
                {
                    "language_pair": language_pair,
                    "question_id": "qualification_notes",
                    "question": "Provide a brief non-identifying note about the basis for your language qualification.",
                    "required_response": "nonempty text",
                    "roster_field": "qualification_notes",
                    "disqualifying_response": "blank",
                },
                {
                    "language_pair": language_pair,
                    "question_id": "conflict_of_interest",
                    "question": "Do you have any conflict of interest with this benchmark or its authors?",
                    "required_response": "FALSE",
                    "roster_field": "conflict_of_interest",
                    "disqualifying_response": "TRUE or blank",
                },
                {
                    "language_pair": language_pair,
                    "question_id": "no_external_tools",
                    "question": "Can you complete labels using your own judgment without machine translation or other external decision aids?",
                    "required_response": "TRUE",
                    "roster_field": "reviewer_attestation",
                    "disqualifying_response": "FALSE or blank",
                },
            ]
        )
    return rows


def build_messages(slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for slot in slots:
        message = build_message(slot)
        lowered = message.lower()
        for marker in PRIVATE_MARKERS:
            require(marker not in lowered, f"reviewer sprint message leaks private marker {marker}")
        rows.append(
            {
                "language_pair": slot["language_pair"],
                "reviewer_index": slot["reviewer_index"],
                "subject": f"RePromptTax blinded review bundle: {LANGUAGE_LABELS[slot['language_pair']]['name']}",
                "body": message,
                "attach_bundle_path": slot["bundle_path"],
                "expected_return_path": slot["expected_return_path"],
            }
        )
    return rows


def next_status_action(*, return_present: bool, shape_ready: bool, roster_present: bool) -> str:
    actions: list[str] = []
    if not return_present:
        actions.append("collect completed reviewer CSV")
    elif not shape_ready:
        actions.append("fix returned CSV header or row count")
    if not roster_present:
        actions.append("fill qualified reviewer roster")
    return "; ".join(actions) if actions else "ready for double-label merge"


def build_status(slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    expected_header, _ = read_csv_header_and_count(Path("data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv"))
    require(expected_header, "current-model launch packet has no header")
    rows = []
    for slot in slots:
        return_path = Path(slot["expected_return_path"])
        roster_path = Path(slot["completed_roster"])
        roster_present = roster_path.exists()
        if return_path.exists():
            observed_header, observed_rows = read_csv_header_and_count(return_path)
            header_ok = observed_header == expected_header
            rows_ok = observed_rows == int(slot["rows_to_label"])
            shape_ready = header_ok and rows_ok
            observed_rows_text: int | str = observed_rows
        else:
            shape_ready = False
            observed_rows_text = ""
        return_present = return_path.exists()
        blockers: list[str] = []
        if not return_present:
            blockers.append("missing returned CSV")
        elif not shape_ready:
            blockers.append("returned CSV header or row count mismatch")
        if not roster_present:
            blockers.append("missing qualified roster")
        rows.append(
            {
                "surface_id": slot["surface_id"],
                "language_pair": slot["language_pair"],
                "reviewer_index": slot["reviewer_index"],
                "rows_to_label": slot["rows_to_label"],
                "bundle_path": slot["bundle_path"],
                "expected_return_path": slot["expected_return_path"],
                "return_present": str(return_present),
                "observed_rows": observed_rows_text,
                "shape_ready": str(shape_ready),
                "completed_roster": slot["completed_roster"],
                "roster_present": str(roster_present),
                "ready_for_merge": str(return_present and shape_ready and roster_present),
                "blocker": "; ".join(blockers) if blockers else "none",
                "next_action": next_status_action(
                    return_present=return_present,
                    shape_ready=shape_ready,
                    roster_present=roster_present,
                ),
                "claim_boundary": slot["claim_boundary"],
            }
        )
    return rows


def build_return_plan(commands: dict[str, str]) -> list[dict[str, Any]]:
    return [
        {
            "step_order": 1,
            "step_id": "screen_reviewers",
            "action": "Screen two qualified reviewers per language pair using the sprint screener.",
            "evidence_required": "six qualified reviewer slots with non-placeholder IDs",
            "command": "",
        },
        {
            "step_order": 2,
            "step_id": "fill_roster",
            "action": "Fill the current-model annotator roster with qualified reviewer IDs and notes.",
            "evidence_required": "data/current_model_human_audit/human_audit_annotator_roster_v0.2_current_gpt5.csv",
            "command": "",
        },
        {
            "step_order": 3,
            "step_id": "send_bundles",
            "action": "Send the three blinded current-model bundles to reviewer1 and reviewer2 for each language pair.",
            "evidence_required": "six returned completed CSV files with the expected reviewer1/reviewer2 names",
            "command": "",
        },
        {
            "step_order": 4,
            "step_id": "merge_double_labels",
            "action": "Merge the six reviewer returns into the double-label packet.",
            "evidence_required": "data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_double_completed.csv",
            "command": commands["merge_double_label_exports"],
        },
        {
            "step_order": 5,
            "step_id": "analyze_disagreements",
            "action": "Generate the disagreement packet for adjudication.",
            "evidence_required": "current-model disagreement and adjudication artifacts",
            "command": commands["analyze_double_labels"],
        },
        {
            "step_order": 6,
            "step_id": "finalize_adjudicated_labels",
            "action": "Finalize one adjudicated label row per audit item.",
            "evidence_required": "data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_completed.csv",
            "command": commands["finalize_adjudicated_labels"],
        },
        {
            "step_order": 7,
            "step_id": "validate_finalized_labels",
            "action": "Validate the completed current-model human audit labels and roster.",
            "evidence_required": "completed human-audit validation passed",
            "command": commands["validate_finalized_labels"],
        },
        {
            "step_order": 8,
            "step_id": "summarize_finalized_labels",
            "action": "Summarize finalized labels before any claim wording changes.",
            "evidence_required": "current-model human-audit summary tables",
            "command": commands["summarize_finalized_labels"],
        },
    ]


def write_markdown(
    path: Path,
    *,
    slots: list[dict[str, Any]],
    status: list[dict[str, Any]],
    screener: list[dict[str, Any]],
    messages: list[dict[str, Any]],
    return_plan: list[dict[str, Any]],
) -> None:
    languages = sorted({row["language_pair"] for row in slots})
    total_row_judgments = sum(int(row["rows_to_label"]) for row in slots)
    present_returns = sum(row["return_present"] == "True" for row in status)
    ready_returns = sum(row["shape_ready"] == "True" for row in status)
    roster_present = any(row["roster_present"] == "True" for row in status)
    lines = [
        "# Current-Model Label Sprint",
        "",
        "This no-API sprint artifact isolates the smallest external-label task",
        "that can upgrade the GPT-5.x headline: the 48-row current-model",
        "human/native audit. It is an operational collection plan, not",
        "completed human/native validation.",
        "",
        "## Summary",
        "",
        f"- Surface: `{SURFACE_ID}`",
        f"- Unique audit rows: 48",
        f"- Preferred reviewer slots: {len(slots)}",
        f"- Preferred row judgments: {total_row_judgments}",
        f"- Returned reviewer CSVs present: {present_returns}/{len(status)}",
        f"- Shape-ready reviewer CSVs: {ready_returns}/{len(status)}",
        f"- Qualified roster present: {roster_present}",
        f"- Language pairs: {', '.join(languages)}",
        "- Fallback minimum path: one qualified reviewer per language pair.",
        "- Stronger path: two independent reviewers per language pair, then",
        "  adjudicate disagreements before running completed-label gates.",
        "- OpenAI API calls: 0",
        "- Claim boundary: do not claim current-model human/native validation",
        "  until finalized labels and the qualified roster pass validation.",
        "",
        "## Reviewer Slots",
        "",
        "| Language pair | Reviewer | Rows | Bundle | Expected return |",
        "|---|---:|---:|---|---|",
    ]
    for row in slots:
        lines.append(
            f"| {row['language_pair']} | {row['reviewer_index']} | {row['rows_to_label']} | "
            f"`{row['bundle_path']}` | `{row['expected_return_path']}` |"
        )
    lines.extend(
        [
            "",
            "## Status Board",
            "",
            "| Language pair | Reviewer | Return present | Shape ready | Roster present | Ready for merge | Next action |",
            "|---|---:|---|---|---|---|---|",
        ]
    )
    for row in status:
        lines.append(
            f"| {row['language_pair']} | {row['reviewer_index']} | {row['return_present']} | "
            f"{row['shape_ready']} | {row['roster_present']} | {row['ready_for_merge']} | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Screener",
            "",
            "| Language pair | Question ID | Required response | Roster field |",
            "|---|---|---|---|",
        ]
    )
    for row in screener:
        lines.append(
            f"| {row['language_pair']} | {row['question_id']} | {row['required_response']} | {row['roster_field']} |"
        )
    lines.extend(
        [
            "",
            "## Send Messages",
            "",
            "| Language pair | Reviewer | Subject | Bundle | Expected return |",
            "|---|---:|---|---|---|",
        ]
    )
    for row in messages:
        lines.append(
            f"| {row['language_pair']} | {row['reviewer_index']} | {row['subject']} | "
            f"`{row['attach_bundle_path']}` | `{row['expected_return_path']}` |"
        )
    lines.extend(
        [
            "",
            "## Return Plan",
            "",
            "| Step | ID | Action | Command |",
            "|---:|---|---|---|",
        ]
    )
    for row in return_plan:
        command = f"`{row['command']}`" if row["command"] else "operator action"
        lines.append(f"| {row['step_order']} | {row['step_id']} | {row['action']} | {command} |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This artifact does not report completed labels. It only makes the",
            "first-priority label sprint concrete enough to execute and audit.",
            "Paper claims remain unchanged until the completed current-model audit",
            "file, qualified roster, summaries, and completed-label gates pass.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    slots = build_slots(read_csv(ASSIGNMENTS), read_csv(QUALIFICATION_REQUIREMENTS))
    screener = build_screener()
    messages = build_messages(slots)
    status = build_status(slots)
    return_plan = build_return_plan(command_by_role(read_csv(RETURN_INTAKE)))

    write_csv(args.out_dir / "current_model_label_sprint_slots.csv", slots)
    write_csv(args.out_dir / "current_model_label_sprint_status.csv", status)
    write_csv(args.out_dir / "current_model_label_sprint_screener.csv", screener)
    write_csv(args.out_dir / "current_model_label_sprint_messages.csv", messages)
    write_csv(args.out_dir / "current_model_label_sprint_return_plan.csv", return_plan)
    write_markdown(args.out_md, slots=slots, status=status, screener=screener, messages=messages, return_plan=return_plan)
    print(f"wrote current-model label sprint to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
