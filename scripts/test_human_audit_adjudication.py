#!/usr/bin/env python
"""Regression tests for double-annotation human-audit adjudication analysis."""

from __future__ import annotations

from copy import deepcopy

from analyze_human_audit_adjudication import validate_long_annotations
from finalize_human_audit_adjudication import finalize_labels
from test_human_audit_completion import MODELS, fixture_rows, roster_rows


SECOND_ANNOTATOR = {
    "ar-en": "ar_native_2",
    "es-en": "es_native_2",
    "hi-en": "hi_native_2",
}


def double_roster() -> list[dict[str, str]]:
    rows = roster_rows()
    for row in roster_rows():
        extra = dict(row)
        extra["annotator_id"] = SECOND_ANNOTATOR[row["language_pair"]]
        extra["qualification_notes"] = extra["qualification_notes"].replace("speaker", "second speaker")
        rows.append(extra)
    return rows


def double_annotations() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    annotations, key_rows = fixture_rows()
    out = deepcopy(annotations)
    for row in annotations:
        extra = dict(row)
        extra["annotator_id"] = SECOND_ANNOTATOR[row["language_pair"]]
        out.append(extra)
    return out, key_rows


def require_raises(fn, expected_fragment: str) -> None:
    try:
        fn()
    except AssertionError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected error containing {expected_fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected AssertionError containing {expected_fragment!r}")


def main() -> None:
    annotations, key_rows = double_annotations()
    summary, by_language, by_family, adjudication = validate_long_annotations(
        annotation_rows=annotations,
        key_rows=key_rows,
        roster_rows=double_roster(),
        expected_models=MODELS,
    )
    if summary["audit_items"] != 72 or summary["annotation_rows"] != 144 or summary["annotators"] != 6:
        raise AssertionError(f"unexpected double-annotation summary: {summary}")
    if summary["pass_pairwise_agreement"] != 1.0 or summary["items_with_component_disagreement"] != 0:
        raise AssertionError(f"unexpected perfect agreement summary: {summary}")
    if len(by_language) != 3 or len(by_family) != 4:
        raise AssertionError(f"unexpected grouped summaries: {by_language}, {by_family}")
    if adjudication:
        raise AssertionError(f"perfect agreement should not create adjudication rows: {adjudication}")
    final_rows, source_rows = finalize_labels(
        annotation_rows=annotations,
        key_rows=key_rows,
        roster_rows=double_roster(),
        adjudication_rows_input=[],
        expected_models=MODELS,
    )
    if len(final_rows) != 72 or {row["final_label_source"] for row in source_rows} != {"consensus"}:
        raise AssertionError(f"unexpected consensus finalization: {source_rows[:3]}")

    disagreement = deepcopy(annotations)
    disagreement[72]["human_pass"] = "FALSE"
    disagreement[72]["human_language_pass"] = "FALSE"
    disagreement[72]["human_failure_types"] = "wrong_output_language"
    disagreement[72]["human_notes"] = "Regression-test disagreement."
    disagreement_summary, _, _, disagreement_packet = validate_long_annotations(
        annotation_rows=disagreement,
        key_rows=key_rows,
        roster_rows=double_roster(),
        expected_models=MODELS,
    )
    if disagreement_summary["pass_pairwise_agreement"] != round(71 / 72, 4):
        raise AssertionError(f"unexpected pass agreement after disagreement: {disagreement_summary}")
    if disagreement_summary["items_with_pass_disagreement"] != 1:
        raise AssertionError(f"expected one pass disagreement: {disagreement_summary}")
    if len(disagreement_packet) != 1 or disagreement_packet[0]["audit_id"] != "rpt_audit_001":
        raise AssertionError(f"unexpected adjudication packet: {disagreement_packet}")
    if disagreement_packet[0]["disagreed_components"] != "pass;language;failure_types":
        raise AssertionError(f"unexpected disagreed components: {disagreement_packet[0]}")
    require_raises(
        lambda: finalize_labels(
            annotation_rows=disagreement,
            key_rows=key_rows,
            roster_rows=double_roster(),
            adjudication_rows_input=[],
            expected_models=MODELS,
        ),
        "completed adjudication IDs must equal required disagreement IDs",
    )
    completed_adjudication = [dict(disagreement_packet[0])]
    completed_adjudication[0].update(
        {
            "adjudicator_id": "ar_native_1",
            "adjudicated_pass": "TRUE",
            "adjudicated_language_pass": "TRUE",
            "adjudicated_script_pass": "TRUE",
            "adjudicated_preservation_pass": "TRUE",
            "adjudicated_task_pass": "TRUE",
            "adjudicated_register_locale_pass": "TRUE",
            "adjudicated_failure_types": "",
            "adjudication_notes": "Final label follows annotator ar_native_1.",
        }
    )
    adjudicated_final, adjudicated_sources = finalize_labels(
        annotation_rows=disagreement,
        key_rows=key_rows,
        roster_rows=double_roster(),
        adjudication_rows_input=completed_adjudication,
        expected_models=MODELS,
    )
    if len(adjudicated_final) != 72:
        raise AssertionError(f"unexpected finalized row count: {len(adjudicated_final)}")
    source_by_id = {row["audit_id"]: row for row in adjudicated_sources}
    if source_by_id["rpt_audit_001"]["final_label_source"] != "adjudicated":
        raise AssertionError(f"expected adjudicated source row: {source_by_id['rpt_audit_001']}")
    final_by_id = {row["audit_id"]: row for row in adjudicated_final}
    if final_by_id["rpt_audit_001"]["human_pass"] != "TRUE" or not final_by_id["rpt_audit_001"]["human_notes"].startswith("ADJUDICATED"):
        raise AssertionError(f"unexpected adjudicated final label: {final_by_id['rpt_audit_001']}")

    single_annotations, single_key_rows = fixture_rows()
    require_raises(
        lambda: validate_long_annotations(
            annotation_rows=single_annotations,
            key_rows=single_key_rows,
            roster_rows=roster_rows(),
            expected_models=MODELS,
        ),
        "fewer than 2 annotations",
    )

    duplicate = deepcopy(annotations)
    duplicate[72]["annotator_id"] = duplicate[0]["annotator_id"]
    require_raises(
        lambda: validate_long_annotations(
            annotation_rows=duplicate,
            key_rows=key_rows,
            roster_rows=double_roster(),
            expected_models=MODELS,
        ),
        "duplicate annotation",
    )

    print("human-audit adjudication regression tests passed")


if __name__ == "__main__":
    main()
