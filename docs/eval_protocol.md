# Evaluation Protocol

## Why The Protocol Changed

The earlier QASPER workflow mixed methodological roles too loosely:

- the original train split was used for development and then later shown again in the final story
- full-train headline reporting is no longer clean evidence after that reuse
- saturated retrieval metrics did not make the retrieval story easier to defend
- the old strongest hard-case slice was anchored to a method, not to the data itself

Bucket 1 resets that foundation without changing the locked retrieval model.

## Split Roles

Going forward, use these roles:

- `train_fast50`: quick debugging only
- `train_dev`: engineering work, ablations, and intermediate experiments
- `train_lockbox`: occasional milestone checks only
- `validation`: model selection
- `test`: final reporting only

The train split redesign is paper-level. A paper never appears in more than one train-side split.

## What Is Forbidden

`train_fast50`
- no headline claims
- no final method comparison tables
- no test-like reporting language

`train_dev`
- no final claims about generalization
- no using it as the sole headline evidence in the serious redo

`train_lockbox`
- do not iterate on it repeatedly
- do not tune to it after every small change
- reserve it for milestone checks when `train_dev` trends look stable

`validation`
- use for model selection only
- do not report it as the final outcome after adapting to it repeatedly

`test`
- no iterative development
- no peeking during tuning
- use only for the final serious-redo report

## New Default Workflow

1. debug on `train_fast50`
2. develop on `train_dev`
3. sanity-check major milestones on `train_lockbox`
4. choose the final retrieval configuration on `validation`
5. report the final result once on `test`

## Legacy Context

The repo still contains old all-splits train/validation/test artifacts and runners because they are part of the project history. Treat them as legacy pre-redo context, not as the new gold-standard protocol.

Examples:

- `artifacts/legacy_pre_redo/final_locked_qasper/final_qasper_model_summary.md`
- `artifacts/legacy_pre_redo/final_locked_qasper/final_qasper_all_splits_summary.md`
- `scripts/legacy/run_qasper_eval_bundle.py`
- `scripts/legacy/run_qasper_full_final_eval.py`
- `scripts/legacy/run_qasper_all_splits_final_eval.py`

## Fixed Settings In Bucket 1

Bucket 1 does not redesign retrieval. The locked model stays:

- segmentation `seg_paragraph_pair`
- hybrid seeds with dense `1.00` and sparse `0.50`
- Bridge v2 skip-local expansion
- continuity `idf_overlap`
- no section scoring, adaptive trigger, reranker, or diversification
