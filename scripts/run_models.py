#!/usr/bin/env python
"""Run RePromptTax model trajectories.

The runner supports a dry-run mode for pipeline validation and an OpenAI API
mode for real experiments. It stops after the first automatically passing turn
to avoid unnecessary API spend.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

from score_auto import score_response


PROMPT_PATHS = {
    "baseline": Path("prompts/baseline_system.txt"),
    "contract": Path("prompts/global_interaction_contract.txt"),
    "content_preservation": Path("prompts/content_preservation_system.txt"),
    "generic_helpfulness": Path("prompts/generic_helpfulness_system.txt"),
}

DEFAULT_KEY_FILE = Path("/home/eston/colm_workshop/apikey.txt")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def usage_dict_from_response(resp: Any, prompt_text: str, output_text: str) -> dict[str, int]:
    usage = getattr(resp, "usage", None)
    if usage is None:
        return {
            "input_tokens": estimate_tokens(prompt_text),
            "output_tokens": estimate_tokens(output_text),
        }
    input_tokens = (
        getattr(usage, "input_tokens", None)
        or getattr(usage, "prompt_tokens", None)
        or getattr(usage, "total_input_tokens", None)
        or 0
    )
    output_tokens = (
        getattr(usage, "output_tokens", None)
        or getattr(usage, "completion_tokens", None)
        or getattr(usage, "total_output_tokens", None)
        or 0
    )
    if not input_tokens:
        input_tokens = estimate_tokens(prompt_text)
    if not output_tokens:
        output_tokens = estimate_tokens(output_text)
    return {"input_tokens": int(input_tokens), "output_tokens": int(output_tokens)}


def extract_responses_text(resp: Any) -> str:
    output_text = getattr(resp, "output_text", None)
    if output_text:
        return output_text
    chunks: list[str] = []
    for output_item in getattr(resp, "output", []) or []:
        for content in getattr(output_item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                chunks.append(text)
    if chunks:
        return "\n".join(chunks)
    choices = getattr(resp, "choices", None)
    if choices:
        message = getattr(choices[0], "message", None)
        content = getattr(message, "content", None)
        if content:
            return content
    return str(resp)


def call_openai(client: Any, model: str, messages: list[dict[str, str]], max_output_tokens: int) -> tuple[str, dict[str, int]]:
    prompt_text = "\n".join(f"{msg['role']}: {msg['content']}" for msg in messages)
    if hasattr(client, "responses"):
        kwargs = {
            "model": model,
            "input": messages,
            "max_output_tokens": max_output_tokens,
        }
        try:
            resp = client.responses.create(**kwargs, temperature=0)
        except TypeError:
            resp = client.responses.create(**kwargs)
        except Exception as exc:
            message = str(exc).lower()
            if "unsupported parameter" not in message or "temperature" not in message:
                raise
            resp = client.responses.create(**kwargs)
        text = extract_responses_text(resp).strip()
        return text, usage_dict_from_response(resp, prompt_text, text)

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        max_tokens=max_output_tokens,
    )
    text = resp.choices[0].message.content.strip()
    return text, usage_dict_from_response(resp, prompt_text, text)


def read_api_key(path: Path) -> str:
    key = path.read_text(encoding="utf-8").strip()
    if not key:
        raise ValueError(f"API key file is empty: {path}")
    return key


def passing_dry_response(item: dict[str, Any]) -> str:
    expected = item["expected_response_language"]
    family = item["task_family"]
    spans = item.get("must_preserve_spans", [])
    markers = item.get("required_any_markers", [])

    if family == "output_language_inference" and markers:
        return markers[0][0].upper() + markers[0][1:] + "."

    if expected == "English":
        marker = markers[0] if markers else "request"
        return f"Here is a polished English version that keeps the key point about {marker}."

    if expected == "Spanish":
        marker = markers[0] if markers else ""
        parts = [part for part in [*spans, marker] if part]
        preserved = " y ".join(dict.fromkeys(parts))
        return f"El texto dice que {preserved} es importante y resume la información de forma breve."

    if expected == "Hindi/Hinglish":
        if spans:
            return f"Ye update batata hai ki {spans[0]} aur {spans[-1]} important hai."
        marker = markers[0] if markers else "main"
        return f"Sorry, main {marker} ke baare mein short message bhej dunga."

    if expected == "Hindi":
        if spans:
            return f"यह सुधरा हुआ हिंदी पाठ {spans[0]} और {spans[-1]} को स्पष्ट रखता है।"
        marker = markers[0] if markers else "विषय"
        return f"यह सुधरा हुआ हिंदी पाठ {marker} को स्पष्ट रखता है।"

    if expected == "Arabic":
        preserved = " و ".join(spans) if spans else "الموضوع"
        return f"يوضح النص أن {preserved} مهم باختصار."

    return "Done."


def failing_dry_response(item: dict[str, Any]) -> str:
    family = item["task_family"]
    if family == "editing_preservation":
        return "Claro, aquí tienes una versión más profesional traducida al español."
    if family == "output_language_inference":
        return "La frase necesita una corrección gramatical, pero no doy la frase corregida."
    if family == "quote_preservation":
        return "El resumen traduce los nombres del proyecto y omite las frases exactas entre comillas."
    if family == "script_register_locale":
        return "I will send a short polite reply in English instead."
    return "This intentionally fails."


def dry_run_response(item: dict[str, Any], condition: str, turn: int) -> str:
    if condition == "contract":
        return passing_dry_response(item)
    if turn == 0:
        return failing_dry_response(item)
    return passing_dry_response(item)


def run_trajectory(
    *,
    item: dict[str, Any],
    model: str,
    condition: str,
    system_prompt: str,
    client: Any | None,
    dry_run: bool,
    max_output_tokens: int,
) -> list[dict[str, Any]]:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": item["user_prompt"]},
    ]
    rows: list[dict[str, Any]] = []
    repair_prompts = [item["repair_prompt_1"], item["repair_prompt_2"]]

    for turn in range(3):
        if dry_run:
            response = dry_run_response(item, condition, turn)
            usage = {
                "input_tokens": estimate_tokens("\n".join(msg["content"] for msg in messages)),
                "output_tokens": estimate_tokens(response),
            }
        else:
            if client is None:
                raise RuntimeError("client is required outside dry-run mode")
            response, usage = call_openai(client, model, messages, max_output_tokens)

        score = score_response(item, response)
        row = {
            "item_id": item["id"],
            "model": model,
            "condition": condition,
            "turn": turn,
            "response": response,
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "auto_pass_at_run": score["pass"],
            "auto_failure_types_at_run": score["failure_types"],
        }
        rows.append(row)
        if score["pass"] or turn == 2:
            break

        messages.append({"role": "assistant", "content": response})
        messages.append({"role": "user", "content": repair_prompts[turn]})

    return rows


def parse_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--models", required=True, help="Comma-separated model names")
    parser.add_argument("--conditions", default="baseline,contract")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--item-id", action="append", default=[])
    parser.add_argument("--item-id-file", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--api-key-file", type=Path, default=DEFAULT_KEY_FILE)
    parser.add_argument("--max-output-tokens", type=int, default=512)
    parser.add_argument("--max-api-calls", type=int, default=40)
    parser.add_argument("--append", action="store_true")
    args = parser.parse_args()

    requested_ids = list(args.item_id)
    if args.item_id_file is not None:
        requested_ids.extend(
            line.strip()
            for line in args.item_id_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )

    items = load_jsonl(args.benchmark)
    if requested_ids:
        requested = set(requested_ids)
        items = [item for item in items if item["id"] in requested]
        missing = requested.difference(item["id"] for item in items)
        if missing:
            raise KeyError(f"missing requested item ids: {sorted(missing)}")
    if args.limit is not None:
        items = items[: args.limit]

    models = parse_csv(args.models)
    conditions = parse_csv(args.conditions)
    for condition in conditions:
        if condition not in PROMPT_PATHS:
            raise ValueError(f"unknown condition: {condition}")

    client = None
    if not args.dry_run:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise SystemExit("OpenAI SDK is not installed in this environment") from exc
        client = OpenAI(api_key=read_api_key(args.api_key_file))

    api_calls = 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if args.append else "w"
    written = 0
    with args.out.open(mode, encoding="utf-8") as f:
        for item in items:
            for model in models:
                for condition in conditions:
                    if not args.dry_run and api_calls >= args.max_api_calls:
                        print(f"stopped at max api calls: {args.max_api_calls}", file=sys.stderr)
                        print(f"wrote {written} rows to {args.out}")
                        return
                    system_prompt = read_text(PROMPT_PATHS[condition])
                    rows = run_trajectory(
                        item=item,
                        model=model,
                        condition=condition,
                        system_prompt=system_prompt,
                        client=client,
                        dry_run=args.dry_run,
                        max_output_tokens=args.max_output_tokens,
                    )
                    if not args.dry_run:
                        api_calls += len(rows)
                    for row in rows:
                        f.write(json.dumps(row, ensure_ascii=False) + "\n")
                        written += 1

    print(f"wrote {written} rows to {args.out}")
    if not args.dry_run:
        print(f"api calls used: {api_calls}")


if __name__ == "__main__":
    main()
