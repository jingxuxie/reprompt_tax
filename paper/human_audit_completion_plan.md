# Human Audit Completion Plan

This plan defines the evidence required before widening RePromptTax claims from
"automatic scoring plus LLM-judge audit" to "human/native-speaker validated".

## Current Status

Prepared but not completed:

- blinded launch packet: `data/human_audit/human_audit_packet_v0.2.csv`
- language slices:
  - `data/human_audit/human_audit_packet_v0.2_ar-en.csv`
  - `data/human_audit/human_audit_packet_v0.2_es-en.csv`
  - `data/human_audit/human_audit_packet_v0.2_hi-en.csv`
- private answer key: `data/human_audit/human_audit_answer_key_v0.2.csv`
- annotator roster template:
  `data/human_audit/human_audit_annotator_roster_template_v0.2.csv`
- launch checklist:
  `data/human_audit/human_audit_launch_checklist_v0.2.md`
- launch validator: `scripts/validate_human_audit_packet.py`
- completed-label validator: `scripts/validate_completed_human_audit.py`
- summarizer: `scripts/summarize_human_audit.py`
- pre-specified acceptance rules:
  `paper/human_audit_acceptance_rules_v02.md`

Any file named like `data/human_audit/human_audit_packet_v0.2_smoke_completed.csv`
is a plumbing smoke test only. It must not be described as human validation.

## Completion Requirements

Before claiming completed human validation, all of the following must be true:

1. The completed annotation file contains all 72 audit rows.
2. Every row has completed boolean labels for:
   - `human_pass`
   - `human_language_pass`
   - `human_script_pass`
   - `human_preservation_pass`
   - `human_task_pass`
   - `human_register_locale_pass`
3. Every row has a non-empty `annotator_id`.
4. A completed roster file
   `data/human_audit/human_audit_annotator_roster_v0.2.csv` maps every
   `annotator_id` to the row's language pair.
5. Every roster row used in the completed packet is marked native or
   near-native, script-competent, and conflict-free, with non-empty
   qualification notes.
6. `human_pass` equals the conjunction of the five component labels.
7. Failing rows list at least one valid `human_failure_types` value.
8. Passing rows list no `human_failure_types` values.
9. No completed row is marked `SMOKE ONLY`.
10. The completed packet still matches the private answer key by `audit_id`,
   `language_pair`, and `task_family`.
11. The answer key remains balanced with one row per
   model/condition/task-family/language-pair stratum.

Run:

```bash
conda run -n reprompt_tax python scripts/validate_completed_human_audit.py \
  --annotations data/human_audit/human_audit_packet_v0.2_completed.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --annotator-roster data/human_audit/human_audit_annotator_roster_v0.2.csv
```

## Analysis Steps After Completion

Summarize labels:

```bash
conda run -n reprompt_tax python scripts/summarize_human_audit.py \
  --annotations data/human_audit/human_audit_packet_v0.2_completed.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --out-dir results/tables/human_audit_v0.2
```

The summarizer refuses incomplete completed-audit files by default, so a
summary table cannot be accidentally produced from blank launch packets. Use
`--allow-partial` only for debugging partially returned annotation batches.

Inspect:

- `results/tables/human_audit_v0.2/human_audit_summary.csv`
- `results/tables/human_audit_v0.2/human_audit_by_language.csv`
- `results/tables/human_audit_v0.2/human_audit_by_family.csv`
- `results/tables/human_audit_v0.2/human_audit_by_model_condition.csv`
- `results/tables/human_audit_v0.2/human_audit_by_annotator.csv`
- `results/tables/human_audit_v0.2/human_audit_disagreements.csv`

If disagreements exist, adjudicate them before widening claims. Preserve the
raw completed annotation file and the disagreement table.

For the stronger two-annotator path from the follow-up plan, concatenate two
independent completed rows per `audit_id` into a long-format file. Each repeated
`audit_id` must have a distinct qualified `annotator_id`. Then run:

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

This produces inter-annotator agreement tables and
`human_audit_adjudication_packet.csv` for rows needing final adjudication. The
finalization command validates completed adjudication rows and writes a
one-row-per-item completed packet for the existing human-audit validator and
summarizer.

Apply the pre-specified acceptance rules in
`paper/human_audit_acceptance_rules_v02.md` before widening claims. The v0.2
GPT-4.1-family audit requires at least 65/72 pass/fail agreements and 306/360
component agreements after the completed-label validator passes. The separate
current-model audit requires at least 44/48 pass/fail agreements and 204/240
component agreements. Passing validation alone is necessary but not sufficient
for a stronger paper claim.

## Claim Boundary

If the completed audit validates and pass/fail agreement is high, the paper may
say:

> A balanced 72-response native/near-native human audit supports the automatic
> scorer on the sampled first-turn labels; annotator qualifications were
> recorded in a private roster.

Do not say:

- "the benchmark is fully human-validated" unless every released benchmark item
  and every turn-level label has been human audited,
- "native speakers agree perfectly" unless the completed annotations prove it,
- "the scorer is equivalent to human judgment",
- "all Arabic/Hindi/Hinglish register and locale judgments are settled" unless
  disagreements have been adjudicated by qualified annotators.

If the completed audit shows meaningful disagreement, keep the current claim
boundary and report the disagreement pattern as a limitation or follow-up
analysis.
