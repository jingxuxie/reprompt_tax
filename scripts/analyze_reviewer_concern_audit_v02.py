#!/usr/bin/env python
"""Map likely reviewer concerns to current RePromptTax evidence and gates."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Any


OUT_DIR = Path("results/tables/reviewer_concern_audit_v02")
OUT_MD = Path("paper/reviewer_concern_audit_v02.md")

CONCERNS: list[dict[str, Any]] = [
    {
        "concern_id": "current_model_timeliness",
        "reviewer_concern": "The original GPT-4.1-family result may be outdated.",
        "readiness": "covered",
        "paper_claim_use": "Use the full gpt-5.5 run as the current-model headline and keep gpt-5.4-mini bounded.",
        "key_answer": "Full 120-item gpt-5.5 evidence shows 81.7% to 98.3% FTGA, 20 paired fixes, zero first-turn regressions, and zero unresolved trajectories under the contract.",
        "evidence": [
            "paper/current_model_refresh_v02.md",
            "paper/current_model_uncertainty_v02.md",
            "paper/current_model_error_analysis_v02.md",
            "paper/current_model_regression_risk_v02.md",
        ],
        "validators": [
            "scripts/validate_current_model_refresh.py",
            "scripts/validate_current_model_uncertainty.py",
            "scripts/validate_current_model_error_analysis.py",
            "scripts/validate_current_model_regression_risk.py",
        ],
        "next_action": "No additional API run is needed for this claim boundary.",
    },
    {
        "concern_id": "lower_cost_model_boundary",
        "reviewer_concern": "The lower-cost current model may not support the same mitigation claim.",
        "readiness": "covered_with_boundary",
        "paper_claim_use": "Report lower normalized token tax plus directional FTGA; do not claim universal repair improvement.",
        "key_answer": "gpt-5.4-mini improves from 80.0% to 85.0% FTGA, but the interval crosses zero, unresolved rate rises, and five first-turn regressions remain.",
        "evidence": [
            "paper/current_model_uncertainty_v02.md",
            "paper/current_model_regression_risk_v02.md",
            "paper/current_model_error_analysis_v02.md",
        ],
        "validators": [
            "scripts/validate_current_model_uncertainty.py",
            "scripts/validate_current_model_regression_risk.py",
            "scripts/validate_current_model_error_analysis.py",
        ],
        "next_action": "Keep the gpt-5.4-mini language as a bounded lower-cost diagnostic.",
    },
    {
        "concern_id": "synthetic_scope",
        "reviewer_concern": "The benchmark is small and synthetic, not representative of global users.",
        "readiness": "covered_with_boundary",
        "paper_claim_use": "Use as a stress pilot and progress probe, not a prevalence or population claim.",
        "key_answer": "The benchmark card, limitations, and claim linter enforce synthetic-pilot, non-representative wording.",
        "evidence": [
            "docs/benchmark_card.md",
            "paper/sections/08_limitations_and_ethics.tex",
            "paper/claim_evidence_checklist.md",
        ],
        "validators": [
            "scripts/lint_claim_boundaries.py",
            "scripts/validate_release_docs.py",
            "scripts/validate_paper_claims.py",
        ],
        "next_action": "Do not describe the result as representative or prevalence-estimating.",
    },
    {
        "concern_id": "scorer_validity",
        "reviewer_concern": "Automatic scoring could create the headline trend.",
        "readiness": "covered_with_boundary",
        "paper_claim_use": "Use deterministic scorer audits and LLM-judge audits as scorer sanity checks, not as native validation.",
        "key_answer": "Known-bad probes fail 390/390, constrained positive controls pass 120/120, and paired judge audits agree on 71/72 and 70/72 sampled labels.",
        "evidence": [
            "paper/scorer_challenge_v02.md",
            "paper/scorer_positive_control_v02.md",
            "paper/judge_agreement_analysis_v02_full120.md",
            "paper/judge_refresh_gpt55_v02_full120.md",
        ],
        "validators": [
            "scripts/validate_scorer_challenge_v02.py",
            "scripts/validate_scorer_positive_control_v02.py",
            "scripts/validate_judge_refresh.py",
            "scripts/test_score_auto.py",
        ],
        "next_action": "Collect qualified human/native labels before widening validity claims.",
    },
    {
        "concern_id": "human_native_validation",
        "reviewer_concern": "Native/near-native validation is still missing.",
        "readiness": "external_label_blocker",
        "paper_claim_use": "Do not claim completed human/native validation.",
        "key_answer": "Reviewer packets, launch checklists, adjudication workflows, and claim gates are ready, but completed qualified labels are absent.",
        "evidence": [
            "paper/label_collection_launch_pack_v02.md",
            "paper/label_collection_dispatch_v02.md",
            "paper/completed_label_claim_gates_v02.md",
            "data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv",
        ],
        "validators": [
            "scripts/validate_label_collection_launch_pack.py",
            "scripts/validate_label_collection_dispatch.py",
            "scripts/validate_completed_label_claim_gates.py",
            "scripts/validate_completed_human_audit.py",
        ],
        "next_action": "Collect current-model labels first, then original v0.2 labels, then v0.3 coverage review if reviewer capacity allows.",
    },
    {
        "concern_id": "mechanism_vs_prompt_engineering",
        "reviewer_concern": "The result might be generic prompt engineering rather than a multilingual mechanism.",
        "readiness": "covered_with_boundary",
        "paper_claim_use": "Frame preservation scaffolding as mechanism evidence, not prompt dominance.",
        "key_answer": "Content-preservation prompts are close to or above the full contract, and contract fixes are concentrated in editing preservation.",
        "evidence": [
            "paper/prompt_family_scorecard_v02.md",
            "paper/current_prompt_mechanism_gpt54mini_v02.md",
            "paper/current_prompt_mechanism_gpt55_v02.md",
            "paper/contract_benefit_decomposition_v02.md",
        ],
        "validators": [
            "scripts/validate_prompt_family_scorecard.py",
            "scripts/validate_current_prompt_mechanism.py",
            "scripts/validate_contract_benefit_decomposition.py",
        ],
        "next_action": "Keep the full contract as the pre-specified intervention and avoid best-prompt claims.",
    },
    {
        "concern_id": "coverage_expansion_v03",
        "reviewer_concern": "The v0.2 benchmark undercovers non-English target-content editing.",
        "readiness": "diagnostic_only",
        "paper_claim_use": "Use v0.3 as launch-ready coverage scaffold and smoke evidence, not headline benchmark evidence.",
        "key_answer": "The v0.3 scaffold adds 60 rows across six coverage slices and has review sheets plus smoke/pilot diagnostics, but native review is incomplete.",
        "evidence": [
            "paper/coverage_expansion_v03.md",
            "paper/coverage_native_review_design_v03.md",
            "paper/coverage_pilot_gpt54mini_v03.md",
            "paper/coverage_smoke_gpt55_v03.md",
        ],
        "validators": [
            "scripts/validate_coverage_expansion_v03.py",
            "scripts/validate_coverage_native_review_packet_v03.py",
            "scripts/validate_coverage_pilot_v03.py",
            "scripts/validate_coverage_smoke_v03.py",
        ],
        "next_action": "Complete native review before treating v0.3 as benchmark evidence.",
    },
    {
        "concern_id": "statistical_robustness",
        "reviewer_concern": "The effect may be sensitive to sampling or repeated prompt items.",
        "readiness": "covered",
        "paper_claim_use": "Use all-five-model paired tests, clustered uncertainty, and balanced-pilot robustness as support.",
        "key_answer": "Across 600 paired model-item rows the contract has 67 fixes vs. 6 regressions; clustered bootstrap gives +5.8 to +15.0 pp.",
        "evidence": [
            "paper/all_model_paired_significance_v02.md",
            "paper/all_model_uncertainty_v02.md",
            "paper/balanced_subsample_robustness_v02.md",
            "paper/sentinel_suite_v02.md",
        ],
        "validators": [
            "scripts/validate_all_model_paired_significance.py",
            "scripts/validate_all_model_uncertainty.py",
            "scripts/validate_balanced_subsample_robustness.py",
            "scripts/validate_sentinel_suite_v02.py",
        ],
        "next_action": "Keep headline claims anchored to full 120-item runs.",
    },
    {
        "concern_id": "token_cost_interpretation",
        "reviewer_concern": "Token tax might be confused with absolute API-cost savings.",
        "readiness": "covered_with_boundary",
        "paper_claim_use": "Report token tax as normalized repair burden, not dollar cost.",
        "key_answer": "The contract lowers normalized token tax for all five full-run models but increases absolute total tokens for every contract row.",
        "evidence": [
            "paper/token_burden_analysis_v02_full120.md",
            "paper/efficiency_tradeoff_v02.md",
            "docs/evaluation_card.md",
        ],
        "validators": [
            "scripts/validate_efficiency_tradeoff.py",
            "scripts/validate_release_docs.py",
            "scripts/validate_paper_claims.py",
        ],
        "next_action": "Keep cost language focused on repair burden and absolute-token caveats.",
    },
    {
        "concern_id": "real_world_motivation_privacy",
        "reviewer_concern": "The real-world motivation scan might imply unsupported prevalence or expose private text.",
        "readiness": "covered_with_boundary",
        "paper_claim_use": "Use WildChat only as aggregate taxonomy motivation.",
        "key_answer": "The scan writes hashed metadata only, reports no raw text, and the taxonomy audit maps all six cue categories to benchmark/scorer/metric surfaces.",
        "evidence": [
            "paper/discovery_cue_analysis.md",
            "paper/taxonomy_traceability_v02.md",
            "results/discovery/wildchat_20k_repair_cues/summary.json",
        ],
        "validators": [
            "scripts/validate_taxonomy_traceability_v02.py",
            "scripts/validate_paper_claims.py",
        ],
        "next_action": "Do not report WildChat cue hits as prevalence estimates.",
    },
]

CSV_FIELDS = [
    "concern_id",
    "reviewer_concern",
    "readiness",
    "paper_claim_use",
    "key_answer",
    "evidence",
    "validators",
    "next_action",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def ensure_paths(paths: list[str], *, concern_id: str, role: str) -> None:
    for path_text in paths:
        path = Path(path_text)
        require(path.exists(), f"{concern_id} missing {role} path: {path}")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, f"refusing to write empty reviewer-concern table {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_summary_csv(path: Path, rows: list[dict[str, str]]) -> None:
    counts = Counter(row["readiness"] for row in rows)
    out = [
        {"readiness": readiness, "concern_count": counts[readiness]}
        for readiness in sorted(counts)
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["readiness", "concern_count"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(out)


def build_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for concern in CONCERNS:
        concern_id = concern["concern_id"]
        require(concern_id not in seen, f"duplicate concern_id {concern_id}")
        seen.add(concern_id)
        ensure_paths(concern["evidence"], concern_id=concern_id, role="evidence")
        ensure_paths(concern["validators"], concern_id=concern_id, role="validator")
        rows.append(
            {
                "concern_id": concern_id,
                "reviewer_concern": concern["reviewer_concern"],
                "readiness": concern["readiness"],
                "paper_claim_use": concern["paper_claim_use"],
                "key_answer": concern["key_answer"],
                "evidence": "; ".join(concern["evidence"]),
                "validators": "; ".join(concern["validators"]),
                "next_action": concern["next_action"],
            }
        )
    return rows


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    counts = Counter(row["readiness"] for row in rows)
    lines = [
        "# Reviewer Concern Audit",
        "",
        "This no-API audit maps likely reviewer concerns to current evidence,",
        "claim boundaries, and validators. It is not a new experiment and does",
        "not replace completed human/native validation.",
        "",
        "## Summary",
        "",
        f"- Reviewer concerns audited: {len(rows)}",
        f"- Covered concerns: {counts['covered']}",
        f"- Covered with explicit boundary: {counts['covered_with_boundary']}",
        f"- Diagnostic-only concerns: {counts['diagnostic_only']}",
        f"- External label blockers: {counts['external_label_blocker']}",
        "- OpenAI API calls: 0",
        "- Claim boundary: native/near-native validation is launch-ready but not completed.",
        "",
        "## Concern Matrix",
        "",
        "| Concern | Readiness | Paper claim use | Key answer | Next action |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['concern_id']}` | {row['readiness']} | {row['paper_claim_use']} | "
            f"{row['key_answer']} | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Evidence Index",
            "",
            "| Concern | Evidence | Validators |",
            "|---|---|---|",
        ]
    )
    for row in rows:
        evidence = "<br>".join(f"`{item}`" for item in row["evidence"].split("; "))
        validators = "<br>".join(f"`{item}`" for item in row["validators"].split("; "))
        lines.append(f"| `{row['concern_id']}` | {evidence} | {validators} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The current package is strongest on current-model timeliness, scorer",
            "plumbing, mechanism diagnostics, robustness checks, and release hygiene.",
            "The main unresolved reviewer concern is external: completed qualified",
            "human/native labels are still missing. Until those labels pass the",
            "completed-label gates, the paper should keep native-validation claims",
            "as launch-ready protocol evidence only.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    rows = build_rows()
    write_csv(args.out_dir / "reviewer_concern_audit.csv", rows)
    write_summary_csv(args.out_dir / "reviewer_concern_summary.csv", rows)
    write_markdown(args.out_md, rows)
    print(f"wrote reviewer concern audit to {args.out_dir} and {args.out_md}")


if __name__ == "__main__":
    main()
