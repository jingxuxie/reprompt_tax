# RePromptTax First-Turn Error Atlas

Generated from `results/scores/openai_three_model_stress60_auto_scores.jsonl`.

This atlas lists first-turn failures only. It is intended for paper writing,
manual inspection, and audit triage; it is not an additional evaluation run.

## Summary

- First-turn failures: 59
- Unresolved after two repair prompts: 5

### Failures by Task Family

| Task family | Failures |
|---|---:|
| Editing preservation | 42 |
| Quote preservation | 10 |
| Script/register/locale | 7 |

### Failures by Model and Condition

| Model | Condition | Failures |
|---|---|---:|
| gpt-4.1 | baseline | 10 |
| gpt-4.1-mini | baseline | 11 |
| gpt-4.1-mini | contract | 8 |
| gpt-4.1-nano | baseline | 18 |
| gpt-4.1-nano | contract | 12 |

### Unresolved Cases

| Item | Model | Condition | Family | Failure types |
|---|---|---|---|---|
| ar_en_SC_001 | gpt-4.1-nano | baseline | Quote preservation | preservation_failure;task_noncompletion |
| ar_en_SC_002 | gpt-4.1-nano | baseline | Quote preservation | preservation_failure;task_noncompletion |
| ar_en_SC_003 | gpt-4.1-nano | baseline | Quote preservation | preservation_failure;task_noncompletion |
| ar_en_SC_004 | gpt-4.1-nano | contract | Quote preservation | preservation_failure;task_noncompletion |
| ar_en_SC_005 | gpt-4.1-nano | baseline | Quote preservation | preservation_failure;task_noncompletion |

## Atlas

