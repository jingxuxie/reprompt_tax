#!/usr/bin/env python
"""Decompose first-turn contract fixes and regressions by slice."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable


TRAJECTORY_PATHS = [
    Path("results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv"),
    Path("results/tables/openai_gpt54mini_stress_v02_full120/trajectory_metrics.csv"),
    Path("results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv"),
]
OUT_DIR = Path("results/tables/contract_benefit_decomposition_v02")
OUT_MD = Path("paper/contract_benefit_decomposition_v02.md")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing trajectory table {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, f"refusing to write empty decomposition table {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def generation(model: str) -> str:
    return "GPT-5.x family" if model.startswith("gpt-5") else "GPT-4.1 family"


def transition(baseline_ftga: int, contract_ftga: int) -> str:
    if baseline_ftga == 0 and contract_ftga == 1:
        return "fix"
    if baseline_ftga == 1 and contract_ftga == 0:
        return "regression"
    if baseline_ftga == 0 and contract_ftga == 0:
        return "both_fail"
    return "both_pass"


def paired_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        rows.extend(read_csv(path))
    by_pair: dict[tuple[str, str], dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_pair[(row["model"], row["item_id"])][row["condition"]] = row

    pairs: list[dict[str, Any]] = []
    for (model, item_id), by_condition in sorted(by_pair.items()):
        require({"baseline", "contract"} <= set(by_condition), f"missing baseline/contract pair for {model}/{item_id}")
        baseline = by_condition["baseline"]
        contract = by_condition["contract"]
        require(baseline["task_family"] == contract["task_family"], f"task-family mismatch for {model}/{item_id}")
        require(baseline["language_pair"] == contract["language_pair"], f"language-pair mismatch for {model}/{item_id}")
        baseline_ftga = int(baseline["ftga"])
        contract_ftga = int(contract["ftga"])
        pairs.append(
            {
                "model": model,
                "generation": generation(model),
                "item_id": item_id,
                "language_pair": baseline["language_pair"],
                "task_family": baseline["task_family"],
                "transition": transition(baseline_ftga, contract_ftga),
                "baseline_ftga": baseline_ftga,
                "contract_ftga": contract_ftga,
                "rtt_delta": float(baseline["rtt"]) - float(contract["rtt"]),
                "token_tax_delta": float(baseline["token_tax"]) - float(contract["token_tax"]),
            }
        )
    require(len(pairs) == 600, f"expected 600 paired model-item rows, found {len(pairs)}")
    return pairs


def aggregate(
    pairs: list[dict[str, Any]],
    *,
    key_fn: Callable[[dict[str, Any]], tuple[str, ...]],
    fields: list[str],
    total_fixes: int,
    total_net: int,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
    for row in pairs:
        grouped[key_fn(row)][row["transition"]] += 1
    out: list[dict[str, Any]] = []
    for key, counts in sorted(grouped.items()):
        fixes = counts["fix"]
        regressions = counts["regression"]
        n_pairs = sum(counts.values())
        result = {field: value for field, value in zip(fields, key)}
        result.update(
            {
                "n_pairs": n_pairs,
                "both_pass": counts["both_pass"],
                "both_fail": counts["both_fail"],
                "fixes": fixes,
                "regressions": regressions,
                "net_first_turn_gain": fixes - regressions,
                "fix_share_of_all_fixes_pct": round(100 * fixes / total_fixes, 1) if total_fixes else 0.0,
                "net_share_of_total_net_gain_pct": round(100 * (fixes - regressions) / total_net, 1) if total_net else 0.0,
            }
        )
        out.append(result)
    return out


def write_markdown(
    path: Path,
    *,
    overall: dict[str, Any],
    by_family: list[dict[str, Any]],
    by_generation: list[dict[str, Any]],
    by_language: list[dict[str, Any]],
    by_generation_family: list[dict[str, Any]],
) -> None:
    lines = [
        "# Contract Benefit Decomposition",
        "",
        "This artifact decomposes first-turn contract fixes and regressions across",
        "all five full 120-item model runs. It uses saved trajectory metrics only;",
        "it makes no API calls and does not replace native/near-native validation.",
        "",
        "## Overall",
        "",
        "| Pairs | Both pass | Both fail | Fixes | Regressions | Net first-turn gain |",
        "|---:|---:|---:|---:|---:|---:|",
        (
            f"| {overall['n_pairs']} | {overall['both_pass']} | {overall['both_fail']} | "
            f"{overall['fixes']} | {overall['regressions']} | {overall['net_first_turn_gain']} |"
        ),
        "",
        "## By Task Family",
        "",
        "| Task family | Pairs | Fixes | Regressions | Net gain | Fix share | Net share |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in by_family:
        lines.append(
            f"| {row['task_family']} | {row['n_pairs']} | {row['fixes']} | "
            f"{row['regressions']} | {row['net_first_turn_gain']} | "
            f"{row['fix_share_of_all_fixes_pct']}% | {row['net_share_of_total_net_gain_pct']}% |"
        )
    lines.extend(
        [
            "",
            "## By Generation",
            "",
            "| Generation | Pairs | Fixes | Regressions | Net gain | Fix share |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in by_generation:
        lines.append(
            f"| {row['generation']} | {row['n_pairs']} | {row['fixes']} | "
            f"{row['regressions']} | {row['net_first_turn_gain']} | "
            f"{row['fix_share_of_all_fixes_pct']}% |"
        )
    lines.extend(
        [
            "",
            "## By Language Pair",
            "",
            "| Language pair | Pairs | Fixes | Regressions | Net gain | Fix share |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in by_language:
        lines.append(
            f"| {row['language_pair']} | {row['n_pairs']} | {row['fixes']} | "
            f"{row['regressions']} | {row['net_first_turn_gain']} | "
            f"{row['fix_share_of_all_fixes_pct']}% |"
        )
    lines.extend(
        [
            "",
            "## By Generation And Family",
            "",
            "| Generation | Task family | Pairs | Fixes | Regressions | Net gain |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in by_generation_family:
        lines.append(
            f"| {row['generation']} | {row['task_family']} | {row['n_pairs']} | "
            f"{row['fixes']} | {row['regressions']} | {row['net_first_turn_gain']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Across all five full-run models, the contract produces 67 first-turn",
            "fixes and 6 first-turn regressions, for a net first-turn gain of 61",
            "model-item pairs.",
            "",
            "Editing preservation accounts for 61 of 67 fixes (91.0%) and zero",
            "regressions. Its +61 net gain exactly equals the overall +61 net",
            "first-turn gain. Output-language inference adds one net fix, quote",
            "preservation contributes one net regression, and script/register/locale",
            "is net zero.",
            "",
            "This supports the paper's mechanism claim: the Global Interaction",
            "Contract mainly reduces implicit editing-preservation failures rather",
            "than uniformly improving every multilingual task family.",
            "",
            "Claim boundary: this is automatic-score decomposition over a synthetic",
            "stress pilot. It strengthens the mechanism story but does not unlock",
            "native/near-native validation claims.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    pairs = paired_rows(TRAJECTORY_PATHS)
    counts = Counter(row["transition"] for row in pairs)
    total_fixes = counts["fix"]
    total_net = counts["fix"] - counts["regression"]
    overall = {
        "n_pairs": len(pairs),
        "both_pass": counts["both_pass"],
        "both_fail": counts["both_fail"],
        "fixes": counts["fix"],
        "regressions": counts["regression"],
        "net_first_turn_gain": total_net,
    }
    by_family = aggregate(
        pairs,
        key_fn=lambda row: (row["task_family"],),
        fields=["task_family"],
        total_fixes=total_fixes,
        total_net=total_net,
    )
    by_generation = aggregate(
        pairs,
        key_fn=lambda row: (row["generation"],),
        fields=["generation"],
        total_fixes=total_fixes,
        total_net=total_net,
    )
    by_language = aggregate(
        pairs,
        key_fn=lambda row: (row["language_pair"],),
        fields=["language_pair"],
        total_fixes=total_fixes,
        total_net=total_net,
    )
    by_generation_family = aggregate(
        pairs,
        key_fn=lambda row: (row["generation"], row["task_family"]),
        fields=["generation", "task_family"],
        total_fixes=total_fixes,
        total_net=total_net,
    )

    write_csv(args.out_dir / "contract_benefit_overall.csv", [overall])
    write_csv(args.out_dir / "contract_benefit_by_family.csv", by_family)
    write_csv(args.out_dir / "contract_benefit_by_generation.csv", by_generation)
    write_csv(args.out_dir / "contract_benefit_by_language.csv", by_language)
    write_csv(args.out_dir / "contract_benefit_by_generation_family.csv", by_generation_family)
    write_markdown(
        args.out_md,
        overall=overall,
        by_family=by_family,
        by_generation=by_generation,
        by_language=by_language,
        by_generation_family=by_generation_family,
    )
    print(f"wrote contract-benefit decomposition to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
