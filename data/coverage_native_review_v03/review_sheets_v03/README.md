# v0.3 Coverage Native-Review Sheets

These static HTML sheets are generated from the v0.3 coverage native-review
launch packet. They are for reviewer convenience only; the authoritative packet
and roster remain the CSV files in `data/coverage_native_review_v03/`.

- Send each reviewer only the HTML sheet for their qualified coverage slice.
- Ask reviewers to enter the same reviewer ID that appears in the completed
  roster, fill every TRUE/FALSE field, and download the completed CSV.
- Prefer two independent reviewers per slice. Merge their completed CSV exports
  with `scripts/merge_review_exports.py --labels-per-item 2` as
  `coverage_native_review_packet_v03_double_completed.csv`, keeping duplicate
  `review_id` values and unique `reviewer_id` values.
- Run `scripts/analyze_coverage_native_review_adjudication.py`, fill the
  generated disagreement packet, then run
  `scripts/finalize_coverage_native_review_adjudication.py`.
- Validate finalized one-row-per-item labels with
  `scripts/validate_completed_coverage_native_review_v03.py` before making any
  completed-native-validation claim.
