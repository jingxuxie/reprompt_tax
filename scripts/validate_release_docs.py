#!/usr/bin/env python
"""Validate release-facing benchmark and evaluation cards."""

from __future__ import annotations

from pathlib import Path


BENCHMARK_CARD = Path("docs/benchmark_card.md")
EVALUATION_CARD = Path("docs/evaluation_card.md")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def normalized_text(path: Path) -> str:
    require(path.exists(), f"missing release document {path}")
    return " ".join(path.read_text(encoding="utf-8").split())


def require_phrases(text: str, phrases: list[str], *, label: str) -> None:
    for phrase in phrases:
        require(phrase in text, f"{label} missing phrase: {phrase}")


def forbid_phrases(text: str, phrases: list[str], *, label: str) -> None:
    for phrase in phrases:
        require(phrase not in text, f"{label} contains stale phrase: {phrase}")


def main() -> None:
    benchmark = normalized_text(BENCHMARK_CARD)
    evaluation = normalized_text(EVALUATION_CARD)

    require_phrases(
        benchmark,
        [
            "RePromptTax-Stress-v0.2 is the paper-facing benchmark",
            "v0.3 synthetic coverage scaffold",
            "not paper-facing benchmark evidence before native validation",
            "GPT-5.x current-model refresh",
            "`gpt-5.5`: FTGA rises from 81.7% to 98.3%",
            "`gpt-5.4-mini`: FTGA rises from 80.0% to 85.0%",
            "+10.2 point aggregate FTGA effect",
            "67 contract fixes and 6 regressions",
            "Balanced 48-item stratified pilots recover the all-model and `gpt-5.5` positive directions in 100.0%",
            "data/stress_v02_sentinel24_ids.txt",
            "24-item sentinel suite covers all 12 language-family cells",
            "95.0% of GPT-5.x contract failure pairs",
            "two blinded LLM-judge audits",
            "71/72 sampled first-turn pass/fail labels",
            "70/72 sampled labels",
            "Native/near-native validation has not been completed",
            "three launch-ready annotation surfaces",
            "180 reviewer-facing rows",
            "18 roster-template slots",
            "12 static browser review sheets",
            "Do not use it to estimate prevalence",
            "scripts/run_submission_checks.py",
            "scripts/validate_release_docs.py",
        ],
        label="benchmark card",
    )
    forbid_phrases(
        benchmark,
        [
            "Corrected auto scorer and judge agree on 71/72 sampled pass/fail labels",
            "Native-speaker validation remains a required next step before strong final claims",
        ],
        label="benchmark card",
    )

    require_phrases(
        evaluation,
        [
            "The paper-facing evaluation combines the original GPT-4.1-family stress runs with a GPT-5.x current-model refresh",
            "`gpt-5.4-mini`",
            "`gpt-5.5`",
            "`content_preservation` on `gpt-4.1-nano`, `gpt-5.4-mini`, and `gpt-5.5`",
            "Token tax is not dollar cost",
            "Scorer challenge audit",
            "paper/scorer_challenge_v02.md",
            "390 known-bad probes",
            "fails 390/390 probes and detects 390/390 expected deterministic failure signals",
            "`gpt-5.5` improves from 81.7% to 98.3% FTGA",
            "20 paired first-turn fixes and zero first-turn regressions",
            "`gpt-5.4-mini` improves from 80.0% to 85.0% FTGA",
            "Content-preservation scaffolding is close to the full contract on current models",
            "85.8% vs 85.0% FTGA on `gpt-5.4-mini`",
            "99.2% vs 98.3% on `gpt-5.5`",
            "All-model robustness and pilot design",
            "paper/balanced_subsample_robustness_v02.md",
            "paper/sentinel_suite_v02.md",
            "data/stress_v02_sentinel24_ids.txt",
            "+10.2 point aggregate FTGA effect over 600 paired model-item rows",
            "prompt-cluster bootstrap interval is +5.8 to +15.0 points",
            "Balanced 48-item stratified pilots recover the all-model and `gpt-5.5` positive directions in 100.0%",
            "`gpt-5.4-mini` and `gpt-4.1-mini` remain less stable at 92.2% and 93.5%",
            "captures 19/20 GPT-5.x contract failure pairs",
            "both GPT-5.5 contract residual items",
            "repair-realism diagnostic",
            "71/72 sampled first-turn pass/fail labels",
            "70/72 labels",
            "not completed human validation",
            "180 reviewer-facing rows",
            "1,504 saved API response rows",
            "1,288 model-response rows",
            "72 repair-variant rows",
            "144 judge-audit rows",
            "285,930 tokens",
            "Run the full local submission gate with no API calls",
            "scripts/validate_release_docs.py",
        ],
        label="evaluation card",
    )
    forbid_phrases(
        evaluation,
        [
            "Paper-facing stress runs evaluate: - `gpt-4.1-nano` - `gpt-4.1-mini` - `gpt-4.1` All model outputs",
            "scripts/summarize_judge_audit.py",
            "Single-model generic-helpfulness prompt-control extension for the 60 v0.2 items",
        ],
        label="evaluation card",
    )

    print("release-doc validation passed")


if __name__ == "__main__":
    main()
