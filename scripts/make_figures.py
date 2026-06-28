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


def read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def pct(value: str) -> float:
    return 100.0 * float(value)


def figure_ftga(summary_rows: list[dict[str, Any]], out_path: Path) -> None:
    import matplotlib.pyplot as plt

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


def figure_repair_curve(trajectory_rows: list[dict[str, Any]], out_path: Path) -> None:
    import matplotlib.pyplot as plt

    groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    for row in trajectory_rows:
        groups[(row["model"], row["condition"])].append(int(row["rtt"]))

    labels = []
    solved_0 = []
    solved_1 = []
    solved_2 = []
    for key, rtts in sorted(groups.items()):
        labels.append(f"{key[0]}\n{key[1]}")
        n = len(rtts)
        solved_0.append(100.0 * sum(rtt <= 0 for rtt in rtts) / n)
        solved_1.append(100.0 * sum(rtt <= 1 for rtt in rtts) / n)
        solved_2.append(100.0 * sum(rtt <= 2 for rtt in rtts) / n)

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
    parser.add_argument("--out-dir", type=Path, default=Path("results/figures"))
    args = parser.parse_args()

    try:
        import matplotlib  # noqa: F401
    except ImportError as exc:
        raise SystemExit("matplotlib is required for figures") from exc

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary_rows = read_csv(args.tables_dir / "metrics_summary.csv")
    trajectory_rows = read_csv(args.tables_dir / "trajectory_metrics.csv")
    figure_ftga(summary_rows, args.out_dir / "ftga_by_condition.png")
    figure_repair_curve(trajectory_rows, args.out_dir / "repair_curve.png")
    print(f"wrote figures to {args.out_dir}")


if __name__ == "__main__":
    main()
