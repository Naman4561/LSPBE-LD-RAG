# Runtime Run Policy

Run this sequence before any serious offline QASPER job:

1. Run `C:\Users\naman\AppData\Local\Programs\Python\Python39\python.exe scripts/run_env_preflight.py`.
2. Confirm `git status` works and check the preflight report for whether `pytest` is actually runnable in the active interpreter.
3. If answer-eval or local-model loading matters, run `C:\Users\naman\AppData\Local\Programs\Python\Python39\python.exe scripts/audit_local_models.py`.
4. Do a smoke run first with `--max-questions`, `--chunk-size`, and `--save-every 1`.
5. Use a stable `--cache-tag` for a long run so restarts can reuse the same cache state.

For heavy answer-eval runs, prefer:

- `--resume` to reuse completed question records
- `--overwrite` only when you intentionally want to reset an existing cache tag
- `--output-dir` for run outputs and `--cache-dir` for method caches
- `--start-index` and `--chunk-size` for chunked recovery or bounded smoke checks

Cache convention for the retrofitted answer-eval path:

- root: `artifacts/current/bucket2_answer_eval/cache/<cache_tag_or_dataset_stem>/`
- per method: `<method>/metadata.json`, `<method>/records.jsonl`, `<method>/state.json`
- `state.json` is the resumable checkpoint source of truth
- final JSON/Markdown/CSV outputs are derived from the cached per-question records

If a run is interrupted:

1. Reuse the same `--cache-tag`.
2. Re-run with `--resume`.
3. Increase `--chunk-size` or remove it when you are ready to continue farther.
4. Check the run manifest and the per-method `state.json` files before starting a brand-new cache tag.
