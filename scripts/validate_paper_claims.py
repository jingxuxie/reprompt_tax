#!/usr/bin/env python
"""Validate paper-facing claims against saved RePromptTax artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


EXPECTED_STRESS_COUNTS = {
    ("es-en", "editing_preservation"): 10,
    ("es-en", "output_language_inference"): 10,
    ("es-en", "quote_preservation"): 10,
    ("es-en", "script_register_locale"): 10,
    ("hi-en", "editing_preservation"): 10,
    ("hi-en", "output_language_inference"): 10,
    ("hi-en", "quote_preservation"): 10,
    ("hi-en", "script_register_locale"): 10,
    ("ar-en", "editing_preservation"): 10,
    ("ar-en", "output_language_inference"): 10,
    ("ar-en", "quote_preservation"): 10,
    ("ar-en", "script_register_locale"): 10,
}

EXPECTED_BENCHMARK_QUALITY_SUMMARY = {
    "benchmark_rows": 120,
    "language_pairs": 3,
    "task_families": 4,
    "stress_tags": 4,
    "unique_user_prompts": 120,
    "normalized_duplicate_prompts": 0,
    "rows_with_required_markers": 120,
    "rows_with_known_bad_outputs": 120,
    "rows_with_forbidden_markers": 60,
    "rows_with_preservation_spans": 60,
    "total_preservation_spans": 99,
    "total_forbidden_markers": 300,
    "privacy_marker_hits": 0,
    "min_prompt_words": 13,
    "mean_prompt_words": 22.4,
    "max_prompt_words": 35,
}

EXPECTED_BENCHMARK_QUALITY_BY_FAMILY = {
    "editing_preservation": {
        "n": 30,
        "rows_with_required_markers": 30,
        "rows_with_known_bad_outputs": 30,
        "rows_with_forbidden_markers": 30,
        "rows_with_preservation_spans": 0,
        "total_preservation_spans": 0,
    },
    "output_language_inference": {
        "n": 30,
        "rows_with_required_markers": 30,
        "rows_with_known_bad_outputs": 30,
        "rows_with_forbidden_markers": 0,
        "rows_with_preservation_spans": 0,
        "total_preservation_spans": 0,
    },
    "quote_preservation": {
        "n": 30,
        "rows_with_required_markers": 30,
        "rows_with_known_bad_outputs": 30,
        "rows_with_forbidden_markers": 0,
        "rows_with_preservation_spans": 30,
        "total_preservation_spans": 60,
    },
    "script_register_locale": {
        "n": 30,
        "rows_with_required_markers": 30,
        "rows_with_known_bad_outputs": 30,
        "rows_with_forbidden_markers": 30,
        "rows_with_preservation_spans": 30,
        "total_preservation_spans": 39,
    },
}

EXPECTED_EXPERIMENT_LEDGER_SUMMARY = {
    "tracked_api_artifacts": 8,
    "api_response_rows": 1504,
    "model_response_rows": 1288,
    "repair_variant_response_rows": 72,
    "judge_response_rows": 144,
    "trajectories_or_judged_rows": 1236,
    "input_tokens": 229646,
    "output_tokens": 56284,
    "total_tokens": 285930,
}

EXPECTED_EXPERIMENT_LEDGER_BY_ARTIFACT = {
    "main_evaluation": {
        "artifact_kind": "model_responses",
        "api_response_rows": 917,
        "first_turn_rows": 720,
        "trajectories": 720,
        "input_tokens": 126306,
        "output_tokens": 25737,
        "total_tokens": 152043,
    },
    "prompt_control": {
        "artifact_kind": "model_responses",
        "api_response_rows": 155,
        "first_turn_rows": 120,
        "trajectories": 120,
        "input_tokens": 23494,
        "output_tokens": 3968,
        "total_tokens": 27462,
    },
    "prompt_ablation_content_preservation": {
        "artifact_kind": "model_responses",
        "api_response_rows": 146,
        "first_turn_rows": 120,
        "trajectories": 120,
        "input_tokens": 20056,
        "output_tokens": 3324,
        "total_tokens": 23380,
    },
    "coverage_pilot_v03_gpt54mini": {
        "artifact_kind": "model_responses",
        "api_response_rows": 58,
        "first_turn_rows": 48,
        "trajectories": 48,
        "input_tokens": 8007,
        "output_tokens": 1958,
        "total_tokens": 9965,
    },
    "coverage_smoke_v03_gpt55": {
        "artifact_kind": "model_responses",
        "api_response_rows": 12,
        "first_turn_rows": 12,
        "trajectories": 12,
        "input_tokens": 1632,
        "output_tokens": 870,
        "total_tokens": 2502,
    },
    "judge_audit": {
        "artifact_kind": "judge_audit",
        "api_response_rows": 72,
        "first_turn_rows": 72,
        "trajectories": 72,
        "input_tokens": 20607,
        "output_tokens": 5339,
        "total_tokens": 25946,
    },
    "judge_refresh_gpt55": {
        "artifact_kind": "judge_audit",
        "api_response_rows": 72,
        "first_turn_rows": 72,
        "trajectories": 72,
        "input_tokens": 20535,
        "output_tokens": 10512,
        "total_tokens": 31047,
    },
    "repair_realism_editing_baseline24": {
        "artifact_kind": "repair_variant_responses",
        "api_response_rows": 72,
        "first_turn_rows": 0,
        "trajectories": 72,
        "input_tokens": 9009,
        "output_tokens": 4576,
        "total_tokens": 13585,
    },
}

EXPECTED_EXPERIMENT_LEDGER_BY_MODEL = {
    ("main_evaluation", "gpt-4.1", "baseline"): {"api_response_rows": 151, "first_turn_rows": 120, "trajectories": 120, "total_tokens": 15924},
    ("main_evaluation", "gpt-4.1", "contract"): {"api_response_rows": 134, "first_turn_rows": 120, "trajectories": 120, "total_tokens": 31035},
    ("main_evaluation", "gpt-4.1-mini", "baseline"): {"api_response_rows": 154, "first_turn_rows": 120, "trajectories": 120, "total_tokens": 14769},
    ("main_evaluation", "gpt-4.1-mini", "contract"): {"api_response_rows": 150, "first_turn_rows": 120, "trajectories": 120, "total_tokens": 36037},
    ("main_evaluation", "gpt-4.1-nano", "baseline"): {"api_response_rows": 173, "first_turn_rows": 120, "trajectories": 120, "total_tokens": 17075},
    ("main_evaluation", "gpt-4.1-nano", "contract"): {"api_response_rows": 155, "first_turn_rows": 120, "trajectories": 120, "total_tokens": 37203},
    ("prompt_control", "gpt-4.1-nano", "generic_helpfulness"): {"api_response_rows": 155, "first_turn_rows": 120, "trajectories": 120, "total_tokens": 27462},
    ("prompt_ablation_content_preservation", "gpt-4.1-nano", "content_preservation"): {"api_response_rows": 146, "first_turn_rows": 120, "trajectories": 120, "total_tokens": 23380},
    ("coverage_pilot_v03_gpt54mini", "gpt-5.4-mini", "baseline"): {"api_response_rows": 32, "first_turn_rows": 24, "trajectories": 24, "total_tokens": 3713},
    ("coverage_pilot_v03_gpt54mini", "gpt-5.4-mini", "contract"): {"api_response_rows": 26, "first_turn_rows": 24, "trajectories": 24, "total_tokens": 6252},
    ("coverage_smoke_v03_gpt55", "gpt-5.5", "baseline"): {"api_response_rows": 6, "first_turn_rows": 6, "trajectories": 6, "total_tokens": 825},
    ("coverage_smoke_v03_gpt55", "gpt-5.5", "contract"): {"api_response_rows": 6, "first_turn_rows": 6, "trajectories": 6, "total_tokens": 1677},
}

EXPECTED_COMPONENT_MODEL_ROWS = {
    ("gpt-4.1", "baseline"): {"ftga_pass_pct": 76.7, "language_pass_pct": 83.3, "script_pass_pct": 91.7, "preservation_pass_pct": 93.3, "task_pass_pct": 90.8, "register_locale_pass_pct": 100.0},
    ("gpt-4.1", "contract"): {"ftga_pass_pct": 93.3, "language_pass_pct": 99.2, "script_pass_pct": 100.0, "preservation_pass_pct": 94.2, "task_pass_pct": 98.3, "register_locale_pass_pct": 100.0},
    ("gpt-4.1-mini", "baseline"): {"ftga_pass_pct": 75.8, "language_pass_pct": 83.3, "script_pass_pct": 91.7, "preservation_pass_pct": 92.5, "task_pass_pct": 81.7, "register_locale_pass_pct": 100.0},
    ("gpt-4.1-mini", "contract"): {"ftga_pass_pct": 79.2, "language_pass_pct": 86.7, "script_pass_pct": 95.0, "preservation_pass_pct": 92.5, "task_pass_pct": 85.0, "register_locale_pass_pct": 100.0},
    ("gpt-4.1-nano", "baseline"): {"ftga_pass_pct": 67.5, "language_pass_pct": 82.5, "script_pass_pct": 91.7, "preservation_pass_pct": 85.0, "task_pass_pct": 73.3, "register_locale_pass_pct": 100.0},
    ("gpt-4.1-nano", "contract"): {"ftga_pass_pct": 76.7, "language_pass_pct": 90.8, "script_pass_pct": 99.2, "preservation_pass_pct": 85.8, "task_pass_pct": 82.5, "register_locale_pass_pct": 100.0},
}

EXPECTED_COMPONENT_FAMILY_ROWS = {
    ("baseline", "editing_preservation"): {"language_pass_pct": 33.3, "script_pass_pct": 66.7, "preservation_pass_pct": 100.0, "task_pass_pct": 44.4},
    ("contract", "editing_preservation"): {"language_pass_pct": 70.0, "script_pass_pct": 92.2, "preservation_pass_pct": 100.0, "task_pass_pct": 70.0},
    ("baseline", "script_register_locale"): {"language_pass_pct": 98.9, "script_pass_pct": 100.0, "preservation_pass_pct": 71.1, "task_pass_pct": 93.3},
    ("contract", "script_register_locale"): {"language_pass_pct": 98.9, "script_pass_pct": 100.0, "preservation_pass_pct": 72.2, "task_pass_pct": 93.3},
}

EXPECTED_COMPONENT_PAIRED_ROWS = {
    ("gpt-4.1", "language_pass"): {"delta_pp": 15.8, "improved_n": 19, "worsened_n": 0, "tied_n": 101},
    ("gpt-4.1", "script_pass"): {"delta_pp": 8.3, "improved_n": 10, "worsened_n": 0, "tied_n": 110},
    ("gpt-4.1-mini", "preservation_pass"): {"delta_pp": 0.0, "improved_n": 0, "worsened_n": 0, "tied_n": 120},
    ("gpt-4.1-nano", "language_pass"): {"delta_pp": 8.3, "improved_n": 11, "worsened_n": 1, "tied_n": 108},
    ("gpt-4.1-nano", "task_pass"): {"delta_pp": 9.2, "improved_n": 11, "worsened_n": 0, "tied_n": 109},
}

EXPECTED_SCORER_ABLATION_BY_CONDITION = {
    "baseline": {
        "n": 360,
        "actual_ftga_pct": 73.3,
        "actual_fail_n": 96,
        "relax_language_delta_pp": 3.1,
        "sole_language_blocker_n": 11,
        "relax_preservation_delta_pp": 5.6,
        "sole_preservation_blocker_n": 20,
        "relax_task_delta_pp": 0.0,
    },
    "contract": {
        "n": 360,
        "actual_ftga_pct": 83.1,
        "actual_fail_n": 61,
        "relax_language_delta_pp": 0.2,
        "sole_language_blocker_n": 1,
        "relax_preservation_delta_pp": 5.2,
        "sole_preservation_blocker_n": 19,
        "relax_task_delta_pp": 0.0,
    },
}

EXPECTED_SCORER_ABLATION_FAMILY_ROWS = {
    ("baseline", "editing_preservation"): {"actual_ftga_pct": 33.3, "relax_language_delta_pp": 11.1, "relax_preservation_delta_pp": 0.0, "sole_language_blocker_n": 10},
    ("baseline", "script_register_locale"): {"actual_ftga_pct": 70.0, "relax_language_delta_pp": 1.1, "relax_preservation_delta_pp": 22.2, "sole_preservation_blocker_n": 20},
    ("contract", "editing_preservation"): {"actual_ftga_pct": 70.0, "relax_language_delta_pp": 0.0, "relax_preservation_delta_pp": 0.0, "sole_language_blocker_n": 0},
    ("contract", "script_register_locale"): {"actual_ftga_pct": 71.1, "relax_language_delta_pp": 1.1, "relax_preservation_delta_pp": 21.1, "sole_preservation_blocker_n": 19},
}

EXPECTED_SCORER_ABLATION_SIGNATURES = {
    ("baseline", "editing_preservation", "language+script+task"): {"count": 30, "share_of_first_turn_failures": 0.5},
    ("baseline", "script_register_locale", "preservation"): {"count": 20, "share_of_first_turn_failures": 0.741},
    ("contract", "editing_preservation", "language+task"): {"count": 20, "share_of_first_turn_failures": 0.741},
    ("contract", "script_register_locale", "preservation"): {"count": 19, "share_of_first_turn_failures": 0.731},
}

EXPECTED_TASK_USEFUL_BY_CONDITION = {
    "baseline": {
        "first_turn_failure_n": 96,
        "task_useful_contract_failure_n": 31,
        "task_useful_share_of_failures_pct": 32.3,
        "task_and_preservation_useful_failure_n": 11,
        "language_or_script_framing_failure_n": 11,
        "task_noncompletion_failure_n": 65,
    },
    "contract": {
        "first_turn_failure_n": 61,
        "task_useful_contract_failure_n": 20,
        "task_useful_share_of_failures_pct": 32.8,
        "task_and_preservation_useful_failure_n": 1,
        "language_or_script_framing_failure_n": 1,
        "task_noncompletion_failure_n": 41,
    },
}

EXPECTED_TASK_USEFUL_FAMILY_ROWS = {
    ("baseline", "editing_preservation"): {
        "first_turn_failure_n": 60,
        "task_useful_contract_failure_n": 10,
        "task_and_preservation_useful_failure_n": 10,
        "task_noncompletion_failure_n": 50,
    },
    ("baseline", "script_register_locale"): {
        "first_turn_failure_n": 27,
        "task_useful_contract_failure_n": 21,
        "task_and_preservation_useful_failure_n": 1,
        "task_noncompletion_failure_n": 6,
    },
    ("contract", "editing_preservation"): {
        "first_turn_failure_n": 27,
        "task_useful_contract_failure_n": 0,
        "task_and_preservation_useful_failure_n": 0,
        "task_noncompletion_failure_n": 27,
    },
    ("contract", "script_register_locale"): {
        "first_turn_failure_n": 26,
        "task_useful_contract_failure_n": 20,
        "task_and_preservation_useful_failure_n": 1,
        "task_noncompletion_failure_n": 6,
    },
}

EXPECTED_TASK_USEFUL_SIGNATURES = {
    ("baseline", "editing_preservation", "language"): 10,
    ("baseline", "script_register_locale", "language"): 1,
    ("baseline", "script_register_locale", "preservation"): 20,
    ("contract", "script_register_locale", "language"): 1,
    ("contract", "script_register_locale", "preservation"): 19,
}

EXPECTED_LANGUAGE_SLICE_METRICS = {
    ("gpt-4.1-nano", "baseline", "ar-en"): {"ftga_pct": 37.5, "mean_rtt": 0.975, "mean_token_tax": 2.432, "unresolved_pct": 15.0, "initially_failed_n": 25},
    ("gpt-4.1-nano", "contract", "ar-en"): {"ftga_pct": 62.5, "mean_rtt": 0.550, "mean_token_tax": 1.573, "unresolved_pct": 7.5, "initially_failed_n": 15},
    ("gpt-4.1", "baseline", "hi-en"): {"ftga_pct": 97.5, "mean_rtt": 0.075, "mean_token_tax": 1.087, "unresolved_pct": 2.5, "initially_failed_n": 1},
    ("gpt-4.1", "contract", "hi-en"): {"ftga_pct": 97.5, "mean_rtt": 0.075, "mean_token_tax": 1.063, "unresolved_pct": 2.5, "initially_failed_n": 1},
    ("gpt-4.1-mini", "baseline", "es-en"): {"ftga_pct": 67.5, "mean_rtt": 0.375, "mean_token_tax": 1.574, "unresolved_pct": 2.5, "initially_failed_n": 13},
    ("gpt-4.1-mini", "contract", "es-en"): {"ftga_pct": 67.5, "mean_rtt": 0.375, "mean_token_tax": 1.421, "unresolved_pct": 2.5, "initially_failed_n": 13},
}

EXPECTED_LANGUAGE_SLICE_EFFECTS = {
    ("gpt-4.1", "ar-en"): {"delta_ftga_pp": 25.0, "rtt_reduction": 0.150, "token_tax_reduction": 0.404, "unresolved_reduction_pp": -5.0, "ftga_improved_n": 10, "ftga_worsened_n": 0, "ftga_tied_n": 30, "ftga_sign_test_p": 0.0020},
    ("gpt-4.1", "es-en"): {"delta_ftga_pp": 25.0, "rtt_reduction": 0.250, "token_tax_reduction": 0.473, "unresolved_reduction_pp": 0.0, "ftga_improved_n": 10, "ftga_worsened_n": 0, "ftga_tied_n": 30, "ftga_sign_test_p": 0.0020},
    ("gpt-4.1-nano", "ar-en"): {"delta_ftga_pp": 25.0, "rtt_reduction": 0.425, "token_tax_reduction": 0.859, "unresolved_reduction_pp": 7.5, "ftga_improved_n": 10, "ftga_worsened_n": 0, "ftga_tied_n": 30, "ftga_sign_test_p": 0.0020},
    ("gpt-4.1-mini", "es-en"): {"delta_ftga_pp": 0.0, "rtt_reduction": 0.000, "token_tax_reduction": 0.152, "unresolved_reduction_pp": 0.0, "ftga_improved_n": 0, "ftga_worsened_n": 0, "ftga_tied_n": 40, "ftga_sign_test_p": 1.0000},
    ("gpt-4.1-nano", "hi-en"): {"delta_ftga_pp": 0.0, "rtt_reduction": 0.000, "token_tax_reduction": 0.024, "unresolved_reduction_pp": 0.0, "ftga_improved_n": 1, "ftga_worsened_n": 1, "ftga_tied_n": 38, "ftga_sign_test_p": 1.0000},
}

EXPECTED_LANGUAGE_SLICE_AGGREGATE = {
    "ar-en": {"mean_delta_ftga_pp": 20.0, "mean_rtt_reduction": 0.217, "mean_token_tax_reduction": 0.511, "total_ftga_improved_n": 24, "total_ftga_worsened_n": 0, "total_ftga_tied_n": 96},
    "es-en": {"mean_delta_ftga_pp": 9.2, "mean_rtt_reduction": 0.083, "mean_token_tax_reduction": 0.265, "total_ftga_improved_n": 11, "total_ftga_worsened_n": 0, "total_ftga_tied_n": 109},
    "hi-en": {"mean_delta_ftga_pp": 0.0, "mean_rtt_reduction": 0.008, "mean_token_tax_reduction": 0.035, "total_ftga_improved_n": 1, "total_ftga_worsened_n": 1, "total_ftga_tied_n": 118},
}

EXPECTED_REPAIR_DYNAMICS_MODEL_ROWS = {
    ("gpt-4.1", "baseline"): {"mean_rtt": 0.283, "initial_failures_n": 28, "first_turn_pass_n": 92, "repaired_after_one_n": 25, "repaired_after_two_n": 0, "unresolved_after_two_n": 3},
    ("gpt-4.1", "contract"): {"mean_rtt": 0.150, "initial_failures_n": 8, "first_turn_pass_n": 112, "repaired_after_one_n": 3, "repaired_after_two_n": 0, "unresolved_after_two_n": 5},
    ("gpt-4.1-mini", "baseline"): {"mean_rtt": 0.275, "initial_failures_n": 29, "first_turn_pass_n": 91, "repaired_after_one_n": 26, "repaired_after_two_n": 2, "unresolved_after_two_n": 1},
    ("gpt-4.1-mini", "contract"): {"mean_rtt": 0.242, "initial_failures_n": 25, "first_turn_pass_n": 95, "repaired_after_one_n": 23, "repaired_after_two_n": 0, "unresolved_after_two_n": 2},
    ("gpt-4.1-nano", "baseline"): {"mean_rtt": 0.467, "initial_failures_n": 39, "first_turn_pass_n": 81, "repaired_after_one_n": 29, "repaired_after_two_n": 3, "unresolved_after_two_n": 7},
    ("gpt-4.1-nano", "contract"): {"mean_rtt": 0.325, "initial_failures_n": 28, "first_turn_pass_n": 92, "repaired_after_one_n": 22, "repaired_after_two_n": 1, "unresolved_after_two_n": 5},
}

EXPECTED_REPAIR_DYNAMICS_FAMILY_ROWS = {
    ("baseline", "editing_preservation"): {"first_turn_pass_n": 30, "repaired_after_one_n": 60, "repaired_after_two_n": 0, "unresolved_after_two_n": 0, "mean_rtt": 0.667},
    ("contract", "editing_preservation"): {"first_turn_pass_n": 63, "repaired_after_one_n": 27, "repaired_after_two_n": 0, "unresolved_after_two_n": 0, "mean_rtt": 0.300},
    ("baseline", "script_register_locale"): {"first_turn_pass_n": 63, "repaired_after_one_n": 17, "repaired_after_two_n": 3, "unresolved_after_two_n": 7, "mean_rtt": 0.489},
    ("contract", "script_register_locale"): {"first_turn_pass_n": 64, "repaired_after_one_n": 15, "repaired_after_two_n": 0, "unresolved_after_two_n": 11, "mean_rtt": 0.533},
}

EXPECTED_REPAIR_PAIRED_EFFECTS = {
    "gpt-4.1": {"mean_rtt_reduction": 0.133, "improved_n": 20, "worsened_n": 2, "tied_n": 98, "baseline_fail_contract_pass_n": 20, "baseline_pass_contract_fail_n": 0, "baseline_unresolved_contract_resolved_n": 0, "baseline_resolved_contract_unresolved_n": 2},
    "gpt-4.1-mini": {"mean_rtt_reduction": 0.033, "improved_n": 5, "worsened_n": 1, "tied_n": 114, "baseline_fail_contract_pass_n": 4, "baseline_pass_contract_fail_n": 0, "baseline_unresolved_contract_resolved_n": 0, "baseline_resolved_contract_unresolved_n": 1},
    "gpt-4.1-nano": {"mean_rtt_reduction": 0.142, "improved_n": 17, "worsened_n": 3, "tied_n": 100, "baseline_fail_contract_pass_n": 12, "baseline_pass_contract_fail_n": 1, "baseline_unresolved_contract_resolved_n": 4, "baseline_resolved_contract_unresolved_n": 2},
}

EXPECTED_REPAIR_TRANSITIONS = {
    ("gpt-4.1", 1, 0): 20,
    ("gpt-4.1", 1, 3): 2,
    ("gpt-4.1", 3, 3): 3,
    ("gpt-4.1-mini", 1, 0): 4,
    ("gpt-4.1-mini", 2, 3): 1,
    ("gpt-4.1-nano", 1, 0): 12,
    ("gpt-4.1-nano", 2, 3): 2,
    ("gpt-4.1-nano", 3, 1): 3,
    ("gpt-4.1-nano", 3, 2): 1,
}

EXPECTED_JUDGE_AGREEMENT_SUMMARY = {
    "n": 72,
    "pass_fail_agreement_n": 71,
    "pass_fail_agreement_pct": 98.6,
    "pass_fail_agreement_ci_low": 92.5,
    "pass_fail_agreement_ci_high": 99.8,
    "auto_pass_n": 64,
    "auto_pass_pct": 88.9,
    "judge_pass_n": 65,
    "judge_pass_pct": 90.3,
    "auto_fail_judge_pass_n": 1,
    "auto_pass_judge_fail_n": 0,
    "judge_parse_error_n": 0,
}

EXPECTED_JUDGE_AGREEMENT_BY_FAMILY = {
    "editing_preservation": {"n": 18, "pass_fail_agreement_n": 17, "pass_fail_agreement_pct": 94.4, "auto_pass_n": 13, "judge_pass_n": 14},
    "output_language_inference": {"n": 18, "pass_fail_agreement_n": 18, "pass_fail_agreement_pct": 100.0, "auto_pass_n": 18, "judge_pass_n": 18},
    "quote_preservation": {"n": 18, "pass_fail_agreement_n": 18, "pass_fail_agreement_pct": 100.0, "auto_pass_n": 17, "judge_pass_n": 17},
    "script_register_locale": {"n": 18, "pass_fail_agreement_n": 18, "pass_fail_agreement_pct": 100.0, "auto_pass_n": 16, "judge_pass_n": 16},
}

EXPECTED_JUDGE_COMPONENT_AGREEMENT = {
    "language": {"agreement_n": 71, "agreement_pct": 98.6, "agreement_ci_low": 92.5, "agreement_ci_high": 99.8, "auto_pass_n": 67, "judge_pass_n": 68, "auto_fail_judge_pass_n": 1, "auto_pass_judge_fail_n": 0, "mismatch_n": 1},
    "script": {"agreement_n": 71, "agreement_pct": 98.6, "agreement_ci_low": 92.5, "agreement_ci_high": 99.8, "auto_pass_n": 70, "judge_pass_n": 69, "auto_fail_judge_pass_n": 0, "auto_pass_judge_fail_n": 1, "mismatch_n": 1},
    "preservation": {"agreement_n": 69, "agreement_pct": 95.8, "agreement_ci_low": 88.5, "agreement_ci_high": 98.6, "auto_pass_n": 69, "judge_pass_n": 66, "auto_fail_judge_pass_n": 0, "auto_pass_judge_fail_n": 3, "mismatch_n": 3},
    "task": {"agreement_n": 71, "agreement_pct": 98.6, "agreement_ci_low": 92.5, "agreement_ci_high": 99.8, "auto_pass_n": 68, "judge_pass_n": 67, "auto_fail_judge_pass_n": 0, "auto_pass_judge_fail_n": 1, "mismatch_n": 1},
    "register_locale": {"agreement_n": 68, "agreement_pct": 94.4, "agreement_ci_low": 86.6, "agreement_ci_high": 97.8, "auto_pass_n": 72, "judge_pass_n": 68, "auto_fail_judge_pass_n": 0, "auto_pass_judge_fail_n": 4, "mismatch_n": 4},
}

EXPECTED_MAIN = {
    ("gpt-4.1-nano", "baseline"): {"ftga": 67.5, "mean_rtt": 0.47, "mean_token_tax": 1.69, "unresolved_rate": 5.8, "repair_success_at_1": 74.4, "repair_success_at_2": 82.1},
    ("gpt-4.1-nano", "contract"): {"ftga": 76.7, "mean_rtt": 0.33, "mean_token_tax": 1.34, "unresolved_rate": 4.2, "repair_success_at_1": 78.6, "repair_success_at_2": 82.1},
    ("gpt-4.1-mini", "baseline"): {"ftga": 75.8, "mean_rtt": 0.28, "mean_token_tax": 1.43, "unresolved_rate": 0.8, "repair_success_at_1": 89.7, "repair_success_at_2": 96.6},
    ("gpt-4.1-mini", "contract"): {"ftga": 79.2, "mean_rtt": 0.24, "mean_token_tax": 1.27, "unresolved_rate": 1.7, "repair_success_at_1": 92.0, "repair_success_at_2": 92.0},
    ("gpt-4.1", "baseline"): {"ftga": 76.7, "mean_rtt": 0.28, "mean_token_tax": 1.43, "unresolved_rate": 2.5, "repair_success_at_1": 89.3, "repair_success_at_2": 89.3},
    ("gpt-4.1", "contract"): {"ftga": 93.3, "mean_rtt": 0.15, "mean_token_tax": 1.13, "unresolved_rate": 4.2, "repair_success_at_1": 37.5, "repair_success_at_2": 37.5},
}

EXPECTED_PAIRED_EFFECTS = {
    "gpt-4.1-nano": {
        "delta_ftga_pp": 9.2,
        "delta_ftga_pp_ci_low": 4.2,
        "delta_ftga_pp_ci_high": 15.0,
        "rtt_reduction": 0.14,
        "rtt_reduction_ci_low": 0.07,
        "rtt_reduction_ci_high": 0.23,
        "token_tax_reduction": 0.35,
        "token_tax_reduction_ci_low": 0.23,
        "token_tax_reduction_ci_high": 0.48,
    },
    "gpt-4.1-mini": {
        "delta_ftga_pp": 3.3,
        "delta_ftga_pp_ci_low": 0.8,
        "delta_ftga_pp_ci_high": 6.7,
        "rtt_reduction": 0.03,
        "rtt_reduction_ci_low": 0.00,
        "rtt_reduction_ci_high": 0.07,
        "token_tax_reduction": 0.16,
        "token_tax_reduction_ci_low": 0.10,
        "token_tax_reduction_ci_high": 0.23,
    },
    "gpt-4.1": {
        "delta_ftga_pp": 16.7,
        "delta_ftga_pp_ci_low": 10.0,
        "delta_ftga_pp_ci_high": 23.3,
        "rtt_reduction": 0.13,
        "rtt_reduction_ci_low": 0.05,
        "rtt_reduction_ci_high": 0.22,
        "token_tax_reduction": 0.30,
        "token_tax_reduction_ci_low": 0.19,
        "token_tax_reduction_ci_high": 0.43,
    },
}

EXPECTED_FAMILY_EFFECTS = {
    ("gpt-4.1", "editing_preservation"): {
        "baseline_ftga_pct": 33.3,
        "contract_ftga_pct": 96.7,
        "delta_ftga_pp": 63.3,
        "baseline_initial_failures": 20,
        "contract_initial_failures": 1,
    },
    ("gpt-4.1-mini", "editing_preservation"): {
        "baseline_ftga_pct": 33.3,
        "contract_ftga_pct": 46.7,
        "delta_ftga_pp": 13.3,
        "baseline_initial_failures": 20,
        "contract_initial_failures": 16,
    },
    ("gpt-4.1-nano", "editing_preservation"): {
        "baseline_ftga_pct": 33.3,
        "contract_ftga_pct": 66.7,
        "delta_ftga_pp": 33.3,
        "baseline_initial_failures": 20,
        "contract_initial_failures": 10,
    },
    ("gpt-4.1-nano", "quote_preservation"): {
        "baseline_ftga_pct": 70.0,
        "contract_ftga_pct": 73.3,
        "baseline_mean_rtt": 0.63,
        "contract_mean_rtt": 0.37,
        "baseline_unresolved_pct": 13.3,
        "contract_unresolved_pct": 3.3,
    },
}

EXPECTED_ITEM_CONSISTENCY_SUMMARY = {
    "items": 120,
    "baseline_all_models_pass": 80,
    "baseline_any_model_fail": 40,
    "baseline_all_models_fail": 27,
    "contract_all_models_pass": 85,
    "contract_any_model_fail": 35,
    "contract_all_models_fail": 8,
    "fewer_fail_models_under_contract": 22,
    "more_fail_models_under_contract": 1,
    "same_fail_models_under_contract": 97,
    "lower_mean_rtt_under_contract": 28,
    "higher_mean_rtt_under_contract": 6,
    "same_mean_rtt_under_contract": 86,
    "baseline_any_unresolved": 8,
    "contract_any_unresolved": 6,
}

EXPECTED_ITEM_CONSISTENCY_BY_FAMILY = {
    "editing_preservation": {
        "items": 30,
        "baseline_any_model_fail": 20,
        "contract_any_model_fail": 16,
        "baseline_all_models_fail": 20,
        "contract_all_models_fail": 1,
        "fewer_fail_models_under_contract": 19,
        "more_fail_models_under_contract": 0,
    },
    "output_language_inference": {
        "items": 30,
        "baseline_any_model_fail": 0,
        "contract_any_model_fail": 0,
        "baseline_all_models_fail": 0,
        "contract_all_models_fail": 0,
        "fewer_fail_models_under_contract": 0,
        "more_fail_models_under_contract": 0,
    },
    "quote_preservation": {
        "items": 30,
        "baseline_any_model_fail": 9,
        "contract_any_model_fail": 8,
        "baseline_all_models_fail": 0,
        "contract_all_models_fail": 0,
        "fewer_fail_models_under_contract": 1,
        "more_fail_models_under_contract": 0,
    },
    "script_register_locale": {
        "items": 30,
        "baseline_any_model_fail": 11,
        "contract_any_model_fail": 11,
        "baseline_all_models_fail": 7,
        "contract_all_models_fail": 7,
        "fewer_fail_models_under_contract": 2,
        "more_fail_models_under_contract": 1,
    },
}

EXPECTED_SIGN_TESTS = {
    ("gpt-4.1", "ftga"): {"positive_n": 20, "negative_n": 0, "tie_n": 100, "mean_delta": 0.1667, "two_sided_sign_p": 0.0000},
    ("gpt-4.1", "rtt"): {"positive_n": 20, "negative_n": 2, "tie_n": 98, "mean_delta": 0.1333, "two_sided_sign_p": 0.0001},
    ("gpt-4.1-mini", "ftga"): {"positive_n": 4, "negative_n": 0, "tie_n": 116, "mean_delta": 0.0333, "two_sided_sign_p": 0.1250},
    ("gpt-4.1-nano", "ftga"): {"positive_n": 12, "negative_n": 1, "tie_n": 107, "mean_delta": 0.0917, "two_sided_sign_p": 0.0034},
    ("gpt-4.1-nano", "rtt"): {"positive_n": 17, "negative_n": 3, "tie_n": 100, "mean_delta": 0.1417, "two_sided_sign_p": 0.0026},
    ("gpt-4.1-nano", "token_tax"): {"positive_n": 39, "negative_n": 1, "tie_n": 80, "mean_delta": 0.3513, "two_sided_sign_p": 0.0000},
}

EXPECTED_PROMPT_CONTROL_SUMMARY = {
    "baseline": {"ftga": 67.5, "mean_rtt": 0.47, "mean_token_tax": 1.69, "unresolved_rate": 5.8, "initially_failed_n": 39},
    "generic_helpfulness": {"ftga": 75.0, "mean_rtt": 0.33, "mean_token_tax": 1.37, "unresolved_rate": 3.3, "initially_failed_n": 30},
    "contract": {"ftga": 76.7, "mean_rtt": 0.33, "mean_token_tax": 1.34, "unresolved_rate": 4.2, "initially_failed_n": 28},
}

EXPECTED_PROMPT_CONTROL_EFFECTS = {
    "generic_helpfulness_minus_baseline": {
        "ftga_improved": 9,
        "ftga_worsened": 0,
        "ftga_tied": 111,
        "ftga_sign_test_p": 0.0039,
        "delta_ftga_pp": 7.5,
        "rtt_reduction": 0.14,
        "token_tax_reduction": 0.32,
        "unresolved_reduction_pp": 2.5,
    },
    "contract_minus_baseline": {
        "ftga_improved": 12,
        "ftga_worsened": 1,
        "ftga_tied": 107,
        "ftga_sign_test_p": 0.0034,
        "delta_ftga_pp": 9.2,
        "rtt_reduction": 0.14,
        "token_tax_reduction": 0.35,
        "unresolved_reduction_pp": 1.7,
    },
    "contract_minus_generic_helpfulness": {
        "ftga_improved": 4,
        "ftga_worsened": 2,
        "ftga_tied": 114,
        "ftga_sign_test_p": 0.6875,
        "delta_ftga_pp": 1.7,
        "rtt_reduction": 0.00,
        "token_tax_reduction": 0.03,
        "unresolved_reduction_pp": -0.8,
    },
}

EXPECTED_PROMPT_ABLATION_SUMMARY = {
    "baseline": {"ftga": 67.5, "mean_rtt": 0.47, "mean_token_tax": 1.69, "unresolved_rate": 5.8, "initially_failed_n": 39},
    "generic_helpfulness": {"ftga": 75.0, "mean_rtt": 0.33, "mean_token_tax": 1.37, "unresolved_rate": 3.3, "initially_failed_n": 30},
    "content_preservation": {"ftga": 80.0, "mean_rtt": 0.27, "mean_token_tax": 1.28, "unresolved_rate": 3.3, "initially_failed_n": 24},
    "contract": {"ftga": 76.7, "mean_rtt": 0.33, "mean_token_tax": 1.34, "unresolved_rate": 4.2, "initially_failed_n": 28},
}

EXPECTED_PROMPT_ABLATION_EFFECTS = {
    "generic_helpfulness_minus_baseline": {
        "ftga_improved": 9,
        "ftga_worsened": 0,
        "ftga_tied": 111,
        "ftga_sign_test_p": 0.0039,
        "delta_ftga_pp": 7.5,
        "rtt_reduction": 0.14,
        "token_tax_reduction": 0.32,
        "unresolved_reduction_pp": 2.5,
    },
    "content_preservation_minus_baseline": {
        "ftga_improved": 16,
        "ftga_worsened": 1,
        "ftga_tied": 103,
        "ftga_sign_test_p": 0.0003,
        "delta_ftga_pp": 12.5,
        "rtt_reduction": 0.20,
        "token_tax_reduction": 0.41,
        "unresolved_reduction_pp": 2.5,
    },
    "contract_minus_baseline": {
        "ftga_improved": 12,
        "ftga_worsened": 1,
        "ftga_tied": 107,
        "ftga_sign_test_p": 0.0034,
        "delta_ftga_pp": 9.2,
        "rtt_reduction": 0.14,
        "token_tax_reduction": 0.35,
        "unresolved_reduction_pp": 1.7,
    },
    "content_preservation_minus_generic_helpfulness": {
        "ftga_improved": 7,
        "ftga_worsened": 1,
        "ftga_tied": 112,
        "ftga_sign_test_p": 0.0703,
        "delta_ftga_pp": 5.0,
        "rtt_reduction": 0.06,
        "token_tax_reduction": 0.09,
        "unresolved_reduction_pp": 0.0,
    },
    "contract_minus_content_preservation": {
        "ftga_improved": 3,
        "ftga_worsened": 7,
        "ftga_tied": 110,
        "ftga_sign_test_p": 0.3438,
        "delta_ftga_pp": -3.3,
        "rtt_reduction": -0.06,
        "token_tax_reduction": -0.06,
        "unresolved_reduction_pp": -0.8,
    },
}

EXPECTED_PROMPT_ABLATION_FAMILY_FTGA = {
    ("baseline", "editing_preservation"): 33.3,
    ("generic_helpfulness", "editing_preservation"): 63.3,
    ("content_preservation", "editing_preservation"): 80.0,
    ("contract", "editing_preservation"): 66.7,
    ("content_preservation", "quote_preservation"): 73.3,
    ("contract", "quote_preservation"): 73.3,
    ("content_preservation", "script_register_locale"): 66.7,
    ("contract", "script_register_locale"): 66.7,
}

EXPECTED_PROMPT_ABLATION_CONTRACT_VS_CONTENT_BY_FAMILY = {
    "editing_preservation": {"n": 30, "both_pass": 20, "content_only_pass": 4, "contract_only_pass": 0, "both_fail": 6, "content_lower_rtt": 4, "contract_lower_rtt": 1, "same_rtt": 25},
    "output_language_inference": {"n": 30, "both_pass": 30, "content_only_pass": 0, "contract_only_pass": 0, "both_fail": 0, "content_lower_rtt": 0, "contract_lower_rtt": 0, "same_rtt": 30},
    "quote_preservation": {"n": 30, "both_pass": 21, "content_only_pass": 1, "contract_only_pass": 1, "both_fail": 7, "content_lower_rtt": 3, "contract_lower_rtt": 1, "same_rtt": 26},
    "script_register_locale": {"n": 30, "both_pass": 18, "content_only_pass": 2, "contract_only_pass": 2, "both_fail": 8, "content_lower_rtt": 3, "contract_lower_rtt": 2, "same_rtt": 25},
}

EXPECTED_PROMPT_ABLATION_CONTRACT_VS_CONTENT_BY_LANGUAGE = {
    "ar-en": {"n": 40, "both_pass": 24, "content_only_pass": 3, "contract_only_pass": 1, "both_fail": 12, "content_lower_rtt": 5, "contract_lower_rtt": 1, "same_rtt": 34},
    "es-en": {"n": 40, "both_pass": 29, "content_only_pass": 3, "contract_only_pass": 0, "both_fail": 8, "content_lower_rtt": 3, "contract_lower_rtt": 1, "same_rtt": 36},
    "hi-en": {"n": 40, "both_pass": 36, "content_only_pass": 1, "contract_only_pass": 2, "both_fail": 1, "content_lower_rtt": 2, "contract_lower_rtt": 2, "same_rtt": 36},
}

EXPECTED_TOKEN_BURDEN = {
    ("gpt-4.1-nano", "baseline"): {"mean_total_tokens_until_stop": 139.3, "mean_extra_tokens_after_first": 59.0, "mean_token_tax": 1.69},
    ("gpt-4.1-nano", "contract"): {"mean_total_tokens_until_stop": 308.1, "mean_extra_tokens_after_first": 81.2, "mean_token_tax": 1.34},
    ("gpt-4.1", "baseline"): {"mean_total_tokens_until_stop": 132.7, "mean_extra_tokens_after_first": 51.2, "mean_token_tax": 1.43},
    ("gpt-4.1", "contract"): {"mean_total_tokens_until_stop": 256.3, "mean_extra_tokens_after_first": 32.9, "mean_token_tax": 1.13},
}

EXPECTED_TOKEN_BURDEN_EFFECTS = {
    "gpt-4.1": {"mean_total_tokens_baseline_minus_contract": -123.6, "mean_extra_tokens_baseline_minus_contract": 18.3, "mean_token_tax_baseline_minus_contract": 0.30},
    "gpt-4.1-mini": {"mean_total_tokens_baseline_minus_contract": -172.2, "mean_extra_tokens_baseline_minus_contract": -21.6, "mean_token_tax_baseline_minus_contract": 0.16},
    "gpt-4.1-nano": {"mean_total_tokens_baseline_minus_contract": -168.8, "mean_extra_tokens_baseline_minus_contract": -22.2, "mean_token_tax_baseline_minus_contract": 0.35},
}

EXPECTED_HUMAN_PACKET_COUNTS = {
    ("ar-en", "editing_preservation"): 6,
    ("ar-en", "output_language_inference"): 6,
    ("ar-en", "quote_preservation"): 6,
    ("ar-en", "script_register_locale"): 6,
    ("es-en", "editing_preservation"): 6,
    ("es-en", "output_language_inference"): 6,
    ("es-en", "quote_preservation"): 6,
    ("es-en", "script_register_locale"): 6,
    ("hi-en", "editing_preservation"): 6,
    ("hi-en", "output_language_inference"): 6,
    ("hi-en", "quote_preservation"): 6,
    ("hi-en", "script_register_locale"): 6,
}

ANNOTATION_FIELDS = (
    "annotator_id",
    "human_pass",
    "human_language_pass",
    "human_script_pass",
    "human_preservation_pass",
    "human_task_pass",
    "human_register_locale_pass",
    "human_failure_types",
    "human_notes",
)

PACKET_PRIVATE_FIELDS = {
    "item_id",
    "model",
    "condition",
    "turn",
    "auto_pass",
    "auto_language_pass",
    "auto_script_pass",
    "auto_preservation_pass",
    "auto_task_pass",
    "auto_register_locale_pass",
    "auto_failure_types",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_tex_surface(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if path.name != "main.tex":
        return text

    parts = [text]
    for match in re.finditer(r"\\input\{([^}]+)\}", text):
        rel = match.group(1)
        input_path = path.parent / rel
        if input_path.suffix == "":
            input_path = input_path.with_suffix(".tex")
        require(input_path.exists(), f"missing included TeX file {input_path}")
        parts.append(input_path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def rounded_percent(value: str | float) -> float:
    return round(100.0 * float(value), 1)


def rounded_float(value: str | float) -> float:
    return round(float(value), 2)


PERCENT_FIELDS = {"ftga", "unresolved_rate", "repair_success_at_1", "repair_success_at_2"}
TWO_DECIMAL_FIELDS = {"mean_rtt", "mean_token_tax"}


def check_stress_benchmark(path: Path) -> None:
    rows = load_jsonl(path)
    require(len(rows) == 120, f"expected 120 stress items, found {len(rows)}")
    ids = [row["id"] for row in rows]
    require(len(ids) == len(set(ids)), "stress benchmark has duplicate ids")
    counts = Counter((row["language_pair"], row["task_family"]) for row in rows)
    require(dict(counts) == EXPECTED_STRESS_COUNTS, f"unexpected stress cell counts: {counts}")
    for row in rows:
        for field in ("user_prompt", "expected_response_language", "expected_script", "repair_prompt_1", "repair_prompt_2"):
            require(row.get(field), f"{row['id']} missing {field}")


def check_benchmark_quality(
    summary_path: Path,
    family_path: Path,
    language_family_path: Path,
    markdown_path: Path,
) -> None:
    summary_rows = load_csv(summary_path)
    require(len(summary_rows) == 1, f"expected one benchmark-quality summary row, found {len(summary_rows)}")
    summary = summary_rows[0]
    for field, expected in EXPECTED_BENCHMARK_QUALITY_SUMMARY.items():
        actual = float(summary[field]) if isinstance(expected, float) else int(summary[field])
        require(actual == expected, f"benchmark-quality summary mismatch for {field}: expected {expected}, got {actual}")

    family_rows = load_csv(family_path)
    require(len(family_rows) == 4, f"expected 4 benchmark-quality family rows, found {len(family_rows)}")
    by_family = {row["task_family"]: row for row in family_rows}
    for family, expected in EXPECTED_BENCHMARK_QUALITY_BY_FAMILY.items():
        require(family in by_family, f"missing benchmark-quality family row {family}")
        row = by_family[family]
        for field, expected_value in expected.items():
            actual = int(row[field])
            require(
                actual == expected_value,
                f"benchmark-quality family mismatch for {family}/{field}: expected {expected_value}, got {actual}",
            )

    language_family_rows = load_csv(language_family_path)
    require(len(language_family_rows) == 12, f"expected 12 language-family quality rows, found {len(language_family_rows)}")
    for row in language_family_rows:
        require(int(row["n"]) == 10, f"unexpected quality cell count for {row['language_pair']}/{row['task_family']}")
        require(int(row["unique_user_prompts"]) == 10, f"duplicate prompts in quality cell {row['language_pair']}/{row['task_family']}")
        require(int(row["rows_with_required_markers"]) == 10, f"missing required markers in quality cell {row['language_pair']}/{row['task_family']}")
        require(int(row["rows_with_known_bad_outputs"]) == 10, f"missing known-bad outputs in quality cell {row['language_pair']}/{row['task_family']}")

    markdown = " ".join(markdown_path.read_text(encoding="utf-8").split())
    for phrase in (
        "not a substitute for native speaker validation",
        "normalized_duplicate_prompts | 0",
        "privacy_marker_hits | 0",
        "quote_preservation | 30 | 30 | 30 | 0 | 30 | 60",
        "script_register_locale | 30 | 30 | 30 | 30 | 30 | 39",
    ):
        require(phrase in markdown, f"benchmark-quality markdown missing phrase: {phrase}")


def check_experiment_ledger(
    summary_path: Path,
    artifact_path: Path,
    model_path: Path,
    judge_path: Path,
    repair_path: Path,
    markdown_path: Path,
) -> None:
    summary_rows = load_csv(summary_path)
    require(len(summary_rows) == 1, f"expected one experiment-ledger summary row, found {len(summary_rows)}")
    summary = summary_rows[0]
    for field, expected in EXPECTED_EXPERIMENT_LEDGER_SUMMARY.items():
        require(int(summary[field]) == expected, f"experiment-ledger summary mismatch for {field}")

    artifact_rows = load_csv(artifact_path)
    require(len(artifact_rows) == 8, f"expected 8 experiment-ledger artifact rows, found {len(artifact_rows)}")
    by_artifact = {row["artifact_label"]: row for row in artifact_rows}
    for artifact_label, expected in EXPECTED_EXPERIMENT_LEDGER_BY_ARTIFACT.items():
        require(artifact_label in by_artifact, f"missing experiment-ledger artifact {artifact_label}")
        row = by_artifact[artifact_label]
        require(row["artifact_kind"] == expected["artifact_kind"], f"experiment-ledger kind mismatch for {artifact_label}")
        for field in ("api_response_rows", "first_turn_rows", "trajectories", "input_tokens", "output_tokens", "total_tokens"):
            require(int(row[field]) == expected[field], f"experiment-ledger artifact mismatch for {artifact_label}/{field}")

    model_rows = load_csv(model_path)
    require(len(model_rows) == 12, f"expected 12 experiment-ledger model rows, found {len(model_rows)}")
    by_model = {(row["artifact_label"], row["model"], row["condition"]): row for row in model_rows}
    for key, expected in EXPECTED_EXPERIMENT_LEDGER_BY_MODEL.items():
        require(key in by_model, f"missing experiment-ledger model row {key}")
        row = by_model[key]
        for field, expected_value in expected.items():
            require(int(row[field]) == expected_value, f"experiment-ledger model mismatch for {key}/{field}")

    judge_rows = load_csv(judge_path)
    require(len(judge_rows) == 2, f"expected two experiment-ledger judge rows, found {len(judge_rows)}")
    by_judge = {row["artifact_label"]: row for row in judge_rows}
    require(by_judge["judge_audit"]["judge_model"] == "gpt-4.1", "unexpected original judge model")
    require(by_judge["judge_refresh_gpt55"]["judge_model"] == "gpt-5.5", "unexpected judge-refresh model")
    require(int(by_judge["judge_audit"]["total_tokens"]) == 25946, "unexpected original judge token count")
    require(int(by_judge["judge_refresh_gpt55"]["total_tokens"]) == 31047, "unexpected judge-refresh token count")

    repair_rows = load_csv(repair_path)
    require(len(repair_rows) == 9, f"expected 9 repair-variant usage rows, found {len(repair_rows)}")
    repair_total = sum(int(row["total_tokens"]) for row in repair_rows)
    require(repair_total == 13585, f"unexpected repair-variant token total: {repair_total}")

    markdown = " ".join(markdown_path.read_text(encoding="utf-8").split())
    for phrase in (
        "does not estimate dollar cost",
        "Historical diagnostic shards are excluded",
        "not a paper-facing benchmark result",
        "tracked_api_artifacts | 8",
        "api_response_rows | 1504",
        "model_response_rows | 1288",
        "repair_variant_response_rows | 72",
        "judge_response_rows | 144",
        "prompt_ablation_content_preservation | model_responses | 146",
        "coverage_pilot_v03_gpt54mini | model_responses | 58",
        "coverage_smoke_v03_gpt55 | model_responses | 12",
        "judge_refresh_gpt55 | judge_audit | 72",
        "repair_realism_editing_baseline24 | repair_variant_responses | 72",
        "total_tokens | 285930",
    ):
        require(phrase in markdown, f"experiment-ledger markdown missing phrase: {phrase}")


def check_metrics(summary_path: Path, tex_path: Path) -> None:
    rows = load_csv(summary_path)
    require(len(rows) == 6, f"expected 6 main metric rows, found {len(rows)}")
    tex = " ".join(read_tex_surface(tex_path).split())
    for row in rows:
        key = (row["model"], row["condition"])
        require(key in EXPECTED_MAIN, f"unexpected metric row {key}")
        expected = EXPECTED_MAIN[key]
        actual = {
            "ftga": rounded_percent(row["ftga"]),
            "mean_rtt": rounded_float(row["mean_rtt"]),
            "mean_token_tax": rounded_float(row["mean_token_tax"]),
            "unresolved_rate": rounded_percent(row["unresolved_rate"]),
            "repair_success_at_1": None if row["repair_success_at_1"] == "" else rounded_percent(row["repair_success_at_1"]),
            "repair_success_at_2": None if row["repair_success_at_2"] == "" else rounded_percent(row["repair_success_at_2"]),
        }
        require(actual == expected, f"metric mismatch for {key}: expected {expected}, got {actual}")
        for field, value in expected.items():
            if value is not None:
                if field in PERCENT_FIELDS:
                    rendered = f"{value:.1f}"
                elif field in TWO_DECIMAL_FIELDS:
                    rendered = f"{value:.2f}"
                else:
                    rendered = str(value)
                require(rendered in tex, f"paper TeX missing rendered metric {rendered} for {key}")


def check_current_model_table(tex_path: Path) -> None:
    tex = " ".join(read_tex_surface(tex_path).split())
    required_phrases = [
        "including the current-model refresh rows",
        "GPT-5.4 mini & Baseline & 80.0 & 0.25 & 1.38 & 2.5 & 87.5 & 87.5",
        "GPT-5.4 mini & Contract & 85.0 & 0.25 & 1.24 & 5.0 & 66.7 & 66.7",
        "GPT-5.5 & Baseline & 81.7 & 0.23 & 1.28 & 1.7 & 86.4 & 90.9",
        "GPT-5.5 & Contract & 98.3 & 0.02 & 1.02 & 0.0 & 100.0 & 100.0",
    ]
    for phrase in required_phrases:
        require(phrase in tex, f"paper TeX missing current-model table phrase: {phrase}")


def check_paired_effects(path: Path, tex_path: Path) -> None:
    rows = load_csv(path)
    require(len(rows) == 3, f"expected 3 paired-effect rows, found {len(rows)}")
    tex = read_tex_surface(tex_path)
    require("Paired sign-test sensitivity" in tex, "paper TeX missing paired sensitivity sentence")
    for row in rows:
        model = row["model"]
        require(model in EXPECTED_PAIRED_EFFECTS, f"unexpected paired-effect model {model}")
        require(int(row["n_pairs"]) == 120, f"expected 120 paired items for {model}, found {row['n_pairs']}")
        expected = EXPECTED_PAIRED_EFFECTS[model]
        actual = {field: round(float(row[field]), 1 if "ftga" in field else 2) for field in expected}
        require(actual == expected, f"paired-effect mismatch for {model}: expected {expected}, got {actual}")
    for phrase in ("+9.2", "+3.3", "+16.7", "0.35", "0.16", "0.30"):
        require(phrase in tex, f"paper TeX missing paired-effect phrase {phrase}")


def check_paired_significance(path: Path, markdown_path: Path) -> None:
    rows = load_csv(path)
    require(len(rows) == 12, f"expected 12 paired sign-test rows, found {len(rows)}")
    by_key = {(row["model"], row["metric"]): row for row in rows}
    for key, expected in EXPECTED_SIGN_TESTS.items():
        require(key in by_key, f"missing paired sign-test row {key}")
        row = by_key[key]
        for field in ("positive_n", "negative_n", "tie_n"):
            require(int(row[field]) == expected[field], f"paired sign-test mismatch for {key} {field}")
        for field in ("mean_delta", "two_sided_sign_p"):
            require(round(float(row[field]), 4) == expected[field], f"paired sign-test mismatch for {key} {field}")

    markdown = " ".join(markdown_path.read_text(encoding="utf-8").split())
    required_markdown = [
        "gpt-4.1 | FTGA | contract_minus_baseline | 20 | 0 | 100 | 0.167 | 0.0000",
        "gpt-4.1-mini | FTGA | contract_minus_baseline | 4 | 0 | 116 | 0.033 | 0.1250",
        "gpt-4.1-nano | FTGA | contract_minus_baseline | 12 | 1 | 107 | 0.092 | 0.0034",
        "gpt-4.1-nano | RTT reduction | baseline_minus_contract | 17 | 3 | 100 | 0.142 | 0.0026",
    ]
    for phrase in required_markdown:
        require(phrase in markdown, f"paired significance markdown missing phrase: {phrase}")


def check_language_slices(metrics_path: Path, effects_path: Path, aggregate_path: Path, markdown_path: Path) -> None:
    metric_rows = load_csv(metrics_path)
    require(len(metric_rows) == 18, f"expected 18 language-slice metric rows, found {len(metric_rows)}")
    by_metric = {(row["model"], row["condition"], row["language_pair"]): row for row in metric_rows}
    for key, expected in EXPECTED_LANGUAGE_SLICE_METRICS.items():
        require(key in by_metric, f"missing language-slice metric row {key}")
        row = by_metric[key]
        require(int(row["n"]) == 40, f"expected 40 language-slice trajectories for {key}")
        for field, expected_value in expected.items():
            actual = int(row[field]) if field == "initially_failed_n" else round(float(row[field]), 3 if "token_tax" in field or field == "mean_rtt" else 1)
            require(actual == expected_value, f"language-slice metric mismatch for {key}/{field}: expected {expected_value}, got {actual}")

    effect_rows = load_csv(effects_path)
    require(len(effect_rows) == 9, f"expected 9 language-slice paired-effect rows, found {len(effect_rows)}")
    by_effect = {(row["model"], row["language_pair"]): row for row in effect_rows}
    for key, expected in EXPECTED_LANGUAGE_SLICE_EFFECTS.items():
        require(key in by_effect, f"missing language-slice effect row {key}")
        row = by_effect[key]
        require(int(row["n_pairs"]) == 40, f"expected 40 language-slice pairs for {key}")
        for field, expected_value in expected.items():
            if field.startswith("ftga_") and field.endswith("_n"):
                actual = int(row[field])
            elif field == "ftga_sign_test_p":
                actual = round(float(row[field]), 4)
            elif field in {"rtt_reduction", "token_tax_reduction"}:
                actual = round(float(row[field]), 3)
            else:
                actual = round(float(row[field]), 1)
            require(actual == expected_value, f"language-slice effect mismatch for {key}/{field}: expected {expected_value}, got {actual}")

    aggregate_rows = load_csv(aggregate_path)
    require(len(aggregate_rows) == 3, f"expected 3 aggregate language-slice rows, found {len(aggregate_rows)}")
    by_aggregate = {row["language_pair"]: row for row in aggregate_rows}
    for language_pair, expected in EXPECTED_LANGUAGE_SLICE_AGGREGATE.items():
        require(language_pair in by_aggregate, f"missing aggregate language-slice row {language_pair}")
        row = by_aggregate[language_pair]
        require(int(row["models"]) == 3, f"expected 3 models in aggregate language-slice row {language_pair}")
        for field, expected_value in expected.items():
            if field.endswith("_n"):
                actual = int(row[field])
            elif field in {"mean_rtt_reduction", "mean_token_tax_reduction"}:
                actual = round(float(row[field]), 3)
            else:
                actual = round(float(row[field]), 1)
            require(actual == expected_value, f"aggregate language-slice mismatch for {language_pair}/{field}: expected {expected_value}, got {actual}")

    markdown = " ".join(markdown_path.read_text(encoding="utf-8").split())
    for phrase in (
        "not a population-level statement",
        "gpt-4.1-nano | ar-en | +25.0 pp | 0.425 | 0.859 | +7.5 pp | 10 / 0 / 30 | 0.0020",
        "gpt-4.1-mini | es-en | +0.0 pp | 0.000 | 0.152 | +0.0 pp | 0 / 0 / 40 | 1.0000",
        "ar-en | 3 | +20.0 pp | 0.217 | 0.511 | 24 / 0 / 96",
        "Aggregated Hindi-English FTGA movement is +0.0 pp",
        "not uniformly strong across every model/language pair",
    ):
        require(phrase in markdown, f"language-slice markdown missing phrase: {phrase}")


def check_repair_dynamics(
    model_path: Path,
    family_path: Path,
    paired_path: Path,
    transition_path: Path,
    markdown_path: Path,
) -> None:
    model_rows = load_csv(model_path)
    require(len(model_rows) == 6, f"expected 6 repair-dynamics model rows, found {len(model_rows)}")
    by_model = {(row["model"], row["condition"]): row for row in model_rows}
    for key, expected in EXPECTED_REPAIR_DYNAMICS_MODEL_ROWS.items():
        require(key in by_model, f"missing repair-dynamics model row {key}")
        row = by_model[key]
        require(int(row["n"]) == 120, f"expected 120 repair trajectories for {key}")
        for field, expected_value in expected.items():
            actual = round(float(row[field]), 3) if field == "mean_rtt" else int(row[field])
            require(actual == expected_value, f"repair-dynamics model mismatch for {key}/{field}: expected {expected_value}, got {actual}")

    family_rows = load_csv(family_path)
    require(len(family_rows) == 8, f"expected 8 repair-dynamics family rows, found {len(family_rows)}")
    by_family = {(row["condition"], row["task_family"]): row for row in family_rows}
    for key, expected in EXPECTED_REPAIR_DYNAMICS_FAMILY_ROWS.items():
        require(key in by_family, f"missing repair-dynamics family row {key}")
        row = by_family[key]
        require(int(row["n"]) == 90, f"expected 90 repair trajectories for {key}")
        for field, expected_value in expected.items():
            actual = round(float(row[field]), 3) if field == "mean_rtt" else int(row[field])
            require(actual == expected_value, f"repair-dynamics family mismatch for {key}/{field}: expected {expected_value}, got {actual}")

    paired_rows = load_csv(paired_path)
    require(len(paired_rows) == 3, f"expected 3 repair paired rows, found {len(paired_rows)}")
    by_paired = {row["model"]: row for row in paired_rows}
    for model, expected in EXPECTED_REPAIR_PAIRED_EFFECTS.items():
        require(model in by_paired, f"missing repair paired row {model}")
        row = by_paired[model]
        require(int(row["n_pairs"]) == 120, f"expected 120 repair pairs for {model}")
        for field, expected_value in expected.items():
            actual = round(float(row[field]), 3) if field == "mean_rtt_reduction" else int(row[field])
            require(actual == expected_value, f"repair paired mismatch for {model}/{field}: expected {expected_value}, got {actual}")

    transition_rows = load_csv(transition_path)
    require(len(transition_rows) == 48, f"expected 48 repair transition rows, found {len(transition_rows)}")
    by_transition = {
        (row["model"], int(row["baseline_rtt"]), int(row["contract_rtt"])): int(row["count"])
        for row in transition_rows
    }
    for key, expected_count in EXPECTED_REPAIR_TRANSITIONS.items():
        require(by_transition.get(key) == expected_count, f"repair transition mismatch for {key}: expected {expected_count}, got {by_transition.get(key)}")

    markdown = " ".join(markdown_path.read_text(encoding="utf-8").split())
    for phrase in (
        "RTT=0 means first-turn success",
        "gpt-4.1 | baseline | 92 (76.7%) | 25 (20.8%) | 0 (0.0%) | 3 (2.5%)",
        "gpt-4.1-nano | contract | 92 (76.7%) | 22 (18.3%) | 1 (0.8%) | 5 (4.2%)",
        "gpt-4.1 | 0.133 | 20 | 2 | 98 | 20 | 0 | 0 | 2",
        "script/register/locale unresolved cases under the contract are 11/90",
    ):
        require(phrase in markdown, f"repair-dynamics markdown missing phrase: {phrase}")


def check_prompt_control(summary_path: Path, effects_path: Path, markdown_path: Path, prompt_path: Path) -> None:
    prompt = prompt_path.read_text(encoding="utf-8").lower()
    for forbidden in ("preserve", "quoted", "script", "multilingual", "content language"):
        require(forbidden not in prompt, f"generic-helpfulness prompt contains contract-specific term: {forbidden}")

    summary_rows = load_csv(summary_path)
    require(len(summary_rows) == 3, f"expected 3 prompt-control summary rows, found {len(summary_rows)}")
    for row in summary_rows:
        condition = row["condition"]
        require(condition in EXPECTED_PROMPT_CONTROL_SUMMARY, f"unexpected prompt-control condition {condition}")
        expected = EXPECTED_PROMPT_CONTROL_SUMMARY[condition]
        actual = {
            "ftga": rounded_percent(row["ftga"]),
            "mean_rtt": rounded_float(row["mean_rtt"]),
            "mean_token_tax": rounded_float(row["mean_token_tax"]),
            "unresolved_rate": rounded_percent(row["unresolved_rate"]),
            "initially_failed_n": int(row["initially_failed_n"]),
        }
        require(actual == expected, f"prompt-control summary mismatch for {condition}: expected {expected}, got {actual}")

    effect_rows = load_csv(effects_path)
    require(len(effect_rows) == 3, f"expected 3 prompt-control effect rows, found {len(effect_rows)}")
    for row in effect_rows:
        comparison = row["comparison"]
        require(comparison in EXPECTED_PROMPT_CONTROL_EFFECTS, f"unexpected prompt-control comparison {comparison}")
        expected = EXPECTED_PROMPT_CONTROL_EFFECTS[comparison]
        actual = {
            "ftga_improved": int(row["ftga_improved"]),
            "ftga_worsened": int(row["ftga_worsened"]),
            "ftga_tied": int(row["ftga_tied"]),
            "ftga_sign_test_p": round(float(row["ftga_sign_test_p"]), 4),
            "delta_ftga_pp": round(float(row["delta_ftga_pp"]), 1),
            "rtt_reduction": rounded_float(row["rtt_reduction"]),
            "token_tax_reduction": rounded_float(row["token_tax_reduction"]),
            "unresolved_reduction_pp": round(float(row["unresolved_reduction_pp"]), 1),
        }
        require(actual == expected, f"prompt-control effect mismatch for {comparison}: expected {expected}, got {actual}")

    markdown = " ".join(markdown_path.read_text(encoding="utf-8").split())
    for phrase in (
        "single-model diagnostic",
        "not a paper-facing three-model claim",
        "does not prove that every gain is specific",
        "120-item stress pilot",
        "generic_helpfulness_minus_baseline | +7.5 pp",
        "contract_minus_generic_helpfulness | +1.7 pp",
    ):
        require(phrase in markdown, f"prompt-control markdown missing phrase: {phrase}")


def check_prompt_ablation(
    summary_path: Path,
    family_path: Path,
    effects_path: Path,
    transition_family_path: Path,
    transition_language_path: Path,
    transition_examples_path: Path,
    transition_items_path: Path,
    markdown_path: Path,
    content_prompt_path: Path,
) -> None:
    content_prompt = content_prompt_path.read_text(encoding="utf-8")
    for phrase in (
        "Preserve the content language",
        "Preserve quoted text",
        "Output only the requested artifact",
    ):
        require(phrase in content_prompt, f"content-preservation prompt missing phrase: {phrase}")

    summary_rows = load_csv(summary_path)
    require(len(summary_rows) == 4, f"expected 4 prompt-ablation summary rows, found {len(summary_rows)}")
    for row in summary_rows:
        condition = row["condition"]
        require(condition in EXPECTED_PROMPT_ABLATION_SUMMARY, f"unexpected prompt-ablation condition {condition}")
        expected = EXPECTED_PROMPT_ABLATION_SUMMARY[condition]
        actual = {
            "ftga": rounded_percent(row["ftga"]),
            "mean_rtt": rounded_float(row["mean_rtt"]),
            "mean_token_tax": rounded_float(row["mean_token_tax"]),
            "unresolved_rate": rounded_percent(row["unresolved_rate"]),
            "initially_failed_n": int(row["initially_failed_n"]),
        }
        require(actual == expected, f"prompt-ablation summary mismatch for {condition}: expected {expected}, got {actual}")

    effect_rows = load_csv(effects_path)
    require(len(effect_rows) == 5, f"expected 5 prompt-ablation effect rows, found {len(effect_rows)}")
    for row in effect_rows:
        comparison = row["comparison"]
        require(comparison in EXPECTED_PROMPT_ABLATION_EFFECTS, f"unexpected prompt-ablation comparison {comparison}")
        expected = EXPECTED_PROMPT_ABLATION_EFFECTS[comparison]
        actual = {
            "ftga_improved": int(row["ftga_improved"]),
            "ftga_worsened": int(row["ftga_worsened"]),
            "ftga_tied": int(row["ftga_tied"]),
            "ftga_sign_test_p": round(float(row["ftga_sign_test_p"]), 4),
            "delta_ftga_pp": round(float(row["delta_ftga_pp"]), 1),
            "rtt_reduction": rounded_float(row["rtt_reduction"]),
            "token_tax_reduction": rounded_float(row["token_tax_reduction"]),
            "unresolved_reduction_pp": round(float(row["unresolved_reduction_pp"]), 1),
        }
        require(actual == expected, f"prompt-ablation effect mismatch for {comparison}: expected {expected}, got {actual}")

    family_rows = load_csv(family_path)
    require(len(family_rows) == 16, f"expected 16 prompt-ablation family rows, found {len(family_rows)}")
    by_family = {(row["condition"], row["task_family"]): row for row in family_rows}
    for key, expected_ftga in EXPECTED_PROMPT_ABLATION_FAMILY_FTGA.items():
        require(key in by_family, f"missing prompt-ablation family row {key}")
        require(rounded_percent(by_family[key]["ftga"]) == expected_ftga, f"prompt-ablation family FTGA mismatch for {key}")

    transition_family_rows = load_csv(transition_family_path)
    require(
        len(transition_family_rows) == len(EXPECTED_PROMPT_ABLATION_CONTRACT_VS_CONTENT_BY_FAMILY),
        f"expected {len(EXPECTED_PROMPT_ABLATION_CONTRACT_VS_CONTENT_BY_FAMILY)} contract-vs-content family rows, found {len(transition_family_rows)}",
    )
    for row in transition_family_rows:
        family = row["task_family"]
        require(family in EXPECTED_PROMPT_ABLATION_CONTRACT_VS_CONTENT_BY_FAMILY, f"unexpected contract-vs-content family {family}")
        actual = {
            field: int(row[field])
            for field in (
                "n",
                "both_pass",
                "content_only_pass",
                "contract_only_pass",
                "both_fail",
                "content_lower_rtt",
                "contract_lower_rtt",
                "same_rtt",
            )
        }
        expected = EXPECTED_PROMPT_ABLATION_CONTRACT_VS_CONTENT_BY_FAMILY[family]
        require(actual == expected, f"contract-vs-content family mismatch for {family}: expected {expected}, got {actual}")

    transition_language_rows = load_csv(transition_language_path)
    require(
        len(transition_language_rows) == len(EXPECTED_PROMPT_ABLATION_CONTRACT_VS_CONTENT_BY_LANGUAGE),
        f"expected {len(EXPECTED_PROMPT_ABLATION_CONTRACT_VS_CONTENT_BY_LANGUAGE)} contract-vs-content language rows, found {len(transition_language_rows)}",
    )
    for row in transition_language_rows:
        language_pair = row["language_pair"]
        require(language_pair in EXPECTED_PROMPT_ABLATION_CONTRACT_VS_CONTENT_BY_LANGUAGE, f"unexpected contract-vs-content language {language_pair}")
        actual = {
            field: int(row[field])
            for field in (
                "n",
                "both_pass",
                "content_only_pass",
                "contract_only_pass",
                "both_fail",
                "content_lower_rtt",
                "contract_lower_rtt",
                "same_rtt",
            )
        }
        expected = EXPECTED_PROMPT_ABLATION_CONTRACT_VS_CONTENT_BY_LANGUAGE[language_pair]
        require(actual == expected, f"contract-vs-content language mismatch for {language_pair}: expected {expected}, got {actual}")

    transition_items = load_csv(transition_items_path)
    require(len(transition_items) == 120, f"expected 120 contract-vs-content item rows, found {len(transition_items)}")
    transition_examples = load_csv(transition_examples_path)
    require(len(transition_examples) == 11, f"expected 11 contract-vs-content example rows, found {len(transition_examples)}")
    by_example = {row["item_id"]: row for row in transition_examples}
    require("es_en_SA_007" in by_example, "missing corrected Spanish example es_en_SA_007")
    require(
        by_example["es_en_SA_007"]["transition"] == "both_fail",
        "corrected Spanish example should now be a both-fail transition",
    )

    markdown = " ".join(markdown_path.read_text(encoding="utf-8").split())
    for phrase in (
        "single-model diagnostic",
        "content_preservation | 80.0%",
        "content_preservation_minus_baseline | +12.5 pp",
        "contract_minus_content_preservation | -3.3 pp",
        "editing_preservation | 33.3% | 63.3% | 80.0% | 66.7%",
        "Content vs Full-Contract Transitions",
        "es_en_SA_007 | editing_preservation | es-en | both_fail",
        "best nano prompt tested in this diagnostic is the narrower content-preservation scaffold",
    ):
        require(phrase in markdown, f"prompt-ablation markdown missing phrase: {phrase}")


def check_token_burden(summary_path: Path, effects_path: Path, markdown_path: Path) -> None:
    rows = load_csv(summary_path)
    require(len(rows) == 6, f"expected 6 token-burden summary rows, found {len(rows)}")
    by_key = {(row["model"], row["condition"]): row for row in rows}
    for key, expected in EXPECTED_TOKEN_BURDEN.items():
        require(key in by_key, f"missing token-burden row {key}")
        row = by_key[key]
        require(int(row["n"]) == 120, f"expected 120 token-burden trajectories for {key}")
        actual = {
            field: round(float(row[field]), 2 if field == "mean_token_tax" else 1)
            for field in expected
        }
        require(actual == expected, f"token-burden mismatch for {key}: expected {expected}, got {actual}")

    effect_rows = load_csv(effects_path)
    require(len(effect_rows) == 3, f"expected 3 token-burden effect rows, found {len(effect_rows)}")
    for row in effect_rows:
        model = row["model"]
        require(model in EXPECTED_TOKEN_BURDEN_EFFECTS, f"unexpected token-burden effect model {model}")
        require(int(row["n_pairs"]) == 120, f"expected 120 token-burden pairs for {model}")
        expected = EXPECTED_TOKEN_BURDEN_EFFECTS[model]
        actual = {
            field: round(float(row[field]), 2 if field == "mean_token_tax_baseline_minus_contract" else 1)
            for field in expected
        }
        require(actual == expected, f"token-burden effect mismatch for {model}: expected {expected}, got {actual}")

    markdown = " ".join(markdown_path.read_text(encoding="utf-8").split())
    for phrase in (
        "absolute total tokens increase",
        "rather than as an API-cost claim",
        "gpt-4.1-nano | contract | 226.9 | 308.1 | 81.2 | 1.34x",
    ):
        require(phrase in markdown, f"token-burden markdown missing phrase: {phrase}")


def check_component_breakdown(
    model_path: Path,
    family_path: Path,
    paired_path: Path,
    markdown_path: Path,
) -> None:
    model_rows = load_csv(model_path)
    require(len(model_rows) == 6, f"expected 6 component model rows, found {len(model_rows)}")
    by_model = {(row["model"], row["condition"]): row for row in model_rows}
    for key, expected in EXPECTED_COMPONENT_MODEL_ROWS.items():
        require(key in by_model, f"missing component model row {key}")
        row = by_model[key]
        require(int(row["n"]) == 120, f"expected 120 first-turn component rows for {key}")
        for field, expected_value in expected.items():
            require(round(float(row[field]), 1) == expected_value, f"component model mismatch for {key}/{field}")

    family_rows = load_csv(family_path)
    require(len(family_rows) == 8, f"expected 8 component family rows, found {len(family_rows)}")
    by_family = {(row["condition"], row["task_family"]): row for row in family_rows}
    for key, expected in EXPECTED_COMPONENT_FAMILY_ROWS.items():
        require(key in by_family, f"missing component family row {key}")
        row = by_family[key]
        require(int(row["n"]) == 90, f"expected 90 first-turn component rows for {key}")
        for field, expected_value in expected.items():
            require(round(float(row[field]), 1) == expected_value, f"component family mismatch for {key}/{field}")

    paired_rows = load_csv(paired_path)
    require(len(paired_rows) == 18, f"expected 18 component paired rows, found {len(paired_rows)}")
    by_paired = {(row["model"], row["component"]): row for row in paired_rows}
    for key, expected in EXPECTED_COMPONENT_PAIRED_ROWS.items():
        require(key in by_paired, f"missing component paired row {key}")
        row = by_paired[key]
        require(int(row["n_pairs"]) == 120, f"expected 120 paired component rows for {key}")
        for field, expected_value in expected.items():
            actual = round(float(row[field]), 1) if field == "delta_pp" else int(row[field])
            require(actual == expected_value, f"component paired mismatch for {key}/{field}")

    markdown = " ".join(markdown_path.read_text(encoding="utf-8").split())
    for phrase in (
        "not independent human judgments",
        "gpt-4.1 | Language | +15.8 pp | 19 | 0 | 101",
        "gpt-4.1-nano | Task | +9.2 pp | 11 | 0 | 109",
        "language pass rate rises from 33.3% to 70.0%",
        "mini preservation delta is +0.0 pp",
        "should not be presented as evidence that nuanced register judgments are solved",
    ):
        require(phrase in markdown, f"component-breakdown markdown missing phrase: {phrase}")


def check_scorer_ablation(
    condition_path: Path,
    family_path: Path,
    signatures_path: Path,
    markdown_path: Path,
) -> None:
    condition_rows = {row["condition"]: row for row in load_csv(condition_path)}
    require(set(condition_rows) == set(EXPECTED_SCORER_ABLATION_BY_CONDITION), f"unexpected scorer-ablation conditions: {set(condition_rows)}")
    for condition, expected in EXPECTED_SCORER_ABLATION_BY_CONDITION.items():
        row = condition_rows[condition]
        for field, expected_value in expected.items():
            actual = int(row[field]) if field.endswith("_n") or field == "n" else round(float(row[field]), 1)
            require(actual == expected_value, f"scorer-ablation condition mismatch for {condition}/{field}: expected {expected_value}, got {actual}")

    family_rows = {(row["condition"], row["task_family"]): row for row in load_csv(family_path)}
    for key, expected in EXPECTED_SCORER_ABLATION_FAMILY_ROWS.items():
        require(key in family_rows, f"missing scorer-ablation family row {key}")
        row = family_rows[key]
        for field, expected_value in expected.items():
            actual = int(row[field]) if field.endswith("_n") else round(float(row[field]), 1)
            require(actual == expected_value, f"scorer-ablation family mismatch for {key}/{field}: expected {expected_value}, got {actual}")

    signature_rows = {
        (row["condition"], row["task_family"], row["failure_signature"]): row
        for row in load_csv(signatures_path)
    }
    for key, expected in EXPECTED_SCORER_ABLATION_SIGNATURES.items():
        require(key in signature_rows, f"missing scorer-ablation signature row {key}")
        row = signature_rows[key]
        actual = {
            "count": int(row["count"]),
            "share_of_first_turn_failures": round(float(row["share_of_first_turn_failures"]), 3),
        }
        require(actual == expected, f"scorer-ablation signature mismatch for {key}: expected {expected}, got {actual}")

    markdown = " ".join(markdown_path.read_text(encoding="utf-8").split())
    for phrase in (
        "scorer-sensitivity diagnostic, not a replacement for human validation",
        "baseline | 73.3% | 76.4% (+3.1)",
        "contract | 83.1% | 83.3% (+0.2)",
        "Script/register/locale | 70.0% | +1.1 pp | +22.2 pp",
        "language+script+task | 30 | 50.0%",
        "not a single fragile rule",
    ):
        require(phrase in markdown, f"scorer-ablation markdown missing phrase: {phrase}")


def check_task_useful_failures(
    condition_path: Path,
    family_path: Path,
    signatures_path: Path,
    markdown_path: Path,
    tex_path: Path,
) -> None:
    condition_rows = {row["condition"]: row for row in load_csv(condition_path)}
    require(set(condition_rows) == set(EXPECTED_TASK_USEFUL_BY_CONDITION), f"unexpected task-useful conditions: {set(condition_rows)}")
    for condition, expected in EXPECTED_TASK_USEFUL_BY_CONDITION.items():
        row = condition_rows[condition]
        for field, expected_value in expected.items():
            actual = int(row[field]) if field.endswith("_n") else round(float(row[field]), 1)
            require(actual == expected_value, f"task-useful condition mismatch for {condition}/{field}: expected {expected_value}, got {actual}")

    family_rows = {(row["condition"], row["task_family"]): row for row in load_csv(family_path)}
    for key, expected in EXPECTED_TASK_USEFUL_FAMILY_ROWS.items():
        require(key in family_rows, f"missing task-useful family row {key}")
        row = family_rows[key]
        for field, expected_value in expected.items():
            actual = int(row[field])
            require(actual == expected_value, f"task-useful family mismatch for {key}/{field}: expected {expected_value}, got {actual}")

    signature_rows = {
        (row["condition"], row["task_family"], row["failure_signature"]): int(row["count"])
        for row in load_csv(signatures_path)
    }
    require(signature_rows == EXPECTED_TASK_USEFUL_SIGNATURES, f"task-useful signatures mismatch: {signature_rows}")

    markdown = " ".join(markdown_path.read_text(encoding="utf-8").split())
    for phrase in (
        "task-useful contract failure",
        "baseline | 96 | 31 (8.6% of all rows) | 32.3% | 11 | 11",
        "contract | 61 | 20 (5.6% of all rows) | 32.8% | 1 | 1",
        "The stricter task+preservation useful subset falls from 11 to 1",
        "Script/register/locale (20) rows",
    ):
        require(phrase in markdown, f"task-useful markdown missing phrase: {phrase}")

    tex = " ".join(read_tex_surface(tex_path).split())
    for phrase in (
        "31/96 baseline first-turn failures still pass the task component",
        "stricter task-plus-preservation slice falls from 11 to 1",
    ):
        require(phrase in tex, f"paper TeX missing task-useful phrase: {phrase}")


def check_failure_mode_analysis(
    *,
    family_summary_path: Path,
    failure_summary_path: Path,
    markdown_path: Path,
    tex_path: Path,
) -> None:
    rows = load_csv(family_summary_path)
    require(len(rows) == 12, f"expected 12 family-effect rows, found {len(rows)}")
    by_key = {(row["model"], row["task_family"]): row for row in rows}
    for key, expected in EXPECTED_FAMILY_EFFECTS.items():
        require(key in by_key, f"missing family-effect row {key}")
        row = by_key[key]
        for field, expected_value in expected.items():
            actual = int(row[field]) if field.endswith("_failures") else round(float(row[field]), 2)
            require(actual == expected_value, f"family-effect mismatch for {key} {field}: expected {expected_value}, got {actual}")

    failure_rows = load_csv(failure_summary_path)
    failures = {
        (row["condition"], row["task_family"], row["failure_type"]): row
        for row in failure_rows
    }
    editing_wrong = failures[("baseline", "editing_preservation", "wrong_output_language")]
    require(int(editing_wrong["count"]) == 60, "expected 60 baseline editing wrong-output-language failures")
    require(int(editing_wrong["initial_failure_denominator"]) == 60, "expected 60 baseline editing initial failures")
    quote_preservation = failures[("baseline", "quote_preservation", "preservation_failure")]
    require(int(quote_preservation["count"]) == 9, "expected 9 baseline quote-preservation preservation failures")

    markdown = markdown_path.read_text(encoding="utf-8")
    required_markdown_phrases = [
        "Editing preservation | 33.3% | 70.0% | 60/90 | 27/90",
        "Output-language inference | 100.0% | 100.0%",
        "Nano quote-preservation remains a capability boundary",
        "wrong_output_language | 60 | 100.0%",
    ]
    for phrase in required_markdown_phrases:
        require(phrase in markdown, f"failure-mode markdown missing phrase: {phrase}")

    tex = " ".join(read_tex_surface(tex_path).split())
    required_tex_phrases = [
        "aggregate baseline FTGA is 33.3\\%",
        "60/90 first-turn failures",
        "output-language inference is saturated at 100.0\\%",
        "+63.3, +13.3, and +33.3",
        "lowers mean RTT from 0.63 to",
        "unresolved rate from 13.3\\% to 3.3\\%",
    ]
    for phrase in required_tex_phrases:
        require(phrase in tex, f"paper TeX missing failure-mode phrase: {phrase}")


def check_item_consistency(
    summary_path: Path,
    family_path: Path,
    hardest_path: Path,
    markdown_path: Path,
) -> None:
    summary_rows = load_csv(summary_path)
    require(len(summary_rows) == 1, f"expected one item-consistency summary row, found {len(summary_rows)}")
    summary = {field: int(value) for field, value in summary_rows[0].items()}
    require(
        summary == EXPECTED_ITEM_CONSISTENCY_SUMMARY,
        f"item-consistency summary mismatch: expected {EXPECTED_ITEM_CONSISTENCY_SUMMARY}, got {summary}",
    )

    family_rows = {row["task_family"]: row for row in load_csv(family_path)}
    require(set(family_rows) == set(EXPECTED_ITEM_CONSISTENCY_BY_FAMILY), f"unexpected item-consistency families: {set(family_rows)}")
    for family, expected in EXPECTED_ITEM_CONSISTENCY_BY_FAMILY.items():
        row = family_rows[family]
        for field, expected_value in expected.items():
            require(int(row[field]) == expected_value, f"item-consistency family mismatch for {family}/{field}")

    hardest_rows = load_csv(hardest_path)
    require(len(hardest_rows) == 12, f"expected 12 hardest residual item rows, found {len(hardest_rows)}")
    top = hardest_rows[0]
    require(top["item_id"] == "ar_en_SD_008", f"unexpected top residual item {top['item_id']}")
    require(int(top["contract_fail_models_n"]) == 3, "expected top residual item to fail for all three contract models")
    require(int(top["contract_unresolved_models_n"]) == 3, "expected top residual item to remain unresolved for all three contract models")

    markdown = " ".join(markdown_path.read_text(encoding="utf-8").split())
    for phrase in (
        "Baseline any-model fail | 40 | 33.3%",
        "Contract all-model fail | 8 | 6.7%",
        "Fewer failing models under contract | 22 | 18.3%",
        "Editing preservation | 30 | 20 (66.7%) | 16 (53.3%) | 20 | 1 | 19 | 0",
        "Script/register/locale | 30 | 11 (36.7%) | 11 (36.7%) | 7 | 7 | 2 | 1",
        "35/120 items still fail for at least one model",
    ):
        require(phrase in markdown, f"item-consistency markdown missing phrase: {phrase}")


def check_error_atlas(csv_path: Path, markdown_path: Path) -> None:
    rows = load_csv(csv_path)
    require(len(rows) == 157, f"expected 157 first-turn error atlas rows, found {len(rows)}")
    require(all(row["response_excerpt"].strip() for row in rows), "error atlas contains blank response excerpt")
    by_family = Counter(row["task_family"] for row in rows)
    require(
        dict(by_family) == {
            "editing_preservation": 87,
            "quote_preservation": 17,
            "script_register_locale": 53,
        },
        f"unexpected error-atlas family counts: {by_family}",
    )
    by_model_condition = Counter((row["model"], row["condition"]) for row in rows)
    require(
        dict(by_model_condition) == {
            ("gpt-4.1", "baseline"): 28,
            ("gpt-4.1", "contract"): 8,
            ("gpt-4.1-mini", "baseline"): 29,
            ("gpt-4.1-mini", "contract"): 25,
            ("gpt-4.1-nano", "baseline"): 39,
            ("gpt-4.1-nano", "contract"): 28,
        },
        f"unexpected error-atlas model/condition counts: {by_model_condition}",
    )
    unresolved = [row for row in rows if row["unresolved"] == "1"]
    require(len(unresolved) == 23, f"expected 23 unresolved atlas rows, found {len(unresolved)}")
    require(any(row["item_id"] == "ar_en_SD_008" for row in unresolved), "expected ar_en_SD_008 among unresolved cases")

    markdown = markdown_path.read_text(encoding="utf-8")
    required_phrases = [
        "First-turn failures: 157",
        "Unresolved after two repair prompts: 23",
        "| Editing preservation | 87 |",
        "| Quote preservation | 17 |",
        "| Script/register/locale | 53 |",
        "| gpt-4.1-nano | contract | 28 |",
        "ar_en_SD_008 | gpt-4.1-nano | contract",
    ]
    for phrase in required_phrases:
        require(phrase in markdown, f"error atlas missing phrase: {phrase}")


def check_judge_audit(path: Path) -> None:
    rows = load_jsonl(path)
    require(len(rows) == 72, f"expected 72 judge rows, found {len(rows)}")
    agree = sum(bool(row["auto_pass"]) == bool(row["judge_pass"]) for row in rows)
    require(agree == 71, f"expected 71/72 judge agreement, got {agree}/72")
    require(all(not row.get("judge_parse_error") for row in rows), "judge audit has parse errors")
    strata = Counter((row["model"], row["condition"], row["task_family"]) for row in rows)
    require(len(strata) == 24, f"expected 24 judge strata, found {len(strata)}")
    require(all(count == 3 for count in strata.values()), f"judge audit not 3 per stratum: {strata}")
    disagreements = [row for row in rows if bool(row["auto_pass"]) != bool(row["judge_pass"])]
    require(len(disagreements) == 1, "expected exactly one judge disagreement")
    require(disagreements[0]["item_id"] == "es_en_SA_007", f"unexpected judge disagreement: {disagreements[0]}")


def check_judge_agreement(
    summary_path: Path,
    family_path: Path,
    component_path: Path,
    pass_fail_disagreements_path: Path,
    component_disagreements_path: Path,
    markdown_path: Path,
) -> None:
    summary_rows = load_csv(summary_path)
    require(len(summary_rows) == 1, f"expected one judge-agreement summary row, found {len(summary_rows)}")
    summary = summary_rows[0]
    for field, expected in EXPECTED_JUDGE_AGREEMENT_SUMMARY.items():
        actual = int(summary[field]) if field.endswith("_n") or field == "n" else round(float(summary[field]), 1)
        require(actual == expected, f"judge-agreement summary mismatch for {field}: expected {expected}, got {actual}")

    family_rows = load_csv(family_path)
    require(len(family_rows) == 4, f"expected 4 judge-agreement family rows, found {len(family_rows)}")
    by_family = {row["task_family"]: row for row in family_rows}
    for family, expected in EXPECTED_JUDGE_AGREEMENT_BY_FAMILY.items():
        require(family in by_family, f"missing judge-agreement family row {family}")
        row = by_family[family]
        for field, expected_value in expected.items():
            actual = int(row[field]) if field.endswith("_n") or field == "n" else round(float(row[field]), 1)
            require(actual == expected_value, f"judge-agreement family mismatch for {family}/{field}")

    component_rows = load_csv(component_path)
    require(len(component_rows) == 5, f"expected 5 judge component rows, found {len(component_rows)}")
    by_component = {row["component"]: row for row in component_rows}
    for component, expected in EXPECTED_JUDGE_COMPONENT_AGREEMENT.items():
        require(component in by_component, f"missing judge component row {component}")
        row = by_component[component]
        require(int(row["n"]) == 72, f"expected 72 rows for judge component {component}")
        for field, expected_value in expected.items():
            actual = int(row[field]) if field.endswith("_n") else round(float(row[field]), 1)
            require(actual == expected_value, f"judge component mismatch for {component}/{field}: expected {expected_value}, got {actual}")

    pass_fail_disagreements = load_csv(pass_fail_disagreements_path)
    require(len(pass_fail_disagreements) == 1, f"expected one pass/fail disagreement, found {len(pass_fail_disagreements)}")
    row = pass_fail_disagreements[0]
    require(row["item_id"] == "es_en_SA_007", "unexpected judge pass/fail disagreement item")
    require(row["model"] == "gpt-4.1" and row["condition"] == "baseline", "unexpected judge pass/fail disagreement row")

    component_disagreements = load_csv(component_disagreements_path)
    require(len(component_disagreements) == 10, f"expected 10 component disagreements, found {len(component_disagreements)}")

    markdown = " ".join(markdown_path.read_text(encoding="utf-8").split())
    for phrase in (
        "not a native-speaker human audit",
        "71/72 (98.6%) | [92.5, 99.8]",
        "editing_preservation | 18 | 17/18 (94.4%)",
        "preservation | 69/72 (95.8%) | [88.5, 98.6]",
        "register_locale | 68/72 (94.4%) | [86.6, 97.8]",
        "required next step before stronger final claims",
    ):
        require(phrase in markdown, f"judge-agreement markdown missing phrase: {phrase}")


def check_judge_refresh(
    raw_path: Path,
    summary_path: Path,
    pairwise_path: Path,
    disagreements_path: Path,
    markdown_path: Path,
) -> None:
    rows = load_jsonl(raw_path)
    require(len(rows) == 72, f"expected 72 GPT-5.5 judge-refresh rows, found {len(rows)}")
    require(all(row["judge_model"] == "gpt-5.5" for row in rows), "judge refresh has unexpected judge model")
    require(all(not row.get("judge_parse_error") for row in rows), "judge refresh has parse errors")
    require(len({(row["item_id"], row["model"], row["condition"], int(row["turn"])) for row in rows}) == 72, "duplicate judge-refresh keys")
    agree = sum(bool(row["auto_pass"]) == bool(row["judge_pass"]) for row in rows)
    require(agree == 70, f"expected 70/72 GPT-5.5 judge agreement, got {agree}/72")
    disagreements = [row["item_id"] for row in rows if bool(row["auto_pass"]) != bool(row["judge_pass"])]
    require(disagreements == ["hi_en_SA_009", "hi_en_SC_008"], f"unexpected GPT-5.5 judge disagreements: {disagreements}")

    summary_rows = {row["judge_label"]: row for row in load_csv(summary_path)}
    require(set(summary_rows) == {"gpt41", "gpt55"}, f"unexpected judge-refresh summary rows: {set(summary_rows)}")
    require(int(summary_rows["gpt41"]["auto_agreement_n"]) == 71, "unexpected GPT-4.1 refresh summary agreement")
    require(int(summary_rows["gpt55"]["auto_agreement_n"]) == 70, "unexpected GPT-5.5 refresh summary agreement")
    require(int(summary_rows["gpt55"]["total_tokens"]) == 31047, "unexpected GPT-5.5 refresh token count")

    pairwise_rows = load_csv(pairwise_path)
    require(len(pairwise_rows) == 1, f"expected one judge-refresh pairwise row, found {len(pairwise_rows)}")
    pairwise = pairwise_rows[0]
    require(int(pairwise["pass_fail_agreement_n"]) == 69, "unexpected judge-to-judge agreement")
    require(int(pairwise["judge_a_pass_judge_b_fail_n"]) == 3, "unexpected judge-to-judge strictness count")
    require(int(pairwise["judge_a_fail_judge_b_pass_n"]) == 0, "unexpected judge-to-judge reverse disagreement count")

    disagreement_rows = {row["item_id"]: row for row in load_csv(disagreements_path)}
    require(set(disagreement_rows) == {"es_en_SA_007", "hi_en_SA_009", "hi_en_SC_008"}, f"unexpected judge-refresh disagreement rows: {set(disagreement_rows)}")
    require(disagreement_rows["es_en_SA_007"]["auto_pass"] == "False", "es_en_SA_007 should be auto fail")
    require(disagreement_rows["es_en_SA_007"]["gpt55_judge_pass"] == "False", "GPT-5.5 should reject es_en_SA_007")
    require(disagreement_rows["hi_en_SA_009"]["auto_pass"] == "True", "hi_en_SA_009 should be auto pass")
    require(disagreement_rows["hi_en_SA_009"]["gpt55_judge_pass"] == "False", "GPT-5.5 should reject hi_en_SA_009")
    require(disagreement_rows["hi_en_SC_008"]["auto_pass"] == "True", "hi_en_SC_008 should be auto pass")
    require(disagreement_rows["hi_en_SC_008"]["gpt55_judge_pass"] == "False", "GPT-5.5 should reject hi_en_SC_008")

    markdown = " ".join(markdown_path.read_text(encoding="utf-8").split())
    for phrase in (
        "`gpt-5.5` judge agrees on 70/72",
        "two judges agree with each other on 69/72",
        "Spanish framing around English rewrites should fail",
        "do not replace native/near-native validation",
    ):
        require(phrase in markdown, f"judge-refresh markdown missing phrase: {phrase}")


def check_repair_realism(summary_path: Path, paired_path: Path, markdown_path: Path) -> None:
    summary_rows = {row["repair_variant"]: row for row in load_csv(summary_path)}
    expected_summary = {
        "standard_saved": {"repair_success_n": 24, "repair_success_pct": 100.0},
        "terse_keep_english": {"repair_success_n": 24, "repair_success_pct": 100.0},
        "frustrated_dont_translate": {"repair_success_n": 17, "repair_success_pct": 70.8},
        "explicit_contract": {"repair_success_n": 5, "repair_success_pct": 20.8},
    }
    require(set(summary_rows) == set(expected_summary), f"unexpected repair-realism variants: {set(summary_rows)}")
    for variant, expected in expected_summary.items():
        row = summary_rows[variant]
        require(int(row["n"]) == 24, f"expected 24 rows for {variant}")
        require(int(row["repair_success_n"]) == expected["repair_success_n"], f"repair success mismatch for {variant}")
        require(round(float(row["repair_success_pct"]), 1) == expected["repair_success_pct"], f"repair success pct mismatch for {variant}")

    paired_rows = {row["comparison"]: row for row in load_csv(paired_path)}
    require(int(paired_rows["frustrated_dont_translate_minus_standard_saved"]["repair_success_worsened"]) == 7, "unexpected frustrated repair regression count")
    require(int(paired_rows["explicit_contract_minus_standard_saved"]["repair_success_worsened"]) == 19, "unexpected explicit repair regression count")

    markdown = " ".join(markdown_path.read_text(encoding="utf-8").split())
    for phrase in (
        "baseline editing-preservation first-turn failures",
        "standard | 24 | 24/24 (100.0%)",
        "frustrated | 24 | 17/24 (70.8%)",
        "explicit | 24 | 5/24 (20.8%)",
        "small interaction-realism diagnostic",
    ):
        require(phrase in markdown, f"repair-realism markdown missing phrase: {phrase}")


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_human_packet(packet_path: Path, key_path: Path) -> None:
    packet_rows = load_csv_rows(packet_path)
    key_rows = load_csv_rows(key_path)
    require(len(packet_rows) == 72, f"expected 72 human audit packet rows, found {len(packet_rows)}")
    require(len(key_rows) == 72, f"expected 72 human audit key rows, found {len(key_rows)}")
    require(not PACKET_PRIVATE_FIELDS.intersection(packet_rows[0].keys()), "human audit packet leaks private answer-key fields")
    for field in ANNOTATION_FIELDS:
        require(field in packet_rows[0], f"human audit packet missing annotation field {field}")
        require(all(row.get(field, "") == "" for row in packet_rows), f"human audit launch packet field {field} is not blank")
    packet_ids = [row["audit_id"] for row in packet_rows]
    key_ids = [row["audit_id"] for row in key_rows]
    require(len(packet_ids) == len(set(packet_ids)), "duplicate audit ids in packet")
    require(set(packet_ids) == set(key_ids), "packet and key audit ids differ")
    counts = Counter((row["language_pair"], row["task_family"]) for row in packet_rows)
    require(dict(counts) == EXPECTED_HUMAN_PACKET_COUNTS, f"unexpected human audit packet counts: {counts}")
    key_strata = Counter((row["model"], row["condition"], row["task_family"], row["language_pair"]) for row in key_rows)
    require(len(key_strata) == 72, f"expected one row per model/condition/family/language stratum, found {len(key_strata)}")
    require(all(count == 1 for count in key_strata.values()), f"human audit key not balanced: {key_strata}")
    out_dir = packet_path.parent
    for language_pair in ("ar-en", "es-en", "hi-en"):
        slice_path = out_dir / f"human_audit_packet_v0.2_{language_pair}.csv"
        require(slice_path.exists(), f"missing human audit slice {slice_path}")
        slice_rows = load_csv_rows(slice_path)
        full_rows = [row for row in packet_rows if row["language_pair"] == language_pair]
        require(slice_rows == full_rows, f"human audit slice {language_pair} does not match full packet subset")
    manifest_path = out_dir / "audit_manifest_v0.2.md"
    require(manifest_path.exists(), f"missing human audit manifest {manifest_path}")
    manifest = manifest_path.read_text(encoding="utf-8")
    require("Strong final paper claims should wait" in manifest, "human audit manifest missing claim-boundary warning")
    launch_checklist_path = out_dir / "human_audit_launch_checklist_v0.2.md"
    require(launch_checklist_path.exists(), f"missing human audit launch checklist {launch_checklist_path}")
    launch_checklist = launch_checklist_path.read_text(encoding="utf-8")
    require("Do not claim native-speaker or human validation" in launch_checklist, "human audit launch checklist missing claim warning")
    require("validate_completed_human_audit.py" in launch_checklist, "human audit launch checklist missing completion validator")
    roster_template_path = out_dir / "human_audit_annotator_roster_template_v0.2.csv"
    require(roster_template_path.exists(), f"missing human audit annotator roster template {roster_template_path}")
    roster_rows = load_csv_rows(roster_template_path)
    require(len(roster_rows) == 6, f"expected 6 annotator roster template rows, found {len(roster_rows)}")
    require(
        Counter(row["language_pair"] for row in roster_rows) == Counter({"ar-en": 2, "es-en": 2, "hi-en": 2}),
        "human audit annotator roster template must cover two slots per language pair",
    )
    roster_ids = [row["annotator_id"] for row in roster_rows]
    require(len(roster_ids) == len(set(roster_ids)), "human audit annotator roster template IDs must be unique")
    require(all(annotator_id.startswith("replace_with_") for annotator_id in roster_ids), "human audit annotator roster template should use placeholder IDs")


def check_human_audit_design(
    summary_path: Path,
    by_language_path: Path,
    by_family_path: Path,
    by_model_condition_path: Path,
    by_failure_type_path: Path,
    markdown_path: Path,
) -> None:
    summary_rows = load_csv_rows(summary_path)
    require(len(summary_rows) == 1, f"expected one human-audit design summary row, found {len(summary_rows)}")
    summary = summary_rows[0]
    expected_summary = {
        "packet_rows": "72",
        "answer_key_rows": "72",
        "language_pairs": "3",
        "task_families": "4",
        "models": "3",
        "conditions": "2",
        "model_condition_language_family_strata": "72",
        "first_turn_only": "True",
        "packet_private_fields_present": "False",
        "annotation_fields_blank": "True",
        "auto_pass_rows": "57",
        "auto_fail_rows": "15",
        "auto_pass_rate": "0.7917",
    }
    for field, expected in expected_summary.items():
        require(summary.get(field) == expected, f"human-audit design summary mismatch for {field}: {summary.get(field)}")

    expected_language = {
        "ar-en": {"n": 24, "auto_pass_n": 16, "auto_fail_n": 8, "auto_pass_rate": 0.6667},
        "es-en": {"n": 24, "auto_pass_n": 18, "auto_fail_n": 6, "auto_pass_rate": 0.75},
        "hi-en": {"n": 24, "auto_pass_n": 23, "auto_fail_n": 1, "auto_pass_rate": 0.9583},
    }
    by_language = {row["language_pair"]: row for row in load_csv_rows(by_language_path)}
    require(set(by_language) == set(expected_language), f"unexpected human-audit design language rows: {set(by_language)}")
    for language_pair, expected in expected_language.items():
        row = by_language[language_pair]
        for field, expected_value in expected.items():
            actual = round(float(row[field]), 4) if field == "auto_pass_rate" else int(row[field])
            require(actual == expected_value, f"human-audit design language mismatch for {language_pair}/{field}")

    expected_family = {
        "editing_preservation": {"n": 18, "auto_pass_n": 9, "auto_fail_n": 9, "auto_pass_rate": 0.5},
        "output_language_inference": {"n": 18, "auto_pass_n": 18, "auto_fail_n": 0, "auto_pass_rate": 1.0},
        "quote_preservation": {"n": 18, "auto_pass_n": 16, "auto_fail_n": 2, "auto_pass_rate": 0.8889},
        "script_register_locale": {"n": 18, "auto_pass_n": 14, "auto_fail_n": 4, "auto_pass_rate": 0.7778},
    }
    by_family = {row["task_family"]: row for row in load_csv_rows(by_family_path)}
    require(set(by_family) == set(expected_family), f"unexpected human-audit design family rows: {set(by_family)}")
    for family, expected in expected_family.items():
        row = by_family[family]
        for field, expected_value in expected.items():
            actual = round(float(row[field]), 4) if field == "auto_pass_rate" else int(row[field])
            require(actual == expected_value, f"human-audit design family mismatch for {family}/{field}")

    expected_model_condition = {
        ("gpt-4.1", "baseline"): {"n": 12, "auto_pass_n": 10, "auto_fail_n": 2, "auto_pass_rate": 0.8333},
        ("gpt-4.1", "contract"): {"n": 12, "auto_pass_n": 11, "auto_fail_n": 1, "auto_pass_rate": 0.9167},
        ("gpt-4.1-mini", "baseline"): {"n": 12, "auto_pass_n": 10, "auto_fail_n": 2, "auto_pass_rate": 0.8333},
        ("gpt-4.1-mini", "contract"): {"n": 12, "auto_pass_n": 8, "auto_fail_n": 4, "auto_pass_rate": 0.6667},
        ("gpt-4.1-nano", "baseline"): {"n": 12, "auto_pass_n": 9, "auto_fail_n": 3, "auto_pass_rate": 0.75},
        ("gpt-4.1-nano", "contract"): {"n": 12, "auto_pass_n": 9, "auto_fail_n": 3, "auto_pass_rate": 0.75},
    }
    by_model_condition = {(row["model"], row["condition"]): row for row in load_csv_rows(by_model_condition_path)}
    require(set(by_model_condition) == set(expected_model_condition), "unexpected human-audit design model/condition rows")
    for key, expected in expected_model_condition.items():
        row = by_model_condition[key]
        for field, expected_value in expected.items():
            actual = round(float(row[field]), 4) if field == "auto_pass_rate" else int(row[field])
            require(actual == expected_value, f"human-audit design model/condition mismatch for {key}/{field}")

    expected_failure_types = {
        "preservation_failure": 6,
        "script_mismatch": 4,
        "task_noncompletion": 11,
        "wrong_output_language": 9,
    }
    by_failure_type = {row["auto_failure_type"]: row for row in load_csv_rows(by_failure_type_path)}
    require(set(by_failure_type) == set(expected_failure_types), f"unexpected human-audit design failure types: {set(by_failure_type)}")
    for failure_type, expected_count in expected_failure_types.items():
        row = by_failure_type[failure_type]
        require(int(row["sampled_failure_rows_with_type"]) == expected_count, f"human-audit design failure-count mismatch for {failure_type}")
        require(int(row["sampled_auto_fail_rows"]) == 15, f"human-audit design sampled-fail denominator mismatch for {failure_type}")

    markdown = " ".join(markdown_path.read_text(encoding="utf-8").split())
    for phrase in (
        "design-readiness audit only; it is not completed human validation",
        "model_condition_language_family_strata | 72",
        "auto_pass_rows | 57",
        "ar-en | 24 | 16 | 8",
        "editing_preservation | 18 | 9 | 9",
        "preservation_failure | 6 | 15",
        "Completed native/near-native annotation is still required",
    ):
        require(phrase in markdown, f"human-audit design markdown missing phrase: {phrase}")


def check_coverage_native_review(
    packet_path: Path,
    roster_path: Path,
    summary_path: Path,
    by_slice_path: Path,
    markdown_path: Path,
) -> None:
    review_fields = (
        "reviewer_id",
        "reviewer_prompt_clear",
        "reviewer_target_language_natural",
        "reviewer_script_expectation_valid",
        "reviewer_preservation_spans_valid",
        "reviewer_known_bad_outputs_valid",
        "reviewer_release_usable",
        "reviewer_issue_types",
        "reviewer_notes",
    )
    expected_slices = {
        "arabic_instruction_arabic_filenames",
        "english_instruction_arabic_content",
        "english_instruction_hindi_content",
        "english_instruction_spanish_content",
        "hindi_english_instruction_hindi_devanagari",
        "spanish_instruction_arabic_quote",
    }
    packet_rows = load_csv_rows(packet_path)
    require(len(packet_rows) == 60, f"expected 60 v0.3 native-review rows, found {len(packet_rows)}")
    require({row["coverage_slice"] for row in packet_rows} == expected_slices, "unexpected v0.3 native-review slices")
    counts = Counter(row["coverage_slice"] for row in packet_rows)
    require(all(count == 10 for count in counts.values()), f"unexpected v0.3 native-review slice counts: {counts}")
    require(all(row["task_family"] == "editing_preservation" for row in packet_rows), "v0.3 native-review rows should all be editing_preservation")
    for field in review_fields:
        require(field in packet_rows[0], f"v0.3 native-review packet missing review field {field}")
        require(all(row.get(field, "") == "" for row in packet_rows), f"v0.3 native-review field {field} is not blank")
    for field in ("must_preserve_spans", "required_any_markers", "forbidden_markers", "known_bad_outputs"):
        require(all(json.loads(row[field]) for row in packet_rows), f"v0.3 native-review field {field} has empty JSON lists")

    roster_rows = load_csv_rows(roster_path)
    require(len(roster_rows) == 12, f"expected twelve v0.3 roster template rows, found {len(roster_rows)}")
    require({row["coverage_slice"] for row in roster_rows} == expected_slices, "v0.3 roster template slice mismatch")
    roster_counts = Counter(row["coverage_slice"] for row in roster_rows)
    require(all(count == 2 for count in roster_counts.values()), f"v0.3 roster template should have two reviewer slots per slice: {roster_counts}")
    require(all(row["reviewer_id"].startswith("replace_with_") for row in roster_rows), "v0.3 roster template should use placeholder reviewer IDs")

    summary_rows = load_csv_rows(summary_path)
    require(len(summary_rows) == 1, "expected one v0.3 native-review summary row")
    expected_summary = {
        "review_rows": "60",
        "coverage_slices": "6",
        "language_pairs": "6",
        "instruction_languages": "4",
        "content_languages": "4",
        "task_families": "1",
        "rows_per_slice_min": "10",
        "rows_per_slice_max": "10",
        "review_fields_blank": "True",
        "rows_requiring_native_review": "60",
        "validation_status": "launch_ready_but_not_completed_native_validation",
    }
    for field, expected in expected_summary.items():
        require(summary_rows[0].get(field) == expected, f"v0.3 native-review summary mismatch for {field}")

    by_slice = {row["coverage_slice"]: row for row in load_csv_rows(by_slice_path)}
    require(set(by_slice) == expected_slices, "v0.3 native-review by-slice table mismatch")
    require(all(int(row["n"]) == 10 for row in by_slice.values()), "v0.3 native-review by-slice rows should all be 10")
    require(all(int(row["total_preservation_spans"]) == 20 for row in by_slice.values()), "v0.3 native-review by-slice preservation spans should all be 20")

    markdown = " ".join(markdown_path.read_text(encoding="utf-8").split())
    for phrase in (
        "60 synthetic v0.3 rows",
        "launch-ready but not completed native validation",
        "Do not claim native validation has been completed",
        "Completed reviewer labels and a qualified roster are still required",
    ):
        require(phrase in markdown, f"v0.3 native-review design markdown missing phrase: {phrase}")


def check_human_completion_plan(path: Path) -> None:
    require(path.exists(), f"missing human audit completion plan {path}")
    text = path.read_text(encoding="utf-8")
    required_phrases = [
        "Prepared but not completed",
        "scripts/validate_completed_human_audit.py",
        "SMOKE ONLY",
        "annotator roster",
        "near-native",
        "Do not say:",
        "the benchmark is fully human-validated",
    ]
    for phrase in required_phrases:
        require(phrase in text, f"human audit completion plan missing phrase: {phrase}")


def check_discovery(summary_path: Path, hit_metadata_path: Path) -> None:
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    require(summary["dataset"] == "allenai/WildChat", f"unexpected discovery dataset: {summary['dataset']}")
    require(summary["conversations_scanned"] == 20000, "unexpected discovery conversation count")
    require(summary["user_turns_scanned"] == 58764, "unexpected discovery user-turn count")
    require(summary["multiturn_conversations"] == 10681, "unexpected discovery multiturn count")
    require(summary["conversations_with_repair_cues"] == 172, "unexpected discovery repair-cue conversation count")
    require(summary["cue_hits_total"] == 219, "unexpected discovery cue hit count")
    require(summary["raw_text_written"] is False, "discovery summary says raw text was written")
    expected_categories = {
        "generic_repair": 93,
        "preservation_failure": 25,
        "register_locale_mismatch": 16,
        "script_mismatch": 4,
        "unwanted_translation": 13,
        "wrong_output_language": 68,
    }
    require(summary["category_counts"] == expected_categories, f"unexpected discovery categories: {summary['category_counts']}")
    hit_rows = load_csv_rows(hit_metadata_path)
    require(len(hit_rows) == 219, f"expected 219 hashed discovery hit rows, found {len(hit_rows)}")
    forbidden_raw_fields = {"text", "content", "user_prompt", "assistant_response"}
    require(not forbidden_raw_fields.intersection(hit_rows[0].keys()), "hashed discovery metadata contains raw-text-like fields")


def check_discovery_cue_analysis(
    overview_path: Path,
    category_path: Path,
    pattern_path: Path,
    repeated_path: Path,
    markdown_path: Path,
) -> None:
    overview_rows = load_csv_rows(overview_path)
    require(len(overview_rows) == 1, f"expected one discovery overview row, found {len(overview_rows)}")
    overview = overview_rows[0]
    expected_overview = {
        "conversations_scanned": 20000,
        "user_turns_scanned": 58764,
        "multiturn_conversations": 10681,
        "conversations_with_repair_cues": 172,
        "cue_hits_total": 219,
        "metadata_rows": 219,
        "unique_conversations_in_metadata": 172,
        "repeated_cue_conversations": 31,
        "max_cue_hits_in_conversation": 5,
    }
    for field, expected in expected_overview.items():
        require(int(overview[field]) == expected, f"discovery cue overview mismatch for {field}: expected {expected}, got {overview[field]}")
    require(overview["raw_text_written"] == "False", "discovery cue overview says raw text was written")

    category_rows = load_csv_rows(category_path)
    expected_categories = {
        "generic_repair": {"cue_hits": 93, "unique_conversations": 81},
        "preservation_failure": {"cue_hits": 25, "unique_conversations": 18},
        "register_locale_mismatch": {"cue_hits": 16, "unique_conversations": 13},
        "script_mismatch": {"cue_hits": 4, "unique_conversations": 2},
        "unwanted_translation": {"cue_hits": 13, "unique_conversations": 13},
        "wrong_output_language": {"cue_hits": 68, "unique_conversations": 48},
    }
    require(len(category_rows) == len(expected_categories), f"unexpected discovery category rows: {len(category_rows)}")
    by_category = {row["category"]: row for row in category_rows}
    for category, expected in expected_categories.items():
        require(category in by_category, f"missing discovery category {category}")
        row = by_category[category]
        for field, expected_value in expected.items():
            require(int(row[field]) == expected_value, f"discovery category mismatch for {category}/{field}")

    pattern_rows = load_csv_rows(pattern_path)
    require(len(pattern_rows) >= 12, "discovery cue pattern table unexpectedly short")
    top_patterns = {(row["category"], row["cue_pattern"]): int(row["cue_hits"]) for row in pattern_rows[:12]}
    require(top_patterns[("generic_repair", r"\bi meant\b")] == 52, "unexpected top generic repair cue count")
    require(top_patterns[("wrong_output_language", r"\bin english\b")] == 47, "unexpected top wrong-language cue count")
    require(top_patterns[("script_mismatch", r"\bromanized\b")] == 4, "unexpected script cue count")

    repeated_rows = load_csv_rows(repeated_path)
    require(len(repeated_rows) == 31, f"expected 31 repeated-cue conversations, found {len(repeated_rows)}")
    require(max(int(row["cue_hits"]) for row in repeated_rows) == 5, "unexpected max repeated cue count")
    forbidden_raw_fields = {"text", "content", "user_prompt", "assistant_response"}
    require(not forbidden_raw_fields.intersection(repeated_rows[0].keys()), "repeated cue metadata contains raw-text-like fields")

    markdown = " ".join(markdown_path.read_text(encoding="utf-8").split())
    for phrase in (
        "writes no raw user or assistant text",
        "must not be interpreted as a representative prevalence estimate",
        "generic_repair | 93 | 81",
        "wrong_output_language | 68 | 48",
        "31 hashed conversations contain two or more cue hits",
        "maximum is 5 cue hits",
        "result should be treated only as motivation for the benchmark taxonomy",
    ):
        require(phrase in markdown, f"discovery cue analysis markdown missing phrase: {phrase}")


def check_figures(paths: list[Path]) -> None:
    for path in paths:
        require(path.exists(), f"missing figure {path}")
        require(path.stat().st_size > 1000, f"figure too small: {path}")


def check_figure_sources(ftga_source: Path, repair_source: Path) -> None:
    expected = {
        ("gpt-4.1-nano", "baseline", "67.5"),
        ("gpt-4.1-nano", "contract", "76.7"),
        ("gpt-4.1-mini", "baseline", "75.8"),
        ("gpt-4.1-mini", "contract", "79.2"),
        ("gpt-4.1", "baseline", "76.7"),
        ("gpt-4.1", "contract", "93.3"),
        ("gpt-5.4-mini", "baseline", "80.0"),
        ("gpt-5.4-mini", "contract", "85.0"),
        ("gpt-5.5", "baseline", "81.7"),
        ("gpt-5.5", "contract", "98.3"),
    }
    ftga_rows = load_csv_rows(ftga_source)
    actual = {(row["model"], row["condition"], row["ftga_pct"]) for row in ftga_rows}
    require(actual == expected, f"unexpected FTGA figure source rows: {actual}")
    require(all(row["n"] == "120" for row in ftga_rows), "FTGA figure source should use full 120-item runs")

    repair_rows = load_csv_rows(repair_source)
    repair_keys = {(row["model"], row["condition"]) for row in repair_rows}
    require(
        repair_keys == {(model, condition) for model, condition, _ in expected},
        "repair-curve source missing full-run rows",
    )
    require(all(row["n"] == "120" for row in repair_rows), "repair-curve source should use full 120-item runs")
    g55_contract = next(row for row in repair_rows if row["model"] == "gpt-5.5" and row["condition"] == "contract")
    require(
        g55_contract["solved_after_two_repairs_pct"] == "100.0",
        "GPT-5.5 contract repair curve should solve all trajectories",
    )


def check_pdf(path: Path) -> None:
    require(path.exists(), f"missing PDF {path}")
    require(path.stat().st_size > 1000, f"PDF too small: {path}")
    try:
        proc = subprocess.run(["pdfinfo", str(path)], check=True, text=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise AssertionError(f"pdfinfo failed for {path}: {exc}") from exc
    match = re.search(r"^Pages:\s+(\d+)$", proc.stdout, flags=re.MULTILINE)
    require(match is not None, "pdfinfo did not report page count")
    require(int(match.group(1)) == 10, f"expected 10-page PDF, got {match.group(1)}")


def check_tex_log(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    bad = re.findall(r"Warning|undefined|Overfull|Underfull|Error", text)
    require(not bad, f"TeX log contains warning/error markers: {bad[:5]}")


def check_claim_checklist(path: Path) -> None:
    require(path.exists(), f"missing claim-evidence checklist {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required_phrases = [
        "Safe Main Claim",
        "Claims Not Supported Yet",
        "native-speaker validation remains necessary",
        "Do not claim cross-provider generality",
        "the paper-facing result is the completed 120-item v0.2 evaluation",
        "scripts/validate_paper_claims.py",
        "scripts/analyze_failure_modes.py",
        "scripts/analyze_prompt_control.py",
        "scripts/analyze_prompt_ablation.py",
        "content-preservation ablation performs better",
        "scripts/build_error_atlas.py",
        "scripts/analyze_task_useful_failures.py",
        "scripts/analyze_human_audit_design.py",
        "57 auto-pass and 15 auto-fail sampled rows",
        "paper/label_collection_launch_pack_v02.md",
        "scripts/validate_coverage_native_review_packet_v03.py",
        "scripts/validate_coverage_native_review_sheets_v03.py",
        "scripts/validate_completed_coverage_native_review_v03.py",
        "scripts/test_coverage_native_review_adjudication.py",
        "not completed native validation",
        "scripts/validate_qualitative_examples.py",
        "scripts/validate_completed_human_audit.py",
        "scripts/validate_human_audit_packet.py",
        "scripts/validate_human_audit_threshold_rationale.py",
        "scripts/validate_followup_probe.py",
        "scripts/validate_label_collection_launch_pack.py",
        "scripts/validate_label_collection_dispatch.py",
        "scripts/validate_label_collection_operator_handoff.py",
        "paper/label_return_preflight_v02.md",
        "scripts/validate_label_return_preflight.py",
        "paper/reviewer_qualification_requirements_v02.md",
        "scripts/validate_reviewer_qualification_requirements.py",
        "scripts/validate_label_collection_priority.py",
        "scripts/validate_all_model_paired_significance.py",
        "scripts/validate_all_model_uncertainty.py",
        "scripts/validate_balanced_subsample_robustness.py",
        "scripts/validate_contract_benefit_decomposition.py",
        "scripts/validate_prompt_family_scorecard.py",
        "paper/reviewer_concern_audit_v02.md",
        "scripts/validate_reviewer_concern_audit_v02.py",
        "paper/submission_anonymity_v02.md",
        "scripts/validate_submission_anonymity_v02.py",
        "scripts/test_api_key_loading.py",
        "zero local path, repository-owner, or API-secret text matches",
        "paper/submission_decision_v02.md",
        "scripts/validate_submission_decision_v02.py",
        "submit conservatively if labels are unavailable",
        "completed qualified labels are absent",
    ]
    for phrase in required_phrases:
        require(phrase in normalized, f"claim-evidence checklist missing required phrase: {phrase}")


def check_extended_abstract(path: Path) -> None:
    require(path.exists(), f"missing extended abstract draft {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required_phrases = [
        "Token tax",
        "1.69x",
        "1.34x",
        "1.43x",
        "1.27x",
        "1.13x",
        "| gpt-5.4-mini | baseline | 80.0% | 0.25 | 1.38x | 2.5% | 87.5% | 87.5% |",
        "| gpt-5.4-mini | contract | 85.0% | 0.25 | 1.24x | 5.0% | 66.7% | 66.7% |",
        "| gpt-5.5 | baseline | 81.7% | 0.23 | 1.28x | 1.7% | 86.4% | 90.9% |",
        "| gpt-5.5 | contract | 98.3% | 0.02 | 1.02x | 0.0% | 100.0% | 100.0% |",
        "full 120-item current-model refreshes for",
        "`gpt-5.4-mini` and `gpt-5.5` under the same baseline and contract conditions",
        "paired `gpt-5.5` judge refresh on the same 72 rows",
        "two first-turn residuals remain",
        "all trajectories resolve within the two-repair budget",
        "reduces mean repair turns and token tax",
        "72-row stratified blinded LLM-judge audit of the GPT-4.1-family first-turn surface",
        "Deterministic scorer stress tests fail 390/390 known-bad probes",
        "accept 120/120 constrained positive-control templates",
        "native-speaker validation remains launch-ready but incomplete",
        "should be audited by native speakers before any stronger native-validation or cultural-appropriateness claim",
        "GPT-4.1-family error atlas lists 157 first-turn failures",
        "under the contract, `gpt-5.5` leaves two first-turn failures and zero unresolved trajectories",
        "`gpt-5.4-mini` leaves 18 first-turn failures and six unresolved trajectories",
    ]
    for phrase in required_phrases:
        require(phrase in text or phrase in normalized, f"extended abstract missing required phrase: {phrase}")
    stale_phrases = [
        "A 10% stratified blinded LLM-judge audit",
        "The generated error atlas lists 157 first-turn failures overall",
        "locale judgments should be audited by native speakers before submission",
    ]
    for phrase in stale_phrases:
        require(phrase not in text and phrase not in normalized, f"extended abstract still contains stale phrase: {phrase}")


def check_appendix(path: Path) -> None:
    require(path.exists(), f"missing appendix {path}")
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required_phrases = [
        "Judge refresh analysis: `scripts/analyze_judge_refresh.py`",
        "Judge refresh validator: `scripts/validate_judge_refresh.py`",
        "same blinded 72-row sample",
        "--judge-model gpt-5.5",
        "conda run -n reprompt_tax python scripts/analyze_judge_refresh.py",
        "conda run -n reprompt_tax python scripts/validate_judge_refresh.py",
        "`gpt-5.5` judge agrees with the automatic scorer on",
        "70/72 sampled pass/fail labels",
        "with the `gpt-4.1` judge on 69/72 labels",
    ]
    for phrase in required_phrases:
        require(phrase in text or phrase in normalized, f"appendix missing required phrase: {phrase}")


def check_related_work(tex_path: Path, refs_path: Path) -> None:
    tex = read_tex_surface(tex_path)
    normalized_tex = " ".join(tex.split())
    refs = refs_path.read_text(encoding="utf-8")
    required_tex_phrases = [
        "MMLU-ProX",
        "BenchMAX",
        "M-IFEval",
        "MT-Bench",
        "StructFlowBench",
        "MultiChallenge",
        "interactional cost of recovery",
        "standardized repairs are needed",
        "script, preservation, register, and locale",
        "recovery cost after a multilingual contract violation",
        "xuan2025mmluprox",
        "huang2025benchmax",
        "dussolle2025mifeval",
        "zheng2023mtbench",
        "li2025structflowbench",
        "sirdeshmukh2025multichallenge",
    ]
    required_bib_keys = [
        "xuan2025mmluprox",
        "huang2025benchmax",
        "dussolle2025mifeval",
        "oh2026ola",
        "zheng2023mtbench",
        "li2025structflowbench",
        "sirdeshmukh2025multichallenge",
    ]
    for phrase in required_tex_phrases:
        require(phrase in normalized_tex, f"main TeX related work missing phrase: {phrase}")
    for key in required_bib_keys:
        require(key in refs, f"refs.bib missing related-work key: {key}")


def check_related_work_positioning(path: Path) -> None:
    require(path.exists(), f"missing related-work positioning note {path}")
    text = path.read_text(encoding="utf-8")
    required_phrases = [
        "Positioning Matrix",
        "Safe Novelty Claim",
        "MMLU-ProX",
        "BenchMAX",
        "M-IFEval",
        "OLA",
        "MT-Bench",
        "Chatbot Arena",
        "StructFlowBench",
        "MultiChallenge",
        "standardized repair protocol",
        "repair trajectory after constraint failures",
        "GPT-5.x refresh makes the result timely",
        "current-model refreshes for `gpt-5.4-mini` and `gpt-5.5`",
        "repair-realism checks",
        "two blinded LLM-judge audits",
        "launch-ready human/native review protocols",
        "`gpt-5.4-mini` regression-risk caveat",
        "token-tax versus absolute-token distinction",
        "Native-speaker validation is still required",
    ]
    for phrase in required_phrases:
        require(phrase in text, f"related-work positioning note missing phrase: {phrase}")


def check_auxiliary_validator(root: Path, script_name: str, expected_stdout: str, script_args: list[str] | None = None) -> None:
    script_path = (root / script_name).resolve()
    require(script_path.exists(), f"missing auxiliary validator {script_path}")
    try:
        proc = subprocess.run(
            [sys.executable, str(script_path), *(script_args or [])],
            cwd=root,
            check=True,
            text=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        raise AssertionError(
            f"{script_name} failed:\n"
            f"stdout:\n{exc.stdout}\n"
            f"stderr:\n{exc.stderr}"
        ) from exc
    require(expected_stdout in proc.stdout, f"{script_name} did not report success")


def check_qualitative_examples(root: Path) -> None:
    script_path = (root / "scripts/validate_qualitative_examples.py").resolve()
    require(script_path.exists(), f"missing qualitative example validator {script_path}")
    try:
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=root,
            check=True,
            text=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        raise AssertionError(
            "qualitative example validator failed:\n"
            f"stdout:\n{exc.stdout}\n"
            f"stderr:\n{exc.stderr}"
        ) from exc
    require("qualitative example validation passed" in proc.stdout, "qualitative example validator did not report success")


def check_score_regressions(root: Path) -> None:
    script_path = (root / "scripts/test_score_auto.py").resolve()
    require(script_path.exists(), f"missing score regression script {script_path}")
    try:
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=root,
            check=True,
            text=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        raise AssertionError(
            "score regression tests failed:\n"
            f"stdout:\n{exc.stdout}\n"
            f"stderr:\n{exc.stderr}"
        ) from exc
    require("score-auto regression tests passed" in proc.stdout, "score regression tests did not report success")


def check_claim_boundary_lint(root: Path) -> None:
    script_path = (root / "scripts/lint_claim_boundaries.py").resolve()
    require(script_path.exists(), f"missing claim-boundary lint script {script_path}")
    try:
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=root,
            check=True,
            text=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        raise AssertionError(
            "claim-boundary lint failed:\n"
            f"stdout:\n{exc.stdout}\n"
            f"stderr:\n{exc.stderr}"
        ) from exc
    require("claim-boundary lint passed" in proc.stdout, "claim-boundary lint did not report success")


def check_artifact_manifest(root: Path) -> None:
    script_path = (root / "scripts/make_artifact_manifest.py").resolve()
    require(script_path.exists(), f"missing artifact manifest script {script_path}")
    try:
        proc = subprocess.run(
            [sys.executable, str(script_path), "--check"],
            cwd=root,
            check=True,
            text=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        raise AssertionError(
            "artifact manifest validation failed:\n"
            f"stdout:\n{exc.stdout}\n"
            f"stderr:\n{exc.stderr}"
        ) from exc
    require("artifact manifest validation passed" in proc.stdout, "artifact manifest validator did not report success")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()

    check_stress_benchmark(root / "data/benchmark_stress_v0.2.jsonl")
    check_benchmark_quality(
        root / "results/tables/benchmark_quality_v02/benchmark_quality_summary.csv",
        root / "results/tables/benchmark_quality_v02/benchmark_quality_by_family.csv",
        root / "results/tables/benchmark_quality_v02/benchmark_quality_by_language_family.csv",
        root / "paper/benchmark_quality_audit_v02.md",
    )
    check_experiment_ledger(
        root / "results/tables/experiment_ledger_v02/experiment_ledger_summary.csv",
        root / "results/tables/experiment_ledger_v02/api_usage_by_artifact.csv",
        root / "results/tables/experiment_ledger_v02/api_usage_by_model_condition.csv",
        root / "results/tables/experiment_ledger_v02/api_usage_by_judge.csv",
        root / "results/tables/experiment_ledger_v02/api_usage_by_repair_variant.csv",
        root / "paper/experiment_ledger_v02.md",
    )
    check_metrics(root / "results/tables/openai_three_model_stress_v02_full120/metrics_summary.csv", root / "paper/main.tex")
    check_current_model_table(root / "paper/main.tex")
    check_paired_effects(root / "results/tables/openai_three_model_stress_v02_full120/paired_contract_effects_by_model.csv", root / "paper/main.tex")
    check_paired_significance(
        root / "results/tables/openai_three_model_stress_v02_full120/paired_significance_by_model.csv",
        root / "paper/paired_significance_v02_full120.md",
    )
    check_language_slices(
        root / "results/tables/openai_three_model_stress_v02_full120/language_slice_metrics.csv",
        root / "results/tables/openai_three_model_stress_v02_full120/language_slice_paired_effects.csv",
        root / "results/tables/openai_three_model_stress_v02_full120/language_slice_aggregate_effects.csv",
        root / "paper/language_slice_analysis_v02_full120.md",
    )
    check_repair_dynamics(
        root / "results/tables/openai_three_model_stress_v02_full120/repair_dynamics_by_model_condition.csv",
        root / "results/tables/openai_three_model_stress_v02_full120/repair_dynamics_by_family_condition.csv",
        root / "results/tables/openai_three_model_stress_v02_full120/repair_paired_effects_by_model.csv",
        root / "results/tables/openai_three_model_stress_v02_full120/repair_rtt_transition_by_model.csv",
        root / "paper/repair_dynamics_v02_full120.md",
    )
    check_prompt_control(
        root / "results/tables/openai_nano_stress_v02_full120_prompt_control/prompt_control_summary.csv",
        root / "results/tables/openai_nano_stress_v02_full120_prompt_control/prompt_control_paired_effects.csv",
        root / "paper/prompt_control_analysis.md",
        root / "prompts/generic_helpfulness_system.txt",
    )
    check_prompt_ablation(
        root / "results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_summary.csv",
        root / "results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_by_family.csv",
        root / "results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_paired_effects.csv",
        root / "results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_contract_vs_content_by_family.csv",
        root / "results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_contract_vs_content_by_language.csv",
        root / "results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_contract_vs_content_examples.csv",
        root / "results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_contract_vs_content_items.csv",
        root / "paper/prompt_ablation_analysis.md",
        root / "prompts/content_preservation_system.txt",
    )
    check_token_burden(
        root / "results/tables/openai_three_model_stress_v02_full120/token_burden_by_model.csv",
        root / "results/tables/openai_three_model_stress_v02_full120/token_burden_paired_effects_by_model.csv",
        root / "paper/token_burden_analysis_v02_full120.md",
    )
    check_failure_mode_analysis(
        family_summary_path=root / "results/tables/openai_three_model_stress_v02_full120/family_effect_summary.csv",
        failure_summary_path=root / "results/tables/openai_three_model_stress_v02_full120/failure_type_summary.csv",
        markdown_path=root / "paper/failure_mode_analysis_v02_full120.md",
        tex_path=root / "paper/main.tex",
    )
    check_item_consistency(
        root / "results/tables/openai_three_model_stress_v02_full120/item_consistency_summary.csv",
        root / "results/tables/openai_three_model_stress_v02_full120/item_consistency_by_family.csv",
        root / "results/tables/openai_three_model_stress_v02_full120/item_consistency_hardest_items.csv",
        root / "paper/item_consistency_analysis_v02_full120.md",
    )
    check_component_breakdown(
        root / "results/tables/openai_three_model_stress_v02_full120/component_pass_by_model_condition.csv",
        root / "results/tables/openai_three_model_stress_v02_full120/component_pass_by_family_condition.csv",
        root / "results/tables/openai_three_model_stress_v02_full120/component_paired_effects_by_model.csv",
        root / "paper/component_breakdown_v02_full120.md",
    )
    check_scorer_ablation(
        root / "results/tables/openai_three_model_stress_v02_full120/scorer_ablation_by_condition.csv",
        root / "results/tables/openai_three_model_stress_v02_full120/scorer_ablation_by_family_condition.csv",
        root / "results/tables/openai_three_model_stress_v02_full120/scorer_ablation_failure_signatures.csv",
        root / "paper/scorer_ablation_sensitivity_v02_full120.md",
    )
    check_task_useful_failures(
        root / "results/tables/openai_three_model_stress_v02_full120/task_useful_failure_by_condition.csv",
        root / "results/tables/openai_three_model_stress_v02_full120/task_useful_failure_by_family_condition.csv",
        root / "results/tables/openai_three_model_stress_v02_full120/task_useful_failure_signatures.csv",
        root / "paper/task_useful_failure_analysis_v02_full120.md",
        root / "paper/main.tex",
    )
    check_error_atlas(
        root / "results/tables/openai_three_model_stress_v02_full120/first_turn_error_atlas.csv",
        root / "paper/error_atlas_v02_full120.md",
    )
    check_judge_audit(root / "results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl")
    check_judge_agreement(
        root / "results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_agreement_summary.csv",
        root / "results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_agreement_by_family.csv",
        root / "results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_component_agreement.csv",
        root / "results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_pass_fail_disagreements.csv",
        root / "results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_component_disagreements.csv",
        root / "paper/judge_agreement_analysis_v02_full120.md",
    )
    check_judge_refresh(
        root / "results/scores/openai_three_model_stress_v02_full120_judge_gpt55_audit72.jsonl",
        root / "results/tables/openai_three_model_stress_v02_full120_judge_refresh_gpt55/judge_refresh_summary.csv",
        root / "results/tables/openai_three_model_stress_v02_full120_judge_refresh_gpt55/judge_refresh_pairwise_comparison.csv",
        root / "results/tables/openai_three_model_stress_v02_full120_judge_refresh_gpt55/judge_refresh_disagreements.csv",
        root / "paper/judge_refresh_gpt55_v02_full120.md",
    )
    check_repair_realism(
        root / "results/tables/openai_three_model_stress_v02_repair_realism_editing_baseline24/repair_realism_summary.csv",
        root / "results/tables/openai_three_model_stress_v02_repair_realism_editing_baseline24/repair_realism_paired_effects.csv",
        root / "paper/repair_realism_editing_baseline24.md",
    )
    check_human_packet(
        root / "data/human_audit/human_audit_packet_v0.2.csv",
        root / "data/human_audit/human_audit_answer_key_v0.2.csv",
    )
    check_human_audit_design(
        root / "results/tables/human_audit_v0.2_design/human_audit_design_summary.csv",
        root / "results/tables/human_audit_v0.2_design/human_audit_design_by_language.csv",
        root / "results/tables/human_audit_v0.2_design/human_audit_design_by_family.csv",
        root / "results/tables/human_audit_v0.2_design/human_audit_design_by_model_condition.csv",
        root / "results/tables/human_audit_v0.2_design/human_audit_design_by_auto_failure_type.csv",
        root / "paper/human_audit_design_audit_v02.md",
    )
    check_coverage_native_review(
        root / "data/coverage_native_review_v03/coverage_native_review_packet_v03.csv",
        root / "data/coverage_native_review_v03/coverage_native_review_roster_template_v03.csv",
        root / "results/tables/coverage_native_review_v03_design/coverage_native_review_summary.csv",
        root / "results/tables/coverage_native_review_v03_design/coverage_native_review_by_slice.csv",
        root / "paper/coverage_native_review_design_v03.md",
    )
    check_human_completion_plan(root / "paper/human_audit_completion_plan.md")
    check_discovery(
        root / "results/discovery/wildchat_20k_repair_cues/summary.json",
        root / "results/discovery/wildchat_20k_repair_cues/hit_metadata_hashed.csv",
    )
    check_discovery_cue_analysis(
        root / "results/discovery/wildchat_20k_repair_cues/cue_discovery_overview.csv",
        root / "results/discovery/wildchat_20k_repair_cues/cue_category_conversation_counts.csv",
        root / "results/discovery/wildchat_20k_repair_cues/cue_pattern_counts.csv",
        root / "results/discovery/wildchat_20k_repair_cues/repeated_cue_conversations_hashed.csv",
        root / "paper/discovery_cue_analysis.md",
    )
    check_figures(
        [
            root / "paper/figures/ftga_by_condition.png",
            root / "paper/figures/repair_curve.png",
            root / "results/figures/openai_three_model_stress_v02_full120/ftga_by_condition.png",
            root / "results/figures/openai_three_model_stress_v02_full120/repair_curve.png",
        ]
    )
    check_figure_sources(
        root / "results/figures/openai_three_model_stress_v02_full120/ftga_by_condition_source.csv",
        root / "results/figures/openai_three_model_stress_v02_full120/repair_curve_source.csv",
    )
    check_pdf(root / "paper/main.pdf")
    check_tex_log(root / "paper/main.log")
    check_claim_checklist(root / "paper/claim_evidence_checklist.md")
    check_extended_abstract(root / "paper/extended_abstract_draft.md")
    check_appendix(root / "paper/appendix.md")
    check_related_work(root / "paper/main.tex", root / "paper/refs.bib")
    check_related_work_positioning(root / "paper/related_work_positioning_v02.md")
    check_auxiliary_validator(root, "scripts/validate_human_audit_review_sheets.py", "human-audit review-sheet validation passed")
    check_auxiliary_validator(root, "scripts/validate_label_collection_launch_pack.py", "label-collection launch-pack validation passed")
    check_auxiliary_validator(root, "scripts/validate_label_collection_dispatch.py", "label-collection dispatch validation passed")
    check_auxiliary_validator(root, "scripts/validate_label_collection_operator_handoff.py", "label-collection operator handoff validation passed")
    check_auxiliary_validator(root, "scripts/validate_label_return_preflight.py", "label-return preflight validation passed")
    check_auxiliary_validator(root, "scripts/validate_reviewer_qualification_requirements.py", "reviewer qualification requirements validation passed")
    check_auxiliary_validator(root, "scripts/validate_label_collection_priority.py", "label-collection priority validation passed")
    check_auxiliary_validator(root, "scripts/test_human_audit_adjudication.py", "human-audit adjudication regression tests passed")
    check_auxiliary_validator(
        root,
        "scripts/validate_current_model_human_audit_packet.py",
        "current-model human-audit packet validation passed",
    )
    check_auxiliary_validator(root, "scripts/test_coverage_native_review_completion.py", "coverage native-review completion regression tests passed")
    check_auxiliary_validator(root, "scripts/test_coverage_native_review_adjudication.py", "coverage native-review adjudication regression tests passed")
    check_auxiliary_validator(root, "scripts/validate_coverage_expansion_v03.py", "validated v0.3 coverage expansion scaffold")
    check_auxiliary_validator(root, "scripts/validate_coverage_native_review_packet_v03.py", "validated v0.3 coverage native-review launch packet")
    check_auxiliary_validator(root, "scripts/validate_coverage_native_review_sheets_v03.py", "coverage native-review sheet validation passed")
    check_auxiliary_validator(root, "scripts/validate_coverage_smoke_v03.py", "validated v0.3 coverage smoke")
    check_auxiliary_validator(root, "scripts/validate_current_model_error_analysis.py", "current-model residual error validation passed")
    check_auxiliary_validator(root, "scripts/validate_current_model_uncertainty.py", "current-model uncertainty validation passed")
    check_auxiliary_validator(root, "scripts/validate_current_model_heterogeneity.py", "current-model heterogeneity validation passed")
    check_auxiliary_validator(root, "scripts/validate_current_model_regression_risk.py", "current-model regression-risk validation passed")
    check_auxiliary_validator(root, "scripts/validate_current_model_case_studies.py", "current-model case-study validation passed")
    check_auxiliary_validator(root, "scripts/validate_current_model_scorer_sensitivity.py", "current-model scorer-sensitivity validation passed")
    check_auxiliary_validator(root, "scripts/validate_scorer_challenge_v02.py", "scorer-challenge validation passed")
    check_auxiliary_validator(root, "scripts/validate_scorer_positive_control_v02.py", "scorer positive-control validation passed")
    check_auxiliary_validator(root, "scripts/validate_taxonomy_traceability_v02.py", "taxonomy traceability validation passed")
    check_auxiliary_validator(root, "scripts/validate_generation_progress_probe.py", "generation-progress probe validation passed")
    check_auxiliary_validator(root, "scripts/validate_efficiency_tradeoff.py", "efficiency tradeoff validation passed")
    check_auxiliary_validator(root, "scripts/validate_followup_plan_readiness.py", "follow-up plan readiness validation passed")
    check_auxiliary_validator(root, "scripts/validate_reviewer_concern_audit_v02.py", "reviewer concern audit validation passed")
    check_auxiliary_validator(root, "scripts/validate_submission_anonymity_v02.py", "submission anonymity audit validation passed")
    check_auxiliary_validator(root, "scripts/test_api_key_loading.py", "api-key loading tests passed")
    check_auxiliary_validator(root, "scripts/validate_submission_decision_v02.py", "submission decision audit validation passed")
    check_auxiliary_validator(root, "scripts/validate_human_audit_acceptance_rules.py", "human/native-review acceptance rules validation passed")
    check_auxiliary_validator(root, "scripts/validate_human_audit_threshold_rationale.py", "human/native-review threshold-rationale validation passed")
    check_auxiliary_validator(root, "scripts/validate_all_model_paired_significance.py", "all-model paired-significance validation passed")
    check_auxiliary_validator(root, "scripts/validate_all_model_uncertainty.py", "all-model clustered-uncertainty validation passed")
    check_auxiliary_validator(root, "scripts/validate_balanced_subsample_robustness.py", "balanced-subsample robustness validation passed")
    check_auxiliary_validator(root, "scripts/validate_sentinel_suite_v02.py", "sentinel-suite validation passed")
    check_auxiliary_validator(root, "scripts/validate_contract_benefit_decomposition.py", "contract-benefit decomposition validation passed")
    check_auxiliary_validator(root, "scripts/validate_prompt_family_scorecard.py", "prompt-family scorecard validation passed")
    check_auxiliary_validator(
        root,
        "scripts/validate_coverage_smoke_v03.py",
        "validated v0.3 coverage smoke",
        [
            "--outputs",
            "results/model_outputs/openai_gpt55_stress_v03_smoke6.jsonl",
            "--scores",
            "results/scores/openai_gpt55_stress_v03_smoke6_auto_scores.jsonl",
            "--tables-dir",
            "results/tables/openai_gpt55_stress_v03_smoke6",
            "--report",
            "paper/coverage_smoke_gpt55_v03.md",
            "--expected-model",
            "gpt-5.5",
            "--expected-api-rows",
            "12",
            "--expected-input-tokens",
            "1632",
            "--expected-output-tokens",
            "870",
            "--expected-baseline-first-turn-passes",
            "6",
            "--expected-contract-first-turn-passes",
            "6",
            "--expected-first-turn-failure-count",
            "0",
            "--expected-successful-repair-rows",
            "0",
            "--expected-baseline-mean-rtt",
            "0",
            "--expected-contract-mean-rtt",
            "0",
            "--expected-es-ar-baseline-ftga",
            "1",
            "--expected-failure-item",
            "",
            "--expected-failure-types",
            "",
        ],
    )
    check_auxiliary_validator(root, "scripts/validate_coverage_pilot_v03.py", "validated v0.3 coverage pilot")
    check_qualitative_examples(root)
    check_score_regressions(root)
    check_claim_boundary_lint(root)
    check_auxiliary_validator(root, "scripts/validate_release_docs.py", "release-doc validation passed")
    check_auxiliary_validator(root, "scripts/validate_result_card.py", "result-card validation passed")
    check_artifact_manifest(root)
    print("paper-claim validation passed")


if __name__ == "__main__":
    main()
