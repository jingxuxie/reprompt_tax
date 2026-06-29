# Human/Native Review Acceptance Rules

These rules pre-specify what future completed labels must show before
the paper can widen claims beyond automatic scoring plus LLM-judge
sanity checks. They are not completed human validation.

## Claim Gates

| Surface | Rows | Reviewer minimum | Acceptance rule | Claim if pass | Claim if fail |
|---|---:|---:|---|---|---|
| human_audit_v02_gpt41_family | 72 | 3 | completed-validator passes; pass agreement >=90%; component agreement >=85%; disagreements inspected before widening claims | native/near-native audit supports the automatic scorer on sampled first-turn labels | report disagreement pattern and keep the automatic-plus-LLM-judge claim boundary |
| human_audit_v02_current_gpt5 | 48 | 3 | completed-validator passes; pass agreement >=90%; component agreement >=85%; disagreements inspected before widening claims | native/near-native audit supports the automatic scorer on sampled first-turn labels | report disagreement pattern and keep the automatic-plus-LLM-judge claim boundary |
| coverage_native_review_v03 | 60 | 6 | completed native-review validator passes; all rows release usable; zero unresolved issue rows before v0.3 performance claims | v0.3 scaffold rows are native-review release usable; model performance still needs a pre-specified run | revise failed rows and relaunch native review before using v0.3 as paper-facing benchmark evidence |

## Numeric Thresholds

| Surface | Pass agreements | Component agreements | Release-usable rows |
|---|---:|---:|---:|
| human_audit_v02_gpt41_family | 65 | 306 |  |
| human_audit_v02_current_gpt5 | 44 | 204 |  |
| coverage_native_review_v03 |  |  | 60 |

## Required Commands

### human_audit_v02_gpt41_family

Validate completed labels:

```bash
conda run -n reprompt_tax python scripts/validate_completed_human_audit.py --annotations data/human_audit/human_audit_packet_v0.2_completed.csv --answer-key data/human_audit/human_audit_answer_key_v0.2.csv --annotator-roster data/human_audit/human_audit_annotator_roster_v0.2.csv --expected-models gpt-4.1,gpt-4.1-mini,gpt-4.1-nano
```

Summarize completed labels:

```bash
conda run -n reprompt_tax python scripts/summarize_human_audit.py --annotations data/human_audit/human_audit_packet_v0.2_completed.csv --answer-key data/human_audit/human_audit_answer_key_v0.2.csv --out-dir results/tables/human_audit_v0.2
```

### human_audit_v02_current_gpt5

Validate completed labels:

```bash
conda run -n reprompt_tax python scripts/validate_completed_human_audit.py --annotations data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_completed.csv --answer-key data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv --annotator-roster data/current_model_human_audit/human_audit_annotator_roster_v0.2_current_gpt5.csv --expected-models gpt-5.4-mini,gpt-5.5
```

Summarize completed labels:

```bash
conda run -n reprompt_tax python scripts/summarize_human_audit.py --annotations data/current_model_human_audit/human_audit_packet_v0.2_current_gpt5_completed.csv --answer-key data/current_model_human_audit/human_audit_answer_key_v0.2_current_gpt5.csv --out-dir results/tables/human_audit_v0.2_current_gpt5
```

### coverage_native_review_v03

Validate completed labels:

```bash
conda run -n reprompt_tax python scripts/validate_completed_coverage_native_review_v03.py --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv
```

Summarize completed labels:

```bash
conda run -n reprompt_tax python scripts/summarize_coverage_native_review_v03.py --annotations data/coverage_native_review_v03/coverage_native_review_packet_v03_completed.csv --launch-packet data/coverage_native_review_v03/coverage_native_review_packet_v03.csv --reviewer-roster data/coverage_native_review_v03/coverage_native_review_roster_v03.csv
```

## Non-Negotiable Boundaries

- A smoke-completed file never unlocks a paper claim.
- Passing validation alone is necessary but not sufficient for a stronger claim; the quantitative thresholds above must also pass.
- Completed-label validation requires every failed component to carry its matching failure or issue code, and rejects codes that contradict passing components.
- If any v0.3 coverage row is not release usable, revise the scaffold and rerun native review before claiming v0.3 benchmark evidence.
- If human-audit agreement misses threshold, report the disagreement pattern and keep the current conservative claim boundary.
