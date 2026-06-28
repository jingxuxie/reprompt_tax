#!/usr/bin/env python
"""Generate the 120-item RePromptTax pilot benchmark.

The pilot is synthetic but hand-template-driven: each cell has stable provenance
and can be manually audited before release.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


OUT_PATH = Path("data/benchmark_v0.1.jsonl")


EDITING_SNIPPETS = [
    {
        "domain": "professor email",
        "text": "Hi professor, I can't submit the homework today because my internet was down. Can I send it tomorrow?",
        "register": "professional email",
        "markers": ["professor", "homework", "internet", "tomorrow"],
    },
    {
        "domain": "support request",
        "text": "Hello, my package arrived damaged and I want a refund or a replacement.",
        "register": "polite customer support message",
        "markers": ["package", "damaged", "refund", "replacement"],
    },
    {
        "domain": "work update",
        "text": "I finished the draft but I still need your comments before I send it to the team.",
        "register": "clear workplace update",
        "markers": ["draft", "comments", "team"],
    },
    {
        "domain": "landlord message",
        "text": "There is a leak under the kitchen sink and it has been getting worse since Monday.",
        "register": "polite maintenance request",
        "markers": ["leak", "kitchen", "sink", "Monday"],
    },
    {
        "domain": "resume bullet",
        "text": "Managed social media posts and helped answer customer questions during busy hours.",
        "register": "concise resume bullet",
        "markers": ["managed", "social media", "customer"],
    },
    {
        "domain": "client apology",
        "text": "Sorry for the delay. We found the problem and will send the corrected file today.",
        "register": "professional apology",
        "markers": ["delay", "problem", "corrected file", "today"],
    },
    {
        "domain": "meeting reschedule",
        "text": "Can we move our meeting to Friday afternoon? I have a doctor's appointment at the original time.",
        "register": "polite scheduling email",
        "markers": ["meeting", "Friday", "appointment"],
    },
    {
        "domain": "scholarship note",
        "text": "I am writing to ask if the scholarship application deadline can be extended by one day.",
        "register": "formal request",
        "markers": ["scholarship", "deadline", "extended"],
    },
    {
        "domain": "project update",
        "text": "The deployment is finished, but we should monitor the dashboard for errors tonight.",
        "register": "concise engineering update",
        "markers": ["deployment", "dashboard", "errors"],
    },
    {
        "domain": "cover letter",
        "text": "I am excited about this role because it matches my experience in data analysis and community projects.",
        "register": "polished cover letter sentence",
        "markers": ["role", "experience", "data analysis", "community"],
    },
]


GRAMMAR_ITEMS = [
    {
        "source": "I am looking forward to hear from you.",
        "target": "I am looking forward to hearing from you.",
        "markers": ["looking forward to hearing from you"],
    },
    {
        "source": "She don't have enough time.",
        "target": "She doesn't have enough time.",
        "markers": ["doesn't have enough time", "does not have enough time"],
    },
    {
        "source": "Please advice me what to do next.",
        "target": "Please advise me on what to do next.",
        "markers": ["advise me", "what to do next"],
    },
    {
        "source": "I have went to the office yesterday.",
        "target": "I went to the office yesterday.",
        "markers": ["went to the office yesterday", "have gone to the office"],
    },
    {
        "source": "Can you explain me the difference?",
        "target": "Can you explain the difference to me?",
        "markers": ["explain the difference to me", "explain to me the difference"],
    },
    {
        "source": "I am agree with your suggestion.",
        "target": "I agree with your suggestion.",
        "markers": ["I agree with your suggestion"],
    },
    {
        "source": "We discussed about the plan yesterday.",
        "target": "We discussed the plan yesterday.",
        "markers": ["discussed the plan yesterday"],
    },
    {
        "source": "It depends of the weather.",
        "target": "It depends on the weather.",
        "markers": ["depends on the weather"],
    },
    {
        "source": "I will revert back to you soon.",
        "target": "I will get back to you soon.",
        "markers": ["get back to you soon", "revert to you soon"],
    },
    {
        "source": "There is many reasons for this problem.",
        "target": "There are many reasons for this problem.",
        "markers": ["There are many reasons", "there are many reasons"],
    },
]


QUOTE_TEXTS = [
    {
        "text": 'The update says that "Project Greenlight" will start after "Phase Zero" is approved.',
        "spans": ["Project Greenlight", "Phase Zero"],
    },
    {
        "text": 'The memo says the product "ClearNote" now includes a feature called "Quick Share".',
        "spans": ["ClearNote", "Quick Share"],
    },
    {
        "text": 'The article describes "City Lab" as part of a larger program named "Open Streets".',
        "spans": ["City Lab", "Open Streets"],
    },
    {
        "text": 'The instructions say to type "reset-cache" before running "sync-data".',
        "spans": ["reset-cache", "sync-data"],
    },
    {
        "text": 'The review says "The Long Road Home" is stronger than "Summer Window".',
        "spans": ["The Long Road Home", "Summer Window"],
    },
    {
        "text": 'The contract refers to "Section 4.2" and the term "Service Credit".',
        "spans": ["Section 4.2", "Service Credit"],
    },
    {
        "text": 'The teacher assigned "Chapter Five" and the worksheet "Practice Set B".',
        "spans": ["Chapter Five", "Practice Set B"],
    },
    {
        "text": 'The announcement says "North Hall" will close before "Winter Break".',
        "spans": ["North Hall", "Winter Break"],
    },
    {
        "text": 'The changelog lists "Safe Mode" and "Export History" as new options.',
        "spans": ["Safe Mode", "Export History"],
    },
    {
        "text": 'The agenda includes "Budget Review" followed by "Community Questions".',
        "spans": ["Budget Review", "Community Questions"],
    },
]


LOCALE_CONTEXTS = [
    {
        "context": "Tell my cousin I will be 20 minutes late.",
        "topic": "late arrival",
        "es_markers": ["llego", "tarde", "minutos"],
        "hi_markers": ["late", "min", "pahunch", "aaunga", "aaungi"],
    },
    {
        "context": "Tell a coworker I will send the file tomorrow morning.",
        "topic": "file tomorrow",
        "es_markers": ["archivo", "mañana"],
        "hi_markers": ["file", "kal", "bhej"],
    },
    {
        "context": "Decline a dinner invitation politely because I have another plan.",
        "topic": "decline invitation",
        "es_markers": ["gracias", "plan", "puedo"],
        "hi_markers": ["sorry", "plan", "nahi"],
    },
    {
        "context": "Ask a friend to bring the charger they borrowed.",
        "topic": "borrowed charger",
        "es_markers": ["cargador", "traer"],
        "hi_markers": ["charger", "laana", "le aana"],
    },
    {
        "context": "Tell a teammate the meeting link is not working.",
        "topic": "broken meeting link",
        "es_markers": ["enlace", "reunión", "funciona"],
        "hi_markers": ["link", "kaam", "nahi"],
    },
    {
        "context": "Ask a shop if they accept UPI payments.",
        "topic": "payment method",
        "es_markers": ["pago", "aceptan"],
        "hi_markers": ["UPI", "payment", "karte"],
    },
    {
        "context": "Tell a neighbor the music is too loud but be respectful.",
        "topic": "noise request",
        "es_markers": ["música", "volumen", "favor"],
        "hi_markers": ["music", "volume", "thoda"],
    },
    {
        "context": "Confirm that I received the documents and will review them today.",
        "topic": "documents received",
        "es_markers": ["documentos", "revisar", "hoy"],
        "hi_markers": ["documents", "mil", "aaj"],
    },
    {
        "context": "Tell my aunt I reached home safely.",
        "topic": "safe arrival",
        "es_markers": ["llegué", "casa", "bien"],
        "hi_markers": ["ghar", "safe", "pahunch"],
    },
    {
        "context": "Ask a classmate to share the notes from today's lecture.",
        "topic": "class notes",
        "es_markers": ["apuntes", "clase", "compartir"],
        "hi_markers": ["notes", "class", "bhej"],
    },
]


LANG_CONFIG = {
    "es-en": {
        "prefix": "es_en",
        "instruction_language": "Spanish/English code-switched",
        "editing_prompt": 'Puedes hacer este texto más natural y profesional, but keep it in English? "{text}"',
        "grammar_prompt": 'Corrige la gramática de esta frase en inglés y responde con la frase corregida: "{source}"',
        "quote_prompt": 'Resume el siguiente texto en español en una frase, pero no traduzcas ni cambies las frases entre comillas: {text}',
        "script_prompt": "Escribe una respuesta breve en español de México, amable pero casual. Context: {context}",
        "quote_expected_language": "Spanish",
        "script_expected_language": "Spanish",
        "quote_expected_script": "Latin",
        "script_expected_script": "Latin",
    },
    "hi-en": {
        "prefix": "hi_en",
        "instruction_language": "Hindi/English code-switched",
        "editing_prompt": 'Is text ko zyada professional bana do, but English mein hi rakhna: "{text}"',
        "grammar_prompt": 'Is English sentence ki grammar correct karo. Bas corrected English sentence do: "{source}"',
        "quote_prompt": "Hindi mein ek short summary do, Latin script only, aur quotes ko exactly same rakho: {text}",
        "script_prompt": "Hindi mein short WhatsApp reply likho, Latin script only, no Devanagari. Context: {context}",
        "quote_expected_language": "Hindi/Hinglish",
        "script_expected_language": "Hindi/Hinglish",
        "quote_expected_script": "Latin",
        "script_expected_script": "Latin",
    },
    "ar-en": {
        "prefix": "ar_en",
        "instruction_language": "Arabic/English code-switched",
        "editing_prompt": 'هل يمكنك تحسين هذا النص وجعله أكثر مهنية، لكن أبقه بالإنجليزية؟ "{text}"',
        "grammar_prompt": 'صحح الجملة الإنجليزية التالية واكتب الجملة المصححة فقط: "{source}"',
        "quote_prompt": "لخص النص التالي بالعربية في جملة واحدة، لكن لا تترجم العبارات بين علامتي الاقتباس: {text}",
        "script_prompt": "اكتب رد واتساب قصير بالعربية، بلهجة مهذبة وغير رسمية. السياق: {context}",
        "quote_expected_language": "Arabic",
        "script_expected_language": "Arabic",
        "quote_expected_script": "Arabic",
        "script_expected_script": "Arabic",
    },
}


def base_item(
    *,
    item_id: str,
    language_pair: str,
    task_family: str,
    user_prompt: str,
    expected_response_language: str,
    expected_script: str,
    must_preserve_spans: list[str] | None = None,
    register_requirement: str | None = None,
    locale_requirement: str | None = None,
    known_bad_outputs: list[str] | None = None,
    repair_prompt_1: str,
    repair_prompt_2: str,
    required_any_markers: list[str] | None = None,
    forbidden_markers: list[str] | None = None,
    notes_for_annotators: str = "",
) -> dict:
    cfg = LANG_CONFIG[language_pair]
    return {
        "id": item_id,
        "language_pair": language_pair,
        "task_family": task_family,
        "user_prompt": user_prompt,
        "instruction_language": cfg["instruction_language"],
        "content_language": "English" if task_family != "script_register_locale" else "context in English",
        "expected_response_language": expected_response_language,
        "expected_script": expected_script,
        "must_preserve_spans": must_preserve_spans or [],
        "register_requirement": register_requirement,
        "locale_requirement": locale_requirement,
        "acceptable_outputs": ["satisfies the expected language, script, preservation, register, and task constraints"],
        "known_bad_outputs": known_bad_outputs or [],
        "repair_prompt_1": repair_prompt_1,
        "repair_prompt_2": repair_prompt_2,
        "required_any_markers": required_any_markers or [],
        "forbidden_markers": forbidden_markers or [],
        "notes_for_annotators": notes_for_annotators,
    }


def build_items() -> list[dict]:
    items: list[dict] = []
    for pair, cfg in LANG_CONFIG.items():
        prefix = cfg["prefix"]

        for idx, snippet in enumerate(EDITING_SNIPPETS, start=1):
            items.append(
                base_item(
                    item_id=f"{prefix}_A_{idx:03d}",
                    language_pair=pair,
                    task_family="editing_preservation",
                    user_prompt=cfg["editing_prompt"].format(text=snippet["text"]),
                    expected_response_language="English",
                    expected_script="Latin",
                    register_requirement=snippet["register"],
                    known_bad_outputs=[
                        "translation into the instruction language",
                        "explanation without rewriting the content",
                        "unnecessary mixed-language answer",
                    ],
                    repair_prompt_1="Please keep the rewritten text in English.",
                    repair_prompt_2="Do not translate. Output only the polished English version.",
                    required_any_markers=snippet["markers"],
                    forbidden_markers=["Estimado", "Claro", "ترجمة", "प्रिय", "नमस्ते"],
                    notes_for_annotators="The output should rewrite the English content, not translate it.",
                )
            )

        for idx, grammar in enumerate(GRAMMAR_ITEMS, start=1):
            items.append(
                base_item(
                    item_id=f"{prefix}_B_{idx:03d}",
                    language_pair=pair,
                    task_family="output_language_inference",
                    user_prompt=cfg["grammar_prompt"].format(source=grammar["source"]),
                    expected_response_language="English",
                    expected_script="Latin",
                    register_requirement="corrected sentence only or minimal explanation",
                    known_bad_outputs=[
                        "translation into the instruction language",
                        "explanation without the corrected English sentence",
                        "keeps the original grammatical error",
                    ],
                    repair_prompt_1="Please give the corrected English sentence.",
                    repair_prompt_2="Output only the corrected English sentence, not a translation.",
                    required_any_markers=grammar["markers"],
                    forbidden_markers=[grammar["source"]],
                    notes_for_annotators="A minimal explanation is acceptable only if the corrected English sentence is present.",
                )
            )

        for idx, quote in enumerate(QUOTE_TEXTS, start=1):
            items.append(
                base_item(
                    item_id=f"{prefix}_C_{idx:03d}",
                    language_pair=pair,
                    task_family="quote_preservation",
                    user_prompt=cfg["quote_prompt"].format(text=quote["text"]),
                    expected_response_language=cfg["quote_expected_language"],
                    expected_script=cfg["quote_expected_script"],
                    must_preserve_spans=quote["spans"],
                    register_requirement="neutral concise summary",
                    known_bad_outputs=[
                        "translated quoted phrase",
                        "transliterated quoted phrase",
                        "dropped quoted phrase",
                    ],
                    repair_prompt_1="Please keep every quoted phrase exactly as written.",
                    repair_prompt_2=f"Do not translate or change {', '.join(quote['spans'])}. Keep those spans exactly.",
                    required_any_markers=quote["spans"],
                    notes_for_annotators="Quoted spans must appear exactly, including capitalization and spacing.",
                )
            )

        for idx, locale in enumerate(LOCALE_CONTEXTS, start=1):
            if pair == "es-en":
                required = locale["es_markers"]
                locale_req = "Mexico-oriented casual Spanish if locale is relevant"
            elif pair == "hi-en":
                required = locale["hi_markers"]
                locale_req = "Romanized Hindi/Hinglish WhatsApp style"
            else:
                required = []
                locale_req = "polite casual Arabic WhatsApp style"

            items.append(
                base_item(
                    item_id=f"{prefix}_D_{idx:03d}",
                    language_pair=pair,
                    task_family="script_register_locale",
                    user_prompt=cfg["script_prompt"].format(context=locale["context"]),
                    expected_response_language=cfg["script_expected_language"],
                    expected_script=cfg["script_expected_script"],
                    register_requirement="polite casual short message",
                    locale_requirement=locale_req,
                    known_bad_outputs=[
                        "wrong script",
                        "English-only response",
                        "overly formal response",
                        "does not address the context",
                    ],
                    repair_prompt_1=f"Please write it in {cfg['script_expected_language']} with the requested script and tone.",
                    repair_prompt_2="Follow the script constraint exactly and output only the short message.",
                    required_any_markers=required,
                    forbidden_markers=["Dear Sir or Madam", "To whom it may concern", "प्रिय", "नमस्ते"],
                    notes_for_annotators=f"Message should address the context: {locale['topic']}.",
                )
            )

    return items


def validate(items: list[dict]) -> None:
    ids = [item["id"] for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate item ids")
    if len(items) != 120:
        raise ValueError(f"expected 120 items, got {len(items)}")
    counts: dict[tuple[str, str], int] = {}
    for item in items:
        key = (item["language_pair"], item["task_family"])
        counts[key] = counts.get(key, 0) + 1
        for field in ("user_prompt", "repair_prompt_1", "repair_prompt_2"):
            if not item[field]:
                raise ValueError(f"{item['id']} has empty {field}")
    bad_counts = {key: count for key, count in counts.items() if count != 10}
    if bad_counts:
        raise ValueError(f"expected 10 items per cell, got {bad_counts}")


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
    print(f"wrote {len(items)} items to {args.out}")


if __name__ == "__main__":
    main()
