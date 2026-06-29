#!/usr/bin/env python
"""Validate the current-model human-audit launch packet and design audit."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


AUDIT_DIR = Path("data/current_model_human_audit")
VERSION = "v0.2_current_gpt5"
PACKET = AUDIT_DIR / f"human_audit_packet_{VERSION}.csv"
ANSWER_KEY = AUDIT_DIR / f"human_audit_answer_key_{VERSION}.csv"
REVIEW_SHEETS_DIR = AUDIT_DIR / f"review_sheets_{VERSION}"
DESIGN_DIR = Path("results/tables/current_model_human_audit_v02_design")
DESIGN_REPORT = Path("paper/current_model_human_audit_design_v02.md")

LANGUAGE_PAIRS = ("ar-en", "es-en", "hi-en")
TASK_FAMILIES = (
    "editing_preservation",
    "output_language_inference",
    "quote_preservation",
    "script_register_locale",
)
MODELS = ("gpt-5.4-mini", "gpt-5.5")
CONDITIONS = ("baseline", "contract")
ANNOTATION_FIELDS = (
    "annotator_id",
    "human_pass",
    "human_language_pass",
    "human_script_pass",
    "human_preservation_pass",
    "human_task_pass",
    "human_register_locale_pass",
    "human_failure_types",
    "human_notes",
)
PRIVATE_FIELDS = {
    "item_id",
    "model",
    "condition",
    "turn",
    "auto_pass",
    "auto_language_pass",
    "auto_script_pass",
    "auto_preservation_pass",
    "auto_task_pass",
    "auto_register_locale_pass",
    "auto_failure_types",
}
PRIVATE_SHEET_MARKERS = (
    "item_id",
    "auto_pass",
    "auto_language_pass",
    "auto_script_pass",
    "auto_preservation_pass",
    "auto_task_pass",
    "auto_register_locale_pass",
    "auto_failure_types",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes", "pass"}


def parse_json_list(value: str, *, row_id: str, field: str) -> list[Any]:
    try:
        parsed = json.loads(value or "[]")
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{row_id} has invalid JSON in {field}") from exc
    require(isinstance(parsed, list), f"{row_id} {field} should be a JSON list")
    return parsed


def validate_packet(packet_rows: list[dict[str, str]], key_rows: list[dict[str, str]]) -> None:
    expected_rows = len(LANGUAGE_PAIRS) * len(TASK_FAMILIES) * len(MODELS) * len(CONDITIONS)
    require(len(packet_rows) == expected_rows, f"expected {expected_rows} packet rows, found {len(packet_rows)}")
    require(len(key_rows) == expected_rows, f"expected {expected_rows} answer-key rows, found {len(key_rows)}")
    require(not PRIVATE_FIELDS.intersection(packet_rows[0]), f"packet leaks private fields: {PRIVATE_FIELDS.intersection(packet_rows[0])}")
    require({row["audit_id"] for row in packet_rows} == {row["audit_id"] for row in key_rows}, "packet/key audit IDs differ")

    for row in packet_rows:
        for field in ANNOTATION_FIELDS:
            require(row.get(field, "") == "", f"{row['audit_id']} launch annotation field {field} is not blank")
        for field in ("must_preserve_spans", "known_bad_outputs"):
            parse_json_list(row.get(field, ""), row_id=row["audit_id"], field=field)

    strata = Counter((row["model"], row["condition"], row["language_pair"], row["task_family"]) for row in key_rows)
    expected_strata = {
        (model, condition, language_pair, task_family): 1
        for model in MODELS
        for condition in CONDITIONS
        for language_pair in LANGUAGE_PAIRS
        for task_family in TASK_FAMILIES
    }
    require(dict(strata) == expected_strata, f"unexpected current-model audit strata: {strata}")
    require(all(row["turn"] == "0" for row in key_rows), "current-model audit should cover first turns only")

    auto_fail_rows = [row for row in key_rows if not parse_bool(row["auto_pass"])]
    require(len(auto_fail_rows) == 16, f"expected 16 failure-enriched auto-fail rows, found {len(auto_fail_rows)}")
    require(
        Counter((row["model"], row["condition"]) for row in auto_fail_rows)
        == Counter(
            {
                ("gpt-5.4-mini", "baseline"): 5,
                ("gpt-5.4-mini", "contract"): 6,
                ("gpt-5.5", "baseline"): 4,
                ("gpt-5.5", "contract"): 1,
            }
        ),
        "unexpected auto-fail distribution by current model/condition",
    )
    for row in auto_fail_rows:
        failure_types = parse_json_list(row.get("auto_failure_types", ""), row_id=row["audit_id"], field="auto_failure_types")
        require(failure_types, f"{row['audit_id']} auto-fail row lacks failure types")


def validate_slices(packet_rows: list[dict[str, str]]) -> None:
    for language_pair in LANGUAGE_PAIRS:
        path = AUDIT_DIR / f"human_audit_packet_{VERSION}_{language_pair}.csv"
        rows = read_csv(path)
        expected = [row for row in packet_rows if row["language_pair"] == language_pair]
        require(len(rows) == 16, f"{path} should contain 16 rows")
        require(rows == expected, f"{path} does not match the full packet language subset")


def validate_review_sheets(packet_rows: list[dict[str, str]]) -> None:
    for language_pair in LANGUAGE_PAIRS:
        path = REVIEW_SHEETS_DIR / f"human_audit_review_sheet_{VERSION}_{language_pair}.html"
        require(path.exists(), f"missing review sheet {path}")
        text = path.read_text(encoding="utf-8")
        for marker in PRIVATE_SHEET_MARKERS:
            require(marker not in text, f"{path} leaks private marker {marker}")
        match = re.search(r'<script id="audit-data" type="application/json">(.*?)</script>', text, flags=re.DOTALL)
        require(match is not None, f"{path} missing audit-data JSON")
        rows = json.loads(match.group(1).replace("<\\/", "</"))
        expected_ids = [row["audit_id"] for row in packet_rows if row["language_pair"] == language_pair]
        require([row["audit_id"] for row in rows] == expected_ids, f"{path} audit IDs do not match packet")


def validate_design_report() -> None:
    summary_rows = read_csv(DESIGN_DIR / "human_audit_design_summary.csv")
    require(len(summary_rows) == 1, "expected one current-model human-audit design summary row")
    summary = summary_rows[0]
    expected = {
        "packet_rows": "48",
        "answer_key_rows": "48",
        "models": "2",
        "conditions": "2",
        "model_condition_language_family_strata": "48",
        "auto_pass_rows": "32",
        "auto_fail_rows": "16",
    }
    for field, value in expected.items():
        require(summary[field] == value, f"design summary mismatch for {field}: expected {value}, got {summary[field]}")

    text = DESIGN_REPORT.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required_phrases = [
        "Current-Model Human Audit Design Audit",
        "not completed human validation",
        "packet contains no private model, condition, item-id, or automatic-label fields",
        "48 strata total",
        "Completed native/near-native annotation is still required",
    ]
    for phrase in required_phrases:
        require(phrase in normalized, f"current-model human-audit design report missing phrase: {phrase}")


def validate_manifest() -> None:
    manifest = AUDIT_DIR / f"audit_manifest_{VERSION}.md"
    checklist = AUDIT_DIR / f"human_audit_launch_checklist_{VERSION}.md"
    roster = AUDIT_DIR / f"human_audit_annotator_roster_template_{VERSION}.csv"
    for path in (manifest, checklist, roster, REVIEW_SHEETS_DIR / "README.md", REVIEW_SHEETS_DIR / "index.html"):
        require(path.exists(), f"missing current-model human-audit launch artifact {path}")
    manifest_text = manifest.read_text(encoding="utf-8")
    for phrase in (
        "gpt-5.4-mini",
        "gpt-5.5",
        "preferring automatic failures",
        "48 rows",
        "--expected-models gpt-5.4-mini,gpt-5.5",
        "Do not send this to annotators",
    ):
        require(phrase in manifest_text, f"current-model human-audit manifest missing phrase: {phrase}")
    checklist_text = checklist.read_text(encoding="utf-8")
    require(
        "--expected-models gpt-5.4-mini,gpt-5.5" in checklist_text,
        "current-model human-audit checklist missing expected-models completion argument",
    )
    require(
        "matching `human_failure_types` code" in checklist_text,
        "current-model human-audit checklist missing failure-type consistency rule",
    )


def main() -> None:
    packet_rows = read_csv(PACKET)
    key_rows = read_csv(ANSWER_KEY)
    validate_packet(packet_rows, key_rows)
    validate_slices(packet_rows)
    validate_review_sheets(packet_rows)
    validate_design_report()
    validate_manifest()
    print("current-model human-audit packet validation passed")


if __name__ == "__main__":
    main()
