# run_qasper_answer_eval.py Run Manifest

- status: `completed`
- resumed: `True`
- started_at: `2026-04-20T09:17:18Z`
- ended_at: `2026-04-20T09:46:52Z`
- duration_seconds: `1774.0`
- outputs: `{"csv": "artifacts/\current\\bucket2_answer_eval\\qasper_answer_eval_validation_per_question.csv", "json": "artifacts/\current\\bucket2_answer_eval\\qasper_answer_eval_validation.json", "manifest_json": "artifacts/\current\\bucket2_answer_eval\\qasper_answer_eval_bucket2_recovery_validation_localqa.run_manifest.json", "manifest_md": "artifacts/\current\\bucket2_answer_eval\\qasper_answer_eval_bucket2_recovery_validation_localqa.run_manifest.md", "markdown": "artifacts/\current\\bucket2_answer_eval\\qasper_answer_eval_validation.md"}`
- config: `{"answerer": {"kind": "local_qa", "model_name": "distilbert-base-cased-distilled-squad", "reason": "Offline QA model 'distilbert-base-cased-distilled-squad' loaded successfully from the local Hugging Face cache."}, "cache_dir": "artifacts/current/bucket2_answer_eval/cache", "cache_tag": "bucket2_recovery_validation_localqa", "chunk_size": null, "dataset_path": "data/qasper_validation_full.json", "max_papers": 1000000, "max_questions": 1000000, "methods": ["adjacency", "bridge_final"], "overwrite": false, "save_every": 10, "segmentation_mode": "seg_paragraph_pair", "split": "validation", "start_index": 0}`
- counters: `{"adjacency": {"cache_dir": "artifacts/current/bucket2_answer_eval/cache/bucket2_recovery_validation_localqa/adjacency", "completed_questions": 1005, "computed_this_run": 0, "legacy_cache_path": null, "skipped_existing": 1005, "target_questions": 1005}, "bridge_final": {"cache_dir": "artifacts/current/bucket2_answer_eval/cache/bucket2_recovery_validation_localqa/bridge_final", "completed_questions": 1005, "computed_this_run": 0, "legacy_cache_path": null, "skipped_existing": 1005, "target_questions": 1005}}`
