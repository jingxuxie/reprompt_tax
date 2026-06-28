#!/usr/bin/env python
"""Automatic scorer for RePromptTax outputs.

This scorer is intentionally lightweight. It should be treated as a triage
signal and paired with LLM-judge or human audit for paper claims.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ARABIC_RE = re.compile(r"[\u0600-\u06ff]")
DEVANAGARI_RE = re.compile(r"[\u0900-\u097f]")
LATIN_RE = re.compile(r"[A-Za-z]")

SPANISH_MARKERS = {
    " el ",
    " la ",
    " los ",
    " las ",
    " de ",
    " que ",
    " por ",
    " para ",
    " con ",
    " gracias",
    " hola",
    " puedo",
    " puedes",
    " voy",
    " llego",
    " mañana",
    " archivo",
    " reunión",
    " música",
    " favor",
    " resumen",
    " texto",
    " dice",
    " podrías",
    " podría",
    " cliente",
    " pago",
    " próxima",
    " semana",
    " llegará",
}

SPANISH_ACCENTS = set("áéíóúñÁÉÍÓÚÑ")
SPANISH_PUNCTUATION = set("¿¡")

HINGLISH_MARKERS = {
    " hai",
    " hoon",
    " hun",
    " main",
    " mein",
    " kal",
    " aaj",
    " nahi",
    " mat",
    " karo",
    " karna",
    " bhej",
    " pahunch",
    " aaunga",
    " aaungi",
    " thoda",
    " kripya",
    " shukriya",
    " yaar",
    " hoga",
    " hogi",
    " ke ",
    " ko ",
    " par ",
    " se ",
    " ne ",
    " kiya",
    " diya",
    " dena",
    " chhod",
    " aane",
    " aate",
    " assign",
    " shikshak",
    " worksheet",
    " waise",
    " rehna",
    " chahiye",
}

WRONG_LANGUAGE_PREFIXES = [
    "claro",
    "por supuesto",
    "aquí tienes",
    "estimado",
    "ترجمة",
    "بالطبع",
    "إليك",
    "प्रिय",
    "नमस्ते",
]

OVER_FORMAL_MARKERS = [
    "dear sir or madam",
    "to whom it may concern",
    "i humbly request",
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON") from exc
    return rows


def strip_preserved_spans(text: str, spans: list[str]) -> str:
    stripped = text
    for span in spans:
        stripped = stripped.replace(span, " ")
    return stripped


def script_counts(text: str) -> dict[str, int]:
    return {
        "arabic": len(ARABIC_RE.findall(text)),
        "devanagari": len(DEVANAGARI_RE.findall(text)),
        "latin": len(LATIN_RE.findall(text)),
    }


def has_any_marker(text: str, markers: list[str]) -> bool:
    if not markers:
        return True
    low = text.lower()
    for marker in markers:
        marker_low = marker.lower()
        if marker_low in low:
            return True
    return False


def has_forbidden_marker(text: str, markers: list[str]) -> bool:
    low = text.lower()
    return any(marker.lower() in low for marker in markers if marker)


def language_pass(response: str, item: dict[str, Any]) -> bool:
    expected = item["expected_response_language"].lower()
    spans = item.get("must_preserve_spans", [])
    stripped = strip_preserved_spans(response, spans)
    counts = script_counts(stripped)
    low_padded = f" {stripped.lower()} "

    if expected == "english":
        if counts["arabic"] or counts["devanagari"]:
            return False
        if any(ch in stripped for ch in SPANISH_ACCENTS | SPANISH_PUNCTUATION):
            return False
        if any(marker in low_padded for marker in SPANISH_MARKERS):
            return False
        if any(prefix in low_padded for prefix in WRONG_LANGUAGE_PREFIXES):
            return False
        return counts["latin"] >= 8

    if expected == "spanish":
        if counts["arabic"] or counts["devanagari"]:
            return False
        if any(ch in stripped for ch in SPANISH_ACCENTS):
            return True
        return any(marker in low_padded for marker in SPANISH_MARKERS)

    if expected == "arabic":
        return counts["arabic"] >= 4

    if expected == "hindi/hinglish":
        if counts["arabic"] or counts["devanagari"]:
            return False
        if counts["latin"] < 4:
            return False
        return any(marker in low_padded for marker in HINGLISH_MARKERS)

    return True


def script_pass(response: str, item: dict[str, Any]) -> bool:
    expected = item["expected_script"].lower()
    spans = item.get("must_preserve_spans", [])
    stripped = strip_preserved_spans(response, spans)
    counts = script_counts(stripped)

    if expected == "latin":
        return counts["arabic"] == 0 and counts["devanagari"] == 0 and counts["latin"] >= 4
    if expected == "arabic":
        return counts["arabic"] >= 4 and counts["devanagari"] == 0
    if expected == "devanagari":
        return counts["devanagari"] >= 4
    return True


def preservation_pass(response: str, item: dict[str, Any]) -> bool:
    spans = item.get("must_preserve_spans", [])
    return all(span in response for span in spans)


def task_pass(response: str, item: dict[str, Any]) -> bool:
    if len(response.strip()) < 3:
        return False
    if has_forbidden_marker(response, item.get("forbidden_markers", [])):
        return False
    family = item["task_family"]
    if family == "quote_preservation":
        return preservation_pass(response, item)
    return has_any_marker(response, item.get("required_any_markers", []))


def register_locale_pass(response: str, item: dict[str, Any]) -> bool:
    low = response.lower()
    if item["task_family"] == "script_register_locale":
        if any(marker in low for marker in OVER_FORMAL_MARKERS):
            return False
        return len(response.split()) <= 80
    return True


def score_response(item: dict[str, Any], response: str) -> dict[str, Any]:
    checks = {
        "language_pass": language_pass(response, item),
        "script_pass": script_pass(response, item),
        "preservation_pass": preservation_pass(response, item),
        "task_pass": task_pass(response, item),
        "register_locale_pass": register_locale_pass(response, item),
    }

    failure_types: list[str] = []
    if not checks["language_pass"]:
        failure_types.append("wrong_output_language")
    if not checks["script_pass"]:
        failure_types.append("script_mismatch")
    if not checks["preservation_pass"]:
        failure_types.append("preservation_failure")
    if not checks["task_pass"]:
        failure_types.append("task_noncompletion")
    if not checks["register_locale_pass"]:
        failure_types.append("register_locale_mismatch")

    passed = all(checks.values())
    return {
        "pass": passed,
        **checks,
        "failure_types": failure_types,
        "short_reason": "passes automatic checks" if passed else ", ".join(failure_types),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    items = {item["id"]: item for item in load_jsonl(args.benchmark)}
    outputs = load_jsonl(args.outputs)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    with args.out.open("w", encoding="utf-8") as f:
        for row in outputs:
            item_id = row["item_id"]
            if item_id not in items:
                raise KeyError(f"unknown item_id in outputs: {item_id}")
            score = score_response(items[item_id], row.get("response", ""))
            merged = {
                **row,
                **score,
                "task_family": items[item_id]["task_family"],
                "language_pair": items[item_id]["language_pair"],
            }
            f.write(json.dumps(merged, ensure_ascii=False) + "\n")

    print(f"scored {len(outputs)} responses to {args.out}")


if __name__ == "__main__":
    main()
