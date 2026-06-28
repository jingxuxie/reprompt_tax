# Concrete Paper Plan: **The Re-prompt Tax**

**Target venue:** *Generative AI for the World: Workshop on Globalizing Tasks, Evaluations, and Systems at COLM 2026*  
**Project type:** API-only evaluation + benchmark + lightweight prompting mitigation  
**Compute budget assumed:** no local LLMs; about \$100 API budget; optional 4090 only for non-LLM utilities such as language ID or plotting  
**Best paper format:** 2-page extended abstract if submitting immediately; 5-page short paper if you can spend 1–2 additional weeks improving validation

---

## 1. One-sentence paper idea

Modern LLM evaluations usually ask whether the final answer is correct, but multilingual and code-switched users often pay a hidden **re-prompt tax**: extra turns, extra tokens, and extra user effort needed to repair answers that are semantically plausible but violate language, script, register, quote-preservation, or locale expectations.

**Paper thesis:** We introduce a small, carefully validated benchmark and metrics for measuring this hidden interaction cost, show that it appears across strong API models, and demonstrate that a simple global-interaction system prompt can reduce—but not eliminate—the tax.

---

## 2. Why this is a strong fit for GenAI4World

The workshop call explicitly asks for work on:

- globalizing tasks,
- evaluation beyond standard performance metrics,
- data collection and annotation for global contexts,
- real global user experiences and vulnerabilities,
- systems that handle language, culture, identity, and context without erasing them.

Your project fits all of these because **Re-prompt Tax** is not another translated accuracy benchmark. It reframes evaluation around a practical question:

> How much extra interaction does a global user need before the model finally behaves as intended?

That framing is likely to resonate with reviewers because it turns a familiar anecdotal frustration—“the model answered in the wrong language,” “it translated the text I asked it to edit,” “it ignored the script/register I needed”—into a measurable research object.

---

## 3. Recommended working title

### Main title

**The Re-prompt Tax: Measuring Hidden Interaction Costs for Multilingual and Code-Switched LLM Users**

### Alternative titles

1. **Beyond First-Turn Accuracy: The Re-prompt Tax for Global LLM Users**
2. **How Many Turns Until It Listens? Measuring Multilingual Repair Burden in LLMs**
3. **Evaluating Global Usability: Hidden Repair Costs in Multilingual LLM Interactions**
4. **When Correct Is Still Wrong: Re-prompt Tax in Code-Switched LLM Use**

My recommendation is to use the first title. It is memorable and makes the contribution legible.

---

## 4. What makes this different from existing work

Related work such as OLA studies **output language alignment** in code-switched interactions. Your paper should acknowledge that and position Re-prompt Tax as a complementary contribution:

| Existing direction | Your extension |
|---|---|
| Does the model answer in the expected language? | How much extra interaction is needed after the model fails? |
| Mostly one-turn evaluation | Multi-turn repair trajectories |
| Language choice as the main target | Language + script + content preservation + register + locale |
| Capability/alignment failure | User-burden metric: turns, tokens, costs, and repair success |
| Benchmark result | Benchmark + practical mitigation + product-facing metric |

Your strongest novelty claim should be:

> We evaluate not only whether a model fails, but the **interactional cost of recovering from that failure**.

---

## 5. Core research questions

### RQ1 — Prevalence

How often do current LLMs produce first-turn responses that are semantically plausible but violate multilingual interaction expectations?

Examples of violations:

- answers in the wrong language,
- translates content that should be edited or preserved,
- changes quoted text or proper nouns,
- ignores requested script,
- uses inappropriate register or locale assumptions.

### RQ2 — Burden

When a failure occurs, how much additional user effort is needed to recover?

Measure:

- extra turns,
- extra input tokens,
- extra output tokens,
- extra API cost,
- probability of successful repair after one or two follow-ups.

### RQ3 — Failure modes

Which task families produce the largest Re-prompt Tax?

Expected high-risk families:

1. editing content in one language while instruction is in another,
2. summarization with mixed language cues,
3. quote/proper-noun preservation,
4. script/register/locale constraints.

### RQ4 — Mitigation

Can a low-cost system prompt reduce the tax without any training?

This is important because your budget does not support training, but a strong workshop paper does not need training if the evaluation is novel and useful.

---

## 6. Main hypothesis

**H1:** Strong LLMs often solve the semantic task but fail the interactional contract.

Example:

> User: “Me puedes mejorar este correo, but keep it in English? ‘Hi professor, I am writing because I need more time…’”

A model might produce a polished Spanish translation. That is fluent and helpful-looking, but it violates the user’s actual need.

**H2:** The cost of these failures is not captured by first-turn accuracy, BLEU, ROUGE, MMLU-style accuracy, or standard helpfulness ratings.

**H3:** A simple “Global Interaction Contract” prompt improves first-turn alignment, showing that the failure is partly an evaluation/alignment issue rather than a deep capability limit.

---

## 7. Minimum viable contribution

For a strong workshop submission, aim for these contributions:

1. **Metric:** Define Re-prompt Tax as a family of turn, token, and repair-success metrics.
2. **Benchmark:** Release a small benchmark, **RePromptTax-Bench**, with 120–360 multilingual/code-switched prompts.
3. **Evaluation:** Test 3–5 API models under baseline and mitigation conditions.
4. **Repair simulation:** Run standardized follow-up prompts after failures.
5. **Analysis:** Show failure categories, cost burden, and whether mitigation helps.
6. **Human validation:** Manually validate at least 20% of examples and all qualitative claims.

