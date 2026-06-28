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
        writer = csv.DictWriter(f, fieldnames=fields)
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
    scores: Path,
    seed: int,
    row_count: int,
) -> None:
    text = f"""# RePromptTax Human Audit Manifest {version}

Generated for the current paper-facing full RePromptTax-Stress-v0.2 result.

Source benchmark: `{benchmark}`
Source scores: `{scores}`
Sampling seed: `{seed}`

## Launch Files

Send annotators only the language slice they can validate:

| Language slice | File | Rows |
|---|---|---:|
| Arabic-English | `human_audit_packet_{version}_ar-en.csv` | 24 |
| Spanish-English | `human_audit_packet_{version}_es-en.csv` | 24 |
| Hindi-English | `human_audit_packet_{version}_hi-en.csv` | 24 |

The full blinded packet is `human_audit_packet_{version}.csv` with {row_count} rows.
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

- 3 language pairs,
- 4 task families,
- 3 models,
- 2 prompt conditions,
- 1 first-turn output per language/model/condition/family stratum.

Each language slice contains 6 rows per task family.

## Required Validation Before Launch

```bash
conda run -n reprompt_tax python scripts/validate_human_audit_packet.py

conda run -n reprompt_tax python scripts/analyze_human_audit_design.py \\
  --packet data/human_audit/human_audit_packet_{version}.csv \\
  --answer-key data/human_audit/human_audit_answer_key_{version}.csv \\
  --out-dir results/tables/human_audit_{version}_design \\
  --out-md paper/human_audit_design_audit_{version.replace(".", "")}.md
```

This checks:

- no private model, condition, item, or auto-label fields leak into annotator packets,
- annotation fields are blank in launch packets,
- language slices exactly match the corresponding full-packet subsets,
- each language/task cell and model/condition/task/language stratum is balanced,
- JSON-list fields are parseable,
- any smoke-only artifacts are explicitly marked,
- the selected audit rows include both automatic passes and failures before annotation.

## Completion Gate

After annotators fill the CSV fields, summarize labels with:

```bash
conda run -n reprompt_tax python scripts/validate_completed_human_audit.py \\
  --annotations data/human_audit/human_audit_packet_{version}_completed.csv \\
  --answer-key data/human_audit/human_audit_answer_key_{version}.csv

conda run -n reprompt_tax python scripts/summarize_human_audit.py \\
  --annotations data/human_audit/human_audit_packet_{version}_completed.csv \\
  --answer-key data/human_audit/human_audit_answer_key_{version}.csv \\
  --out-dir results/tables/human_audit_{version}
```

Strong final paper claims should wait for completed human/native-speaker labels.
Completed claims also require a filled annotator roster with native or
near-native language competence, script competence, and no conflict of interest
for every annotator ID used in the completed packet.
Any smoke-completed file is only a plumbing test and must not be used for final
claims.
"""
    path.write_text(text, encoding="utf-8")


def write_launch_checklist(*, path: Path, version: str, row_count: int) -> None:
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
- Do not send `human_audit_answer_key_{version}.csv`.
- Ask annotators to fill all annotation columns in their CSV slice and preserve
  the original row order and `audit_id` values.
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
audit rows. If annotators work from language slices, concatenate the completed
slice rows under the original header without adding answer-key fields.

## Completion Commands

```bash
conda run -n reprompt_tax python scripts/validate_completed_human_audit.py \\
  --annotations data/human_audit/human_audit_packet_{version}_completed.csv \\
  --answer-key data/human_audit/human_audit_answer_key_{version}.csv \\
  --annotator-roster data/human_audit/human_audit_annotator_roster_{version}.csv

conda run -n reprompt_tax python scripts/summarize_human_audit.py \\
  --annotations data/human_audit/human_audit_packet_{version}_completed.csv \\
  --answer-key data/human_audit/human_audit_answer_key_{version}.csv \\
  --out-dir results/tables/human_audit_{version}
```

## Claim Rule

Do not claim native-speaker or human validation until the completed file and
filled roster pass validation. If validation passes but disagreements are
substantial, keep the current automatic-plus-LLM-judge claim boundary and report
the disagreement pattern as a limitation.
"""
    path.write_text(text, encoding="utf-8")


def select_balanced_first_turns(rows: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    first_turns = [row for row in rows if int(row["turn"]) == 0]
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in first_turns:
        key = (row["model"], row["condition"], row["task_family"], row["language_pair"])
        grouped[key].append(row)

    rng = random.Random(seed)
    selected: list[dict[str, Any]] = []
    for key in sorted(grouped):
        group = grouped[key]
        if not group:
            continue
        selected.append(rng.choice(sorted(group, key=lambda row: row["item_id"])))
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
    parser.add_argument("--scores", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=Path("data/human_audit"))
    parser.add_argument("--packet-version", default="v0.2")
    parser.add_argument("--seed", type=int, default=23)
    args = parser.parse_args()

    items = {row["id"]: row for row in load_jsonl(args.benchmark)}
    score_rows = load_jsonl(args.scores)
    selected = select_balanced_first_turns(score_rows, args.seed)
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
    )
    write_launch_checklist(
        path=args.out_dir / f"human_audit_launch_checklist_{version}.md",
        version=version,
        row_count=len(packet_rows),
    )

    print(f"wrote {len(packet_rows)} audit rows to {args.out_dir}")


if __name__ == "__main__":
    main()
