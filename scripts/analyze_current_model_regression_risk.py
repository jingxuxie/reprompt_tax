#!/usr/bin/env python
"""Analyze contract-induced regression risk for current-model refresh runs."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Any


CURRENT_MODELS = {
    "gpt-5.4-mini": {
        "base": Path("results/tables/openai_gpt54mini_stress_v02_full120/trajectory_metrics.csv"),
        "content": Path("results/tables/openai_gpt54mini_stress_v02_full120_content_preservation/trajectory_metrics.csv"),
    },
    "gpt-5.5": {
        "base": Path("results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv"),
        "content": Path("results/tables/openai_gpt55_stress_v02_full120_content_preservation/trajectory_metrics.csv"),
    },
}
OUT_DIR = Path("results/tables/current_model_regression_risk_v02")
OUT_MD = Path("paper/current_model_regression_risk_v02.md")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def pct(numerator: int, denominator: int) -> float:
    return round(100.0 * numerator / denominator, 1) if denominator else 0.0


def paired_rows(base_path: Path, model: str) -> list[tuple[dict[str, str], dict[str, str]]]:
    by_item: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in read_csv(base_path):
        require(row["model"] == model, f"{base_path} contains unexpected model {row['model']}")
        by_item[row["item_id"]][row["condition"]] = row

    pairs: list[tuple[dict[str, str], dict[str, str]]] = []
    for item_id, conditions in sorted(by_item.items()):
        require(set(conditions) == {"baseline", "contract"}, f"{model}/{item_id} missing baseline/contract pair")
        pairs.append((conditions["baseline"], conditions["contract"]))
    require(len(pairs) == 120, f"{model} expected 120 paired items, found {len(pairs)}")
    return pairs


def content_lookup(path: Path, model: str) -> dict[str, dict[str, str]]:
    rows = [row for row in read_csv(path) if row["model"] == model and row["condition"] == "content_preservation"]
    require(len(rows) == 120, f"{model} expected 120 content-preservation rows, found {len(rows)}")
    return {row["item_id"]: row for row in rows}


def is_pass(row: dict[str, str]) -> bool:
    return row["ftga"] == "1"


def is_unresolved(row: dict[str, str]) -> bool:
    return row["unresolved"] == "1"


def summarize_model(
    model: str,
    pairs: list[tuple[dict[str, str], dict[str, str]]],
    content: dict[str, dict[str, str]],
) -> dict[str, Any]:
    ftga_fixes = ftga_regressions = both_pass = both_fail = 0
    resolved_to_unresolved = unresolved_to_resolved = 0
    content_pass_on_contract_regressions = 0
    content_unresolved_on_contract_regressions = 0
    contract_regression_items: list[str] = []

    for baseline, contract in pairs:
        item_id = baseline["item_id"]
        base_pass = is_pass(baseline)
        contract_pass = is_pass(contract)
        if base_pass and contract_pass:
            both_pass += 1
        elif not base_pass and contract_pass:
            ftga_fixes += 1
        elif base_pass and not contract_pass:
            ftga_regressions += 1
            contract_regression_items.append(item_id)
            if is_pass(content[item_id]):
                content_pass_on_contract_regressions += 1
            if is_unresolved(content[item_id]):
                content_unresolved_on_contract_regressions += 1
        else:
            both_fail += 1

        if is_unresolved(baseline) and not is_unresolved(contract):
            unresolved_to_resolved += 1
        if not is_unresolved(baseline) and is_unresolved(contract):
            resolved_to_unresolved += 1

    return {
        "model": model,
        "n_pairs": len(pairs),
        "both_pass_n": both_pass,
        "baseline_fail_contract_pass_n": ftga_fixes,
        "baseline_pass_contract_fail_n": ftga_regressions,
        "both_fail_n": both_fail,
        "ftga_regression_rate_pct": pct(ftga_regressions, len(pairs)),
        "baseline_unresolved_contract_resolved_n": unresolved_to_resolved,
        "baseline_resolved_contract_unresolved_n": resolved_to_unresolved,
        "content_pass_on_contract_regression_n": content_pass_on_contract_regressions,
        "content_unresolved_on_contract_regression_n": content_unresolved_on_contract_regressions,
        "contract_regression_items": ";".join(contract_regression_items) if contract_regression_items else "none",
    }


def regression_case_rows(
    model: str,
    pairs: list[tuple[dict[str, str], dict[str, str]]],
    content: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for baseline, contract in pairs:
        if not (is_pass(baseline) and not is_pass(contract)):
            continue
        content_row = content[baseline["item_id"]]
        out.append(
            {
                "model": model,
                "item_id": baseline["item_id"],
                "language_pair": baseline["language_pair"],
                "task_family": baseline["task_family"],
                "baseline_rtt": int(baseline["rtt"]),
                "contract_rtt": int(contract["rtt"]),
                "contract_unresolved": int(contract["unresolved"]),
                "contract_failure_types": contract["first_failure_types"],
                "content_preservation_ftga": int(content_row["ftga"]),
                "content_preservation_rtt": int(content_row["rtt"]),
                "content_preservation_unresolved": int(content_row["unresolved"]),
                "content_preservation_failure_types": content_row["first_failure_types"],
            }
        )
    return out


def unresolved_shift_rows(
    model: str,
    pairs: list[tuple[dict[str, str], dict[str, str]]],
    content: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for baseline, contract in pairs:
        if not (not is_unresolved(baseline) and is_unresolved(contract)):
            continue
        content_row = content[baseline["item_id"]]
        out.append(
            {
                "model": model,
                "item_id": baseline["item_id"],
                "language_pair": baseline["language_pair"],
                "task_family": baseline["task_family"],
                "baseline_ftga": int(baseline["ftga"]),
                "contract_ftga": int(contract["ftga"]),
                "contract_failure_types": contract["first_failure_types"],
                "content_preservation_ftga": int(content_row["ftga"]),
                "content_preservation_unresolved": int(content_row["unresolved"]),
                "content_preservation_failure_types": content_row["first_failure_types"],
            }
        )
    return out


def row_by(rows: list[dict[str, Any]], **kwargs: str) -> dict[str, Any]:
    for row in rows:
        if all(str(row[key]) == value for key, value in kwargs.items()):
            return row
    raise AssertionError(f"missing row for {kwargs}")


def write_markdown(
    path: Path,
    *,
    summary_rows: list[dict[str, Any]],
    regression_rows: list[dict[str, Any]],
    unresolved_rows: list[dict[str, Any]],
) -> None:
    g54 = row_by(summary_rows, model="gpt-5.4-mini")
    g55 = row_by(summary_rows, model="gpt-5.5")
    g54_regressions = [row for row in regression_rows if row["model"] == "gpt-5.4-mini"]
    g55_regressions = [row for row in regression_rows if row["model"] == "gpt-5.5"]
    g54_unresolved = [row for row in unresolved_rows if row["model"] == "gpt-5.4-mini"]

    lines = [
        "# Current-Model Contract Regression Risk",
        "",
        "This diagnostic isolates paired cases where the contract hurts first-turn",
        "automatic success relative to the baseline. It uses saved full-120",
        "trajectory metrics plus saved content-preservation rows; it makes no API",
        "calls.",
        "",
        "## Summary",
        "",
        "| Model | N | Fixes | Regressions | Both fail | Resolved->unresolved | Content-preservation pass on regression cases |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            "| "
            f"{row['model']} | {row['n_pairs']} | {row['baseline_fail_contract_pass_n']} | "
            f"{row['baseline_pass_contract_fail_n']} | {row['both_fail_n']} | "
            f"{row['baseline_resolved_contract_unresolved_n']} | "
            f"{row['content_pass_on_contract_regression_n']} |"
        )

    lines.extend(
        [
            "",
            "## First-Turn Regression Cases",
            "",
            "| Model | Item | Language | Family | Contract RTT | Contract unresolved | Contract failure | Content-preservation FTGA | Content unresolved |",
            "|---|---|---|---|---:|---:|---|---:|---:|",
        ]
    )
    if regression_rows:
        for row in regression_rows:
            lines.append(
                "| "
                f"{row['model']} | {row['item_id']} | {row['language_pair']} | {row['task_family']} | "
                f"{row['contract_rtt']} | {row['contract_unresolved']} | {row['contract_failure_types']} | "
                f"{row['content_preservation_ftga']} | {row['content_preservation_unresolved']} |"
            )
    else:
        lines.append("| none | none | none | none |  |  | none |  |  |")

    lines.extend(
        [
            "",
            "## Resolved-To-Unresolved Shifts",
            "",
            "| Model | Item | Language | Family | Baseline FTGA | Contract FTGA | Contract failure | Content-preservation FTGA | Content unresolved |",
            "|---|---|---|---|---:|---:|---|---:|---:|",
        ]
    )
    if unresolved_rows:
        for row in unresolved_rows:
            lines.append(
                "| "
                f"{row['model']} | {row['item_id']} | {row['language_pair']} | {row['task_family']} | "
                f"{row['baseline_ftga']} | {row['contract_ftga']} | {row['contract_failure_types']} | "
                f"{row['content_preservation_ftga']} | {row['content_preservation_unresolved']} |"
            )
    else:
        lines.append("| none | none | none | none |  |  | none |  |  |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"`gpt-5.5` has {g55['baseline_fail_contract_pass_n']} baseline-fail/contract-pass fixes, "
            f"{g55['baseline_pass_contract_fail_n']} first-turn regressions, and "
            f"{g55['baseline_resolved_contract_unresolved_n']} resolved-to-unresolved shifts. This supports the clean flagship mitigation claim.",
            "",
            f"`gpt-5.4-mini` has {g54['baseline_fail_contract_pass_n']} fixes but {g54['baseline_pass_contract_fail_n']} first-turn regressions "
            f"and {g54['baseline_resolved_contract_unresolved_n']} resolved-to-unresolved shifts. The regressions are concentrated in quote-preservation and script/register/locale rows, not in output-language inference.",
            "",
            f"Content-preservation avoids first-turn failure on {g54['content_pass_on_contract_regression_n']} of the {len(g54_regressions)} "
            "`gpt-5.4-mini` regression cases and leaves only "
            f"{g54['content_unresolved_on_contract_regression_n']} unresolved among those regression cases. This reinforces the mechanism result: for the lower-cost current model, the full contract is not uniformly safer than the narrower preservation scaffold.",
            "",
            f"The resolved-to-unresolved set has {len(g54_unresolved)} `gpt-5.4-mini` cases and {g55['baseline_resolved_contract_unresolved_n']} `gpt-5.5` cases. "
            "The lower-cost result should therefore be worded as bounded token-burden and directional FTGA improvement, with explicit regression risk.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    summary_rows: list[dict[str, Any]] = []
    regression_rows: list[dict[str, Any]] = []
    unresolved_rows: list[dict[str, Any]] = []
    for model, paths in CURRENT_MODELS.items():
        pairs = paired_rows(paths["base"], model)
        content = content_lookup(paths["content"], model)
        summary_rows.append(summarize_model(model, pairs, content))
        regression_rows.extend(regression_case_rows(model, pairs, content))
        unresolved_rows.extend(unresolved_shift_rows(model, pairs, content))

    write_csv(args.out_dir / "current_model_regression_risk_summary.csv", summary_rows)
    write_csv(args.out_dir / "current_model_contract_regression_cases.csv", regression_rows)
    write_csv(args.out_dir / "current_model_resolved_to_unresolved_cases.csv", unresolved_rows)
    write_markdown(args.out_md, summary_rows=summary_rows, regression_rows=regression_rows, unresolved_rows=unresolved_rows)
    print(f"wrote current-model regression-risk analysis to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
