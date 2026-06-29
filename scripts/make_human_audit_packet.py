#!/usr/bin/env python
"""Create blinded human-audit packets for RePromptTax outputs."""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any


ANNOTATION_FIELDS = [
    "annotator_id",
    "human_pass",
    "human_language_pass",
    "human_script_pass",
    "human_preservation_pass",
    "human_task_pass",
    "human_register_locale_pass",
    "human_failure_types",
    "human_notes",
]

ROSTER_FIELDS = [
    "annotator_id",
    "language_pair",
    "native_or_near_native",
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
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_roster_template(path: Path) -> None:
    rows = [
        {
            "annotator_id": "replace_with_ar_en_annotator_id",
            "language_pair": "ar-en",
            "native_or_near_native": "",
            "can_validate_script": "",
            "qualification_notes": "",
            "conflict_of_interest": "",
            "notes": "",
        },
        {
            "annotator_id": "replace_with_es_en_annotator_id",
            "language_pair": "es-en",
            "native_or_near_native": "",
            "can_validate_script": "",
            "qualification_notes": "",
            "conflict_of_interest": "",
            "notes": "",
        },
        {
            "annotator_id": "replace_with_hi_en_annotator_id",
            "language_pair": "hi-en",
            "native_or_near_native": "",
            "can_validate_script": "",
            "qualification_notes": "",
            "conflict_of_interest": "",
            "notes": "",
        },
    ]
    write_csv(path, rows, ROSTER_FIELDS)


def write_manifest(
    *,
    path: Path,
    version: str,
    benchmark: Path,
    scores: list[Path],
    seed: int,
    row_count: int,
    packet_rows: list[dict[str, Any]],
    key_rows: list[dict[str, Any]],
    prefer_failures: bool,
) -> None:
    out_dir = path.parent
    language_counts = {
        language_pair: sum(row["language_pair"] == language_pair for row in packet_rows)
        for language_pair in sorted({row["language_pair"] for row in packet_rows})
    }
    language_table = "\n".join(
        f"| {language_pair} | `human_audit_packet_{version}_{language_pair}.csv` | {count} |"
        for language_pair, count in language_counts.items()
    )
    score_lines = "\n".join(f"- `{score}`" for score in scores)
    models = sorted({row["model"] for row in key_rows})
    conditions = sorted({row["condition"] for row in key_rows})
    task_families = sorted({row["task_family"] for row in key_rows})
    language_pairs = sorted(language_counts)
    rows_per_language_task = len(models) * len(conditions)
    expected_models_arg = ",".join(models)
    selection_rule = (
        "one first-turn row per model/condition/language/family stratum, preferring automatic failures when a stratum contains at least one failure"
        if prefer_failures
        else "one seeded first-turn row per model/condition/language/family stratum"
    )
    text = f"""# RePromptTax Human Audit Manifest {version}

Generated for the current paper-facing full RePromptTax-Stress-v0.2 result.

Source benchmark: `{benchmark}`
Source scores:
{score_lines}
Sampling seed: `{seed}`
Selection rule: {selection_rule}.

## Launch Files

Send annotators only the language slice they can validate:

| Language slice | File | Rows |
|---|---|---:|
{language_table}

The full blinded packet is `human_audit_packet_{version}.csv` with {row_count} rows.
Reviewer-facing static HTML sheets are available under
`review_sheets_{version}/`; they are generated from the blinded packet and
support local CSV export without revealing the answer key.
The annotator roster template is
`human_audit_annotator_roster_template_{version}.csv`; copy it to
`human_audit_annotator_roster_{version}.csv` and fill one qualified annotator
row per language slice before claiming human/native-speaker validation.

## Private Files

Do not send this to annotators:

- `human_audit_answer_key_{version}.csv`

The answer key maps audit IDs to item IDs, model names, prompt conditions, and
automatic labels.

## Balance

The full packet contains:

- {len(language_pairs)} language pairs,
- {len(task_families)} task families,
- {len(models)} models: {", ".join(f"`{model}`" for model in models)},
- {len(conditions)} prompt conditions: {", ".join(f"`{condition}`" for condition in conditions)},
- 1 first-turn output per language/model/condition/family stratum.

Each language slice contains {rows_per_language_task} rows per task family.

## Required Validation Before Launch

```bash
conda run -n reprompt_tax python scripts/validate_human_audit_packet.py \\
  --out-dir {out_dir} \\
  --packet-version {version} \\
  --expected-models {expected_models_arg}

conda run -n reprompt_tax python scripts/analyze_human_audit_design.py \\
  --packet {out_dir}/human_audit_packet_{version}.csv \\
  --answer-key {out_dir}/human_audit_answer_key_{version}.csv \\
  --out-dir results/tables/human_audit_{version}_design \\
  --out-md paper/human_audit_design_audit_{version.replace(".", "")}.md \\
  --expected-models {expected_models_arg}

conda run -n reprompt_tax python scripts/make_human_audit_review_sheets.py \\
  --packet {out_dir}/human_audit_packet_{version}.csv \\
  --out-dir {out_dir}/review_sheets_{version} \\
  --packet-version {version}

conda run -n reprompt_tax python scripts/validate_human_audit_review_sheets.py \\
  --packet {out_dir}/human_audit_packet_{version}.csv \\
  --out-dir {out_dir}/review_sheets_{version} \\
  --packet-version {version}
```

This checks:

- no private model, condition, item, or auto-label fields leak into annotator packets,
- annotation fields are blank in launch packets,
- language slices exactly match the corresponding full-packet subsets,
- each language/task cell and model/condition/task/language stratum is balanced,
- JSON-list fields are parseable,
- any smoke-only artifacts are explicitly marked,
- the selected audit rows include both automatic passes and failures before annotation.
- generated static review sheets cover all audit IDs without private fields.

## Completion Gate

After annotators fill the CSV fields, summarize labels with:

```bash
conda run -n reprompt_tax python scripts/validate_completed_human_audit.py \\
  --annotations {out_dir}/human_audit_packet_{version}_completed.csv \\
  --answer-key {out_dir}/human_audit_answer_key_{version}.csv \\
  --annotator-roster {out_dir}/human_audit_annotator_roster_{version}.csv \\
  --expected-models {expected_models_arg}

conda run -n reprompt_tax python scripts/summarize_human_audit.py \\
  --annotations {out_dir}/human_audit_packet_{version}_completed.csv \\
  --answer-key {out_dir}/human_audit_answer_key_{version}.csv \\
  --out-dir results/tables/human_audit_{version}
```

`summarize_human_audit.py` fails on incomplete files by default. Use
`--allow-partial` only to debug partially returned batches, not for
paper-facing validation claims.

Optional stronger two-annotator workflow: concatenate independently completed
annotation rows into a long-format file with duplicate `audit_id` values but
unique `annotator_id` values per item, then compute inter-annotator agreement
and generate a blinded adjudication packet for disagreements:

```bash
conda run -n reprompt_tax python scripts/analyze_human_audit_adjudication.py \\
  --annotations {out_dir}/human_audit_packet_{version}_double_completed.csv \\
  --answer-key {out_dir}/human_audit_answer_key_{version}.csv \\
  --annotator-roster {out_dir}/human_audit_annotator_roster_{version}.csv \\
  --expected-models {expected_models_arg} \\
  --out-dir results/tables/human_audit_{version}_adjudication \\
  --out-md paper/human_audit_adjudication_{version.replace(".", "")}.md

# After filling results/tables/human_audit_{version}_adjudication/human_audit_adjudication_packet.csv:
conda run -n reprompt_tax python scripts/finalize_human_audit_adjudication.py \\
  --annotations {out_dir}/human_audit_packet_{version}_double_completed.csv \\
  --answer-key {out_dir}/human_audit_answer_key_{version}.csv \\
  --annotator-roster {out_dir}/human_audit_annotator_roster_{version}.csv \\
  --adjudication results/tables/human_audit_{version}_adjudication/human_audit_adjudication_packet.csv \\
  --expected-models {expected_models_arg} \\
  --out {out_dir}/human_audit_packet_{version}_adjudicated_completed.csv
```

Strong final paper claims should wait for completed human/native-speaker labels.
Completed claims also require a filled annotator roster with native or
near-native language competence, script competence, and no conflict of interest
for every annotator ID used in the completed packet.
Any smoke-completed file is only a plumbing test and must not be used for final
claims.
"""
    path.write_text(text, encoding="utf-8")


def write_launch_checklist(*, path: Path, version: str, row_count: int, expected_models: list[str]) -> None:
    out_dir = path.parent
    expected_models_arg = ",".join(expected_models)
    text = f"""# RePromptTax Human Audit Launch Checklist {version}

This checklist is for launching the native/near-native validation audit. It is
not a completed validation result.

## Minimum Launch

- Recruit one qualified annotator for each language slice:
  - Arabic-English: `human_audit_packet_{version}_ar-en.csv`
  - Spanish-English: `human_audit_packet_{version}_es-en.csv`
  - Hindi-English: `human_audit_packet_{version}_hi-en.csv`
- Send each annotator only their language slice and the public guide
  `docs/human_audit_guide.md`.
- Optional: send the matching static HTML sheet from
  `review_sheets_{version}/` instead of the raw CSV slice; it exports the same
  completed CSV format locally in the annotator's browser.
- Do not send `human_audit_answer_key_{version}.csv`.
- Ask annotators to fill all annotation columns in their CSV slice and preserve
  the original row order and `audit_id` values.
- Ask annotators to include the matching `human_failure_types` code for every
  component field marked `FALSE`, and not to list a failure code for a
  component marked `TRUE`.
- Copy `human_audit_annotator_roster_template_{version}.csv` to
  `human_audit_annotator_roster_{version}.csv` and replace every placeholder
  row with the real annotator ID, language pair, qualifications, script
  competence, and conflict-of-interest status.

## Qualification Check

Each roster row used for claims must satisfy:

- `native_or_near_native` is TRUE,
- `can_validate_script` is TRUE,
- `conflict_of_interest` is FALSE,
- `qualification_notes` is non-empty,
- the annotator's `language_pair` matches every row they labeled.

## Files To Combine After Annotation

The completed file should be named
`human_audit_packet_{version}_completed.csv` and should contain all {row_count}
audit rows. If annotators work from language slices or static HTML exports,
merge the completed slice rows with:

```bash
conda run -n reprompt_tax python scripts/merge_review_exports.py \\
  --mode human_audit \\
  --launch-packet {out_dir}/human_audit_packet_{version}.csv \\
  --out {out_dir}/human_audit_packet_{version}_completed.csv \\
  --inputs \\
  {out_dir}/human_audit_packet_{version}_ar-en_completed.csv \\
  {out_dir}/human_audit_packet_{version}_es-en_completed.csv \\
  {out_dir}/human_audit_packet_{version}_hi-en_completed.csv
```

For two independent labels per item, include every returned export after
`--inputs` and add `--labels-per-item 2`, writing to
`human_audit_packet_{version}_double_completed.csv`.

## Completion Commands

```bash
conda run -n reprompt_tax python scripts/validate_completed_human_audit.py \\
  --annotations {out_dir}/human_audit_packet_{version}_completed.csv \\
  --answer-key {out_dir}/human_audit_answer_key_{version}.csv \\
  --annotator-roster {out_dir}/human_audit_annotator_roster_{version}.csv \\
  --expected-models {expected_models_arg}

conda run -n reprompt_tax python scripts/summarize_human_audit.py \\
  --annotations {out_dir}/human_audit_packet_{version}_completed.csv \\
  --answer-key {out_dir}/human_audit_answer_key_{version}.csv \\
  --out-dir results/tables/human_audit_{version}
```

`summarize_human_audit.py` fails on incomplete files by default. Use
`--allow-partial` only to debug partially returned batches, not for
paper-facing validation claims.

Optional stronger two-annotator workflow: concatenate independently completed
annotation rows into a long-format file with duplicate `audit_id` values but
unique `annotator_id` values per item, then compute inter-annotator agreement
and generate a blinded adjudication packet for disagreements:

```bash
conda run -n reprompt_tax python scripts/analyze_human_audit_adjudication.py \\
  --annotations {out_dir}/human_audit_packet_{version}_double_completed.csv \\
  --answer-key {out_dir}/human_audit_answer_key_{version}.csv \\
  --annotator-roster {out_dir}/human_audit_annotator_roster_{version}.csv \\
  --expected-models {expected_models_arg} \\
  --out-dir results/tables/human_audit_{version}_adjudication \\
  --out-md paper/human_audit_adjudication_{version.replace(".", "")}.md

# After filling results/tables/human_audit_{version}_adjudication/human_audit_adjudication_packet.csv:
conda run -n reprompt_tax python scripts/finalize_human_audit_adjudication.py \\
  --annotations {out_dir}/human_audit_packet_{version}_double_completed.csv \\
  --answer-key {out_dir}/human_audit_answer_key_{version}.csv \\
  --annotator-roster {out_dir}/human_audit_annotator_roster_{version}.csv \\
  --adjudication results/tables/human_audit_{version}_adjudication/human_audit_adjudication_packet.csv \\
  --expected-models {expected_models_arg} \\
  --out {out_dir}/human_audit_packet_{version}_adjudicated_completed.csv
```

## Claim Rule

Do not claim native-speaker or human validation until the completed file and
filled roster pass validation. If validation passes but disagreements are
substantial, keep the current automatic-plus-LLM-judge claim boundary and report
the disagreement pattern as a limitation.
"""
    path.write_text(text, encoding="utf-8")


def select_balanced_first_turns(rows: list[dict[str, Any]], seed: int, *, prefer_failures: bool = False) -> list[dict[str, Any]]:
    first_turns = [row for row in rows if int(row["turn"]) == 0]
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in first_turns:
        key = (row["model"], row["condition"], row["task_family"], row["language_pair"])
        grouped[key].append(row)

    rng = random.Random(seed)
    selected: list[dict[str, Any]] = []
    for key in sorted(grouped):
        group = sorted(grouped[key], key=lambda row: row["item_id"])
        if not group:
            continue
        candidates = [row for row in group if not bool(row["pass"])] if prefer_failures else group
        if not candidates:
            candidates = group
        selected.append(rng.choice(candidates))
    return sorted(selected, key=lambda row: (row["language_pair"], row["task_family"], row["model"], row["condition"], row["item_id"]))


def build_packet_rows(selected: list[dict[str, Any]], items: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    packet_rows: list[dict[str, Any]] = []
    key_rows: list[dict[str, Any]] = []

    for idx, row in enumerate(selected, start=1):
        item = items[row["item_id"]]
        audit_id = f"rpt_audit_{idx:03d}"
        packet_rows.append(
            {
                "audit_id": audit_id,
                "language_pair": row["language_pair"],
                "task_family": row["task_family"],
                "user_prompt": item["user_prompt"],
                "assistant_response": row["response"],
                "expected_response_language": item["expected_response_language"],
                "expected_script": item["expected_script"],
                "must_preserve_spans": json.dumps(item.get("must_preserve_spans", []), ensure_ascii=False),
                "register_requirement": item.get("register_requirement", ""),
                "locale_requirement": item.get("locale_requirement", ""),
                "known_bad_outputs": json.dumps(item.get("known_bad_outputs", []), ensure_ascii=False),
                "notes_for_annotators": item.get("notes_for_annotators", ""),
                **{field: "" for field in ANNOTATION_FIELDS},
            }
        )
        key_rows.append(
            {
                "audit_id": audit_id,
                "item_id": row["item_id"],
                "model": row["model"],
                "condition": row["condition"],
                "turn": row["turn"],
                "language_pair": row["language_pair"],
                "task_family": row["task_family"],
                "auto_pass": row["pass"],
                "auto_language_pass": row["language_pass"],
                "auto_script_pass": row["script_pass"],
                "auto_preservation_pass": row["preservation_pass"],
                "auto_task_pass": row["task_pass"],
                "auto_register_locale_pass": row["register_locale_pass"],
                "auto_failure_types": json.dumps(row.get("failure_types", []), ensure_ascii=False),
            }
        )

    return packet_rows, key_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument("--scores", type=Path, nargs="+", required=True)
    parser.add_argument("--out-dir", type=Path, default=Path("data/human_audit"))
    parser.add_argument("--packet-version", default="v0.2")
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--prefer-failures", action="store_true", help="within each stratum, sample an automatic failure when available")
    args = parser.parse_args()

    items = {row["id"]: row for row in load_jsonl(args.benchmark)}
    score_rows: list[dict[str, Any]] = []
    for score_path in args.scores:
        score_rows.extend(load_jsonl(score_path))
    selected = select_balanced_first_turns(score_rows, args.seed, prefer_failures=args.prefer_failures)
    packet_rows, key_rows = build_packet_rows(selected, items)

    packet_fields = [
        "audit_id",
        "language_pair",
        "task_family",
        "user_prompt",
        "assistant_response",
        "expected_response_language",
        "expected_script",
        "must_preserve_spans",
        "register_requirement",
        "locale_requirement",
        "known_bad_outputs",
        "notes_for_annotators",
        *ANNOTATION_FIELDS,
    ]
    key_fields = [
        "audit_id",
        "item_id",
        "model",
        "condition",
        "turn",
        "language_pair",
        "task_family",
        "auto_pass",
        "auto_language_pass",
        "auto_script_pass",
        "auto_preservation_pass",
        "auto_task_pass",
        "auto_register_locale_pass",
        "auto_failure_types",
    ]

    version = args.packet_version
    write_csv(args.out_dir / f"human_audit_packet_{version}.csv", packet_rows, packet_fields)
    write_csv(args.out_dir / f"human_audit_answer_key_{version}.csv", key_rows, key_fields)
    write_roster_template(args.out_dir / f"human_audit_annotator_roster_template_{version}.csv")

    for language_pair in sorted({row["language_pair"] for row in packet_rows}):
        lang_rows = [row for row in packet_rows if row["language_pair"] == language_pair]
        write_csv(args.out_dir / f"human_audit_packet_{version}_{language_pair}.csv", lang_rows, packet_fields)

    write_manifest(
        path=args.out_dir / f"audit_manifest_{version}.md",
        version=version,
        benchmark=args.benchmark,
        scores=args.scores,
        seed=args.seed,
        row_count=len(packet_rows),
        packet_rows=packet_rows,
        key_rows=key_rows,
        prefer_failures=args.prefer_failures,
    )
    write_launch_checklist(
        path=args.out_dir / f"human_audit_launch_checklist_{version}.md",
        version=version,
        row_count=len(packet_rows),
        expected_models=sorted({row["model"] for row in key_rows}),
    )

    print(f"wrote {len(packet_rows)} audit rows to {args.out_dir}")


if __name__ == "__main__":
    main()