A 2-page extended abstract can be strong with 120 prompts. A 5-page short paper should target 300–600 prompts.

---

## 8. Scope: choose languages carefully

Do **not** try to cover the world. Cover a few languages well.

### Recommended default scope

Use **three language pairs**:

| Pair | Why include it | Risk |
|---|---|---|
| English–Spanish | High-resource, Latin script, easy to validate with many annotators | Reviewers may see it as too easy unless paired with harder cases |
| English–Hindi | Common code-switching/Hinglish setting; script issues possible | Requires native or near-native validation |
| English–Arabic | Non-Latin, right-to-left script, register/script issues | Requires native or near-native validation |

### Alternative pairs

Use the languages you or collaborators can validate. Better options than the default may be:

- English–Indonesian,
- English–Tagalog,
- English–Korean,
- English–Chinese,
- English–Swahili,
- English–Vietnamese,
- English–Bengali,
- English–Urdu.

### Quality rule

A paper with **2 languages and excellent validation** is better than a paper with **12 languages and weak labels**.

If you have no native-speaker collaborators, choose:

- one language you know well,
- English,
- one additional language with a paid validator for a small audit.

---

## 9. Benchmark design

### Benchmark name

**RePromptTax-Bench**

### Recommended size

| Version | Items | Use case |
|---|---:|---|
| Emergency pilot | 120 | 2-page extended abstract |
| Solid workshop benchmark | 360 | 5-page short paper |
| Stronger release | 600 | long paper / arXiv follow-up |

### Recommended 360-item design

| Dimension | Count |
|---|---:|
| Language pairs | 3 |
| Task families | 4 |
| Items per pair-family cell | 30 |
| Total | 3 × 4 × 30 = 360 |

### Emergency 120-item design

| Dimension | Count |
|---|---:|
| Language pairs | 3 |
| Task families | 4 |
| Items per pair-family cell | 10 |
| Total | 3 × 4 × 10 = 120 |

---

## 10. Task families

Keep the benchmark narrow enough to explain clearly, but broad enough to show that the phenomenon is not one isolated trick.

### Family A — Editing-with-preservation

The instruction is in one language, but the content to edit is in another. The model should preserve the content language unless explicitly asked to translate.

**Example:**

```text
Me puedes hacer este email more professional, but keep it in English?

"Hi professor, I cannot submit the assignment today because my internet was down. Can I send it tomorrow?"
```

**Expected behavior:** Output a professional English email. Do not translate into Spanish.

**Failure types:**

- translates into Spanish,
- explains in Spanish instead of editing,
- mixes languages unnecessarily,
- changes the meaning of the email.

---

### Family B — Output-language inference

The user code-switches and does not always explicitly say the response language. Humans can often infer it from context.

**Example:**

```text
이 문장 자연스럽게 고쳐줘: "I am looking forward to hear from you."
```

**Expected behavior:** Correct the English sentence in English, possibly with a brief Korean explanation only if appropriate.

**Failure types:**

- answers entirely in Korean,
- translates the English sentence into Korean,
- provides an explanation but not the corrected sentence,
- gives both languages when only one is needed.

---

### Family C — Quote/proper-noun preservation

The user asks for a response in one language but wants quoted names, product names, titles, legal terms, code snippets, or addresses preserved.

**Example:**

```text
لخص النص التالي بالعربية، لكن لا تترجم العبارات بين علامتي الاقتباس:
The report says that "Project Greenlight" will launch after "Phase Zero".
```

**Expected behavior:** Arabic summary while preserving “Project Greenlight” and “Phase Zero” exactly.

**Failure types:**

- translates quoted phrases,
- transliterates quoted phrases,
- drops quoted phrases,
- changes capitalization or exact wording.

---

### Family D — Script, register, and locale constraints

The user needs the same semantic answer in a particular script, politeness level, or local convention.

**Example:**

```text
Write a short WhatsApp reply in Hindi, but use Latin script, not Devanagari. Make it polite but casual.

Context: I need to tell my cousin I will be 20 minutes late.
```

**Expected behavior:** Romanized Hindi / Hinglish, polite-casual tone, no Devanagari.

**Failure types:**

- outputs Devanagari,
- outputs English only,
- becomes overly formal,
- uses unnatural register,
- ignores local messaging convention.

---

## 11. Item schema

Use a structured JSONL/CSV format so the benchmark is easy to release and score.

```json
{
  "id": "es_en_A_001",
  "language_pair": "es-en",
  "task_family": "editing_preservation",
  "user_prompt": "Me puedes hacer este email more professional, but keep it in English?...",
  "instruction_language": "Spanish/English code-switched",
  "content_language": "English",
  "expected_response_language": "English",
  "expected_script": "Latin",
  "must_preserve_spans": ["Hi professor"],
  "must_not_translate_spans": [],
  "register_requirement": "professional email",
  "locale_requirement": null,
  "acceptable_outputs": ["edited English email"],
  "known_bad_outputs": ["Spanish translation", "Spanish explanation only"],
  "repair_prompt_1": "Please keep the email in English and only rewrite it professionally.",
  "repair_prompt_2": "Do not translate. Output only the revised English email.",
  "notes_for_annotators": "Minor grammar changes are acceptable; meaning should be preserved."
}
```

---

## 12. How to create the benchmark

### Step 1 — Write seed templates manually

