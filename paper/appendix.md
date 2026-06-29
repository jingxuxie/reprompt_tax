# Appendix: RePromptTax Stress Pilot

## A. Artifact Map

- Plan: `reprompt_tax_workshop_paper_plan.md`
- Original stress benchmark: `data/benchmark_stress_v0.1.jsonl`
- Paper-facing stress benchmark: `data/benchmark_stress_v0.2.jsonl`
- Remaining full-v0.2 run IDs: `data/stress_v02_remaining_36_ids.txt`
- Expanded follow-up probe IDs: `data/stress_v02_new_balanced_24_ids.txt`
- Standard pilot benchmark: `data/benchmark_v0.1.jsonl`
- System prompts: `prompts/baseline_system.txt`,
  `prompts/content_preservation_system.txt`,
  `prompts/generic_helpfulness_system.txt`,
  `prompts/global_interaction_contract.txt`
- Model runner: `scripts/run_models.py`
- Automatic scorer: `scripts/score_auto.py`
- Scorer regression tests: `scripts/test_score_auto.py`
- Judge audit: `scripts/judge_outputs.py`
- Judge agreement analysis: `scripts/analyze_judge_agreement.py`
- Judge refresh analysis: `scripts/analyze_judge_refresh.py`
- Judge refresh validator: `scripts/validate_judge_refresh.py`
- Metrics: `scripts/compute_metrics.py`
- Full v0.2 score merge: `scripts/build_full_v02_scores.py`
- Benchmark-quality audit: `scripts/analyze_benchmark_quality.py`
- Paired mitigation effects: `scripts/paired_effects.py`
- Paired sign-test sensitivity: `scripts/paired_significance.py`
- Language-slice analysis: `scripts/analyze_language_slices.py`
- Repair-dynamics analysis: `scripts/analyze_repair_dynamics.py`
- Token-burden analysis: `scripts/analyze_token_burden.py`
- Prompt-control diagnostic: `scripts/analyze_prompt_control.py`
- Prompt-ablation diagnostic: `scripts/analyze_prompt_ablation.py`
- Failure-mode analysis: `scripts/analyze_failure_modes.py`
- Scorer-component breakdown: `scripts/analyze_component_breakdown.py`
- Error atlas: `scripts/build_error_atlas.py`
- Experiment ledger: `scripts/summarize_experiment_ledger.py`
- Artifact manifest generator: `scripts/make_artifact_manifest.py`
- Claim-boundary lint: `scripts/lint_claim_boundaries.py`
- Paper validator: `scripts/validate_paper_claims.py`
- Related-work positioning note: `paper/related_work_positioning_v02.md`
- Qualitative example validator: `scripts/validate_qualitative_examples.py`
- Stress benchmark validator: `scripts/validate_stress_benchmark.py`
- Follow-up probe validator: `scripts/validate_followup_probe.py`
- Human audit packet generator: `scripts/make_human_audit_packet.py`
- Human audit packet validator: `scripts/validate_human_audit_packet.py`
- Human audit design analysis: `scripts/analyze_human_audit_design.py`
- Completed human audit validator: `scripts/validate_completed_human_audit.py`
- Human audit summarizer: `scripts/summarize_human_audit.py`
- Discovery cue analysis: `scripts/analyze_discovery_cues.py`
- Main tables: `results/tables/openai_three_model_stress_v02_full120/`
- Paired effect tables:
  `results/tables/openai_three_model_stress_v02_full120/paired_contract_effects_by_model.csv`,
  `results/tables/openai_three_model_stress_v02_full120/paired_contract_effects_by_family.csv`
- Paired sign-test sensitivity:
  `results/tables/openai_three_model_stress_v02_full120/paired_significance_by_model.csv`,
  `paper/paired_significance_v02_full120.md`
- Language-slice analysis:
  `results/tables/openai_three_model_stress_v02_full120/language_slice_metrics.csv`,
  `results/tables/openai_three_model_stress_v02_full120/language_slice_paired_effects.csv`,
  `results/tables/openai_three_model_stress_v02_full120/language_slice_aggregate_effects.csv`,
  `paper/language_slice_analysis_v02_full120.md`
- Repair-dynamics analysis:
  `results/tables/openai_three_model_stress_v02_full120/repair_dynamics_by_model_condition.csv`,
  `results/tables/openai_three_model_stress_v02_full120/repair_paired_effects_by_model.csv`,
  `results/tables/openai_three_model_stress_v02_full120/repair_rtt_transition_by_model.csv`,
  `paper/repair_dynamics_v02_full120.md`
