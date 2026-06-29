#!/usr/bin/env python
"""Create a native-review launch packet for the v0.3 coverage scaffold."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


EXPECTED_SLICES = (
    "arabic_instruction_arabic_filenames",
    "english_instruction_arabic_content",
    "english_instruction_hindi_content",
    "english_instruction_spanish_content",
    "hindi_english_instruction_hindi_devanagari",
    "spanish_instruction_arabic_quote",
)

REVIEW_FIELDS = [
    "reviewer_id",
    "reviewer_prompt_clear",
    "reviewer_target_language_natural",
    "reviewer_script_expectation_valid",
    "reviewer_preservation_spans_valid",
    "reviewer_known_bad_outputs_valid",
    "reviewer_release_usable",
    "reviewer_issue_types",
    "reviewer_notes",
]

PACKET_FIELDS = [
    "review_id",
    "item_id",
    "coverage_slice",
    "language_pair",
    "instruction_language",
    "content_language",
    "task_family",
    "user_prompt",
    "expected_response_language",
    "expected_script",
    "must_preserve_spans",
    "required_any_markers",
    "forbidden_markers",
    "known_bad_outputs",
    "register_requirement",
    "locale_requirement",
    "notes_for_reviewers",
    *REVIEW_FIELDS,
]

ROSTER_FIELDS = [
    "reviewer_id",
    "coverage_slice",
    "language_pair",
    "target_content_language",
    "can_validate_instruction_language",
    "can_validate_target_language",
    "can_validate_script",
    "qualification_notes",
    "conflict_of_interest",
    "notes",
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def json_list(row: dict[str, Any], field: str) -> str:
    return json.dumps(row.get(field) or [], ensure_ascii=False)


def build_packet_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    packet_rows: list[dict[str, Any]] = []
    for idx, row in enumerate(sorted(rows, key=lambda r: (r["coverage_slice"], r["id"])), start=1):
        packet_rows.append(
            {
                "review_id": f"rpt_v03_native_{idx:03d}",
                "item_id": row["id"],
                "coverage_slice": row["coverage_slice"],
                "language_pair": row["language_pair"],
                "instruction_language": row["instruction_language"],
                "content_language": row["content_language"],
                "task_family": row["task_family"],
                "user_prompt": row["user_prompt"],
                "expected_response_language": row["expected_response_language"],
                "expected_script": row["expected_script"],
                "must_preserve_spans": json_list(row, "must_preserve_spans"),
                "required_any_markers": json_list(row, "required_any_markers"),
                "forbidden_markers": json_list(row, "forbidden_markers"),
                "known_bad_outputs": json_list(row, "known_bad_outputs"),
                "register_requirement": row.get("register_requirement") or "",
                "locale_requirement": row.get("locale_requirement") or "",
                "notes_for_reviewers": row.get("notes_for_annotators", ""),
                **{field: "" for field in REVIEW_FIELDS},
            }
        )
    return packet_rows


def build_roster_template(packet_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for coverage_slice in EXPECTED_SLICES:
        slice_rows = [row for row in packet_rows if row["coverage_slice"] == coverage_slice]
        if not slice_rows:
            continue
        first = slice_rows[0]
        for reviewer_index in (1, 2):
            rows.append(
                {
                    "reviewer_id": f"replace_with_{coverage_slice}_reviewer_{reviewer_index}_id",
                    "coverage_slice": coverage_slice,
                    "language_pair": first["language_pair"],
                    "target_content_language": first["content_language"],
                    "can_validate_instruction_language": "",
                    "can_validate_target_language": "",
                    "can_validate_script": "",
                    "qualification_notes": "",
                    "conflict_of_interest": "",
                    "notes": "",
                }
            )
    return rows


def write_manifest(path: Path, *, benchmark: Path, out_dir: Path, row_count: int) -> None:
    text = f"""# v0.3 Coverage Native-Review Manifest

Generated for `data/benchmark_stress_v0.3_expansion.jsonl`.

Source benchmark: `{benchmark}`
Review rows: {row_count}

This is a launch package for native/near-native review of the synthetic v0.3
coverage scaffold. It is not completed native validation and must not be used
as paper-facing benchmark evidence until the completed review packet and roster
pass validation.

## Launch Files