For each task family, write 10 seed templates per language pair.

Example template for editing-preservation:

```text
[Instruction in L1 or code-switched L1-English]
"[Content in L2]"
```

Variables:

- domain: email, text message, resume bullet, school note, customer support reply,
- tone: professional, friendly, polite, concise,
- output language: content language or instruction language,
- preservation span: quoted title/name/product/legal phrase,
- ambiguity level: explicit vs implicit.

### Step 2 — Generate paraphrases with an API model

Use a cheap model to generate variants, but do not trust them blindly.

Prompt:

```text
Create 10 realistic multilingual user prompts for the following benchmark category.
Do not include sensitive personal data, copyrighted text, or real names.
The prompt should be natural and short.
Return JSONL with fields: user_prompt, expected_response_language, expected_script,
must_preserve_spans, known_bad_outputs.

Category: Editing an English email while the instruction is in Spanish.
The desired output is English, not Spanish.
```

### Step 3 — Manually clean

For each generated item, check:

- Is this a plausible real user request?
- Is the expected answer unambiguous enough for evaluation?
- Are the language/script/register constraints clear to a native speaker?
- Are there no real personal names, addresses, medical records, or sensitive details?
- Is the item not just a translation benchmark in disguise?

### Step 4 — Add repair prompts

For each item, write two standardized repair prompts.

Repair prompt 1 should sound like a real frustrated user:

```text
I wanted this in English, not Spanish. Please revise.
```

Repair prompt 2 should be more explicit:

```text
Do not translate the email. Output only the polished English version.
```

The repair prompts are crucial because they let you measure how many turns are needed to recover.

---

## 13. Optional real-world discovery analysis

This part makes the paper more compelling, but it is optional for the 2-page version.

### Goal

Use public conversation datasets to motivate the taxonomy. Do **not** release raw user conversations.

### Candidate sources

- WildChat: real ChatGPT interaction logs, multi-turn and multilingual.
- LMSYS-Chat-1M: one million real-world conversations with multiple models and language tags.

### Safe use pattern

Use these datasets only to answer questions like:

- What kinds of language-related repair requests occur?
- Which phrases do users use when correcting a model?
- How often do follow-up turns look like repairs?

Do **not** copy raw user prompts into your released benchmark. Instead:

- report aggregate counts,
- paraphrase examples,
- release synthetic benchmark items inspired by observed patterns,
- follow dataset licenses and terms.

### Candidate repair cues

English cues:

```text
in English
not in English
wrong language
I said English
keep it in
don't translate
why did you translate
use Spanish
answer in Arabic
write it in Latin script
not Devanagari
I meant
that's not what I asked
```

Spanish cues:

```text
en inglés
en español
no traduzcas
te dije
manténlo en
corrige pero no traduzcas
```

Hindi/Hinglish cues:

```text
English mein
Hindi mein
translate mat karo
same language mein rakho
Devanagari nahi
Latin script mein
```

Arabic cues:

```text
بالإنجليزية
بالعربية
لا تترجم
نفس اللغة
اكتب بالحروف اللاتينية
ليس هذا ما طلبته
```

### Discovery pipeline

1. Load or stream the dataset.
2. Keep conversations with at least two user turns.
3. Filter for multilingual/code-switched language tags or repair cues.
4. Use a cheap model or rules to classify the follow-up user turn.
5. Manually inspect 100–200 candidates.
6. Build a taxonomy from the verified examples.
7. Use the taxonomy to justify benchmark categories.

### Classifier JSON schema

```json
{
  "is_repair_turn": true,
  "repair_target": "assistant_previous_response",
  "failure_type": "wrong_output_language",
  "expected_language": "English",
  "evidence_phrase": "I said keep it in English",
  "confidence": "high"
}
```

### What to report

A small table like this is enough:

| Repair type | Share of verified repair turns | Example paraphrase |
|---|---:|---|
| Wrong output language | TBD | “I asked for English, not Spanish.” |
| Unwanted translation | TBD | “Keep the quote as-is.” |
| Script mismatch | TBD | “Use Latin script, not native script.” |
| Register/tone mismatch | TBD | “Make it respectful, not casual.” |
| Locale assumption | TBD | “Use Indian rupees, not dollars.” |

Use “TBD” during planning, then fill in actual numbers after running the discovery script.

---

## 14. Models to evaluate

You do not need local LLMs. Use API models only.

### Minimum model set

| Role | Example choice | Why |
|---|---|---|
| Cheap baseline | `gpt-4.1-nano` or equivalent | Tests whether cheap models impose high repair burden |
| Mid-tier model | `gpt-4.1-mini` or equivalent | Likely realistic developer choice |
| Strong model | `gpt-4.1` or current strong API model | Tests whether frontier quality solves the issue |

### Better model set

Add one non-OpenAI model if you already have access, for provider diversity. For example:

- a Gemini Flash/Pro model,
- a Claude Haiku/Sonnet model,
- a Mistral model,
- a Cohere Command model.

Do not spend half the project fighting provider access. A clean evaluation of 3 models is better than a messy evaluation of 8.

### Run settings

Use deterministic settings where possible:

```text
temperature = 0
top_p = 1
max_output_tokens = 512
presence_penalty = 0
frequency_penalty = 0
```

Record exact model names, dates, provider, and API versions.

---

## 15. Experimental conditions

Run each model in two conditions.

### Condition 1 — Baseline

System prompt:

