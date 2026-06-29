# The Re-prompt Tax Persists: Measuring Hidden Interaction Costs for Multilingual and Code-Switched LLM Users

## Abstract

Multilingual users often interact with LLMs through code-switched prompts,
mixed-language editing requests, and constraints about script, register,
locale, and literal text preservation. Standard one-turn evaluations miss a
common usability failure: the model returns a fluent, plausible answer that
violates the user's interaction contract, forcing the user to spend extra turns
repairing the response. We introduce **Re-prompt Tax**, a metric family that
measures the turns, tokens, and repair success required to recover from these
failures. We construct a 120-item stress pilot across Spanish-English,
Hindi-English, and Arabic-English interactions and evaluate three GPT-4.1-family
API models under a baseline prompt and a Global Interaction Contract prompt,
then add full 120-item current-model refreshes for `gpt-5.4-mini` and
`gpt-5.5`. Baseline first-turn global alignment ranges from 67.5% to 76.7% on
the GPT-4.1-family runs; the mitigation improves alignment to 76.7%-93.3% and
reduces mean repair turns and token tax. The current-model refresh shows the
same pressure under `gpt-5.5`: alignment rises from 81.7% to 98.3%, mean repair
turns fall from 0.225 to 0.017, and unresolved trajectories fall to 0.0% while
two first-turn residuals remain. A 72-row stratified blinded LLM-judge audit of
the GPT-4.1-family first-turn surface agrees with the automatic scorer on 71/72
sampled pass/fail labels, and a paired GPT-5.5 judge refresh agrees on 70/72
labels. Deterministic scorer stress tests fail 390/390 known-bad probes and
accept 120/120 constrained positive-control templates, while native-speaker
validation remains launch-ready but incomplete.

## 1. Motivation

The GenAI4World workshop asks how evaluation should move beyond standard
performance metrics to capture register, cultural expectation, and usability
across contexts. Re-prompt Tax targets one such gap: a model may be semantically
helpful while still making the interaction more expensive for multilingual
users.

Consider a user who asks in Spanish to improve an English message:

> Me ayudas a mejorar este texto para que suene natural? "I can't join the call
> today, but I can share my update by email."

A globally aligned model should infer that the quoted content is the object of
editing and should remain English unless translation is requested. In our pilot,
models often produce Spanish preambles or full Spanish translations. These
answers are fluent, but they require the user to re-prompt: "Please keep the
rewritten text in English."

## 2. Re-prompt Tax

We define **First-Turn Global Alignment** (FTGA) as whether the first response
satisfies the expected language, script, preservation, task, register, and
locale constraints. We define **Re-prompt Turn Tax** (RTT) as the minimum number
of standardized repair prompts needed before success, with a budget of two
repair turns. We also report unresolved rate, Repair@1, Repair@2, and token tax.

This differs from one-turn output-language alignment benchmarks such as OLA by
measuring not only whether the model chooses the expected language, but also how
costly it is to recover after failures involving content-language preservation,
quoted spans, script constraints, and locale-sensitive literal data.

## 3. Benchmark and Protocol

We created `RePromptTax-Stress-v0.2`, a 120-item pilot with three language pairs:
Spanish-English, Hindi-English, and Arabic-English. Each pair has ten items in
four task families:

1. implicit editing preservation,
2. output-language inference,
3. quote/proper-noun preservation,
4. script/register/locale constraints.

Each item includes the user prompt, expected output language and script, literal
spans that must be preserved, task/register notes, and two standardized repair
prompts. We evaluated `gpt-4.1-nano`, `gpt-4.1-mini`, and `gpt-4.1` with
temperature 0 under two system prompts: a generic baseline and a Global
Interaction Contract that explicitly instructs the assistant to infer language,
script, content-preservation, register, and locale constraints before
answering. We then ran full 120-item current-model refreshes for
`gpt-5.4-mini` and `gpt-5.5` under the same baseline and contract conditions,
plus a content-preservation diagnostic on both current models. Experiments were
run on June 28, 2026.

Scoring combines deterministic checks for exact span preservation and script
with rule-based language/task checks. We also ran a blinded `gpt-4.1` judge
audit on 72 first-turn responses, sampling three examples from every
model-condition-family stratum, and a paired `gpt-5.5` judge refresh on the
same 72 rows. The judge saw only the user prompt, expected contract, and
assistant response, not the model identity or condition.

## 4. Results

| Model | Condition | FTGA | Mean RTT | Token tax | Unresolved | Repair@1 | Repair@2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-4.1-nano | baseline | 67.5% | 0.47 | 1.69x | 5.8% | 74.4% | 82.1% |
| gpt-4.1-nano | contract | 76.7% | 0.33 | 1.34x | 4.2% | 78.6% | 82.1% |
| gpt-4.1-mini | baseline | 75.8% | 0.28 | 1.43x | 0.8% | 89.7% | 96.6% |
| gpt-4.1-mini | contract | 79.2% | 0.24 | 1.27x | 1.7% | 92.0% | 92.0% |
| gpt-4.1 | baseline | 76.7% | 0.28 | 1.43x | 2.5% | 89.3% | 89.3% |
| gpt-4.1 | contract | 93.3% | 0.15 | 1.13x | 4.2% | 37.5% | 37.5% |
| gpt-5.4-mini | baseline | 80.0% | 0.25 | 1.38x | 2.5% | 87.5% | 87.5% |
| gpt-5.4-mini | contract | 85.0% | 0.25 | 1.24x | 5.0% | 66.7% | 66.7% |
| gpt-5.5 | baseline | 81.7% | 0.23 | 1.28x | 1.7% | 86.4% | 90.9% |
| gpt-5.5 | contract | 98.3% | 0.02 | 1.02x | 0.0% | 100.0% | 100.0% |

