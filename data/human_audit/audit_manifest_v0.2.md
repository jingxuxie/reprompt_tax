# RePromptTax Human Audit Manifest v0.2

Generated for the current paper-facing full RePromptTax-Stress-v0.2 result.

Source benchmark: `data/benchmark_stress_v0.2.jsonl`
Source scores: `results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl`
Sampling seed: `23`

## Launch Files

Send annotators only the language slice they can validate:

| Language slice | File | Rows |
|---|---|---:|
| Arabic-English | `human_audit_packet_v0.2_ar-en.csv` | 24 |
| Spanish-English | `human_audit_packet_v0.2_es-en.csv` | 24 |
| Hindi-English | `human_audit_packet_v0.2_hi-en.csv` | 24 |

The full blinded packet is `human_audit_packet_v0.2.csv` with 72 rows.
The annotator roster template is
`human_audit_annotator_roster_template_v0.2.csv`; copy it to
`human_audit_annotator_roster_v0.2.csv` and fill one qualified annotator
row per language slice before claiming human/native-speaker validation.

## Private Files

Do not send this to annotators:

- `human_audit_answer_key_v0.2.csv`

The answer key maps audit IDs to item IDs, model names, prompt conditions, and
automatic labels.

## Balance

The full packet contains:

- 3 language pairs,
- 4 task families,
- 3 models,
- 2 prompt conditions,
- 1 first-turn output per language/model/condition/family stratum.

Each language slice contains 6 rows per task family.

## Required Validation Before Launch

```bash
conda run -n reprompt_tax python scripts/validate_human_audit_packet.py

conda run -n reprompt_tax python scripts/analyze_human_audit_design.py \
  --packet data/human_audit/human_audit_packet_v0.2.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --out-dir results/tables/human_audit_v0.2_design \
  --out-md paper/human_audit_design_audit_v02.md
```

This checks:

- no private model, condition, item, or auto-label fields leak into annotator packets,
- annotation fields are blank in launch packets,
- language slices exactly match the corresponding full-packet subsets,
- each language/task cell and model/condition/task/language stratum is balanced,
- JSON-list fields are parseable,
- any smoke-only artifacts are explicitly marked,
- the selected audit rows include both automatic passes and failures before annotation.

## Completion Gate

After annotators fill the CSV fields, summarize labels with:

```bash
conda run -n reprompt_tax python scripts/validate_completed_human_audit.py \
  --annotations data/human_audit/human_audit_packet_v0.2_completed.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv

conda run -n reprompt_tax python scripts/summarize_human_audit.py \
  --annotations data/human_audit/human_audit_packet_v0.2_completed.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --out-dir results/tables/human_audit_v0.2
```

Strong final paper claims should wait for completed human/native-speaker labels.
Completed claims also require a filled annotator roster with native or
near-native language competence, script competence, and no conflict of interest
for every annotator ID used in the completed packet.
Any smoke-completed file is only a plumbing test and must not be used for final
claims.
