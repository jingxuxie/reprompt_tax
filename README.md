# RePromptTax Pilot

This repository contains a fast pilot pipeline for the Re-prompt Tax project:
measuring hidden extra turns, tokens, and repair burden in multilingual and
code-switched LLM interactions.

The current paper-facing result uses the full 120-item RePromptTax-Stress-v0.2
pilot:

- 3 language pairs: Spanish-English, Hindi-English, Arabic-English
- 4 task families: editing preservation, output-language inference,
  quote preservation, script/register/locale constraints
- 10 items per pair-family cell
- 2 conditions: baseline and Global Interaction Contract

The repository also includes a 120-item easier standard pilot, the original
60-item stress set, a 24-item v0.2 diagnostic probe, and a single-model
prompt-control plus prompt-ablation diagnostic.

## Quick Start

Generate the benchmark:

```bash
conda run -n reprompt_tax python scripts/generate_benchmark.py
```

Generate and validate the paper-facing stress benchmark:

```bash
conda run -n reprompt_tax python scripts/generate_stress_benchmark_v02.py
conda run -n reprompt_tax python scripts/validate_stress_benchmark.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --expected-per-cell 10
conda run -n reprompt_tax python scripts/analyze_benchmark_quality.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --out-dir results/tables/benchmark_quality_v02 \
  --out-md paper/benchmark_quality_audit_v02.md
```

Generate and audit the synthetic v0.3 coverage scaffold for non-English
target-content editing. This is not a paper-facing scored result until native
validation and model runs are completed:

```bash
conda run -n reprompt_tax python scripts/generate_coverage_expansion_v03.py
conda run -n reprompt_tax python scripts/analyze_coverage_expansion_v03.py
conda run -n reprompt_tax python scripts/validate_coverage_expansion_v03.py
```

Prepare the launch-ready native-review packet for the same 60 synthetic v0.3
rows. This validates packet structure only; it is not completed native
validation:

```bash
conda run -n reprompt_tax python scripts/make_coverage_native_review_packet_v03.py
conda run -n reprompt_tax python scripts/validate_coverage_native_review_packet_v03.py
conda run -n reprompt_tax python scripts/make_coverage_native_review_sheets_v03.py
conda run -n reprompt_tax python scripts/validate_coverage_native_review_sheets_v03.py
conda run -n reprompt_tax python scripts/analyze_coverage_native_review_design_v03.py
conda run -n reprompt_tax python scripts/test_coverage_native_review_adjudication.py
```

After reviewers complete one independent row per v0.3 item, validate and
summarize the finalized one-row-per-item labels with:

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

Preferred stronger workflow: concatenate independently completed reviewer rows
into a long-format file with duplicate `review_id` values but unique
`reviewer_id` values per item, generate a disagreement-only adjudication
packet, fill it, and then finalize the labels:

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

Regenerate the saved six-item `gpt-5.4-mini` v0.3 coverage-smoke analysis
without additional API calls:

```bash
conda run -n reprompt_tax python scripts/score_auto.py \
  --benchmark data/benchmark_stress_v0.3_expansion.jsonl \
  --outputs results/model_outputs/openai_gpt54mini_stress_v03_smoke6.jsonl \
  --out results/scores/openai_gpt54mini_stress_v03_smoke6_auto_scores.jsonl

conda run -n reprompt_tax python scripts/compute_metrics.py \
  --scores results/scores/openai_gpt54mini_stress_v03_smoke6_auto_scores.jsonl \
  --out-dir results/tables/openai_gpt54mini_stress_v03_smoke6

conda run -n reprompt_tax python scripts/analyze_coverage_smoke_v03.py
conda run -n reprompt_tax python scripts/validate_coverage_smoke_v03.py
```

Regenerate the saved 24-item `gpt-5.4-mini` v0.3 coverage-pilot analysis
without additional API calls. This merges the six saved smoke rows with the
18-item remaining shard:

```bash
conda run -n reprompt_tax python scripts/build_coverage_pilot_v03_outputs.py
conda run -n reprompt_tax python scripts/score_auto.py \
  --benchmark data/benchmark_stress_v0.3_expansion.jsonl \
  --outputs results/model_outputs/openai_gpt54mini_stress_v03_pilot24.jsonl \
  --out results/scores/openai_gpt54mini_stress_v03_pilot24_auto_scores.jsonl
conda run -n reprompt_tax python scripts/compute_metrics.py \
  --scores results/scores/openai_gpt54mini_stress_v03_pilot24_auto_scores.jsonl \
  --out-dir results/tables/openai_gpt54mini_stress_v03_pilot24
conda run -n reprompt_tax python scripts/analyze_coverage_pilot_v03.py
conda run -n reprompt_tax python scripts/validate_coverage_pilot_v03.py
```