```text
You are a helpful assistant.
```

### Condition 2 — Global Interaction Contract

System prompt:

```text
You are a helpful assistant for multilingual users.
Before answering, infer the user's interaction contract:
1. Identify the language of the instruction and the language of the content being edited, summarized, or transformed.
2. If the user asks to edit, polish, correct, shorten, or rewrite text, preserve the original content language unless the user explicitly asks for translation.
3. Preserve quoted text, product names, proper nouns, addresses, code, and titles exactly unless the user explicitly asks to translate or modify them.
4. Follow explicit language, script, register, and locale requirements.
5. If the user mixes languages, do not assume that the answer should be in the last language used. Use the task goal to infer the expected output language.
6. Output only what the user asked for; avoid unnecessary explanation.
```

### Optional Condition 3 — Two-stage self-check

Use only if time and budget allow.

Ask the model to silently or explicitly infer:

```json
{
  "output_language": "...",
  "content_language_to_preserve": "...",
  "script": "...",
  "spans_to_preserve": ["..."],
  "task": "..."
}
```

Then answer. This will probably improve accuracy but increase token cost. That makes it an interesting tradeoff.

---

## 16. Repair simulation protocol

For each benchmark item and model condition:

1. Send the original user prompt.
2. Score the first response.
3. If the first response passes, Re-prompt Turn Tax = 0.
4. If it fails, append repair prompt 1 and generate a second response.
5. Score the second response.
6. If it passes, Re-prompt Turn Tax = 1.
7. If it fails, append repair prompt 2 and generate a third response.
8. Score the third response.
9. If it still fails, mark as unresolved within the repair budget.

This simulates realistic user frustration without requiring a live human in the loop.

---

## 17. Metrics

### 17.1 First-Turn Global Alignment

Binary metric:

```text
FTGA(i, m) = 1 if model m satisfies all global interaction constraints on item i in the first response.
FTGA(i, m) = 0 otherwise.
```

A response passes only if it satisfies:

- correct output language,
- correct script,
- correct task completion,
- required span preservation,
- required register/locale constraints.

### 17.2 Re-prompt Turn Tax

```text
RTT(i, m) = minimum number of repair prompts needed before success.
```

Values:

| Value | Meaning |
|---:|---|
| 0 | first response succeeded |
| 1 | succeeded after one repair prompt |
| 2 | succeeded after two repair prompts |
| 3 | still failed after two repair prompts |

Use 3 as a censored “unresolved” value.

### 17.3 Repair Success@k

```text
RepairSuccess@1 = share of initially failed items fixed after one repair prompt.
RepairSuccess@2 = share of initially failed items fixed after two repair prompts.
```

### 17.4 Token Tax

```text
TokenTax(i, m) = total tokens consumed until success / tokens consumed by the first response attempt.
```

If the model fails after two repairs, compute total tokens across all three attempts and mark unresolved.

### 17.5 Cost Tax

```text
CostTax(i, m) = total API cost until success / first-attempt API cost.
```

This is useful because global users may pay extra money, not just extra time.

### 17.6 Component pass rates

Track separate components:

| Component | Binary check |
|---|---|
| Language | Response is in expected language |
| Script | Response uses expected script |
| Preservation | Required spans preserved exactly |
| Task | User’s actual transformation completed |
| Register | Formality/tone appropriate |
| Locale | Dates/currency/address conventions followed |

Component rates make the paper more diagnostic.

---

## 18. Scoring protocol

Use a hybrid scoring approach: automatic checks + LLM judge + human audit.

### Automatic checks

Use for things that are objective:

- script ratio: Latin vs Devanagari vs Arabic, etc.,
- exact preservation of quoted spans,
- output length constraints,
- forbidden translation of exact strings,
- approximate language ID after removing quoted spans.

Possible lightweight tools:

- `regex` for scripts,
- `langdetect`, `lingua`, `fastText lid.176`, or `pycld3` for language ID,
- provider tokenizer for token counts.

### LLM judge

Use a strong model as a structured judge, blind to the model identity.

Judge prompt:

```text
You are evaluating whether an assistant response satisfies a multilingual user request.
Do not reward general helpfulness if the response violates the user's language, script,
quote-preservation, register, or task constraints.

Return JSON only.

User prompt:
{user_prompt}

Expected contract:
- expected_response_language: {expected_response_language}
- expected_script: {expected_script}
- must_preserve_spans: {must_preserve_spans}
- register_requirement: {register_requirement}
- task_family: {task_family}

Assistant response:
{assistant_response}

JSON schema:
{
  "pass": true/false,
  "language_pass": true/false,
  "script_pass": true/false,
  "preservation_pass": true/false,
  "task_pass": true/false,
  "register_locale_pass": true/false,
  "failure_types": ["wrong_output_language", "unwanted_translation", "script_mismatch", "register_mismatch", "locale_mismatch", "task_noncompletion", "other"],
  "short_reason": "one sentence"
}
```

### Human audit

For workshop quality, do at least one of the following:

#### Minimum

- Manually inspect 20% of items × model outputs.
- Make sure every language pair has some human-audited examples.
- Report LLM judge accuracy against human audit.

#### Better

- Get one native speaker per language pair.
- Ask each validator to label 50–100 outputs.
- Double-label 30–50 examples to measure agreement.

#### Strong

- Two native speakers per language pair for a subset.
- Report Cohen’s κ or Krippendorff’s α for binary pass/fail.

