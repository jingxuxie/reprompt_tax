# Repair-Realism Diagnostic

This diagnostic compares the saved standardized first repair prompt against
three user-like one-turn repair prompts on a deterministic 24-item sample of
baseline editing-preservation first-turn failures. The sample is balanced
across the three GPT-4.1-family models and Arabic-English/Spanish-English
editing failures.

## Summary

| Repair prompt | n | Success | Task pass | Language pass | Preservation pass | Apology without task | Mean tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| standard | 24 | 24/24 (100.0%) | 24/24 (100.0%) | 24/24 (100.0%) | 24/24 (100.0%) | 0 | 181.7 |
| terse | 24 | 24/24 (100.0%) | 24/24 (100.0%) | 24/24 (100.0%) | 24/24 (100.0%) | 0 | 189.1 |
| frustrated | 24 | 17/24 (70.8%) | 24/24 (100.0%) | 17/24 (70.8%) | 24/24 (100.0%) | 0 | 184.5 |
| explicit | 24 | 5/24 (20.8%) | 17/24 (70.8%) | 5/24 (20.8%) | 24/24 (100.0%) | 0 | 192.4 |

## Paired Effects Against Standard Repair

| Comparison | Improved | Worsened | Tied | Sign p | Success delta | Mean token delta |
|---|---:|---:|---:|---:|---:|---:|
| terse_keep_english_minus_standard_saved | 0 | 0 | 24 | 1 | +0.0 pp | +7.5 |
| frustrated_dont_translate_minus_standard_saved | 0 | 7 | 17 | 0.015625 | -29.2 pp | +2.9 |
| explicit_contract_minus_standard_saved | 0 | 19 | 5 | 3.8147e-06 | -79.2 pp | +10.7 |

## By Model

| Model | Repair prompt | n | Success | Mean tokens |
|---|---|---:|---:|---:|
| gpt-4.1 | explicit | 8 | 1/8 (12.5%) | 228.2 |
| gpt-4.1 | frustrated | 8 | 5/8 (62.5%) | 217.8 |
| gpt-4.1 | standard | 8 | 8/8 (100.0%) | 217.6 |
| gpt-4.1 | terse | 8 | 8/8 (100.0%) | 223.5 |
| gpt-4.1-mini | explicit | 8 | 0/8 (0.0%) | 191.6 |
| gpt-4.1-mini | frustrated | 8 | 8/8 (100.0%) | 187.6 |
| gpt-4.1-mini | standard | 8 | 8/8 (100.0%) | 177.2 |
| gpt-4.1-mini | terse | 8 | 8/8 (100.0%) | 193.6 |
| gpt-4.1-nano | explicit | 8 | 4/8 (50.0%) | 157.2 |
| gpt-4.1-nano | frustrated | 8 | 4/8 (50.0%) | 148.2 |
| gpt-4.1-nano | standard | 8 | 8/8 (100.0%) | 150.1 |
| gpt-4.1-nano | terse | 8 | 8/8 (100.0%) | 150.2 |

## Variant Disagreements

