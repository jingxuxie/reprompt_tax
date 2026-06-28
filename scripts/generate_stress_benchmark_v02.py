#!/usr/bin/env python
"""Generate an expanded RePromptTax stress set.

This extends RePromptTax-Stress-v0.1 with five more stress cases per
language-pair/task-family cell. The resulting 120-item v0.2 benchmark is the
current paper-facing stress set.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from generate_benchmark import LANG_CONFIG, base_item
from generate_stress_benchmark import (
    GRAMMAR_STRESS,
    IMPLICIT_EDITING,
    SCRIPT_LOCALE_CASES,
    STRESS_PROMPTS,
    TRANSLATABLE_HEADINGS,
)


OUT_PATH = Path("data/benchmark_stress_v0.2.jsonl")


IMPLICIT_EDITING_MORE = [
    {
        "text": "I reviewed the report, and the second chart seems confusing for new readers.",
        "markers": ["report", "chart", "readers"],
        "register": "clear editing feedback",
    },
    {
        "text": "Could you tell the client that the payment will arrive next week?",
        "markers": ["client", "payment", "next week"],
        "register": "polite client update",
    },
    {
        "text": "The survey question sounds too direct and might make people uncomfortable.",
        "markers": ["survey", "direct", "uncomfortable"],
        "register": "constructive research feedback",
    },
    {
        "text": "I need to ask my manager for one more day to finish the slide deck.",
        "markers": ["manager", "one more day", "slide deck"],
        "register": "polite workplace request",
    },
    {
        "text": "Please tell the tenant we fixed the heating issue and will check again tomorrow.",
        "markers": ["tenant", "heating", "tomorrow"],
        "register": "clear maintenance update",
    },
]


GRAMMAR_STRESS_MORE = [
    {
        "source": "Neither of the answers are correct.",
        "markers": ["neither of the answers is correct", "neither answer is correct", "none of the answers are correct"],
    },
    {
        "source": "The team have finished its review.",
        "markers": ["the team has finished its review", "the team have finished their review"],
    },
    {
        "source": "Please discuss about the schedule before Monday.",
        "markers": ["discuss the schedule before Monday", "discuss the schedule"],
    },
    {
        "source": "I am used to work late on Fridays.",
        "markers": ["used to working late", "accustomed to working late"],
    },
    {
        "source": "This option is more better for small teams.",
        "markers": ["better for small teams", "more suitable for small teams"],
    },
]


TRANSLATABLE_HEADINGS_MORE = [
    ("Office Hours", "Makeup Exam"),
    ("Payment Deadline", "Late Fee"),
    ("Visitor Guidelines", "Check-In Desk"),
    ("Account Settings", "Password Reset"),
    ("Health Benefits", "Enrollment Form"),
]


SCRIPT_LOCALE_CASES_MORE = [
    {
        "context": "Ask if the clinic can move my visit to 10:30 AM without changing the appointment number INV-2048.",
        "spans": ["10:30 AM", "INV-2048"],
        "es_markers": ["clínica", "10:30 AM", "INV-2048"],
        "hi_markers": ["clinic", "10:30 AM", "INV-2048"],
    },
    {
        "context": "Tell the delivery driver to leave the box at Apt 5B and call when they arrive.",
        "spans": ["Apt 5B"],
        "es_markers": ["Apt 5B", "caja", "llame"],
        "hi_markers": ["Apt 5B", "box", "call"],
    },
    {
        "context": "Tell HR I can start on June 12 and the employee ID QR-77 should stay the same.",
        "spans": ["June 12", "QR-77"],
        "es_markers": ["June 12", "QR-77", "empezar"],
        "hi_markers": ["June 12", "QR-77", "start"],
    },
    {
        "context": "Ask the bank to keep account label Travel_Fund exactly as written.",
        "spans": ["Travel_Fund"],
        "es_markers": ["Travel_Fund", "cuenta", "exactamente"],
        "hi_markers": ["Travel_Fund", "account", "same"],
    },
    {
        "context": "Confirm the pickup window is 2-4 PM and the order code is BK-903.",
        "spans": ["2-4 PM", "BK-903"],
        "es_markers": ["2-4 PM", "BK-903", "pedido"],
        "hi_markers": ["2-4 PM", "BK-903", "order"],
    },
]


def build_items() -> list[dict]:
    items: list[dict] = []
    implicit_items = [*IMPLICIT_EDITING, *IMPLICIT_EDITING_MORE]
    grammar_items = [*GRAMMAR_STRESS, *GRAMMAR_STRESS_MORE]
    heading_items = [*TRANSLATABLE_HEADINGS, *TRANSLATABLE_HEADINGS_MORE]
    script_items = [*SCRIPT_LOCALE_CASES, *SCRIPT_LOCALE_CASES_MORE]

    for pair, cfg in LANG_CONFIG.items():
        stress = STRESS_PROMPTS[pair]
        prefix = cfg["prefix"]

        for idx, item in enumerate(implicit_items, start=1):
            row = base_item(
                item_id=f"{prefix}_SA_{idx:03d}",
                language_pair=pair,
                task_family="editing_preservation",
                user_prompt=stress["implicit_editing"].format(text=item["text"]),
                expected_response_language="English",
                expected_script="Latin",
                register_requirement=item["register"],
                known_bad_outputs=["translation into instruction language", "explanation without rewriting"],
                repair_prompt_1="Please keep the rewritten text in English.",
                repair_prompt_2="Do not translate. Output only the polished English version.",
                required_any_markers=item["markers"],
                forbidden_markers=["Estimado", "Claro", "بالطبع", "إليك", "प्रिय", "नमस्ते"],
                notes_for_annotators="Instruction language differs from content language; output should preserve content language.",
            )
            row["stress_tag"] = "implicit_content_language"
            items.append(row)

        for idx, item in enumerate(grammar_items, start=1):
            row = base_item(
                item_id=f"{prefix}_SB_{idx:03d}",
                language_pair=pair,
                task_family="output_language_inference",
                user_prompt=stress["grammar"].format(source=item["source"]),
                expected_response_language="English",
                expected_script="Latin",
                register_requirement="corrected sentence only",
                known_bad_outputs=["translation", "explanation without corrected English sentence"],
                repair_prompt_1="Please give only the corrected English sentence.",
                repair_prompt_2="Output only the corrected English sentence, not a translation or explanation.",
                required_any_markers=item["markers"],
                forbidden_markers=[],
                notes_for_annotators="Equivalent grammatical corrections are acceptable.",
            )
            row["stress_tag"] = "correction_only"
            items.append(row)

        for idx, (span_a, span_b) in enumerate(heading_items, start=1):
            row = base_item(
                item_id=f"{prefix}_SC_{idx:03d}",
                language_pair=pair,
                task_family="quote_preservation",
                user_prompt=stress["quote"].format(a=span_a, b=span_b),
                expected_response_language=stress["quote_language"],
                expected_script=stress["quote_script"],
                must_preserve_spans=[span_a, span_b],
                register_requirement="neutral concise summary",
                known_bad_outputs=["translated quoted heading", "dropped quoted heading"],
                repair_prompt_1="Please keep the quoted headings exactly in English.",
                repair_prompt_2=f'Do not translate or change "{span_a}" or "{span_b}".',
                required_any_markers=[span_a, span_b],
                notes_for_annotators="The quoted headings are semantically translatable but must remain exact.",
            )
            row["stress_tag"] = "translatable_quoted_heading"
            items.append(row)

        for idx, item in enumerate(script_items, start=1):
            if pair == "es-en":
                required = item["es_markers"]
            elif pair == "hi-en":
                required = item["hi_markers"]
            else:
                required = item["spans"]
            row = base_item(
                item_id=f"{prefix}_SD_{idx:03d}",
                language_pair=pair,
                task_family="script_register_locale",
                user_prompt=stress["script"].format(context=item["context"]),
                expected_response_language=stress["script_language"],
                expected_script=stress["script_script"],
                must_preserve_spans=item["spans"],
                register_requirement="short polite casual message",
                locale_requirement="preserve literal dates, codes, names, filenames, and amounts exactly",
                known_bad_outputs=["wrong script", "changes literal data", "English-only response"],
                repair_prompt_1="Please preserve the literal data exactly and follow the requested script.",
                repair_prompt_2="Output only the short message with the literal span unchanged.",
                required_any_markers=required,
                forbidden_markers=["Dear Sir or Madam", "To whom it may concern", "प्रिय", "नमस्ते"],
                notes_for_annotators="Literal data must be unchanged even if the surrounding language changes.",
            )
            row["stress_tag"] = "literal_locale_span"
            items.append(row)

    return items


def validate(items: list[dict]) -> None:
    if len(items) != 120:
        raise ValueError(f"expected 120 items, got {len(items)}")
    ids = [item["id"] for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate item ids")
    counts = Counter((item["language_pair"], item["task_family"]) for item in items)
    expected = {
        (pair, family): 10
        for pair in LANG_CONFIG
        for family in (
            "editing_preservation",
            "output_language_inference",
            "quote_preservation",
            "script_register_locale",
        )
    }
    if dict(counts) != expected:
        raise ValueError(f"unexpected cell counts: {counts}")
    for item in items:
        for field in ("id", "user_prompt", "expected_response_language", "expected_script", "repair_prompt_1", "repair_prompt_2"):
            if not item.get(field):
                raise ValueError(f"{item.get('id', '<missing id>')} missing {field}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    args = parser.parse_args()
    items = build_items()
    validate(items)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"wrote {len(items)} stress items to {args.out}")


if __name__ == "__main__":
    main()
