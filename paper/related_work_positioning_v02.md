# Related-Work Positioning for RePromptTax

This note keeps the paper's novelty claim narrow and reviewable. It is a
positioning artifact, not an additional experiment.

## Positioning Matrix

| Line of work | Representative sources | Main evaluation target | RePromptTax distinction |
|---|---|---|---|
| Broad multilingual capability benchmarks | MMLU-ProX, BenchMAX | Accuracy, reasoning, and instruction following across many languages | RePromptTax is smaller and synthetic, but targets interaction contracts that can be violated even when the answer is semantically plausible. |
| Multilingual verifiable instruction following | M-IFEval, XIFBench, Marco-Bench-MIF | Whether models satisfy explicit constraints in many languages | RePromptTax adopts verifiable constraints but scores the downstream repair burden after failures, rather than only first-turn compliance. |
| Output-language alignment in code-switched prompts | OLA | Whether the model infers the expected response language from pragmatic cues | RePromptTax includes output language but also script, literal span preservation, register, and locale constraints. |
| Multi-turn dialogue and instruction-following evaluation | MT-Bench, Chatbot Arena, StructFlowBench, MultiChallenge | Conversational quality, pairwise preference, structural dependencies, and realistic dialogue challenges | RePromptTax fixes a standardized repair protocol after a first-turn contract failure and measures turn/token burden to recover. |
| Real-world chat-log datasets | WildChat, LMSYS-Chat-1M | Observational diversity of public LLM use | RePromptTax uses only an aggregate cue scan for motivation and releases synthetic stress items rather than raw user logs. |

## Safe Novelty Claim

The paper should claim a metric and pilot protocol for hidden multilingual
repair burden, not broad multilingual ability, real-world prevalence, or
cross-provider generality. The defensible contribution is the combination of:

- first-turn contract alignment over language, script, preservation, register,
  and locale constraints,
- a fixed two-turn repair budget that yields RTT, Repair@1/2, unresolved rate,
  and token tax,
- a 120-item stress pilot spanning three GPT-4.1-family API models plus full
  current-model refreshes for `gpt-5.4-mini` and `gpt-5.5`,
- diagnostics that keep the mechanism and evaluation claims bounded:
  content-preservation prompt comparisons on current models, scorer-sensitivity
  checks, repair-realism checks, and two blinded LLM-judge audits,
- launch-ready human/native review protocols with pre-specified claim gates,
  while completed native/near-native validation remains a required next step
  before stronger final claims.

## Reviewer-Facing Caveats

- The benchmark is a synthetic stress pilot over three language pairs, not a
  representative prevalence study.
- OLA is the closest one-turn multilingual interaction benchmark; the paper's
  differentiator is recovery cost and a broader interaction contract.
- M-IFEval, XIFBench, and Marco-Bench-MIF are close multilingual
  instruction-following references; the paper's differentiator is measuring
  the repair trajectory after constraint failures.
- MT-Bench, Chatbot Arena, StructFlowBench, and MultiChallenge are the closest
  multi-turn evaluation reference points; the paper's differentiator is a
  controlled repair trajectory rather than open-ended dialogue preference or
  broad dialogue challenge coverage.
- The GPT-5.x refresh makes the result timely, but it should be framed as a
  current-model stress-pilot diagnostic rather than a broad leaderboard.
- The `gpt-5.5` headline is strongest on editing-preservation failures; the
  paper should explicitly retain the `gpt-5.4-mini` regression-risk caveat and
  the token-tax versus absolute-token distinction.
- Native-speaker validation is still required before stronger final claims.
