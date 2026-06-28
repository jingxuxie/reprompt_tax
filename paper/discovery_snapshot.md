# Real-World Repair Cue Discovery Snapshot

Dataset: `allenai/WildChat`

Scan command:

```bash
conda run -n reprompt_tax python scripts/discover_repair_cues.py \
  --dataset allenai/WildChat \
  --split train \
  --max-conversations 20000 \
  --out-dir results/discovery/wildchat_20k_repair_cues
```

## Privacy Posture

The script writes no raw user or assistant text. Outputs are aggregate counts
plus hashed conversation IDs, message indices, cue categories, cue regex names,
and language metadata.

## Aggregate Result

Source: `results/discovery/wildchat_20k_repair_cues/summary.json`

- Conversations scanned: 20,000
- User turns scanned: 58,764
- Multi-turn conversations: 10,681
- Conversations with repair cues: 172
- Total cue hits: 219

Cue category counts:

| Category | Count |
|---|---:|
| generic_repair | 93 |
| wrong_output_language | 68 |
| preservation_failure | 25 |
| register_locale_mismatch | 16 |
| unwanted_translation | 13 |
| script_mismatch | 4 |

Additional hashed-metadata analysis:

- Unique conversations in hit metadata: 172
- Conversations with repeated cue hits: 31
- Maximum cue hits in a single hashed conversation: 5
- Unique conversations by category:
  - generic_repair: 81
  - wrong_output_language: 48
  - preservation_failure: 18
  - register_locale_mismatch: 13
  - unwanted_translation: 13
  - script_mismatch: 2

See `paper/discovery_cue_analysis.md` for cue-pattern and language-metadata
breakdowns.

## Interpretation

This is a bounded, cue-based discovery scan over a streamed WildChat slice. It
should not be interpreted as a representative prevalence estimate. It does
support the paper's motivation: public multi-turn LLM logs contain follow-up
turns with repair language related to generic correction, output language,
exact preservation, unwanted translation, script, and register/locale.
