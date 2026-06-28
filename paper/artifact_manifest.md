# RePromptTax Artifact Manifest

Schema: `reprompt-tax-artifact-manifest-v1`

## Notes

- Deterministic manifest for paper-facing artifacts only.
- API keys, raw external logs, caches, and TeX build intermediates are intentionally excluded.
- Run scripts/make_artifact_manifest.py after regenerating artifacts.

## Reproduction Commands

- `conda run -n reprompt_tax python scripts/run_submission_checks.py`
- `conda run -n reprompt_tax python scripts/build_full_v02_scores.py`
- `conda run -n reprompt_tax python scripts/compute_metrics.py --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl --out-dir results/tables/openai_three_model_stress_v02_full120`
- `conda run -n reprompt_tax python scripts/build_full_v02_prompt_control_scores.py`
- `conda run -n reprompt_tax python scripts/compute_metrics.py --scores results/scores/openai_nano_stress_v02_full120_generic_helpfulness_auto_scores.jsonl --out-dir results/tables/openai_nano_stress_v02_full120_generic_helpfulness`
- `conda run -n reprompt_tax python scripts/score_auto.py --benchmark data/benchmark_stress_v0.2.jsonl --outputs results/model_outputs/openai_nano_stress_v02_full120_content_preservation.jsonl --out results/scores/openai_nano_stress_v02_full120_content_preservation_auto_scores.jsonl`
- `conda run -n reprompt_tax python scripts/compute_metrics.py --scores results/scores/openai_nano_stress_v02_full120_content_preservation_auto_scores.jsonl --out-dir results/tables/openai_nano_stress_v02_full120_content_preservation`
- `conda run -n reprompt_tax python scripts/paired_effects.py --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv --out-dir results/tables/openai_three_model_stress_v02_full120`
- `conda run -n reprompt_tax python scripts/analyze_language_slices.py --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv --out-dir results/tables/openai_three_model_stress_v02_full120 --out-md paper/language_slice_analysis_v02_full120.md`
- `conda run -n reprompt_tax python scripts/analyze_repair_dynamics.py --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv --out-dir results/tables/openai_three_model_stress_v02_full120 --out-md paper/repair_dynamics_v02_full120.md`
- `conda run -n reprompt_tax python scripts/analyze_benchmark_quality.py --benchmark data/benchmark_stress_v0.2.jsonl --out-dir results/tables/benchmark_quality_v02 --out-md paper/benchmark_quality_audit_v02.md`
- `conda run -n reprompt_tax python scripts/analyze_token_burden.py --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl --out-dir results/tables/openai_three_model_stress_v02_full120 --out-md paper/token_burden_analysis_v02_full120.md`
- `conda run -n reprompt_tax python scripts/summarize_experiment_ledger.py --out-dir results/tables/experiment_ledger_v02 --out-md paper/experiment_ledger_v02.md`
- `conda run -n reprompt_tax python scripts/analyze_failure_modes.py --tables-dir results/tables/openai_three_model_stress_v02_full120 --paper-out paper/failure_mode_analysis_v02_full120.md`
- `conda run -n reprompt_tax python scripts/analyze_item_consistency.py --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv --out-dir results/tables/openai_three_model_stress_v02_full120 --out-md paper/item_consistency_analysis_v02_full120.md`
- `conda run -n reprompt_tax python scripts/analyze_component_breakdown.py --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl --out-dir results/tables/openai_three_model_stress_v02_full120 --out-md paper/component_breakdown_v02_full120.md`
- `conda run -n reprompt_tax python scripts/analyze_scorer_ablation.py --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl --out-dir results/tables/openai_three_model_stress_v02_full120 --out-md paper/scorer_ablation_sensitivity_v02_full120.md`
- `conda run -n reprompt_tax python scripts/analyze_task_useful_failures.py --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl --out-dir results/tables/openai_three_model_stress_v02_full120 --out-md paper/task_useful_failure_analysis_v02_full120.md`
- `conda run -n reprompt_tax python scripts/analyze_prompt_control.py`
- `conda run -n reprompt_tax python scripts/analyze_prompt_ablation.py`
- `conda run -n reprompt_tax python scripts/build_error_atlas.py --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl --trajectories results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv --out-csv results/tables/openai_three_model_stress_v02_full120/first_turn_error_atlas.csv --out-md paper/error_atlas_v02_full120.md`
- `conda run -n reprompt_tax python scripts/paired_significance.py --trajectory-metrics results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv --out-csv results/tables/openai_three_model_stress_v02_full120/paired_significance_by_model.csv --out-md paper/paired_significance_v02_full120.md`
- `conda run -n reprompt_tax python scripts/analyze_judge_agreement.py --audit results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl --out-dir results/tables/openai_three_model_stress_v02_full120_judge_audit72 --out-md paper/judge_agreement_analysis_v02_full120.md`
- `conda run -n reprompt_tax python scripts/make_figures.py --tables-dir results/tables/openai_three_model_stress_v02_full120 --out-dir results/figures/openai_three_model_stress_v02_full120`
- `conda run -n reprompt_tax python scripts/make_human_audit_packet.py --benchmark data/benchmark_stress_v0.2.jsonl --scores results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl --out-dir data/human_audit --packet-version v0.2 --seed 23`
- `conda run -n reprompt_tax python scripts/analyze_human_audit_design.py --packet data/human_audit/human_audit_packet_v0.2.csv --answer-key data/human_audit/human_audit_answer_key_v0.2.csv --out-dir results/tables/human_audit_v0.2_design --out-md paper/human_audit_design_audit_v02.md`
- `conda run -n reprompt_tax python scripts/test_score_auto.py`
- `conda run -n reprompt_tax python scripts/lint_claim_boundaries.py`
- `cd paper && latexmk -pdf -interaction=nonstopmode main.tex`
- `conda run -n reprompt_tax python scripts/validate_paper_claims.py`
- `conda run -n reprompt_tax python scripts/validate_qualitative_examples.py`
- `conda run -n reprompt_tax python scripts/validate_followup_probe.py`
- `conda run -n reprompt_tax python scripts/validate_human_audit_packet.py`
- `conda run -n reprompt_tax python scripts/validate_stress_benchmark.py --benchmark data/benchmark_stress_v0.2.jsonl --expected-per-cell 10`
- `conda run -n reprompt_tax python scripts/discover_repair_cues.py --dataset allenai/WildChat --split train --max-conversations 20000 --out-dir results/discovery/wildchat_20k_repair_cues`
- `conda run -n reprompt_tax python scripts/analyze_discovery_cues.py --summary results/discovery/wildchat_20k_repair_cues/summary.json --metadata results/discovery/wildchat_20k_repair_cues/hit_metadata_hashed.csv --out-dir results/discovery/wildchat_20k_repair_cues --out-md paper/discovery_cue_analysis.md`
- `rg -n "Warning|undefined|Overfull|Underfull|Error" paper/main.log`

