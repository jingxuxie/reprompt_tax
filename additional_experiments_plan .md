# Additional Experiments Plan for RePromptTax

**Goal:** turn the RePromptTax stress-pilot paper into a stronger, more current
workshop submission by adding a modern model refresh, human/native-speaker
validation, and targeted mechanism experiments without requiring local LLM
training.

**Current evidence state:** the repo now contains a 120-item
`RePromptTax-Stress-v0.2` paper-facing pilot over Spanish-English,
Hindi-English, and Arabic-English; four task families; baseline vs Global
Interaction Contract prompting; automatic scoring; full GPT-4.1-family runs;
full 120-item `gpt-5.4-mini` and `gpt-5.5` current-model refreshes;
content-preservation mechanism diagnostics on current models; repair-realism
diagnostics; language/family slices; token analysis; a 72-row blinded
`gpt-4.1` judge audit; and a paired `gpt-5.5` judge refresh on the same 72
rows. The automatic scorer is now covered in both directions by no-API
deterministic audits: 390/390 known-bad probes fail with their expected signals,
and 120/120 constrained positive-control templates pass all scorer components.
The aggregate WildChat motivation scan now also has a taxonomy traceability
audit: all six cue categories map to benchmark, scorer, or repair-metric
surfaces, with five categories tied to deterministic scorer components.

**Main remaining gap:** completed qualified human/native labels are still
missing. The current paper can conservatively submit with the GPT-5.5
current-model headline and launch-ready audit protocols, but it should not
claim native/near-native validation until the original v0.2 audit, current
GPT-5.x audit, or v0.3 coverage-review packets are completed and pass their
validators. A collaborator-validated new language pair remains optional and
should be added only if a qualified validator is available.

## 0. Current Execution Status

| Plan item | Current status | Paper use now | Remaining action |
|---|---|---|---|
| Experiment A: current-model refresh | complete paper-facing evidence | `gpt-5.5` headline: 81.7% to 98.3% FTGA; `gpt-5.4-mini` bounded lower-cost result | none for current submission |
| Experiment B: human/native audit | launch-ready but not completed | protocol-ready evidence only | collect qualified labels and pass completed-label validators |
| Experiment C: prompt mechanism | complete paper-facing evidence | content-preservation is close to the full contract on current models; no prompt-dominance claim | none |
| Experiment D: v0.3 coverage expansion | scaffold, packets, and smokes complete; not headline evidence | bounded runnability/scoring diagnostic | complete native review before using v0.3 as benchmark evidence |
| Experiment E: collaborator-validated language pair | not started | not claim-ready | add only with a qualified validator |
| Experiment F: repair realism | complete supporting diagnostic | repair wording sensitivity on dominant failures | keep framed as controlled diagnostic, not user study |
| Experiment G: judge refresh | complete supporting diagnostic | scorer sanity check: GPT-5.5 judge agrees with auto scorer on 70/72 rows | do not substitute for human/native labels |

---

## 1. Minimum high-impact experiment package

This was the first package to run. It is small, directly addresses the
“GPT-4.1 is outdated” concern, and fits the existing codebase.

### Experiment A — Current-model refresh

**Status:** complete and paper-facing. The saved full 120-item runs show
`gpt-5.5` improving from 81.7% to 98.3% FTGA under the Global Interaction
Contract, with all trajectories resolved within the two-repair budget.
`gpt-5.4-mini` improves from 80.0% to 85.0% FTGA, but its uncertainty interval
crosses zero and the lower-cost claim should remain bounded.

**Question:** does Re-prompt Tax persist on a current flagship model?

**Models:**

1. `gpt-5.5` — current flagship model.
2. `gpt-5.4-mini` — current lower-cost model.
3. Keep the existing `gpt-4.1`, `gpt-4.1-mini`, and `gpt-4.1-nano` results as historical/comparison baselines.

**Conditions:**

- `baseline`: `You are a helpful assistant.`
- `contract`: existing Global Interaction Contract.
- Optional third condition, if budget allows: `content_preservation`, because the current nano diagnostic shows this prompt beats the full contract on nano.

