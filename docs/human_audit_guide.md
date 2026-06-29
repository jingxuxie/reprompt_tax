# Human Audit Guide

## Goal

Label whether an assistant response satisfies a multilingual interaction
contract. Do not reward general fluency if the response violates the requested
language, script, exact preservation, task, register, or locale constraints.

## Files

- Full packet: `data/human_audit/human_audit_packet_v0.2.csv`
- Spanish-English slice: `data/human_audit/human_audit_packet_v0.2_es-en.csv`
- Hindi-English slice: `data/human_audit/human_audit_packet_v0.2_hi-en.csv`
- Arabic-English slice: `data/human_audit/human_audit_packet_v0.2_ar-en.csv`
- Annotator roster template:
  `data/human_audit/human_audit_annotator_roster_template_v0.2.csv`
- Launch checklist:
  `data/human_audit/human_audit_launch_checklist_v0.2.md`
- Static review sheets:
  `data/human_audit/review_sheets_v0.2/index.html`
- Private answer key: `data/human_audit/human_audit_answer_key_v0.2.csv`
- Launch manifest: `data/human_audit/audit_manifest_v0.2.md`
- Design audit: `paper/human_audit_design_audit_v02.md`
- Completion plan: `paper/human_audit_completion_plan.md`

Annotators should receive only the packet CSV, not the answer key. Before
claiming native/near-native validation, copy the roster template to
`data/human_audit/human_audit_annotator_roster_v0.2.csv` and fill one row per
annotator with language competence, script competence, qualification notes, and
conflict-of-interest status. The v0.2 human-audit roster template includes two
placeholder slots per language pair so the preferred double-label workflow can
assign independent reviewers.

The optional static HTML sheets are generated from the same blinded packet. If
used, send each annotator only the sheet matching their language pair and ask
them to export the completed CSV from the page.

To avoid sending answer keys or private scoring fields by mistake, build and
validate sendable reviewer zip files before launch:

```bash
conda run -n reprompt_tax python scripts/build_label_collection_bundles.py
conda run -n reprompt_tax python scripts/validate_label_collection_bundles.py
```

The generated bundles live under `results/label_collection_bundles_v02`.

## v0.3 Coverage Native Review

The v0.3 coverage packet is separate from the v0.2 model-response audit. It
asks qualified reviewers to validate synthetic benchmark rows before those rows
become paper-facing benchmark evidence.

- Full packet: `data/coverage_native_review_v03/coverage_native_review_packet_v03.csv`
- Slice packets: `data/coverage_native_review_v03/coverage_native_review_v03_<coverage_slice>.csv`
- Roster template: `data/coverage_native_review_v03/coverage_native_review_roster_template_v03.csv`
- Static review sheets: `data/coverage_native_review_v03/review_sheets_v03/index.html`
- Launch checklist: `data/coverage_native_review_v03/coverage_native_review_launch_checklist_v03.md`
- Design audit: `paper/coverage_native_review_design_v03.md`

Validate launch readiness with:

```bash
conda run -n reprompt_tax python scripts/make_coverage_native_review_packet_v03.py
conda run -n reprompt_tax python scripts/validate_coverage_native_review_packet_v03.py
conda run -n reprompt_tax python scripts/make_coverage_native_review_sheets_v03.py
conda run -n reprompt_tax python scripts/validate_coverage_native_review_sheets_v03.py
conda run -n reprompt_tax python scripts/analyze_coverage_native_review_design_v03.py
conda run -n reprompt_tax python scripts/test_coverage_native_review_completion.py
conda run -n reprompt_tax python scripts/test_coverage_native_review_adjudication.py
```

After reviewers complete one independent row per item, validate and summarize
the finalized one-row-per-item labels. First merge returned slice exports:

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

Then validate and summarize:

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

Preferred stronger workflow: concatenate independent reviewer rows into
`coverage_native_review_packet_v03_double_completed.csv`, with duplicate
`review_id` values but unique `reviewer_id` values per item, then adjudicate
only disagreement rows:

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

Do not describe this launch packet as completed native validation.

For v0.3 coverage review, mark `reviewer_release_usable` as `TRUE` only when
all component fields pass. When a component field is `FALSE`, include the
matching issue type: `reviewer_prompt_clear` -> `ambiguous_instruction`,
`reviewer_target_language_natural` -> `unnatural_target_text`,
`reviewer_script_expectation_valid` -> `script_expectation_problem`,
`reviewer_preservation_spans_valid` -> `preservation_span_problem`, and
`reviewer_known_bad_outputs_valid` -> `known_bad_output_problem`. Do not list
an issue type for a component marked `TRUE`; use `other` only with a short note.

## Label Fields