Regenerate the saved six-item `gpt-5.5` v0.3 coverage-smoke analysis without
additional API calls:

```bash
conda run -n reprompt_tax python scripts/score_auto.py \
  --benchmark data/benchmark_stress_v0.3_expansion.jsonl \
  --outputs results/model_outputs/openai_gpt55_stress_v03_smoke6.jsonl \
  --out results/scores/openai_gpt55_stress_v03_smoke6_auto_scores.jsonl
conda run -n reprompt_tax python scripts/compute_metrics.py \
  --scores results/scores/openai_gpt55_stress_v03_smoke6_auto_scores.jsonl \
  --out-dir results/tables/openai_gpt55_stress_v03_smoke6
conda run -n reprompt_tax python scripts/analyze_coverage_smoke_v03.py \
  --scores results/scores/openai_gpt55_stress_v03_smoke6_auto_scores.jsonl \
  --outputs results/model_outputs/openai_gpt55_stress_v03_smoke6.jsonl \
  --out-dir results/tables/openai_gpt55_stress_v03_smoke6 \
  --out-md paper/coverage_smoke_gpt55_v03.md
conda run -n reprompt_tax python scripts/validate_coverage_smoke_v03.py \
  --outputs results/model_outputs/openai_gpt55_stress_v03_smoke6.jsonl \
  --scores results/scores/openai_gpt55_stress_v03_smoke6_auto_scores.jsonl \
  --tables-dir results/tables/openai_gpt55_stress_v03_smoke6 \
  --report paper/coverage_smoke_gpt55_v03.md \
  --expected-model gpt-5.5 \
  --expected-api-rows 12 \
  --expected-input-tokens 1632 \
  --expected-output-tokens 870 \
  --expected-baseline-first-turn-passes 6 \
  --expected-contract-first-turn-passes 6 \
  --expected-first-turn-failure-count 0 \
  --expected-successful-repair-rows 0 \
  --expected-baseline-mean-rtt 0 \
  --expected-contract-mean-rtt 0 \
  --expected-es-ar-baseline-ftga 1 \
  --expected-failure-item "" \
  --expected-failure-types ""
```

Generate the human-audit packet and optional static review sheets for
native/near-native annotators. The sheets are generated from the blinded packet
and export completed CSV files locally in the browser:

```bash
conda run -n reprompt_tax python scripts/make_human_audit_packet.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --out-dir data/human_audit \
  --packet-version v0.2 \
  --seed 23

conda run -n reprompt_tax python scripts/validate_human_audit_packet.py
conda run -n reprompt_tax python scripts/make_human_audit_review_sheets.py
conda run -n reprompt_tax python scripts/validate_human_audit_review_sheets.py
```

Run a local dry-run smoke test:

```bash
conda run -n reprompt_tax python scripts/run_models.py \
  --benchmark data/benchmark_v0.1.jsonl \
  --out results/model_outputs/dry_run.jsonl \
  --models dry-model \
  --conditions baseline,contract \
  --limit 12 \
  --dry-run
```

Run the full expanded stress dry-run without API calls:

```bash
conda run -n reprompt_tax python scripts/run_models.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --out results/model_outputs/dry_run_stress_v02.jsonl \
  --models dry-model \
  --conditions baseline,contract \
  --dry-run
```

Run the historical bounded three-model probe on 24 new v0.2 items:

```bash
conda run -n reprompt_tax python scripts/run_models.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --out results/model_outputs/openai_nano_stress_v02_new24.jsonl \
  --models gpt-4.1-nano \
  --conditions baseline,contract \
  --item-id-file data/stress_v02_new_balanced_24_ids.txt \
  --max-output-tokens 256 \
  --max-api-calls 100

conda run -n reprompt_tax python scripts/run_models.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --out results/model_outputs/openai_mini_gpt41_stress_v02_new24.jsonl \
  --models gpt-4.1-mini,gpt-4.1 \
  --conditions baseline,contract \
  --item-id-file data/stress_v02_new_balanced_24_ids.txt \
  --max-output-tokens 256 \
  --max-api-calls 140
```

Run the bounded single-model generic-helpfulness prompt-control extension for
the 60 v0.2 items that are not in the original stress60 control:

