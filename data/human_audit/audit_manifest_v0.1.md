# RePromptTax Human Audit Manifest v0.1

Historical packet generated for the original 60-item stress diagnostic. The
current paper-facing packet is `audit_manifest_v0.2.md`.

## Launch Files

Send annotators only the language slice they can validate:

| Language slice | File | Rows |
|---|---|---:|
| Arabic-English | `human_audit_packet_v0.1_ar-en.csv` | 24 |
| Spanish-English | `human_audit_packet_v0.1_es-en.csv` | 24 |
| Hindi-English | `human_audit_packet_v0.1_hi-en.csv` | 24 |

The full blinded packet is `human_audit_packet_v0.1.csv` with 72 rows.

## Private Files

Do not send these to annotators:

- `human_audit_answer_key_v0.1.csv`
- `human_audit_packet_v0.1_smoke_completed.csv`

The answer key maps audit IDs to item IDs, model names, prompt conditions, and
automatic labels. The smoke-completed file copies automatic labels into the
human fields and is only a plumbing test.

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
```

This checks:

- no private model, condition, item, or auto-label fields leak into annotator packets,
- annotation fields are blank in launch packets,
- language slices exactly match the corresponding full-packet subsets,
- each language/task cell and model/condition/task/language stratum is balanced,
- JSON-list fields are parseable,
- smoke-only artifacts are explicitly marked.

## Completion Gate

After annotators fill the CSV fields, summarize labels with:

```bash
conda run -n reprompt_tax python scripts/validate_completed_human_audit.py \
  --annotations data/human_audit/human_audit_packet_v0.1_completed.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.1.csv

conda run -n reprompt_tax python scripts/summarize_human_audit.py \
  --annotations data/human_audit/human_audit_packet_v0.1_completed.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.1.csv \
  --out-dir results/tables/human_audit_v0.1
```

Strong final paper claims should wait for completed human/native-speaker labels.
The smoke-completed file is only a plumbing test and must not be used for final
claims.
