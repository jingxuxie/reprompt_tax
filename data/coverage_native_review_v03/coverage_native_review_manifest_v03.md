# v0.3 Coverage Native-Review Manifest

Generated for `data/benchmark_stress_v0.3_expansion.jsonl`.

Source benchmark: `data/benchmark_stress_v0.3_expansion.jsonl`
Review rows: 60

This is a launch package for native/near-native review of the synthetic v0.3
coverage scaffold. It is not completed native validation and must not be used
as paper-facing benchmark evidence until the completed review packet and roster
pass validation.

## Launch Files

- Full packet: `data/coverage_native_review_v03/coverage_native_review_packet_v03.csv`
- Slice packets: `data/coverage_native_review_v03/coverage_native_review_v03_<coverage_slice>.csv`
- Roster template: `data/coverage_native_review_v03/coverage_native_review_roster_template_v03.csv`
- Optional static review sheets: `data/coverage_native_review_v03/review_sheets_v03/index.html`
- Launch checklist: `data/coverage_native_review_v03/coverage_native_review_launch_checklist_v03.md`

Each coverage slice has 10 rows. The roster template includes two reviewer
slots per slice for the preferred independent-review-plus-adjudication workflow.
Send reviewers only the slice they are qualified to evaluate. For cross-language
slices, each claim-bearing reviewer must be able to judge the target content
language and script; record whether each reviewer can also validate instruction
language clarity.

## Review Fields

Reviewers should fill every TRUE/FALSE field plus issue types and notes when a
row is not release-usable. Allowed `reviewer_issue_types` values are:

- `ambiguous_instruction`
- `unnatural_target_text`
- `wrong_expected_language`
- `script_expectation_problem`
- `preservation_span_problem`
- `known_bad_output_problem`
- `privacy_or_safety_issue`
- `cultural_or_locale_issue`
- `other`

The completion validator requires every failed component to carry its matching
issue code: `reviewer_prompt_clear` -> `ambiguous_instruction`,
`reviewer_target_language_natural` -> `unnatural_target_text`,
`reviewer_script_expectation_valid` -> `script_expectation_problem`,
`reviewer_preservation_spans_valid` -> `preservation_span_problem`, and
`reviewer_known_bad_outputs_valid` -> `known_bad_output_problem`. It also
rejects issue codes that contradict passing components.

## Reproduction

```bash
conda run -n reprompt_tax python scripts/make_coverage_native_review_packet_v03.py
conda run -n reprompt_tax python scripts/validate_coverage_native_review_packet_v03.py
conda run -n reprompt_tax python scripts/make_coverage_native_review_sheets_v03.py
conda run -n reprompt_tax python scripts/validate_coverage_native_review_sheets_v03.py
conda run -n reprompt_tax python scripts/analyze_coverage_native_review_design_v03.py
conda run -n reprompt_tax python scripts/test_coverage_native_review_completion.py
conda run -n reprompt_tax python scripts/test_coverage_native_review_adjudication.py
```

After reviewers complete one independent row per v0.3 item, validate and
summarize the finalized one-row-per-item labels with:

```bash
conda run -n reprompt_tax python scripts/validate_completed_coverage_native_review_v03.py \
  --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv \
  --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv \
  --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv

conda run -n reprompt_tax python scripts/summarize_coverage_native_review_v03.py \
  --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv \
  --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv \
  --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv
```

Preferred stronger workflow: concatenate independent reviewer rows into a
long-format file with duplicate `review_id` values but unique `reviewer_id`
values per item, generate an adjudication packet, fill only the disagreement
rows, and then finalize to the one-row-per-item completed format:

```bash
conda run -n reprompt_tax python scripts/analyze_coverage_native_review_adjudication.py \
  --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_double_completed.csv \
  --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv \
  --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv \
  --out-dir results/tables/coverage_native_review_v03_adjudication \
  --out-md paper/coverage_native_review_adjudication_v03.md

# After filling the generated coverage_native_review_adjudication_packet.csv:
conda run -n reprompt_tax python scripts/finalize_coverage_native_review_adjudication.py \
  --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_double_completed.csv \
  --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv \
  --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv \
  --adjudication results/tables/coverage_native_review_v03_adjudication/coverage_native_review_adjudication_packet.csv \
  --out data/coverage_native_review_v03/coverage_native_review_packet_v03_adjudicated_completed.csv
```

Do not claim native validation has been completed until a completed packet and
filled qualified-reviewer roster pass the future completion gate.
