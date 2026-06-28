#!/usr/bin/env python
"""Summarize nano prompt ablations on the full v0.2 stress pilot."""

from __future__ import annotations

import argparse
import ast
import csv
import json
from math import comb
from pathlib import Path
from statistics import mean
from typing import Any


CONDITIONS = ["baseline", "generic_helpfulness", "content_preservation", "contract"]
COMPARISONS = [
    ("baseline", "generic_helpfulness"),
    ("baseline", "content_preservation"),
    ("baseline", "contract"),
    ("generic_helpfulness", "content_preservation"),
    ("content_preservation", "contract"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
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


def sign_test_p_value(improved: int, worsened: int) -> float:
    n = improved + worsened
    if n == 0:
        return 1.0
    k = min(improved, worsened)
    tail = sum(comb(n, i) for i in range(k + 1)) / (2**n)
    return min(1.0, 2.0 * tail)


def index_rows(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    indexed: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        if row["model"] != "gpt-4.1-nano":
            continue
        if row["condition"] not in CONDITIONS:
            continue
        key = (row["item_id"], row["condition"])
        if key in indexed:
            raise AssertionError(f"duplicate trajectory row for {key}")
        indexed[key] = row
    return indexed


def require_complete(indexed: dict[tuple[str, str], dict[str, str]], expected_items: int) -> list[str]:
    item_ids = sorted({item_id for item_id, _ in indexed})
    if len(item_ids) != expected_items:
        raise AssertionError(f"expected {expected_items} paired stress items, found {len(item_ids)}")
    missing = [
        f"{item_id}:{condition}"
        for item_id in item_ids
        for condition in CONDITIONS
        if (item_id, condition) not in indexed
    ]
    if missing:
        raise AssertionError(f"missing prompt-ablation rows: {missing[:10]}")
    return item_ids


def pct(value: float) -> float:
    return 100.0 * value


def summarize(indexed: dict[tuple[str, str], dict[str, str]], item_ids: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for condition in CONDITIONS:
        rows = [indexed[(item_id, condition)] for item_id in item_ids]
        initially_failed = sum(int(row["initially_failed"]) for row in rows)
        out.append(
            {
                "model": "gpt-4.1-nano",
                "condition": condition,
                "n": len(rows),
                "ftga": mean(float(row["ftga"]) for row in rows),
                "mean_rtt": mean(float(row["rtt"]) for row in rows),
                "mean_token_tax": mean(float(row["token_tax"]) for row in rows),
                "unresolved_rate": mean(float(row["unresolved"]) for row in rows),
                "initially_failed_n": initially_failed,
            }
        )
    return out


def summarize_by_family(indexed: dict[tuple[str, str], dict[str, str]], item_ids: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    families = sorted({indexed[(item_id, "baseline")]["task_family"] for item_id in item_ids})
    for condition in CONDITIONS:
        for family in families:
            rows = [
                indexed[(item_id, condition)]
                for item_id in item_ids
                if indexed[(item_id, condition)]["task_family"] == family
            ]
            initially_failed = sum(int(row["initially_failed"]) for row in rows)
            out.append(
                {
                    "model": "gpt-4.1-nano",
                    "condition": condition,
                    "task_family": family,
                    "n": len(rows),
                    "ftga": mean(float(row["ftga"]) for row in rows),
                    "mean_rtt": mean(float(row["rtt"]) for row in rows),
                    "mean_token_tax": mean(float(row["token_tax"]) for row in rows),
                    "unresolved_rate": mean(float(row["unresolved"]) for row in rows),
                    "initially_failed_n": initially_failed,
                }
            )
    return out


def paired_effects(indexed: dict[tuple[str, str], dict[str, str]], item_ids: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for before, after in COMPARISONS:
        ftga_deltas = []
        rtt_reductions = []
        token_tax_reductions = []
        unresolved_reductions = []
        improved = 0
        worsened = 0
        tied = 0
        for item_id in item_ids:
            before_row = indexed[(item_id, before)]
            after_row = indexed[(item_id, after)]
            ftga_delta = float(after_row["ftga"]) - float(before_row["ftga"])
            if ftga_delta > 0:
                improved += 1
            elif ftga_delta < 0:
                worsened += 1
            else:
                tied += 1
            ftga_deltas.append(ftga_delta)
            rtt_reductions.append(float(before_row["rtt"]) - float(after_row["rtt"]))
            token_tax_reductions.append(float(before_row["token_tax"]) - float(after_row["token_tax"]))
            unresolved_reductions.append(float(before_row["unresolved"]) - float(after_row["unresolved"]))
        out.append(
            {
                "comparison": f"{after}_minus_{before}",
                "n_pairs": len(item_ids),
                "ftga_improved": improved,
                "ftga_worsened": worsened,
                "ftga_tied": tied,
                "ftga_sign_test_p": sign_test_p_value(improved, worsened),
                "delta_ftga_pp": pct(mean(ftga_deltas)),
                "rtt_reduction": mean(rtt_reductions),
                "token_tax_reduction": mean(token_tax_reductions),
                "unresolved_reduction_pp": pct(mean(unresolved_reductions)),
            }
        )
    return out


def fmt_pct(value: float) -> str:
    return f"{pct(value):.1f}%"


def fmt_pp(value: float) -> str:
    return f"{value:+.1f} pp"


def parse_failure_types(value: str) -> list[str]:
    if not value:
        return []
    parsed = ast.literal_eval(value)
    if not isinstance(parsed, list):
        raise AssertionError(f"unexpected failure-type value: {value}")
    return [str(item) for item in parsed]


def excerpt(text: str, max_chars: int = 180) -> str:
    one_line = " ".join(text.split())
    if len(one_line) <= max_chars:
        return one_line
    return one_line[: max_chars - 3].rstrip() + "..."


def response_index(score_rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for row in score_rows:
        if row.get("model") != "gpt-4.1-nano" or int(row.get("turn", -1)) != 0:
            continue
        condition = str(row.get("condition"))
        if condition not in CONDITIONS:
            continue
        out[(row["item_id"], condition)] = row
    return out


def transition_label(content_row: dict[str, str], contract_row: dict[str, str]) -> str:
    content_ftga = int(content_row["ftga"])
    contract_ftga = int(contract_row["ftga"])
    if content_ftga == 1 and contract_ftga == 1:
        return "both_pass"
    if content_ftga == 0 and contract_ftga == 0:
        return "both_fail"
    if content_ftga == 1 and contract_ftga == 0:
        return "content_only_pass"
    return "contract_only_pass"


def rtt_label(content_row: dict[str, str], contract_row: dict[str, str]) -> str:
    content_rtt = int(content_row["rtt"])
    contract_rtt = int(contract_row["rtt"])
    if content_rtt < contract_rtt:
        return "content_lower_rtt"
    if content_rtt > contract_rtt:
        return "contract_lower_rtt"
    return "same_rtt"


def content_contract_item_rows(
    indexed: dict[tuple[str, str], dict[str, str]],
    responses: dict[tuple[str, str], dict[str, Any]],
    item_ids: list[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item_id in item_ids:
        content_row = indexed[(item_id, "content_preservation")]
        contract_row = indexed[(item_id, "contract")]
        content_response = responses.get((item_id, "content_preservation"), {})
        contract_response = responses.get((item_id, "contract"), {})
        rows.append(
            {
                "item_id": item_id,
                "language_pair": content_row["language_pair"],
                "task_family": content_row["task_family"],
                "transition": transition_label(content_row, contract_row),
                "rtt_transition": rtt_label(content_row, contract_row),
                "content_ftga": int(content_row["ftga"]),
                "contract_ftga": int(contract_row["ftga"]),
                "content_rtt": int(content_row["rtt"]),
                "contract_rtt": int(contract_row["rtt"]),
                "content_token_tax": round(float(content_row["token_tax"]), 3),
                "contract_token_tax": round(float(contract_row["token_tax"]), 3),
                "content_first_failure_types": ";".join(parse_failure_types(content_row["first_failure_types"])),
                "contract_first_failure_types": ";".join(parse_failure_types(contract_row["first_failure_types"])),
                "content_first_response_excerpt": excerpt(str(content_response.get("response", ""))),
                "contract_first_response_excerpt": excerpt(str(contract_response.get("response", ""))),
            }
        )
    return rows


def summarize_transitions(item_rows: list[dict[str, Any]], group_fields: tuple[str, ...]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for row in item_rows:
        groups.setdefault(tuple(str(row[field]) for field in group_fields), []).append(row)

    out: list[dict[str, Any]] = []
    for group, rows in sorted(groups.items()):
        base = {field: value for field, value in zip(group_fields, group)}
        transitions = {name: sum(1 for row in rows if row["transition"] == name) for name in ("both_pass", "content_only_pass", "contract_only_pass", "both_fail")}
        rtt = {name: sum(1 for row in rows if row["rtt_transition"] == name) for name in ("content_lower_rtt", "contract_lower_rtt", "same_rtt")}
        base.update(
            {
                "n": len(rows),
                **transitions,
                **rtt,
            }
        )
        out.append(base)
    return out


def transition_examples(item_rows: list[dict[str, Any]], limit_per_transition: int = 4) -> list[dict[str, Any]]:
    wanted = ("content_only_pass", "contract_only_pass", "both_fail")
    out: list[dict[str, Any]] = []
    for transition in wanted:
        rows = [row for row in item_rows if row["transition"] == transition]
        rows.sort(key=lambda row: (row["task_family"], row["language_pair"], row["item_id"]))
        out.extend(rows[:limit_per_transition])
    return out


def write_markdown(
    path: Path,
    summary_rows: list[dict[str, Any]],
    family_rows: list[dict[str, Any]],
    effect_rows: list[dict[str, Any]],
    transition_by_family: list[dict[str, Any]],
    transition_examples_rows: list[dict[str, Any]],
    *,
    n_items: int,
) -> None:
    by_condition = {row["condition"]: row for row in summary_rows}
    by_effect = {row["comparison"]: row for row in effect_rows}
    by_family = {(row["condition"], row["task_family"]): row for row in family_rows}
    lines = [
        "# Prompt-Ablation Diagnostic",
        "",
        "This is a single-model diagnostic on `gpt-4.1-nano`, not a paper-facing",
        "three-model claim. It compares the baseline, a generic-helpfulness prompt,",
        "a narrow content-preservation prompt, and the full Global Interaction",
        f"Contract on the same {n_items}-item stress pilot.",
        "",
        "## Aggregate Metrics",
        "",
        "| Condition | FTGA | Mean RTT | Token tax | Unresolved | Initial failures |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for condition in CONDITIONS:
        row = by_condition[condition]
        lines.append(
            "| "
            f"{condition} | {fmt_pct(float(row['ftga']))} | "
            f"{float(row['mean_rtt']):.2f} | {float(row['mean_token_tax']):.2f}x | "
            f"{fmt_pct(float(row['unresolved_rate']))} | {row['initially_failed_n']} |"
        )

    lines.extend(
        [
            "",
            "## Paired Effects",
            "",
            "| Comparison | FTGA delta | Improved / worsened / tied | Sign-test p | RTT reduction | Token-tax reduction | Unresolved reduction |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for before, after in COMPARISONS:
        comparison = f"{after}_minus_{before}"
        row = by_effect[comparison]
        lines.append(
            "| "
            f"{comparison} | {fmt_pp(float(row['delta_ftga_pp']))} | "
            f"{row['ftga_improved']} / {row['ftga_worsened']} / {row['ftga_tied']} | "
            f"{float(row['ftga_sign_test_p']):.4f} | {float(row['rtt_reduction']):.2f} | "
            f"{float(row['token_tax_reduction']):.2f}x | {fmt_pp(float(row['unresolved_reduction_pp']))} |"
        )

    lines.extend(
        [
            "",
            "## Family Slice",
            "",
            "| Task family | Baseline FTGA | Generic FTGA | Content-preservation FTGA | Full-contract FTGA |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for family in sorted({row["task_family"] for row in family_rows}):
        lines.append(
            "| "
            f"{family} | "
            f"{fmt_pct(float(by_family[('baseline', family)]['ftga']))} | "
            f"{fmt_pct(float(by_family[('generic_helpfulness', family)]['ftga']))} | "
            f"{fmt_pct(float(by_family[('content_preservation', family)]['ftga']))} | "
            f"{fmt_pct(float(by_family[('contract', family)]['ftga']))} |"
        )

    lines.extend(
        [
            "",
            "## Content vs Full-Contract Transitions",
            "",
            "| Task family | Both pass | Content only pass | Contract only pass | Both fail | Content lower RTT | Contract lower RTT | Same RTT |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in transition_by_family:
        lines.append(
            "| "
            f"{row['task_family']} | {row['both_pass']} | {row['content_only_pass']} | "
            f"{row['contract_only_pass']} | {row['both_fail']} | {row['content_lower_rtt']} | "
            f"{row['contract_lower_rtt']} | {row['same_rtt']} |"
        )

    lines.extend(
        [
            "",
            "## Disagreement Examples",
            "",
            "| Item | Family | Language | Transition | Content first response | Contract first response |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in transition_examples_rows:
        content_excerpt = str(row["content_first_response_excerpt"]).replace("|", "/")
        contract_excerpt = str(row["contract_first_response_excerpt"]).replace("|", "/")
        lines.append(
            "| "
            f"{row['item_id']} | {row['task_family']} | {row['language_pair']} | {row['transition']} | "
            f"{content_excerpt} | {contract_excerpt} |"
        )

    content = by_condition["content_preservation"]
    contract = by_condition["contract"]
    content_vs_base = by_effect["content_preservation_minus_baseline"]
    contract_vs_content = by_effect["contract_minus_content_preservation"]
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"The narrow content-preservation prompt reaches {fmt_pct(float(content['ftga']))} FTGA,",
            f"above the full contract's {fmt_pct(float(contract['ftga']))} on this nano diagnostic.",
            f"Relative to baseline, content preservation adds {fmt_pp(float(content_vs_base['delta_ftga_pp']))}",
            "FTGA and lowers token tax. The full contract trails content preservation by",
            f"{fmt_pp(float(contract_vs_content['delta_ftga_pp']))} FTGA on the same items.",
            "",
            "This should be reported as mechanism evidence and a claim boundary: the",
            "main three-model result still uses the pre-registered Global Interaction",
            "Contract, but the best nano prompt tested in this diagnostic is the",
            "narrower content-preservation scaffold. The result suggests that content",
            "language and literal-preservation rules drive much of the mitigation.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--main-trajectories",
        type=Path,
        default=Path("results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv"),
    )
    parser.add_argument(
        "--generic-trajectories",
        type=Path,
        default=Path("results/tables/openai_nano_stress_v02_full120_generic_helpfulness/trajectory_metrics.csv"),
    )
    parser.add_argument(
        "--content-trajectories",
        type=Path,
        default=Path("results/tables/openai_nano_stress_v02_full120_content_preservation/trajectory_metrics.csv"),
    )
    parser.add_argument(
        "--main-scores",
        type=Path,
        default=Path("results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl"),
    )
    parser.add_argument(
        "--generic-scores",
        type=Path,
        default=Path("results/scores/openai_nano_stress_v02_full120_generic_helpfulness_auto_scores.jsonl"),
    )
    parser.add_argument(
        "--content-scores",
        type=Path,
        default=Path("results/scores/openai_nano_stress_v02_full120_content_preservation_auto_scores.jsonl"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables/openai_nano_stress_v02_full120_prompt_ablation"))
    parser.add_argument("--out-md", type=Path, default=Path("paper/prompt_ablation_analysis.md"))
    parser.add_argument("--expected-items", type=int, default=120)
    args = parser.parse_args()

    indexed = index_rows(
        read_csv(args.main_trajectories)
        + read_csv(args.generic_trajectories)
        + read_csv(args.content_trajectories)
    )
    item_ids = require_complete(indexed, args.expected_items)
    summary_rows = summarize(indexed, item_ids)
    family_rows = summarize_by_family(indexed, item_ids)
    effect_rows = paired_effects(indexed, item_ids)
    responses = response_index(
        read_jsonl(args.main_scores)
        + read_jsonl(args.generic_scores)
        + read_jsonl(args.content_scores)
    )
    item_rows = content_contract_item_rows(indexed, responses, item_ids)
    transition_by_family = summarize_transitions(item_rows, ("task_family",))
    transition_by_language = summarize_transitions(item_rows, ("language_pair",))
    example_rows = transition_examples(item_rows)
    write_csv(args.out_dir / "prompt_ablation_summary.csv", summary_rows)
    write_csv(args.out_dir / "prompt_ablation_by_family.csv", family_rows)
    write_csv(args.out_dir / "prompt_ablation_paired_effects.csv", effect_rows)
    write_csv(args.out_dir / "prompt_ablation_contract_vs_content_items.csv", item_rows)
    write_csv(args.out_dir / "prompt_ablation_contract_vs_content_by_family.csv", transition_by_family)
    write_csv(args.out_dir / "prompt_ablation_contract_vs_content_by_language.csv", transition_by_language)
    write_csv(args.out_dir / "prompt_ablation_contract_vs_content_examples.csv", example_rows)
    write_markdown(
        args.out_md,
        summary_rows,
        family_rows,
        effect_rows,
        transition_by_family,
        example_rows,
        n_items=len(item_ids),
    )
    print(f"wrote prompt-ablation diagnostic to {args.out_md} and {args.out_dir}")


if __name__ == "__main__":
    main()