## Artifacts

| Path | Bytes | Lines | SHA-256 |
|---|---:|---:|---|
| `README.md` | 14457 | 390 | `1cc76f9fb2f0f1da48eddaeb95b9f3565b956373b873de3d9d1c967220be1875` |
| `data/benchmark_stress_v0.1.jsonl` | 72122 | 60 | `bbdb07ce418df7c3e6b9882e781e37c39b7dec5f095bc99c05b50e76ed521df9` |
| `data/benchmark_stress_v0.2.jsonl` | 144157 | 120 | `04add9af2ad78e08d7b5dd747cf9d7852031fea977e54f8701587879ba56eef1` |
| `data/human_audit/audit_manifest_v0.2.md` | 3156 | 88 | `c0efecbc923df7adbaa27ef2da6370ec580e7fd59843aa77a6972075fb33bf69` |
| `data/human_audit/human_audit_annotator_roster_template_v0.2.csv` | 249 | 4 | `405a29dff0a5025f2b1ec208ee6dd9aa0f583712b6d08ef622769c264767ac2e` |
| `data/human_audit/human_audit_answer_key_v0.2.csv` | 9020 | 73 | `4b2910b9e3a120fc43f455bec1b4ce7b018a58ec898712ca7cfceef2e32ba5a9` |
| `data/human_audit/human_audit_launch_checklist_v0.2.md` | 2377 | 58 | `0117916d2ded9ece7b82c3011f0c73d688c0a38c065ec5eabf2ee95d76ec42d8` |
| `data/human_audit/human_audit_packet_v0.2.csv` | 40897 | 126 | `94743ae01e3601fde57aa985adf26cdd2e617561b68097fa1cac9c1ac75613aa` |
| `data/human_audit/human_audit_packet_v0.2_ar-en.csv` | 15066 | 45 | `16b55bc90aa307c5cabd1223b23c770f2fa153f4448882b96dbf97caf2808e71` |
| `data/human_audit/human_audit_packet_v0.2_es-en.csv` | 13107 | 48 | `025b5ceedccb36aa3779dd8bdd588fe0caff13e86163d95f1d151bd99a8dcd05` |
| `data/human_audit/human_audit_packet_v0.2_hi-en.csv` | 13464 | 35 | `8024df03d5ec6035d8d78ef8bbfd681782aec3e92e7bd7c6a5880106ad58bb99` |
| `data/stress_v02_new_60_ids.txt` | 780 | 60 | `82709e81a0a165808a67a4ef52bc881fb6c44d52f494ab8654305c3069addaa1` |
| `data/stress_v02_new_balanced_24_ids.txt` | 312 | 24 | `8a62685673d2ac2d45724096c7803da191e669efdc99ccf573bb03dfba6354a2` |
| `data/stress_v02_remaining_36_ids.txt` | 468 | 36 | `1518dd71b3a07eae29f58f1c784b075523881b0e54e18427833edbf58d3d92f8` |
| `docs/benchmark_card.md` | 4054 | 121 | `47d24383cb9ab1e3396d853d9c62fb0d247faa119290806175f677681c243622` |
| `docs/evaluation_card.md` | 11029 | 304 | `df388b48b9eb28cf2f87e8a2d0ac1b5efbb65760402230042953505d9d497dbd` |
| `docs/human_audit_guide.md` | 4540 | 100 | `4d7258e1f4561a6f2032bc2665902da0dbcca092211b075bb246d73666844e2d` |
| `docs/result_card.md` | 10055 | 243 | `faa73a8f63a6463d48807e1b13aa73ba01b3d6df58f7901bf8add249d046253b` |
| `paper/appendix.md` | 21269 | 514 | `9907c9cec4d273a9173f5228e1691180b5338735eaebce3efac74b8ebe5f3530` |
| `paper/benchmark_quality_audit_v02.md` | 2165 | 64 | `4496d0ad427b825daa769542bbb73c6c7e68cc0a071b412c23bdcba9e69e8fdc` |
| `paper/claim_evidence_checklist.md` | 20544 | 167 | `a000580f704bb660512446d0237667184cca298ebe1a53defb40708de70eb147` |
| `paper/component_breakdown_v02_full120.md` | 3508 | 70 | `55cefed242fc5279ab83995d48ce07768490ba1f47f07d9ea54d94eb719107cc` |
| `paper/discovery_cue_analysis.md` | 2599 | 68 | `9d72eca4c37c1d7ba531387d845aa275b3cb2fd9cd591ed14a4a08050b9a368f` |
| `paper/discovery_snapshot.md` | 1845 | 64 | `2d5186a320b4b6b9a47e0b41c4306e5a3ffe300f923badfed375f9ed0c7ca1d4` |
| `paper/error_atlas_v02_full120.md` | 46430 | 220 | `8dc96aa65041be5d702af83a5661b7557634f68d10e24e25657981be23ee119a` |
| `paper/experiment_ledger_v02.md` | 2784 | 60 | `4894761852629e4aff5eed81a597922f6ec1c6791f3133d8790683cdc9ae3b5b` |
| `paper/extended_abstract_draft.md` | 9080 | 169 | `2096b9ddcfc5b6ff274eeae5d63837d27b98834d6600259fde37f71d807139af` |
| `paper/failure_mode_analysis_v02_full120.md` | 2474 | 40 | `9f451cb72c2eadbd941a9dfe40314a6a04292edbbdfd04621d26f4ea6bfb9601` |
| `paper/figures/ftga_by_condition.png` | 62975 |  | `1bf3e2e002d8dff48007101de75a1ed4b9903a7429181d829f36dcce3cbe7b36` |
| `paper/figures/repair_curve.png` | 97353 |  | `624510cc7cfa194381695b987b7d8ce4cca1b7a9caef1ef5400053060d2d7eb4` |
| `paper/human_audit_completion_plan.md` | 4309 | 107 | `090d8c93fb15d12b25aac07f616a36c2c1db29c6da3abdf4223531abcdc58082` |
| `paper/human_audit_design_audit_v02.md` | 2513 | 74 | `d62ed82524a16695b16d6181a329843b2d334c63571d0989df43eb3ae587281b` |
| `paper/item_consistency_analysis_v02_full120.md` | 3553 | 60 | `bfbb182bbcb2e198034ba10587c69d4434a14f8d36f664b1871c0ef4c39020c0` |
| `paper/judge_agreement_analysis_v02_full120.md` | 2524 | 52 | `4fee9895693920669176c8545f14eca2f5d8ab82c4e3e5307cbe3220fccd215d` |
| `paper/language_slice_analysis_v02_full120.md` | 3925 | 72 | `12d4da2d0ff01b5215c9bd51a8b052c2d5ad8bde46d6d786ef34b53ffe1aa79a` |
| `paper/main.pdf` | 169414 |  | `8ef474e3418577308a1742e5183ced55047fd18dd647db9d10269c6a52ce07eb` |
| `paper/main.tex` | 11789 | 242 | `8f00601c2f7a6c99bf8aad49916d4204314018e55a474e983cabbd217388f931` |
| `paper/paired_significance_v02_full120.md` | 1467 | 21 | `6093644e2ef6ac3486c690d4c22079e2985910a1792d389b9ad6274c1458e295` |
| `paper/prompt_ablation_analysis.md` | 6347 | 74 | `6ab68c79d3f7f459a7d765d0473ae2d9b55ffabc9dc4ef2df05150f205b727a8` |
| `paper/prompt_control_analysis.md` | 1614 | 33 | `268f517a0050c6eb65d8dcd1bf0f2d5274fc3f1c1fcd15d0e98fe94d811bff6d` |
| `paper/qualitative_examples.md` | 3977 | 142 | `1a417d225c1f47354a4648d094daca7618f0ab78ae54b16824e309a544b0746e` |
| `paper/refs.bib` | 2770 | 75 | `9ec5931246ae76e183f6e2601a4a453b8ae1cd117681930b2f1091f3a1ba3405` |
| `paper/related_work_positioning_v02.md` | 2535 | 38 | `8ecc29f5b66ecad3d7e0f5e3eae03e972d1eae3359c22883b47395010d4e652f` |
| `paper/repair_dynamics_v02_full120.md` | 2838 | 56 | `51355fe1c072c65b807558c210eefa2ed9529fbf0d8ffc8bf87b493e5f605269` |
| `paper/results_snapshot.md` | 12999 | 246 | `e628886cb4cdc0fec6300872757acb4c81a4cda30dccf5daf523002322dddd8a` |
| `paper/scorer_ablation_sensitivity_v02_full120.md` | 3167 | 57 | `fed29921eb43863bda11a671beae3b3e531e93bbffc2632d4e55bdfa044da6b3` |
| `paper/task_useful_failure_analysis_v02_full120.md` | 2976 | 67 | `a0af9a3ebec89515952af0d913d567a03fa7e34e1ce0ab80b00b1e40140cce4d` |
| `paper/token_burden_analysis_v02_full120.md` | 1595 | 34 | `197ab127d34a2951b8dddca321277c83bd40a4982cf6a98146bd6d3e94ede74c` |
| `prompts/baseline_system.txt` | 30 | 2 | `1a576e23794b48e45e2dbfc9a8c6240d60e351b2432d6ee5e9c5d06c5365c301` |
| `prompts/content_preservation_system.txt` | 427 | 5 | `8f2f6eb7cff91e81ccdb53438f4db9691155cd268d612c5a08956648e8c30613` |
| `prompts/generic_helpfulness_system.txt` | 487 | 8 | `93384811b9c6a92aeb5efd5fb2c97ab5179d67830e57703c5984f7347311b5bb` |
| `prompts/global_interaction_contract.txt` | 838 | 9 | `d6ef558ea1389e7407a86a548103d9ba5c4b711dc47ccb99826a5caf8a3501fc` |
| `prompts/judge_prompt.txt` | 848 | 32 | `f555705f9c54efb39998339343ca313ef79cfec910f919e323703e5164190ef2` |
| `reprompt_tax_workshop_paper_plan.md` | 46099 | 1541 | `db27cd7a17f68147da01204406acd4792b24d1743e02a24bded3cca3dc62049a` |
| `results/discovery/wildchat_20k_repair_cues/category_counts.csv` | 159 | 7 | `811a1119c2d2f7e610e7b342949ff93497af87462f4d4956d9d9f356df530e81` |
| `results/discovery/wildchat_20k_repair_cues/cue_category_conversation_counts.csv` | 416 | 7 | `40b9f4cc4e52d2d61c8b7ace1cb95becdc6158ea7437c9c22a324f105a0437ce` |
| `results/discovery/wildchat_20k_repair_cues/cue_discovery_overview.csv` | 315 | 2 | `75d6f6df119e8033cfbbcdf40abfa9fcdb941dd7eb6aa671a910dd384ead8ebe` |
| `results/discovery/wildchat_20k_repair_cues/cue_language_category_counts.csv` | 1562 | 34 | `8cba7ebaa4d30c2af40a7d88bc1bae558feab00b1628b130af3832ae148ac7ea` |
| `results/discovery/wildchat_20k_repair_cues/cue_pattern_counts.csv` | 951 | 23 | `be24b385c9b7534e421b7f511ba18d392c7e580c637760900d67d5439969c89b` |
| `results/discovery/wildchat_20k_repair_cues/hit_metadata_hashed.csv` | 15884 | 220 | `ec9194bbdd04298ac0b93098c46a8b18419a707b1620bc1b789bf7638c9bdb0d` |
| `results/discovery/wildchat_20k_repair_cues/repeated_cue_conversations_hashed.csv` | 2012 | 32 | `57592ca3acbf101f1546e6dc76a9308b2942f1997e9f39545d7fe3a484445661` |
| `results/discovery/wildchat_20k_repair_cues/summary.json` | 727 | 29 | `d693234ce2293e05e467488820a79698a1c99849b765fb10a4708c76ed173182` |
| `results/figures/openai_three_model_stress_v02_full120/ftga_by_condition.png` | 62975 |  | `1bf3e2e002d8dff48007101de75a1ed4b9903a7429181d829f36dcce3cbe7b36` |
| `results/figures/openai_three_model_stress_v02_full120/repair_curve.png` | 97353 |  | `624510cc7cfa194381695b987b7d8ce4cca1b7a9caef1ef5400053060d2d7eb4` |
| `results/scores/openai_mini_gpt41_stress_v02_remaining36_auto_scores.jsonl` | 130033 | 195 | `e7a11b47088c5718ad95d350ef35b82e0d2995c82711845212830cd309383c28` |
| `results/scores/openai_nano_stress60_generic_helpfulness_auto_scores.jsonl` | 49693 | 75 | `ce3f43fa8b72660372f85da2f6055c108733ea4e4a71b4e5a4e0c1024a3f0421` |
| `results/scores/openai_nano_stress_v02_full120_content_preservation_auto_scores.jsonl` | 94587 | 146 | `b15f53f06f7057f1af611e35f3843137993a43f1d1937e17917d560154577d76` |
| `results/scores/openai_nano_stress_v02_full120_generic_helpfulness_auto_scores.jsonl` | 102747 | 155 | `a38a0166a0be8d6ad1e070cf7e9a72c0374104d45492381b4618bb845f1c5617` |
| `results/scores/openai_nano_stress_v02_new60_generic_helpfulness_auto_scores.jsonl` | 53054 | 80 | `81713932162a580504d253d8616b6fcc2d1d31c7051a24a8dac4c761abbb9c12` |
| `results/scores/openai_nano_stress_v02_remaining36_auto_scores.jsonl` | 71020 | 105 | `9225e333c8bbb8064594bb89938de0f8ae35b7406ac5b3f478db5b5621d943fa` |
| `results/scores/openai_three_model_stress60_auto_scores.jsonl` | 286792 | 435 | `416b18e36e02eda8bc6a284b19a4d6891f45017588659f8bb432ebaee8a3e180` |
| `results/scores/openai_three_model_stress_v02_full120_auto_scores.jsonl` | 607833 | 917 | `c12f04d5c2c69b6c0d065fee053132a8f6050055c765e89e7f719f5ed325fac4` |
| `results/scores/openai_three_model_stress_v02_full120_judge_audit72.jsonl` | 71573 | 72 | `d16c073339e8e49bf4fac6963ae979db7bddaf37c75bede5ccb6000d9013ae46` |
| `results/scores/openai_three_model_stress_v02_new24_auto_scores.jsonl` | 119988 | 182 | `5625b2098374fd5f20ecddeb97a4708a4d3f4b9190eb78135cce96adf842293f` |
| `results/tables/benchmark_quality_v02/benchmark_quality_by_family.csv` | 439 | 5 | `361d37bcb1b814223f36722387f73659f0ebe03fb28da4877ec03cb26ac0a478` |
| `results/tables/benchmark_quality_v02/benchmark_quality_by_language.csv` | 343 | 4 | `933049c1470a8df03f49d669d28362b2d11f9e017581cb1f7014dda9d20c3da4` |
| `results/tables/benchmark_quality_v02/benchmark_quality_by_language_family.csv` | 949 | 13 | `1201695c2e4e149816949a64b2ce0d60f19bcd5204acf433df8482024a7af684` |
| `results/tables/benchmark_quality_v02/benchmark_quality_summary.csv` | 390 | 2 | `5cb58f74e7652c280909e257ee85e8be4f56499b2da7cab8af9768d2db76af98` |
| `results/tables/experiment_ledger_v02/api_usage_by_artifact.csv` | 991 | 5 | `10446d8fc5a533e7f04f67b70e721408702c106e38bdc5809fc227399f57784c` |
| `results/tables/experiment_ledger_v02/api_usage_by_judge.csv` | 225 | 2 | `0290017ae22c286c3bcabac9457a9136560d36378c17a52c0c1935661e499741` |
| `results/tables/experiment_ledger_v02/api_usage_by_model_condition.csv` | 1255 | 9 | `7d71fe299179fd3fadd5acffd6726b8980e5212d19b807b1b643ab1700024d22` |
| `results/tables/experiment_ledger_v02/experiment_ledger_summary.csv` | 289 | 2 | `75fd5a4f3d060ae04f884b6550e2a18edea9756407209721eac68bd103ac4726` |
| `results/tables/human_audit_v0.2_design/human_audit_design_by_auto_failure_type.csv` | 176 | 5 | `339d649c92cd60aaa9aa432067fb40cdff2a90839cff52bf2aeeae0319d3d8fc` |
| `results/tables/human_audit_v0.2_design/human_audit_design_by_family.csv` | 200 | 5 | `fb76c9bc5265085700e77ee1d60bf0b32783a12a042a505ad101bf699f807ecb` |
| `results/tables/human_audit_v0.2_design/human_audit_design_by_language.csv` | 120 | 4 | `0bb9bf543f752fd486d30ddd24732c2ced37224f1ba7dc0a563d8c39a2bbeb81` |
| `results/tables/human_audit_v0.2_design/human_audit_design_by_language_family.csv` | 557 | 13 | `3a24796ac4a5d33f5713538671c7876dda1185854a2915ffd775b1686ad8b5ba` |
| `results/tables/human_audit_v0.2_design/human_audit_design_by_model_condition.csv` | 269 | 7 | `7cd93c89665d440179a4dd9c29eb6e251d3b667d05101f0659987b41c4f82b02` |
| `results/tables/human_audit_v0.2_design/human_audit_design_summary.csv` | 277 | 2 | `089d9d3a22b7a8db5588123c8daf2ab26f9c71064760c0059e7c99e6d70aae41` |
| `results/tables/openai_nano_stress_v02_full120_content_preservation/failure_types_by_family.csv` | 668 | 8 | `5bcbeb64fae4426aeb3d013fbe9ba815610e418ee148098b755f74685064a90f` |
| `results/tables/openai_nano_stress_v02_full120_content_preservation/metrics_by_family.csv` | 916 | 5 | `1843e1bb6bfa2d6d5bb0664344e8d85be1ee058f4effe0af632324f88b9ac28d` |
| `results/tables/openai_nano_stress_v02_full120_content_preservation/metrics_by_language.csv` | 550 | 4 | `a93c5dd3d3a1725d6a65a597a8db1645a52e955dc2f6e1b6ac6a6a059890111e` |
| `results/tables/openai_nano_stress_v02_full120_content_preservation/metrics_summary.csv` | 402 | 2 | `1e249af616a8e5e9b020f5f18f76d34493b5921262a2a3d32c67233570375ac6` |
| `results/tables/openai_nano_stress_v02_full120_content_preservation/trajectory_metrics.csv` | 13042 | 121 | `283cf629a7780717399cc8e9ef33042d1a34829b33fc0c4c056da15ffea1dd00` |
| `results/tables/openai_nano_stress_v02_full120_generic_helpfulness/failure_types_by_family.csv` | 740 | 9 | `0aff53c5d51f335264a210ad80331de0adbbe05db6c0ec4bd3784014c71986ff` |
| `results/tables/openai_nano_stress_v02_full120_generic_helpfulness/metrics_by_family.csv` | 819 | 5 | `029297db1726f72cf973b159887715d2790a484c35258d1d674a3bc9a98b3784` |
| `results/tables/openai_nano_stress_v02_full120_generic_helpfulness/metrics_by_language.csv` | 543 | 4 | `00946755485d31e860c43452989cbec94e35b5dd6af2fc2bf36f7a80ef8bb20c` |
| `results/tables/openai_nano_stress_v02_full120_generic_helpfulness/metrics_summary.csv` | 361 | 2 | `1289090d72eb1af1448630a021cbedafc5ff04d582ec8235264c96a68bb08646` |
| `results/tables/openai_nano_stress_v02_full120_generic_helpfulness/trajectory_metrics.csv` | 13390 | 121 | `1b3ca1fe180ac42481242b9329db5dcdb504ab56d1b3c030086a8df0ac6181ab` |
| `results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_by_family.csv` | 1797 | 17 | `4c5cb056558e2dcbe905e91a4f5c0583601bf288ea0e748a4a3066081d03ca55` |
| `results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_contract_vs_content_by_family.csv` | 287 | 5 | `dde8b466d525d00d1189a8c3299a7154db9d7278c1aa9659eb015ad7b1170e3d` |
| `results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_contract_vs_content_by_language.csv` | 199 | 4 | `6ea2297315690940b76b048cba5d01d61a0083c378ac742f16c26c241ddad554` |
| `results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_contract_vs_content_examples.csv` | 4571 | 12 | `8a5c9b84b75c8b28867c694105fed8ddfddb6c7c74c1f0c75a0eb1c3d623cdea` |
| `results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_contract_vs_content_items.csv` | 34336 | 121 | `ca8865844d833f21b54c4fec6b66905412e2710707c40d61aaa1e027ae01c3fd` |
| `results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_paired_effects.csv` | 742 | 6 | `14ecfa01791b7ed7e5fdadf65f9b83047bb063c1ce80cc9ab07e025866c5430e` |
| `results/tables/openai_nano_stress_v02_full120_prompt_ablation/prompt_ablation_summary.csv` | 469 | 5 | `fc3da4f5e6b083c1378830677c4b30441b9319406b9109e3c2ce4b754d99676b` |
| `results/tables/openai_nano_stress_v02_full120_prompt_control/prompt_control_paired_effects.csv` | 502 | 4 | `d2d89c30c5acf43a09ef061668e93ff3a164125193cba505c8374a51e34523d1` |
| `results/tables/openai_nano_stress_v02_full120_prompt_control/prompt_control_summary.csv` | 364 | 4 | `b138f2fc84f16e264d5681ec67a1d54307397a738133c62dc89fdfde7c9f46b0` |
| `results/tables/openai_three_model_stress60/trajectory_metrics.csv` | 33986 | 361 | `4ce795253f64befe35000455480ef5a3cfd56c9c0df831858f897df1927972c3` |
| `results/tables/openai_three_model_stress_v02_full120/component_paired_effects_by_model.csv` | 837 | 19 | `108d8a679fb34e4f293b053dcc2c1938be9e62d49de7706f390df19e806f6856` |
| `results/tables/openai_three_model_stress_v02_full120/component_pass_by_family_condition.csv` | 923 | 9 | `8f91496c9b0d7a6e9cc966009267c830687ca9810d7dff58a035b2d5fd71e074` |
| `results/tables/openai_three_model_stress_v02_full120/component_pass_by_language_condition.csv` | 678 | 7 | `9e5db0177707d3e23520ea8aa9bc9ec896a29c6b51e55452cc9fcc563f04a208` |
| `results/tables/openai_three_model_stress_v02_full120/component_pass_by_model_condition.csv` | 699 | 7 | `19e7e727ef12447a84d123e7a71a933d012b1bacc0df121194b88c105951eac2` |
| `results/tables/openai_three_model_stress_v02_full120/failure_type_summary.csv` | 1077 | 17 | `da102bfed8c44c8d1e3b253b7790cb86d1d0d97f25fdc4930bf8c61688e963b1` |
| `results/tables/openai_three_model_stress_v02_full120/failure_types_by_family.csv` | 2552 | 36 | `ee036213a1e0a3046b3821dcbabc3458a652ae55dd0ea8328220d6938f443d5b` |
| `results/tables/openai_three_model_stress_v02_full120/family_effect_summary.csv` | 2391 | 13 | `8a430d2079709aeb4b9ecb3ee8fcdd1dfd098009180bd1b0b42c9bc96337c0ef` |
| `results/tables/openai_three_model_stress_v02_full120/first_turn_error_atlas.csv` | 47753 | 158 | `1b10b5c1f11cc157465b8b664c308202aeb9377246cae67ce8815ad39a8d2880` |
| `results/tables/openai_three_model_stress_v02_full120/item_consistency_by_family.csv` | 642 | 5 | `6d09c603aff4bcc26920ba5de7d4df7cf5b68e5b07b468692e6051079286378d` |
| `results/tables/openai_three_model_stress_v02_full120/item_consistency_by_item.csv` | 12431 | 121 | `67eeba0debfcb450838f4dbd62b0ef50c0cd8f022c0ff33dc84bd16b34cbf2a5` |
| `results/tables/openai_three_model_stress_v02_full120/item_consistency_hardest_items.csv` | 1375 | 13 | `1da64a6eafe9763b40cc9e7373305d69f3e639c274cec5161dc5c1cebb58366d` |
| `results/tables/openai_three_model_stress_v02_full120/item_consistency_summary.csv` | 432 | 2 | `8da01a462ef63490de6a8ca9babb613f537c51d4543f9ad065aff212f09110ff` |
| `results/tables/openai_three_model_stress_v02_full120/language_slice_aggregate_effects.csv` | 248 | 4 | `a2411906c8afc72002eb6b34f2a8d62307e6440e9b09243318f4c4f87b57a034` |
| `results/tables/openai_three_model_stress_v02_full120/language_slice_metrics.csv` | 1059 | 19 | `540cca33eb164efc7b38df9194b050f9a829a8cb6eb4675b13972bb3be44595a` |
| `results/tables/openai_three_model_stress_v02_full120/language_slice_paired_effects.csv` | 639 | 10 | `194d9ed71c43a48b9921de1b9027d708332eac3ef504fcaa1ec6162641f974a4` |
| `results/tables/openai_three_model_stress_v02_full120/metrics_by_family.csv` | 3519 | 25 | `52e161cfdc9fbe7a8c28bd0be66c298e728d1b73288b1e72e95d020a8683b23c` |
| `results/tables/openai_three_model_stress_v02_full120/metrics_by_language.csv` | 2160 | 19 | `22b48f1d08d69f3928878fddd5b5ac925b0691919e6b65991c63afd26f373b1e` |
| `results/tables/openai_three_model_stress_v02_full120/metrics_summary.csv` | 1320 | 7 | `fe971ddc6400b84baa35a4750bc6f4d6a82d64e5aa500b13c73c82e6db9424b1` |
| `results/tables/openai_three_model_stress_v02_full120/paired_contract_effects_by_family.csv` | 2132 | 13 | `9c1f96ed0b3600458494adf37fe7baa551784e62b72e970890d3866ba7bee469` |
| `results/tables/openai_three_model_stress_v02_full120/paired_contract_effects_by_model.csv` | 905 | 4 | `2aa20832192ed6ba8f8cb926c3262a02b8836d316343b4bd90e8b948755754df` |
| `results/tables/openai_three_model_stress_v02_full120/paired_significance_by_model.csv` | 1363 | 13 | `9707c06d7d5c17292adb16c6e1c93369126f31d9550ef2274f4e9e05a887cbaf` |
| `results/tables/openai_three_model_stress_v02_full120/repair_dynamics_by_family_condition.csv` | 1007 | 9 | `0c7ad48e29285aa02bf87a6c19de91478d4c9d505b516f6cdb1570dfcdbaa320` |
| `results/tables/openai_three_model_stress_v02_full120/repair_dynamics_by_language_condition.csv` | 756 | 7 | `859c7892599863a69cf7e165c2c24305a84cdd899c999e24de6cdc28c6fa768d` |
| `results/tables/openai_three_model_stress_v02_full120/repair_dynamics_by_model_condition.csv` | 779 | 7 | `2f2e576e15b8f827efb918fd4346435366e6b1f92b9220cae07ff9180d357597` |
| `results/tables/openai_three_model_stress_v02_full120/repair_paired_effects_by_model.csv` | 321 | 4 | `e88710fd5d3af2f008513cdfff9d2775a44eda77e6169fc8eb0bd828990326d2` |
| `results/tables/openai_three_model_stress_v02_full120/repair_rtt_transition_by_model.csv` | 926 | 49 | `ab71cf9849ef04db9dc0f7a7fdcbba1293141e9c6081e52f7c3683412805a478` |
| `results/tables/openai_three_model_stress_v02_full120/scorer_ablation_by_condition.csv` | 752 | 3 | `2853f80503d0bce59cfc467451047d9cddd7de7b8e97d05ec0419d7b144c3764` |
| `results/tables/openai_three_model_stress_v02_full120/scorer_ablation_by_family_condition.csv` | 1503 | 9 | `f94456193455b7f631969a359f8faf22d46cfe34f1ee60ee6cb609fbe42d48b4` |
| `results/tables/openai_three_model_stress_v02_full120/scorer_ablation_by_model_condition.csv` | 1199 | 7 | `9152cf2a574b7c2c7253095fae52a20d5bfe04173c00a52b8c25a00a9a78f1fd` |
| `results/tables/openai_three_model_stress_v02_full120/scorer_ablation_failure_signatures.csv` | 786 | 14 | `e09cfb06982598e798c60e21da793dd002c729ff6eeec928be0aa37368b1ecea` |
| `results/tables/openai_three_model_stress_v02_full120/scorer_ablation_top_failure_signatures.csv` | 637 | 11 | `c66bb25cbecc83c859d198f6dbbb9f2cdad69baac2ff8345c30a8cb8fe650eca` |
| `results/tables/openai_three_model_stress_v02_full120/task_useful_failure_by_condition.csv` | 525 | 3 | `dc396b100070d8b102723b8ab191ab069e1960dca5ef4d21738e609a0c867d16` |
| `results/tables/openai_three_model_stress_v02_full120/task_useful_failure_by_family_condition.csv` | 1056 | 9 | `0a5711468ca4afde77dd8ef601d49d76adcd3a4f2103714cbaab7fb9a51b13cb` |
| `results/tables/openai_three_model_stress_v02_full120/task_useful_failure_by_language_condition.csv` | 813 | 7 | `7bc1a85f3255033de14924c56f76e62a0b14dc47150e24a2d4c97c2f75527757` |
| `results/tables/openai_three_model_stress_v02_full120/task_useful_failure_by_model_condition.csv` | 837 | 7 | `d11f9985daa2bba9f0e7702d49de8d5d26c0cb1d72f580910979f82913f83a7c` |
| `results/tables/openai_three_model_stress_v02_full120/task_useful_failure_signatures.csv` | 334 | 6 | `5d5490bf0e7e04d8025ecfc6345fa7561257441eda3713abc163262a7e62c23a` |
| `results/tables/openai_three_model_stress_v02_full120/token_burden_by_family.csv` | 3242 | 25 | `96445d7b16f5ade38bae988b8c6ce868e89e1f3976c4a056d51d01959e377913` |
| `results/tables/openai_three_model_stress_v02_full120/token_burden_by_language.csv` | 1895 | 19 | `6dc52e21a7d866bff62afd12f37ea94469ac864fa81fec0c95446d13e03e10c8` |
| `results/tables/openai_three_model_stress_v02_full120/token_burden_by_model.csv` | 974 | 7 | `72f59b4748bbb26d7939526ad573c723ceb6aa13a1df5bdbc1a116c4b79b426a` |
| `results/tables/openai_three_model_stress_v02_full120/token_burden_paired_effects_by_model.csv` | 484 | 4 | `4876a8080c304f5e3511832c551ccd2632538eafc6dce80de1519df2799a1a15` |
| `results/tables/openai_three_model_stress_v02_full120/token_burden_trajectory_metrics.csv` | 66295 | 721 | `8fc8dbab7c151a2a9844ac2aa333ffffa3a9b3226ad834ea5b6eae54f43d6648` |
| `results/tables/openai_three_model_stress_v02_full120/trajectory_metrics.csv` | 69222 | 721 | `2ae33870419dc8470159b31626097cee1583a8caec79dd469b9925ce7ad17167` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_agreement_by_family.csv` | 509 | 5 | `40dd9a4161859597f91d6e453899de395dc6aa4c351948716fd9e48b30305dd0` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_agreement_by_model_condition.csv` | 640 | 7 | `2277baed731a74996a245f48b6eb4a4dabe083860d8b8fedc6007857b25d9369` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_agreement_summary.csv` | 268 | 2 | `7aef22cc0d51ed58b5496b7a96816ef1a2d64824041e92a9ea0fa06e6d7ebbce` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_audit_by_family.csv` | 372 | 5 | `f0a7ff82d1746ab29d873df454dfb85a7de44a57dce365515c8e91767ce9ca71` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_audit_by_model_condition.csv` | 479 | 7 | `e4c58263b36ffef25e96afc1f9de166fa2d56d31ca0ffa49122b2394da1aaea9` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_audit_disagreements.csv` | 340 | 2 | `6ee75ded388e7ddaa662612dae36a523cb5a23f168fabaf7834e8af5de278d26` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_audit_summary.csv` | 151 | 2 | `26dff309045fa862d781ff0442abe923df27829e0b78cb3543f0820f59c5a86a` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_component_agreement.csv` | 376 | 6 | `b70dce2079141c0da73291a9f5b4f1afea4e1f04c406930472c13ab8cabd7e2a` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_component_disagreements.csv` | 3571 | 11 | `0d0509ddb44c93fb9020eaef1a6aa4611a1e911f213a35a2c24d19dd2067cbe1` |
| `results/tables/openai_three_model_stress_v02_full120_judge_audit72/judge_pass_fail_disagreements.csv` | 340 | 2 | `6ee75ded388e7ddaa662612dae36a523cb5a23f168fabaf7834e8af5de278d26` |
| `results/tables/openai_three_model_stress_v02_new24/metrics_summary.csv` | 1062 | 7 | `8a87c75c4a11aaa7878ceb765c59a109f17f9edf0be8e6de5a0eb8db6dbff28f` |
| `scripts/analyze_benchmark_quality.py` | 12525 | 287 | `bfcf43a5fed62b75abacebf8304899f6e873983ef860644fce0d13f65eaa3b8b` |
| `scripts/analyze_component_breakdown.py` | 10897 | 263 | `03c5ae35f1bceb6b4ab85094cf7f22656ec3a57f1005360395cf59ad2b817e4b` |
| `scripts/analyze_discovery_cues.py` | 9499 | 218 | `552e8eba15fcd5dc635d30978a9b1449b950061e3b17db6f0d800790a6d9c9c0` |
| `scripts/analyze_failure_modes.py` | 11765 | 312 | `060c338ed3d314cf6643e8f2a231b9f5bc3756b9ff9d0ad5b9e1f18f325a7546` |
| `scripts/analyze_human_audit_design.py` | 11589 | 297 | `e0bc74548f4c92775a885e25fb706c53a9950268b181208d407c555841968384` |
| `scripts/analyze_item_consistency.py` | 13187 | 292 | `6418de1c3a662b6229e38c8f3de446373b45b9520a4ce912a335da8930cb350a` |
| `scripts/analyze_judge_agreement.py` | 15274 | 348 | `d28a45382aa125ce9aa3870af3c7d2aefade6d33a043c87daf6c5d3820f96d18` |
| `scripts/analyze_language_slices.py` | 11635 | 262 | `d0d671f104c5f72ca0529235d086470d978b0d25bda88634fda55b25608bd470` |
| `scripts/analyze_prompt_ablation.py` | 20660 | 515 | `fc0fa06d4786539efde85ae3eefc7a1fd62a0cdb496b8a40d0475af018965e7d` |
| `scripts/analyze_prompt_control.py` | 9802 | 248 | `9e0982e223833a1d964f69c1520d28a0088be37e6642e9bc142af1e69185f4ed` |
| `scripts/analyze_repair_dynamics.py` | 11340 | 247 | `9bb4b0ebccb615eccc7ea811e0d39042a2f43992768f4fbf597e60a218db3447` |
| `scripts/analyze_scorer_ablation.py` | 12281 | 314 | `d2e7f8f82c7498a020a7c4cc2ab6024f9f987742ef19e251f5e3b1330e077dd2` |
| `scripts/analyze_task_useful_failures.py` | 13571 | 334 | `2a7f5ab5ad64b0a1342a68f1b98ce8bce4300f7ae56b68680a8ae4f59c684c96` |
| `scripts/analyze_token_burden.py` | 9289 | 216 | `685148118bd92bce9c82d75c50c8a899d787684b9085c6251b29a0d4de34b611` |
| `scripts/build_error_atlas.py` | 7011 | 199 | `427a6deb54059cb98e39e8bbb079978e7fec9304ca6defa55eb1c6baa77ee50a` |
| `scripts/build_full_v02_prompt_control_scores.py` | 3334 | 86 | `6f0a1f66e2f2c78f1492109338e533a8147d65ae80285025d63cf90607cf3c69` |
| `scripts/build_full_v02_scores.py` | 3507 | 89 | `d8f36dbfe48e68288cbf5c8486ac3c3f3920a5c2aab89225e449ef5d79ce45c5` |
| `scripts/compute_metrics.py` | 7489 | 195 | `bb74f1beb218466ae64a319e89b2653796594586f5cb57aca87d805db7fd0f52` |
| `scripts/discover_repair_cues.py` | 8156 | 243 | `fb9114fddba0a718a1eb5122d36c014ade87f90445b4a6c47f70909b687f1269` |
| `scripts/generate_benchmark.py` | 20043 | 470 | `68a3e454555497be971db9046adbca2ff5bcb2009eff1aa6a9c297e78ff8f31d` |
| `scripts/generate_stress_benchmark.py` | 11955 | 267 | `98e670ac4dff7377fe68572bc3100e49c3f6f0305d56f9935e369cee31b674f2` |
| `scripts/generate_stress_benchmark_v02.py` | 10953 | 262 | `ee407c0bbc5567895b155a59e5dce7722a2e320703a64995ff5fdf51238b4ff1` |
| `scripts/judge_outputs.py` | 10150 | 274 | `bc090a1735c5ce24f9941949b042956c03c5f287255ff1f7f83d099854e4dffb` |
| `scripts/lint_claim_boundaries.py` | 3515 | 105 | `38d925f2d44627084336c283ab6e4848696d8f43846965bb077be0f081edaf52` |
| `scripts/make_artifact_manifest.py` | 25467 | 372 | `82e7b7007fa093da0a0ffd81c8de0c570e8b9246e2289b89b03aeb113d064de9` |
| `scripts/make_figures.py` | 3300 | 98 | `03a120ad55433b233e42b29234110522fce8231aeb483a6a4fcf630b9d7512f7` |
| `scripts/make_human_audit_packet.py` | 13832 | 389 | `bc249ef5f8825e05179fae215b59bcda05b048ea21a70521cf9626fe182fcbff` |
| `scripts/paired_effects.py` | 4793 | 121 | `3fc08c5d121606352801c177497b2f40fa5d0422d776abb43c9e8eb3c005c24b` |
| `scripts/paired_significance.py` | 5364 | 147 | `55a79e0e90b5dfc22a13b06001cce155a729057bb2118e726c5609606cc15788` |
| `scripts/run_models.py` | 11654 | 323 | `88d6f4ffe49883a9356bedee3467cf555c788a9c740c3d91fc777ab08556d313` |
| `scripts/run_submission_checks.py` | 11238 | 320 | `1b109a4fe6e32ae2da94113737740bd7b8c851b71d5c7b3cfc2550ab5cd88fa9` |
| `scripts/score_auto.py` | 8140 | 299 | `4cc1d94f0924a448291eff9fb82357a5b1abd49063c6e469d254b36afc66e996` |
| `scripts/summarize_experiment_ledger.py` | 13458 | 334 | `2265cc714aa8d3b26c57c33f49ff7ebf48300299668afae46ce4f8c2a7aaf3ba` |
| `scripts/summarize_human_audit.py` | 6222 | 160 | `3fa4368f6baf7a83f4d1b868d3a632df400988eea6a2ea9a8211dad382784a8f` |
| `scripts/summarize_judge_audit.py` | 3995 | 108 | `a368a123ca3db04b10751a38a8c8a42a0ca30620d83fbf31ade616ea9dd26cc9` |
| `scripts/test_human_audit_completion.py` | 5928 | 173 | `1b68f5f887cd18e24ff7c1cfe16f6e4b81f959d82db6c24316148b67cc43492a` |
| `scripts/test_score_auto.py` | 6070 | 156 | `9c4422d98e18da6be5ba076284d82ee982526f61b429484f3e91eea42cbaacba` |
| `scripts/validate_completed_human_audit.py` | 9952 | 230 | `62aca763cbde7ab6c6d371e498ad3bed224b52d3c32627a379e95be4f1467c17` |
| `scripts/validate_followup_probe.py` | 6033 | 138 | `641f94e0233e92e807056dcd306aaceab7d84e514d5b8cabe259c57514d404b3` |
| `scripts/validate_human_audit_packet.py` | 8680 | 197 | `4566a2fd748c471b3b7facd0dc188327c97e568113e7c5b3f3dae548c53811d9` |
| `scripts/validate_paper_claims.py` | 112701 | 2158 | `0c485384bd77fffc8086ae0f13f73a29ca80c40c4106b8e758853247dd827b02` |
| `scripts/validate_qualitative_examples.py` | 6982 | 202 | `b483926397b7df75c18a626d0af28332e7c5c22e34ae9b8dc1f61ff28be78d62` |
| `scripts/validate_stress_benchmark.py` | 3087 | 88 | `d5edb4e9d83a9f40c9b57d175abe689a9f2b419a19ebbb430344def190cfa2f7` |