| Item | Lang | Family | Model | Condition | RTT | Failure types | Response excerpt |
|---|---|---|---|---|---:|---|---|
| ar_en_SA_001 | ar-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة محسّنة وأكثر وضوحًا ولطفًا من النص: "Hi team, I’ve finished writing the notes. I would appreciate it if you could take a look, especially at the conclusion, as... |
| ar_en_SA_001 | ar-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة محسّنة وأكثر لطفاً ووضوحاً من النص: "Hi team, I have finished the notes. Could you please take a look and let me know if the conclusion is clear enough? I appr... |
| ar_en_SA_001 | ar-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة أكثر وضوحًا ولطفًا من النص: "مرحبًا فريق، لقد أنجزت الملاحظات، لكنني لست متأكدًا إذا كانت الخاتمة واضحة بما يكفي. أرجو أن تتفضلوا بمراجعتها وإبداء ملاحظاتكم. ش... |
| ar_en_SA_002 | ar-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة أوضح وأكثر لطفاً من النص: "Hello, I hope you’re well. I would like to kindly request to reschedule my appointment, as my train was delayed. Thank you very much... |
| ar_en_SA_002 | ar-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نصًا محسنًا وأكثر لطفًا ووضوحًا: "Hello, I hope you're doing well. I would like to kindly request to reschedule my appointment because my train has been delayed. Th... |
| ar_en_SA_002 | ar-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة أكثر لطفًا ووضوحًا من النص: "مرحبًا، أود أن أغير موعدي بسبب تأخير قطاري، هل يمكنكم مساعدتي في ذلك؟ شكرًا جزيلًا لكم." |
| ar_en_SA_003 | ar-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة محسّنة وأكثر لطفاً ووضوحاً من النص: Thank you very much for your help. I will review the invoice and make sure to send you the missing details later tonight. |
| ar_en_SA_003 | ar-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نصًا محسنًا وأكثر لطفًا ووضوحًا: "Thank you very much for your help. I will carefully review the invoice and make sure to send you the missing details by tonight."... |
| ar_en_SA_003 | ar-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة أكثر لطفًا ووضوحًا من النص: "شكراً جزيلاً على مساعدتك. سأقوم بمراجعة الفاتورة وإرسال التفاصيل الناقصة الليلة إن شاء الله." |
| ar_en_SA_004 | ar-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة محسّنة وأكثر لطفاً من النص: "I’m sorry I won’t be able to join the call today, but I’d be happy to share my update by email instead." أو إذا أردت أن تكون أكثر... |
| ar_en_SA_004 | ar-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نصًا محسنًا وأكثر لطفًا ووضوحًا: "أعتذر لعدم تمكني من الانضمام إلى المكالمة اليوم، لكنني سأشارك تحديثي عبر البريد الإلكتروني. شكراً لتفهمكم." |
| ar_en_SA_004 | ar-en | Editing preservation | gpt-4.1-mini | contract | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نصًا محسنًا وأكثر لطفًا: "Unfortunately, I won’t be able to join the call today, but I’d be happy to share my update via email." |
| ar_en_SA_004 | ar-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة أكثر لطفًا ووضوحًا من النص: "عذرًا، لن أتمكن من الانضمام إلى المكالمة اليوم، لكنني سأرسل لك تحديثي عبر البريد الإلكتروني. شكرًا لتفهمك!" |
| ar_en_SA_004 | ar-en | Editing preservation | gpt-4.1-nano | contract | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة أكثر لطفًا ووضوحًا من النص: "I won't be able to join the call today, but I’d be happy to share my update via email. Thank you for understanding." |
| ar_en_SA_005 | ar-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! يمكنك إعادة صياغة الجملة لتكون أكثر وضوحًا ولطفًا على النحو التالي: "The first paragraph is a bit lengthy, and the final sentence could be phrased more politely." أو إذا... |
| ar_en_SA_005 | ar-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نصًا محسنًا وأكثر لطفًا ووضوحًا: "الفقرة الأولى طويلة بعض الشيء، وقد يكون من الأفضل تقسيمها لتسهيل القراءة. كما أن الجملة الأخيرة قد تُفهم على أنها حادة قليلاً، فهل... |
| ar_en_SA_005 | ar-en | Editing preservation | gpt-4.1-mini | contract | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نصًا محسنًا وأكثر لطفًا: "The first paragraph feels a bit lengthy, and the final sentence could be softened to sound more polite." |
| ar_en_SA_005 | ar-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة محسنة من النص لتكون أكثر وضوحًا ولطفًا: "الفقرة الأولى طويلة بعض الشيء، وأعتقد أن الجملة الأخيرة قد تبدو غير لطيفة قليلاً. هل يمكننا تعديلها لجعلها أكثر لطفًا... |
| es_en_SA_001 | es-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language | ¡Por supuesto! Aquí tienes algunas opciones para que el mensaje suene más natural: 1. Hi team, I’ve finished the notes, but I’m not sure if the conclusion is clear. 2. Hi team,... |
| es_en_SA_001 | es-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural y fluida del texto: "Hi team, I’ve finished the notes, but I’m not sure if the conclusion is clear." Si quieres, también puedo ayudart... |
| es_en_SA_001 | es-en | Editing preservation | gpt-4.1-mini | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural: "Hi team, I’ve finished the notes, but I’m not sure if the conclusion is clear." |
| es_en_SA_001 | es-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural del texto: "Hi team, I’ve finished the notes, but I’m not sure if the conclusion is clear." ¿Quieres que sea aún más formal o informal? |
| es_en_SA_002 | es-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language | ¡Por supuesto! Aquí tienes algunas opciones para que suene más natural: 1. Hi, I need to reschedule my appointment because my train was delayed. 2. Hello, I’d like to change my... |
| es_en_SA_002 | es-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural y amable del texto: "Hello, I need to reschedule my appointment because my train was delayed." Si quieres que suene un poco más formal... |
| es_en_SA_002 | es-en | Editing preservation | gpt-4.1-mini | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural del texto: "Hello, I need to reschedule my appointment because my train was delayed." |
| es_en_SA_002 | es-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural del texto: "Hi, I need to reschedule my appointment because my train was delayed." |
| es_en_SA_002 | es-en | Editing preservation | gpt-4.1-nano | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural: "Hi, I need to reschedule my appointment because my train was delayed." |
| es_en_SA_003 | es-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language | ¡Por supuesto! Aquí tienes algunas opciones para que el texto suene más natural: 1. Thank you for your help. I’ll review the invoice and send you the missing details tonight. 2.... |
| es_en_SA_003 | es-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural y fluida del texto: "Thanks for your help! I’ll review the invoice and send you the missing details tonight." ¿Quieres que sea más for... |
| es_en_SA_003 | es-en | Editing preservation | gpt-4.1-mini | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural del texto: "Thanks for your help. I’ll review the invoice and send the missing details later tonight." |
| es_en_SA_003 | es-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural del texto: "Thanks for your help. I'll review the invoice and send the missing details tonight." ¿Quieres que sea aún más formal o inf... |
| es_en_SA_003 | es-en | Editing preservation | gpt-4.1-nano | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural del texto: "Thanks for your help. I'll review the invoice and send the missing details tonight." |
| es_en_SA_004 | es-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language | ¡Por supuesto! Aquí tienes algunas opciones para que suene más natural: 1. I won't be able to join the call today, but I can send my update by email. 2. I can't make it to the c... |
| es_en_SA_004 | es-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural y fluida: "I won’t be able to join the call today, but I can send you my update by email." ¿Quieres que sea más formal o más casual? |
| es_en_SA_004 | es-en | Editing preservation | gpt-4.1-mini | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural del texto: "I won’t be able to join the call today, but I can send you my update by email." |
| es_en_SA_004 | es-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural y fluida del texto: "No puedo unirme a la llamada hoy, pero puedo enviar mi actualización por correo." |
| es_en_SA_004 | es-en | Editing preservation | gpt-4.1-nano | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural: "No puedo unirme a la llamada hoy, pero puedo compartir mi actualización por correo." |
| es_en_SA_005 | es-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language | ¡Por supuesto! Aquí tienes una versión más natural del texto: "The first paragraph is a bit lengthy, and the last sentence comes across as somewhat harsh." Si necesitas que lo a... |
| es_en_SA_005 | es-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural y amable del texto: "The first paragraph is a bit too long, and the last sentence comes across as somewhat harsh." ¿Quieres que te ayu... |
| es_en_SA_005 | es-en | Editing preservation | gpt-4.1-mini | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural del texto: "The first paragraph is too long, and the last sentence comes across as a bit rude." |
| es_en_SA_005 | es-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural y suave del texto: "La primera oración es demasiado larga y la última frase suena un poco brusca." |
| es_en_SA_005 | es-en | Editing preservation | gpt-4.1-nano | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural y suave del texto: "The first paragraph is a bit too long, and the last sentence comes across as a little harsh." |
| ar_en_SC_001 | ar-en | Quote preservation | gpt-4.1-nano | baseline | 3 | preservation_failure;task_noncompletion | بالطبع، يرجى تزويدي بالنص الذي ترغب في تلخيصه. |
| ar_en_SC_001 | ar-en | Quote preservation | gpt-4.1-nano | contract | 1 | preservation_failure;task_noncompletion | الوثيقة تذكر "سياسة الإرجاع" قبل "طلب الاسترداد". |
| ar_en_SC_002 | ar-en | Quote preservation | gpt-4.1-nano | baseline | 3 | preservation_failure;task_noncompletion | بالطبع، يرجى تزويدي بالنص الذي ترغب في تلخيصه. |
| ar_en_SC_002 | ar-en | Quote preservation | gpt-4.1-nano | contract | 1 | preservation_failure;task_noncompletion | الوثيقة تتضمن مراجعة الميزانية قبل قسم "أسئلة المجتمع". |
| ar_en_SC_003 | ar-en | Quote preservation | gpt-4.1-nano | baseline | 3 | preservation_failure;task_noncompletion | بالطبع، يرجى تزويدي بالنص الذي ترغب في تلخيصه. |
| ar_en_SC_003 | ar-en | Quote preservation | gpt-4.1-nano | contract | 2 | preservation_failure;task_noncompletion | يقدم المستند إرشادات السلامة قبل ذكر "Emergency Contact". |
| ar_en_SC_004 | ar-en | Quote preservation | gpt-4.1-nano | baseline | 2 | preservation_failure;task_noncompletion | بالطبع، يرجى تزويدي بالنص الذي ترغب في تلخيصه. |
| ar_en_SC_004 | ar-en | Quote preservation | gpt-4.1-nano | contract | 3 | preservation_failure;task_noncompletion | يرجى تزويدي بالنص الذي ترغب في تلخيصه. |
| ar_en_SC_005 | ar-en | Quote preservation | gpt-4.1-nano | baseline | 3 | preservation_failure;task_noncompletion | بالطبع، يرجى تزويدي بالنص الذي ترغب في تلخيصه. |
| ar_en_SC_005 | ar-en | Quote preservation | gpt-4.1-nano | contract | 1 | preservation_failure;task_noncompletion | الوثيقة تتضمن متطلبات الدورة قبل الامتحان النهائي. |
| ar_en_SD_001 | ar-en | Script/register/locale | gpt-4.1-mini | baseline | 1 | preservation_failure;task_noncompletion | دفعت ٥٠٠ روبية، وسأرسل الإيصال غداً. |
| ar_en_SD_001 | ar-en | Script/register/locale | gpt-4.1-mini | contract | 1 | preservation_failure;task_noncompletion | دفعت ٥٠٠ روبية وسأرسل الإيصال غداً. |
| ar_en_SD_001 | ar-en | Script/register/locale | gpt-4.1-nano | baseline | 1 | preservation_failure;task_noncompletion | دفعت ٥٠٠ روبية، وببعتلك الإيصال بكرة. |
| ar_en_SD_001 | ar-en | Script/register/locale | gpt-4.1-nano | contract | 1 | preservation_failure;task_noncompletion | دفعت ٥٠٠ روبية، أرسل لك الإيصال بكرة إن شاء الله. |
| ar_en_SD_004 | ar-en | Script/register/locale | gpt-4.1-nano | baseline | 1 | preservation_failure;task_noncompletion | هل يمكن أن يُحتفظ بالطلب باسم ميرا راو تمامًا؟ |
| ar_en_SD_004 | ar-en | Script/register/locale | gpt-4.1-nano | contract | 1 | preservation_failure;task_noncompletion | هل يمكنكم حفظ الطلب باسم ميرا راو تماماً؟ |
| hi_en_SD_005 | hi-en | Script/register/locale | gpt-4.1-nano | baseline | 1 | wrong_output_language | The file name draft_v2.pdf should stay unchanged. |
