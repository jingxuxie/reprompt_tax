# Qualitative Examples From Stress Pilot

These examples are drawn from the paper-facing full-v0.2 artifacts:
`results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl` and
`results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv`.

## Example 1: Unwanted Translation In Editing

- Item: `es_en_SA_004`
- Model/condition: `gpt-4.1-nano`, baseline
- Failure type: wrong output language + task noncompletion
- RTT: 1

User prompt:

```text
Me ayudas a mejorar este texto para que suene natural? "I can't join the call today, but I can share my update by email."
```

First response:

```text
Claro, aquí tienes una versión más natural y fluida del texto:
"No puedo unirme a la llamada hoy, pero puedo enviar mi actualización por correo."
```

Why it fails: the model translated the English content into Spanish instead of
editing it in English.

Recovery after repair prompt 1:

```text
Of course! Here's a more natural-sounding version in English:
"I won't be able to join the call today, but I can send my update via email."
```

## Example 2: Strong Model Still Pays Preamble Tax

- Item: `es_en_SA_004`
- Model/condition: `gpt-4.1`, baseline
- Failure type: wrong output language
- RTT: 1

First response excerpt:

```text
¡Por supuesto! Aquí tienes algunas opciones para que suene más natural:
1. I won't be able to join the call today, but I can send my update by email.
...
Cualquiera de estas opciones suena natural y profesional.
```

Why it fails: the edited content is English, but the answer wraps it in Spanish
instructions and follow-up text. The content is useful, but the user still has
to repair the interaction contract.

Matched contract condition on the same item passes first turn:

```text
Sure! Here’s a more natural version:
"I won't be able to join the call today, but I can send my update by email."
```

## Example 3: Quote Preservation Failure And Recovery

- Item: `ar_en_SC_002`
- Model/condition: `gpt-4.1-nano`, contract
- Failure type: quote preservation failure + task noncompletion
- RTT: 1

User prompt:

```text
لخص هذا بالعربية، لكن اترك العناوين بين علامتي الاقتباس كما هي بالإنجليزية:
The document lists "Budget Review" before "Community Questions".
```

First response:

```text
الوثيقة تتضمن مراجعة الميزانية قبل قسم "أسئلة المجتمع".
```

Why it fails: both quoted English headings are translated instead of preserved.

Recovery after repair prompt 1:

```text
الوثيقة تتضمن "Budget Review" قبل قسم "Community Questions".
```

## Example 4: Unresolved Within Repair Budget

- Item: `ar_en_SC_002`
- Model/condition: `gpt-4.1-nano`, baseline
- Failure type: quote preservation failure + task noncompletion
- RTT: 3, unresolved after two repairs

First response:

```text
بالطبع، يرجى تزويدي بالنص الذي ترغب في تلخيصه.
```

After repair prompt 2:

```text
بالطبع، يرجى تزويدي بالنص الذي ترغب في تلخيصه وسأقوم بذلك مع الالتزام بعدم ترجمة أو تغيير العناوين المقتبسة.
```

Why it fails: the model repeatedly asks for text even though the text is already
present in the prompt.

## Example 5: Script/Locale Literal Preservation

- Item: `hi_en_SD_005`
- Model/condition: `gpt-4.1-nano`, baseline
- Failure type: wrong output language
- RTT: 1

User prompt:

```text
Hindi mein short WhatsApp reply likho, Latin script only, no Devanagari.
Context mein exact data same rakhna. Context: Tell my classmate that the file
name draft_v2.pdf should stay unchanged.
```

First response:

```text
The file name draft_v2.pdf should stay unchanged.
```

Recovery after repair prompt 1:

```text
draft_v2.pdf ko badalna nahi hai.
```

Why it matters: the first response preserves the literal filename but ignores
the requested Hindi/Hinglish WhatsApp style.