The current-model refresh makes the persistence claim timely. On the same 120
items, `gpt-5.4-mini` moves from 80.0% to 85.0% FTGA with lower token tax but a
higher unresolved rate, so we treat that as a bounded lower-cost result. The
full `gpt-5.5` run is cleaner: FTGA rises from 81.7% to 98.3%, token tax falls
from 1.28x to 1.02x, and all trajectories resolve within the two-repair budget.
The remaining two GPT-5.5 contract first-turn failures are both
Spanish-English editing-preservation cases that repair after one prompt.

Paired sign-test sensitivity over item-level FTGA changes gives 12 improved vs
1 worsened item for `gpt-4.1-nano` (two-sided p=0.0034), 4 vs 0 for
`gpt-4.1-mini` (p=0.1250), and 20 vs 0 for `gpt-4.1` (p<0.0001). We therefore
treat the mini FTGA effect as directional rather than strong standalone
evidence.

A single-model prompt-control diagnostic on `gpt-4.1-nano` shows that generic
helpfulness scaffolding explains much of the mitigation effect: FTGA rises from
67.5% to 75.0% under a longer generic helpfulness prompt, while the Global
Interaction Contract reaches 76.7%. A content-preservation ablation reaches
80.0% FTGA and the lowest token tax, suggesting that content-language and
literal-preservation rules drive much of the effect. We therefore do not claim
that the full contract is the best prompt tested or that every gain is unique to
multilingual-contract wording.

The largest baseline failure mode is implicit editing preservation: across the
GPT-4.1-family models, 60/90 editing-preservation trajectories fail on the
first turn and the aggregate family FTGA is 33.3%. The GPT-4.1-family error
atlas lists 157 first-turn failures across baseline and contract conditions,
including 87 editing-preservation failures and 23 unresolved cases. The
current-model residual analysis keeps the refresh boundary separate: under the
contract, `gpt-5.5` leaves two first-turn failures and zero unresolved
trajectories, while `gpt-5.4-mini` leaves 18 first-turn failures and six
unresolved trajectories. For `gpt-4.1`, the Global Interaction Contract raises
editing-preservation FTGA from 33.3% to 96.7%.

The cheaper model shows an additional weakness: quote-preservation failures.
`gpt-4.1-nano` translates semantically transparent quoted headings such as
`"Budget Review"` and `"Community Questions"` despite explicit preservation
instructions. Under the contract prompt, nano quote-preservation FTGA rises
from 70.0% to 73.3%, mean RTT drops from 0.63 to 0.37, and unresolved rate
drops from 13.3% to 3.3%. The stronger two models pass those quote-preservation cases in
this pilot.

The judge audits and deterministic scorer stress tests support the scoring used
for the main table. On 72 sampled first-turn responses from the GPT-4.1-family
surface, the original blinded GPT-4.1 judge and corrected automatic scorer
agree on 71/72 pass/fail labels (98.6%). A paired GPT-5.5 judge refresh agrees
with the automatic scorer on 70/72 labels and with the GPT-4.1 judge on 69/72
labels. Separately, known-bad probes fail all 390/390 deterministic challenge
cases and constrained positive-control templates pass 120/120 cases. This does
not replace native-speaker validation, but it reduces the immediate risk that
the headline trend is an artifact of the automatic rules.

## 5. Related Work

Recent multilingual LLM benchmarks such as MMLU-ProX and BenchMAX broaden
accuracy and instruction-following evaluation across many languages. OLA studies
output language alignment in code-switched LLM interactions and shows that
models can fail to infer expected response language from pragmatic cues.
Multi-turn dialogue evaluations such as MT-Bench and Chatbot Arena evaluate
conversational quality and preference agreement; Re-prompt Tax instead fixes the
initial contract violation and measures the standardized repair trajectory.
Re-prompt Tax is complementary: it measures the interactional cost of recovering
from failures, and extends the contract beyond output language to script,
preservation, register, and locale constraints.

Real-world conversation datasets such as WildChat and LMSYS-Chat-1M motivate
studying multi-turn repair, because they show that public LLM use is diverse,
multilingual, and interactional. We do not release raw user logs in this pilot;
all benchmark items are synthetic and designed for privacy-safe evaluation.

## 6. Limitations and Ethics

This is a pilot benchmark, not a representative sample of global multilingual
use. It covers only three language pairs and uses synthetic prompts. Automatic
checks are useful for exact spans and scripts, but language, register, and
locale judgments should be audited by native speakers before any stronger
native-validation or cultural-appropriateness claim. The benchmark should not
be interpreted as characterizing all Spanish, Hindi, Arabic, or code-switched
users.

The intended impact is to make global usability failures measurable: a model
that looks cheaper or more accurate on the first turn may impose hidden repair
costs on users whose language, script, and preservation expectations are not
well represented by standard evaluations.

## Reference Starting Points For LaTeX

- GenAI4World COLM 2026 workshop call:
  https://sites.google.com/view/genai4world/call-for-papers
- OLA: Output Language Alignment in Code-Switched LLM Interactions:
  https://arxiv.org/abs/2601.03589
- MMLU-ProX: A Multilingual Benchmark for Advanced Large Language Model Evaluation:
  https://arxiv.org/abs/2503.10497
- BenchMAX: A Comprehensive Multilingual Evaluation Suite for Large Language Models:
  https://arxiv.org/abs/2502.07346
- WildChat: 1M ChatGPT Interaction Logs in the Wild:
  https://arxiv.org/abs/2405.01470
- LMSYS-Chat-1M:
  https://arxiv.org/abs/2309.11998
