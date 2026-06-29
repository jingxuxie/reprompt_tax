#!/usr/bin/env python
"""Create simple paper figures from RePromptTax metric CSVs."""

from __future__ import annotations

import argparse
import csv
import os
from collections import defaultdict
from pathlib import Path
from typing import Any


os.environ.setdefault("MPLCONFIGDIR", "/tmp/reprompt_tax_mplconfig")

MODEL_ORDER = {
    "gpt-4.1-nano": 0,
    "gpt-4.1-mini": 1,
    "gpt-4.1": 2,
    "gpt-5.4-mini": 3,
    "gpt-5.5": 4,
}
CONDITION_ORDER = {
    "baseline": 0,
    "contract": 1,
    "content_preservation": 2,
    "generic_helpfulness": 3,
}


def read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def pct(value: str) -> float:
    return 100.0 * float(value)


def row_key(row: dict[str, Any]) -> tuple[int, int, str, str]:
    return (
        MODEL_ORDER.get(str(row["model"]), 999),
        CONDITION_ORDER.get(str(row["condition"]), 999),
        str(row["model"]),
        str(row["condition"]),
    )


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_ftga_source(summary_rows: list[dict[str, Any]], out_path: Path) -> None:
    rows = [
        {
            "model": row["model"],
            "condition": row["condition"],
            "n": row["n"],
            "ftga_pct": f"{pct(row['ftga']):.1f}",
        }
        for row in sorted(summary_rows, key=row_key)
    ]
    write_csv(out_path, rows, ["model", "condition", "n", "ftga_pct"])


def figure_ftga(summary_rows: list[dict[str, Any]], out_path: Path) -> None:
    import matplotlib.pyplot as plt

    summary_rows = sorted(summary_rows, key=row_key)
    labels = [f"{row['model']}\n{row['condition']}" for row in summary_rows]
    values = [pct(row["ftga"]) for row in summary_rows]
    colors = ["#4C78A8" if row["condition"] == "baseline" else "#F58518" for row in summary_rows]

    fig, ax = plt.subplots(figsize=(max(6, 0.8 * len(labels)), 4))
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("First-turn global alignment (%)")
    ax.set_ylim(0, 100)
    ax.tick_params(axis="x", labelrotation=35)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def repair_curve_rows(trajectory_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    for row in trajectory_rows:
        groups[(row["model"], row["condition"])].append(int(row["rtt"]))

    rows = []
    for key, rtts in sorted(
        groups.items(),
        key=lambda item: row_key({"model": item[0][0], "condition": item[0][1]}),
    ):
        n = len(rtts)
        rows.append(
            {
                "model": key[0],
                "condition": key[1],
                "n": str(n),
                "solved_after_first_turn_pct": f"{100.0 * sum(rtt <= 0 for rtt in rtts) / n:.1f}",
                "solved_after_one_repair_pct": f"{100.0 * sum(rtt <= 1 for rtt in rtts) / n:.1f}",
                "solved_after_two_repairs_pct": f"{100.0 * sum(rtt <= 2 for rtt in rtts) / n:.1f}",
            }
        )
    return rows


def write_repair_curve_source(trajectory_rows: list[dict[str, Any]], out_path: Path) -> None:
    write_csv(
        out_path,
        repair_curve_rows(trajectory_rows),
        [
            "model",
            "condition",
            "n",
            "solved_after_first_turn_pct",
            "solved_after_one_repair_pct",
            "solved_after_two_repairs_pct",
        ],
    )


def figure_repair_curve(trajectory_rows: list[dict[str, Any]], out_path: Path) -> None:
    import matplotlib.pyplot as plt

    source_rows = repair_curve_rows(trajectory_rows)
    labels = [f"{row['model']}\n{row['condition']}" for row in source_rows]
    solved_0 = [float(row["solved_after_first_turn_pct"]) for row in source_rows]
    solved_1 = [float(row["solved_after_one_repair_pct"]) for row in source_rows]
    solved_2 = [float(row["solved_after_two_repairs_pct"]) for row in source_rows]

    x = list(range(len(labels)))
    fig, ax = plt.subplots(figsize=(max(6, 0.8 * len(labels)), 4))
    ax.plot(x, solved_0, marker="o", label="after first turn")
    ax.plot(x, solved_1, marker="o", label="after one repair")
    ax.plot(x, solved_2, marker="o", label="after two repairs")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylabel("Solved trajectories (%)")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tables-dir", type=Path, default=Path("results/tables"))
    parser.add_argument("--extra-summary", type=Path, action="append", default=[])
    parser.add_argument("--extra-trajectories", type=Path, action="append", default=[])
    parser.add_argument("--out-dir", type=Path, default=Path("results/figures"))
    args = parser.parse_args()

    try:
        import matplotlib  # noqa: F401
    except ImportError as exc:
        raise SystemExit("matplotlib is required for figures") from exc

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary_rows = read_csv(args.tables_dir / "metrics_summary.csv")
    for path in args.extra_summary:
        summary_rows.extend(read_csv(path))
    trajectory_rows = read_csv(args.tables_dir / "trajectory_metrics.csv")
    for path in args.extra_trajectories:
        trajectory_rows.extend(read_csv(path))
    write_ftga_source(summary_rows, args.out_dir / "ftga_by_condition_source.csv")
    write_repair_curve_source(trajectory_rows, args.out_dir / "repair_curve_source.csv")
    figure_ftga(summary_rows, args.out_dir / "ftga_by_condition.png")
    figure_repair_curve(trajectory_rows, args.out_dir / "repair_curve.png")
    print(f"wrote figures to {args.out_dir}")


if __name__ == "__main__":
    main()
