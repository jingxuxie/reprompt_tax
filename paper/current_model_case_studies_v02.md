# Current-Model Case Studies

These case studies are generated from saved GPT-5.x full-120 score logs
and benchmark rows. They make no new API calls and are intended to
make the current-model headline and lower-cost-model boundary inspectable.

Source artifacts:

- `results/scores/openai_gpt55_stress_v02_full120_auto_scores.jsonl`
- `results/scores/openai_gpt54mini_stress_v02_full120_auto_scores.jsonl`
- `data/benchmark_stress_v0.2.jsonl`

## Summary Table

| Case | Model | Condition | Item | RTT | Unresolved | First failure types | Interpretation |
|---|---|---|---|---:|---:|---|---|
| gpt55_baseline_fixed_by_contract | gpt-5.5 | baseline | `es_en_SA_001` | 1 | 0 | wrong_output_language,task_noncompletion | Baseline preserves useful English edits but wraps them in Spanish; the matched contract row passes first turn. |
| gpt55_contract_residual_repairs | gpt-5.5 | contract | `es_en_SA_004` | 1 | 0 | wrong_output_language | The contract nearly solves editing preservation, but one Spanish wrapper still creates a first-turn language failure that repairs in one turn. |
| gpt54mini_contract_quote_unresolved | gpt-5.4-mini | contract | `hi_en_SC_003` | 3 | 1 | wrong_output_language | The lower-cost current model preserves quoted English headings but never switches to the requested Hindi/Hinglish Latin-script summary. |
| gpt54mini_contract_literal_unresolved | gpt-5.4-mini | contract | `ar_en_SD_008` | 3 | 1 | preservation_failure | The lower-cost current model follows Arabic script but localizes the literal date instead of preserving the requested exact span. |

## GPT-5.5 baseline still pays wrapper tax

- Case ID: `gpt55_baseline_fixed_by_contract`
- Item: `es_en_SA_001` (es-en, editing_preservation)
- Model/condition: `gpt-5.5` / `baseline`
- Expected response: English in Latin script
- RTT: 1; unresolved: 0
- First failure types: wrong_output_language,task_noncompletion

User prompt excerpt:

```text
Me ayudas a mejorar este texto para que suene natural? "Hi team, I finished the notes but I am not sure if the conclusion is clear."
```

First response excerpt:

```text
Claro. Una versión más natural sería: **“Hi team, I’ve finished the notes, but I’m not sure if the conclusion is clear.”** También podrías decir, un poco más fluido: **“Hi team, I’ve finished the notes, but I’m not sure the conclusion is clear enough.”** O...
```

Final saved response excerpt after turn 1:

```text
Of course. Here are a few natural options in English: **“Hi team, I’ve finished the notes, but I’m not sure if the conclusion is clear.”** A slightly more natural version: **“Hi team, I’ve finished the notes, but I’m not sure the conclusion is clear enough....
```

Matched `contract` first response excerpt:

```text
"Hi team, I’ve finished the notes, but I’m not sure the conclusion is clear."
```

Interpretation: Baseline preserves useful English edits but wraps them in Spanish; the matched contract row passes first turn.

## GPT-5.5 contract residual repairs immediately

- Case ID: `gpt55_contract_residual_repairs`
- Item: `es_en_SA_004` (es-en, editing_preservation)
- Model/condition: `gpt-5.5` / `contract`
- Expected response: English in Latin script
- RTT: 1; unresolved: 0
- First failure types: wrong_output_language

User prompt excerpt:

```text
Me ayudas a mejorar este texto para que suene natural? "I can't join the call today, but I can share my update by email."
```

First response excerpt:

```text
“I can’t join the call today, but I can share my update by email.” También suena natural así: “I won’t be able to join the call today, but I can send my update by email.”
```

Final saved response excerpt after turn 1:

```text
I won’t be able to join the call today, but I can send my update by email.
```

Interpretation: The contract nearly solves editing preservation, but one Spanish wrapper still creates a first-turn language failure that repairs in one turn.

## GPT-5.4-mini repeats English in a Hindi/Hinglish quote task

- Case ID: `gpt54mini_contract_quote_unresolved`
- Item: `hi_en_SC_003` (hi-en, quote_preservation)
- Model/condition: `gpt-5.4-mini` / `contract`
- Expected response: Hindi/Hinglish in Latin script
- RTT: 3; unresolved: 1
- First failure types: wrong_output_language

User prompt excerpt:

```text
Hindi mein short summary do, Latin script only. Quoted headings ko exactly English mein rakho: The document lists "Safety Guidelines" before "Emergency Contact".
```

First response excerpt:

```text
The document lists "Safety Guidelines" before "Emergency Contact".
```

Final saved response excerpt after turn 2:

```text
The document lists "Safety Guidelines" before "Emergency Contact".
```

Interpretation: The lower-cost current model preserves quoted English headings but never switches to the requested Hindi/Hinglish Latin-script summary.

## GPT-5.4-mini changes literal date format in Arabic script

- Case ID: `gpt54mini_contract_literal_unresolved`
- Item: `ar_en_SD_008` (ar-en, script_register_locale)
- Model/condition: `gpt-5.4-mini` / `contract`
- Expected response: Arabic in Arabic script
- RTT: 3; unresolved: 1
- First failure types: preservation_failure

User prompt excerpt:

```text
اكتب رد واتساب قصير بالعربية. حافظ على البيانات المذكورة في السياق كما هي تماماً. السياق: Tell HR I can start on June 12 and the employee ID QR-77 should stay the same.
```

First response excerpt:

```text
أخبر الموارد البشرية أنني أستطيع البدء في 12 يونيو، وأن رقم الموظف QR-77 يجب أن يبقى كما هو.
```

Final saved response excerpt after turn 2:

```text
أخبر الموارد البشرية أنني أستطيع البدء في 12 يونيو، وأن رقم الموظف QR-77 يجب أن يبقى كما هو.
```

Interpretation: The lower-cost current model follows Arabic script but localizes the literal date instead of preserving the requested exact span.

## Claim Boundary

These examples are qualitative diagnostics from saved automatic-score
rows. They support the paper's interpretation of residual burden, but
they do not replace native/near-native human validation.
