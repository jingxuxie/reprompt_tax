# Related-Work Positioning for RePromptTax

This note keeps the paper's novelty claim narrow and reviewable. It is a
positioning artifact, not an additional experiment.

## Positioning Matrix

| Line of work | Representative sources | Main evaluation target | RePromptTax distinction |
|---|---|---|---|
| Broad multilingual capability benchmarks | MMLU-ProX, BenchMAX | Accuracy, reasoning, and instruction following across many languages | RePromptTax is smaller and synthetic, but targets interaction contracts that can be violated even when the answer is semantically plausible. |
| Output-language alignment in code-switched prompts | OLA | Whether the model infers the expected response language from pragmatic cues | RePromptTax includes output language but also script, literal span preservation, register, and locale constraints. |
| Multi-turn dialogue evaluation and preference judging | MT-Bench, Chatbot Arena | Conversational quality, pairwise preference, and LLM-as-judge agreement | RePromptTax fixes a standardized repair protocol after a first-turn contract failure and measures turn/token burden to recover. |
| Real-world chat-log datasets | WildChat, LMSYS-Chat-1M | Observational diversity of public LLM use | RePromptTax uses only an aggregate cue scan for motivation and releases synthetic stress items rather than raw user logs. |

## Safe Novelty Claim

The paper should claim a metric and pilot protocol for hidden multilingual
repair burden, not broad multilingual ability, real-world prevalence, or
cross-provider generality. The defensible contribution is the combination of:

- first-turn contract alignment over language, script, preservation, register,
  and locale constraints,
- a fixed two-turn repair budget that yields RTT, Repair@1/2, unresolved rate,
  and token tax,
- a stress pilot showing the burden on three GPT-4.1-family API models, with
  prompt-control, content-preservation, scorer-sensitivity, and judge-audit
  diagnostics.

## Reviewer-Facing Caveats

- The benchmark is a synthetic stress pilot over three language pairs, not a
  representative prevalence study.
- OLA is the closest one-turn multilingual interaction benchmark; the paper's
  differentiator is recovery cost and a broader interaction contract.
- MT-Bench and Chatbot Arena are the closest multi-turn evaluation reference
  points; the paper's differentiator is a controlled repair trajectory rather
  than open-ended dialogue preference.
- Native-speaker validation is still required before stronger final claims.
