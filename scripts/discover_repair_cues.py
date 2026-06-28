#!/usr/bin/env python
"""Aggregate-only repair-cue discovery in public chat datasets.

This script does not write raw user text. It scans follow-up user turns for
predefined repair cues and outputs aggregate counts plus hashed hit metadata.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

CUE_PATTERNS: dict[str, list[str]] = {
    "wrong_output_language": [
        r"\bin english\b",
        r"\bnot in english\b",
        r"\bwrong language\b",
        r"\bi said english\b",
        r"\banswer in (english|spanish|arabic|hindi)\b",
        r"\buse (english|spanish|arabic|hindi)\b",
        r"\ben ingl[eé]s\b",
        r"\ben espa[nñ]ol\b",
        r"\benglish mein\b",
        r"\bhindi mein\b",
        r"بالإنجليزية",
        r"بالانجليزية",
        r"بالعربية",
    ],
    "unwanted_translation": [
        r"\bdon'?t translate\b",
        r"\bdo not translate\b",
        r"\bwithout translating\b",
        r"\bkeep (it|this|the text) in\b",
        r"\bsame language\b",
        r"\bno traduzcas\b",
        r"\bmant[eé]n.*idioma\b",
        r"\btranslate mat karo\b",
        r"\bsame language mein\b",
        r"لا تترجم",
        r"نفس اللغة",
    ],
    "script_mismatch": [
        r"\blatin script\b",
        r"\bromanized\b",
        r"\bnot devanagari\b",
        r"\bno devanagari\b",
        r"\benglish letters\b",
        r"\buse roman\b",
        r"\bhuruf latin\b",
        r"الحروف اللاتينية",
    ],
    "preservation_failure": [
        r"\bkeep .* exactly\b",
        r"\bkeep .* as written\b",
        r"\bkeep .* as-is\b",
        r"\bdon'?t change\b",
        r"\bdo not change\b",
        r"\bpreserve\b",
        r"\bno cambies\b",
        r"\bexactamente\b",
        r"كما هي",
    ],
    "register_locale_mismatch": [
        r"\bmore formal\b",
        r"\btoo formal\b",
        r"\bmore polite\b",
        r"\btoo casual\b",
        r"\bnot rude\b",
        r"\brespectful\b",
        r"\buse rupees\b",
        r"\bnot dollars\b",
        r"\bdate format\b",
    ],
    "generic_repair": [
        r"\bthat'?s not what i asked\b",
        r"\bi meant\b",
        r"\btry again\b",
        r"\bplease revise\b",
        r"\bnot what i wanted\b",
        r"\bte dije\b",
        r"\bno es lo que\b",
        r"ليس هذا ما طلبته",
    ],
}


def compile_patterns() -> dict[str, list[re.Pattern[str]]]:
    return {
        category: [re.compile(pattern, flags=re.IGNORECASE) for pattern in patterns]
        for category, patterns in CUE_PATTERNS.items()
    }


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:16]


def load_stream(dataset: str, split: str) -> Iterable[dict[str, Any]]:
    from datasets import load_dataset

    return load_dataset(dataset, split=split, streaming=True)


def message_role(message: dict[str, Any]) -> str:
    return str(message.get("role", "")).lower()


def message_text(message: dict[str, Any]) -> str:
    return str(message.get("content", "") or "")


def conversation_id(row: dict[str, Any], index: int) -> str:
    for key in ("conversation_id", "id", "conversation_hash"):
        if row.get(key):
            return str(row[key])
    return f"row-{index}"


def scan_row(
    row: dict[str, Any],
    row_index: int,
    patterns: dict[str, list[re.Pattern[str]]],
) -> tuple[dict[str, int], list[dict[str, Any]], int, int]:
    conversation = row.get("conversation")
    if not isinstance(conversation, list):
        return {}, [], 0, 0

    user_turn_seen = 0
    user_turns = 0
    hit_counts: Counter[str] = Counter()
    hits: list[dict[str, Any]] = []
    conv_id = conversation_id(row, row_index)
    conv_hash = stable_hash(conv_id)

    for msg_idx, message in enumerate(conversation):
        if not isinstance(message, dict) or message_role(message) != "user":
            continue
        user_turns += 1
        user_turn_seen += 1
        if user_turn_seen == 1:
            continue
        text = message_text(message)
        low = text.lower()
        for category, category_patterns in patterns.items():
            for pattern in category_patterns:
                if pattern.search(low):
                    hit_counts[category] += 1
                    hits.append(
                        {
                            "conversation_hash": conv_hash,
                            "message_index": msg_idx,
                            "user_turn_index": user_turn_seen,
                            "category": category,
                            "cue_pattern": pattern.pattern,
                            "row_language": row.get("language", ""),
                            "message_language": message.get("language", ""),
                        }
                    )
                    break

    return dict(hit_counts), hits, user_turns, 1 if user_turns >= 2 else 0


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="allenai/WildChat")
    parser.add_argument("--split", default="train")
    parser.add_argument("--max-conversations", type=int, default=5000)
    parser.add_argument("--out-dir", type=Path, default=Path("results/discovery/wildchat_repair_cues"))
    args = parser.parse_args()

    patterns = compile_patterns()
    rows_seen = 0
    user_turns = 0
    multiturn_conversations = 0
    conversations_with_hits: set[str] = set()
    category_counts: Counter[str] = Counter()
    language_counts: Counter[str] = Counter()
    hit_rows: list[dict[str, Any]] = []

    for row_index, row in enumerate(load_stream(args.dataset, args.split)):
        if rows_seen >= args.max_conversations:
            break
        rows_seen += 1
        counts, hits, row_user_turns, has_multiturn = scan_row(row, row_index, patterns)
        user_turns += row_user_turns
        multiturn_conversations += has_multiturn
        if hits:
            conversations_with_hits.add(stable_hash(conversation_id(row, row_index)))
            language_counts[str(row.get("language", ""))] += 1
        category_counts.update(counts)
        hit_rows.extend(hits)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "dataset": args.dataset,
        "split": args.split,
        "max_conversations": args.max_conversations,
        "conversations_scanned": rows_seen,
        "user_turns_scanned": user_turns,
        "multiturn_conversations": multiturn_conversations,
        "conversations_with_repair_cues": len(conversations_with_hits),
        "cue_hits_total": sum(category_counts.values()),
        "category_counts": dict(sorted(category_counts.items())),
        "conversation_language_counts_with_hits": dict(sorted(language_counts.items())),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "raw_text_written": False,
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(args.out_dir / "category_counts.csv", [{"category": key, "count": value} for key, value in sorted(category_counts.items())])
    write_csv(args.out_dir / "hit_metadata_hashed.csv", hit_rows)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    sys.stdout.flush()
    # Avoid rare PyArrow/HF streaming finalizer crashes after all artifacts are
    # safely written. This keeps the command usable in CI and latex pipelines.
    os._exit(0)


if __name__ == "__main__":
    main()
