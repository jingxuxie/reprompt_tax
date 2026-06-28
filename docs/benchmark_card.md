# RePromptTax Benchmark Card

## Name

RePromptTax-Stress-v0.2

## Purpose

Measure hidden interaction costs for multilingual and code-switched LLM users:
extra turns, tokens, and unresolved repair trajectories caused by failures in
language, script, quote/literal preservation, register, locale, or task
interpretation.

## Scope

- Size: 120 stress items.
- Language pairs: Spanish-English, Hindi-English, Arabic-English.
- Task families:
  - `editing_preservation`
  - `output_language_inference`
  - `quote_preservation`
  - `script_register_locale`
- Design: 3 language pairs x 4 task families x 10 items.

The standard pilot `data/benchmark_v0.1.jsonl` has 120 easier items and is kept
for comparison. The paper-facing result uses `data/benchmark_stress_v0.2.jsonl`.
The original `data/benchmark_stress_v0.1.jsonl` has 60 stress items and is kept
for historical diagnostics. The v0.2 benchmark preserves the v0.1 item IDs for
the first five cases in each cell and adds five new cases per cell.

## Schema

Each JSONL row includes:

- `id`
- `language_pair`
- `task_family`
- `user_prompt`
- `instruction_language`
- `content_language`
- `expected_response_language`
- `expected_script`
- `must_preserve_spans`
- `register_requirement`
- `locale_requirement`
- `known_bad_outputs`
- `repair_prompt_1`
- `repair_prompt_2`
- `required_any_markers`
- `forbidden_markers`
- `notes_for_annotators`
- `stress_tag`

## Item Creation

Items are synthetic and template-driven. They do not contain raw public chat
logs, real addresses, real private user text, or sensitive personal data.

Stress items focus on failure modes observed in the initial pilot:

- implicit preservation of English content during Spanish/Arabic/Hinglish
  editing instructions,
- preservation of semantically transparent quoted headings,
- literal preservation of dates, filenames, names, and amounts,
- script and casual messaging constraints.

A separate aggregate-only WildChat scan is included as a motivation check for
the taxonomy. It does not release raw public conversation text and is not used
as benchmark data.

## Intended Use

- Compare first-turn global alignment across models.
- Measure re-prompt turn tax under a fixed repair protocol.
- Diagnose failure types by task family and language pair.
- Evaluate lightweight prompt-level mitigations.

## Out-of-Scope Use

- Do not treat this benchmark as representative of all Spanish, Hindi, Arabic,
  English, or code-switched users.
- Do not use it as a native-speaker quality benchmark without additional human
  validation.
- Do not use the synthetic prompts to infer population-level behavior.

## Validation Status

- Automatic scoring checks exact span preservation, script, and rule-based
  language/task markers.
- A deterministic benchmark-quality audit checks balance, duplicate prompts,
  scoring-marker coverage, preservation-span coverage, prompt lengths, and
  privacy-like markers. The v0.2 audit reports 120 unique prompts, zero
  normalized duplicate prompts, and zero privacy-marker hits under the audit
  regexes.
- A blinded `gpt-4.1` judge audit covers 72 first-turn stress responses:
  3 samples per model/condition/task-family stratum.
- Corrected auto scorer and judge agree on 71/72 sampled pass/fail labels
  (98.6%); the one disagreement is reported as a limitation.
- Native-speaker validation remains a required next step before strong final
  claims.

## Reproduction

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

Validate paper-facing claims:

```bash
conda run -n reprompt_tax python scripts/validate_paper_claims.py
```
