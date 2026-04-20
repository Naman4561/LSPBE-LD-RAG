# Scripts Guide

## Serious Redo First

Use these first for the new QASPER protocol:

- `build_qasper_protocol_assets.py`: builds the paper-level train split manifests, materialized `train_dev` / `train_lockbox` / `train_fast50` datasets, and cached validation/test subset labels under `artifacts/current/bucket1_protocol/`
- `run_qasper_protocol_sanity_check.py`: canonical Bucket 1 sanity runner for `train_fast50` and optional validation, writing to `artifacts/current/bucket1_protocol/`
- `run_qasper_answer_eval.py`: canonical Bucket 2 answer-eval runner, now with resumable per-method caches, chunk controls, and run manifests
- `run_qasper_structure_repr_study.py`: canonical Bucket 3 retrieval-first runner for comparing `current` vs `structure_aware` QASPER representations under the locked retrieval backbone
- `run_env_preflight.py`: verifies Python, package, dataset, artifact, `pytest`, and `git status` readiness and writes reports to `artifacts/current/environment/`
- `audit_local_models.py`: audits locally cached Hugging Face models with offline config/tokenizer load checks and writes reports to `artifacts/current/environment/`
- `build_qasper_subset_manual_review_sample.py`: writes the manual subset inspection bundle to `artifacts/current/manual_review/`

`run_qasper_answer_eval.py` is validation-first. Use `train_fast50` only for sanity checks in Bucket 2, keep `validation` for answer-method comparison, and reserve `test` for later final reporting.

`run_qasper_structure_repr_study.py` is also validation-first. It keeps the locked `bridge_final` retrieval path fixed, compares representation modes, writes to `artifacts/current/bucket3_structure_repr/`, and keeps answer evaluation optional and secondary.

Useful `run_qasper_answer_eval.py` controls for heavy runs:

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

## Legacy Pre-Redo Runners

These remain for reproducibility and historical context, but they are not the default serious-redo path:

- `run_qasper_final_model.py`: legacy locked-model runner
- `run_qasper_baseline_compare.py`: legacy four-way comparison runner
- `run_qasper_eval_bundle.py`: legacy one-process artifact writer
- `run_qasper_full_final_eval.py`: legacy full-split bundle wrapper
- `run_qasper_all_splits_final_eval.py`: legacy train/validation/test reporting pass
- `run_qasper_segmentation_study.py`: prior targeted segmentation study
- `run_qasper_diagnostics.py`: optional exploratory studies

## Older Reproducibility Scripts

- `run_bridge_v2_doc_constrained_sweep.py`
- `run_bridge_v21_doc_constrained_sweep.py`
- `run_bridge_streamlined_section_study.py`
- `run_doc_constrained_sweep.py`
- `run_mve.py`
- `run_mve_debug.py`

Legacy scripts now default to writing under `artifacts/legacy_pre_redo/`, with locked full-run artifacts collected in `artifacts/legacy_pre_redo/final_locked_qasper/`.