```bash
conda run -n reprompt_tax python scripts/run_models.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --out results/model_outputs/openai_nano_stress_v02_new60_generic_helpfulness.jsonl \
  --models gpt-4.1-nano \
  --conditions generic_helpfulness \
  --item-id-file data/stress_v02_new_60_ids.txt \
  --max-output-tokens 256 \
  --max-api-calls 160
```

Run the bounded single-model content-preservation prompt ablation on the full
120-item stress pilot:

```bash
conda run -n reprompt_tax python scripts/run_models.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --out results/model_outputs/openai_nano_stress_v02_full120_content_preservation.jsonl \
  --models gpt-4.1-nano \
  --conditions content_preservation \
  --max-output-tokens 256 \
  --max-api-calls 220
```

Regenerate the saved current-model refresh tables without additional API calls:

```bash
conda run -n reprompt_tax python scripts/analyze_current_model_refresh.py
conda run -n reprompt_tax python scripts/validate_current_model_refresh.py
```

Regenerate current-model uncertainty and claim-scope checks without additional
API calls. This combines paired bootstrap intervals with exact paired sign
tests for the full GPT-5.x refresh runs:

```bash
conda run -n reprompt_tax python scripts/analyze_current_model_uncertainty.py
conda run -n reprompt_tax python scripts/validate_current_model_uncertainty.py
```

Regenerate current-model heterogeneity checks without additional API calls.
This reports language-pair, task-family, and leave-one-stratum effects for the
full GPT-5.x refresh runs:

```bash
conda run -n reprompt_tax python scripts/analyze_current_model_heterogeneity.py
conda run -n reprompt_tax python scripts/validate_current_model_heterogeneity.py
```

Regenerate current-model contract-regression risk checks without additional API
calls. This isolates paired rows where a contract fixes or hurts first-turn
success relative to the baseline:

```bash
conda run -n reprompt_tax python scripts/analyze_current_model_regression_risk.py
conda run -n reprompt_tax python scripts/validate_current_model_regression_risk.py
```

Regenerate the current-model residual-error analysis without additional API
calls. This inspects where `gpt-5.4-mini` and `gpt-5.5` still fail after the
full refresh:

```bash
conda run -n reprompt_tax python scripts/analyze_current_model_error_analysis.py
conda run -n reprompt_tax python scripts/validate_current_model_error_analysis.py
```

Regenerate qualitative current-model case studies from saved score logs:

```bash
conda run -n reprompt_tax python scripts/analyze_current_model_case_studies.py
conda run -n reprompt_tax python scripts/validate_current_model_case_studies.py
```

Regenerate the current-model scorer-sensitivity diagnostic without additional
API calls. This relaxes one automatic scoring component at a time over saved
first-turn score logs:

```bash
conda run -n reprompt_tax python scripts/analyze_current_model_scorer_sensitivity.py
conda run -n reprompt_tax python scripts/validate_current_model_scorer_sensitivity.py
```

Regenerate the generation-progress probe without additional API calls. This
compares item-level failure movement from the GPT-4.1-family rows to the
GPT-5.x-family rows:

```bash
conda run -n reprompt_tax python scripts/analyze_generation_progress_probe.py
conda run -n reprompt_tax python scripts/validate_generation_progress_probe.py
```

Regenerate the saved current-model prompt-mechanism diagnostic without
additional API calls. This emits the `gpt-5.4-mini` and `gpt-5.5`
content-preservation mechanism reports:

```bash
conda run -n reprompt_tax python scripts/analyze_current_prompt_mechanism.py
conda run -n reprompt_tax python scripts/validate_current_prompt_mechanism.py
```

Score and aggregate:

```bash
conda run -n reprompt_tax python scripts/score_auto.py \
  --benchmark data/benchmark_v0.1.jsonl \
  --outputs results/model_outputs/dry_run.jsonl \
  --out results/scores/dry_run_auto_scores.jsonl

conda run -n reprompt_tax python scripts/compute_metrics.py \
  --scores results/scores/dry_run_auto_scores.jsonl \
  --out-dir results/tables
```

Regenerate the saved full120 prompt-control diagnostic without API calls:

```bash
conda run -n reprompt_tax python scripts/score_auto.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --outputs results/model_outputs/openai_nano_stress_v02_new60_generic_helpfulness.jsonl \
  --out results/scores/openai_nano_stress_v02_new60_generic_helpfulness_auto_scores.jsonl

conda run -n reprompt_tax python scripts/build_full_v02_prompt_control_scores.py

conda run -n reprompt_tax python scripts/compute_metrics.py \
  --scores results/scores/openai_nano_stress_v02_full120_generic_helpfulness_auto_scores.jsonl \
  --out-dir results/tables/openai_nano_stress_v02_full120_generic_helpfulness

conda run -n reprompt_tax python scripts/analyze_prompt_control.py
```

