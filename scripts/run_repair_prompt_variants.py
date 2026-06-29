#!/usr/bin/env python
"""Run user-like repair prompt variants for saved first-turn failures."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from run_models import DEFAULT_KEY_FILE, PROMPT_PATHS, call_openai, read_api_key, read_text
from score_auto import score_response


SOURCE_LANGUAGE_BY_PAIR = {
    "ar-en": "Arabic",
    "es-en": "Spanish",
    "hi-en": "Hindi/Hinglish",
}


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


def row_key(row: dict[str, Any]) -> tuple[str, str, str, int]:
    return (row["item_id"], row["model"], row["condition"], int(row["turn"]))


def variant_prompt(variant: str, item: dict[str, Any]) -> str:
    if variant == "terse_keep_english":
        return "No, keep it in English."
    if variant == "frustrated_dont_translate":
        return "I meant don't translate it."
    if variant == "explicit_contract":
        source_language = SOURCE_LANGUAGE_BY_PAIR.get(item["language_pair"], "the instruction language")
        return f"The instruction is {source_language}, but the content should remain English."
    raise ValueError(f"unknown repair variant: {variant}")


def selected_failures(
    *,
    score_rows: list[dict[str, Any]],
    task_family: str,
    condition: str,
    sample_size: int,
    seed: int,
) -> list[dict[str, Any]]:
    candidates = [
        row
        for row in score_rows
        if int(row["turn"]) == 0
        and row["task_family"] == task_family
        and row["condition"] == condition
        and not bool(row["pass"])
    ]
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in candidates:
        grouped[(row["model"], row["language_pair"])].append(row)
    rng = random.Random(seed)
    selected: list[dict[str, Any]] = []
    group_keys = sorted(grouped)
    base_per_group = sample_size // len(group_keys)
    remainder = sample_size % len(group_keys)
    for idx, key in enumerate(group_keys):
        group = sorted(grouped[key], key=lambda row: row["item_id"])
        take = base_per_group + (1 if idx < remainder else 0)
        if len(group) < take:
            raise ValueError(f"not enough candidates for {key}: need {take}, found {len(group)}")
        selected.extend(sorted(rng.sample(group, take), key=lambda row: row["item_id"]))
    return sorted(selected, key=lambda row: (row["model"], row["language_pair"], row["item_id"]))


def standard_repair_row(
    *,
    first_turn: dict[str, Any],
    item: dict[str, Any],
    scores_by_key: dict[tuple[str, str, str, int], dict[str, Any]],
) -> dict[str, Any]:
    key = (first_turn["item_id"], first_turn["model"], first_turn["condition"], 1)
    if key not in scores_by_key:
        raise KeyError(f"missing saved standardized repair row for {key}")
    saved = scores_by_key[key]
    return {
        "item_id": first_turn["item_id"],
        "model": first_turn["model"],
        "condition": first_turn["condition"],
        "task_family": first_turn["task_family"],
        "language_pair": first_turn["language_pair"],
        "first_turn_response": first_turn["response"],
        "first_turn_failure_types": first_turn["failure_types"],
        "repair_variant": "standard_saved",
        "repair_prompt": item["repair_prompt_1"],
        "response": saved["response"],
        "input_tokens": saved["input_tokens"],
        "output_tokens": saved["output_tokens"],
        "created_at": saved["created_at"],
        "source": "saved_main_trajectory",
        "pass": saved["pass"],
        "language_pass": saved["language_pass"],
        "script_pass": saved["script_pass"],
        "preservation_pass": saved["preservation_pass"],
        "task_pass": saved["task_pass"],
        "register_locale_pass": saved["register_locale_pass"],
        "failure_types": saved["failure_types"],
        "short_reason": saved["short_reason"],
    }


def call_variant(
    *,
    client: Any,
    first_turn: dict[str, Any],
    item: dict[str, Any],
    variant: str,
    max_output_tokens: int,
) -> dict[str, Any]:
    repair = variant_prompt(variant, item)
    messages = [
        {"role": "system", "content": read_text(PROMPT_PATHS[first_turn["condition"]])},
        {"role": "user", "content": item["user_prompt"]},
        {"role": "assistant", "content": first_turn["response"]},
        {"role": "user", "content": repair},
    ]
    response, usage = call_openai(client, first_turn["model"], messages, max_output_tokens)
    score = score_response(item, response)
    return {
        "item_id": first_turn["item_id"],
        "model": first_turn["model"],
        "condition": first_turn["condition"],
        "task_family": first_turn["task_family"],
        "language_pair": first_turn["language_pair"],
        "first_turn_response": first_turn["response"],
        "first_turn_failure_types": first_turn["failure_types"],
        "repair_variant": variant,
        "repair_prompt": repair,
        "response": response,
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": "repair_variant_api",
        **score,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, default=Path("data/benchmark_stress_v0.2.jsonl"))
    parser.add_argument("--scores", type=Path, default=Path("results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--task-family", default="editing_preservation")
    parser.add_argument("--condition", default="baseline")
    parser.add_argument("--sample-size", type=int, default=24)
    parser.add_argument("--seed", type=int, default=29)
    parser.add_argument("--api-key-file", type=Path, default=DEFAULT_KEY_FILE)
    parser.add_argument("--max-output-tokens", type=int, default=256)
    parser.add_argument("--max-api-calls", type=int, default=72)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    items = {item["id"]: item for item in load_jsonl(args.benchmark)}
    score_rows = load_jsonl(args.scores)
    scores_by_key = {row_key(row): row for row in score_rows}
    first_turns = selected_failures(
        score_rows=score_rows,
        task_family=args.task_family,
        condition=args.condition,
        sample_size=args.sample_size,
        seed=args.seed,
    )

    existing_keys: set[tuple[str, str, str, str]] = set()
    if args.resume and args.out.exists():
        existing_rows = load_jsonl(args.out)
        existing_keys = {(row["item_id"], row["model"], row["condition"], row["repair_variant"]) for row in existing_rows}

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit("OpenAI SDK is not installed in this environment") from exc
    client = OpenAI(api_key=read_api_key(args.api_key_file))

    variants = ["standard_saved", "terse_keep_english", "frustrated_dont_translate", "explicit_contract"]
    api_variants = [variant for variant in variants if variant != "standard_saved"]
    api_calls = 0
    written = 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if args.resume and args.out.exists() else "w"
    with args.out.open(mode, encoding="utf-8") as f:
        for first_turn in first_turns:
            item = items[first_turn["item_id"]]
            if (first_turn["item_id"], first_turn["model"], first_turn["condition"], "standard_saved") not in existing_keys:
                row = standard_repair_row(first_turn=first_turn, item=item, scores_by_key=scores_by_key)
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                written += 1
            for variant in api_variants:
                key = (first_turn["item_id"], first_turn["model"], first_turn["condition"], variant)
                if key in existing_keys:
                    continue
                if api_calls >= args.max_api_calls:
                    print(f"stopped at max api calls: {args.max_api_calls}", file=sys.stderr)
                    print(f"selected {len(first_turns)} first-turn failures; wrote {written} rows to {args.out}")
                    print(f"api calls used: {api_calls}")
                    return
                row = call_variant(
                    client=client,
                    first_turn=first_turn,
                    item=item,
                    variant=variant,
                    max_output_tokens=args.max_output_tokens,
                )
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                written += 1
                api_calls += 1

    print(f"selected {len(first_turns)} first-turn failures; wrote {written} rows to {args.out}")
    print(f"api calls used: {api_calls}")


if __name__ == "__main__":
    main()
