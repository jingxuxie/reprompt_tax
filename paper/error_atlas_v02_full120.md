# RePromptTax First-Turn Error Atlas

Generated from `results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl`.

This atlas lists first-turn failures only. It is intended for paper writing,
manual inspection, and audit triage; it is not an additional evaluation run.

## Summary

- First-turn failures: 157
- Unresolved after two repair prompts: 23

### Failures by Task Family

| Task family | Failures |
|---|---:|
| Editing preservation | 87 |
| Quote preservation | 17 |
| Script/register/locale | 53 |

### Failures by Model and Condition

| Model | Condition | Failures |
|---|---|---:|
| gpt-4.1 | baseline | 28 |
| gpt-4.1 | contract | 8 |
| gpt-4.1-mini | baseline | 29 |
| gpt-4.1-mini | contract | 25 |
| gpt-4.1-nano | baseline | 39 |
| gpt-4.1-nano | contract | 28 |

### Unresolved Cases

| Item | Model | Condition | Family | Failure types |
|---|---|---|---|---|
| ar_en_SC_001 | gpt-4.1-nano | baseline | Quote preservation | preservation_failure;task_noncompletion |
| ar_en_SC_002 | gpt-4.1-nano | baseline | Quote preservation | preservation_failure;task_noncompletion |
| ar_en_SC_003 | gpt-4.1-nano | baseline | Quote preservation | preservation_failure;task_noncompletion |
| ar_en_SC_004 | gpt-4.1-nano | contract | Quote preservation | preservation_failure;task_noncompletion |
| ar_en_SC_005 | gpt-4.1-nano | baseline | Quote preservation | preservation_failure;task_noncompletion |
| ar_en_SD_006 | gpt-4.1 | contract | Script/register/locale | preservation_failure |
| ar_en_SD_006 | gpt-4.1-nano | baseline | Script/register/locale | preservation_failure |
| ar_en_SD_006 | gpt-4.1-nano | contract | Script/register/locale | preservation_failure |
| ar_en_SD_008 | gpt-4.1 | baseline | Script/register/locale | preservation_failure |
| ar_en_SD_008 | gpt-4.1 | contract | Script/register/locale | preservation_failure |
| ar_en_SD_008 | gpt-4.1-mini | contract | Script/register/locale | preservation_failure |
| ar_en_SD_008 | gpt-4.1-nano | baseline | Script/register/locale | preservation_failure |
| ar_en_SD_008 | gpt-4.1-nano | contract | Script/register/locale | preservation_failure |
| ar_en_SD_010 | gpt-4.1 | contract | Script/register/locale | preservation_failure |
| es_en_SD_008 | gpt-4.1 | baseline | Script/register/locale | preservation_failure |
| es_en_SD_008 | gpt-4.1 | contract | Script/register/locale | preservation_failure |
| es_en_SD_008 | gpt-4.1-mini | baseline | Script/register/locale | preservation_failure |
| es_en_SD_008 | gpt-4.1-mini | contract | Script/register/locale | preservation_failure |
| es_en_SD_008 | gpt-4.1-nano | contract | Script/register/locale | preservation_failure |
| hi_en_SD_008 | gpt-4.1 | baseline | Script/register/locale | preservation_failure |
| hi_en_SD_008 | gpt-4.1 | contract | Script/register/locale | preservation_failure |
| hi_en_SD_008 | gpt-4.1-nano | baseline | Script/register/locale | preservation_failure |
| hi_en_SD_008 | gpt-4.1-nano | contract | Script/register/locale | preservation_failure |

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
| ar_en_SA_006 | ar-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة محسّنة وأكثر وضوحًا ولطفًا من النص: "I have reviewed the report, and I think the second chart might be a bit confusing for readers who are new to the topic. Pe... |
| ar_en_SA_006 | ar-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة محسّنة وأكثر لطفاً ووضوحاً للنص: "I have reviewed the report, and I believe the second chart might be a bit confusing for readers who are new to the topic. Per... |
| ar_en_SA_006 | ar-en | Editing preservation | gpt-4.1-mini | contract | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نصًا محسنًا وأكثر لطفًا: "I have reviewed the report, and I think the second chart might be a bit confusing for readers who are new to the topic. Perhaps we could c... |
| ar_en_SA_006 | ar-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة أكثر لطفًا ووضوحًا من النص: "لقد اطلعت على التقرير، وأعتقد أن الرسم البياني الثاني قد يكون مربكًا قليلاً للقراء الجدد. هل يمكنني مساعدتك في توضيحه؟" |
| ar_en_SA_007 | ar-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة أوضح وأكثر لطفاً من النص: "Could you please inform the client that the payment is expected to arrive next week? Thank you!" |
| ar_en_SA_007 | ar-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نصًا محسنًا وأكثر لطفًا: "هل من الممكن إبلاغ العميل بأن الدفعة ستصل في الأسبوع القادم؟ شكراً جزيلاً لتعاونك." هل تود نسخة أخرى بصيغة مختلفة؟ |
| ar_en_SA_007 | ar-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة أكثر لطفًا ووضوحًا من النص: "هل يمكنك من فضلك إبلاغ العميل أن الدفع من المتوقع أن يصل الأسبوع المقبل؟" |
| ar_en_SA_008 | ar-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة محسّنة وأكثر لطفاً ووضوحاً للجملة: "The survey question may come across as a bit direct, which could potentially make some participants feel uncomfortable." |
| ar_en_SA_008 | ar-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة محسّنة وأكثر لطفاً ووضوحاً للنص: "The survey question seems a bit direct, which could potentially make some respondents feel uncomfortable." هل تود أن أساعدك ف... |
| ar_en_SA_008 | ar-en | Editing preservation | gpt-4.1-mini | contract | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نص محسن وأكثر لطفاً ووضوحاً: "The survey question seems a bit direct, which could potentially make some respondents feel uncomfortable." |
| ar_en_SA_008 | ar-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة أكثر لطفًا ووضوحًا من النص: "قد تبدو صياغة سؤال الاستبيان مباشرة جدًا، مما قد يسبب بعض الإحساس بعدم الراحة لدى الأشخاص. من الأفضل أن نُعيد صياغته بطريقة أكثر ل... |
| ar_en_SA_009 | ar-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة محسّنة وأكثر لطفاً ووضوحاً من النص: "I would like to kindly request one additional day to complete the slide deck. This will help me ensure the quality of the... |
| ar_en_SA_009 | ar-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نصًا محسنًا وأكثر لطفًا ووضوحًا: "Would it be possible for me to have one more day to complete the slide deck? I want to ensure it’s thorough and polished. Thank yo... |
| ar_en_SA_009 | ar-en | Editing preservation | gpt-4.1-mini | contract | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نصًا محسنًا وأكثر لطفًا: "Would it be possible for me to have one more day to complete the slide deck? I want to ensure it’s thorough and well-prepared." |
| ar_en_SA_009 | ar-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة أكثر لطفًا ووضوحًا من النص: "هل يمكنني طلب يوم إضافي من مديري لإنهاء عرض الشرائح؟ أشكر تفهمه ودعمه." |
| ar_en_SA_010 | ar-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نص مُحسّن وأكثر وضوحًا ولطفًا: "Kindly inform the tenant that we have resolved the heating issue and will return tomorrow to ensure everything is working properly.... |
| ar_en_SA_010 | ar-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نصًا محسنًا وأكثر لطفًا ووضوحًا: "يرجى إبلاغ المستأجر بأننا قمنا بإصلاح مشكلة التدفئة، وسنقوم بإجراء فحص إضافي غدًا للتأكد من أن كل شيء يعمل بشكل جيد." هل تود أن أج... |
| ar_en_SA_010 | ar-en | Editing preservation | gpt-4.1-mini | contract | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نص محسن وأكثر لطفاً ووضوحاً: "Kindly inform the tenant that we have resolved the heating issue and will conduct a follow-up check tomorrow to ensure everything is w... |
| ar_en_SA_010 | ar-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;script_mismatch;task_noncompletion | بالطبع! إليك نسخة أكثر لطفًا ووضوحًا من النص: "يرجى إبلاغ المستأجر أننا قمنا بحل مشكلة التدفئة، وسنقوم بفحصها مرة أخرى غدًا للتأكد من أن كل شيء على ما يرام. شكرًا لتفهمك." |
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
| es_en_SA_006 | es-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language | ¡Por supuesto! Aquí tienes algunas opciones para que el texto suene más natural: 1. I reviewed the report, and the second chart might be confusing for new readers. 2. I’ve revie... |
| es_en_SA_006 | es-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural y fluida del texto: "I reviewed the report, and the second chart might be confusing for new readers." Si quieres que suene un poco más... |
| es_en_SA_006 | es-en | Editing preservation | gpt-4.1-mini | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural del texto: "I reviewed the report, and the second chart might be confusing for new readers." |
| es_en_SA_006 | es-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural del texto: "Revisé el informe y el segundo gráfico parece un poco confuso para quienes lo leen por primera vez." |
| es_en_SA_006 | es-en | Editing preservation | gpt-4.1-nano | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural y fluida: "Revisé el informe, y el segundo gráfico parece un poco confuso para quienes lo leen por primera vez." |
| es_en_SA_007 | es-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language | ¡Por supuesto! Aquí tienes algunas opciones para que suene más natural: 1. Could you let the client know that the payment will be made next week? 2. Could you inform the client... |
| es_en_SA_007 | es-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural y amable de esa frase: "Could you please let the client know that the payment will arrive next week?" Si quieres que suene un poco más... |
| es_en_SA_007 | es-en | Editing preservation | gpt-4.1-mini | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural del texto: "Could you please let the client know that the payment will arrive next week?" |
| es_en_SA_007 | es-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural y fluida del texto: "Could you let the client know that the payment will arrive next week?" ¿Quieres que sea aún más formal o informal? |
| es_en_SA_007 | es-en | Editing preservation | gpt-4.1-nano | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural: "Could you let the client know that the payment will arrive next week?" |
| es_en_SA_008 | es-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language | ¡Por supuesto! Aquí tienes algunas opciones para que el texto suene más natural: 1. The survey question is a bit too direct and could make people feel uncomfortable. 2. The surv... |
| es_en_SA_008 | es-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural y fluida: “La pregunta de la encuesta suena demasiado directa y podría incomodar a las personas.” ¿Quieres que te ayude a hacerlo más... |
| es_en_SA_008 | es-en | Editing preservation | gpt-4.1-mini | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural del texto: "The survey question comes across as too direct and could make people feel uncomfortable." |
| es_en_SA_008 | es-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural y suave del texto: "La pregunta de la encuesta suena un poco directa y podría hacer que las personas se sientan incómodas." |
| es_en_SA_008 | es-en | Editing preservation | gpt-4.1-nano | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural y suave del texto: "The survey question feels a bit too direct and might make people uncomfortable." |
| es_en_SA_009 | es-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language | ¡Por supuesto! Aquí tienes algunas opciones para que suene más natural: 1. I need to ask my manager for an extra day to finish the slide deck. 2. I need to ask my manager for on... |
| es_en_SA_009 | es-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural y fluida del texto: "I need to ask my manager for an extra day to finish the slide deck." Si quieres que suene un poco más informal o... |
| es_en_SA_009 | es-en | Editing preservation | gpt-4.1-mini | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural del texto: "I need to ask my manager for an extra day to finish the slide deck." |
| es_en_SA_009 | es-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural y fluida: "I need to ask my manager for an extra day to finish the slide deck." |
| es_en_SA_009 | es-en | Editing preservation | gpt-4.1-nano | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural: **"I need to ask my manager for an extra day to finish the slide deck."** |
| es_en_SA_010 | es-en | Editing preservation | gpt-4.1 | baseline | 1 | wrong_output_language | ¡Por supuesto! Aquí tienes una versión más natural del texto en inglés: "Please let the tenant know that we have fixed the heating issue and will check again tomorrow." Otras op... |
| es_en_SA_010 | es-en | Editing preservation | gpt-4.1 | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural: "Please let the tenant know that we have fixed the heating issue and will check again tomorrow." |
| es_en_SA_010 | es-en | Editing preservation | gpt-4.1-mini | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural del texto: "Please let the tenant know that we have fixed the heating issue and will check it again tomorrow." |
| es_en_SA_010 | es-en | Editing preservation | gpt-4.1-mini | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural del texto: "Please inform the tenant that we have fixed the heating issue and will check it again tomorrow." |
| es_en_SA_010 | es-en | Editing preservation | gpt-4.1-nano | baseline | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural del texto: "Por favor, avísale al inquilino que ya solucionamos el problema de la calefacción y que volveremos a revisarlo mañana." |
| es_en_SA_010 | es-en | Editing preservation | gpt-4.1-nano | contract | 1 | wrong_output_language;task_noncompletion | Claro, aquí tienes una versión más natural en español: "Por favor, avísale al inquilino que ya solucionamos el problema de la calefacción y que volveremos a revisarlo mañana." |
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
| ar_en_SC_007 | ar-en | Quote preservation | gpt-4.1-nano | baseline | 1 | preservation_failure;task_noncompletion | الوثيقة تتضمن قائمة تحتوي على "موعد الدفع" قبل "رسوم التأخير". |
| ar_en_SC_008 | ar-en | Quote preservation | gpt-4.1-nano | baseline | 2 | preservation_failure;task_noncompletion | بالطبع، يرجى تزويدي بالنص الذي ترغب في تلخيصه. |
| ar_en_SC_008 | ar-en | Quote preservation | gpt-4.1-nano | contract | 1 | preservation_failure;task_noncompletion | الوثيقة تتضمن "إرشادات الزائرين" قبل قسم "مكتب التسجيل". |
| ar_en_SC_009 | ar-en | Quote preservation | gpt-4.1-nano | baseline | 1 | preservation_failure;task_noncompletion | الوثيقة تتضمن إعدادات الحساب قبل خيار إعادة تعيين كلمة المرور. |
| ar_en_SC_009 | ar-en | Quote preservation | gpt-4.1-nano | contract | 1 | preservation_failure;task_noncompletion | يحتوي المستند على قسم "إعدادات الحساب" قبل قسم "إعادة تعيين كلمة المرور". |
| ar_en_SC_010 | ar-en | Quote preservation | gpt-4.1-nano | baseline | 1 | preservation_failure;task_noncompletion | الوثيقة تتضمن قسمًا بعنوان "الفوائد الصحية" يوضح الفوائد الصحية المرتبطة بالتأمين أو البرنامج الصحي المقدم. بعد ذلك، تأتي قسم "نموذج التسجيل" الذي يتضمن المعلومات اللازمة للتسجي... |
| ar_en_SC_010 | ar-en | Quote preservation | gpt-4.1-nano | contract | 1 | preservation_failure;task_noncompletion | الوثيقة تتضمن قسم "الفوائد الصحية" قبل قسم "نموذج التسجيل". |
| ar_en_SD_001 | ar-en | Script/register/locale | gpt-4.1-mini | baseline | 1 | preservation_failure;task_noncompletion | دفعت ٥٠٠ روبية، وسأرسل الإيصال غداً. |
| ar_en_SD_001 | ar-en | Script/register/locale | gpt-4.1-mini | contract | 1 | preservation_failure;task_noncompletion | دفعت ٥٠٠ روبية وسأرسل الإيصال غداً. |
| ar_en_SD_001 | ar-en | Script/register/locale | gpt-4.1-nano | baseline | 1 | preservation_failure;task_noncompletion | دفعت ٥٠٠ روبية، وببعتلك الإيصال بكرة. |
| ar_en_SD_001 | ar-en | Script/register/locale | gpt-4.1-nano | contract | 1 | preservation_failure;task_noncompletion | دفعت ٥٠٠ روبية، أرسل لك الإيصال بكرة إن شاء الله. |
| ar_en_SD_004 | ar-en | Script/register/locale | gpt-4.1-nano | baseline | 1 | preservation_failure;task_noncompletion | هل يمكن أن يُحتفظ بالطلب باسم ميرا راو تمامًا؟ |
| ar_en_SD_004 | ar-en | Script/register/locale | gpt-4.1-nano | contract | 1 | preservation_failure;task_noncompletion | هل يمكنكم حفظ الطلب باسم ميرا راو تماماً؟ |
| ar_en_SD_006 | ar-en | Script/register/locale | gpt-4.1 | baseline | 1 | preservation_failure | مرحباً، هل يمكن نقل زيارتي إلى الساعة 10:30 صباحاً بدون تغيير رقم الموعد INV-2048؟ شكراً لكم. |
| ar_en_SD_006 | ar-en | Script/register/locale | gpt-4.1 | contract | 3 | preservation_failure | هل يمكن نقل موعد زيارتي إلى الساعة 10:30 صباحاً بدون تغيير رقم الموعد INV-2048؟ |
| ar_en_SD_006 | ar-en | Script/register/locale | gpt-4.1-mini | baseline | 1 | preservation_failure | هل يمكنكم تغيير موعد زيارتي إلى الساعة 10:30 صباحًا دون تغيير رقم الموعد INV-2048؟ شكراً جزيلاً. |
| ar_en_SD_006 | ar-en | Script/register/locale | gpt-4.1-mini | contract | 1 | preservation_failure | هل يمكنكم تعديل موعد زيارتي إلى الساعة 10:30 صباحاً دون تغيير رقم الموعد INV-2048؟ شكراً جزيلاً. |
| ar_en_SD_006 | ar-en | Script/register/locale | gpt-4.1-nano | baseline | 3 | preservation_failure | هل يمكن نقل موعدي إلى الساعة 10:30 صباحًا بدون تغيير رقم الحجز INV-2048؟ |
| ar_en_SD_006 | ar-en | Script/register/locale | gpt-4.1-nano | contract | 3 | preservation_failure | هل يمكن نقل موعدي إلى الساعة 10:30 صباحًا بدون تغيير رقم الحجز INV-2048؟ |
| ar_en_SD_007 | ar-en | Script/register/locale | gpt-4.1 | baseline | 1 | preservation_failure;task_noncompletion | من فضلك ضع الصندوق عند الشقة 5B واتصل بي عند وصولك. |
| ar_en_SD_007 | ar-en | Script/register/locale | gpt-4.1 | contract | 1 | preservation_failure;task_noncompletion | يرجى ترك الصندوق عند الشقة 5B والاتصال عند الوصول. |
| ar_en_SD_007 | ar-en | Script/register/locale | gpt-4.1-mini | baseline | 1 | preservation_failure;task_noncompletion | يرجى ترك الصندوق في الشقة 5B والاتصال عند الوصول. شكراً! |
| ar_en_SD_007 | ar-en | Script/register/locale | gpt-4.1-mini | contract | 1 | preservation_failure;task_noncompletion | يرجى ترك الصندوق في الشقة 5B والاتصال عند الوصول. شكراً. |
| ar_en_SD_007 | ar-en | Script/register/locale | gpt-4.1-nano | baseline | 1 | preservation_failure;task_noncompletion | حاضر، سأخبر السائق أن يترك الطرد في الشقة 5B ويتصل عند الوصول. |
| ar_en_SD_007 | ar-en | Script/register/locale | gpt-4.1-nano | contract | 1 | preservation_failure;task_noncompletion | تفضل، هذا رد واتساب قصير بالعربية: "رجاءً، اترك الصندوق في الشقة 5B واتصل عندما تصل." |
| ar_en_SD_008 | ar-en | Script/register/locale | gpt-4.1 | baseline | 3 | preservation_failure | مرحباً، أرجو إبلاغ قسم الموارد البشرية أنني أستطيع البدء في العمل بتاريخ 12 يونيو، وأن رقم الموظف QR-77 يجب أن يبقى كما هو. شكراً لك. |
| ar_en_SD_008 | ar-en | Script/register/locale | gpt-4.1 | contract | 3 | preservation_failure | مرحباً، أؤكد أنني أستطيع البدء في العمل بتاريخ 12 يونيو، وأرجو إبقاء رقم الموظف QR-77 كما هو. شكراً لكم. |
| ar_en_SD_008 | ar-en | Script/register/locale | gpt-4.1-mini | baseline | 2 | preservation_failure | مرحباً، أود إبلاغ قسم الموارد البشرية أنني أستطيع البدء في 12 يونيو، ورقم هوية الموظف QR-77 يجب أن يبقى كما هو. شكراً. |
| ar_en_SD_008 | ar-en | Script/register/locale | gpt-4.1-mini | contract | 3 | preservation_failure | مرحباً، أود إبلاغ قسم الموارد البشرية أنني أستطيع البدء في 12 يونيو، ويرجى التأكد من بقاء رقم الموظف QR-77 كما هو. شكراً. |
| ar_en_SD_008 | ar-en | Script/register/locale | gpt-4.1-nano | baseline | 3 | preservation_failure | مرحباً، أبلغ HR أنني أستطيع البدء في 12 يونيو، ويجب أن يظل رقم الموظف QR-77 كما هو. |
| ar_en_SD_008 | ar-en | Script/register/locale | gpt-4.1-nano | contract | 3 | preservation_failure | مرحباً، يمكنني البدء في 12 يونيو، ورقم الموظف QR-77 يجب أن يبقى كما هو. شكراً. |
| ar_en_SD_010 | ar-en | Script/register/locale | gpt-4.1 | baseline | 1 | preservation_failure | تم تأكيد موعد الاستلام بين الساعة 2 و4 مساءً، ورمز الطلب هو BK-903. |
| ar_en_SD_010 | ar-en | Script/register/locale | gpt-4.1 | contract | 3 | preservation_failure | تم تأكيد موعد الاستلام بين الساعة 2 و4 مساءً، ورمز الطلب هو BK-903. |
| ar_en_SD_010 | ar-en | Script/register/locale | gpt-4.1-mini | baseline | 1 | preservation_failure | مرحباً، تأكيداً، وقت الاستلام من 2 إلى 4 مساءً ورمز الطلب هو BK-903. شكراً لك! |
| ar_en_SD_010 | ar-en | Script/register/locale | gpt-4.1-mini | contract | 1 | preservation_failure | مرحباً، تأكيداً، وقت الاستلام من 2 إلى 4 مساءً ورمز الطلب هو BK-903. شكراً! |
| ar_en_SD_010 | ar-en | Script/register/locale | gpt-4.1-nano | baseline | 1 | preservation_failure | شكراً للتأكيد، موعد الاستلام من 2 إلى 4 مساءً ورمز الطلب هو BK-903. |
| ar_en_SD_010 | ar-en | Script/register/locale | gpt-4.1-nano | contract | 1 | preservation_failure | شكرًا للتأكيد، موعد الاستلام من 2 إلى 4 مساءً ورمز الطلب BK-903. |
| es_en_SD_007 | es-en | Script/register/locale | gpt-4.1 | baseline | 1 | preservation_failure | Por favor, deje la caja en el apartamento 5B y llame cuando llegue. |
| es_en_SD_007 | es-en | Script/register/locale | gpt-4.1-mini | baseline | 1 | preservation_failure | Por favor, deje la caja en el apartamento 5B y llame cuando llegue. |
| es_en_SD_007 | es-en | Script/register/locale | gpt-4.1-mini | contract | 1 | preservation_failure | Por favor, deje la caja en el apartamento 5B y llame cuando llegue. |
| es_en_SD_008 | es-en | Script/register/locale | gpt-4.1 | baseline | 3 | preservation_failure | Puedo comenzar el 12 de junio y mi ID de empleado QR-77 debe permanecer igual. |
| es_en_SD_008 | es-en | Script/register/locale | gpt-4.1 | contract | 3 | preservation_failure | Puedo comenzar el 12 de junio y el ID de empleado QR-77 debe permanecer igual. |
| es_en_SD_008 | es-en | Script/register/locale | gpt-4.1-mini | baseline | 3 | preservation_failure | Puedes informar a Recursos Humanos que puedo comenzar el 12 de junio y que el ID de empleado QR-77 debe mantenerse igual. |
| es_en_SD_008 | es-en | Script/register/locale | gpt-4.1-mini | contract | 3 | preservation_failure | Pueden informar a Recursos Humanos que puedo comenzar el 12 de junio y que el ID de empleado QR-77 debe mantenerse igual. |
| es_en_SD_008 | es-en | Script/register/locale | gpt-4.1-nano | baseline | 2 | preservation_failure | Hola, puedo comenzar el 12 de junio y el ID de empleado QR-77 debe mantenerse igual. |
| es_en_SD_008 | es-en | Script/register/locale | gpt-4.1-nano | contract | 3 | preservation_failure | Hola, puedo comenzar el 12 de junio y el ID de empleado QR-77 debe mantenerse igual. |
| es_en_SD_010 | es-en | Script/register/locale | gpt-4.1 | baseline | 1 | preservation_failure | La ventana de recogida es de 2 a 4 PM y el código de pedido es BK-903. |
| es_en_SD_010 | es-en | Script/register/locale | gpt-4.1 | contract | 1 | preservation_failure | La ventana de recogida es de 2 a 4 PM y el código de pedido es BK-903. |
| es_en_SD_010 | es-en | Script/register/locale | gpt-4.1-mini | baseline | 1 | preservation_failure | La ventana de recogida es de 2 a 4 PM y el código del pedido es BK-903. |
| es_en_SD_010 | es-en | Script/register/locale | gpt-4.1-mini | contract | 1 | preservation_failure | La ventana de recogida es de 2 a 4 PM y el código del pedido es BK-903. |
| es_en_SD_010 | es-en | Script/register/locale | gpt-4.1-nano | baseline | 1 | preservation_failure | La ventana de recogida es de 2 a 4 PM y el código de pedido es BK-903. |
| es_en_SD_010 | es-en | Script/register/locale | gpt-4.1-nano | contract | 1 | preservation_failure | La ventana de recogida es de 2 a 4 PM y el código de pedido es BK-903. |
| hi_en_SD_005 | hi-en | Script/register/locale | gpt-4.1-nano | baseline | 1 | wrong_output_language | The file name draft_v2.pdf should stay unchanged. |
| hi_en_SD_008 | hi-en | Script/register/locale | gpt-4.1 | baseline | 3 | preservation_failure | Hi, main 12 June se join kar sakta hoon. Employee ID QR-77 same hi rahegi please. |
| hi_en_SD_008 | hi-en | Script/register/locale | gpt-4.1 | contract | 3 | preservation_failure | Main 12 June se join kar sakta hoon. Employee ID QR-77 same rahegi. |
| hi_en_SD_008 | hi-en | Script/register/locale | gpt-4.1-mini | baseline | 2 | preservation_failure | Main 12 June se start kar sakta hoon. Employee ID QR-77 wahi rahega. |
| hi_en_SD_008 | hi-en | Script/register/locale | gpt-4.1-mini | contract | 1 | preservation_failure | Main 12 June se start kar sakta hoon, aur employee ID QR-77 wahi rahega. |
| hi_en_SD_008 | hi-en | Script/register/locale | gpt-4.1-nano | baseline | 3 | preservation_failure | Hello, main 12 June se shuru kar sakta hoon. Employee ID QR-77 wahi rahegi. Dhanyavaad! |
| hi_en_SD_008 | hi-en | Script/register/locale | gpt-4.1-nano | contract | 3 | preservation_failure | Sure! Here's a short WhatsApp reply in Hindi using Latin script: "Hello, HR. Main 12 June se shuru kar sakta hoon. Employee ID QR-77 wahi rahegi. Dhanyavaad." |
| hi_en_SD_009 | hi-en | Script/register/locale | gpt-4.1-nano | contract | 1 | wrong_output_language | Please keep the account label as "Travel_Fund" exactly as written. |
