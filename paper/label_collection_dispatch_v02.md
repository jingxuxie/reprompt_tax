# Label Collection Dispatch Readiness

This report audits the exact reviewer zip files that are safe to send
for the remaining human/native-label collection. It is a dispatch
manifest, not completed human/native validation.

## Summary

- Ready reviewer bundles: 12 / 12
- Reviewer-facing rows across ready bundles: 180
- Total zip payload bytes: 92484
- Claim gate status: no completed human/native validation claim is unlocked.
- Send only these zip files or their contained blinded `slice_packet.csv` and
  `review_sheet.html`; do not send answer keys, automatic labels, model names,
  or prompt conditions.

## Dispatch Priority

| Priority | Surface | Ready bundles | Rows | Claim gate | Next action |
|---:|---|---:|---:|---|---|
| 1 | current_model_human_audit_v02 | 3/3 | 48 | needs_labels / no_claim | send three 16-row current-model slices and collect completed CSV exports plus qualified roster |
| 2 | human_audit_v02 | 3/3 | 72 | needs_labels / no_claim | send three 24-row original v0.2 slices and collect completed CSV exports plus qualified roster |
| 3 | coverage_native_review_v03 | 6/6 | 60 | needs_labels / no_claim | send six 10-row v0.3 coverage-review slices after reviewer availability is confirmed |

## Bundle Manifest

| Surface | Slice | Rows | Expected return file | Bundle | SHA-256 |
|---|---|---:|---|---|---|
| current_model_human_audit_v02 | ar-en | 16 | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_ar-en_completed.csv` | `results/label_collection_bundles_v02/current_model_human_audit_v02/ar-en.zip` | `5de8736621a4ee6c8a4dd2543f323ea741dc9607598ade045f3c269609432670` |
| current_model_human_audit_v02 | es-en | 16 | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_es-en_completed.csv` | `results/label_collection_bundles_v02/current_model_human_audit_v02/es-en.zip` | `a43d00010bc7364b9474d8f7d01b82cea57d8068a119084f5584cc8fe3204648` |
| current_model_human_audit_v02 | hi-en | 16 | `data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_hi-en_completed.csv` | `results/label_collection_bundles_v02/current_model_human_audit_v02/hi-en.zip` | `e7147d3581fd3060fe5d365bb2370cf043c843ec09197a2e3bf71e13c8f3abcc` |
| human_audit_v02 | ar-en | 24 | `data/human_audit/human_audit_packet_v0.2_ar-en_completed.csv` | `results/label_collection_bundles_v02/human_audit_v02/ar-en.zip` | `234b1233764c66e6d1eb0cc5262e3c629086d4e77704239463e6db3badc9a8e7` |
| human_audit_v02 | es-en | 24 | `data/human_audit/human_audit_packet_v0.2_es-en_completed.csv` | `results/label_collection_bundles_v02/human_audit_v02/es-en.zip` | `4ef5328ee36d3f3adcafb64f402122e118ccc33c47e4722bed5a90f4dd5be9f1` |
| human_audit_v02 | hi-en | 24 | `data/human_audit/human_audit_packet_v0.2_hi-en_completed.csv` | `results/label_collection_bundles_v02/human_audit_v02/hi-en.zip` | `4641a7d9fd9cbe1fe100ced5f3407792781436c90f561e4eb19edb9c2880da4c` |
| coverage_native_review_v03 | arabic_instruction_arabic_filenames | 10 | `data/coverage_native_review_v03/coverage_native_review_v03_arabic_instruction_arabic_filenames_completed.csv` | `results/label_collection_bundles_v02/coverage_native_review_v03/arabic_instruction_arabic_filenames.zip` | `a6d239ba8154055d4e5cd149a6c3285f9c7cfa43c51c2ac9d0338522169e7472` |
| coverage_native_review_v03 | english_instruction_arabic_content | 10 | `data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_arabic_content_completed.csv` | `results/label_collection_bundles_v02/coverage_native_review_v03/english_instruction_arabic_content.zip` | `5120d81e8ea40620d6929605b1d2fbb253a52a3953c2815e91c96438b9118536` |
| coverage_native_review_v03 | english_instruction_hindi_content | 10 | `data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_hindi_content_completed.csv` | `results/label_collection_bundles_v02/coverage_native_review_v03/english_instruction_hindi_content.zip` | `9295de2b9a086a81d14f3557cd373f0f2a025eb603c8f7e13b228c56239e75a6` |
| coverage_native_review_v03 | english_instruction_spanish_content | 10 | `data/coverage_native_review_v03/coverage_native_review_v03_english_instruction_spanish_content_completed.csv` | `results/label_collection_bundles_v02/coverage_native_review_v03/english_instruction_spanish_content.zip` | `97653dc8f0ab0cea293b3ea53c00779b7e5622e5b23bcd07ec5fd14164b5845d` |
| coverage_native_review_v03 | hindi_english_instruction_hindi_devanagari | 10 | `data/coverage_native_review_v03/coverage_native_review_v03_hindi_english_instruction_hindi_devanagari_completed.csv` | `results/label_collection_bundles_v02/coverage_native_review_v03/hindi_english_instruction_hindi_devanagari.zip` | `9b794db92b009eb7e3a0144bd3c95367c731861629b4d5dfd9749dd205f5a025` |
| coverage_native_review_v03 | spanish_instruction_arabic_quote | 10 | `data/coverage_native_review_v03/coverage_native_review_v03_spanish_instruction_arabic_quote_completed.csv` | `results/label_collection_bundles_v02/coverage_native_review_v03/spanish_instruction_arabic_quote.zip` | `cc72f48b4ce52fb11a421a851c6cedc673b4b4df19e4b8e6541f58fe096f0093` |

After completed CSV exports and qualified rosters are returned, merge
the slice exports with `scripts/merge_review_exports.py`, run the
surface-specific completed-label validator, summarize labels, then rerun
`scripts/analyze_completed_label_claim_gates.py` before changing any
paper claim.
