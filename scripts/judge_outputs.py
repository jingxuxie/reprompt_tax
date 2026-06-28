#!/usr/bin/env python
"""Run a blinded LLM judge over RePromptTax outputs."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from run_models import DEFAULT_KEY_FILE, call_openai, read_api_key


JUDGE_SYSTEM = """You are a strict evaluator of multilingual LLM responses.
You evaluate whether the assistant response satisfies the user's interaction
contract. Do not reward general helpfulness if the response violates language,
script, exact-span preservation, locale, register, or task constraints.
Return JSON only."""


JUDGE_USER_TEMPLATE = """Evaluate the assistant response below.

User prompt:
{user_prompt}

Expected contract:
- expected_response_language: {expected_response_language}
- expected_script: {expected_script}
- must_preserve_spans: {must_preserve_spans}
- register_requirement: {register_requirement}
- locale_requirement: {locale_requirement}
- task_family: {task_family}
- known_bad_outputs: {known_bad_outputs}
- notes_for_annotators: {notes_for_annotators}

Assistant response:
{assistant_response}

Return exactly this JSON shape:
{{
  "pass": true,
  "language_pass": true,
  "script_pass": true,
  "preservation_pass": true,
  "task_pass": true,
  "register_locale_pass": true,
  "failure_types": [],
  "short_reason": "one sentence"
}}
"""


BOOL_FIELDS = [
    "pass",
    "language_pass",
    "script_pass",
    "preservation_pass",
    "task_pass",
    "register_locale_pass",
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


def dump_jsonl(path: Path, rows: list[dict[str, Any]], append: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with path.open(mode, encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.lower().startswith("json"):
            stripped = stripped[4:].strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end <= start:
            raise
        parsed = json.loads(stripped[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("judge response was not a JSON object")
    return parsed


def normalize_judgment(parsed: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for field in BOOL_FIELDS:
        out[field] = bool(parsed.get(field, False))
    failure_types = parsed.get("failure_types", [])
    if not isinstance(failure_types, list):
        failure_types = [str(failure_types)]
    out["failure_types"] = [str(item) for item in failure_types]
    out["short_reason"] = str(parsed.get("short_reason", "")).strip()
    out["pass"] = all(out[field] for field in BOOL_FIELDS if field != "pass") if parsed.get("pass") is None else out["pass"]
    return out


def build_messages(item: dict[str, Any], response: str) -> list[dict[str, str]]:
    user = JUDGE_USER_TEMPLATE.format(
        user_prompt=item["user_prompt"],
        expected_response_language=item["expected_response_language"],
        expected_script=item["expected_script"],
        must_preserve_spans=json.dumps(item.get("must_preserve_spans", []), ensure_ascii=False),
        register_requirement=item.get("register_requirement"),
        locale_requirement=item.get("locale_requirement"),
        task_family=item["task_family"],
        known_bad_outputs=json.dumps(item.get("known_bad_outputs", []), ensure_ascii=False),
        notes_for_annotators=item.get("notes_for_annotators", ""),
        assistant_response=response,
    )
    return [
        {"role": "system", "content": JUDGE_SYSTEM},
        {"role": "user", "content": user},
    ]


def row_key(row: dict[str, Any]) -> tuple[str, str, str, int]:
    return (row["item_id"], row["model"], row["condition"], int(row["turn"]))


def select_rows(
    rows: list[dict[str, Any]],
    *,
    turn: int | None,
    sample_per_stratum: int | None,
    seed: int,
    limit: int | None,
) -> list[dict[str, Any]]:
    if turn is not None:
        rows = [row for row in rows if int(row["turn"]) == turn]
    rows = sorted(rows, key=lambda row: (row["model"], row["condition"], row.get("task_family", ""), row["item_id"], row["turn"]))

    if sample_per_stratum is not None:
        rng = random.Random(seed)
        grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[(row["model"], row["condition"], row.get("task_family", ""))].append(row)
        sampled: list[dict[str, Any]] = []
        for key in sorted(grouped):
            group = grouped[key]
            if len(group) <= sample_per_stratum:
                sampled.extend(group)
            else:
                sampled.extend(sorted(rng.sample(group, sample_per_stratum), key=lambda row: (row["item_id"], row["turn"])))
        rows = sampled

    if limit is not None:
        rows = rows[:limit]
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument("--scores", type=Path, required=True, help="Auto-scored JSONL to audit")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--judge-model", default="gpt-4.1")
    parser.add_argument("--api-key-file", type=Path, default=DEFAULT_KEY_FILE)
    parser.add_argument("--max-output-tokens", type=int, default=350)
    parser.add_argument("--max-api-calls", type=int, default=80)
    parser.add_argument("--turn", type=int, default=0, help="Turn to judge; use -1 for all turns")
    parser.add_argument("--sample-per-stratum", type=int, default=None)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--append", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    items = {item["id"]: item for item in load_jsonl(args.benchmark)}
    score_rows = load_jsonl(args.scores)
    turn = None if args.turn < 0 else args.turn
    selected = select_rows(
        score_rows,
        turn=turn,
        sample_per_stratum=args.sample_per_stratum,
        seed=args.seed,
        limit=args.limit,
    )

    existing_keys: set[tuple[str, str, str, int]] = set()
    if args.resume and args.out.exists():
        existing_keys = {row_key(row) for row in load_jsonl(args.out)}
        selected = [row for row in selected if row_key(row) not in existing_keys]

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit("OpenAI SDK is not installed in this environment") from exc

    client = OpenAI(api_key=read_api_key(args.api_key_file))
    judged_rows: list[dict[str, Any]] = []
    api_calls = 0

    for row in selected:
        if api_calls >= args.max_api_calls:
            print(f"stopped at max api calls: {args.max_api_calls}", file=sys.stderr)
            break
        item = items[row["item_id"]]
        messages = build_messages(item, row.get("response", ""))
        raw_response, usage = call_openai(client, args.judge_model, messages, args.max_output_tokens)
        api_calls += 1
        try:
            judgment = normalize_judgment(parse_json_object(raw_response))
            parse_error = None
        except Exception as exc:  # noqa: BLE001
            judgment = {
                "pass": False,
                "language_pass": False,
                "script_pass": False,
                "preservation_pass": False,
                "task_pass": False,
                "register_locale_pass": False,
                "failure_types": ["judge_parse_error"],
                "short_reason": "judge response could not be parsed",
            }
            parse_error = str(exc)

        judged_rows.append(
            {
                "item_id": row["item_id"],
                "model": row["model"],
                "condition": row["condition"],
                "turn": row["turn"],
                "task_family": row.get("task_family"),
                "language_pair": row.get("language_pair"),
                "auto_pass": row.get("pass"),
                "auto_failure_types": row.get("failure_types", []),
                "judge_model": args.judge_model,
                "judge_pass": judgment["pass"],
                "judge_language_pass": judgment["language_pass"],
                "judge_script_pass": judgment["script_pass"],
                "judge_preservation_pass": judgment["preservation_pass"],
                "judge_task_pass": judgment["task_pass"],
                "judge_register_locale_pass": judgment["register_locale_pass"],
                "judge_failure_types": judgment["failure_types"],
                "judge_short_reason": judgment["short_reason"],
                "judge_raw_response": raw_response,
                "judge_parse_error": parse_error,
                "judge_input_tokens": usage["input_tokens"],
                "judge_output_tokens": usage["output_tokens"],
                "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            }
        )

    dump_jsonl(args.out, judged_rows, append=args.append or (args.resume and args.out.exists()))
    print(f"selected {len(selected)} rows; judged {len(judged_rows)} rows to {args.out}")
    print(f"api calls used: {api_calls}")


if __name__ == "__main__":
    main()