Regenerate the saved full120 content-preservation prompt-ablation diagnostic
without additional API calls:

```bash
conda run -n reprompt_tax python scripts/score_auto.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --outputs results/model_outputs/openai_nano_stress_v02_full120_content_preservation.jsonl \
  --out results/scores/openai_nano_stress_v02_full120_content_preservation_auto_scores.jsonl

conda run -n reprompt_tax python scripts/compute_metrics.py \
  --scores results/scores/openai_nano_stress_v02_full120_content_preservation_auto_scores.jsonl \
  --out-dir results/tables/openai_nano_stress_v02_full120_content_preservation

conda run -n reprompt_tax python scripts/analyze_prompt_ablation.py
```

Build the full paper-facing v0.2 score file from saved shards:

```bash
conda run -n reprompt_tax python scripts/build_full_v02_scores.py
```

Compute paired contract-vs-baseline effects from full v0.2 trajectory metrics:

```bash
conda run -n reprompt_tax python scripts/paired_effects.py \
  --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv \
  --out-dir results/tables/openai_three_model_stress_v02_full120

conda run -n reprompt_tax python scripts/paired_significance.py \
  --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv \
  --out-csv results/tables/openai_three_model_stress_v02_full120/paired_significance_by_model.csv \
  --out-md paper/paired_significance_v02_full120.md

conda run -n reprompt_tax python scripts/analyze_language_slices.py \
  --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv \
  --out-dir results/tables/openai_three_model_stress_v02_full120 \
  --out-md paper/language_slice_analysis_v02_full120.md

conda run -n reprompt_tax python scripts/analyze_repair_dynamics.py \
  --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv \
  --out-dir results/tables/openai_three_model_stress_v02_full120 \
  --out-md paper/repair_dynamics_v02_full120.md

conda run -n reprompt_tax python scripts/analyze_item_consistency.py \
  --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv \
  --out-dir results/tables/openai_three_model_stress_v02_full120 \
  --out-md paper/item_consistency_analysis_v02_full120.md

conda run -n reprompt_tax python scripts/analyze_scorer_ablation.py \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --out-dir results/tables/openai_three_model_stress_v02_full120 \
  --out-md paper/scorer_ablation_sensitivity_v02_full120.md
```

Analyze absolute token burden:

```bash
conda run -n reprompt_tax python scripts/analyze_token_burden.py \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --out-dir results/tables/openai_three_model_stress_v02_full120 \
  --out-md paper/token_burden_analysis_v02_full120.md
```

Audit benchmark release hygiene:

```bash
conda run -n reprompt_tax python scripts/analyze_benchmark_quality.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --out-dir results/tables/benchmark_quality_v02 \
  --out-md paper/benchmark_quality_audit_v02.md
```

Summarize paper-facing API usage and provenance from saved artifacts:

```bash
conda run -n reprompt_tax python scripts/summarize_experiment_ledger.py \
  --out-dir results/tables/experiment_ledger_v02 \
  --out-md paper/experiment_ledger_v02.md
```

Run a stratified blinded judge audit over first-turn stress outputs:

```bash
conda run -n reprompt_tax python scripts/judge_outputs.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --out results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl \
  --judge-model gpt-4.1 \
  --turn 0 \
  --sample-per-stratum 3 \
  --seed 17 \
  --max-api-calls 72

conda run -n reprompt_tax python scripts/summarize_judge_audit.py \
  --audit results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl \
  --out-dir results/tables/openai_three_model_stress_v02_full120_judge_audit72

conda run -n reprompt_tax python scripts/analyze_judge_agreement.py \
  --audit results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --out-dir results/tables/openai_three_model_stress_v02_full120_judge_audit72 \
  --out-md paper/judge_agreement_analysis_v02_full120.md
```

Run or regenerate the paired `gpt-5.5` judge refresh on the same 72-row sample:

```bash
conda run -n reprompt_tax python scripts/judge_outputs.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --out results/scores/openai_three_model_stress_v02_full120_judge_gpt55_audit72.jsonl \
  --judge-model gpt-5.5 \
  --turn 0 \
  --sample-per-stratum 3 \
  --seed 17 \
  --max-api-calls 72

conda run -n reprompt_tax python scripts/analyze_judge_refresh.py
conda run -n reprompt_tax python scripts/validate_judge_refresh.py
```

