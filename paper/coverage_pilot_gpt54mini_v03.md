# GPT-5.4-mini v0.3 Coverage Pilot

This 24-item pilot uses four rows from each synthetic v0.3 coverage-expansion slice.
It reuses the six saved smoke rows and adds 18 new rows; it is not paper-facing model result evidence.
The v0.3 scaffold still requires native validation before claims.

## Summary

| Condition | n | FTGA | Mean RTT | Unresolved | Repair@2 | Mean token tax | Initially failed |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline | 24 | 75.0% | 0.417 | 8.3% | 66.7% | 1.579 | 6 |
| contract | 24 | 95.8% | 0.125 | 4.2% | 0.0% | 1.104 | 1 |

Paired FTGA movement: 5 improved, 0 worsened, 19 tied out of 24 items.
Saved API rows: 58 (8007 input tokens, 1958 output tokens).

## By Coverage Slice

| Slice | Condition | n | FTGA | Mean RTT | Initially failed |
|---|---|---:|---:|---:|---:|
| arabic_instruction_arabic_filenames | baseline | 4 | 100.0% | 0.000 | 0 |
| arabic_instruction_arabic_filenames | contract | 4 | 100.0% | 0.000 | 0 |
| english_instruction_arabic_content | baseline | 4 | 75.0% | 0.750 | 1 |
| english_instruction_arabic_content | contract | 4 | 75.0% | 0.750 | 1 |
| english_instruction_hindi_content | baseline | 4 | 75.0% | 0.750 | 1 |
| english_instruction_hindi_content | contract | 4 | 100.0% | 0.000 | 0 |
| english_instruction_spanish_content | baseline | 4 | 100.0% | 0.000 | 0 |
| english_instruction_spanish_content | contract | 4 | 100.0% | 0.000 | 0 |
| hindi_english_instruction_hindi_devanagari | baseline | 4 | 100.0% | 0.000 | 0 |
| hindi_english_instruction_hindi_devanagari | contract | 4 | 100.0% | 0.000 | 0 |
| spanish_instruction_arabic_quote | baseline | 4 | 0.0% | 1.000 | 4 |
| spanish_instruction_arabic_quote | contract | 4 | 100.0% | 0.000 | 0 |

## First-Turn Failures

| Item | Slice | Condition | Failure types | Snippet |
|---|---|---|---|---|
| v03_en_hi_EP_002 | english_instruction_hindi_content | baseline | preservation_failure | पुस्तकालय सोमवार को जल्दी खुलेगा, क्योंकि अध्ययन सत्र आयोजित किया गया है। |
| v03_en_ar_EP_004 | english_instruction_arabic_content | baseline | preservation_failure | تقدّم الصف في المشروع، لكن الملخّص النهائي يحتاج إلى أمثلة إضافية. |
| v03_en_ar_EP_004 | english_instruction_arabic_content | contract | preservation_failure | تقدّم الصف في المشروع، لكن الملخّص النهائي يحتاج إلى أمثلة. |
| v03_es_ar_EP_001 | spanish_instruction_arabic_quote | baseline | task_noncompletion | Claro. Una versión más pulida en árabe, sin traducirla ni cambiar los términos clave, sería:  **أنهى الفريق المسودة، لكن الخاتمة تحتاج إلى مزيد من التوضيح قبل الإرسال.**  Si quieres, también puedo darte 2–3 variantes con |
| v03_es_ar_EP_002 | spanish_instruction_arabic_quote | baseline | task_noncompletion | Claro. Una versión más pulida en árabe, sin cambiar los términos clave, sería:  **ستفتح المكتبة مبكرًا يوم الاثنين لأن جلسة القراءة ستبدأ صباحًا.**  Si quieres, también puedo darte una versión **más formal** o **más lite |
| v03_es_ar_EP_003 | spanish_instruction_arabic_quote | baseline | task_noncompletion | Claro. Una versión más pulida en árabe, sin cambiar los términos clave, sería:  **وافق العميل على التصميم، لكنه طلب تعديلات على الغلاف.**  Si quieres, también puedo darte 2–3 variantes con un tono más formal o más natura |
| v03_es_ar_EP_004 | spanish_instruction_arabic_quote | baseline | task_noncompletion | Claro. Una versión más fluida en árabe, sin traducirla ni cambiar sus términos clave, sería:  **"تقدّم الصف في المشروع، لكن الملخص النهائي يحتاج إلى أمثلة."**  Si quieres, también puedo darte **2–3 variantes más formales |

## Claim Boundary

- Treat this as a 24-item synthetic v0.3 pilot, not as a headline benchmark result.
- Do not merge it into the v0.2 paper-facing tables.
- Do not report v0.3 performance claims until native validation is complete.