Human validation is one of the highest-return uses of your time. It makes the work much more credible than a fully synthetic, LLM-judged benchmark.

---

## 19. API budget estimate

This project is API-cheap. Human validation is the main cost.

### Assumptions

For one item, one model, one condition, across up to 3 attempts:

| Quantity | Approximation |
|---|---:|
| Total input tokens | 1,900 |
| Total output tokens | 900 |
| Attempts | first attempt + up to two repairs |

For 360 items, 2 conditions, and 3 models:

```text
360 items × 2 conditions × 3 models = 2,160 item-model-condition runs
```

Approximate generation tokens:

```text
Input: 2,160 × 1,900 = 4.10M input tokens
Output: 2,160 × 900 = 1.94M output tokens
```

This is very affordable on small and mid-tier models.

### Example OpenAI GPT-4.1-family costs

As of the OpenAI GPT-4.1 launch/pricing page:

| Model | Input / 1M tokens | Output / 1M tokens |
|---|---:|---:|
| gpt-4.1 | \$2.00 | \$8.00 |
| gpt-4.1-mini | \$0.40 | \$1.60 |
| gpt-4.1-nano | \$0.10 | \$0.40 |

If you used only these three models, approximate generation cost would likely be far below \$50. Add judging and reruns, and \$100 is still enough if you keep the benchmark compact.

### Where the money should go

| Item | Suggested spend |
|---|---:|
| API generation | \$5–\$30 |
| LLM judging | \$5–\$30 |
| Human validation | \$0–\$150 depending on collaborators |
| Total target | \$20–\$100 API-only; more if paying annotators |

If your \$100 is API-only credit and cannot pay annotators, use collaborators or self-validation for languages you know, and be transparent about limitations.

---

## 20. Statistical analysis

### Main table

Report:

| Model | Condition | FTGA ↑ | RTT ↓ | Repair@1 ↑ | Unresolved ↓ | TokenTax ↓ |
|---|---|---:|---:|---:|---:|---:|
| Model A | Baseline | TBD | TBD | TBD | TBD | TBD |
| Model A | Contract | TBD | TBD | TBD | TBD | TBD |
| Model B | Baseline | TBD | TBD | TBD | TBD | TBD |
| Model B | Contract | TBD | TBD | TBD | TBD | TBD |

### Breakdown table

| Task family | FTGA | RTT | Most common failure |
|---|---:|---:|---|
| Editing-with-preservation | TBD | TBD | unwanted translation |
| Output-language inference | TBD | TBD | wrong output language |
| Quote/proper-noun preservation | TBD | TBD | span translated or altered |
| Script/register/locale | TBD | TBD | script mismatch |

### Figures

Make exactly 2–3 figures for a workshop paper:

1. **Bar chart:** FTGA by model and condition.
2. **Stacked bar or heatmap:** failure types by task family.
3. **Cumulative repair curve:** share of items solved after 0, 1, and 2 repair prompts.

### Confidence intervals

Use paired bootstrap over benchmark items:

```text
For each bootstrap sample:
  sample items with replacement
  recompute FTGA, RTT, TokenTax
Report 95% confidence intervals.
```

For baseline vs mitigation, use paired tests because every item appears under both conditions.

### Regression analysis

Optional but useful:

```text
pass ~ model + condition + task_family + language_pair + explicitness + script_mismatch
```

Use logistic regression or mixed-effects logistic regression if you are comfortable with it. If not, bootstrap tables are enough.

---

## 21. Qualitative analysis

Include 4–6 short examples.

For each example:

1. Show the user prompt.
2. Show a shortened model failure.
3. State why it failed.
4. Show the repair prompt.
5. State whether the model recovered.

Example format:

```text
User: Me puedes mejorar este email, but keep it in English? "Hi professor..."
Model: Claro, aquí tienes una versión más profesional: "Estimado profesor..."
Failure: unwanted translation; expected English edited email.
Repair: I wanted the email in English, not Spanish.
Recovery: succeeds after one repair; RTT = 1.
```

Do not include raw examples from real chat datasets unless the license and privacy terms clearly allow it. Prefer synthetic or paraphrased examples.

---

## 22. Mitigation: Global Interaction Contract

This is your lightweight “systems” contribution.

### Why it matters

If the prompt reduces failures, you can argue:

- standard chat settings under-specify multilingual user expectations,
- evaluation should measure global interaction contracts,
- even cheap system-level changes can reduce user burden.

### What to compare

| Condition | Description |
|---|---|
| Baseline | Generic helpful assistant |
| Contract prompt | Explicit instructions for language/content/register preservation |
| Optional self-check | Model first infers contract, then answers |

### What success looks like

The mitigation does not need to solve everything. A result like this is publishable:

```text
The Global Interaction Contract improves first-turn alignment from 68% to 81%,
reduces mean Re-prompt Turn Tax from 0.54 to 0.27, and reduces unresolved cases
from 11% to 5%, with the largest gains on editing-with-preservation tasks.
```

These numbers are hypothetical. Replace them with your actual results.

### What if mitigation fails?

Still publishable if framed correctly:

```text
A direct system prompt improves explicit language mismatches but fails on quote preservation
and register-sensitive cases, suggesting that global interaction alignment cannot be solved
by generic prompting alone.
```

Negative results are useful if the benchmark and analysis are strong.

---

## 23. Implementation plan

### Repository structure

