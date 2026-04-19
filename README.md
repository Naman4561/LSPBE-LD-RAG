# LSPBE-LD-RAG

Lightweight long-document retrieval for QASPER using local bridge expansion.

The repo now centers on one locked final QASPER model, `bridge_final`, plus three reproducible comparison baselines:

- `adjacency`: adjacency-only expansion
- `bridge_v1`: original multi-signal local bridge baseline
- `bridge_v2`: current Bridge v2 skip-local baseline
- `bridge_final`: streamlined final model

## What The Project Does

LSPBE tests whether document-local structure can recover evidence that plain chunk retrieval misses. Documents are segmented into section-aware paragraph chunks, seed chunks are retrieved with BGE embeddings, and local expansion adds nearby evidence without building a full document graph.

## Final Model

Canonical model name: `bridge_final`

Locked QASPER configuration:

- hybrid seed retrieval
- dense weight `1.00`
- sparse weight `0.50`
- Bridge v2 skip-local design
- max skip distance `2`
- top bridge candidate per seed `1`
- continuity mode `idf_overlap`
- no section scoring
- no adaptive trigger
- no reranker
- no diversification

This is the clean default because the latest diagnostics showed that the extra v2.1 add-ons did not improve the best result beyond the hybrid seed change.

## Locked 50-Paper Diagnostic Results

- adjacency: `0.7704`
- bridge v1: `0.7704`
- current Bridge v2 baseline: `0.8112`
- final streamlined model: `0.8214`
- beyond-adjacency subset hit rate for the final streamlined model: `0.8511`

Main interpretation:

- the biggest extra gain over the earlier Bridge v2 baseline came from hybrid seed retrieval
- section scoring did not improve the streamlined study
- diversification did not improve the streamlined study
- no examples were found where improved section scoring helped
- no examples were found where removing sections helped over the tied streamlined result

## Install

```bash
pip install -e .
pip install -e ".[retrieval,dev]"
pip install datasets
```

## Data Prep

Create a small QASPER subset for debugging:

```bash
python scripts/convert_qasper_hf_to_subset.py --split train --max-papers 2 --max-qas 3 --output data/qasper_train_tiny.json
```

## Main Commands

Run the locked final model:

```bash
python scripts/run_qasper_final_model.py --qasper-path data/qasper_subset_debug_50.json
```

Run the main four-way baseline comparison:

```bash
python scripts/run_qasper_baseline_compare.py --qasper-path data/qasper_subset_debug_50.json
```

Run the one-shot canonical 50-paper bundle that writes both public artifact sets:

```bash
python scripts/run_qasper_eval_bundle.py --qasper-path data/qasper_subset_debug_50.json --max-papers 50 --max-qas 10000 --tag final_qasper_50paper_recomputed
```

Run the targeted 50-paper segmentation robustness study:

```bash
python scripts/run_qasper_segmentation_study.py
```

The segmentation study winner for the planned full-QASPER run is `seg_paragraph_pair`.

Run optional diagnostics:

```bash
python scripts/run_qasper_diagnostics.py --study streamlined
```

Legacy v2.1 component sweep:

```bash
python scripts/run_qasper_diagnostics.py --study legacy_v21
```

## Scripts And Repo Layout

Canonical scripts:

- `scripts/run_qasper_final_model.py`: single clean entry point for the locked final model
- `scripts/run_qasper_baseline_compare.py`: adjacency vs bridge_v1 vs bridge_v2 vs bridge_final
- `scripts/run_qasper_diagnostics.py`: optional dispatcher for non-canonical studies

Useful legacy or exploratory scripts kept for reproducibility:

- `scripts/run_bridge_v2_doc_constrained_sweep.py`
- `scripts/run_bridge_v21_doc_constrained_sweep.py`
- `scripts/run_bridge_streamlined_section_study.py`
- `scripts/run_doc_constrained_sweep.py`

Key library files:

- [src/lspbe/qasper.py](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/src/lspbe/qasper.py): named QASPER method registry and locked final config
- [src/lspbe/qasper_eval.py](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/src/lspbe/qasper_eval.py): shared evaluation helpers for the new runners
- [src/lspbe/expansion.py](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/src/lspbe/expansion.py): expansion logic including the locked `bridge_final` helper

## Final Artifacts

The locked final summary lives in:

- [artifacts/final_qasper_model_summary.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/final_qasper_model_summary.md)
- [artifacts/final_qasper_model_results.json](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/final_qasper_model_results.json)
- [artifacts/final_qasper_model_summary_recomputed.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/final_qasper_model_summary_recomputed.md)
- [artifacts/final_qasper_baseline_compare_recomputed.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/final_qasper_baseline_compare_recomputed.md)
- [artifacts/final_verification_note.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/final_verification_note.md)
- [artifacts/qasper_segmentation_study_50_summary.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/qasper_segmentation_study_50_summary.md)

For the full-QASPER final run path, use:

```bash
python scripts/run_qasper_full_final_eval.py --qasper-path data/qasper_train_full.json --segmentation-mode seg_paragraph_pair
```

The exact full-run plan is documented in [docs/final_full_qasper_run_plan.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/docs/final_full_qasper_run_plan.md).
