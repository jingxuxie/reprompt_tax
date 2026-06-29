# Human Audit Review Sheets v0.2

These static HTML sheets are generated from the blinded launch packet. They are
for annotation convenience only; the authoritative packet and answer key remain
the CSV files in `data/human_audit/`.

- Send each annotator only the HTML sheet for their language pair.
- Do not send `human_audit_answer_key_v0.2.csv`.
- Ask annotators to enter the same annotator ID that appears in the completed
  roster, fill every TRUE/FALSE field, and download the completed CSV.
- Merge the three completed CSV exports with `scripts/merge_review_exports.py`
  as `data/human_audit/human_audit_packet_v0.2_completed.csv`.
- Validate the completed audit with `scripts/validate_completed_human_audit.py`
  before making any human/native-speaker validation claim.
