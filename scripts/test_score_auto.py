#!/usr/bin/env python
"""Regression tests for the deterministic RePromptTax automatic scorer."""

from __future__ import annotations

from score_auto import score_response


def item(
    *,
    expected_response_language: str = "English",
    expected_script: str = "Latin",
    task_family: str = "editing_preservation",
    must_preserve_spans: list[str] | None = None,
    required_any_markers: list[str] | None = None,
    forbidden_markers: list[str] | None = None,
) -> dict:
    return {
        "expected_response_language": expected_response_language,
        "expected_script": expected_script,
        "task_family": task_family,
        "must_preserve_spans": must_preserve_spans or [],
        "required_any_markers": required_any_markers or [],
        "forbidden_markers": forbidden_markers or [],
    }


CASES = [
    {
        "name": "english_editing_pass",
        "item": item(required_any_markers=["call today", "email"]),
        "response": "I can't join the call today, but I can share my update by email.",
        "expected_pass": True,
        "expected_failures": [],
    },
    {
        "name": "spanish_preamble_and_no_required_marker_fail",
        "item": item(required_any_markers=["call today", "email"]),
        "response": "Claro, aquí tienes una versión más natural.",
        "expected_pass": False,
        "expected_failures": ["wrong_output_language", "task_noncompletion"],
    },
    {
        "name": "spanish_sentence_with_required_markers_for_english_fail",
        "item": item(required_any_markers=["client", "payment", "next week"]),
        "response": "¿Podrías decirle al cliente que el pago llegará la próxima semana?",
        "expected_pass": False,
        "expected_failures": ["wrong_output_language"],
    },
    {
        "name": "arabic_script_for_english_latin_fail",
        "item": item(required_any_markers=["invoice"]),
        "response": "بالطبع سأراجع الفاتورة الليلة.",
        "expected_pass": False,
        "expected_failures": ["wrong_output_language", "script_mismatch", "task_noncompletion"],
    },
    {
        "name": "quote_preservation_pass",
        "item": item(
            expected_response_language="Arabic",
            expected_script="Arabic",
            task_family="quote_preservation",
            must_preserve_spans=["Budget Review", "Community Questions"],
            required_any_markers=["Budget Review", "Community Questions"],
        ),
        "response": 'تذكر الوثيقة "Budget Review" قبل "Community Questions".',
        "expected_pass": True,
        "expected_failures": [],
    },
    {
        "name": "quote_preservation_fail",
        "item": item(
            expected_response_language="Arabic",
            expected_script="Arabic",
            task_family="quote_preservation",
            must_preserve_spans=["Budget Review", "Community Questions"],
            required_any_markers=["Budget Review", "Community Questions"],
        ),
        "response": "تذكر الوثيقة مراجعة الميزانية قبل أسئلة المجتمع.",
        "expected_pass": False,
        "expected_failures": ["preservation_failure", "task_noncompletion"],
    },
    {
        "name": "literal_locale_span_fail",
        "item": item(
            expected_response_language="Arabic",
            expected_script="Arabic",
            task_family="script_register_locale",
            must_preserve_spans=["₹500"],
            required_any_markers=["₹500"],
        ),
        "response": "دفعت ٥٠٠ روبية وسأرسل الإيصال غداً.",
        "expected_pass": False,
        "expected_failures": ["preservation_failure", "task_noncompletion"],
    },
    {
        "name": "register_locale_overformal_fail",
        "item": item(
            task_family="script_register_locale",
            must_preserve_spans=["ABC-17"],
            required_any_markers=["ABC-17"],
        ),
        "response": "Dear Sir or Madam, the booking code ABC-17 is correct and I will arrive after lunch.",
        "expected_pass": False,
        "expected_failures": ["register_locale_mismatch"],
    },
    {
        "name": "hinglish_latin_pass",
        "item": item(
            expected_response_language="Hindi/Hinglish",
            expected_script="Latin",
            task_family="script_register_locale",
            must_preserve_spans=["draft_v2.pdf"],
            required_any_markers=["draft_v2.pdf", "file"],
        ),
        "response": "File draft_v2.pdf same rehna chahiye, change mat karo.",
        "expected_pass": True,
        "expected_failures": [],
    },
    {
        "name": "hinglish_devanagari_fail",
        "item": item(
            expected_response_language="Hindi/Hinglish",
            expected_script="Latin",
            task_family="script_register_locale",
            must_preserve_spans=["draft_v2.pdf"],
            required_any_markers=["draft_v2.pdf", "file"],
        ),
        "response": "फ़ाइल draft_v2.pdf को मत बदलना.",
        "expected_pass": False,
        "expected_failures": ["wrong_output_language", "script_mismatch"],
    },
    {
        "name": "spanish_language_pass",
        "item": item(expected_response_language="Spanish", expected_script="Latin", required_any_markers=["recibo"]),
        "response": "Gracias, enviaré el recibo mañana.",
        "expected_pass": True,
        "expected_failures": [],
    },
]


def main() -> None:
    for case in CASES:
        score = score_response(case["item"], case["response"])
        if score["pass"] != case["expected_pass"]:
            raise AssertionError(f"{case['name']} pass mismatch: {score}")
        if score["failure_types"] != case["expected_failures"]:
            raise AssertionError(
                f"{case['name']} failure mismatch: expected {case['expected_failures']}, got {score['failure_types']}"
            )
    print(f"score-auto regression tests passed for {len(CASES)} cases")


if __name__ == "__main__":
    main()
