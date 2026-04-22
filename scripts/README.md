# Scripts Guide

## Serious Redo First

Use these first for the new QASPER protocol:

- `build_qasper_protocol_assets.py`: builds the paper-level train split manifests, materialized `train_dev` / `train_lockbox` / `train_fast50` datasets, and cached validation/test subset labels under `artifacts/current/bucket1_protocol/`
- `run_qasper_protocol_sanity_check.py`: canonical Bucket 1 sanity runner for `train_fast50` and optional validation, writing to `artifacts/current/bucket1_protocol/`
- `run_qasper_answer_eval.py`: canonical Bucket 2 answer-eval runner, now with resumable per-method caches, chunk controls, and run manifests
- `run_qasper_structure_repr_study.py`: canonical Bucket 3 retrieval-first runner for comparing `current` vs `structure_aware` QASPER representations under the locked retrieval backbone
- `run_qasper_model_selection_study.py`: canonical Bucket 4 validation-only retrieval-family comparison and finalist answer-eval runner; compares `flat`, `adjacency`, `bridge_v2`, `bridge_final`, and one deterministic fixed-chunk baseline under the cleaned protocol
- `run_qasper_bridge_repair_study.py`: canonical Bucket 4.5 retrieval-only bridge-repair runner; reuses Bucket 4 validation baselines, tests `bridge_from_flat_seeds_current` first, then `bridge_from_flat_seeds_selective_current`, and writes outputs under `artifacts/current/bucket4_5_bridge_repair/`
- `run_qasper_final_reporting_bundle.py`: canonical Bucket 5 final reporting runner; keeps `flat_hybrid_current` locked, compares it to one compact baseline on `test`, runs held-out retrieval plus answer eval, writes the error audit, and builds the presentation bundle under `artifacts/current/bucket5_final/`
- `run_env_preflight.py`: verifies Python, package, dataset, artifact, `pytest`, and `git status` readiness and writes reports to `artifacts/current/environment/`
- `audit_local_models.py`: audits locally cached Hugging Face models with offline config/tokenizer load checks and writes reports to `artifacts/current/environment/`
- `build_qasper_subset_manual_review_sample.py`: writes the manual subset inspection bundle to `artifacts/current/manual_review/`

`run_qasper_answer_eval.py` is validation-first. Use `train_fast50` only for sanity checks in Bucket 2, keep `validation` for answer-method comparison, and reserve `test` for later final reporting.

`run_qasper_structure_repr_study.py` is also validation-first. It keeps the locked `bridge_final` retrieval path fixed, compares representation modes, writes to `artifacts/current/bucket3_structure_repr/`, and keeps answer evaluation optional and secondary.

`run_qasper_model_selection_study.py` is the Bucket 4 main scientific comparison bucket. It stays validation-only, treats retrieval as the primary selector, advances only the top retrieval finalists to full answer evaluation, and writes its study outputs under `artifacts/current/bucket4_model_selection/`.

`run_qasper_bridge_repair_study.py` is the Bucket 4.5 follow-up bucket. It stays retrieval-only, keeps the Bucket 4 mainline representation fixed, does not rerun the old method matrix, and only asks whether bridge becomes competitive again once it starts from the same flat seeds and then uses selective expansion.

`run_qasper_final_reporting_bundle.py` is the Bucket 5 final execution/reporting bucket. It does not reopen selection, keeps retrieval as the main story, includes answer eval as a secondary signal, and produces the slide-ready artifacts for the 8-minute presentation.

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
