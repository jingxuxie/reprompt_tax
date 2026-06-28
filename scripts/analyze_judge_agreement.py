#!/usr/bin/env python
"""Analyze LLM-judge agreement against saved automatic scorer labels."""

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
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
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


def score_index(score_rows: list[dict[str, Any]]) -> dict[tuple[str, str, str, int], dict[str, Any]]:
    out: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    for row in score_rows:
        key = (row["item_id"], row["model"], row["condition"], int(row["turn"]))
        if key in out:
            raise AssertionError(f"duplicate score row for {key}")
        out[key] = row
    return out


def pass_fail_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    agree_n = sum(bool_value(row["auto_pass"]) == bool_value(row["judge_pass"]) for row in rows)
    ci_low, ci_high = wilson_interval(agree_n, n)
    auto_pass_n = sum(bool_value(row["auto_pass"]) for row in rows)
    judge_pass_n = sum(bool_value(row["judge_pass"]) for row in rows)
    return {
        "n": n,
        "pass_fail_agreement_n": agree_n,
        "pass_fail_agreement_pct": pct(agree_n, n),
        "pass_fail_agreement_ci_low": ci_low,
        "pass_fail_agreement_ci_high": ci_high,
        "auto_pass_n": auto_pass_n,
        "auto_pass_pct": pct(auto_pass_n, n),
        "judge_pass_n": judge_pass_n,
        "judge_pass_pct": pct(judge_pass_n, n),
        "auto_fail_judge_pass_n": sum((not bool_value(row["auto_pass"])) and bool_value(row["judge_pass"]) for row in rows),
        "auto_pass_judge_fail_n": sum(bool_value(row["auto_pass"]) and (not bool_value(row["judge_pass"])) for row in rows),
        "judge_parse_error_n": sum(bool(row.get("judge_parse_error")) for row in rows),
    }