Use `TRUE` or `FALSE` for each binary field.

- `annotator_id`: stable ID matching the completed annotator roster.
- `human_pass`: TRUE only if all component checks pass.
- `human_language_pass`: response language matches `expected_response_language`.
- `human_script_pass`: response uses `expected_script` and avoids forbidden scripts.
- `human_preservation_pass`: every `must_preserve_spans` string is present exactly.
- `human_task_pass`: response performs the requested edit, summary, correction, or message task.
- `human_register_locale_pass`: response follows register, tone, locale, and literal data requirements.
- `human_failure_types`: comma-separated values from:
  - `wrong_output_language`
  - `script_mismatch`
  - `preservation_failure`
  - `task_noncompletion`
  - `register_locale_mismatch`
  - `other`
- `human_notes`: one short note explaining non-obvious decisions.

When a component field is `FALSE`, include the matching failure type:
`human_language_pass` -> `wrong_output_language`,
`human_script_pass` -> `script_mismatch`,
`human_preservation_pass` -> `preservation_failure`,
`human_task_pass` -> `task_noncompletion`, and
`human_register_locale_pass` -> `register_locale_mismatch`. Do not list a
failure type for a component marked `TRUE`. Use `other` only with a short note.

## Decision Rules

1. If exact quoted spans, filenames, dates, names, codes, or amounts are listed
   in `must_preserve_spans`, they must appear exactly. Translation,
   transliteration, or format conversion is a failure unless the prompt asks for
   it.
2. If the user asks to edit, polish, correct, or rewrite quoted English content,
   keep the content language unless the prompt asks for translation.
3. A response can fail even if it is semantically helpful. For example, a
   Spanish explanation around an English rewrite can fail when the expected
   output is only English.
4. Minor wording changes are acceptable if they preserve meaning and satisfy the
   expected language/script/register contract.
5. For Hindi/Hinglish Latin-script items, natural Romanized Hindi/Hinglish is
   acceptable. Devanagari is a script failure when the expected script is Latin.
6. For Arabic expected-script items, quoted English spans may remain in Latin if
   and only if they are required preserved spans.

## Summarizing Completed Labels

Before sending packets to annotators, validate launch readiness:

```bash
conda run -n reprompt_tax python scripts/validate_human_audit_packet.py

conda run -n reprompt_tax python scripts/analyze_human_audit_design.py \
  --packet data/human_audit/human_audit_packet_v0.2.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --out-dir results/tables/human_audit_v0.2_design \
  --out-md paper/human_audit_design_audit_v02.md

conda run -n reprompt_tax python scripts/make_human_audit_review_sheets.py
conda run -n reprompt_tax python scripts/validate_human_audit_review_sheets.py
```

After annotators fill the CSV:

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

The summarizer reports agreement and Cohen's kappa against the automatic
scorer, plus disagreement rows for manual adjudication.

After finalized labels have been validated and summarized, run the claim gate
before changing paper claims:

```bash
conda run -n reprompt_tax python scripts/analyze_completed_label_claim_gates.py
conda run -n reprompt_tax python scripts/validate_completed_label_claim_gates.py
```

If a surface is not `claim_ready`, keep the conservative
automatic-plus-LLM-judge claim boundary.

## Two-Annotator Adjudication

For stronger claims, collect two independent completed rows per `audit_id`.
Concatenate them into a long-format file with duplicate `audit_id` values and
unique `annotator_id` values per item. Then run:

```bash
conda run -n reprompt_tax python scripts/analyze_human_audit_adjudication.py \
  --annotations data/human_audit/human_audit_packet_v0.2_double_completed.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --annotator-roster data/human_audit/human_audit_annotator_roster_v0.2.csv \
  --out-dir results/tables/human_audit_v0.2_adjudication \
  --out-md paper/human_audit_adjudication_v02.md

# After filling the generated human_audit_adjudication_packet.csv:
conda run -n reprompt_tax python scripts/finalize_human_audit_adjudication.py \
  --annotations data/human_audit/human_audit_packet_v0.2_double_completed.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --annotator-roster data/human_audit/human_audit_annotator_roster_v0.2.csv \
  --adjudication results/tables/human_audit_v0.2_adjudication/human_audit_adjudication_packet.csv \
  --out data/human_audit/human_audit_packet_v0.2_adjudicated_completed.csv
```

This writes inter-annotator agreement tables and a blinded adjudication packet
for rows where annotators disagree. The finalization command validates completed
adjudication records and writes a one-row-per-item completed packet that can be
passed to `validate_completed_human_audit.py` and `summarize_human_audit.py`.

The smoke-completed file may be checked only as a plumbing test with
`--allow-smoke`; it is not human validation.