**Dataset:** full `data/benchmark_stress_v0.2.jsonl` with 120 items.

**Completed run order:**

1. Run `gpt-5.4-mini` on all 120 items under baseline+contract.
2. Run `gpt-5.5` on a 40-item stratified pilot.
3. If no obvious pipeline/scoring issues, run `gpt-5.5` on all 120 items.
4. Run `content_preservation` only after baseline+contract are complete.

**Reproduction commands:**

```bash
# 40-item stratified pilot first: create a balanced ID file manually or with a helper script.
conda run -n reprompt_tax python scripts/run_models.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --out results/model_outputs/openai_gpt55_stress_v02_pilot40.jsonl \
  --models gpt-5.5 \
  --conditions baseline,contract \
  --item-id-file data/stress_v02_pilot40_ids.txt \
  --max-output-tokens 256 \
  --max-api-calls 100

# Full GPT-5.5 run.
conda run -n reprompt_tax python scripts/run_models.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --out results/model_outputs/openai_gpt55_stress_v02_full120.jsonl \
  --models gpt-5.5 \
  --conditions baseline,contract \
  --max-output-tokens 256 \
  --max-api-calls 500

# Full GPT-5.4-mini run.
conda run -n reprompt_tax python scripts/run_models.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --out results/model_outputs/openai_gpt54mini_stress_v02_full120.jsonl \
  --models gpt-5.4-mini \
  --conditions baseline,contract \
  --max-output-tokens 256 \
  --max-api-calls 500
```

**Scoring commands:**

```bash
conda run -n reprompt_tax python scripts/score_auto.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --outputs results/model_outputs/openai_gpt55_stress_v02_full120.jsonl \
  --out results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl

conda run -n reprompt_tax python scripts/compute_metrics.py \
  --scores results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl \
  --out-dir results/tables/openai_gpt55_stress_v02_full120

conda run -n reprompt_tax python scripts/paired_effects.py \
  --trajectory-metrics results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv \
  --out-dir results/tables/openai_gpt55_stress_v02_full120

conda run -n reprompt_tax python scripts/paired_significance.py \
  --trajectory-metrics results/tables/openai_gpt55_stress_v02_full120/trajectory_metrics.csv \
  --out-csv results/tables/openai_gpt55_stress_v02_full120/paired_significance_by_model.csv \
  --out-md paper/paired_significance_gpt55_v02_full120.md
```

Repeat the same scoring commands for `gpt-5.4-mini`.

**Paper table to add:**

| Model generation | Model | Baseline FTGA | Contract FTGA | Delta | Baseline RTT | Contract RTT | Baseline token tax | Contract token tax |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| GPT-4.1 family | gpt-4.1-nano | existing | existing | existing | existing | existing | existing | existing |
| GPT-4.1 family | gpt-4.1-mini | existing | existing | existing | existing | existing | existing | existing |
| GPT-4.1 family | gpt-4.1 | existing | existing | existing | existing | existing | existing | existing |
| GPT-5.x family | gpt-5.4-mini | new | new | new | new | new | new | new |
| GPT-5.x family | gpt-5.5 | new | new | new | new | new | new | new |

**Expected interpretation patterns:**

- If GPT-5.5 still has nonzero RTT: strong evidence that Re-prompt Tax is not just an older-model artifact.
- If GPT-5.5 solves most first-turn failures: still useful; the paper becomes a “benchmark as progress probe” and shows where older/smaller models lag.
- If the contract hurts GPT-5.5 or changes little: also useful; the mitigation may be model-generation-specific, and the benchmark remains valuable.

---

## 2. Human/native-speaker validation

This is the strongest quality upgrade after the model refresh.

### Experiment B — 72-row native/near-native audit

**Status:** launch-ready but not completed. The repo contains reviewer-facing
CSV packets, static review sheets, roster templates, acceptance thresholds, and
completion/adjudication validators. It does not contain qualified completed
labels, so the paper should keep human/native validation as a planned or
launch-ready protocol until labels are collected.

**Question:** does the automatic scorer match qualified human judgments for language, script, preservation, and task success?

**Scope:** reuse the existing 72-row human audit packet design.

