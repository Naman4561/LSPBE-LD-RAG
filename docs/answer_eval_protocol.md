# Answer Eval Protocol

Answer evaluation in this repo is a fixed secondary layer on top of the cleaned QASPER retrieval protocol. Its job is to check whether retrieval differences still point in the same direction once a single answerer is applied to the retrieved context. It is useful for diagnosis and communication, but it is not the main model-selection criterion.

## Purpose

- keep the retrieval comparison scientifically primary
- apply one fixed answer layer across compared retrieval methods
- measure whether better evidence recovery also tends to support better answer behavior
- preserve a method-comparable answer readout without turning answer noise into the selector

## Relation To The Cleaned Split Protocol

The retrieval protocol is the main story of the serious-redo project:

- `validation` is the model-selection split
- `test` is reserved for final held-out reporting
- `train_fast50` is a smoke/debug convenience slice, not headline evidence

Answer evaluation was added after the split cleanup and stayed subordinate to it. Bucket 2 introduced the answer-eval layer, Bucket 4 used retrieval-first validation ranking to choose finalists, and Bucket 5 kept answer metrics as supporting evidence in the final held-out comparison.

## Canonical Runner

Use the current categorized runner:

```bash
python scripts/final/run_qasper_answer_eval.py \
  --dataset-path data/qasper_validation_full.json \
  --split validation \
  --methods adjacency,bridge_final \
  --output-dir artifacts/current/bucket2_answer_eval \
  --cache-dir artifacts/support/cache/bucket2_answer_eval \
  --cache-tag validation_main
```

Common operational flags:

- `--max-questions` for bounded smoke runs
- `--start-index` and `--chunk-size` for chunked recovery
- `--save-every` for checkpoint frequency
- `--resume` to reuse cached per-question state
- `--overwrite` only when intentionally resetting an existing cache tag
- `--json-out`, `--md-out`, and `--csv-out` if you need explicit output filenames

## Supported Metrics

Required answer metrics:

- exact match
- token F1

Additional diagnostics:

- yes/no accuracy on yes/no gold questions
- empty prediction rate
- prediction length behavior in the per-question records
- retrieval evidence hit rate carried alongside the answer metrics

Subset reporting is preserved for:

- `adjacency_easy`
- `skip_local`
- `multi_span`
- `float_table`
- `question_type`

Treat `float_table` as a coarse label rather than a perfectly precise category.

## Answerer And Fallback Behavior

The repo no longer needs to be described as a deterministic-fallback-only project state. The active runner supports:

- `auto`
- `deterministic_extractive`
- `local_qa`

In practice, the answer layer is still deliberately fixed per comparison. When a usable offline QA model is available in the active environment, `local_qa` can be used; otherwise the runner falls back to deterministic extraction from the retrieved context. That fallback behavior is historical context for why answer evaluation stayed conservative, not the defining story of the final repo.

## Why Answer Eval Stayed Secondary

Answer evaluation remained secondary throughout the final project state because:

- retrieval metrics map more directly to the long-document evidence-recovery problem
- retrieval failures are easier to interpret than answer-generation failures
- answer quality still depends on a comparatively weak local answer layer
- empty or brittle answer behavior can obscure real retrieval differences

The final selected model therefore remains `flat_hybrid_current` based on retrieval-first evidence from validation and held-out test, with answer evaluation acting as supporting confirmation rather than the selection rule.

## Outputs And Locations

Current answer-eval outputs live in:

- `artifacts/current/bucket2_answer_eval/` for canonical saved reports
- `artifacts/support/cache/bucket2_answer_eval/` for resumable per-method caches

The runner writes:

- a main JSON payload
- a Markdown summary
- a per-question CSV
- a run manifest
- resumable cache records under the selected cache tag

## Final Interpretation

Use answer evaluation to answer a narrow question: given a locked retrieval comparison and one fixed answerer, do answer-level metrics broadly support the same conclusion? In this repo, they did not overturn the retrieval-first story, so answer evaluation remains an informative secondary layer rather than the project's main decision surface.