- Full packet: `{out_dir / "coverage_native_review_packet_v03.csv"}`
- Slice packets: `{out_dir}/coverage_native_review_v03_<coverage_slice>.csv`
- Roster template: `{out_dir / "coverage_native_review_roster_template_v03.csv"}`
- Optional static review sheets: `{out_dir / "review_sheets_v03/index.html"}`
- Launch checklist: `{out_dir / "coverage_native_review_launch_checklist_v03.md"}`

Each coverage slice has 10 rows. The roster template includes two reviewer
slots per slice for the preferred independent-review-plus-adjudication workflow.
Send reviewers only the slice they are qualified to evaluate. For cross-language
slices, each claim-bearing reviewer must be able to judge the target content
language and script; record whether each reviewer can also validate instruction
language clarity.

## Review Fields

Reviewers should fill every TRUE/FALSE field plus issue types and notes when a
row is not release-usable. Allowed `reviewer_issue_types` values are:

- `ambiguous_instruction`
- `unnatural_target_text`
- `wrong_expected_language`
- `script_expectation_problem`
- `preservation_span_problem`
- `known_bad_output_problem`
- `privacy_or_safety_issue`
- `cultural_or_locale_issue`
- `other`

The completion validator requires every failed component to carry its matching
issue code: `reviewer_prompt_clear` -> `ambiguous_instruction`,
`reviewer_target_language_natural` -> `unnatural_target_text`,
`reviewer_script_expectation_valid` -> `script_expectation_problem`,
`reviewer_preservation_spans_valid` -> `preservation_span_problem`, and
`reviewer_known_bad_outputs_valid` -> `known_bad_output_problem`. It also
rejects issue codes that contradict passing components.

## Reproduction

```bash
conda run -n reprompt_tax python scripts/make_coverage_native_review_packet_v03.py
conda run -n reprompt_tax python scripts/validate_coverage_native_review_packet_v03.py
conda run -n reprompt_tax python scripts/make_coverage_native_review_sheets_v03.py
conda run -n reprompt_tax python scripts/validate_coverage_native_review_sheets_v03.py
conda run -n reprompt_tax python scripts/analyze_coverage_native_review_design_v03.py
conda run -n reprompt_tax python scripts/test_coverage_native_review_completion.py
conda run -n reprompt_tax python scripts/test_coverage_native_review_adjudication.py
```

After reviewers complete one independent row per v0.3 item, validate and
summarize the finalized one-row-per-item labels with:

```bash
conda run -n reprompt_tax python scripts/validate_completed_coverage_native_review_v03.py \\
  --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv \\
  --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv \\
  --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv

conda run -n reprompt_tax python scripts/summarize_coverage_native_review_v03.py \\
  --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv \\
  --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv \\
  --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv
```

Preferred stronger workflow: concatenate independent reviewer rows into a
long-format file with duplicate `review_id` values but unique `reviewer_id`
values per item, generate an adjudication packet, fill only the disagreement
rows, and then finalize to the one-row-per-item completed format:

```bash
conda run -n reprompt_tax python scripts/analyze_coverage_native_review_adjudication.py \\
  --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_double_completed.csv \\
  --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv \\
  --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv \\
  --out-dir results/tables/coverage_native_review_v03_adjudication \\
  --out-md paper/coverage_native_review_adjudication_v03.md

# After filling the generated coverage_native_review_adjudication_packet.csv:
conda run -n reprompt_tax python scripts/finalize_coverage_native_review_adjudication.py \\
  --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_double_completed.csv \\
  --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv \\
  --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv \\
  --adjudication results/tables/coverage_native_review_v03_adjudication/coverage_native_review_adjudication_packet.csv \\
  --out data/coverage_native_review_v03/coverage_native_review_packet_v03_adjudicated_completed.csv
```

Do not claim native validation has been completed until a completed packet and
filled qualified-reviewer roster pass the future completion gate.
"""
    path.write_text(text, encoding="utf-8")


def write_launch_checklist(path: Path, *, out_dir: Path, row_count: int) -> None:
    text = f"""# v0.3 Coverage Native-Review Launch Checklist

This checklist launches native/near-native review for the 60-row synthetic
v0.3 coverage scaffold. It is prepared but not completed native validation.

## Minimum Launch

- Recruit at least two qualified reviewers for each of the six coverage slices.
- Send each reviewer only their relevant slice CSV from `{out_dir}` or the
  matching static HTML sheet from `{out_dir / "review_sheets_v03"}`.
- Copy `coverage_native_review_roster_template_v03.csv` to
  `coverage_native_review_roster_v03.csv` and replace placeholder reviewer IDs.
