# Final Repo Guide

## Top-Level Structure

- `src/lspbe/`: core library code.
- `scripts/`: categorized runners plus root compatibility wrappers.
- `docs/`: protocol docs, final retrospective docs, and archived older plans.
- `data/`: canonical serious-redo datasets and split manifests.
- `artifacts/`: current outputs, support caches/logs, archived smoke, and legacy historical outputs.
- `tests/`: lightweight regression tests.

## Script Structure

- `scripts/final/`: canonical rerun path.
- `scripts/studies/`: major scientific studies that led to the final choice.
- `scripts/diagnostics/`: environment and troubleshooting helpers.
- `scripts/utilities/`: data-format support scripts.
- `scripts/legacy/`: old or superseded runners.

## Artifact Structure

- `artifacts/current/`: current serious-redo artifacts and release summaries.
- `artifacts/support/cache/`: caches and resumable state.
- `artifacts/support/logs/`: logs.
- `artifacts/archive_serious_redo/`: archived smoke or low-value redo artifacts.
- `artifacts/legacy_pre_redo/`: pre-redo project history.

## Data Structure

Canonical current data:

- `data/qasper_train_full.json`
- `data/qasper_train_dev.json`
- `data/qasper_train_lockbox.json`
- `data/qasper_train_fast50.json`
- `data/qasper_validation_full.json`
- `data/qasper_test_full.json`
- `data/splits/*.json`

Archived debug-only data:

- `data/archive_debug/qasper_subset_debug_10.json`
- `data/archive_debug/qasper_subset_debug_50.json`
- `data/archive_debug/qasper_subset_sample.json`
- `data/archive_debug/qasper_train_tiny.json`

## Canonical Rerun Path

1. `scripts/diagnostics/run_env_preflight.py`
2. `scripts/final/build_qasper_protocol_assets.py`
3. `scripts/final/run_qasper_protocol_sanity_check.py`
4. `scripts/studies/run_qasper_model_selection_study.py`
5. `scripts/studies/run_qasper_bridge_repair_study.py`
6. `scripts/final/run_qasper_final_reporting_bundle.py`
7. `scripts/final/run_flat_vs_bridge_significance.py`