```text
reprompt-tax/
  README.md
  data/
    benchmark_v0.1.jsonl
    sample_items_for_paper.jsonl
    annotations_human.csv
    annotations_judge.jsonl
  prompts/
    baseline_system.txt
    global_interaction_contract.txt
    judge_prompt.txt
    item_generation_prompt.txt
  scripts/
    generate_items.py
    run_models.py
    score_auto.py
    judge_outputs.py
    compute_metrics.py
    bootstrap_ci.py
    make_figures.py
  results/
    model_outputs/
    scores/
    tables/
    figures/
  paper/
    main.tex
    refs.bib
    figures/
```

### Response log format

```json
{
  "item_id": "es_en_A_001",
  "model": "gpt-4.1-mini-YYYY-MM-DD",
  "condition": "baseline",
  "turn": 0,
  "prompt_messages": ["..."],
  "response": "...",
  "input_tokens": 271,
  "output_tokens": 144,
  "created_at": "2026-06-28T12:00:00Z"
}
```

### Metric computation pseudocode

```python
def reprompt_turn_tax(pass_by_turn):
    # pass_by_turn is a list like [False, True, ...]
    for turn, passed in enumerate(pass_by_turn):
        if passed:
            return turn
    return 3  # unresolved after two repairs


def token_tax(tokens_by_turn, pass_by_turn):
    first_attempt_tokens = tokens_by_turn[0]
    for turn, passed in enumerate(pass_by_turn):
        if passed:
            return sum(tokens_by_turn[:turn + 1]) / max(first_attempt_tokens, 1)
    return sum(tokens_by_turn) / max(first_attempt_tokens, 1)
```

---

## 24. 48-hour submission plan

The workshop deadline is close, so here is a realistic emergency plan for a strong 2-page extended abstract.

### June 28, 2026 — Build and run pilot

**Goal:** produce enough evidence for a credible abstract.

Tasks:

1. Pick 2–3 language pairs.
2. Build 120 items: 3 language pairs × 4 task families × 10 items.
3. Manually check all 120 prompts for clarity.
4. Run 3 API models in baseline condition.
5. Run the same 3 models with the Global Interaction Contract.
6. Run repair simulation with up to two repair prompts.
7. Score with automatic checks and LLM judge.
8. Manually audit 30–50 outputs.

Deliverables by end of day:

- `benchmark_v0.1.jsonl`,
- raw model outputs,
- preliminary metrics table,
- 3–5 example failures.

### June 29, 2026 — Analyze and draft

Tasks:

1. Compute FTGA, RTT, Repair@1, unresolved rate, and TokenTax.
2. Bootstrap confidence intervals.
3. Make 2 figures.
4. Write 2-page paper draft.
5. Write ethics statement outside page limit.
6. Prepare appendix with benchmark examples and judge rubric.

Deliverables:

- main table,
- figure 1: FTGA by model/condition,
- figure 2: repair curve or failure-type heatmap,
- complete 2-page draft.

### June 30, 2026 — Polish and submit

Tasks:

1. Tighten title/abstract/introduction.
2. Add related work paragraph.
3. Double-check all claims match results.
4. Remove deanonymizing information for double-blind review.
5. Include limitations and ethics.
6. Submit through OpenReview using the COLM style.

---

## 25. Two-week stronger plan

If you are not constrained to the immediate deadline, expand the project.

### Days 1–2 — Scope and pilot

- Finalize language pairs and task families.
- Build 120-item pilot.
- Run 3 models.
- Debug scoring.

### Days 3–5 — Full benchmark

- Expand to 360 items.
- Add real-world discovery analysis from WildChat/LMSYS if feasible.
- Validate all expected contracts.

### Days 6–8 — Full model runs

- Run 3–5 models.
- Run baseline and mitigation.
- Run repair simulation.
- Run LLM judge.

### Days 9–10 — Human validation

- Audit 20–30% of model outputs.
- Double-label a subset.
- Compute judge-vs-human agreement.

### Days 11–12 — Analysis

- Bootstrap confidence intervals.
- Create tables and figures.
- Write qualitative analysis.

### Days 13–14 — Paper

- Write full short paper.
- Prepare benchmark release.
- Write ethics and limitations.
- Prepare reproducibility checklist.

---

## 26. Paper outline for 2-page extended abstract

### Title

The Re-prompt Tax: Measuring Hidden Interaction Costs for Multilingual and Code-Switched LLM Users

### Abstract — 120–150 words

Include:

- problem,
- metric,
- benchmark,
- models evaluated,
- one headline result,
- mitigation result,
- release statement.

Template:

```text
Multilingual users often interact with LLMs through code-switched prompts, mixed-language editing requests, and culturally specific formatting expectations. Existing evaluations typically measure first-turn task performance, missing cases where a model gives a fluent but interactionally wrong answer that users must repair. We introduce Re-prompt Tax, a metric family measuring the extra turns, tokens, and costs required to recover from multilingual interaction failures. We construct RePromptTax-Bench, a benchmark of [N] prompts across [languages] and [task families], and evaluate [models] under baseline and mitigation conditions. We find that [headline result]. A simple Global Interaction Contract prompt [reduces/does not eliminate] the tax, suggesting that global usability requires explicit evaluation of interaction contracts rather than semantic correctness alone.
```

### Section 1 — Introduction

Key points:

- Global users do not always prompt monolingually.
- Correctness is not enough; interactional fit matters.
- Re-prompting imposes hidden costs.
- Contributions.

### Section 2 — Re-prompt Tax

