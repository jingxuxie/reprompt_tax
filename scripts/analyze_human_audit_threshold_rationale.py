#!/usr/bin/env python
"""Explain the numeric thresholds behind future human/native-review claim gates."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any


ACCEPTANCE_RULES = Path("results/tables/human_audit_acceptance_rules_v02/human_audit_acceptance_rules.csv")
OUT_DIR = Path("results/tables/human_audit_threshold_rationale_v02")
OUT_MD = Path("paper/human_audit_threshold_rationale_v02.md")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing threshold-rationale input {path}")
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, f"refusing to write empty threshold-rationale table {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def wilson_interval(successes: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    require(0 <= successes <= n, f"invalid Wilson count {successes}/{n}")
    if n == 0:
        return (0.0, 0.0)
    phat = successes / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    radius = z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n) / denom
    return max(0.0, center - radius), min(1.0, center + radius)


def pct(value: float) -> str:
    return f"{100 * value:.1f}"


def add_rate_row(
    rows: list[dict[str, Any]],
    *,
    surface: str,
    metric: str,
    threshold_count: int,
    denominator: int,
    rationale: str,
) -> None:
    low, high = wilson_interval(threshold_count, denominator)
    rows.append(
        {
            "surface": surface,
            "metric": metric,
            "threshold_count": threshold_count,
            "denominator": denominator,
            "threshold_rate_pct": pct(threshold_count / denominator),
            "wilson_95_low_pct": pct(low),
            "wilson_95_high_pct": pct(high),
            "rationale": rationale,
        }
    )


def build_rows(rule_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rule in rule_rows:
        surface = rule["surface"]
        expected_rows = int(rule["expected_rows"])
        if rule["review_type"] == "human_audit_completed_labels":
            add_rate_row(
                rows,
                surface=surface,
                metric="overall_pass_agreement",
                threshold_count=int(rule["min_pass_agreements"]),
                denominator=expected_rows,
                rationale="requires at least 90 percent overall pass/fail agreement before claiming scorer support",
            )
            add_rate_row(
                rows,
                surface=surface,
                metric="component_agreement",
                threshold_count=int(rule["min_component_agreements"]),
                denominator=expected_rows * 5,
                rationale="requires at least 85 percent agreement across language, script, preservation, task, and register/locale components",
            )
        elif rule["review_type"] == "native_review_scaffold_release":
            add_rate_row(
                rows,
                surface=surface,
                metric="release_usable_rows",
                threshold_count=int(rule["min_release_usable_rows"]),
                denominator=expected_rows,
                rationale="requires every synthetic v0.3 row to be release usable before any v0.3 benchmark-evidence claim",
            )
        else:
            raise AssertionError(f"unexpected review type {rule['review_type']}")
    return rows


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Human/Native Review Threshold Rationale",
        "",
        "This report explains the numeric gates in",
        "`paper/human_audit_acceptance_rules_v02.md`. It does not report completed",
        "labels; it only makes the pre-specified future claim thresholds auditable.",
        "",
        "## Thresholds",
        "",
        "| Surface | Metric | Threshold | Rate | Wilson 95% interval | Rationale |",
        "|---|---|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['surface']} | {row['metric']} | "
            f"{row['threshold_count']}/{row['denominator']} | "
            f"{row['threshold_rate_pct']}% | "
            f"[{row['wilson_95_low_pct']}%, {row['wilson_95_high_pct']}%] | "
            f"{row['rationale']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The two human-audit surfaces use an overall pass/fail agreement gate",
            "  and a stricter component-level audit gate because language, script,",
            "  preservation, task completion, and register/locale can disagree.",
            "- The v0.3 coverage surface has a 60/60 release-usability gate because",
            "  it validates synthetic benchmark rows rather than model outputs.",
            "- Passing these thresholds is necessary but not sufficient: the completed",
            "  label validators, qualified rosters, and claim-gate analyzer must also",
            "  pass before the paper claims native/near-native validation.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--acceptance-rules", type=Path, default=ACCEPTANCE_RULES)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    rows = build_rows(read_csv(args.acceptance_rules))
    write_csv(args.out_dir / "human_audit_threshold_rationale.csv", rows)
    write_markdown(args.out_md, rows)
    print(f"wrote human/native-review threshold rationale to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
