# QASPER Answer Eval (validation adjacency cache build)

- split: `validation`
- dataset_path: `data/qasper_validation_full.json`
- segmentation_mode: `seg_paragraph_pair`
- questions: `1005`
- answerer: `deterministic_extractive`
- answerer_note: No practical cached offline QA/generation model was available; Bucket 2 freezes a deterministic fallback.
- subset_counts: `{"adjacency_easy": 698, "boolean": 145, "float_table": 616, "how": 193, "multi_span": 172, "other": 60, "skip_local": 202, "what": 506, "which": 101}`

## Overall

### adjacency

- exact_match: `0.0726`
- token_f1: `0.1608`
- retrieval_evidence_hit_rate: `0.8517`
- empty_prediction_rate: `0.0000`
- yes_no_accuracy: `0.5588`

## Subsets

- `float_table` is preserved here as a coarse subset label only; do not treat it as a perfectly precise category.

### adjacency_easy

- `adjacency`: questions `698`, EM `0.0716`, F1 `0.1660`, retrieval-hit `0.9556`

### skip_local

- `adjacency`: questions `202`, EM `0.0644`, F1 `0.1752`, retrieval-hit `0.9950`

### multi_span

- `adjacency`: questions `172`, EM `0.0756`, F1 `0.1865`, retrieval-hit `1.0000`

### float_table

- `adjacency`: questions `616`, EM `0.0682`, F1 `0.1624`, retrieval-hit `0.9334`

## Question Types

### boolean

- `adjacency`: questions `145`, EM `0.4897`, F1 `0.4924`

### what

- `adjacency`: questions `506`, EM `0.0000`, F1 `0.0982`

### how

- `adjacency`: questions `193`, EM `0.0000`, F1 `0.1170`

### which

- `adjacency`: questions `101`, EM `0.0000`, F1 `0.0923`

### other

- `adjacency`: questions `60`, EM `0.0333`, F1 `0.1436`