Run or regenerate the bounded repair-realism diagnostic for baseline
editing-preservation failures:

```bash
conda run -n reprompt_tax python scripts/run_repair_prompt_variants.py \
  --out results/scores/openai_three_model_stress_v02_repair_realism_editing_baseline24.jsonl \
  --sample-size 24 \
  --seed 29 \
  --max-output-tokens 256 \
  --max-api-calls 72

conda run -n reprompt_tax python scripts/analyze_repair_realism.py
conda run -n reprompt_tax python scripts/validate_repair_realism.py
```

For real API runs, install the OpenAI SDK in the `reprompt_tax` environment and
use a small limit first. The runner reads the API key from
`/home/eston/colm_workshop/apikey.txt` by default and does not print it.

Build the current COLM-style paper draft:

```bash
cd paper
latexmk -pdf -interaction=nonstopmode main.tex
```

The current compiled draft is `paper/main.pdf`.

Generate the paper-facing failure-mode analysis:

```bash
conda run -n reprompt_tax python scripts/analyze_failure_modes.py \
  --tables-dir results/tables/openai_three_model_stress_v02_full120 \
  --paper-out paper/failure_mode_analysis_v02_full120.md
conda run -n reprompt_tax python scripts/analyze_component_breakdown.py \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --out-dir results/tables/openai_three_model_stress_v02_full120 \
  --out-md paper/component_breakdown_v02_full120.md
conda run -n reprompt_tax python scripts/build_error_atlas.py \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --trajectories results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv \
  --out-csv results/tables/openai_three_model_stress_v02_full120/first_turn_error_atlas.csv \
  --out-md paper/error_atlas_v02_full120.md
conda run -n reprompt_tax python scripts/paired_significance.py \
  --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv \
  --out-csv results/tables/openai_three_model_stress_v02_full120/paired_significance_by_model.csv \
  --out-md paper/paired_significance_v02_full120.md
```

Run deterministic scorer regression tests:

```bash
conda run -n reprompt_tax python scripts/test_score_auto.py
```

Run claim-boundary lint:

```bash
conda run -n reprompt_tax python scripts/lint_claim_boundaries.py
```

Generate the deterministic artifact manifest:

```bash
conda run -n reprompt_tax python scripts/make_artifact_manifest.py
```

Run the full local submission gate, which regenerates saved tables and figures,
builds the PDF, refreshes the manifest, and runs validators without making API
calls:

```bash
conda run -n reprompt_tax python scripts/run_submission_checks.py
```

Analyze saved aggregate WildChat repair-cue metadata without raw text:

```bash
conda run -n reprompt_tax python scripts/analyze_discovery_cues.py \
  --summary results/discovery/wildchat_20k_repair_cues/summary.json \
  --metadata results/discovery/wildchat_20k_repair_cues/hit_metadata_hashed.csv \
  --out-dir results/discovery/wildchat_20k_repair_cues \
  --out-md paper/discovery_cue_analysis.md
```

Validate that the paper-facing claims match saved artifacts:

```bash
conda run -n reprompt_tax python scripts/validate_paper_claims.py
```

Validate the artifact manifest without rewriting it:

```bash
conda run -n reprompt_tax python scripts/make_artifact_manifest.py --check
```

Validate qualitative examples directly against saved score rows:

```bash
conda run -n reprompt_tax python scripts/validate_qualitative_examples.py
```

Validate the non-paper-facing v0.2 follow-up probe:

```bash
conda run -n reprompt_tax python scripts/validate_followup_probe.py
```

Release-facing documentation:

- `docs/benchmark_card.md`
- `docs/evaluation_card.md`
- `docs/result_card.md`
- `docs/human_audit_guide.md`
- `paper/appendix.md`
- `paper/claim_evidence_checklist.md`
- `paper/related_work_positioning_v02.md`
- `data/human_audit/audit_manifest_v0.2.md`
- `data/human_audit/human_audit_launch_checklist_v0.2.md`
- `data/current_model_human_audit/audit_manifest_v0.2_current_gpt5.md`
- `data/current_model_human_audit/human_audit_launch_checklist_v0.2_current_gpt5.md`
- `paper/current_model_human_audit_design_v02.md`
- `data/coverage_native_review_v03/coverage_native_review_manifest_v03.md`
- `data/coverage_native_review_v03/coverage_native_review_launch_checklist_v03.md`
- `paper/coverage_native_review_design_v03.md`

