# Prompt-Ablation Diagnostic

This is a single-model diagnostic on `gpt-4.1-nano`, not a paper-facing
three-model claim. It compares the baseline, a generic-helpfulness prompt,
a narrow content-preservation prompt, and the full Global Interaction
Contract on the same 120-item stress pilot.

## Aggregate Metrics

| Condition | FTGA | Mean RTT | Token tax | Unresolved | Initial failures |
|---|---:|---:|---:|---:|---:|
| baseline | 67.5% | 0.47 | 1.69x | 5.8% | 39 |
| generic_helpfulness | 75.0% | 0.33 | 1.37x | 3.3% | 30 |
| content_preservation | 80.0% | 0.27 | 1.28x | 3.3% | 24 |
| contract | 76.7% | 0.33 | 1.34x | 4.2% | 28 |

## Paired Effects

| Comparison | FTGA delta | Improved / worsened / tied | Sign-test p | RTT reduction | Token-tax reduction | Unresolved reduction |
|---|---:|---:|---:|---:|---:|---:|
| generic_helpfulness_minus_baseline | +7.5 pp | 9 / 0 / 111 | 0.0039 | 0.14 | 0.32x | +2.5 pp |
| content_preservation_minus_baseline | +12.5 pp | 16 / 1 / 103 | 0.0003 | 0.20 | 0.41x | +2.5 pp |
| contract_minus_baseline | +9.2 pp | 12 / 1 / 107 | 0.0034 | 0.14 | 0.35x | +1.7 pp |
| content_preservation_minus_generic_helpfulness | +5.0 pp | 7 / 1 / 112 | 0.0703 | 0.06 | 0.09x | +0.0 pp |
| contract_minus_content_preservation | -3.3 pp | 3 / 7 / 110 | 0.3438 | -0.06 | -0.06x | -0.8 pp |

## Family Slice

| Task family | Baseline FTGA | Generic FTGA | Content-preservation FTGA | Full-contract FTGA |
|---|---:|---:|---:|---:|
| editing_preservation | 33.3% | 63.3% | 80.0% | 66.7% |
| output_language_inference | 100.0% | 100.0% | 100.0% | 100.0% |
| quote_preservation | 70.0% | 70.0% | 73.3% | 73.3% |
| script_register_locale | 66.7% | 66.7% | 66.7% | 66.7% |

## Content vs Full-Contract Transitions

| Task family | Both pass | Content only pass | Contract only pass | Both fail | Content lower RTT | Contract lower RTT | Same RTT |
|---|---:|---:|---:|---:|---:|---:|---:|
| editing_preservation | 20 | 4 | 0 | 6 | 4 | 1 | 25 |
| output_language_inference | 30 | 0 | 0 | 0 | 0 | 0 | 30 |
| quote_preservation | 21 | 1 | 1 | 7 | 3 | 1 | 26 |
| script_register_locale | 18 | 2 | 2 | 8 | 3 | 2 | 25 |

## Disagreement Examples

| Item | Family | Language | Transition | Content first response | Contract first response |
|---|---|---|---|---|---|
| ar_en_SA_004 | editing_preservation | ar-en | content_only_pass | Certainly! Here's a more clear and polite version of your message: "Unfortunately, I won't be able to join the call today, but I would be happy to share my update via email." | بالطبع! إليك نسخة أكثر لطفًا ووضوحًا من النص: "I won't be able to join the call today, but I’d be happy to share my update via email. Thank you for understanding." |
| es_en_SA_002 | editing_preservation | es-en | content_only_pass | Sure! Here's a more natural version: "Hi, I need to reschedule my appointment because my train was delayed." | Claro, aquí tienes una versión más natural: "Hi, I need to reschedule my appointment because my train was delayed." |
| es_en_SA_003 | editing_preservation | es-en | content_only_pass | Sure! Here's a more natural-sounding version: "Thanks for your help. I'll review the invoice and send the missing details tonight." | Claro, aquí tienes una versión más natural del texto: "Thanks for your help. I'll review the invoice and send the missing details tonight." |
| es_en_SA_009 | editing_preservation | es-en | content_only_pass | Sure! Here's a more natural-sounding version: "I need to ask my manager for an extra day to finish the slide deck." | Claro, aquí tienes una versión más natural: **"I need to ask my manager for an extra day to finish the slide deck."** |
| ar_en_SC_007 | quote_preservation | ar-en | contract_only_pass | الوثيقة تتضمن قائمة بـ"موعد الدفع" قبل "رسوم التأخير". | الوثيقة تذكر أولاً "Payment Deadline" ثم "Late Fee". |
| hi_en_SD_005 | script_register_locale | hi-en | contract_only_pass | The file name draft_v2.pdf should stay unchanged. | Theek hai, draft_v2.pdf file ka naam badalna nahi hai. |
| hi_en_SD_006 | script_register_locale | hi-en | contract_only_pass | Haan, please 10:30 AM pe move kar dein, appointment number INV-2048 same hi rahega. | Haan, INV-2048 ke appointment number ko badle bina, kya aap meri visit 10:30 AM par kar sakte hain? |
| es_en_SA_004 | editing_preservation | es-en | both_fail | Claro, aquí tienes una versión más natural: "No puedo unirme a la llamada hoy, pero puedo compartir mi actualización por correo." | Claro, aquí tienes una versión más natural: "No puedo unirme a la llamada hoy, pero puedo compartir mi actualización por correo." |
| es_en_SA_005 | editing_preservation | es-en | both_fail | Claro, aquí tienes una versión más natural y suave del texto: "The first paragraph is a bit too long, and the last sentence comes across as a little harsh." | Claro, aquí tienes una versión más natural y suave del texto: "The first paragraph is a bit too long, and the last sentence comes across as a little harsh." |
| es_en_SA_006 | editing_preservation | es-en | both_fail | Claro, aquí tienes una versión más natural: "I reviewed the report, and the second chart might be confusing for new readers." | Claro, aquí tienes una versión más natural y fluida: "Revisé el informe, y el segundo gráfico parece un poco confuso para quienes lo leen por primera vez." |
| es_en_SA_007 | editing_preservation | es-en | both_fail | ¿Podrías decirle al cliente que el pago llegará la próxima semana? | Claro, aquí tienes una versión más natural: "Could you let the client know that the payment will arrive next week?" |

## Interpretation

The narrow content-preservation prompt reaches 80.0% FTGA,
above the full contract's 76.7% on this nano diagnostic.
Relative to baseline, content preservation adds +12.5 pp
FTGA and lowers token tax. The full contract trails content preservation by
-3.3 pp FTGA on the same items.

This should be reported as mechanism evidence and a claim boundary: the
main three-model result still uses the pre-registered Global Interaction
Contract, but the best nano prompt tested in this diagnostic is the
narrower content-preservation scaffold. The result suggests that content
language and literal-preservation rules drive much of the mitigation.