**Annotators:**

- At least one qualified annotator per language pair.
- Best case: two annotators per language pair plus adjudication.
- Acceptable workshop version: one annotator per language pair, with a clear limitation statement.

**Labels to collect:**

- Overall pass/fail.
- Language pass/fail.
- Script pass/fail.
- Preservation pass/fail.
- Task completion pass/fail.
- Register/locale pass/fail.
- Short free-text reason for failures.

**Existing commands:**

```bash
conda run -n reprompt_tax python scripts/make_human_audit_packet.py \
  --benchmark data/benchmark_stress_v0.2.jsonl \
  --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl \
  --out-dir data/human_audit \
  --seed 23

conda run -n reprompt_tax python scripts/validate_human_audit_packet.py
```

After annotation:

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

**Paper result to add:**

> “A native/near-native audit over 72 stratified first-turn responses agrees with the automatic scorer on X/Y overall labels. Agreement is strongest for literal preservation and script, and weaker for register/locale, supporting the automatic scorer as a conservative diagnostic while bounding cultural-appropriateness claims.”

**Why this matters:** reviewers may trust a small human audit more than a larger automatic table, especially for a global-evaluation workshop.

---

## 3. Prompt mechanism experiments

The existing prompt-ablation diagnostic is valuable but only run on `gpt-4.1-nano`. Make it stronger by running the best prompts on current models.

### Experiment C — Contract vs content-preservation prompt across models

**Status:** complete for the paper-facing mechanism story. The full 120-item
content-preservation diagnostics on `gpt-5.4-mini` and `gpt-5.5` are close to
the full contract, which supports a preservation-mechanism interpretation but
not prompt dominance.

**Question:** is the gain due to the full Global Interaction Contract or mostly due to content-language preservation?

**Models:**

- `gpt-4.1-nano` — already done.
- `gpt-5.4-mini` — new low-cost current model.
- Optional: `gpt-5.5` on a 40-item or full 120-item set.

**Conditions:**

- `baseline`
- `generic_helpfulness`
- `content_preservation`
- `contract`

**Suggested low-cost design:**

- Run all four conditions on the 40 hardest items only: items that failed for at least one model in the existing baseline.
- Or run `content_preservation` only on the full 120, because baseline and contract will already exist.

**Paper table to add:**

| Model | Prompt | FTGA | Mean RTT | Token tax | Editing FTGA | Quote FTGA | Script/register/locale FTGA |
|---|---|---:|---:|---:|---:|---:|---:|
| gpt-5.4-mini | baseline | new | new | new | new | new | new |
| gpt-5.4-mini | content-preservation | new | new | new | new | new | new |
| gpt-5.4-mini | contract | new | new | new | new | new | new |

**Decision rule:**

- If content-preservation wins, rename the mitigation from “Global Interaction Contract” to “contract-family prompts” and emphasize that the best prompt is task-family-specific.
- If the full contract wins on GPT-5.5/GPT-5.4-mini, keep the current framing.
- If generic helpfulness is close, soften the mechanism claim: “structured reminders reduce burden, with preservation-specific reminders most effective in our pilot.”

---

## 4. Benchmark coverage expansion

Do this only after the model refresh and human audit, unless you have collaborators.

### Experiment D — Add non-English target-content editing

**Status:** launch-ready coverage scaffold and bounded model diagnostics exist,
but not paper-facing benchmark evidence yet. The 60-row v0.3 coverage scaffold,
native-review packets, static sheets, and small model smokes/pilot are saved;
completed native review and a pre-specified larger run are required before
using v0.3 as headline benchmark evidence.

The current editing-preservation family often has non-English instructions around English content. Add the reverse and non-English-to-non-English versions.

**New task slices:**

1. English instruction + Spanish/Hindi/Arabic content to preserve.
2. Spanish instruction + Arabic quoted content to preserve.
3. Hindi-English code-switched instruction + Hindi target content in Devanagari.
4. Arabic instruction + Arabic target content with English file names.

**Why:** this addresses a likely reviewer critique that the current benchmark is “English content preservation under multilingual instructions,” not fully global content preservation.

