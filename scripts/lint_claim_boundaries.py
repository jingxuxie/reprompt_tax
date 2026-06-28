#!/usr/bin/env python
"""Lint RePromptTax paper artifacts for unsupported claim widening."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(".")

CLAIM_SURFACES = [
    Path("paper/main.tex"),
    Path("paper/extended_abstract_draft.md"),
    Path("paper/results_snapshot.md"),
]

PROHIBITED_PATTERNS = [
    r"\brepresentative of all\b",
    r"\bprevalence of re-prompt tax\b",
    r"\bfully solves?\b",
    r"\bgeneralizes across providers\b",
    r"\bnative-speaker validation has been completed\b",
    r"\bhuman validation is complete\b",
    r"\bfully human-validated\b",
    r"\bLLM-judge audit replaces native-speaker validation\b",
    r"\bstate-of-the-art\b",
    r"\bSOTA\b",
]

REQUIRED_PHRASES = {
    Path("paper/main.tex"): [
        "This is a pilot benchmark, not a representative sample",
        "native-speaker audit remains necessary",
        "benchmark items are synthetic",
        "not as the best possible prompt",
        "not to characterize all speakers",
    ],
    Path("paper/extended_abstract_draft.md"): [
        "This is a pilot benchmark, not a representative sample",
        "does not replace native-speaker validation",
        "do not claim that the full contract is the best prompt tested",
        "should be audited by native speakers before submission",
    ],
    Path("paper/results_snapshot.md"): [
        "Human or native-speaker audit is still needed",
        "not that the Global Interaction Contract is the best prompt tested",
        "not a representative prevalence estimate",
        "The current paper-facing result is the full",
    ],
    Path("paper/claim_evidence_checklist.md"): [
        "Safe Main Claim",
        "Claims Not Supported Yet",
        "Do not claim cross-provider generality",
        "Do not claim native-speaker validation has been completed",
    ],
    Path("paper/human_audit_completion_plan.md"): [
        "Prepared but not completed",
        "plumbing smoke test only",
        "must not be described as human validation",
    ],
    Path("docs/result_card.md"): [
        "Do not claim:",
        "that this benchmark is representative of all multilingual users",
        "that prompt mitigation fully solves the problem",
    ],
    Path("docs/benchmark_card.md"): [
        "Do not treat this benchmark as representative",
        "Do not use it as a native-speaker quality benchmark",
    ],
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def lint_prohibited_claims() -> None:
    for path in CLAIM_SURFACES:
        text = (ROOT / path).read_text(encoding="utf-8")
        for pattern in PROHIBITED_PATTERNS:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match is not None:
                raise AssertionError(f"{path} contains unsupported claim pattern {pattern!r}: {match.group(0)!r}")


def lint_required_phrases() -> None:
    for path, phrases in REQUIRED_PHRASES.items():
        full_path = ROOT / path
        require(full_path.exists(), f"missing claim-boundary file {path}")
        text = full_path.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        for phrase in phrases:
            require(phrase in normalized, f"{path} missing required claim-boundary phrase: {phrase}")


def main() -> None:
    lint_prohibited_claims()
    lint_required_phrases()
    print("claim-boundary lint passed")


if __name__ == "__main__":
    main()
