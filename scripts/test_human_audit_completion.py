#!/usr/bin/env python
"""Regression tests for completed human-audit validation."""

from __future__ import annotations

from copy import deepcopy

from validate_completed_human_audit import validate_annotations


LANGUAGE_PAIRS = ("ar-en", "es-en", "hi-en")
TASK_FAMILIES = (
    "editing_preservation",
    "output_language_inference",
    "quote_preservation",
    "script_register_locale",
)
MODELS = ("gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano")
CONDITIONS = ("baseline", "contract")


def roster_rows() -> list[dict[str, str]]:
    return [
        {
            "annotator_id": "ar_native_1",
            "language_pair": "ar-en",
            "native_or_near_native": "TRUE",
            "can_validate_script": "TRUE",
            "qualification_notes": "Native Arabic speaker with professional English fluency.",
            "conflict_of_interest": "FALSE",
            "notes": "",
        },
        {
            "annotator_id": "es_native_1",
            "language_pair": "es-en",
            "native_or_near_native": "TRUE",
            "can_validate_script": "TRUE",
            "qualification_notes": "Native Spanish speaker with professional English fluency.",
            "conflict_of_interest": "FALSE",
            "notes": "",
        },
        {
            "annotator_id": "hi_native_1",
            "language_pair": "hi-en",
            "native_or_near_native": "TRUE",
            "can_validate_script": "TRUE",
            "qualification_notes": "Native Hindi/Hinglish speaker with professional English fluency.",
            "conflict_of_interest": "FALSE",
            "notes": "",
        },
    ]


def fixture_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    annotations: list[dict[str, str]] = []
    key_rows: list[dict[str, str]] = []
    annotator_by_language = {
        "ar-en": "ar_native_1",
        "es-en": "es_native_1",
        "hi-en": "hi_native_1",
    }
    idx = 1
    for model in MODELS:
        for condition in CONDITIONS:
            for family in TASK_FAMILIES:
                for language_pair in LANGUAGE_PAIRS:
                    audit_id = f"rpt_audit_{idx:03d}"
                    annotations.append(
                        {
                            "audit_id": audit_id,
                            "language_pair": language_pair,
                            "task_family": family,
                            "annotator_id": annotator_by_language[language_pair],
                            "human_pass": "TRUE",
                            "human_language_pass": "TRUE",
                            "human_script_pass": "TRUE",
                            "human_preservation_pass": "TRUE",
                            "human_task_pass": "TRUE",
                            "human_register_locale_pass": "TRUE",
                            "human_failure_types": "",
                            "human_notes": "",
                        }
                    )
                    key_rows.append(
                        {
                            "audit_id": audit_id,
                            "language_pair": language_pair,
                            "task_family": family,
                            "model": model,
                            "condition": condition,
                            "turn": "0",
                            "auto_pass": "TRUE",
                            "auto_language_pass": "TRUE",
                            "auto_script_pass": "TRUE",
                            "auto_preservation_pass": "TRUE",
                            "auto_task_pass": "TRUE",
                            "auto_register_locale_pass": "TRUE",
                            "auto_failure_types": "[]",
                        }
                    )
                    idx += 1
    return annotations, key_rows


def require_raises(fn, expected_fragment: str) -> None:
    try:
        fn()
    except AssertionError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected error containing {expected_fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected AssertionError containing {expected_fragment!r}")


def main() -> None:
    annotations, key_rows = fixture_rows()
    summary = validate_annotations(
        annotation_rows=annotations,
        key_rows=key_rows,
        roster_rows=roster_rows(),
        allow_smoke=False,
    )
    if summary["rows"] != 72 or summary["annotators"] != 3:
        raise AssertionError(f"unexpected validation summary: {summary}")

    require_raises(
        lambda: validate_annotations(
            annotation_rows=annotations,
            key_rows=key_rows,
            roster_rows=None,
            allow_smoke=False,
        ),
        "annotator roster is empty",
    )

    placeholder_roster = deepcopy(roster_rows())
    placeholder_roster[0]["annotator_id"] = "replace_with_ar_en_annotator_id"
    require_raises(
        lambda: validate_annotations(
            annotation_rows=annotations,
            key_rows=key_rows,
            roster_rows=placeholder_roster,
            allow_smoke=False,
        ),
        "placeholder ID",
    )

    wrong_language = deepcopy(annotations)
    wrong_language[0]["annotator_id"] = "es_native_1"
    require_raises(
        lambda: validate_annotations(
            annotation_rows=wrong_language,
            key_rows=key_rows,
            roster_rows=roster_rows(),
            allow_smoke=False,
        ),
        "not qualified for ar-en",
    )

    smoke_summary = validate_annotations(
        annotation_rows=annotations,
        key_rows=key_rows,
        roster_rows=None,
        allow_smoke=True,
    )
    if smoke_summary["annotators"] != 0:
        raise AssertionError(f"smoke validation should not count annotators: {smoke_summary}")

    print("human-audit completion regression tests passed")


if __name__ == "__main__":
    main()