Define:

- first-turn global alignment,
- re-prompt turn tax,
- token/cost tax,
- repair success.

### Section 3 — Benchmark and protocol

Describe:

- languages,
- task families,
- item creation,
- model runs,
- scoring.

### Section 4 — Results

Include:

- main table,
- one figure,
- mitigation result,
- qualitative examples.

### Section 5 — Limitations and ethics

Be explicit:

- small language coverage,
- imperfect judging,
- synthetic prompts,
- need native-speaker validation,
- privacy-safe use of public chat logs.

---

## 27. Paper outline for 5-page short paper

1. **Introduction**
   - motivating examples,
   - hidden cost framing,
   - contributions.

2. **Related Work**
   - multilingual/code-switched LLM evaluation,
   - output language alignment,
   - real-world interaction logs,
   - LLM usability/evaluation beyond accuracy.

3. **The Re-prompt Tax Metric**
   - formal definitions,
   - turn/cost/token metrics,
   - component pass rates.

4. **RePromptTax-Bench**
   - language pairs,
   - task families,
   - item schema,
   - annotation protocol,
   - validation.

5. **Experiments**
   - models,
   - baseline vs Global Interaction Contract,
   - repair simulation,
   - scoring.

6. **Results**
   - aggregate results,
   - task-family breakdown,
   - language-pair breakdown,
   - failure taxonomy,
   - qualitative examples.

7. **Discussion**
   - what standard evaluations miss,
   - product implications,
   - why small models may be cheaper per token but more costly per successful interaction,
   - future work.

8. **Limitations and Ethics**
   - language coverage,
   - annotation validity,
   - privacy,
   - overgeneralization risks.

---

## 28. Expected results patterns to look for

You do not know the results yet. These are the patterns to check.

### Pattern A — Strong models still pay tax

High-impact if true:

```text
Even the strongest model fails first-turn global alignment on nontrivial portions of the benchmark.
```

### Pattern B — Cheap models are not always cheaper

High-impact if true:

```text
A cheaper model has lower per-token cost but higher repair cost, narrowing or reversing the apparent cost advantage.
```

### Pattern C — Prompt mitigation helps unevenly

High-impact if true:

```text
The Global Interaction Contract reduces wrong-language failures but has weaker effects on quote preservation or register.
```

### Pattern D — Language ID alone misses failures

High-impact if true:

```text
Automatic language ID marks an answer as correct-language, but the response still fails because it translated quoted spans or changed the requested register.
```

### Pattern E — Repair is not guaranteed

High-impact if true:

```text
Some models continue to translate or switch language even after explicit correction.
```

---

## 29. Claims you can safely make

Use careful claims like:

- “We propose a metric for hidden interaction cost.”
- “We show that first-turn evaluation can miss global usability failures.”
- “In our benchmark, several models require additional repair turns.”
- “A simple system prompt reduces some failures but does not eliminate the tax.”
- “Our results suggest global evaluation should include repair burden, not only first-turn task success.”

Avoid overclaims like:

- “LLMs do not work for global users.”
- “This benchmark represents all multilingual users.”
- “Spanish/Hindi/Arabic users behave like this universally.”
- “Our LLM judge is equivalent to native-speaker evaluation.”

---

## 30. Ethics and broader impacts statement

Include a concise but serious ethics section.

Suggested text:

```text
This work studies multilingual interaction failures that can impose additional effort and cost on global LLM users. We construct synthetic benchmark prompts inspired by common multilingual workflows rather than releasing raw user conversations. If public interaction logs are used for taxonomy discovery, we report only aggregate statistics and paraphrased examples, follow dataset licenses, and do not attempt to identify users. Because language, register, and script preferences vary across communities and individuals, our benchmark should not be interpreted as representing all speakers of the included languages. We include native-speaker validation where possible and report limitations transparently. The intended impact is to improve evaluation of global usability and reduce unequal interaction burdens across languages and contexts.
```

---

## 31. Reviewer-facing contribution checklist

Make sure the paper visibly answers these questions:

| Reviewer question | Your answer |
|---|---|
| What is new? | Re-prompt Tax metric + repair-trajectory evaluation |
| Why workshop-relevant? | Measures global usability beyond standard performance |
| Why not just OLA? | Measures recovery cost across language, script, preservation, register, and locale |
| Is it feasible? | API-only, small benchmark, no training |
| Is it rigorous? | Structured benchmark, scoring rubric, human audit, bootstrap CIs |
| Is it useful? | Product teams can measure and reduce hidden user burden |
| Is it safe/ethical? | Synthetic release; privacy-safe real-log analysis; native validation; limited claims |

---

## 32. Concrete “Day 1” task list

Start with this exact checklist.

### Choose scope

- [ ] Pick 3 language pairs.
- [ ] Pick 4 task families.
- [ ] Decide whether you can get native-speaker validation.

### Build benchmark

- [ ] Create `benchmark_v0.1.jsonl`.
- [ ] Write 10 items per pair-family cell for a 120-item pilot.
- [ ] Add expected language/script/preservation fields.
- [ ] Add repair prompts.
- [ ] Manually inspect every item.

### Run models

- [ ] Implement API call wrapper.
- [ ] Run one item end-to-end before batch generation.
- [ ] Run baseline condition.
- [ ] Run Global Interaction Contract condition.
- [ ] Run repair turns only when first response fails, or run all turns and decide after scoring.

### Score

