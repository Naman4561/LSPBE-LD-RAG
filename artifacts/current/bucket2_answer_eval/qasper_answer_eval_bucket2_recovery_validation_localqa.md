# QASPER Answer Eval

- split: `validation`
- dataset_path: `data/qasper_validation_full.json`
- segmentation_mode: `seg_paragraph_pair`
- questions: `5`
- total_questions_available: `1005`
- start_index: `1000`
- end_index: `1005`
- answerer: `local_qa`
- answerer_note: Offline QA model 'distilbert-base-cased-distilled-squad' loaded successfully from the local Hugging Face cache.
- subset_counts: `{"adjacency_easy": 1, "boolean": 1, "float_table": 2, "how": 0, "multi_span": 1, "other": 0, "skip_local": 1, "what": 4, "which": 0}`

## Overall

### adjacency

- exact_match: `0.2000`
- token_f1: `0.2063`
- retrieval_evidence_hit_rate: `0.4000`
- empty_prediction_rate: `0.2000`
- yes_no_accuracy: `0.0000`

### bridge_final

- exact_match: `0.2000`
- token_f1: `0.2063`
- retrieval_evidence_hit_rate: `0.4000`
- empty_prediction_rate: `0.2000`
- yes_no_accuracy: `0.0000`

## Subsets

- `float_table` is preserved here as a coarse subset label only; do not treat it as a perfectly precise category.

### adjacency_easy

- `adjacency`: questions `1`, EM `0.0000`, F1 `0.0000`, retrieval-hit `1.0000`
- `bridge_final`: questions `1`, EM `0.0000`, F1 `0.0000`, retrieval-hit `1.0000`

### skip_local

- `adjacency`: questions `1`, EM `0.0000`, F1 `0.0317`, retrieval-hit `1.0000`
- `bridge_final`: questions `1`, EM `0.0000`, F1 `0.0317`, retrieval-hit `1.0000`

### multi_span

- `adjacency`: questions `1`, EM `0.0000`, F1 `0.0317`, retrieval-hit `1.0000`
- `bridge_final`: questions `1`, EM `0.0000`, F1 `0.0317`, retrieval-hit `1.0000`

### float_table

- `adjacency`: questions `2`, EM `0.0000`, F1 `0.0159`, retrieval-hit `1.0000`
- `bridge_final`: questions `2`, EM `0.0000`, F1 `0.0159`, retrieval-hit `1.0000`

## Question Types

### boolean

- `adjacency`: questions `1`, EM `0.0000`, F1 `0.0000`
- `bridge_final`: questions `1`, EM `0.0000`, F1 `0.0000`

### what

- `adjacency`: questions `4`, EM `0.2500`, F1 `0.2579`
- `bridge_final`: questions `4`, EM `0.2500`, F1 `0.2579`

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

- `adjacency`: completed `5` / `5`, computed_this_run `5`, skipped_existing `0`
- `bridge_final`: completed `5` / `5`, computed_this_run `5`, skipped_existing `0`
