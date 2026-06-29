#!/usr/bin/env python
"""Generate qualitative current-model case studies from saved outputs."""

from __future__ import annotations

import argparse
import ast
import csv
import json
from pathlib import Path
from typing import Any


OUT_DIR = Path("results/tables/current_model_case_studies_v02")
OUT_CSV = OUT_DIR / "current_model_case_studies.csv"
OUT_MD = Path("paper/current_model_case_studies_v02.md")

MODEL_ARTIFACTS = {
    "gpt-5.4-mini": {
        "scores": Path("results/scores/openai_gpt54mini_stress_v02_full120_auto_scores.jsonl"),
        "trajectories": Path("results/tables/openai_gpt54mini_stress_v02_full120/trajectory_metrics.csv"),
    },
    "gpt-5.5": {
        "scores": Path("results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl"),
        "trajectories": Path("results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv"),
    },
}

CASES = [
    {
        "case_id": "gpt55_baseline_fixed_by_contract",
        "title": "GPT-5.5 baseline still pays wrapper tax",
        "model": "gpt-5.5",
        "condition": "baseline",
        "item_id": "es_en_SA_001",
        "contrast_condition": "contract",
        "interpretation": "Baseline preserves useful English edits but wraps them in Spanish; the matched contract row passes first turn.",
    },
    {
        "case_id": "gpt55_contract_residual_repairs",
        "title": "GPT-5.5 contract residual repairs immediately",
        "model": "gpt-5.5",
        "condition": "contract",
        "item_id": "es_en_SA_004",
        "contrast_condition": "",
        "interpretation": "The contract nearly solves editing preservation, but one Spanish wrapper still creates a first-turn language failure that repairs in one turn.",
    },
    {
        "case_id": "gpt54mini_contract_quote_unresolved",
        "title": "GPT-5.4-mini repeats English in a Hindi/Hinglish quote task",
        "model": "gpt-5.4-mini",
        "condition": "contract",
        "item_id": "hi_en_SC_003",
        "contrast_condition": "",
        "interpretation": "The lower-cost current model preserves quoted English headings but never switches to the requested Hindi/Hinglish Latin-script summary.",
    },
    {
        "case_id": "gpt54mini_contract_literal_unresolved",
        "title": "GPT-5.4-mini changes literal date format in Arabic script",
        "model": "gpt-5.4-mini",
        "condition": "contract",
        "item_id": "ar_en_SD_008",
        "contrast_condition": "",
        "interpretation": "The lower-cost current model follows Arabic script but localizes the literal date instead of preserving the requested exact span.",
    },
]