**Size:** add 60 items, not 300.

- 3 language pairs × 2 new task variants × 10 items = 60.
- New total: 180 items.

**Paper framing:** “v0.3 broadens the direction of language preservation; v0.2 is the original stress pilot.”

### Experiment E — Add one collaborator-validated language pair

**Status:** not started. Leave this out of the current submission unless a
qualified validator can review the new language pair before claims are made.

Add only a language pair you can validate with a native/near-native speaker.

Good candidates:

- Chinese-English: script and content-language preservation are salient, and reviewers understand why it matters.
- Japanese-English or Korean-English: register/politeness can be meaningful, but scoring must be more human-heavy.
- Indonesian-English or Swahili-English: useful if you have a validator; avoids a benchmark that only covers globally dominant languages.

**Size:** 40 items per new language pair using the existing four-family template.

**Do not add a language without validation** unless it is explicitly labeled as synthetic smoke coverage.

---

## 5. Repair realism experiment

The current protocol uses standardized repair prompts. That is good for control, but reviewers may ask whether users actually repair that way.

### Experiment F — Standardized vs user-like repair prompts

**Status:** complete as a controlled diagnostic. The saved repair-realism run
shows that standardized and terse repairs recover all 24 sampled dominant
editing-preservation failures, while more natural/frustrated or source-language
contract repairs are weaker. Frame this as repair-wording sensitivity, not as a
user study.

**Question:** how sensitive is RTT to the wording of repair prompts?

**Design:** for each first-turn failure, compare:

1. Standard repair: “Please keep the rewritten text in English.”
2. User-like terse repair: “No, keep it in English.”
3. User-like frustrated repair: “I meant don’t translate it.”
4. Explicit contract repair: “The instruction is Spanish, but the content should remain English.”

**Scope:** only first-turn failures from the existing run, not all items.

**Metrics:**

- Repair success after one turn.
- Repair-token cost.
- Whether the model overcorrects or apologizes without completing the task.

**Paper value:** this turns Re-prompt Tax from a fixed benchmark metric into a more realistic interaction-burden measure.

---

## 6. Judge-refresh experiment

### Experiment G — GPT-4.1 judge vs GPT-5.5 judge vs human audit

**Status:** GPT-5.5 judge refresh complete; human audit still missing. The
paired GPT-5.5 judge agrees with the automatic scorer on 70/72 sampled labels
and with the GPT-4.1 judge on 69/72 labels. This supports scorer sanity checks
but does not replace native/near-native validation.

**Question:** does a stronger judge change the automatic-scorer validation story?

**Design:** rerun the same 72-row judge audit with `gpt-5.5` as judge.

**Compare:**

- Automatic scorer vs GPT-4.1 judge.
- Automatic scorer vs GPT-5.5 judge.
- GPT-4.1 judge vs GPT-5.5 judge.
- Human audit vs both judges, if available.

**Why:** a global-evaluation workshop may care about evaluation methodology as much as model performance. This adds a meta-evaluation angle.

---

## 7. Cost-control strategy

**Status:** the API-spending portion of this plan is complete for the current
paper package. Before any new paid run, first validate saved JSONL outputs and
the local gates, then justify the additional run against the remaining claim
gap. The highest-value next spend is likely not another model call; it is
qualified human/native label collection.

For provenance, the API-spending portion followed the bounded model-call order
below. The human/native audit was never an API-spending step; it remains the
external label-collection step.

### Completed API/model-output order

1. `gpt-5.4-mini` full 120 baseline+contract.
2. `gpt-5.5` 40-item stratified pilot baseline+contract.
3. `gpt-5.5` full 120 baseline+contract.
4. `content_preservation` on GPT-5.4-mini full 120.
5. `content_preservation` on GPT-5.5 full 120.
6. GPT-5.5 judge audit on the existing 72-row sample.
7. v0.3 coverage scaffold smokes and pilot diagnostics.

### Remaining non-API step

1. Collect qualified human/native labels for the launch-ready audit packets.
2. Validate completed labels and rosters before widening any human-validation
   or v0.3 benchmark-evidence claim.

### Practical safeguards

