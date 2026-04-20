# QASPER Answer Eval Smoke (train_fast50)

- split: `train`
- dataset_path: `data/qasper_train_fast50.json`
- segmentation_mode: `seg_paragraph_pair`
- questions: `5`
- answerer: `deterministic_extractive`
- answerer_note: No practical cached offline QA/generation model was available; Bucket 2 freezes a deterministic fallback.
- subset_counts: `{"adjacency_easy": 4, "boolean": 1, "float_table": 4, "how": 1, "multi_span": 1, "other": 0, "skip_local": 1, "what": 3, "which": 0}`

## Overall

### adjacency

- exact_match: `0.0000`
- token_f1: `0.1901`
- retrieval_evidence_hit_rate: `1.0000`
- empty_prediction_rate: `0.0000`
- yes_no_accuracy: `n/a`

### bridge_final

- exact_match: `0.0000`
- token_f1: `0.2020`
- retrieval_evidence_hit_rate: `1.0000`
- empty_prediction_rate: `0.0000`
- yes_no_accuracy: `n/a`

## Subsets

- `float_table` is preserved here as a coarse subset label only; do not treat it as a perfectly precise category.

### adjacency_easy

- `adjacency`: questions `4`, EM `0.0000`, F1 `0.2376`, retrieval-hit `1.0000`
- `bridge_final`: questions `4`, EM `0.0000`, F1 `0.2376`, retrieval-hit `1.0000`

### skip_local

- `adjacency`: questions `1`, EM `0.0000`, F1 `0.0000`, retrieval-hit `1.0000`
- `bridge_final`: questions `1`, EM `0.0000`, F1 `0.0597`, retrieval-hit `1.0000`

### multi_span

- `adjacency`: questions `1`, EM `0.0000`, F1 `0.0000`, retrieval-hit `1.0000`
- `bridge_final`: questions `1`, EM `0.0000`, F1 `0.0597`, retrieval-hit `1.0000`

### float_table

- `adjacency`: questions `4`, EM `0.0000`, F1 `0.2376`, retrieval-hit `1.0000`
- `bridge_final`: questions `4`, EM `0.0000`, F1 `0.2525`, retrieval-hit `1.0000`

## Question Types

### boolean

- `adjacency`: questions `1`, EM `0.0000`, F1 `0.0000`
- `bridge_final`: questions `1`, EM `0.0000`, F1 `0.0000`

### what

- `adjacency`: questions `3`, EM `0.0000`, F1 `0.0000`
- `bridge_final`: questions `3`, EM `0.0000`, F1 `0.0199`

### how

- `adjacency`: questions `1`, EM `0.0000`, F1 `0.9505`
- `bridge_final`: questions `1`, EM `0.0000`, F1 `0.9505`

### which

- `adjacency`: questions `0`, EM `0.0000`, F1 `0.0000`
- `bridge_final`: questions `0`, EM `0.0000`, F1 `0.0000`

### other

- `adjacency`: questions `0`, EM `0.0000`, F1 `0.0000`
- `bridge_final`: questions `0`, EM `0.0000`, F1 `0.0000`
