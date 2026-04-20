# Bucket 1 Protocol Reset Summary

## What Changed

Bucket 1 resets the QASPER evaluation foundation without changing the locked retrieval model.

The new protocol is:

- `train_fast50` for quick debugging
- `train_dev` for development and ablations
- `train_lockbox` for occasional milestone checks
- `validation` for model selection
- `test` for final reporting only

## Paper-Level Train Split Counts

- `train_dev`: `622` papers, `1817` questions
- `train_lockbox`: `266` papers, `776` questions
- `train_fast50`: `50` papers, `146` questions

No paper leakage was detected:

- `train_dev` vs `train_lockbox`: `0`
- `train_fast50` outside `train_dev`: `0`
- `train_fast50` vs `train_lockbox`: `0`

## Headline Retrieval Metrics

The serious redo now emphasizes:

- `evidence_hit_rate`
- `evidence_coverage_rate`
- `seed_hit_rate`
- `first_evidence_rank`

`Recall@k` and `MRR` remain in raw outputs for compatibility, but they are no longer the centerpiece of the serious-redo reporting story.

## Hard Subsets

Reusable method-independent subset labels now exist for:

- `adjacency_easy`
- `skip_local`
- `multi_span`
- `float_table`
- `question_type` with `boolean`, `what`, `how`, `which`, and `other`

## Canonical Files For Later Buckets

Use these as the new protocol defaults:

- `scripts/build_qasper_protocol_assets.py`
- `scripts/run_qasper_protocol_sanity_check.py`
- `docs/eval_protocol.md`
- `docs/retrieval_metrics.md`
- `docs/subset_definitions.md`
- `artifacts/qasper_split_protocol_summary.md`

## Still Deferred

Later buckets still need to handle:

- answer-generation evaluation
- EM / F1 style end-task metrics
- float-aware indexing improvements
- model selection on validation under the new protocol
- the final locked test run
