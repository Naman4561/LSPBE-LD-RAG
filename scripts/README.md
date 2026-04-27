# Scripts Guide

## Taxonomy

The canonical script tree is now organized by role:

- `scripts/final/`: final rerun and release-prep scripts.
- `scripts/studies/`: major serious-redo studies that informed the final decision.
- `scripts/diagnostics/`: environment, sanity, and exploratory checks.
- `scripts/utilities/`: one-off support utilities.
- `scripts/legacy/`: preserved pre-redo and superseded runners.

The root `scripts/*.py` files are compatibility wrappers. Use the categorized subfolders for new work and for any documentation references.

## Canonical Final Scripts

- `scripts/final/build_qasper_protocol_assets.py`
- `scripts/final/run_qasper_protocol_sanity_check.py`
- `scripts/final/run_qasper_answer_eval.py`
- `scripts/final/run_qasper_final_reporting_bundle.py`
- `scripts/final/run_flat_vs_bridge_significance.py`
- `scripts/final/build_qasper_subset_manual_review_sample.py`
- `scripts/final/make_presentation_figures.py`
- `scripts/final/audit_local_models.py`

## Study Scripts

- `scripts/studies/run_qasper_structure_repr_study.py`
- `scripts/studies/run_qasper_model_selection_study.py`
- `scripts/studies/run_qasper_bridge_repair_study.py`
- `scripts/studies/post_presentation/build_segmentation_variants.py`
- `scripts/studies/post_presentation/build_structure_segmentation_variants.py`
- `scripts/studies/post_presentation/summarize_segmentation_variants.py`
- `scripts/studies/post_presentation/summarize_structure_segmentation_variants.py`
- `scripts/studies/post_presentation/run_chunking_screen.py`
- `scripts/studies/post_presentation/run_structure_segmentation_screen.py`
- `scripts/studies/post_presentation/summarize_chunking_screen.py`
- `scripts/studies/post_presentation/run_segmentation_diagnostics.py`
- `scripts/studies/post_presentation/run_structure_segmentation_diagnostics.py`
- `scripts/studies/post_presentation/run_structure_audit_and_verification.py`

## Diagnostic Scripts

- `scripts/diagnostics/run_env_preflight.py`
- `scripts/diagnostics/run_qasper_diagnostics.py`
- `scripts/diagnostics/audit_hardcoded_paths.py`
- `scripts/diagnostics/check_retrieval_text_safety.py`

## Utility Scripts

- `scripts/utilities/convert_qasper_hf_to_subset.py`
- `scripts/utilities/sanitize_artifact_paths.py`

## Legacy Scripts

These are preserved for provenance and older reruns, but they are not the serious-redo mainline:

- `scripts/legacy/run_qasper_final_model.py`
- `scripts/legacy/run_qasper_baseline_compare.py`
- `scripts/legacy/run_qasper_eval_bundle.py`
- `scripts/legacy/run_qasper_full_final_eval.py`
- `scripts/legacy/run_qasper_all_splits_final_eval.py`
- `scripts/legacy/run_qasper_segmentation_study.py`
- `scripts/legacy/run_bridge_v2_doc_constrained_sweep.py`
- `scripts/legacy/run_bridge_v21_doc_constrained_sweep.py`
- `scripts/legacy/run_bridge_streamlined_section_study.py`
- `scripts/legacy/run_doc_constrained_sweep.py`
- `scripts/legacy/run_mve.py`
- `scripts/legacy/run_mve_debug.py`

Legacy scripts that depend on debug-only data now read from `data/archive_debug/`.

## Output Conventions

- headline artifacts: `artifacts/current/...`
- caches: `artifacts/support/cache/...`
- logs: `artifacts/support/logs/...`
- archived smoke or clutter: `artifacts/archive_serious_redo/...`

## Layer 0 Guardrails

- For Layer 0 or Layer 1 segmentation cross-family comparisons, use fixed question-level subset labels via `lspbe.fixed_subsets` rather than rebuilding segmentation-specific subset labels as the primary slice view.
- `scripts/diagnostics/check_retrieval_text_safety.py` is the lightweight guardrail check for the Layer 0 `retrieval_text` separation rule.
