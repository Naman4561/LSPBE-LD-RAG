# Bucket 6 Cleanup Change Log

## Scripts Moved And Reclassified

Moved into `scripts/final/`:
- `audit_local_models.py`
- `build_qasper_protocol_assets.py`
- `build_qasper_subset_manual_review_sample.py`
- `make_presentation_figures.py`
- `run_qasper_answer_eval.py`
- `run_qasper_final_reporting_bundle.py`
- `run_qasper_protocol_sanity_check.py`
- `run_flat_vs_bridge_significance.py` added here as a new Bucket 6 final script

Moved into `scripts/studies/`:
- `run_qasper_structure_repr_study.py`
- `run_qasper_model_selection_study.py`
- `run_qasper_bridge_repair_study.py`

Moved into `scripts/diagnostics/`:
- `run_env_preflight.py`
- `run_qasper_diagnostics.py`

Moved into `scripts/utilities/`:
- `convert_qasper_hf_to_subset.py`

Moved into `scripts/legacy/`:
- `run_qasper_final_model.py`
- `run_qasper_baseline_compare.py`
- `run_qasper_eval_bundle.py`
- `run_qasper_full_final_eval.py`
- `run_qasper_all_splits_final_eval.py`
- `run_qasper_segmentation_study.py`
- `run_bridge_v2_doc_constrained_sweep.py`
- `run_bridge_v21_doc_constrained_sweep.py`
- `run_bridge_streamlined_section_study.py`
- `run_doc_constrained_sweep.py`
- `run_mve.py`
- `run_mve_debug.py`

Root compatibility wrappers were recreated in `scripts/` for the moved runners so older commands still work.

## Artifacts Moved Or Archived

Moved caches out of current result buckets into `artifacts/support/cache/`:
- `bucket2_answer_eval/cache`
- `bucket4_model_selection/cache`
- `bucket4_5_bridge_repair/cache`
- `bucket5_final/cache`
- `environment/_run_control_smoke`

Moved logs out of current result buckets into `artifacts/support/logs/`:
- `bucket4_model_selection/logs`
- `bucket4_5_bridge_repair/logs`
- `bucket5_final/logs`

Archived from `artifacts/current/` into `artifacts/archive_serious_redo/smoke/`:
- `bucket4_model_selection_smoke/`

Moved presentation file:
- `LSPBE Presentation.pptx` to `artifacts/current/bucket5_final/presentation/`

Added final statistical addendum outputs in `artifacts/current/final_statistics/`:
- `flat_vs_bridge_significance_validation.json`
- `flat_vs_bridge_significance_validation.md`
- `flat_vs_bridge_significance_test.json`
- `flat_vs_bridge_significance_test.md`
- `flat_vs_bridge_significance_summary.md`

Added release-style top-level summaries in `artifacts/current/`:
- `final_project_summary.md`
- `final_lessons_learned.md`
- `final_limitations_and_future_work.md`

## Data Moves

Moved debug-only data into `data/archive_debug/`:
- `qasper_subset_debug_10.json`
- `qasper_subset_debug_50.json`
- `qasper_subset_sample.json`
- `qasper_train_tiny.json`

Kept as canonical current data in `data/`:
- `qasper_train_full.json`
- `qasper_train_dev.json`
- `qasper_train_lockbox.json`
- `qasper_train_fast50.json`
- `qasper_validation_full.json`
- `qasper_test_full.json`
- `splits/*.json`

## Docs Added Or Rewritten

Added or rewritten:
- `README.md`
- `scripts/README.md`
- `artifacts/ARTIFACTS_MAP.md`
- `docs/final_research_record.md`
- `docs/retrospective_analysis.md`
- `docs/what_we_did_and_did_not_do.md`
- `docs/final_repo_guide.md`
- `docs/experiment_chronology.md`
- `docs/technical_debt_and_next_steps.md`
- `docs/bucket6_cleanup_change_log.md`

Archived older plan doc:
- `docs/final_full_qasper_run_plan.md` to `docs/archive/final_full_qasper_run_plan.md`

## Removals

Removed generated clutter:
- `.pytest_cache/`
- `scripts/__pycache__/`
- `src/lspbe/__pycache__/`
- `tests/__pycache__/`

## Compatibility And Path Adjustments

- moved runner scripts were updated to rediscover the repo root from any categorized subdirectory
- final and study scripts now default caches and logs to `artifacts/support/` instead of bucket-local cache/log folders
- legacy scripts that depend on debug-only subsets now point to `data/archive_debug/`
- `.gitignore` was updated to ignore `artifacts/support/cache/` and `artifacts/support/logs/`
