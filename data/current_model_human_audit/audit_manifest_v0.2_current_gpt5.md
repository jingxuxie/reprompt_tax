# RePromptTax Human Audit Manifest v0.2_current_gpt5

Generated for the current paper-facing full RePromptTax-Stress-v0.2 result.

Source benchmark: `data/benchmark_stress_v0.2.jsonl`
Source scores:
- `results/scores/openai_gpt54mini_stress_v02_full120_auto_scores.jsonl`
- `results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl`
Sampling seed: `29`
Selection rule: one first-turn row per model/condition/language/family stratum, preferring automatic failures when a stratum contains at least one failure.

## Launch Files

Send annotators only the language slice they can validate:

| Language slice | File | Rows |
|---|---|---:|
| ar-en | `human_audit_packet_v0.2_current_gpt5_ar-en.csv` | 16 |
| es-en | `human_audit_packet_v0.2_current_gpt5_es-en.csv` | 16 |
| hi-en | `human_audit_packet_v0.2_current_gpt5_hi-en.csv` | 16 |

The full blinded packet is `human_audit_packet_v0.2_current_gpt5.csv` with 48 rows.
Reviewer-facing static HTML sheets are available under
`review_sheets_v0.2_current_gpt5/`; they are generated from the blinded packet and
support local CSV export without revealing the answer key.
The annotator roster template is
`human_audit_annotator_roster_template_v0.2_current_gpt5.csv`; copy it to
`human_audit_annotator_roster_v0.2_current_gpt5.csv` and fill one qualified annotator
row per language slice before claiming human/native-speaker validation.

## Private Files

Do not send this to annotators:

- `human_audit_answer_key_v0.2_current_gpt5.csv`

The answer key maps audit IDs to item IDs, model names, prompt conditions, and
automatic labels.

## Balance

The full packet contains:

- 3 language pairs,
- 4 task families,
- 2 models: `gpt-5.4-mini`, `gpt-5.5`,
- 2 prompt conditions: `baseline`, `contract`,
- 1 first-turn output per language/model/condition/family stratum.

Each language slice contains 4 rows per task family.

## Required Validation Before Launch

```bash
conda run -n reprompt_tax python scripts/validate_human_audit_packet.py \
  --out-dir data/current_model_human_audit \
  --packet-version v0.2_current_gpt5 \
  --expected-models gpt-5.4-mini,gpt-5.5

conda run -n reprompt_tax python scripts/analyze_human_audit_design.py \
  --packet data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv \
  --answer-key data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv \
  --out-dir results/tables/human_audit_v0.2_current_gpt5_design \
  --out-md paper/human_audit_design_audit_v02_current_gpt5.md \
  --expected-models gpt-5.4-mini,gpt-5.5

conda run -n reprompt_tax python scripts/make_human_audit_review_sheets.py \
  --packet data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv \
  --out-dir data/current_model_human_audit/review_sheets_v0.2_current_gpt5 \
  --packet-version v0.2_current_gpt5

conda run -n reprompt_tax python scripts/validate_human_audit_review_sheets.py \
  --packet data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5.csv \
  --out-dir data/current_model_human_audit/review_sheets_v0.2_current_gpt5 \
  --packet-version v0.2_current_gpt5
```

This checks:

- no private model, condition, item, or auto-label fields leak into annotator packets,
- annotation fields are blank in launch packets,
- language slices exactly match the corresponding full-packet subsets,
- each language/task cell and model/condition/task/language stratum is balanced,
- JSON-list fields are parseable,
- any smoke-only artifacts are explicitly marked,
- the selected audit rows include both automatic passes and failures before annotation.
- generated static review sheets cover all audit IDs without private fields.

## Completion Gate

After annotators fill the CSV fields, summarize labels with:

```bash
conda run -n reprompt_tax python scripts/validate_completed_human_audit.py \
  --annotations data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_completed.csv \
  --answer-key data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv \
  --annotator-roster data/current_model_human_audit/human_audit_annotator_roster_v0.2_current_gpt5.csv \
  --expected-models gpt-5.4-mini,gpt-5.5

conda run -n reprompt_tax python scripts/summarize_human_audit.py \
  --annotations data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_completed.csv \
  --answer-key data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv \
  --out-dir results/tables/human_audit_v0.2_current_gpt5
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
  --annotations data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_double_completed.csv \
  --answer-key data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv \
  --annotator-roster data/current_model_human_audit/human_audit_annotator_roster_v0.2_current_gpt5.csv \
  --expected-models gpt-5.4-mini,gpt-5.5 \
  --out-dir results/tables/human_audit_v0.2_current_gpt5_adjudication \
  --out-md paper/human_audit_adjudication_v02_current_gpt5.md

# After filling results/tables/human_audit_v0.2_current_gpt5_adjudication/human_audit_adjudication_packet.csv:
conda run -n reprompt_tax python scripts/finalize_human_audit_adjudication.py \
  --annotations data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_double_completed.csv \
  --answer-key data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv \
  --annotator-roster data/current_model_human_audit/human_audit_annotator_roster_v0.2_current_gpt5.csv \
  --adjudication results/tables/human_audit_v0.2_current_gpt5_adjudication/human_audit_adjudication_packet.csv \
  --expected-models gpt-5.4-mini,gpt-5.5 \
  --out data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_adjudicated_completed.csv
```

Strong final paper claims should wait for completed human/native-speaker labels.
Completed claims also require a filled annotator roster with native or
near-native language competence, script competence, and no conflict of interest
for every annotator ID used in the completed packet.
Any smoke-completed file is only a plumbing test and must not be used for final
claims.
