# gpt-5.4-mini v0.3 Coverage Smoke

This six-item smoke uses one row from each synthetic v0.3 coverage-expansion slice.
It is not paper-facing model result evidence and requires native validation before claims.
The purpose is to verify that non-English target-content rows are runnable, scoreable, and worth a bounded follow-up.

## Summary

| Metric | Value |
|---|---:|
| model | gpt-5.4-mini |
| items | 6 |
| trajectories | 12 |
| api_response_rows | 13 |
| baseline_ftga | 83.3% |
| contract_ftga | 100.0% |
| ftga_delta | 16.7 pp |
| baseline_mean_rtt | 0.167 |
| contract_mean_rtt | 0.000 |
| baseline_unresolved | 0 |
| contract_unresolved | 0 |
| total_tokens | 2260 |

## By Coverage Slice

| Slice | Pair | Expected | Baseline FTGA | Contract FTGA | Baseline RTT | Contract RTT |
|---|---|---|---:|---:|---:|---:|
| arabic_instruction_arabic_filenames | ar-ar | Arabic | 1 | 1 | 0 | 0 |
| english_instruction_arabic_content | en-ar | Arabic | 1 | 1 | 0 | 0 |
| english_instruction_hindi_content | en-hi | Hindi | 1 | 1 | 0 | 0 |
| english_instruction_spanish_content | en-es | Spanish | 1 | 1 | 0 | 0 |
| hindi_english_instruction_hindi_devanagari | hi-hi | Hindi | 1 | 1 | 0 | 0 |
| spanish_instruction_arabic_quote | es-ar | Arabic | 0 | 1 | 1 | 0 |

## First-Turn Failures

| Item | Slice | Condition | Failure types | Snippet |
|---|---|---|---|---|
| v03_es_ar_EP_001 | spanish_instruction_arabic_quote | baseline | task_noncompletion | Claro. Una versión más pulida en árabe, sin traducirla ni cambiar los términos clave, sería:  **أنهى الفريق المسودة، لكن الخاتمة تحتاج إلى مزيد من التوضيح قبل الإرسال.**  Si quieres, también puedo darte 2–3 variantes con |

## Claim Boundary

- Treat this as a six-item smoke, not as a benchmark result.
- Do not merge it into the v0.2 headline tables.
- Do not report v0.3 performance claims until native validation and a larger pre-specified run are complete.
