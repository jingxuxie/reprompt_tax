# RePromptTax Evaluation Card

## Models

Paper-facing stress runs evaluate:

- `gpt-4.1-nano`
- `gpt-4.1-mini`
- `gpt-4.1`

All model outputs were generated on June 28, 2026 with temperature 0 and a
maximum output budget of 256 tokens per response.

## Conditions

### Baseline

```text
You are a helpful assistant.
```

### Global Interaction Contract

The contract prompt instructs the model to infer the user's interaction
contract before answering: instruction language, content language, preservation
requirements, script, register, locale, and whether an edit should preserve the
source content language.

Full prompt: `prompts/global_interaction_contract.txt`.

## Repair Protocol

For each item/model/condition:

1. Send the original user prompt.
2. Score the first response.
3. If it passes, RTT = 0.
4. If it fails, append `repair_prompt_1`.
5. If the second response passes, RTT = 1.
6. If it fails, append `repair_prompt_2`.
7. If the third response passes, RTT = 2.
8. Otherwise mark unresolved with RTT = 3.

The runner stops after the first automatically passing turn to conserve API
budget.

Paper-facing API usage is summarized in `paper/experiment_ledger_v02.md`. The
ledger reports saved response rows and provider-reported token usage; it does
not estimate dollar cost because provider prices change.

## Metrics

- FTGA: first-turn global alignment.
- RTT: re-prompt turn tax.
- Repair@1: share of first-turn failures repaired by the first repair prompt.
- Repair@2: share of first-turn failures repaired within two repair prompts.
- Unresolved rate: share unresolved after two repair prompts.
- Token tax: total tokens until success divided by first-attempt tokens.

## Scoring

Automatic scoring is implemented in `scripts/score_auto.py`.
Regression coverage for the deterministic scorer is in
`scripts/test_score_auto.py`.

Deterministic checks:

- exact preservation of `must_preserve_spans`,
- script checks for Latin, Arabic, and Devanagari ranges,
- forbidden marker checks,
- required marker checks for known valid task outputs.

Audit:

- `scripts/judge_outputs.py` runs blinded LLM-judge audits.
- `scripts/summarize_judge_audit.py` computes agreement summaries.
- `scripts/validate_qualitative_examples.py` checks selected qualitative
  examples against saved score rows and trajectory metrics.

## Reproduction Commands

Main three-model metric table:

```bash
conda run -n reprompt_tax python scripts/build_full_v02_scores.py

conda run -n reprompt_tax python scripts/compute_metrics.py \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --out-dir results/tables/openai_three_model_stress_v02_full120
```

Paired mitigation effects:

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
```

Failure-mode analysis:

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
```

Scorer regression tests:

```bash
conda run -n reprompt_tax python scripts/test_score_auto.py
```

Claim-boundary lint:

```bash
conda run -n reprompt_tax python scripts/lint_claim_boundaries.py
```

Experiment ledger:

```bash
conda run -n reprompt_tax python scripts/summarize_experiment_ledger.py \
  --out-dir results/tables/experiment_ledger_v02 \
  --out-md paper/experiment_ledger_v02.md
```

Full local submission gate, with no API calls:

```bash
conda run -n reprompt_tax python scripts/run_submission_checks.py
```

Artifact manifest:

```bash
conda run -n reprompt_tax python scripts/make_artifact_manifest.py
conda run -n reprompt_tax python scripts/make_artifact_manifest.py --check
```

Single-model generic-helpfulness prompt-control extension for the 60 v0.2 items
that are not in the original stress60 control. This is API-spending and capped
at 160 calls:

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

Regenerate the saved local full120 prompt-control diagnostic without API calls:

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

Single-model content-preservation prompt ablation on all 120 v0.2 stress items.
This is API-spending and capped at 220 calls:

```bash
conda run -n reprompt_tax python scripts/run_models.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --out results/model_outputs/openai_nano_stress_v02_full120_content_preservation.jsonl \
  --models gpt-4.1-nano \
  --conditions content_preservation \
  --max-output-tokens 256 \
  --max-api-calls 220
```

Regenerate the saved local full120 prompt-ablation diagnostic without API calls:

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

Expanded stress dry-run smoke, with no API calls:

```bash
conda run -n reprompt_tax python scripts/run_models.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --out results/model_outputs/dry_run_stress_v02.jsonl \
  --models dry-model \
  --conditions baseline,contract \
  --dry-run

conda run -n reprompt_tax python scripts/score_auto.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --outputs results/model_outputs/dry_run_stress_v02.jsonl \
  --out results/scores/dry_run_stress_v02_auto_scores.jsonl

conda run -n reprompt_tax python scripts/compute_metrics.py \
  --scores results/scores/dry_run_stress_v02_auto_scores.jsonl \
  --out-dir results/tables/dry_run_stress_v02
```

Historical bounded three-model probe on 24 new v0.2 items:

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

conda run -n reprompt_tax python scripts/score_auto.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --outputs results/model_outputs/openai_nano_stress_v02_new24.jsonl \
  --out results/scores/openai_nano_stress_v02_new24_auto_scores.jsonl

conda run -n reprompt_tax python scripts/score_auto.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --outputs results/model_outputs/openai_mini_gpt41_stress_v02_new24.jsonl \
  --out results/scores/openai_mini_gpt41_stress_v02_new24_auto_scores.jsonl

cat results/scores/openai_nano_stress_v02_new24_auto_scores.jsonl \
  results/scores/openai_mini_gpt41_stress_v02_new24_auto_scores.jsonl \
  > results/scores/openai_three_model_stress_v02_new24_auto_scores.jsonl

conda run -n reprompt_tax python scripts/compute_metrics.py \
  --scores results/scores/openai_three_model_stress_v02_new24_auto_scores.jsonl \
  --out-dir results/tables/openai_three_model_stress_v02_new24
```

Judge audit summary:

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

Paper build:

```bash
cd paper
latexmk -pdf -interaction=nonstopmode main.tex
```