- Benchmark-quality audit:
  `results/tables/benchmark_quality_v02/benchmark_quality_summary.csv`,
  `results/tables/benchmark_quality_v02/benchmark_quality_by_family.csv`,
  `results/tables/benchmark_quality_v02/benchmark_quality_by_language_family.csv`,
  `paper/benchmark_quality_audit_v02.md`
- Token-burden analysis:
  `results/tables/openai_three_model_stress_v02_full120/token_burden_by_model.csv`,
  `results/tables/openai_three_model_stress_v02_full120/token_burden_paired_effects_by_model.csv`,
  `paper/token_burden_analysis_v02_full120.md`
- Prompt-control diagnostic:
  `results/tables/openai_nano_stress_v02_full120_prompt_control/`,
  `paper/prompt_control_analysis.md`
- Prompt-ablation diagnostic:
  `results/tables/openai_nano_stress_v02_full120_content_preservation/`,
  `results/tables/openai_nano_stress_v02_full120_prompt_ablation/`,
  `paper/prompt_ablation_analysis.md`
- Failure-mode analysis:
  `results/tables/openai_three_model_stress_v02_full120/family_effect_summary.csv`,
  `results/tables/openai_three_model_stress_v02_full120/failure_type_summary.csv`,
  `paper/failure_mode_analysis_v02_full120.md`
- Item-consistency analysis:
  `results/tables/openai_three_model_stress_v02_full120/item_consistency_summary.csv`,
  `results/tables/openai_three_model_stress_v02_full120/item_consistency_by_family.csv`,
  `results/tables/openai_three_model_stress_v02_full120/item_consistency_hardest_items.csv`,
  `paper/item_consistency_analysis_v02_full120.md`
- Scorer-component breakdown:
  `results/tables/openai_three_model_stress_v02_full120/component_pass_by_model_condition.csv`,
  `results/tables/openai_three_model_stress_v02_full120/component_pass_by_family_condition.csv`,
  `results/tables/openai_three_model_stress_v02_full120/component_paired_effects_by_model.csv`,
  `paper/component_breakdown_v02_full120.md`
- Scorer-ablation sensitivity:
  `results/tables/openai_three_model_stress_v02_full120/scorer_ablation_by_condition.csv`,
  `results/tables/openai_three_model_stress_v02_full120/scorer_ablation_by_family_condition.csv`,
  `results/tables/openai_three_model_stress_v02_full120/scorer_ablation_failure_signatures.csv`,
  `paper/scorer_ablation_sensitivity_v02_full120.md`
- Error atlas:
  `results/tables/openai_three_model_stress_v02_full120/first_turn_error_atlas.csv`,
  `paper/error_atlas_v02_full120.md`
- Experiment ledger:
  `results/tables/experiment_ledger_v02/experiment_ledger_summary.csv`,
  `results/tables/experiment_ledger_v02/api_usage_by_artifact.csv`,
  `results/tables/experiment_ledger_v02/api_usage_by_model_condition.csv`,
  `results/tables/experiment_ledger_v02/api_usage_by_judge.csv`,
  `paper/experiment_ledger_v02.md`
- Judge audit tables:
  `results/tables/openai_three_model_stress_v02_full120_judge_audit72/`
- Judge agreement analysis:
  `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_agreement_summary.csv`,
  `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_component_agreement.csv`,
  `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_component_disagreements.csv`,
  `paper/judge_agreement_analysis_v02_full120.md`
- Human audit packet: `data/human_audit/human_audit_packet_v0.2.csv`
- Human audit design audit:
  `results/tables/human_audit_v0.2_design/`,
  `paper/human_audit_design_audit_v02.md`
- Human audit manifest: `data/human_audit/audit_manifest_v0.2.md`
- Human audit launch checklist:
  `data/human_audit/human_audit_launch_checklist_v0.2.md`
- Human audit completion plan: `paper/human_audit_completion_plan.md`
- Real-world cue discovery summary:
  `results/discovery/wildchat_20k_repair_cues/summary.json`
- Discovery cue analysis:
  `results/discovery/wildchat_20k_repair_cues/cue_discovery_overview.csv`,
  `results/discovery/wildchat_20k_repair_cues/cue_category_conversation_counts.csv`,
  `results/discovery/wildchat_20k_repair_cues/cue_pattern_counts.csv`,
  `paper/discovery_cue_analysis.md`
- Paper PDF: `paper/main.pdf`
- Claim-evidence checklist: `paper/claim_evidence_checklist.md`
- Artifact manifest: `paper/artifact_manifest.json`,
  `paper/artifact_manifest.md`

## B. Stress Benchmark Schema

Each JSONL item has:

```json
{
  "id": "es_en_SA_001",
  "language_pair": "es-en",
  "task_family": "editing_preservation",
  "user_prompt": "...",
  "instruction_language": "...",
  "content_language": "...",
  "expected_response_language": "English",
  "expected_script": "Latin",
  "must_preserve_spans": [],
  "register_requirement": "...",
  "locale_requirement": null,
  "known_bad_outputs": ["translation into instruction language"],
  "repair_prompt_1": "Please keep the rewritten text in English.",
  "repair_prompt_2": "Do not translate. Output only the polished English version.",
  "required_any_markers": ["..."],
  "forbidden_markers": ["..."],
  "notes_for_annotators": "...",
  "stress_tag": "implicit_content_language"
}
```

## C. Scoring Rubric

A response passes only if all component checks pass:

- `language_pass`: output language matches the expected response language.
- `script_pass`: output uses the expected script and avoids forbidden scripts.
- `preservation_pass`: all `must_preserve_spans` appear exactly.
- `task_pass`: the requested transformation is completed.
- `register_locale_pass`: output respects the requested register, tone, and
  locale/literal-data constraints.

Failure types:

- `wrong_output_language`
- `script_mismatch`
- `preservation_failure`
- `task_noncompletion`
- `register_locale_mismatch`

The automatic scorer is intentionally conservative and transparent. Exact span
and script checks are objective. Language/task checks use marker lists and are
audited with a blinded LLM judge.

## D. Judge Audit Protocol

The blinded judge audit samples 72 first-turn responses:

- 3 models,
- 2 conditions,
- 4 task families,
- 3 examples per model/condition/family stratum.

The judge sees:

- user prompt,
- expected response language,
- expected script,
- required preserved spans,
- register and locale requirements,
- task family,
- known bad outputs,
- assistant response.

The judge does not see:

- model identity in the prompt,
- baseline vs contract condition in the prompt,
- automatic score.

Command:

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
```

Summary:

```bash
conda run -n reprompt_tax python scripts/summarize_judge_audit.py \
  --audit results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl \
  --out-dir results/tables/openai_three_model_stress_v02_full120_judge_audit72

conda run -n reprompt_tax python scripts/analyze_judge_agreement.py \
  --audit results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --out-dir results/tables/openai_three_model_stress_v02_full120_judge_audit72 \
  --out-md paper/judge_agreement_analysis_v02_full120.md
```

Current result: 71/72 pass-fail agreement with the corrected automatic scorer.

The paired `gpt-5.5` judge refresh reuses the same blinded 72-row sample and
checks scorer agreement under a current judge model:

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

Current refresh result: the `gpt-5.5` judge agrees with the automatic scorer on
70/72 sampled pass/fail labels and with the `gpt-4.1` judge on 69/72 labels.

## E. Main Reproduction Commands

Generate benchmark:

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

Build the full paper-facing score file from saved shards:

```bash
conda run -n reprompt_tax python scripts/build_full_v02_scores.py
```

Compute metrics:

```bash
conda run -n reprompt_tax python scripts/compute_metrics.py \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --out-dir results/tables/openai_three_model_stress_v02_full120
```

Compute paired mitigation effects:

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

conda run -n reprompt_tax python scripts/analyze_token_burden.py \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --out-dir results/tables/openai_three_model_stress_v02_full120 \
  --out-md paper/token_burden_analysis_v02_full120.md

conda run -n reprompt_tax python scripts/summarize_experiment_ledger.py \
  --out-dir results/tables/experiment_ledger_v02 \
  --out-md paper/experiment_ledger_v02.md
```

Make figures:

```bash
conda run -n reprompt_tax python scripts/make_figures.py \
  --tables-dir results/tables/openai_three_model_stress_v02_full120 \
  --extra-summary results/tables/openai_gpt54mini_stress_v02_full120/metrics_summary.csv \
  --extra-summary results/tables/openai_gpt55_stress_v02_full120/metrics_summary.csv \
  --extra-trajectories results/tables/openai_gpt54mini_stress_v02_full120/trajectory_metrics.csv \
  --extra-trajectories results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv \
  --out-dir results/figures/openai_three_model_stress_v02_full120
```

Run the full local submission gate:

```bash
conda run -n reprompt_tax python scripts/run_submission_checks.py
```

Validate paper claims:

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
conda run -n reprompt_tax python scripts/test_score_auto.py
conda run -n reprompt_tax python scripts/lint_claim_boundaries.py
conda run -n reprompt_tax python scripts/validate_paper_claims.py
```

Analyze saved discovery cue metadata without raw text:

```bash
conda run -n reprompt_tax python scripts/analyze_discovery_cues.py \
  --summary results/discovery/wildchat_20k_repair_cues/summary.json \
  --metadata results/discovery/wildchat_20k_repair_cues/hit_metadata_hashed.csv \
  --out-dir results/discovery/wildchat_20k_repair_cues \
  --out-md paper/discovery_cue_analysis.md