Prepare and summarize a human/native-speaker audit packet:

```bash
conda run -n reprompt_tax python scripts/make_human_audit_packet.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --out-dir data/human_audit \
  --seed 23

conda run -n reprompt_tax python scripts/validate_human_audit_packet.py

conda run -n reprompt_tax python scripts/analyze_human_audit_design.py \
  --packet data/human_audit/human_audit_packet_v0.2.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --out-dir results/tables/human_audit_v0.2_design \
  --out-md paper/human_audit_design_audit_v02.md

conda run -n reprompt_tax python scripts/validate_completed_human_audit.py \
  --annotations data/human_audit/human_audit_packet_v0.2_completed.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --annotator-roster data/human_audit/human_audit_annotator_roster_v0.2.csv

conda run -n reprompt_tax python scripts/summarize_human_audit.py \
  --annotations data/human_audit/human_audit_packet_v0.2_completed.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --out-dir results/tables/human_audit_v0.2
```

The summarizer fails on incomplete completed-audit files by default. Use
`--allow-partial` only for debugging partially returned annotation batches, not
for paper-facing human-validation claims.

Optional stronger two-annotator workflow: concatenate independently completed
annotation rows into a long-format file with duplicate `audit_id` values but
unique `annotator_id` values per item, then compute inter-annotator agreement
and generate a blinded adjudication packet for disagreements:

```bash
conda run -n reprompt_tax python scripts/analyze_human_audit_adjudication.py \
  --annotations data/human_audit/human_audit_packet_v0.2_double_completed.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --annotator-roster data/human_audit/human_audit_annotator_roster_v0.2.csv \
  --out-dir results/tables/human_audit_v0.2_adjudication \
  --out-md paper/human_audit_adjudication_v02.md

# After filling results/tables/human_audit_v0.2_adjudication/human_audit_adjudication_packet.csv:
conda run -n reprompt_tax python scripts/finalize_human_audit_adjudication.py \
  --annotations data/human_audit/human_audit_packet_v0.2_double_completed.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --annotator-roster data/human_audit/human_audit_annotator_roster_v0.2.csv \
  --adjudication results/tables/human_audit_v0.2_adjudication/human_audit_adjudication_packet.csv \
  --out data/human_audit/human_audit_packet_v0.2_adjudicated_completed.csv
```

Prepare the separate current-model human-audit launch packet. This is a
48-row, failure-enriched, blinded packet for the saved `gpt-5.4-mini` and
`gpt-5.5` first-turn outputs; it is not completed human validation.

```bash
conda run -n reprompt_tax python scripts/make_human_audit_packet.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --scores results/scores/openai_gpt54mini_stress_v02_full120_auto_scores.jsonl \
    results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl \
  --out-dir data/current_model_human_audit \
  --packet-version v0.2_current_gpt5 \
  --seed 29 \
  --prefer-failures

conda run -n reprompt_tax python scripts/validate_current_model_human_audit_packet.py

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

Prepare and validate the separate v0.3 coverage native-review packet:

```bash
conda run -n reprompt_tax python scripts/make_coverage_native_review_packet_v03.py
conda run -n reprompt_tax python scripts/validate_coverage_native_review_packet_v03.py
conda run -n reprompt_tax python scripts/make_coverage_native_review_sheets_v03.py
conda run -n reprompt_tax python scripts/validate_coverage_native_review_sheets_v03.py
conda run -n reprompt_tax python scripts/analyze_coverage_native_review_design_v03.py
conda run -n reprompt_tax python scripts/test_coverage_native_review_completion.py
conda run -n reprompt_tax python scripts/test_coverage_native_review_adjudication.py
```

Regenerate the pre-specified human/native-review acceptance gates before using
completed labels to widen claims:

```bash
conda run -n reprompt_tax python scripts/analyze_human_audit_acceptance_rules.py
conda run -n reprompt_tax python scripts/validate_human_audit_acceptance_rules.py
conda run -n reprompt_tax python scripts/analyze_label_collection_launch_pack.py
conda run -n reprompt_tax python scripts/validate_label_collection_launch_pack.py
```

Run a bounded, aggregate-only WildChat repair-cue discovery scan:

```bash
conda run -n reprompt_tax python scripts/discover_repair_cues.py \
  --dataset allenai/WildChat \
  --split train \
  --max-conversations 20000 \
  --out-dir results/discovery/wildchat_20k_repair_cues
```