| Item | Model | Language | Variant | Standard pass | Variant pass | Variant failures | Response excerpt |
|---|---|---|---|---:|---:|---|---|
| ar_en_SA_001 | gpt-4.1-mini | ar-en | explicit | True | False | ["wrong_output_language", "script_mismatch", "task_noncompletion"] | بكل سرور! إليك نصك بعد تحسينه ليصبح أوضح وأكثر لطفاً مع الحفاظ على اللغة الإنجليزية:  "Hi team, I have finished the notes. I’m not entirely sure if the conclusion is clear, so I would really appreciate it if you could take a look and share  |
| ar_en_SA_002 | gpt-4.1 | ar-en | explicit | True | False | ["wrong_output_language", "script_mismatch", "task_noncompletion"] | شكرًا للتوضيح! إليك نص مُحسّن وأكثر لطفًا باللغة الإنجليزية:  Hello, I hope you are well. I wanted to let you know that my train was delayed, and I will not be able to make it to my appointment on time. Would it be possible to reschedule? T |
| ar_en_SA_005 | gpt-4.1 | ar-en | explicit | True | False | ["wrong_output_language", "script_mismatch", "task_noncompletion"] | شكرًا للتوضيح! إليك نسخة محسّنة وأكثر لطفًا ووضوحًا من الجملة:  "The first paragraph is somewhat lengthy, and the tone of the final sentence could be softened for greater politeness."  أو يمكنك استخدام:  "The first paragraph could be shorte |
| ar_en_SA_006 | gpt-4.1 | ar-en | explicit | True | False | ["wrong_output_language", "script_mismatch", "task_noncompletion"] | شكرًا للتوضيح! إليك نسخة محسّنة وأكثر وضوحًا ولطفًا من النص باللغة الإنجليزية:  "I have reviewed the report, and I noticed that the second chart might be a bit confusing for readers who are new to the subject. It may be helpful to clarify o |
| ar_en_SA_006 | gpt-4.1-mini | ar-en | explicit | True | False | ["wrong_output_language", "script_mismatch", "task_noncompletion"] | بالطبع! إليك نسخة محسّنة للنص باللغة الإنجليزية مع الحفاظ على الطابع اللطيف والواضح:  "I have reviewed the report, and I noticed that the second chart might be a little confusing for readers who are new to the subject. It could be helpful t |
| ar_en_SA_007 | gpt-4.1-mini | ar-en | explicit | True | False | ["wrong_output_language", "script_mismatch", "task_noncompletion"] | بالطبع! إليك نصًا محسنًا وأكثر لطفًا باللغة الإنجليزية:  "Could you please inform the client that the payment is expected to arrive next week? Thank you very much for your help."  هل تود نسخة أخرى بصيغة مختلفة؟ |
| ar_en_SA_009 | gpt-4.1-mini | ar-en | explicit | True | False | ["wrong_output_language", "script_mismatch", "task_noncompletion"] | بالطبع! إليك نصًا محسنًا باللغة الإنجليزية مع الحفاظ على اللطف والوضوح:  "I would like to kindly ask if I could have one more day to finish the slide deck. I want to make sure it’s complete and well-prepared. Thank you very much for your un |
| es_en_SA_001 | gpt-4.1-mini | es-en | explicit | True | False | ["wrong_output_language"] | Perfecto, aquí tienes una versión mejorada que suena más natural en inglés:  "Hi team, I’ve finished the notes, but I’m not sure if the conclusion is clear."  Si quieres, puedo ayudarte a hacerla más formal o más informal. ¿Quieres? |
| es_en_SA_002 | gpt-4.1 | es-en | frustrated | True | False | ["wrong_output_language"] | ¡Gracias por aclararlo! Aquí tienes una versión mejorada y más natural de tu texto en inglés:  "Hi, I need to reschedule my appointment because my train has been delayed."  Otras opciones naturales podrían ser:  - "Hello, I need to change m |
| es_en_SA_002 | gpt-4.1 | es-en | explicit | True | False | ["wrong_output_language"] | ¡Entendido! Aquí tienes algunas opciones mejoradas en inglés, manteniendo el contenido original pero sonando más natural:  1. Hi, I need to reschedule my appointment because my train was delayed. 2. Hello, I need to change my appointment as |
| es_en_SA_002 | gpt-4.1-mini | es-en | explicit | True | False | ["wrong_output_language"] | Por supuesto, aquí tienes una versión más natural en inglés:  "Hello, I need to reschedule my appointment because my train was delayed."  Si quieres que suene un poco más formal, podrías decir:  "Hello, I would like to reschedule my appoint |
| es_en_SA_005 | gpt-4.1 | es-en | explicit | True | False | ["wrong_output_language"] | ¡Entendido! Aquí tienes una versión mejorada y natural en inglés:  "The first paragraph is quite long, and the last sentence sounds a little too blunt."  Si quieres que suene más formal o más suave, dime y lo ajusto. |
| es_en_SA_006 | gpt-4.1-mini | es-en | explicit | True | False | ["wrong_output_language"] | Perfecto, aquí tienes una versión mejorada en inglés, con un tono natural:  "I reviewed the report, and the second chart might be a bit confusing for new readers."  ¿Quieres que sea más formal o más informal? |
| es_en_SA_006 | gpt-4.1-nano | es-en | frustrated | True | False | ["wrong_output_language"] | ¡Entendido! Aquí tienes una versión más natural en inglés:   "I looked over the report, and the second chart might be a bit confusing for new readers." |
| es_en_SA_006 | gpt-4.1-nano | es-en | explicit | True | False | ["wrong_output_language"] | Entendido. Aquí tienes una versión más natural en inglés:   "I reviewed the report, and the second chart might be a bit confusing for new readers." |
| es_en_SA_007 | gpt-4.1-nano | es-en | frustrated | True | False | ["wrong_output_language"] | ¡Entendido! Aquí tienes una versión más natural en inglés:    "Can you let the client know that the payment will be arriving next week?"    ¿Quieres que sea más formal, informal o simplemente más natural? |
| es_en_SA_007 | gpt-4.1-nano | es-en | explicit | True | False | ["wrong_output_language"] | ¡Entendido! Aquí tienes una versión más natural en inglés, manteniendo la instrucción en español:    "Could you inform the client that the payment will arrive next week?"    ¿Quieres que sea más formal, informal o simplemente más natural? |
| es_en_SA_008 | gpt-4.1-mini | es-en | explicit | True | False | ["wrong_output_language"] | Entendido, aquí tienes una versión más natural en inglés:  “The survey question comes across as too direct and might make people feel uncomfortable.”   ¿Quieres que lo haga más formal o más casual? |
| es_en_SA_008 | gpt-4.1-nano | es-en | frustrated | True | False | ["wrong_output_language"] | Entendido. Aquí tienes una versión más natural en inglés:  "The survey question feels a bit too direct and might make people uncomfortable." |
| es_en_SA_008 | gpt-4.1-nano | es-en | explicit | True | False | ["wrong_output_language"] | Entendido. Aquí tienes una versión más natural en inglés, manteniendo la instrucción en español:  "The survey question feels a bit too direct and might make people uncomfortable." |
| es_en_SA_009 | gpt-4.1 | es-en | frustrated | True | False | ["wrong_output_language"] | ¡Perfecto! Aquí tienes algunas formas de mejorar la frase en inglés para que suene más natural:  1. I need to ask my manager for an extra day to finish the slide deck. 2. I need to request one more day from my manager to finish the slide de |
| es_en_SA_009 | gpt-4.1 | es-en | explicit | True | False | ["wrong_output_language"] | ¡Entendido! Aquí tienes algunas opciones mejoradas y naturales en inglés:  1. I need to ask my manager for an extra day to finish the slide deck. 2. I need to request one more day from my manager to complete the slide deck. 3. I need to ask |
| es_en_SA_009 | gpt-4.1-nano | es-en | frustrated | True | False | ["wrong_output_language"] | ¡Entendido! Aquí tienes una versión más natural en inglés:   "I need to ask my manager for one more day to finish the slide deck."    ¿Quieres que sea aún más informal o formal? |
| es_en_SA_009 | gpt-4.1-nano | es-en | explicit | True | False | ["wrong_output_language"] | ¡Entendido! Aquí tienes una versión más natural en inglés:   "I need to ask my manager for one more day to finish the slide deck."    ¿Quieres que sea aún más informal o formal? |
| es_en_SA_010 | gpt-4.1 | es-en | frustrated | True | False | ["wrong_output_language"] | ¡Perfecto! Entonces, aquí tienes algunas opciones mejoradas y naturales en inglés:  1. Please let the tenant know that we have fixed the heating issue and will check it again tomorrow. 2. Please inform the tenant that the heating problem ha |
| es_en_SA_010 | gpt-4.1 | es-en | explicit | True | False | ["wrong_output_language"] | ¡Perfecto! Aquí tienes algunas opciones mejoradas y naturales en inglés, siguiendo tu instrucción:  1. Please let the tenant know that we have fixed the heating issue and will check it again tomorrow. 2. Please inform the tenant that the he |

## Interpretation

The saved standardized repair succeeds on 24/24 sampled failures.
The explicit user-like contract repair succeeds on 5/24,
while the terse repair succeeds on 24/24.
This is a small interaction-realism diagnostic, not a replacement for a
full user study. It shows whether RTT conclusions are sensitive to the
wording of the first repair prompt on the dominant editing-preservation
failure mode.
