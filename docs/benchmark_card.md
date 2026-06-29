# RePromptTax Benchmark Card

## Name

RePromptTax-Stress-v0.2 is the paper-facing benchmark. The repository also
contains historical v0.1 files and a v0.3 synthetic coverage scaffold, but v0.3
is not paper-facing benchmark evidence until native review is completed.

## Purpose

RePromptTax measures hidden interaction costs for multilingual and
code-switched LLM users: extra turns, token overhead, and unresolved repair
trajectories caused by failures in language choice, script, literal
preservation, register, locale, or task interpretation.

The benchmark is a stress pilot and progress probe. It is not a prevalence
estimate for real user populations.

## Paper-Facing Scope

- Dataset: `data/benchmark_stress_v0.2.jsonl`
- Size: 120 synthetic stress items
- Language pairs: Spanish-English, Hindi-English, Arabic-English
- Task families: `editing_preservation`, `output_language_inference`,
  `quote_preservation`, and `script_register_locale`
- Cell design: 3 language pairs x 4 task families x 10 items
- Repair budget: two standardized repair prompts per failed first turn

Historical files:

- `data/benchmark_v0.1.jsonl`: easier standard pilot retained for comparison
- `data/benchmark_stress_v0.1.jsonl`: 60-row stress precursor retained for
  diagnostics

Supplemental scaffold:

- `data/benchmark_stress_v0.3_expansion.jsonl`: 60 synthetic rows covering
  non-English target-content editing and cross-language preservation slices
- v0.3 has launch-ready native-review packets and small model smokes, but it is
  not paper-facing benchmark evidence before native validation and a
  pre-specified larger run are complete

## Schema

Each v0.2 JSONL row includes:

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
logs, private user text, real addresses, or sensitive personal data.

Stress items focus on:

- implicit preservation of English content during Spanish, Arabic, or Hinglish
  editing instructions
- preservation of semantically transparent quoted headings
- literal preservation of dates, filenames, names, and amounts
- script, register, locale, and casual-message constraints

An aggregate-only WildChat repair-cue scan motivates the taxonomy. It writes
hashed metadata and aggregate counts only; it does not release raw conversation
text and should not be treated as prevalence evidence.

## Intended Use

- Compare first-turn global alignment across model families
- Measure re-prompt turn tax under a fixed repair protocol
- Diagnose failure types by task family and language pair
- Evaluate lightweight prompt-level mitigations
- Track progress from GPT-4.1-family runs to GPT-5.x current-model refresh rows
- Run compact future smoke checks with `data/stress_v02_sentinel24_ids.txt`,
  then confirm any paper-facing claim on the full 120-item benchmark

## Out-of-Scope Use

- Do not treat this benchmark as representative of all multilingual,
  code-switched, Spanish, Hindi, Arabic, or English-speaking users.
- Do not use it to estimate prevalence of re-prompt tax in real deployments.
- Do not use it as a native-speaker quality benchmark without completed
  native/near-native validation.
- Do not treat automatic scores or LLM-judge audits as native-speaker
  validation.
- Do not use v0.3 model smokes or the 24-item v0.3 pilot as paper-facing
  benchmark evidence before native review is completed.
- Do not claim the mitigation fully solves multilingual interaction failures or
  that it generalizes across providers.

## Validation Status

Benchmark hygiene:

- `paper/benchmark_quality_audit_v02.md` reports 120 unique prompts, zero
  normalized duplicate prompts, complete required-marker and known-bad-output
  coverage, and zero privacy-marker hits under the release regexes.
- `scripts/validate_paper_claims.py` checks benchmark balance, core metric
  values, claim boundaries, and manifest freshness.

Model-result evidence:

- The paper-facing table includes three GPT-4.1-family full runs and a
  GPT-5.x current-model refresh on `gpt-5.4-mini` and `gpt-5.5`.
- `gpt-5.5`: FTGA rises from 81.7% to 98.3% under the Global Interaction
  Contract, mean RTT falls from 0.225 to 0.017, and unresolved trajectories
  fall to 0.0%.
- `gpt-5.4-mini`: FTGA rises from 80.0% to 85.0%, but the FTGA uncertainty
  interval crosses zero and unresolved rate increases from 2.5% to 5.0%.
- All-five-model sensitivity checks report a +10.2 point aggregate FTGA effect
  over 600 paired model-item rows, with 67 contract fixes and 6 regressions.
- Balanced 48-item stratified pilots recover the all-model and `gpt-5.5`
  positive directions in 100.0% of saved-trajectory simulations. Smaller-effect
  models remain less stable, so full claims stay anchored to the 120-item runs.
- The 24-item sentinel suite covers all 12 language-family cells and captures
  all GPT-5.5 contract residual items plus 95.0% of GPT-5.x contract failure
  pairs; it is for future fast checks, not headline benchmark evidence.

Scorer checks:

- A synthetic scorer challenge audit over 390 known-bad probes fails all probes
  and detects every expected deterministic failure signal.
- The release includes two blinded LLM-judge audits over the same 72-row sample.
- A blinded GPT-4.1 judge audit agrees with the automatic scorer on 71/72
  sampled first-turn pass/fail labels.
- A paired GPT-5.5 judge refresh agrees with the automatic scorer on 70/72
  sampled labels and with the GPT-4.1 judge on 69/72 labels.
- These are scorer sanity checks, not native/near-native validation.

Human/native validation status:

- Native/near-native validation has not been completed.
- The release has three launch-ready annotation surfaces: the original 72-row v0.2
  human/native audit, a 48-row current-model GPT-5.x human/native audit, and a
  60-row v0.3 coverage native-review packet.
- Together these surfaces contain 180 reviewer-facing rows, 18 roster-template
  slots, and 12 static browser review sheets.
- Stronger claims require completed labels, qualified rosters, and the
  pre-specified gates in `paper/human_audit_acceptance_rules_v02.md`.

## Reproduction

Regenerate the v0.2 stress benchmark and quality audit:

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

Run the full local submission gate without API calls:

```bash
conda run -n reprompt_tax python scripts/run_submission_checks.py
```

Validate release-facing documentation and artifact hashes:

```bash
conda run -n reprompt_tax python scripts/validate_release_docs.py
conda run -n reprompt_tax python scripts/make_artifact_manifest.py --check
```
