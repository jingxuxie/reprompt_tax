# Taxonomy Traceability Audit v0.2

This no-API audit links aggregate WildChat repair-cue categories to the
synthetic benchmark families, deterministic scorer components, and repair
metric surfaces used by RePromptTax-Stress-v0.2. It uses only aggregate
cue counts, hashed metadata summaries, and benchmark schema fields; it
does not inspect or release raw WildChat text and is not a prevalence
estimate.

## Overview

| Metric | Value |
|---|---:|
| dataset | allenai/WildChat |
| conversations_scanned | 20000 |
| multiturn_conversations | 10681 |
| conversations_with_repair_cues | 172 |
| cue_hits_total | 219 |
| raw_text_written | False |
| cue_categories | 6 |
| mapped_categories | 6 |
| categories_with_direct_scorer_component | 5 |
| categories_mapped_to_repair_metrics | 1 |
| benchmark_items | 120 |
| benchmark_families | 4 |
| not_prevalence_estimate | 1 |

## Category Mapping

| Cue category | Cue hits | Unique conversations | Benchmark surface | Items | Scorer or metric surface |
|---|---:|---:|---|---:|---|
| generic_repair | 93 | 81 | all_v0.2_task_families | 120 | rtt;repair_at_1;repair_at_2;unresolved_rate |
| preservation_failure | 25 | 18 | quote_preservation;script_register_locale | 60 | preservation_failure;task_noncompletion |
| register_locale_mismatch | 16 | 13 | script_register_locale | 30 | register_locale_mismatch |
| script_mismatch | 4 | 2 | script_register_locale | 30 | script_mismatch;wrong_output_language |
| unwanted_translation | 13 | 13 | editing_preservation;quote_preservation | 60 | wrong_output_language;preservation_failure;task_noncompletion |
| wrong_output_language | 68 | 48 | editing_preservation;output_language_inference | 60 | wrong_output_language;script_mismatch |

## Interpretation

All six discovery cue categories are mapped to at least one benchmark,
scorer, or metric surface. Five of six categories map to deterministic
scorer components; `generic_repair` maps to the multi-turn repair-tax
metrics rather than a scorer component. This supports taxonomy
traceability, not real-world prevalence or native-speaker validity.

The mapping also clarifies the benchmark boundary: public-chat cues
motivate the taxonomy, while the paper-facing claims remain anchored to
the synthetic 120-item stress pilot, deterministic scorer audits,
LLM-judge sanity checks, and future completed human/native labels.