- Require `can_validate_target_language`, `can_validate_script`, and
  `conflict_of_interest` to be filled for every reviewer.
- For cross-language slices, record whether the reviewer can validate the
  instruction language; if not, add a second qualified reviewer or keep the
  claim limited to target-language/content validity.
- Ask reviewers to include the matching `reviewer_issue_types` code for every
  component field marked `FALSE`, and not to list an issue code for a component
  marked `TRUE`.
- Combine independently completed slice files as either
  `coverage_native_review_packet_v03_completed.csv` with all {row_count}
  finalized rows or, preferably, as
  `coverage_native_review_packet_v03_double_completed.csv` with two rows per
  item before adjudication.
- Merge completed slice exports with:

```bash
conda run -n reprompt_tax python scripts/merge_review_exports.py \\
  --mode coverage_native_review \\
  --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv \\
  --out data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv \\
  --inputs \\
  data/coverage_native_review_v03/coverage_native_review_v03_arabic_instruction_arabic_filenames_completed.csv \\
  data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_arabic_content_completed.csv \\
  data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_hindi_content_completed.csv \\
  data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_spanish_content_completed.csv \\
  data/coverage_native_review_v03/coverage_native_review_v03_hindi_english_instruction_hindi_devanagari_completed.csv \\
  data/coverage_native_review_v03/coverage_native_review_v03_spanish_instruction_arabic_quote_completed.csv
```

For two independent labels per item, include every returned export after
`--inputs` and add `--labels-per-item 2`, writing to
`coverage_native_review_packet_v03_double_completed.csv`.

## Claim Rule

Do not claim native validation has been completed until the completed packet
and filled roster pass validation. Until then, describe this as a launch-ready
review packet for synthetic v0.3 rows only.

## Completion Commands

Generate reviewer-facing static sheets if using browser-based local export:

```bash
conda run -n reprompt_tax python scripts/make_coverage_native_review_sheets_v03.py
conda run -n reprompt_tax python scripts/validate_coverage_native_review_sheets_v03.py
```

```bash
conda run -n reprompt_tax python scripts/validate_completed_coverage_native_review_v03.py \\
  --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv \\
  --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv \\
  --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv

conda run -n reprompt_tax python scripts/summarize_coverage_native_review_v03.py \\
  --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv \\
  --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv \\
  --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv
```

## Preferred Adjudication Commands

```bash
conda run -n reprompt_tax python scripts/analyze_coverage_native_review_adjudication.py \\
  --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_double_completed.csv \\
  --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv \\
  --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv \\
  --out-dir results/tables/coverage_native_review_v03_adjudication \\
  --out-md paper/coverage_native_review_adjudication_v03.md

conda run -n reprompt_tax python scripts/finalize_coverage_native_review_adjudication.py \\
  --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_double_completed.csv \\
  --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv \\
  --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv \\
  --adjudication results/tables/coverage_native_review_v03_adjudication/coverage_native_review_adjudication_packet.csv \\
  --out data/coverage_native_review_v03/coverage_native_review_packet_v03_adjudicated_completed.csv
```
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, default=Path("data/benchmark_stress_v0.3_expansion.jsonl"))
    parser.add_argument("--out-dir", type=Path, default=Path("data/coverage_native_review_v03"))
    args = parser.parse_args()

    benchmark_rows = load_jsonl(args.benchmark)
    packet_rows = build_packet_rows(benchmark_rows)
    write_csv(args.out_dir / "coverage_native_review_packet_v03.csv", packet_rows, PACKET_FIELDS)
    write_csv(args.out_dir / "coverage_native_review_roster_template_v03.csv", build_roster_template(packet_rows), ROSTER_FIELDS)

    for coverage_slice in EXPECTED_SLICES:
        slice_rows = [row for row in packet_rows if row["coverage_slice"] == coverage_slice]
        write_csv(args.out_dir / f"coverage_native_review_v03_{coverage_slice}.csv", slice_rows, PACKET_FIELDS)

    write_manifest(args.out_dir / "coverage_native_review_manifest_v03.md", benchmark=args.benchmark, out_dir=args.out_dir, row_count=len(packet_rows))
    write_launch_checklist(args.out_dir / "coverage_native_review_launch_checklist_v03.md", out_dir=args.out_dir, row_count=len(packet_rows))
    print(f"wrote {len(packet_rows)} v0.3 native-review rows to {args.out_dir}")


if __name__ == "__main__":
    main()
