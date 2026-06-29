# RePromptTax Human Audit Launch Checklist v0.2

This checklist is for launching the native/near-native validation audit. It is
not a completed validation result.

## Minimum Launch

- Minimum path: recruit one qualified annotator for each language slice:
  - Arabic-English: `human_audit_packet_v0.2_ar-en.csv`
  - Spanish-English: `human_audit_packet_v0.2_es-en.csv`
  - Hindi-English: `human_audit_packet_v0.2_hi-en.csv`
- Preferred path: recruit two independent qualified annotators for each
  language slice, using the reviewer1/reviewer2 return-file names in the
  consolidated launch pack.
- Send each annotator only their language slice and the public guide
  `docs/human_audit_guide.md`.
- Optional: send the matching static HTML sheet from
  `review_sheets_v0.2/` instead of the raw CSV slice; it exports the same
  completed CSV format locally in the annotator's browser.
- Do not send `human_audit_answer_key_v0.2.csv`.
- Ask annotators to fill all annotation columns in their CSV slice and preserve
  the original row order and `audit_id` values.
- Ask annotators to include the matching `human_failure_types` code for every
  component field marked `FALSE`, and not to list a failure code for a
  component marked `TRUE`.
- Copy `human_audit_annotator_roster_template_v0.2.csv` to
  `human_audit_annotator_roster_v0.2.csv` and replace every placeholder
  row used for collection with the real annotator ID, language pair,
  qualifications, script competence, and conflict-of-interest status.

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
audit rows. If annotators work from language slices or static HTML exports,
merge the completed slice rows with:

```bash
conda run -n reprompt_tax python scripts/merge_review_exports.py \
  --mode human_audit \
  --launch-packet data/human_audit/human_audit_packet_v0.2.csv \
  --out data/human_audit/human_audit_packet_v0.2_completed.csv \
  --inputs \
  data/human_audit/human_audit_packet_v0.2_ar-en_completed.csv \
  data/human_audit/human_audit_packet_v0.2_es-en_completed.csv \
  data/human_audit/human_audit_packet_v0.2_hi-en_completed.csv
```

For two independent labels per item, include every returned export after
`--inputs` and add `--labels-per-item 2`, writing to
`human_audit_packet_v0.2_double_completed.csv`.

## Completion Commands

```bash
conda run -n reprompt_tax python scripts/validate_completed_human_audit.py \
  --annotations data/human_audit/human_audit_packet_v0.2_completed.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --annotator-roster data/human_audit/human_audit_annotator_roster_v0.2.csv \
  --expected-models gpt-4.1,gpt-4.1-mini,gpt-4.1-nano

conda run -n reprompt_tax python scripts/summarize_human_audit.py \
  --annotations data/human_audit/human_audit_packet_v0.2_completed.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --out-dir results/tables/human_audit_v0.2
```

`summarize_human_audit.py` fails on incomplete files by default. Use
`--allow-partial` only to debug partially returned batches, not for
paper-facing validation claims.

Optional stronger two-annotator workflow: concatenate independently completed
annotation rows into a long-format file with duplicate `audit_id` values but
unique `annotator_id` values per item, then compute inter-annotator agreement
and generate a blinded adjudication packet for disagreements:

```bash
conda run -n reprompt_tax python scripts/analyze_human_audit_adjudication.py \
  --annotations data/human_audit/human_audit_packet_v0.2_double_completed.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --annotator-roster data/human_audit/human_audit_annotator_roster_v0.2.csv \
  --expected-models gpt-4.1,gpt-4.1-mini,gpt-4.1-nano \
  --out-dir results/tables/human_audit_v0.2_adjudication \
  --out-md paper/human_audit_adjudication_v02.md

# After filling results/tables/human_audit_v0.2_adjudication/human_audit_adjudication_packet.csv:
conda run -n reprompt_tax python scripts/finalize_human_audit_adjudication.py \
  --annotations data/human_audit/human_audit_packet_v0.2_double_completed.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --annotator-roster data/human_audit/human_audit_annotator_roster_v0.2.csv \
  --adjudication results/tables/human_audit_v0.2_adjudication/human_audit_adjudication_packet.csv \
  --expected-models gpt-4.1,gpt-4.1-mini,gpt-4.1-nano \
  --out data/human_audit/human_audit_packet_v0.2_adjudicated_completed.csv
```

## Claim Rule

Do not claim native-speaker or human validation until the completed file and
filled roster pass validation. If validation passes but disagreements are
substantial, keep the current automatic-plus-LLM-judge claim boundary and report
the disagreement pattern as a limitation.
