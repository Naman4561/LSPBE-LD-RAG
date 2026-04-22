# Final Full-QASPER Run Plan

## Recommended Dataset Path

Use the fully converted training split already present in the repo:

- `data/qasper_train_full.json`

Recommended segmentation for the full canonical run:

- `seg_paragraph_pair`

Reason:

- it was the winner in the targeted 50-paper segmentation robustness study
- it improved `bridge_final` from `0.8214` to `0.8418` on the 50-paper set
- it also improved the adjacency baseline and the beyond-adjacency subset slice

Other available full converted splits:

- `data/qasper_validation_full.json`
- `data/qasper_test_full.json`

## Canonical Commands

Full final-model evaluation:

```bash
python scripts/run_qasper_final_model.py --qasper-path data/qasper_train_full.json --max-papers 1000000 --max-qas 1000000 --segmentation-mode seg_paragraph_pair --output-json artifacts/legacy_pre_redo/final_locked_qasper/final_qasper_full_model_results.json
```

Full baseline comparison:

```bash
python scripts/run_qasper_baseline_compare.py --qasper-path data/qasper_train_full.json --max-papers 1000000 --max-qas 1000000 --segmentation-mode seg_paragraph_pair --output-json artifacts/legacy_pre_redo/final_locked_qasper/final_qasper_full_baseline_compare.json
```

Cleaner one-shot bundle:

```bash
python scripts/run_qasper_full_final_eval.py --qasper-path data/qasper_train_full.json --segmentation-mode seg_paragraph_pair
```

## Expected Outputs

If using the one-shot bundle, the canonical artifacts are:

- `artifacts/legacy_pre_redo/final_locked_qasper/final_qasper_full_baseline_compare.json`
- `artifacts/legacy_pre_redo/final_locked_qasper/final_qasper_full_baseline_compare.md`
- `artifacts/legacy_pre_redo/final_locked_qasper/final_qasper_full_model_results.json`
- `artifacts/legacy_pre_redo/final_locked_qasper/final_qasper_full_model_summary.md`

## Environment Requirements

- `sentence-transformers` installed
- local access to the cached `BAAI/bge-base-en-v1.5` model, or network access to download it
- enough wall-clock time for BGE embedding over the full converted QASPER file

## Current Session Status

The cleaned codepath is in place, and the full converted QASPER files exist locally.

The full train / validation / test run has now completed successfully with:

- final model: `bridge_final`
- segmentation: `seg_paragraph_pair`
- outputs written under `artifacts/legacy_pre_redo/final_locked_qasper/final_qasper_*`

Rough wall-clock estimate from the fresh 50-paper validation:

- 50-paper bundle: 196 QA pairs in about 20.2 minutes
- full train split: 2593 QA pairs, roughly 4.5 hours at the same throughput
- full validation split: 1005 QA pairs, roughly 1.7 hours
- full test split: 1451 QA pairs, roughly 2.5 hours

The final public summaries now live in:

- `artifacts/legacy_pre_redo/final_locked_qasper/final_qasper_all_splits_summary.md`
- `artifacts/legacy_pre_redo/final_locked_qasper/final_qasper_presentation_summary.md`
