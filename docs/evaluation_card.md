# RePromptTax Evaluation Card

## Model Runs

The paper-facing evaluation combines the original GPT-4.1-family stress runs
with a GPT-5.x current-model refresh.

Full 120-item v0.2 stress runs:

- `gpt-4.1-nano`
- `gpt-4.1-mini`
- `gpt-4.1`
- `gpt-5.4-mini`
- `gpt-5.5`

All saved OpenAI model outputs were generated on June 28, 2026 with
temperature 0 and a maximum output budget of 256 tokens per response.

Supporting diagnostics include:

- `generic_helpfulness` on `gpt-4.1-nano`
- `content_preservation` on `gpt-4.1-nano`, `gpt-5.4-mini`, and `gpt-5.5`
- a 24-row repair-realism diagnostic over dominant editing-preservation
  failures
- six-row and 24-row v0.3 coverage smokes/pilots that remain non-headline
  diagnostics until native review is complete

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

### Generic Helpfulness

The generic-helpfulness control is a longer general assistant prompt. It checks
whether mitigation gains come from generic scaffolding rather than the
multilingual interaction contract.

Full prompt: `prompts/generic_helpfulness_system.txt`.

### Content Preservation

The content-preservation prompt is a narrower mechanism diagnostic focused on
preserving the language and literal form of quoted or target content.

Full prompt: `prompts/content_preservation_system.txt`.

## Repair Protocol

For each item/model/condition:

1. Send the original user prompt.
2. Score the first response.
3. If it passes, set RTT to 0.
4. If it fails, append `repair_prompt_1`.
5. If the second response passes, set RTT to 1.
6. If it fails, append `repair_prompt_2`.
7. If the third response passes, set RTT to 2.
8. Otherwise mark unresolved with RTT = 3.

The runner stops after the first automatically passing turn to conserve API
budget.

## Metrics

- FTGA: first-turn global alignment.
- RTT: re-prompt turn tax.
- Repair@1: share of first-turn failures repaired by the first repair prompt.
- Repair@2: share of first-turn failures repaired within two repair prompts.
- Unresolved rate: share unresolved after two repair prompts.
- Token tax: total tokens until success or exhaustion divided by first-attempt
  tokens.

Token tax is not dollar cost. The all-five-model efficiency analysis shows that
the contract lowers normalized token tax while increasing absolute total tokens
for every full-run model.

## Scoring

Automatic scoring is implemented in `scripts/score_auto.py`; deterministic
regression tests are in `scripts/test_score_auto.py`.

Scorer components include:

- exact preservation of `must_preserve_spans`
- script checks for Latin, Arabic, and Devanagari ranges
- forbidden marker checks
- required marker checks for known valid task outputs
- language, task, register, and locale rules where deterministic checks are
  possible

The automatic scorer is intentionally conservative and weakest for nuanced
register, locale, cultural appropriateness, and borderline helpfulness
judgments.

## Main Evaluation Evidence

Current-model refresh:

- `paper/current_model_refresh_v02.md`
- `paper/current_model_uncertainty_v02.md`
- `paper/current_model_error_analysis_v02.md`
- `paper/current_model_heterogeneity_v02.md`
- `paper/current_model_regression_risk_v02.md`

Headline boundary:

- `gpt-5.5` improves from 81.7% to 98.3% FTGA under the contract, with 20
  paired first-turn fixes and zero first-turn regressions.
- The remaining two `gpt-5.5` contract first-turn failures are both
  Spanish-English editing-preservation rows and both repair in one turn.
- `gpt-5.4-mini` improves from 80.0% to 85.0% FTGA, but its uncertainty
  interval crosses zero, it has five first-turn regressions, and its unresolved
  rate rises under the contract.

Prompt mechanism:

- `paper/current_prompt_mechanism_gpt54mini_v02.md`
- `paper/current_prompt_mechanism_gpt55_v02.md`

Content-preservation scaffolding is close to the full contract on current
models: 85.8% vs 85.0% FTGA on `gpt-5.4-mini`, and 99.2% vs 98.3% on
`gpt-5.5`. This supports a preservation-mechanism interpretation but does not
establish prompt dominance.

Repair realism:

- `paper/repair_realism_editing_baseline24.md`

Saved standard and terse repairs recover 24/24 sampled dominant failures,
whereas a frustrated repair recovers 17/24 and an explicit source-language
contract repair recovers 5/24. This is a controlled diagnostic, not a user
study.

Judge audits:

- `paper/judge_agreement_analysis_v02_full120.md`
- `paper/judge_refresh_gpt55_v02_full120.md`

The GPT-4.1 judge audit agrees with the automatic scorer on 71/72 sampled
first-turn pass/fail labels. The paired GPT-5.5 judge refresh agrees with the
automatic scorer on 70/72 labels and with the GPT-4.1 judge on 69/72 labels.
These audits support scorer sanity checks but do not replace native/near-native
validation.

## Human/Native Validation Status

Human/native validation is launch-ready but not completed human validation.

Prepared surfaces:

- Original v0.2 human/native audit: 72 reviewer-facing rows
- Current-model GPT-5.x human/native audit: 48 reviewer-facing rows
- v0.3 coverage native review: 60 reviewer-facing rows

The consolidated launch pack in `paper/label_collection_launch_pack_v02.md`
tracks 180 reviewer-facing rows, 18 roster-template slots, 12 static browser
review sheets, finalization commands, adjudication commands, and claim gates.
Future completed labels must pass `paper/human_audit_acceptance_rules_v02.md`
before any claim is widened.

## API Usage and Provenance

The experiment ledger reports 1,504 saved API response rows:

- 1,288 model-response rows
- 72 repair-variant rows
- 144 judge-audit rows

Saved provider-reported usage totals 285,930 tokens. The ledger reports token
usage only and does not estimate dollar cost because provider prices change.

## Reproduction Commands

Run the full local submission gate with no API calls:

```bash
conda run -n reprompt_tax python scripts/run_submission_checks.py
```

Run focused validators:

```bash
conda run -n reprompt_tax python scripts/test_score_auto.py
conda run -n reprompt_tax python scripts/lint_claim_boundaries.py
conda run -n reprompt_tax python scripts/validate_release_docs.py
conda run -n reprompt_tax python scripts/validate_result_card.py
conda run -n reprompt_tax python scripts/validate_paper_claims.py
conda run -n reprompt_tax python scripts/make_artifact_manifest.py --check
```

Regenerate saved current-model summaries without API calls:

```bash
conda run -n reprompt_tax python scripts/analyze_current_model_refresh.py
conda run -n reprompt_tax python scripts/validate_current_model_refresh.py
conda run -n reprompt_tax python scripts/analyze_current_prompt_mechanism.py
conda run -n reprompt_tax python scripts/validate_current_prompt_mechanism.py
conda run -n reprompt_tax python scripts/analyze_efficiency_tradeoff.py
conda run -n reprompt_tax python scripts/validate_efficiency_tradeoff.py
```

Real API-spending commands and caps are documented in `README.md`. Use cached
JSONL outputs and the local validators before making any new API calls.