def grouped_pass_fail(rows: list[dict[str, Any]], group_fields: tuple[str, ...]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[tuple(str(row.get(field, "")) for field in group_fields)].append(row)
    out: list[dict[str, Any]] = []
    for key, group in sorted(groups.items()):
        summary = {field: value for field, value in zip(group_fields, key)}
        summary.update(pass_fail_summary(group))
        out.append(summary)
    return out


def component_summary(audit_rows: list[dict[str, Any]], scores_by_key: dict[tuple[str, str, str, int], dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for component, auto_field, judge_field in COMPONENTS:
        n = len(audit_rows)
        agree_n = 0
        auto_pass_n = 0
        judge_pass_n = 0
        auto_fail_judge_pass_n = 0
        auto_pass_judge_fail_n = 0
        for row in audit_rows:
            score_row = scores_by_key[(row["item_id"], row["model"], row["condition"], int(row["turn"]))]
            auto_pass = bool_value(score_row[auto_field])
            judge_pass = bool_value(row[judge_field])
            agree_n += auto_pass == judge_pass
            auto_pass_n += auto_pass
            judge_pass_n += judge_pass
            auto_fail_judge_pass_n += (not auto_pass) and judge_pass
            auto_pass_judge_fail_n += auto_pass and (not judge_pass)
        ci_low, ci_high = wilson_interval(agree_n, n)
        out.append(
            {
                "component": component,
                "n": n,
                "agreement_n": agree_n,
                "agreement_pct": pct(agree_n, n),
                "agreement_ci_low": ci_low,
                "agreement_ci_high": ci_high,
                "auto_pass_n": auto_pass_n,
                "judge_pass_n": judge_pass_n,
                "auto_fail_judge_pass_n": auto_fail_judge_pass_n,
                "auto_pass_judge_fail_n": auto_pass_judge_fail_n,
                "mismatch_n": n - agree_n,
            }
        )
    return out


def component_disagreements(audit_rows: list[dict[str, Any]], scores_by_key: dict[tuple[str, str, str, int], dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in audit_rows:
        score_row = scores_by_key[(row["item_id"], row["model"], row["condition"], int(row["turn"]))]
        for component, auto_field, judge_field in COMPONENTS:
            auto_pass = bool_value(score_row[auto_field])
            judge_pass = bool_value(row[judge_field])
            if auto_pass == judge_pass:
                continue
            out.append(
                {
                    "item_id": row["item_id"],
                    "model": row["model"],
                    "condition": row["condition"],
                    "turn": row["turn"],
                    "task_family": row.get("task_family", ""),
                    "language_pair": row.get("language_pair", ""),
                    "component": component,
                    "auto_component_pass": auto_pass,
                    "judge_component_pass": judge_pass,
                    "auto_pass": row["auto_pass"],
                    "judge_pass": row["judge_pass"],
                    "auto_failure_types": json.dumps(row.get("auto_failure_types", []), ensure_ascii=False),
                    "judge_failure_types": json.dumps(row.get("judge_failure_types", []), ensure_ascii=False),
                    "judge_short_reason": row.get("judge_short_reason", ""),
                }
            )
    return out


def pass_fail_disagreements(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        if bool_value(row["auto_pass"]) == bool_value(row["judge_pass"]):
            continue
        out.append(
            {
                "item_id": row["item_id"],
                "model": row["model"],
                "condition": row["condition"],
                "turn": row["turn"],
                "task_family": row.get("task_family", ""),
                "language_pair": row.get("language_pair", ""),
                "auto_pass": row["auto_pass"],
                "judge_pass": row["judge_pass"],
                "auto_failure_types": json.dumps(row.get("auto_failure_types", []), ensure_ascii=False),
                "judge_failure_types": json.dumps(row.get("judge_failure_types", []), ensure_ascii=False),
                "judge_short_reason": row.get("judge_short_reason", ""),
            }
        )
    return out


def write_markdown(
    path: Path,
    summary: dict[str, Any],
    by_family: list[dict[str, Any]],
    component_rows: list[dict[str, Any]],
    pass_fail_disagreement_rows: list[dict[str, Any]],
) -> None:
    lines = [
        "# Judge Agreement Analysis",
        "",
        "Generated from `results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl`",
        "and first-turn component labels in",
        "`results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl`.",
        "",
        "The judge is an LLM audit, not a native-speaker human audit. These numbers",
        "support scorer sanity checks but do not replace native/near-native validation.",
        "",
        "## Pass/Fail Agreement",
        "",
        "| n | Agreement | Wilson 95% CI | Auto pass | Judge pass | Auto fail / judge pass | Auto pass / judge fail | Parse errors |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
        (
            "| "
            f"{summary['n']} | {summary['pass_fail_agreement_n']}/{summary['n']} "
            f"({summary['pass_fail_agreement_pct']:.1f}%) | "
            f"[{summary['pass_fail_agreement_ci_low']:.1f}, {summary['pass_fail_agreement_ci_high']:.1f}] | "
            f"{summary['auto_pass_n']} ({summary['auto_pass_pct']:.1f}%) | "
            f"{summary['judge_pass_n']} ({summary['judge_pass_pct']:.1f}%) | "
            f"{summary['auto_fail_judge_pass_n']} | {summary['auto_pass_judge_fail_n']} | "
            f"{summary['judge_parse_error_n']} |"
        ),
        "",
        "## Pass/Fail Agreement By Family",
        "",
        "| Task family | n | Agreement | Wilson 95% CI | Auto pass | Judge pass |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in by_family:
        lines.append(
            "| "
            f"{row['task_family']} | {row['n']} | {row['pass_fail_agreement_n']}/{row['n']} "
            f"({row['pass_fail_agreement_pct']:.1f}%) | "
            f"[{row['pass_fail_agreement_ci_low']:.1f}, {row['pass_fail_agreement_ci_high']:.1f}] | "
            f"{row['auto_pass_n']} | {row['judge_pass_n']} |"
        )

    lines.extend(
        [
            "",
            "## Component Agreement",
            "",
            "| Component | Agreement | Wilson 95% CI | Auto pass | Judge pass | Auto fail / judge pass | Auto pass / judge fail |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in component_rows:
        lines.append(
            "| "
            f"{row['component']} | {row['agreement_n']}/{row['n']} ({row['agreement_pct']:.1f}%) | "
            f"[{row['agreement_ci_low']:.1f}, {row['agreement_ci_high']:.1f}] | "
            f"{row['auto_pass_n']} | {row['judge_pass_n']} | "
            f"{row['auto_fail_judge_pass_n']} | {row['auto_pass_judge_fail_n']} |"
        )

    lines.extend(["", "## Pass/Fail Disagreements", ""])
    if not pass_fail_disagreement_rows:
        lines.append("No pass/fail disagreements.")
    else:
        lines.extend(
            [
                "| Item | Model | Condition | Family | Language pair | Auto pass | Judge pass | Judge reason |",
                "|---|---|---|---|---|---:|---:|---|",
            ]
        )
        for row in pass_fail_disagreement_rows:
            reason = str(row["judge_short_reason"]).replace("|", "/")
            lines.append(
                "| "
                f"{row['item_id']} | {row['model']} | {row['condition']} | {row['task_family']} | "
                f"{row['language_pair']} | {row['auto_pass']} | {row['judge_pass']} | {reason} |"
            )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"The pass/fail agreement is {summary['pass_fail_agreement_n']}/{summary['n']} "
            f"({summary['pass_fail_agreement_pct']:.1f}%; Wilson 95% CI "
            f"{summary['pass_fail_agreement_ci_low']:.1f}--{summary['pass_fail_agreement_ci_high']:.1f}).",
            "The single pass/fail disagreement is an editing-preservation case where",
            "the automatic scorer rejects Spanish framing around English rewrites and",
            "the judge accepts the response.",
            "",
            "Component agreement is more nuanced than the headline pass/fail number:",
            "preservation agreement is 69/72 and register/locale agreement is 68/72.",
            "This supports the current conservative claim boundary: use the judge audit",
            "as a scorer sanity check, while keeping native/near-native audit as a",
            "required next step before stronger final claims.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, default=Path("results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl"))
    parser.add_argument("--scores", type=Path, default=Path("results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/openai_three_model_stress_v02_full120_judge_audit72"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/judge_agreement_analysis_v02_full120.md"))
    args = parser.parse_args()

    audit_rows = load_jsonl(args.audit)
    score_rows = load_jsonl(args.scores)
    require(len(audit_rows) == 72, f"expected 72 judge-audit rows, found {len(audit_rows)}")
    scores_by_key = score_index(score_rows)
    for row in audit_rows:
        key = (row["item_id"], row["model"], row["condition"], int(row["turn"]))
        require(key in scores_by_key, f"judge row missing matching score row: {key}")

    summary = pass_fail_summary(audit_rows)
    by_family = grouped_pass_fail(audit_rows, ("task_family",))
    by_model_condition = grouped_pass_fail(audit_rows, ("model", "condition"))
    component_rows = component_summary(audit_rows, scores_by_key)
    pass_fail_disagreement_rows = pass_fail_disagreements(audit_rows)
    component_disagreement_rows = component_disagreements(audit_rows, scores_by_key)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "judge_agreement_summary.csv", [summary])
    write_csv(args.out_dir / "judge_agreement_by_family.csv", by_family)
    write_csv(args.out_dir / "judge_agreement_by_model_condition.csv", by_model_condition)
    write_csv(args.out_dir / "judge_component_agreement.csv", component_rows)
    write_csv(args.out_dir / "judge_pass_fail_disagreements.csv", pass_fail_disagreement_rows)
    write_csv(args.out_dir / "judge_component_disagreements.csv", component_disagreement_rows)
    write_markdown(args.out_md, summary, by_family, component_rows, pass_fail_disagreement_rows)
    print(f"wrote judge-agreement analysis to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