CSV_FIELDS = [
    "case_id",
    "title",
    "model",
    "condition",
    "item_id",
    "language_pair",
    "task_family",
    "expected_response_language",
    "expected_script",
    "rtt",
    "unresolved",
    "first_failure_types",
    "final_turn",
    "final_pass",
    "contrast_condition",
    "contrast_first_pass",
    "user_prompt_excerpt",
    "first_response_excerpt",
    "final_response_excerpt",
    "contrast_first_response_excerpt",
    "interpretation",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def excerpt(text: str, limit: int = 260) -> str:
    cleaned = " ".join(str(text).split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def parse_types(value: str) -> list[str]:
    parsed = ast.literal_eval(value)
    require(isinstance(parsed, list), f"expected list literal, got {value!r}")
    return [str(item) for item in parsed]


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


def benchmark_items(path: Path) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in load_jsonl(path)}


def build_case_rows() -> list[dict[str, Any]]:
    benchmark = benchmark_items(Path("data/benchmark_stress_v0.2.jsonl"))
    score_by_model = {
        model: index_scores(load_jsonl(paths["scores"]))
        for model, paths in MODEL_ARTIFACTS.items()
    }
    traj_by_model = {
        model: index_trajectories(load_csv(paths["trajectories"]))
        for model, paths in MODEL_ARTIFACTS.items()
    }

    out: list[dict[str, Any]] = []
    for case in CASES:
        model = case["model"]
        condition = case["condition"]
        item_id = case["item_id"]
        item = benchmark[item_id]
        trajectory = traj_by_model[model][(item_id, model, condition)]
        scores = score_by_model[model]
        turns = [
            key[3]
            for key in scores
            if key[0] == item_id and key[1] == model and key[2] == condition
        ]
        require(turns, f"missing score turns for {model}/{condition}/{item_id}")
        final_turn = max(turns)
        first = scores[(item_id, model, condition, 0)]
        final = scores[(item_id, model, condition, final_turn)]

        contrast_condition = case["contrast_condition"]
        contrast_first = None
        if contrast_condition:
            contrast_first = scores[(item_id, model, contrast_condition, 0)]

        out.append(
            {
                "case_id": case["case_id"],
                "title": case["title"],
                "model": model,
                "condition": condition,
                "item_id": item_id,
                "language_pair": item["language_pair"],
                "task_family": item["task_family"],
                "expected_response_language": item["expected_response_language"],
                "expected_script": item["expected_script"],
                "rtt": trajectory["rtt"],
                "unresolved": trajectory["unresolved"],
                "first_failure_types": ",".join(parse_types(trajectory["first_failure_types"])),
                "final_turn": final_turn,
                "final_pass": bool(final["pass"]),
                "contrast_condition": contrast_condition,
                "contrast_first_pass": "" if contrast_first is None else bool(contrast_first["pass"]),
                "user_prompt_excerpt": excerpt(item["user_prompt"]),
                "first_response_excerpt": excerpt(first["response"]),
                "final_response_excerpt": excerpt(final["response"]),
                "contrast_first_response_excerpt": "" if contrast_first is None else excerpt(contrast_first["response"]),
                "interpretation": case["interpretation"],
            }
        )
    return out


def md_cell(value: Any) -> str:
    return str(value).replace("|", "/")


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Current-Model Case Studies",
        "",
        "These case studies are generated from saved GPT-5.x full-120 score logs",
        "and benchmark rows. They make no new API calls and are intended to",
        "make the current-model headline and lower-cost-model boundary inspectable.",
        "",
        "Source artifacts:",
        "",
        "- `results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl`",
        "- `results/scores/openai_gpt54mini_stress_v02_full120_auto_scores.jsonl`",
        "- `data/benchmark_stress_v0.2.jsonl`",
        "",
        "## Summary Table",
        "",
        "| Case | Model | Condition | Item | RTT | Unresolved | First failure types | Interpretation |",
        "|---|---|---|---|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['case_id']} | {row['model']} | {row['condition']} | `{row['item_id']}` | "
            f"{row['rtt']} | {row['unresolved']} | {row['first_failure_types']} | {md_cell(row['interpretation'])} |"
        )

    for row in rows:
        lines.extend(
            [
                "",
                f"## {row['title']}",
                "",
                f"- Case ID: `{row['case_id']}`",
                f"- Item: `{row['item_id']}` ({row['language_pair']}, {row['task_family']})",
                f"- Model/condition: `{row['model']}` / `{row['condition']}`",
                f"- Expected response: {row['expected_response_language']} in {row['expected_script']} script",
                f"- RTT: {row['rtt']}; unresolved: {row['unresolved']}",
                f"- First failure types: {row['first_failure_types'] or 'none'}",
                "",
                "User prompt excerpt:",
                "",
                "```text",
                str(row["user_prompt_excerpt"]),
                "```",
                "",
                "First response excerpt:",
                "",
                "```text",
                str(row["first_response_excerpt"]),
                "```",
            ]
        )
        if str(row["final_turn"]) != "0":
            lines.extend(
                [
                    "",
                    f"Final saved response excerpt after turn {row['final_turn']}:",
                    "",
                    "```text",
                    str(row["final_response_excerpt"]),
                    "```",
                ]
            )
        if row["contrast_condition"]:
            lines.extend(
                [
                    "",
                    f"Matched `{row['contrast_condition']}` first response excerpt:",
                    "",
                    "```text",
                    str(row["contrast_first_response_excerpt"]),
                    "```",
                ]
            )
        lines.extend(["", f"Interpretation: {row['interpretation']}"])

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "These examples are qualitative diagnostics from saved automatic-score",
            "rows. They support the paper's interpretation of residual burden, but",
            "they do not replace native/near-native human validation.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-csv", type=Path, default=OUT_CSV)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    rows = build_case_rows()
    write_csv(args.out_csv, rows)
    write_markdown(args.out_md, rows)
    print(f"wrote current-model case studies to {args.out_md} and {args.out_csv}")


if __name__ == "__main__":
    main()
