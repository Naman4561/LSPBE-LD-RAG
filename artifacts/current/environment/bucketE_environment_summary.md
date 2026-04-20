# Bucket E Environment Summary

- `pytest` in this runtime: not working. Plain `pytest` is not on `PATH`, and `python -m pytest` also failed because `pytest` is not installed in the active interpreter used here.
- `git status` in this runtime: working.
- Python requirement check: the active interpreter here is Python `3.9.5`, while `pyproject.toml` declares `>=3.10`.
- Stabilized areas: environment preflight, offline local-model audit, resumable question-indexed cache/state writing, atomic output writes, run manifests, and restart-safe answer-eval execution.
- Retrofitted script: `scripts/run_qasper_answer_eval.py`.
- New support scripts: `scripts/run_env_preflight.py` and `scripts/audit_local_models.py`.
- Shared runtime utility: `src/lspbe/run_control.py`.

New answer-eval runtime flags:

- `--resume`
- `--overwrite`
- `--max-questions` / `--max-qas`
- `--max-papers`
- `--start-index`
- `--chunk-size`
- `--save-every`
- `--output-dir`
- `--cache-dir`
- `--cache-tag`

Cache and resume convention:

- method cache root: `artifacts/current/bucket2_answer_eval/cache/<cache_tag_or_dataset_stem>/<method>/`
- method files: `metadata.json`, `records.jsonl`, `state.json`
- reruns with the same cache tag and `--resume` skip completed `question_id` records
- final JSON, Markdown, and CSV outputs are rebuilt from the cached per-question records

Verification completed in this runtime:

- preflight report: `artifacts/current/environment/env_preflight_report.json`
- local model audit: `artifacts/current/environment/local_model_audit.json`
- direct run-control assertion smoke: `artifacts/current/environment/_run_control_smoke/`
- answer-eval resume smoke: `artifacts/current/environment/run_resume_smoke_test.json`

Resume smoke result:

- worked
- step 1 computed 2 questions per method
- step 2 resumed the same cache tag, skipped those 2 completed questions per method, and computed only the remaining 3

Remaining limits for later buckets:

- this runtime still lacks a runnable `pytest` installation
- this runtime is below the repo's declared Python floor (`>=3.10`)
- the local offline audit only found embedding models, not cached QA or generation models
- only the mandatory Bucket E retrofit was completed; legacy long-run scripts still use their older execution model
