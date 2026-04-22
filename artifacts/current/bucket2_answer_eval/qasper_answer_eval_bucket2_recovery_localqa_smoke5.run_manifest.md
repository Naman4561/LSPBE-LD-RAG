# run_qasper_answer_eval.py Run Manifest

- status: `completed`
- resumed: `True`
- started_at: `2026-04-20T06:03:12Z`
- ended_at: `2026-04-20T06:03:28Z`
- duration_seconds: `16.0`
- outputs: `{"csv": "artifacts/\current\\bucket2_answer_eval\\qasper_answer_eval_bucket2_recovery_localqa_smoke5_per_question.csv", "json": "artifacts/\current\\bucket2_answer_eval\\qasper_answer_eval_bucket2_recovery_localqa_smoke5.json", "manifest_json": "artifacts/\current\\bucket2_answer_eval\\qasper_answer_eval_bucket2_recovery_localqa_smoke5.run_manifest.json", "manifest_md": "artifacts/\current\\bucket2_answer_eval\\qasper_answer_eval_bucket2_recovery_localqa_smoke5.run_manifest.md", "markdown": "artifacts/\current\\bucket2_answer_eval\\qasper_answer_eval_bucket2_recovery_localqa_smoke5.md"}`
- config: `{"answerer": {"kind": "local_qa", "model_name": "distilbert-base-cased-distilled-squad", "reason": "Offline QA model 'distilbert-base-cased-distilled-squad' loaded successfully from the local Hugging Face cache."}, "cache_dir": "artifacts/current/bucket2_answer_eval/cache", "cache_tag": "bucket2_recovery_localqa_smoke5", "chunk_size": 5, "dataset_path": "data/qasper_train_fast50.json", "max_papers": 1000000, "max_questions": 5, "methods": ["adjacency", "bridge_final"], "overwrite": false, "save_every": 1, "segmentation_mode": "seg_paragraph_pair", "split": "train", "start_index": 0}`
- counters: `{"adjacency": {"cache_dir": "artifacts/current/bucket2_answer_eval/cache/bucket2_recovery_localqa_smoke5/adjacency", "completed_questions": 5, "computed_this_run": 0, "legacy_cache_path": null, "skipped_existing": 5, "target_questions": 5}, "bridge_final": {"cache_dir": "artifacts/current/bucket2_answer_eval/cache/bucket2_recovery_localqa_smoke5/bridge_final", "completed_questions": 5, "computed_this_run": 0, "legacy_cache_path": null, "skipped_existing": 5, "target_questions": 5}}`
