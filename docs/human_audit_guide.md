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
- Private answer key: `data/human_audit/human_audit_answer_key_v0.2.csv`
- Launch manifest: `data/human_audit/audit_manifest_v0.2.md`
- Design audit: `paper/human_audit_design_audit_v02.md`
- Completion plan: `paper/human_audit_completion_plan.md`

Annotators should receive only the packet CSV, not the answer key. Before
claiming native/near-native validation, copy the roster template to
`data/human_audit/human_audit_annotator_roster_v0.2.csv` and fill one row per
annotator with language competence, script competence, qualification notes, and
conflict-of-interest status.

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
```

After annotators fill the CSV:

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

The smoke-completed file may be checked only as a plumbing test with
`--allow-smoke`; it is not human validation.