- Keep `--max-output-tokens 256` for comparability.
- Run a 10-item smoke test before any full run.
- Save raw provider token usage for every call.
- Do not use GPT-5.5 as the judge for everything until the model-output runs are complete.
- Track prompt+completion tokens separately from token-tax ratios.
- Use the current `validate_paper_claims.py` style to prevent paper claims from drifting beyond artifacts.

---

## 8. Recommended paper narrative after new experiments

### Best-case story

> “Re-prompt Tax persists even on GPT-5.5, although at a lower rate. The Global Interaction Contract reduces repair burden on both older and current model families. Human audit supports the automatic scorer on most pass/fail labels, while exact preservation and register/locale remain the hardest residual components.”

### If GPT-5.5 nearly solves the benchmark

> “The stress pilot distinguishes model generations: GPT-5.5 largely eliminates the dominant editing-preservation failure, while cheaper and older models still impose measurable repair burden. RePromptTax is useful as a progress probe and as a deployment diagnostic for cost-sensitive global settings.”

### If the contract does not help GPT-5.5

> “The prompt mitigation is not universally beneficial; RePromptTax exposes model- and prompt-specific interactions. Stronger models may already internalize parts of the contract, while smaller models need explicit preservation scaffolding.”

### If human audit disagrees with the automatic scorer

> “Automatic RePromptTax scoring is useful for exact script and literal-preservation checks, but human validation is required for register and pragmatic acceptability. We therefore report automatic results as conservative diagnostics and release the human-audit protocol as part of the benchmark.”

---

## 9. Submission-ready checklist

Before submission, make sure the paper includes:

- [x] Current-model table including `gpt-5.5` and one current low-cost model.
- [x] Main results table with FTGA, RTT, unresolved rate, Repair@1/2, token tax.
- [x] Family-level table showing editing-preservation dominance.
- [x] Language-slice table or paragraph with clear non-population caveat.
- [x] Token-burden paragraph distinguishing normalized token tax from absolute cost.
- [x] Clearly marked launch-ready audit packets and acceptance gates.
- [x] Bidirectional deterministic scorer audit: known-bad probes fail and constrained positive-control templates pass.
- [ ] Completed human/native audit result, if the paper will claim native/near-native validation.
- [x] Prompt-control/ablation paragraph clarifying that the full contract is not necessarily the best prompt.
- [x] Related work section covering multilingual benchmarks, code-switching/output-language alignment, instruction following, multi-turn evaluation, LLM-as-judge, and tokenization/cost inequality.
- [x] Limitations stating that the benchmark is synthetic, small, non-representative, and not a broad claim about all speakers of included languages.
- [x] Artifact manifest and claim-evidence checklist regenerated.

---

## 10. Concrete next steps

### If labels can be collected before submission

1. Prioritize the 48-row current-model GPT-5.x human/native audit and the
   72-row original v0.2 audit; use `paper/label_collection_launch_pack_v02.md`
   as the operational checklist and `paper/label_collection_priority_v02.md`
   as the pre-specified collection order.
2. Send reviewers only the relevant blinded CSV slice or static HTML sheet, not
   the answer key.
3. Fill the matching roster file from its template and run the completed-label
   validator before summarizing.
4. If using two reviewers per item, run the adjudication analyzer, fill only
   disagreement rows, finalize, then validate the finalized one-row-per-item
   file.
5. If acceptance thresholds pass, update the paper from “launch-ready audit
   protocol” to “native/near-native audit supports the scorer”; otherwise
   report disagreement patterns and keep the current conservative claim
   boundary.

### If labels cannot be collected before submission

1. Submit with the GPT-5.5 current-model headline, the prompt-mechanism and
   repair-realism diagnostics, the paired LLM-judge audits, and launch-ready
   human/native review protocols.
2. Keep v0.3 coverage smokes out of headline benchmark claims until native
   review and a pre-specified larger run are complete.
3. Do not add a collaborator-validated language pair unless a qualified
   validator can review it before claims are made.
4. Rerun `conda run -n reprompt_tax python scripts/run_submission_checks.py`
   after any artifact, paper, or claim-boundary change.
