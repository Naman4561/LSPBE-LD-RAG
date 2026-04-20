# Bucket E Resume Proof Step 1

- split: `train`
- dataset_path: `data/qasper_train_fast50.json`
- segmentation_mode: `seg_paragraph_pair`
- questions: `2`
- total_questions_available: `5`
- start_index: `0`
- end_index: `2`
- answerer: `deterministic_extractive`
- answerer_note: No practical cached offline QA/generation model was available; Bucket 2 freezes a deterministic fallback.
- subset_counts: `{"adjacency_easy": 2, "boolean": 0, "float_table": 1, "how": 0, "multi_span": 0, "other": 0, "skip_local": 0, "what": 2, "which": 0}`

## Overall

### adjacency

- exact_match: `0.0000`
- token_f1: `0.0000`
- retrieval_evidence_hit_rate: `1.0000`
- empty_prediction_rate: `0.0000`
- yes_no_accuracy: `n/a`

### bridge_final

- exact_match: `0.0000`
- token_f1: `0.0000`
- retrieval_evidence_hit_rate: `1.0000`
- empty_prediction_rate: `0.0000`
- yes_no_accuracy: `n/a`

## Subsets

- `float_table` is preserved here as a coarse subset label only; do not treat it as a perfectly precise category.

### adjacency_easy

- `adjacency`: questions `2`, EM `0.0000`, F1 `0.0000`, retrieval-hit `1.0000`
- `bridge_final`: questions `2`, EM `0.0000`, F1 `0.0000`, retrieval-hit `1.0000`

### skip_local

- `adjacency`: questions `0`, EM `0.0000`, F1 `0.0000`, retrieval-hit `0.0000`
- `bridge_final`: questions `0`, EM `0.0000`, F1 `0.0000`, retrieval-hit `0.0000`

### multi_span

- `adjacency`: questions `0`, EM `0.0000`, F1 `0.0000`, retrieval-hit `0.0000`
- `bridge_final`: questions `0`, EM `0.0000`, F1 `0.0000`, retrieval-hit `0.0000`

### float_table

- `adjacency`: questions `1`, EM `0.0000`, F1 `0.0000`, retrieval-hit `1.0000`
- `bridge_final`: questions `1`, EM `0.0000`, F1 `0.0000`, retrieval-hit `1.0000`

## Question Types

### boolean

- `adjacency`: questions `0`, EM `0.0000`, F1 `0.0000`
- `bridge_final`: questions `0`, EM `0.0000`, F1 `0.0000`

### what

- `adjacency`: questions `2`, EM `0.0000`, F1 `0.0000`
- `bridge_final`: questions `2`, EM `0.0000`, F1 `0.0000`

### how

- `adjacency`: questions `0`, EM `0.0000`, F1 `0.0000`
- `bridge_final`: questions `0`, EM `0.0000`, F1 `0.0000`

### which

- `adjacency`: questions `0`, EM `0.0000`, F1 `0.0000`
- `bridge_final`: questions `0`, EM `0.0000`, F1 `0.0000`

### other

- `adjacency`: questions `0`, EM `0.0000`, F1 `0.0000`
- `bridge_final`: questions `0`, EM `0.0000`, F1 `0.0000`

## Run Progress

- `adjacency`: completed `2` / `2`, computed_this_run `2`, skipped_existing `0`
- `bridge_final`: completed `2` / `2`, computed_this_run `2`, skipped_existing `0`
