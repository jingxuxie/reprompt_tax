# v0.3 Coverage Native-Review Launch Checklist

This checklist launches native/near-native review for the 60-row synthetic
v0.3 coverage scaffold. It is prepared but not completed native validation.

## Minimum Launch

- Recruit at least two qualified reviewers for each of the six coverage slices.
- Send each reviewer only their relevant slice CSV from `data/coverage_native_review_v03` or the
  matching static HTML sheet from `data/coverage_native_review_v03/review_sheets_v03`.
- Copy `coverage_native_review_roster_template_v03.csv` to
  `coverage_native_review_roster_v03.csv` and replace placeholder reviewer IDs.
- Require `can_validate_target_language`, `can_validate_script`, and
  `conflict_of_interest` to be filled for every reviewer.
- For cross-language slices, record whether the reviewer can validate the
  instruction language; if not, add a second qualified reviewer or keep the
  claim limited to target-language/content validity.
- Ask reviewers to include the matching `reviewer_issue_types` code for every
  component field marked `FALSE`, and not to list an issue code for a component
  marked `TRUE`.
- Combine independently completed slice files as either
  `coverage_native_review_packet_v03_completed.csv` with all 60
  finalized rows or, preferably, as
  `coverage_native_review_packet_v03_double_completed.csv` with two rows per
  item before adjudication.
- Merge completed slice exports with:

```bash
conda run -n reprompt_tax python scripts/merge_review_exports.py \
  --mode coverage_native_review \
  --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv \
  --out data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv \
  --inputs \
  data/coverage_native_review_v03/coverage_native_review_v03_arabic_instruction_arabic_filenames_completed.csv \
  data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_arabic_content_completed.csv \
  data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_hindi_content_completed.csv \
  data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_spanish_content_completed.csv \
  data/coverage_native_review_v03/coverage_native_review_v03_hindi_english_instruction_hindi_devanagari_completed.csv \
  data/coverage_native_review_v03/coverage_native_review_v03_spanish_instruction_arabic_quote_completed.csv
```

For two independent labels per item, include every returned export after
`--inputs` and add `--labels-per-item 2`, writing to
`coverage_native_review_packet_v03_double_completed.csv`.

## Claim Rule

Do not claim native validation has been completed until the completed packet
and filled roster pass validation. Until then, describe this as a launch-ready
review packet for synthetic v0.3 rows only.

## Completion Commands

Generate reviewer-facing static sheets if using browser-based local export:

```bash
conda run -n reprompt_tax python scripts/make_coverage_native_review_sheets_v03.py
conda run -n reprompt_tax python scripts/validate_coverage_native_review_sheets_v03.py
```

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

## Preferred Adjudication Commands

```bash
conda run -n reprompt_tax python scripts/analyze_coverage_native_review_adjudication.py \
  --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_double_completed.csv \
  --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv \
  --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv \
  --out-dir results/tables/coverage_native_review_v03_adjudication \
  --out-md paper/coverage_native_review_adjudication_v03.md

conda run -n reprompt_tax python scripts/finalize_coverage_native_review_adjudication.py \
  --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_double_completed.csv \
  --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv \
  --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv \
  --adjudication results/tables/coverage_native_review_v03_adjudication/coverage_native_review_adjudication_packet.csv \
  --out data/coverage_native_review_v03/coverage_native_review_packet_v03_adjudicated_completed.csv
```
