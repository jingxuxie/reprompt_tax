# Human/Native Review Threshold Rationale

This report explains the numeric gates in
`paper/human_audit_acceptance_rules_v02.md`. It does not report completed
labels; it only makes the pre-specified future claim thresholds auditable.

## Thresholds

| Surface | Metric | Threshold | Rate | Wilson 95% interval | Rationale |
|---|---|---:|---:|---|---|
| human_audit_v02_gpt41_family | overall_pass_agreement | 65/72 | 90.3% | [81.3%, 95.2%] | requires at least 90 percent overall pass/fail agreement before claiming scorer support |
| human_audit_v02_gpt41_family | component_agreement | 306/360 | 85.0% | [80.9%, 88.3%] | requires at least 85 percent agreement across language, script, preservation, task, and register/locale components |
| human_audit_v02_current_gpt5 | overall_pass_agreement | 44/48 | 91.7% | [80.4%, 96.7%] | requires at least 90 percent overall pass/fail agreement before claiming scorer support |
| human_audit_v02_current_gpt5 | component_agreement | 204/240 | 85.0% | [79.9%, 89.0%] | requires at least 85 percent agreement across language, script, preservation, task, and register/locale components |
| coverage_native_review_v03 | release_usable_rows | 60/60 | 100.0% | [94.0%, 100.0%] | requires every synthetic v0.3 row to be release usable before any v0.3 benchmark-evidence claim |

## Interpretation

- The two human-audit surfaces use an overall pass/fail agreement gate
  and a stricter component-level audit gate because language, script,
  preservation, task completion, and register/locale can disagree.
- The v0.3 coverage surface has a 60/60 release-usability gate because
  it validates synthetic benchmark rows rather than model outputs.
- Passing these thresholds is necessary but not sufficient: the completed
  label validators, qualified rosters, and claim-gate analyzer must also
  pass before the paper claims native/near-native validation.