```

Validate qualitative examples:

```bash
conda run -n reprompt_tax python scripts/validate_qualitative_examples.py
```

Validate the artifact manifest:

```bash
conda run -n reprompt_tax python scripts/make_artifact_manifest.py --check
```

Build paper:

```bash
cd paper
latexmk -pdf -interaction=nonstopmode main.tex
```

## F. Qualitative Example Index

Detailed examples are in `paper/qualitative_examples.md`.
They are checked against saved score rows and trajectory metrics by
`scripts/validate_qualitative_examples.py`.

- `es_en_SA_004`, `gpt-4.1-nano`, baseline: unwanted translation during
  editing; RTT = 1.
- `es_en_SA_004`, `gpt-4.1`, baseline vs contract: strong-model preamble tax
  eliminated by contract prompt.
- `ar_en_SC_002`, `gpt-4.1-nano`, baseline: unresolved quote-preservation case
  after two repairs.
- `ar_en_SC_002`, `gpt-4.1-nano`, contract: quote preservation repaired after
  one follow-up.
- `hi_en_SD_005`, `gpt-4.1-nano`, baseline: literal filename preserved, but
  Hindi/Hinglish style ignored until repair.

## G. Remaining Validation Needed

Before making strong final claims:

- complete the prepared 72-row native or near-native speaker audit,
- verify Arabic and Hindi/Hinglish register judgments,
- optionally add one non-OpenAI provider for provider diversity,
- optionally expand beyond the 120-item stress pilot after the audit is complete,
- keep claims scoped to synthetic stress testing unless real-log discovery is
  added.

## H. Human Audit Packet

A balanced 72-row human audit packet is prepared in `data/human_audit/`.

Design:

- 3 language pairs,
- 4 task families,
- 3 models,
- 2 conditions,
- 1 first-turn output per language/model/condition/family stratum.

Files:

- `human_audit_packet_v0.2.csv`: full blinded packet.
- `human_audit_packet_v0.2_es-en.csv`: Spanish-English slice.
- `human_audit_packet_v0.2_hi-en.csv`: Hindi-English slice.
- `human_audit_packet_v0.2_ar-en.csv`: Arabic-English slice.
- `human_audit_answer_key_v0.2.csv`: private mapping to model, condition, and
  automatic labels.
- `human_audit_annotator_roster_template_v0.2.csv`: template for recording
  annotator IDs, language competence, script competence, qualification notes,
  and conflict-of-interest status.
- `paper/human_audit_design_audit_v02.md`: design-readiness audit for the
  launch packet.

Annotators should receive only the packet file for the language slice they can
validate. The guide is `docs/human_audit_guide.md`.

To generate the packet:

```bash
conda run -n reprompt_tax python scripts/make_human_audit_packet.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --out-dir data/human_audit \
  --seed 23
```

To validate packet launch readiness:

```bash
conda run -n reprompt_tax python scripts/validate_human_audit_packet.py
```

To analyze the packet design before annotation:

```bash
conda run -n reprompt_tax python scripts/analyze_human_audit_design.py \
  --packet data/human_audit/human_audit_packet_v0.2.csv \
  --answer-key data/human_audit/human_audit_answer_key_v0.2.csv \
  --out-dir results/tables/human_audit_v0.2_design \
  --out-md paper/human_audit_design_audit_v02.md
```

To summarize completed annotations:

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

Any `human_audit_packet_v0.2_smoke_completed.csv` file is only a plumbing test
created by copying automatic labels into the human fields. It is not human
validation and should not be cited as such.

## I. Real-World Repair Cue Discovery

We ran a bounded, aggregate-only cue scan over the first 20,000 streamed
WildChat conversations. The script writes no raw user text.

Command:

```bash
conda run -n reprompt_tax python scripts/discover_repair_cues.py \
  --dataset allenai/WildChat \
  --split train \
  --max-conversations 20000 \
  --out-dir results/discovery/wildchat_20k_repair_cues
```

Output summary:

- conversations scanned: 20,000,
- user turns scanned: 58,764,
- multi-turn conversations: 10,681,
- conversations with repair cues: 172,
- total cue hits: 219.

Category counts:

- generic repair: 93,
- wrong output language: 68,
- preservation failure: 25,
- register/locale mismatch: 16,
- unwanted translation: 13,
- script mismatch: 4.

This scan is used only as a motivation check. It is not a representative
prevalence estimate, because the cue list is incomplete and the sample is a
bounded streamed slice.
