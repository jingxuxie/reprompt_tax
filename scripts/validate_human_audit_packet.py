#!/usr/bin/env python
"""Validate launch readiness of RePromptTax human-audit packets."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


LANGUAGE_PAIRS = ("ar-en", "es-en", "hi-en")
TASK_FAMILIES = (
    "editing_preservation",
    "output_language_inference",
    "quote_preservation",
    "script_register_locale",
)
MODELS = ("gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano")
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
PACKET_FORBIDDEN_FIELDS = {
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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def parse_json_list(value: str, *, row_id: str, field: str) -> list[Any]:
    try:
        parsed = json.loads(value or "[]")
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{row_id} has invalid JSON in {field}") from exc
    require(isinstance(parsed, list), f"{row_id} field {field} must be a JSON list")
    return parsed


def validate_packet_rows(packet_rows: list[dict[str, str]]) -> None:
    require(len(packet_rows) == 72, f"expected 72 packet rows, found {len(packet_rows)}")
    require(packet_rows, "packet is empty")
    fields = set(packet_rows[0].keys())
    require(not PACKET_FORBIDDEN_FIELDS.intersection(fields), f"packet leaks private fields: {PACKET_FORBIDDEN_FIELDS.intersection(fields)}")
    for field in ANNOTATION_FIELDS:
        require(field in fields, f"packet missing annotation field {field}")

    ids = [row["audit_id"] for row in packet_rows]
    require(len(ids) == len(set(ids)), "packet has duplicate audit_id values")
    require(ids == sorted(ids), "packet audit_id values are not sorted")

    counts = Counter((row["language_pair"], row["task_family"]) for row in packet_rows)
    expected_counts = {(lang, family): 6 for lang in LANGUAGE_PAIRS for family in TASK_FAMILIES}
    require(dict(counts) == expected_counts, f"unexpected packet language/family counts: {counts}")

    for row in packet_rows:
        audit_id = row["audit_id"]
        require(row["language_pair"] in LANGUAGE_PAIRS, f"{audit_id} has unexpected language_pair")
        require(row["task_family"] in TASK_FAMILIES, f"{audit_id} has unexpected task_family")
        for field in ("user_prompt", "assistant_response", "expected_response_language", "expected_script"):
            require(row.get(field, "").strip(), f"{audit_id} missing {field}")
        for field in ("must_preserve_spans", "known_bad_outputs"):
            parse_json_list(row.get(field, ""), row_id=audit_id, field=field)
        for field in ANNOTATION_FIELDS:
            require(row.get(field, "") == "", f"{audit_id} annotation field {field} is not blank in launch packet")


def validate_key_rows(key_rows: list[dict[str, str]], packet_rows: list[dict[str, str]]) -> None:
    require(len(key_rows) == 72, f"expected 72 answer-key rows, found {len(key_rows)}")
    key_ids = [row["audit_id"] for row in key_rows]
    packet_ids = [row["audit_id"] for row in packet_rows]
    require(len(key_ids) == len(set(key_ids)), "answer key has duplicate audit_id values")
    require(set(key_ids) == set(packet_ids), "packet and answer-key audit IDs differ")

    key_by_id = {row["audit_id"]: row for row in key_rows}
    for packet_row in packet_rows:
        key_row = key_by_id[packet_row["audit_id"]]
        for field in ("language_pair", "task_family"):
            require(packet_row[field] == key_row[field], f"{packet_row['audit_id']} packet/key mismatch for {field}")

    strata = Counter((row["model"], row["condition"], row["task_family"], row["language_pair"]) for row in key_rows)
    expected_strata = {
        (model, condition, family, lang): 1
        for model in MODELS
        for condition in CONDITIONS
        for family in TASK_FAMILIES
        for lang in LANGUAGE_PAIRS
    }
    require(dict(strata) == expected_strata, f"answer key is not one row per model/condition/family/language stratum: {strata}")
    require(all(row["turn"] == "0" for row in key_rows), "human audit should cover only first-turn outputs")
    for row in key_rows:
        parse_json_list(row.get("auto_failure_types", ""), row_id=row["audit_id"], field="auto_failure_types")


def validate_slices(out_dir: Path, packet_rows: list[dict[str, str]], packet_version: str) -> None:
    full_by_lang = {
        lang: [row for row in packet_rows if row["language_pair"] == lang]
        for lang in LANGUAGE_PAIRS
    }
    for lang in LANGUAGE_PAIRS:
        path = out_dir / f"human_audit_packet_{packet_version}_{lang}.csv"
        require(path.exists(), f"missing language slice {path}")
        rows = read_csv(path)
        require(len(rows) == 24, f"expected 24 rows in {path}, found {len(rows)}")
        require(rows == full_by_lang[lang], f"language slice {path} does not match full packet subset")
        require(not PACKET_FORBIDDEN_FIELDS.intersection(rows[0].keys()), f"language slice leaks private fields: {path}")


def validate_smoke_file(out_dir: Path, packet_version: str) -> None:
    path = out_dir / f"human_audit_packet_{packet_version}_smoke_completed.csv"
    if not path.exists():
        return
    rows = read_csv(path)
    require(len(rows) == 72, f"expected 72 smoke rows, found {len(rows)}")
    require(all(row.get("human_notes", "").startswith("SMOKE ONLY:") for row in rows), "smoke file must be clearly marked as smoke-only")


def validate_roster_template(out_dir: Path, packet_version: str) -> None:
    path = out_dir / f"human_audit_annotator_roster_template_{packet_version}.csv"
    require(path.exists(), f"missing annotator roster template {path}")
    rows = read_csv(path)
    require(len(rows) == 3, f"expected 3 annotator roster template rows, found {len(rows)}")
    require({row["language_pair"] for row in rows} == set(LANGUAGE_PAIRS), "roster template must include one row per language pair")
    for row in rows:
        require(row["annotator_id"].startswith("replace_with_"), f"roster template annotator_id should be a placeholder for {row['language_pair']}")
        for field in ("native_or_near_native", "can_validate_script", "qualification_notes", "conflict_of_interest"):
            require(row.get(field, "") == "", f"roster template field {field} should be blank before completion")


def validate_launch_checklist(out_dir: Path, packet_version: str) -> None:
    path = out_dir / f"human_audit_launch_checklist_{packet_version}.md"
    require(path.exists(), f"missing human audit launch checklist {path}")
    text = path.read_text(encoding="utf-8")
    required_phrases = [
        "Minimum Launch",
        "Do not send `human_audit_answer_key_",
        "human_audit_annotator_roster_",
        "validate_completed_human_audit.py",
        "summarize_human_audit.py",
        "Do not claim native-speaker or human validation",
    ]
    for phrase in required_phrases:
        require(phrase in text, f"human audit launch checklist missing phrase: {phrase}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("data/human_audit"))
    parser.add_argument("--packet-version", default="v0.2")
    args = parser.parse_args()

    packet_path = args.out_dir / f"human_audit_packet_{args.packet_version}.csv"
    key_path = args.out_dir / f"human_audit_answer_key_{args.packet_version}.csv"
    require(packet_path.exists(), f"missing packet {packet_path}")
    require(key_path.exists(), f"missing answer key {key_path}")

    packet_rows = read_csv(packet_path)
    key_rows = read_csv(key_path)
    validate_packet_rows(packet_rows)
    validate_key_rows(key_rows, packet_rows)
    validate_slices(args.out_dir, packet_rows, args.packet_version)
    validate_roster_template(args.out_dir, args.packet_version)
    validate_launch_checklist(args.out_dir, args.packet_version)
    validate_smoke_file(args.out_dir, args.packet_version)
    print(f"human-audit packet validation passed for {args.out_dir}")


if __name__ == "__main__":
    main()
