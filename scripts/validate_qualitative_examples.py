#!/usr/bin/env python
"""Validate qualitative examples against saved RePromptTax score artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


EXAMPLES = [
    {
        "name": "unwanted_translation_editing",
        "item_id": "es_en_SA_004",
        "model": "gpt-4.1-nano",
        "condition": "baseline",
        "rtt": 1,
        "turns": {
            0: {
                "pass": False,
                "failure_types": {"wrong_output_language", "task_noncompletion"},
                "snippets": ["No puedo unirme a la llamada hoy"],
            },
            1: {
                "pass": True,
                "failure_types": set(),
                "snippets": ["I won't be able to join the call today"],
            },
        },
    },
    {
        "name": "strong_model_preamble_tax",
        "item_id": "es_en_SA_004",
        "model": "gpt-4.1",
        "condition": "baseline",
        "rtt": 1,
        "turns": {
            0: {
                "pass": False,
                "failure_types": {"wrong_output_language"},
                "snippets": ["¡Por supuesto!", "Cualquiera de estas opciones"],
            }
        },
    },
    {
        "name": "matched_contract_pass",
        "item_id": "es_en_SA_004",
        "model": "gpt-4.1",
        "condition": "contract",
        "rtt": 0,
        "turns": {
            0: {
                "pass": True,
                "failure_types": set(),
                "snippets": ["Sure!", "I won't be able to join the call today"],
            }
        },
    },
    {
        "name": "quote_preservation_recovery",
        "item_id": "ar_en_SC_002",
        "model": "gpt-4.1-nano",
        "condition": "contract",
        "rtt": 1,
        "turns": {
            0: {
                "pass": False,
                "failure_types": {"preservation_failure", "task_noncompletion"},
                "snippets": ["مراجعة الميزانية", "أسئلة المجتمع"],
            },
            1: {
                "pass": True,
                "failure_types": set(),
                "snippets": ['"Budget Review"', '"Community Questions"'],
            },
        },
    },
    {
        "name": "unresolved_quote_preservation",
        "item_id": "ar_en_SC_002",
        "model": "gpt-4.1-nano",
        "condition": "baseline",
        "rtt": 3,
        "turns": {
            0: {
                "pass": False,
                "failure_types": {"preservation_failure", "task_noncompletion"},
                "snippets": ["يرجى تزويدي بالنص"],
            },
            2: {
                "pass": False,
                "failure_types": {"preservation_failure", "task_noncompletion"},
                "snippets": ["الالتزام بعدم ترجمة"],
            },
        },
    },
    {
        "name": "script_locale_literal_preservation",
        "item_id": "hi_en_SD_005",
        "model": "gpt-4.1-nano",
        "condition": "baseline",
        "rtt": 1,
        "turns": {
            0: {
                "pass": False,
                "failure_types": {"wrong_output_language"},
                "snippets": ["The file name draft_v2.pdf should stay unchanged"],
            },
            1: {
                "pass": True,
                "failure_types": set(),
                "snippets": ["draft_v2.pdf ko badalna nahi hai"],
            },
        },
    },
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def index_scores(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str, int], dict[str, Any]]:
    return {
        (row["item_id"], row["model"], row["condition"], int(row["turn"])): row
        for row in rows
    }


def index_trajectories(rows: list[dict[str, str]]) -> dict[tuple[str, str, str], dict[str, str]]:
    return {
        (row["item_id"], row["model"], row["condition"]): row
        for row in rows
    }


def validate_markdown(markdown_path: Path) -> None:
    text = markdown_path.read_text(encoding="utf-8")
    require(
        "results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl" in text,
        "qualitative examples must name paper-facing full-v0.2 source score log",
    )
    require(
        "results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv" in text,
        "qualitative examples must name paper-facing full-v0.2 trajectory table",
    )
    for example in EXAMPLES:
        require(example["item_id"] in text, f"qualitative examples missing item {example['item_id']}")
        require(example["model"] in text, f"qualitative examples missing model {example['model']}")


def validate_examples(
    *,
    scores: dict[tuple[str, str, str, int], dict[str, Any]],
    trajectories: dict[tuple[str, str, str], dict[str, str]],
) -> None:
    for example in EXAMPLES:
        traj_key = (example["item_id"], example["model"], example["condition"])
        require(traj_key in trajectories, f"missing trajectory for {example['name']}")
        trajectory = trajectories[traj_key]
        require(int(trajectory["rtt"]) == example["rtt"], f"{example['name']} RTT mismatch")
        for turn, expected in example["turns"].items():
            score_key = (*traj_key, turn)
            require(score_key in scores, f"missing score row for {example['name']} turn {turn}")
            row = scores[score_key]
            require(bool(row["pass"]) == expected["pass"], f"{example['name']} turn {turn} pass mismatch")
            require(set(row.get("failure_types", [])) == expected["failure_types"], f"{example['name']} turn {turn} failure-type mismatch")
            response = row.get("response", "")
            for snippet in expected["snippets"]:
                require(snippet in response, f"{example['name']} turn {turn} missing response snippet: {snippet}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", type=Path, default=Path("results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl"))
    parser.add_argument("--trajectories", type=Path, default=Path("results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv"))
    parser.add_argument("--markdown", type=Path, default=Path("paper/qualitative_examples.md"))
    args = parser.parse_args()

    validate_markdown(args.markdown)
    validate_examples(
        scores=index_scores(load_jsonl(args.scores)),
        trajectories=index_trajectories(load_csv(args.trajectories)),
    )
    print("qualitative example validation passed")


if __name__ == "__main__":
    main()
