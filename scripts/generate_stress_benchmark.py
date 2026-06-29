#!/usr/bin/env python
"""Generate a harder RePromptTax stress set.

This set keeps the same schema as benchmark_v0.1 but concentrates on cases that
the initial pilot suggests are more fragile: implicit edit-language preservation,
exact preservation of translatable headings, and script/locale constraints with
literal spans.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from generate_benchmark import LANG_CONFIG, base_item


OUT_PATH = Path("data/benchmark_stress_v0.1.jsonl")


IMPLICIT_EDITING = [
    {
        "text": "Hi team, I finished the notes but I am not sure if the conclusion is clear.",
        "markers": ["team", "notes", "conclusion"],
        "register": "clear workplace message",
    },
    {
        "text": "Hello, I need to change my appointment because my train was delayed.",
        "markers": ["appointment", "train", "delayed"],
        "register": "polite appointment message",
    },
    {
        "text": "Thanks for your help. I will review the invoice and send the missing details tonight.",
        "markers": ["invoice", "missing details", "tonight"],
        "register": "professional reply",
    },
    {
        "text": "I can't join the call today, but I can share my update by email.",
        "markers": ["call", "today", "email"],
        "register": "concise workplace update",
    },
    {
        "text": "The first paragraph is too long and the final sentence sounds a bit rude.",
        "markers": ["paragraph", "sentence", "rude"],
        "register": "editing feedback",
    },
]


GRAMMAR_STRESS = [
    {
        "source": "The data are not enough to support this claim.",
        "markers": ["data are insufficient", "data are not sufficient", "data is not enough", "data are not enough"],
    },
    {
        "source": "Each of the students have submitted their form.",
        "markers": ["each of the students has submitted", "each student has submitted"],
    },
    {
        "source": "I would appreciate if you can reply today.",
        "markers": ["I would appreciate it if you could reply today", "appreciate it if you can reply today"],
    },
    {
        "source": "This feedback is more clear than the last version.",
        "markers": ["clearer than the last version", "more clear than the last version"],
    },
    {
        "source": "Please let me know if there is any informations missing.",
        "markers": ["any information missing", "any information is missing", "any missing information"],
    },
]


TRANSLATABLE_HEADINGS = [
    ("Return Policy", "Refund Request"),
    ("Budget Review", "Community Questions"),
    ("Safety Guidelines", "Emergency Contact"),
    ("Privacy Notice", "Data Export"),
    ("Course Requirements", "Final Exam"),
]


SCRIPT_LOCALE_CASES = [
    {
        "context": "Tell a friend I paid ₹500 and will send the receipt tomorrow.",
        "spans": ["₹500"],
        "es_markers": ["pagué", "recibo", "mañana"],
        "hi_markers": ["₹500", "receipt", "kal"],
    },
    {
        "context": "Confirm the meeting is on 05/07/2026 and ask them not to change the date format.",
        "spans": ["05/07/2026"],
        "es_markers": ["reunión", "05/07/2026", "fecha"],
        "hi_markers": ["meeting", "05/07/2026", "date"],
    },
    {
        "context": "Say the booking code ABC-17 is correct and I will arrive after lunch.",
        "spans": ["ABC-17"],
        "es_markers": ["ABC-17", "llego", "almuerzo"],
        "hi_markers": ["ABC-17", "lunch", "pahunch"],
    },
    {
        "context": "Ask if the shop can keep the order under the name Mira Rao exactly.",
        "spans": ["Mira Rao"],
        "es_markers": ["Mira Rao", "pedido", "nombre"],
        "hi_markers": ["Mira Rao", "order", "naam"],
    },
    {
        "context": "Tell my classmate that the file name draft_v2.pdf should stay unchanged.",
        "spans": ["draft_v2.pdf"],
        "es_markers": ["draft_v2.pdf", "archivo", "cambiar"],
        "hi_markers": ["draft_v2.pdf", "file", "change"],
    },
]


STRESS_PROMPTS = {
    "es-en": {
        "implicit_editing": 'Me ayudas a mejorar este texto para que suene natural? "{text}"',
        "grammar": 'Corrige solo la frase en inglés. No expliques nada: "{source}"',
        "quote": 'Resume esto en español, pero deja los títulos entre comillas exactamente en inglés: The document lists "{a}" before "{b}".',
        "script": "Escribe una respuesta breve en español. Conserva exactamente estos datos si aparecen en el contexto. Context: {context}",
        "quote_language": "Spanish",
        "script_language": "Spanish",
        "quote_script": "Latin",
        "script_script": "Latin",
    },
    "hi-en": {
        "implicit_editing": 'Is text ko natural aur polished bana do: "{text}"',
        "grammar": 'Sirf corrected English sentence do, explanation nahi: "{source}"',
        "quote": 'Hindi mein short summary do, Latin script only. Quoted headings ko exactly English mein rakho: The document lists "{a}" before "{b}".',
        "script": "Hindi mein short WhatsApp reply likho, Latin script only, no Devanagari. Context mein exact data same rakhna. Context: {context}",
        "quote_language": "Hindi/Hinglish",
        "script_language": "Hindi/Hinglish",
        "quote_script": "Latin",
        "script_script": "Latin",
    },
    "ar-en": {
        "implicit_editing": 'ساعدني في تحسين هذا النص ليصبح أوضح وأكثر لطفاً: "{text}"',
        "grammar": 'صحح الجملة الإنجليزية فقط من دون شرح: "{source}"',
        "quote": 'لخص هذا بالعربية، لكن اترك العناوين بين علامتي الاقتباس كما هي بالإنجليزية: The document lists "{a}" before "{b}".',
        "script": "اكتب رد واتساب قصير بالعربية. حافظ على البيانات المذكورة في السياق كما هي تماماً. السياق: {context}",
        "quote_language": "Arabic",
        "script_language": "Arabic",
        "quote_script": "Arabic",
        "script_script": "Arabic",
    },
}


def build_items() -> list[dict]:
    items: list[dict] = []
    for pair, cfg in LANG_CONFIG.items():
        stress = STRESS_PROMPTS[pair]
        prefix = cfg["prefix"]

        for idx, item in enumerate(IMPLICIT_EDITING, start=1):
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

        for idx, item in enumerate(GRAMMAR_STRESS, start=1):
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

        for idx, (span_a, span_b) in enumerate(TRANSLATABLE_HEADINGS, start=1):
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
                repair_prompt_2=f"Do not translate or change \"{span_a}\" or \"{span_b}\".",
                required_any_markers=[span_a, span_b],
                notes_for_annotators="The quoted headings are semantically translatable but must remain exact.",
            )
            row["stress_tag"] = "translatable_quoted_heading"
            items.append(row)

        for idx, item in enumerate(SCRIPT_LOCALE_CASES, start=1):
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
    if len(items) != 60:
        raise ValueError(f"expected 60 items, got {len(items)}")
    ids = [item["id"] for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate item ids")


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
