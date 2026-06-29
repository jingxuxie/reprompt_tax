#!/usr/bin/env python
"""Generate an operator handoff for qualified human/native label collection."""

from __future__ import annotations

import argparse
import csv
import textwrap
from pathlib import Path
from typing import Any


OUT_DIR = Path("results/tables/label_collection_operator_handoff_v02")
OUT_MD = Path("paper/label_collection_operator_handoff_v02.md")

DISPATCH_MANIFEST = Path("results/tables/label_collection_dispatch_v02/label_collection_dispatch_manifest.csv")
DISPATCH_SUMMARY = Path("results/tables/label_collection_dispatch_v02/label_collection_dispatch_summary.csv")
LAUNCH_COMMANDS = Path("results/tables/label_collection_launch_pack_v02/label_collection_commands.csv")

SURFACE_LABELS = {
    "current_model_human_audit_v02": "Current-model human/native audit",
    "human_audit_v02": "Original v0.2 human/native audit",
    "coverage_native_review_v03": "v0.3 coverage native review",
}

OUTGOING_PRIVATE_MARKERS = (
    "answer_key",
    "automatic label",
    "automatic labels",
    "auto_pass",
    "model name",
    "model names",
    "prompt condition",
    "prompt conditions",
)

EXPECTED_COMMAND_ROLES = (
    "merge_single_label_exports",
    "validate_finalized_labels",
    "summarize_finalized_labels",
    "analyze_double_labels",
    "finalize_adjudicated_labels",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing handoff input {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, f"refusing to write empty handoff table {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_message(row: dict[str, str]) -> str:
    return textwrap.dedent(
        f"""\
        Please complete the attached RePromptTax review bundle for {row['title']}.
        It contains {row['expected_rows']} rows. Use your assigned reviewer ID,
        fill every TRUE/FALSE field, include the matching reason code for any
        failed component, and export the completed CSV as
        {row['expected_export_name']}. Please do not add extra columns or edit
        static prompt fields."""
    ).replace("\n", " ")


def build_dispatch_rows(dispatch_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in dispatch_rows:
        require(row["ready_to_send"] == "True", f"{row['surface_id']}:{row['slice_id']} is not ready to send")
        require(row["claim_decision"] == "no_claim", f"{row['surface_id']} must not unlock a claim")
        require(Path(row["bundle_path"]).exists(), f"missing bundle {row['bundle_path']}")
        body = build_message(row)
        lowered = body.lower()
        for marker in OUTGOING_PRIVATE_MARKERS:
            require(marker not in lowered, f"outgoing reviewer message leaks private marker {marker}")
        out.append(
            {
                "dispatch_priority": row["dispatch_priority"],
                "surface_id": row["surface_id"],
                "slice_id": row["slice_id"],
                "reviewer_slot": f"{row['surface_id']}::{row['slice_id']}::reviewer_1",
                "surface_label": SURFACE_LABELS[row["surface_id"]],
                "title": row["title"],
                "rows": row["expected_rows"],
                "attach_bundle_path": row["bundle_path"],
                "bundle_sha256": row["bundle_sha256"],
                "expected_return_path": row["expected_return_path"],
                "expected_export_name": row["expected_export_name"],
                "outgoing_subject": f"RePromptTax review bundle: {row['title']}",
                "outgoing_message": body,
                "claim_boundary": "do_not_claim_completed_human_or_native_validation_until_finalized_labels_pass_gates",
            }
        )
    return out


def command_by_surface_role(command_rows: list[dict[str, str]]) -> dict[tuple[str, str], str]:
    out: dict[tuple[str, str], str] = {}
    for row in command_rows:
        key = (row["surface_id"], row["command_role"])
        require(key not in out, f"duplicate command row {key}")
        out[key] = row["command"]
    return out


def build_return_rows(summary_rows: list[dict[str, str]], command_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    commands = command_by_surface_role(command_rows)
    out: list[dict[str, Any]] = []
    for summary in summary_rows:
        surface_id = summary["surface_id"]
        require(summary["claim_decision"] == "no_claim", f"{surface_id} should remain no_claim before labels")
        for order, role in enumerate(EXPECTED_COMMAND_ROLES, start=1):
            key = (surface_id, role)
            require(key in commands, f"{surface_id} missing command role {role}")
            out.append(
                {
                    "dispatch_priority": summary["dispatch_priority"],
                    "surface_id": surface_id,
                    "surface_label": SURFACE_LABELS[surface_id],
                    "step_order": order,
                    "workflow_role": role,
                    "command": commands[key],
                    "required_before_running": summary["claim_required_action"],
                    "claim_gate_status_before_labels": summary["claim_gate_status"],
                    "claim_decision_before_labels": summary["claim_decision"],
                }
            )
    return out


def write_markdown(
    path: Path,
    *,
    dispatch_rows: list[dict[str, Any]],
    return_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, str]],
) -> None:
    total_rows = sum(int(row["rows"]) for row in dispatch_rows)
    lines = [
        "# Label Collection Operator Handoff",
        "",
        "This handoff converts the validated reviewer bundles into an execution",
        "checklist for collecting the missing qualified human/native labels. It",
        "is operational support, not completed human/native validation.",
        "",
        "## Summary",
        "",
        f"- Outgoing reviewer bundle assignments: {len(dispatch_rows)}",
        f"- Reviewer-facing rows to collect: {total_rows}",
        "- First priority: current-model human/native audit.",
        "- OpenAI API calls: 0",
        "- Claim boundary: no human/native-validation claim is unlocked until",
        "  returned labels, rosters, summaries, and completed-label gates pass.",
        "",
        "## Send Checklist",
        "",
        "| Priority | Surface | Slice | Rows | Bundle | Expected return |",
        "|---:|---|---|---:|---|---|",
    ]
    for row in dispatch_rows:
        lines.append(
            f"| {row['dispatch_priority']} | {row['surface_id']} | {row['slice_id']} | "
            f"{row['rows']} | `{row['attach_bundle_path']}` | `{row['expected_return_path']}` |"
        )
    lines.extend(
        [
            "",
            "## Return Intake",
            "",
            "| Priority | Surface | Step | Command role |",
            "|---:|---|---:|---|",
        ]
    )
    for row in return_rows:
        lines.append(f"| {row['dispatch_priority']} | {row['surface_id']} | {row['step_order']} | `{row['workflow_role']}` |")
    lines.extend(
        [
            "",
            "Run the single-label merge, finalized-label validator, and summary only",
            "after every expected slice export and qualified roster for the surface",
            "has been returned. For the stronger two-reviewer workflow, use the",
            "`analyze_double_labels` and `finalize_adjudicated_labels` commands",
            "before any paper claim is widened.",
            "",
            "## Claim Gate Status",
            "",
            "| Priority | Surface | Gate status | Decision | Required action |",
            "|---:|---|---|---|---|",
        ]
    )
    for row in summary_rows:
        lines.append(
            f"| {row['dispatch_priority']} | {row['surface_id']} | {row['claim_gate_status']} | "
            f"{row['claim_decision']} | {row['claim_required_action']} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dispatch-manifest", type=Path, default=DISPATCH_MANIFEST)
    parser.add_argument("--dispatch-summary", type=Path, default=DISPATCH_SUMMARY)
    parser.add_argument("--launch-commands", type=Path, default=LAUNCH_COMMANDS)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    dispatch_rows = build_dispatch_rows(read_csv(args.dispatch_manifest))
    summary_rows = read_csv(args.dispatch_summary)
    return_rows = build_return_rows(summary_rows, read_csv(args.launch_commands))
    write_csv(args.out_dir / "operator_dispatch_assignments.csv", dispatch_rows)
    write_csv(args.out_dir / "operator_return_intake.csv", return_rows)
    write_markdown(args.out_md, dispatch_rows=dispatch_rows, return_rows=return_rows, summary_rows=summary_rows)
    print(f"wrote label-collection operator handoff to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
