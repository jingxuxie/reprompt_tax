#!/usr/bin/env python
"""Challenge the automatic scorer with synthetic known-bad responses."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from score_auto import score_response


BENCHMARK_PATH = Path("data/benchmark_stress_v0.2.jsonl")
OUT_DIR = Path("results/tables/scorer_challenge_v02")
OUT_MD = Path("paper/scorer_challenge_v02.md")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    require(path.exists(), f"missing benchmark {path}")
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


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, f"refusing to write empty challenge table {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def generic_good_language(item: dict[str, Any]) -> str:
    expected = str(item["expected_response_language"]).lower()
    if expected == "spanish":
        return "Gracias, el texto esta listo y claro."
    if expected == "arabic":
        return "تمت صياغة الرد بشكل واضح ومناسب."
    if expected == "hindi":
        return "यह उत्तर स्पष्ट और स्वाभाविक है।"
    if expected == "hindi/hinglish":
        return "yeh response clear hai aur theek hai."
    return "This response is clear, concise, and ready to use."


def wrong_script_response(item: dict[str, Any]) -> str:
    expected_script = str(item["expected_script"]).lower()
    if expected_script == "latin":
        return "بالطبع، سأقدم ردا واضحا ومناسبا."
    if expected_script == "arabic":
        return "This is an English response with Latin script only."
    if expected_script == "devanagari":
        return "This is an English response with Latin script only."
    return "بالطبع، سأقدم ردا واضحا ومناسبا."


def marker_text(item: dict[str, Any]) -> str:
    markers = [str(marker) for marker in item.get("required_any_markers", []) if str(marker).strip()]
    spans = [str(span) for span in item.get("must_preserve_spans", []) if str(span).strip()]
    unique: list[str] = []
    for value in [*markers, *spans]:
        if value not in unique:
            unique.append(value)
    return " ".join(unique[:4])


def challenge_specs(item: dict[str, Any]) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []

    forbidden = [str(marker) for marker in item.get("forbidden_markers", []) if str(marker).strip()]
    if forbidden:
        response = " ".join(part for part in [forbidden[0], marker_text(item), generic_good_language(item)] if part)
        specs.append(
            {
                "challenge_type": "forbidden_marker",
                "response": response,
                "expected_failure_types": ["task_noncompletion"],
            }
        )

    specs.append(
        {
            "challenge_type": "required_marker_omission",
            "response": generic_good_language(item),
            "expected_failure_types": ["task_noncompletion"],
        }
    )

    specs.append(
        {
            "challenge_type": "wrong_script",
            "response": wrong_script_response(item),
            "expected_failure_types": ["wrong_output_language", "script_mismatch"],
        }
    )

    if item.get("must_preserve_spans"):
        specs.append(
            {
                "challenge_type": "preservation_drop",
                "response": generic_good_language(item),
                "expected_failure_types": ["preservation_failure"],
            }
        )

    if item["task_family"] == "script_register_locale":
        response = " ".join(
            part
            for part in [
                "Dear Sir or Madam, I humbly request that this message be handled with care.",
                marker_text(item),
            ]
            if part
        )
        specs.append(
            {
                "challenge_type": "overformal_register",
                "response": response,
                "expected_failure_types": ["register_locale_mismatch"],
            }
        )

    return specs


def build_challenges(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in sorted(items, key=lambda row: row["id"]):
        for spec in challenge_specs(item):
            score = score_response(item, spec["response"])
            expected = list(spec["expected_failure_types"])
            failure_types = list(score["failure_types"])
            expected_detected = all(name in failure_types for name in expected)
            rows.append(
                {
                    "item_id": item["id"],
                    "language_pair": item["language_pair"],
                    "task_family": item["task_family"],
                    "expected_response_language": item["expected_response_language"],
                    "expected_script": item["expected_script"],
                    "challenge_type": spec["challenge_type"],
                    "auto_pass": int(bool(score["pass"])),
                    "auto_failed": int(not bool(score["pass"])),
                    "expected_failure_types": ";".join(expected),
                    "failure_types": ";".join(failure_types),
                    "expected_signal_detected": int(expected_detected),
                    "response_chars": len(spec["response"]),
                    "response_preview": spec["response"][:140],
                }
            )
    require(rows, "no scorer challenges generated")
    return rows


def summarize(rows: list[dict[str, Any]], key_fields: tuple[str, ...]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(str(row[field]) for field in key_fields)].append(row)

    out: list[dict[str, Any]] = []
    for key, group in sorted(grouped.items()):
        result = {field: value for field, value in zip(key_fields, key)}
        failure_counter = Counter(
            failure_type
            for row in group
            for failure_type in str(row["failure_types"]).split(";")
            if failure_type
        )
        result.update(
            {
                "n_challenges": len(group),
                "auto_failed_n": sum(int(row["auto_failed"]) for row in group),
                "auto_failed_pct": round(100 * sum(int(row["auto_failed"]) for row in group) / len(group), 1),
                "expected_signal_detected_n": sum(int(row["expected_signal_detected"]) for row in group),
                "expected_signal_detected_pct": round(
                    100 * sum(int(row["expected_signal_detected"]) for row in group) / len(group),
                    1,
                ),
                "auto_pass_n": sum(int(row["auto_pass"]) for row in group),
                "top_failure_types": ";".join(f"{name}:{count}" for name, count in failure_counter.most_common(5)),
            }
        )
        out.append(result)
    return out


def write_markdown(
    path: Path,
    *,
    overall: dict[str, Any],
    by_type: list[dict[str, Any]],
    by_family: list[dict[str, Any]],
    by_language: list[dict[str, Any]],
) -> None:
    lines = [
        "# Scorer Challenge Audit v0.2",
        "",
        "This no-API audit feeds synthetic known-bad responses through the real",
        "`scripts/score_auto.py` scorer for every v0.2 benchmark item. It checks",
        "whether the deterministic scorer catches benchmark-wide challenge probes",
        "for forbidden markers, omitted required markers, wrong script/language,",
        "dropped preservation spans, and over-formal register. It is a scorer",
        "stress test, not native/near-native validation.",
        "",
        "## Overall",
        "",
        "| Challenges | Auto failed | Expected signal detected | Auto passed |",
        "|---:|---:|---:|---:|",
        (
            f"| {overall['n_challenges']} | {overall['auto_failed_n']} "
            f"({overall['auto_failed_pct']}%) | {overall['expected_signal_detected_n']} "
            f"({overall['expected_signal_detected_pct']}%) | {overall['auto_pass_n']} |"
        ),
        "",
        "## By Challenge Type",
        "",
        "| Challenge | n | Auto failed | Expected signal detected | Top failure types |",
        "|---|---:|---:|---:|---|",
    ]
    for row in by_type:
        lines.append(
            f"| {row['challenge_type']} | {row['n_challenges']} | "
            f"{row['auto_failed_n']} ({row['auto_failed_pct']}%) | "
            f"{row['expected_signal_detected_n']} ({row['expected_signal_detected_pct']}%) | "
            f"{row['top_failure_types']} |"
        )

    lines.extend(
        [
            "",
            "## By Task Family",
            "",
            "| Family | n | Auto failed | Expected signal detected |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in by_family:
        lines.append(
            f"| {row['task_family']} | {row['n_challenges']} | "
            f"{row['auto_failed_n']} ({row['auto_failed_pct']}%) | "
            f"{row['expected_signal_detected_n']} ({row['expected_signal_detected_pct']}%) |"
        )

    lines.extend(
        [
            "",
            "## By Language Pair",
            "",
            "| Language pair | n | Auto failed | Expected signal detected |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in by_language:
        lines.append(
            f"| {row['language_pair']} | {row['n_challenges']} | "
            f"{row['auto_failed_n']} ({row['auto_failed_pct']}%) | "
            f"{row['expected_signal_detected_n']} ({row['expected_signal_detected_pct']}%) |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The synthetic challenge suite is intentionally adversarial and narrow: it",
            "tests whether known-bad perturbations trigger deterministic failure",
            "components, not whether fluent real model answers are culturally or",
            "pragmatically correct. Passing this audit supports using the scorer as",
            "a conservative benchmark triage tool, while the human/native review",
            "gates remain necessary for stronger validation claims.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, default=BENCHMARK_PATH)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    items = load_jsonl(args.benchmark)
    require(len(items) == 120, f"expected 120 v0.2 items, found {len(items)}")
    rows = build_challenges(items)
    overall = summarize(rows, tuple())[0]
    by_type = summarize(rows, ("challenge_type",))
    by_family = summarize(rows, ("task_family",))
    by_language = summarize(rows, ("language_pair",))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "scorer_challenge_rows.csv", rows)
    write_csv(args.out_dir / "scorer_challenge_by_type.csv", by_type)
    write_csv(args.out_dir / "scorer_challenge_by_family.csv", by_family)
    write_csv(args.out_dir / "scorer_challenge_by_language.csv", by_language)
    write_csv(args.out_dir / "scorer_challenge_overall.csv", [overall])
    write_markdown(args.out_md, overall=overall, by_type=by_type, by_family=by_family, by_language=by_language)
    print(f"wrote scorer challenge audit to {args.out_md} and {args.out_dir}")


if __name__ == "__main__":
    main()
