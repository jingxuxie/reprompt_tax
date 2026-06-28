# RePromptTax Human Audit Launch Checklist v0.2

This checklist is for launching the native/near-native validation audit. It is
not a completed validation result.

## Minimum Launch

- Recruit one qualified annotator for each language slice:
  - Arabic-English: `human_audit_packet_v0.2_ar-en.csv`
  - Spanish-English: `human_audit_packet_v0.2_es-en.csv`
  - Hindi-English: `human_audit_packet_v0.2_hi-en.csv`
- Send each annotator only their language slice and the public guide
  `docs/human_audit_guide.md`.
- Do not send `human_audit_answer_key_v0.2.csv`.
- Ask annotators to fill all annotation columns in their CSV slice and preserve
  the original row order and `audit_id` values.
- Copy `human_audit_annotator_roster_template_v0.2.csv` to
  `human_audit_annotator_roster_v0.2.csv` and replace every placeholder
  row with the real annotator ID, language pair, qualifications, script
  competence, and conflict-of-interest status.

## Qualification Check

Each roster row used for claims must satisfy:

- `native_or_near_native` is TRUE,
- `can_validate_script` is TRUE,
- `conflict_of_interest` is FALSE,
- `qualification_notes` is non-empty,
- the annotator's `language_pair` matches every row they labeled.

## Files To Combine After Annotation

The completed file should be named
`human_audit_packet_v0.2_completed.csv` and should contain all 72
audit rows. If annotators work from language slices, concatenate the completed
slice rows under the original header without adding answer-key fields.

## Completion Commands

```bash
conda run -n reprompt_tax python scripts/validate_completed_human_audit.py \
  --annotations data/human_audit/human_audit_packet_v0.2_completed.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --annotator-roster data/human_audit/human_audit_annotator_roster_v0.2.csv

conda run -n reprompt_tax python scripts/summarize_human_audit.py \
  --annotations data/human_audit/human_audit_packet_v0.2_completed.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --out-dir results/tables/human_audit_v0.2
```

## Claim Rule

Do not claim native-speaker or human validation until the completed file and
filled roster pass validation. If validation passes but disagreements are
substantial, keep the current automatic-plus-LLM-judge claim boundary and report
the disagreement pattern as a limitation.
