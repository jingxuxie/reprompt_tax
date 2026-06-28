# Discovery Cue Analysis

Generated from `results/discovery/wildchat_20k_repair_cues/summary.json`
and `results/discovery/wildchat_20k_repair_cues/hit_metadata_hashed.csv`.

This analysis uses only aggregate counts and hashed metadata. It writes no
raw user or assistant text and must not be interpreted as a representative
prevalence estimate.

## Overview

| Metric | Value |
|---|---:|
| dataset | allenai/WildChat |
| split | train |
| conversations_scanned | 20000 |
| user_turns_scanned | 58764 |
| multiturn_conversations | 10681 |
| conversations_with_repair_cues | 172 |
| cue_hits_total | 219 |
| metadata_rows | 219 |
| unique_conversations_in_metadata | 172 |
| repeated_cue_conversations | 31 |
| max_cue_hits_in_conversation | 5 |
| raw_text_written | False |

## Categories

| Category | Cue hits | Unique conversations | Top row language | Top message language |
|---|---:|---:|---|---|
| generic_repair | 93 | 81 | English (90) | English (85) |
| preservation_failure | 25 | 18 | English (24) | English (23) |
| register_locale_mismatch | 16 | 13 | English (16) | English (16) |
| script_mismatch | 4 | 2 | English (4) | English (4) |
| unwanted_translation | 13 | 13 | English (10) | English (13) |
| wrong_output_language | 68 | 48 | English (38) | English (45) |

## Top Cue Patterns

| Category | Cue pattern | Hits |
|---|---|---:|
| generic_repair | `\bi meant\b` | 52 |
| wrong_output_language | `\bin english\b` | 47 |
| generic_repair | `\btry again\b` | 34 |
| preservation_failure | `\bpreserve\b` | 17 |
| unwanted_translation | `\bsame language\b` | 10 |
| wrong_output_language | `\ben ingl[eé]s\b` | 10 |
| wrong_output_language | `\ben espa[nñ]ol\b` | 9 |
| register_locale_mismatch | `\bmore formal\b` | 7 |
| register_locale_mismatch | `\brespectful\b` | 7 |
| generic_repair | `\bte dije\b` | 5 |
| script_mismatch | `\bromanized\b` | 4 |
| preservation_failure | `\bdo not change\b` | 3 |

## Repeated Cue Conversations

31 hashed conversations contain two or more cue hits; 
the maximum is 5 cue hits in one conversation.

## Interpretation

The cue scan supports the taxonomy used in the synthetic stress benchmark:
generic repair, wrong output language, preservation, unwanted translation,
script, and register/locale cues all occur in a bounded public-chat slice.
Wrong-output-language cues are the most multilingual-looking category in
the metadata, while generic repair cues are mostly English. Because the
method is regex-based and no raw turns are inspected in this artifact, the
result should be treated only as motivation for the benchmark taxonomy.
