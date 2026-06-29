#!/usr/bin/env python
"""Analyze paired GPT-4.1 and GPT-5.5 judge audits."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


COMPONENTS = (
    ("language", "language_pass", "judge_language_pass"),
    ("script", "script_pass", "judge_script_pass"),
    ("preservation", "preservation_pass", "judge_preservation_pass"),
    ("task", "task_pass", "judge_task_pass"),
    ("register_locale", "register_locale_pass", "judge_register_locale_pass"),
)


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


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return bool(value)


def pct(numerator: int, denominator: int) -> float:
    return round(100.0 * numerator / denominator, 1)


def wilson_interval(successes: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    require(n > 0, "cannot compute Wilson interval for n=0")
    p_hat = successes / n
    denom = 1.0 + z * z / n
    center = (p_hat + z * z / (2.0 * n)) / denom
    half_width = z * math.sqrt((p_hat * (1.0 - p_hat) + z * z / (4.0 * n)) / n) / denom
    return round(100.0 * (center - half_width), 1), round(100.0 * (center + half_width), 1)


def row_key(row: dict[str, Any]) -> tuple[str, str, str, int]:
    return (row["item_id"], row["model"], row["condition"], int(row["turn"]))


def summarize_judge(rows: list[dict[str, Any]], label: str) -> dict[str, Any]:
    n = len(rows)
    agree_n = sum(bool_value(row["auto_pass"]) == bool_value(row["judge_pass"]) for row in rows)
    ci_low, ci_high = wilson_interval(agree_n, n)
    auto_pass_n = sum(bool_value(row["auto_pass"]) for row in rows)
    judge_pass_n = sum(bool_value(row["judge_pass"]) for row in rows)
    return {
        "judge_label": label,
        "judge_model": rows[0]["judge_model"] if rows else "",
        "n": n,
        "auto_agreement_n": agree_n,
        "auto_agreement_pct": pct(agree_n, n),
        "auto_agreement_ci_low": ci_low,
        "auto_agreement_ci_high": ci_high,
        "auto_pass_n": auto_pass_n,
        "judge_pass_n": judge_pass_n,
        "auto_fail_judge_pass_n": sum((not bool_value(row["auto_pass"])) and bool_value(row["judge_pass"]) for row in rows),
        "auto_pass_judge_fail_n": sum(bool_value(row["auto_pass"]) and (not bool_value(row["judge_pass"])) for row in rows),
        "judge_parse_error_n": sum(bool(row.get("judge_parse_error")) for row in rows),
        "input_tokens": sum(int(row.get("judge_input_tokens", 0)) for row in rows),
        "output_tokens": sum(int(row.get("judge_output_tokens", 0)) for row in rows),
        "total_tokens": sum(int(row.get("judge_input_tokens", 0)) + int(row.get("judge_output_tokens", 0)) for row in rows),
    }


def summarize_by_family(rows: list[dict[str, Any]], label: str) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row["task_family"])].append(row)
    out: list[dict[str, Any]] = []
    for family, group in sorted(groups.items()):
        summary = summarize_judge(group, label)
        summary["task_family"] = family
        out.append(summary)
    return out


def component_summary(rows: list[dict[str, Any]], scores_by_key: dict[tuple[str, str, str, int], dict[str, Any]], label: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for component, auto_field, judge_field in COMPONENTS:
        agree_n = 0
        auto_pass_n = 0
        judge_pass_n = 0
        auto_fail_judge_pass_n = 0
        auto_pass_judge_fail_n = 0
        for row in rows:
            score_row = scores_by_key[row_key(row)]
            auto_pass = bool_value(score_row[auto_field])
            judge_pass = bool_value(row[judge_field])
            agree_n += auto_pass == judge_pass
            auto_pass_n += auto_pass
            judge_pass_n += judge_pass
            auto_fail_judge_pass_n += (not auto_pass) and judge_pass
            auto_pass_judge_fail_n += auto_pass and (not judge_pass)
        ci_low, ci_high = wilson_interval(agree_n, len(rows))
        out.append(
            {
                "judge_label": label,
                "component": component,
                "n": len(rows),
                "agreement_n": agree_n,
                "agreement_pct": pct(agree_n, len(rows)),
                "agreement_ci_low": ci_low,
                "agreement_ci_high": ci_high,
                "auto_pass_n": auto_pass_n,
                "judge_pass_n": judge_pass_n,
                "auto_fail_judge_pass_n": auto_fail_judge_pass_n,
                "auto_pass_judge_fail_n": auto_pass_judge_fail_n,
                "mismatch_n": len(rows) - agree_n,
            }
        )
    return out


def paired_comparison(old_rows: list[dict[str, Any]], new_rows: list[dict[str, Any]]) -> dict[str, Any]:
    old_by_key = {row_key(row): row for row in old_rows}
    new_by_key = {row_key(row): row for row in new_rows}
    require(set(old_by_key) == set(new_by_key), "judge audits are not paired on identical keys")
    n = len(old_by_key)
    agree_n = 0
    old_pass_new_fail = 0
    old_fail_new_pass = 0
    both_pass = 0
    both_fail = 0
    for key in old_by_key:
        old_pass = bool_value(old_by_key[key]["judge_pass"])
        new_pass = bool_value(new_by_key[key]["judge_pass"])
        agree_n += old_pass == new_pass
        old_pass_new_fail += old_pass and not new_pass
        old_fail_new_pass += (not old_pass) and new_pass
        both_pass += old_pass and new_pass
        both_fail += (not old_pass) and (not new_pass)
    ci_low, ci_high = wilson_interval(agree_n, n)
    return {
        "judge_a": old_rows[0]["judge_model"],
        "judge_b": new_rows[0]["judge_model"],
        "n": n,
        "pass_fail_agreement_n": agree_n,
        "pass_fail_agreement_pct": pct(agree_n, n),
        "pass_fail_agreement_ci_low": ci_low,
        "pass_fail_agreement_ci_high": ci_high,
        "both_pass_n": both_pass,
        "both_fail_n": both_fail,
        "judge_a_pass_judge_b_fail_n": old_pass_new_fail,
        "judge_a_fail_judge_b_pass_n": old_fail_new_pass,
    }


def disagreement_rows(old_rows: list[dict[str, Any]], new_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    old_by_key = {row_key(row): row for row in old_rows}
    new_by_key = {row_key(row): row for row in new_rows}
    out: list[dict[str, Any]] = []
    for key in sorted(old_by_key):
        old = old_by_key[key]
        new = new_by_key[key]
        auto_pass = bool_value(old["auto_pass"])
        old_pass = bool_value(old["judge_pass"])
        new_pass = bool_value(new["judge_pass"])
        if auto_pass == old_pass and auto_pass == new_pass and old_pass == new_pass:
            continue
        out.append(
            {
                "item_id": old["item_id"],
                "model": old["model"],
                "condition": old["condition"],
                "turn": old["turn"],
                "task_family": old.get("task_family", ""),
                "language_pair": old.get("language_pair", ""),
                "auto_pass": auto_pass,
                "gpt41_judge_pass": old_pass,
                "gpt55_judge_pass": new_pass,
                "auto_vs_gpt41_disagree": auto_pass != old_pass,
                "auto_vs_gpt55_disagree": auto_pass != new_pass,
                "gpt41_vs_gpt55_disagree": old_pass != new_pass,
                "auto_failure_types": json.dumps(old.get("auto_failure_types", []), ensure_ascii=False),
                "gpt41_failure_types": json.dumps(old.get("judge_failure_types", []), ensure_ascii=False),
                "gpt55_failure_types": json.dumps(new.get("judge_failure_types", []), ensure_ascii=False),
                "gpt41_reason": old.get("judge_short_reason", ""),
                "gpt55_reason": new.get("judge_short_reason", ""),
            }
        )
    return out


def validate_inputs(old_rows: list[dict[str, Any]], new_rows: list[dict[str, Any]], score_rows: list[dict[str, Any]]) -> None:
    require(len(old_rows) == 72, f"expected 72 GPT-4.1 judge rows, found {len(old_rows)}")
    require(len(new_rows) == 72, f"expected 72 GPT-5.5 judge rows, found {len(new_rows)}")
    require(len({row_key(row) for row in old_rows}) == 72, "duplicate GPT-4.1 judge keys")
    require(len({row_key(row) for row in new_rows}) == 72, "duplicate GPT-5.5 judge keys")
    require({row_key(row) for row in old_rows} == {row_key(row) for row in new_rows}, "judge audits have different keys")
    require(all(not row.get("judge_parse_error") for row in old_rows), "GPT-4.1 judge audit has parse errors")
    require(all(not row.get("judge_parse_error") for row in new_rows), "GPT-5.5 judge audit has parse errors")
    strata = defaultdict(int)
    for row in new_rows:
        strata[(row["model"], row["condition"], row["task_family"])] += 1
    require(len(strata) == 24, f"expected 24 GPT-5.5 judge strata, found {len(strata)}")
    require(all(count == 3 for count in strata.values()), f"GPT-5.5 judge audit not 3 per stratum: {dict(strata)}")
    scores_by_key = {row_key(row): row for row in score_rows}
    missing = [key for key in {row_key(row) for row in new_rows} if key not in scores_by_key]
    require(not missing, f"judge rows missing score rows: {missing[:5]}")


def write_markdown(
    path: Path,
    *,
    summary_rows: list[dict[str, Any]],
    pairwise: dict[str, Any],
    disagreements: list[dict[str, Any]],
) -> None:
    by_label = {row["judge_label"]: row for row in summary_rows}
    gpt41 = by_label["gpt41"]
    gpt55 = by_label["gpt55"]
    lines = [
        "# GPT-5.5 Judge Refresh",
        "",
        "This artifact reruns the same 72-row blinded first-turn judge-audit sample",
        "with `gpt-5.5` and compares it with the saved `gpt-4.1` judge audit.",
        "The sample is exactly paired: 3 rows for each model/condition/task-family",
        "stratum from the full 120-item stress evaluation.",
        "",
        "## Summary",
        "",
        "| Judge | Auto agreement | Wilson 95% CI | Auto pass | Judge pass | Parse errors | Tokens |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            "| "
            f"{row['judge_model']} | {row['auto_agreement_n']}/{row['n']} ({row['auto_agreement_pct']:.1f}%) | "
            f"[{row['auto_agreement_ci_low']:.1f}, {row['auto_agreement_ci_high']:.1f}] | "
            f"{row['auto_pass_n']} | {row['judge_pass_n']} | {row['judge_parse_error_n']} | {row['total_tokens']} |"
        )
    lines.extend(
        [
            "",
            "## Judge-to-Judge Agreement",
            "",
            "| Judge A | Judge B | Agreement | Wilson 95% CI | Both pass | Both fail | A pass / B fail | A fail / B pass |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
            (
                "| "
                f"{pairwise['judge_a']} | {pairwise['judge_b']} | "
                f"{pairwise['pass_fail_agreement_n']}/{pairwise['n']} ({pairwise['pass_fail_agreement_pct']:.1f}%) | "
                f"[{pairwise['pass_fail_agreement_ci_low']:.1f}, {pairwise['pass_fail_agreement_ci_high']:.1f}] | "
                f"{pairwise['both_pass_n']} | {pairwise['both_fail_n']} | "
                f"{pairwise['judge_a_pass_judge_b_fail_n']} | {pairwise['judge_a_fail_judge_b_pass_n']} |"
            ),
            "",
            "## Disagreement Rows",
            "",
            "| Item | Model | Condition | Family | Auto | GPT-4.1 judge | GPT-5.5 judge | GPT-5.5 reason |",
            "|---|---|---|---|---:|---:|---:|---|",
        ]
    )
    for row in disagreements:
        reason = str(row["gpt55_reason"]).replace("|", "/")
        lines.append(
            "| "
            f"{row['item_id']} | {row['model']} | {row['condition']} | {row['task_family']} | "
            f"{row['auto_pass']} | {row['gpt41_judge_pass']} | {row['gpt55_judge_pass']} | {reason} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"The original `gpt-4.1` judge agrees with the automatic scorer on {gpt41['auto_agreement_n']}/72",
            f"pass/fail labels, while the `gpt-5.5` judge agrees on {gpt55['auto_agreement_n']}/72.",
            f"The two judges agree with each other on {pairwise['pass_fail_agreement_n']}/72 pass/fail labels.",
            "The GPT-5.5 judge is stricter on three rows: it agrees with the automatic scorer",
            "that Spanish framing around English rewrites should fail, and it newly flags",
            "one polite-request register issue plus one over-informative quote-summary issue.",
            "This refresh strengthens the methodological caveat: LLM judges are useful scorer",
            "sanity checks, but they do not replace native/near-native validation.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpt41-audit", type=Path, default=Path("results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl"))
    parser.add_argument("--gpt55-audit", type=Path, default=Path("results/scores/openai_three_model_stress_v02_full120_judge_gpt55_audit72.jsonl"))
    parser.add_argument("--scores", type=Path, default=Path("results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/openai_three_model_stress_v02_full120_judge_refresh_gpt55"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/judge_refresh_gpt55_v02_full120.md"))
    args = parser.parse_args()

    gpt41_rows = load_jsonl(args.gpt41_audit)
    gpt55_rows = load_jsonl(args.gpt55_audit)
    score_rows = load_jsonl(args.scores)
    validate_inputs(gpt41_rows, gpt55_rows, score_rows)
    scores_by_key = {row_key(row): row for row in score_rows}

    summary_rows = [summarize_judge(gpt41_rows, "gpt41"), summarize_judge(gpt55_rows, "gpt55")]
    family_rows = [*summarize_by_family(gpt41_rows, "gpt41"), *summarize_by_family(gpt55_rows, "gpt55")]
    component_rows = [*component_summary(gpt41_rows, scores_by_key, "gpt41"), *component_summary(gpt55_rows, scores_by_key, "gpt55")]
    pairwise = paired_comparison(gpt41_rows, gpt55_rows)
    disagreements = disagreement_rows(gpt41_rows, gpt55_rows)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "judge_refresh_summary.csv", summary_rows)
    write_csv(args.out_dir / "judge_refresh_by_family.csv", family_rows)
    write_csv(args.out_dir / "judge_refresh_component_agreement.csv", component_rows)
    write_csv(args.out_dir / "judge_refresh_pairwise_comparison.csv", [pairwise])
    write_csv(args.out_dir / "judge_refresh_disagreements.csv", disagreements)
    write_markdown(args.out_md, summary_rows=summary_rows, pairwise=pairwise, disagreements=disagreements)
    print(f"wrote judge-refresh analysis to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