- [ ] Run automatic checks.
- [ ] Run LLM judge.
- [ ] Manually audit 30–50 outputs.
- [ ] Fix scoring rules before looking too much at model comparisons.

### Analyze

- [ ] Compute FTGA.
- [ ] Compute RTT.
- [ ] Compute Repair@1 and Repair@2.
- [ ] Compute TokenTax.
- [ ] Make one table and two figures.

### Write

- [ ] Draft abstract.
- [ ] Draft method.
- [ ] Add results table.
- [ ] Add limitations.
- [ ] Add ethics statement.

---

## 33. Example benchmark items

These are illustrative. Replace or validate them before release.

### Spanish–English, editing preservation

```json
{
  "id": "es_en_A_001",
  "language_pair": "es-en",
  "task_family": "editing_preservation",
  "user_prompt": "Me puedes hacer este email más profesional, but keep it in English? \"Hi professor, I can't submit the homework today because my internet was down. Can I send it tomorrow?\"",
  "expected_response_language": "English",
  "expected_script": "Latin",
  "must_preserve_spans": [],
  "register_requirement": "professional email",
  "known_bad_outputs": ["Spanish translation", "Spanish explanation only"],
  "repair_prompt_1": "I wanted the email in English, not Spanish. Please revise it.",
  "repair_prompt_2": "Do not translate. Output only the polished English email."
}
```

### Hindi–English, script constraint

```json
{
  "id": "hi_en_D_001",
  "language_pair": "hi-en",
  "task_family": "script_register_locale",
  "user_prompt": "Write a short reply in Hindi but Latin script only, no Devanagari. Context: I need to tell my cousin I'll be 20 minutes late.",
  "expected_response_language": "Hindi/Hinglish",
  "expected_script": "Latin",
  "must_preserve_spans": [],
  "register_requirement": "polite casual WhatsApp message",
  "known_bad_outputs": ["Devanagari", "English only", "too formal"],
  "repair_prompt_1": "Please use Latin script, not Devanagari.",
  "repair_prompt_2": "Write it like a natural Hindi WhatsApp message using English letters only."
}
```

### Arabic–English, quote preservation

```json
{
  "id": "ar_en_C_001",
  "language_pair": "ar-en",
  "task_family": "quote_preservation",
  "user_prompt": "لخص النص التالي بالعربية، لكن لا تترجم العبارات بين علامتي الاقتباس: The update says that \"Project Greenlight\" will start after \"Phase Zero\" is approved.",
  "expected_response_language": "Arabic",
  "expected_script": "Arabic",
  "must_preserve_spans": ["Project Greenlight", "Phase Zero"],
  "register_requirement": "neutral concise summary",
  "known_bad_outputs": ["translated quoted phrases", "dropped quoted phrases"],
  "repair_prompt_1": "Please keep the quoted phrases in English exactly as written.",
  "repair_prompt_2": "Do not translate \"Project Greenlight\" or \"Phase Zero\". Keep them exactly."
}
```

### Spanish–English, output-language inference

```json
{
  "id": "es_en_B_001",
  "language_pair": "es-en",
  "task_family": "output_language_inference",
  "user_prompt": "Corrige la gramática de esta frase: \"I am looking forward to hear from you.\"",
  "expected_response_language": "English",
  "expected_script": "Latin",
  "must_preserve_spans": [],
  "register_requirement": "corrected sentence only or minimal explanation",
  "known_bad_outputs": ["Spanish translation", "Spanish explanation without corrected sentence"],
  "repair_prompt_1": "Please give the corrected English sentence.",
  "repair_prompt_2": "Output only the corrected English sentence, not a Spanish translation."
}
```

---

## 34. Related work to cite

Use these as starting references. Verify BibTeX and latest versions before submission.

1. **GenAI4World workshop call.**  
   Relevance: workshop motivation and fit.  
   URL: https://sites.google.com/view/genai4world/

2. **GenAI4World call for papers.**  
   Relevance: topics, page limits, non-archival status, ethics statement requirement.  
   URL: https://sites.google.com/view/genai4world/call-for-papers

3. **OLA: Output Language Alignment in Code-Switched LLM Interactions.**  
   Relevance: closest related benchmark on expected output language in code-switched prompts.  
   URL: https://arxiv.org/abs/2601.03589

4. **WildChat: 1M ChatGPT Interaction Logs in the Wild.**  
   Relevance: real-world, multi-turn, multilingual interaction logs.  
   URL: https://arxiv.org/html/2405.01470v1

5. **LMSYS-Chat-1M.**  
   Relevance: real-world conversation dataset with many languages and models.  
   URL: https://huggingface.co/datasets/lmsys/lmsys-chat-1m

6. **OpenAI GPT-4.1 API launch/pricing page.**  
   Relevance: model family, instruction following, pricing, and low-cost API feasibility.  
   URL: https://openai.com/index/gpt-4-1/

---

## 35. Final recommendation

Prioritize a **small, rigorous, memorable** paper:

> “We define Re-prompt Tax, build a 120–360 item multilingual benchmark, evaluate 3–5 API models, and show that global users often pay extra turns/tokens to repair language, script, preservation, register, and locale failures. A simple global-interaction prompt reduces the burden but does not eliminate it.”

That is a strong workshop contribution because it is:

- aligned with the venue,
- feasible with your budget,
- not dependent on training,
- easy to explain,
- useful to benchmark builders and product teams,
- extensible after the workshop.

