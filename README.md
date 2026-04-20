# LSPBE-LD-RAG

Lightweight long-document retrieval for QASPER using local bridge expansion.

The repo keeps the locked `bridge_final` retrieval model, but the serious QASPER redo now uses a new protocol layer on top of it:

- paper-level train split redesign
- method-independent hard subsets
- retrieval-side headline metrics centered on evidence recovery and coverage
- explicit split roles for development, lockbox checks, validation, and final test reporting

## Start Here

Read these first for the serious redo path:

- [docs/eval_protocol.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/docs/eval_protocol.md)
- [docs/retrieval_metrics.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/docs/retrieval_metrics.md)
- [docs/subset_definitions.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/docs/subset_definitions.md)
- [artifacts/ARTIFACTS_MAP.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/ARTIFACTS_MAP.md)
- [bucket1_protocol_reset_summary.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/current/bucket1_protocol/bucket1_protocol_reset_summary.md)

## Serious Redo Protocol

Use these split roles going forward:

- `train_fast50`: quick debugging only
- `train_dev`: development and ablations
- `train_lockbox`: occasional milestone checks only
- `validation`: model selection
- `test`: final reporting only

The train split is now materialized at:

- `data/qasper_train_dev.json`
- `data/qasper_train_lockbox.json`
- `data/qasper_train_fast50.json`

The paper manifests live at:

- `data/splits/train_dev_papers.json`
- `data/splits/train_lockbox_papers.json`
- `data/splits/train_fast50_papers.json`

## Canonical Model

The retrieval model itself is unchanged in Bucket 1.

Locked QASPER configuration:

- segmentation `seg_paragraph_pair`
- hybrid seed retrieval
- dense weight `1.00`
- sparse weight `0.50`
- Bridge v2 skip-local expansion
- continuity `idf_overlap`
- no section scoring
- no adaptive trigger
- no reranker
- no diversification

## Main Commands

Build the split manifests, materialized train subsets, and cached subset labels:

```bash
python scripts/build_qasper_protocol_assets.py
```

Run the canonical serious-redo sanity check on `train_fast50`:

```bash
python scripts/run_qasper_protocol_sanity_check.py
```

Optionally add validation to the sanity pass:

```bash
python scripts/run_qasper_protocol_sanity_check.py --also-validation
```

Active serious-redo outputs now live under:

- `artifacts/current/bucket1_protocol/`
- `artifacts/current/manual_review/`
- `artifacts/current/bucket2_answer_eval/`

## Legacy Context

The repo still preserves the earlier pre-redo artifacts and runners for reproducibility, including the old all-splits full-train reporting story. Those results remain useful context, but they are no longer the gold-standard evaluation path for the serious redo.

Legacy examples:

- [final_qasper_model_summary.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/legacy_pre_redo/final_locked_qasper/final_qasper_model_summary.md)
- [final_qasper_all_splits_summary.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/legacy_pre_redo/final_locked_qasper/final_qasper_all_splits_summary.md)
- `scripts/run_qasper_eval_bundle.py`
- `scripts/run_qasper_full_final_eval.py`
- `scripts/run_qasper_all_splits_final_eval.py`

## Repo Layout

Key protocol files:

- [src/lspbe/qasper_protocol.py](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/src/lspbe/qasper_protocol.py)
- [src/lspbe/subsets.py](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/src/lspbe/subsets.py)
- [src/lspbe/qasper_eval.py](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/src/lspbe/qasper_eval.py)

Key model/config files:

- [src/lspbe/qasper.py](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/src/lspbe/qasper.py)
- [docs/algorithm_spec.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/docs/algorithm_spec.md)
