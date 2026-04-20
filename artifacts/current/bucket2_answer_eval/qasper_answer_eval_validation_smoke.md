# QASPER Answer Eval (validation smoke)

- split: `validation`
- dataset_path: `data/qasper_validation_full.json`
- segmentation_mode: `seg_paragraph_pair`
- questions: `150`
- answerer: `deterministic_extractive`
- answerer_note: No practical cached offline QA/generation model was available; Bucket 2 freezes a deterministic fallback.
- subset_counts: `{"adjacency_easy": 92, "boolean": 25, "float_table": 115, "how": 23, "multi_span": 43, "other": 12, "skip_local": 49, "what": 71, "which": 19}`

## Overall

### adjacency

- exact_match: `0.1200`
- token_f1: `0.2055`
- retrieval_evidence_hit_rate: `0.8733`
- empty_prediction_rate: `0.0000`
- yes_no_accuracy: `0.8333`

### bridge_final

- exact_match: `0.1133`
- token_f1: `0.1940`
- retrieval_evidence_hit_rate: `0.9133`
- empty_prediction_rate: `0.0000`
- yes_no_accuracy: `0.7778`

## Subsets

- `float_table` is preserved here as a coarse subset label only; do not treat it as a perfectly precise category.

### adjacency_easy

- `adjacency`: questions `92`, EM `0.1196`, F1 `0.2154`, retrieval-hit `0.9239`
- `bridge_final`: questions `92`, EM `0.1196`, F1 `0.2074`, retrieval-hit `0.9891`

### skip_local

- `adjacency`: questions `49`, EM `0.1224`, F1 `0.2091`, retrieval-hit `0.9796`
- `bridge_final`: questions `49`, EM `0.1020`, F1 `0.1889`, retrieval-hit `0.9796`

### multi_span

- `adjacency`: questions `43`, EM `0.1395`, F1 `0.2261`, retrieval-hit `1.0000`
- `bridge_final`: questions `43`, EM `0.1163`, F1 `0.2031`, retrieval-hit `1.0000`

### float_table

- `adjacency`: questions `115`, EM `0.1043`, F1 `0.1984`, retrieval-hit `0.9217`
- `bridge_final`: questions `115`, EM `0.0957`, F1 `0.1875`, retrieval-hit `0.9652`

## Question Types

### boolean

- `adjacency`: questions `25`, EM `0.7200`, F1 `0.7200`
- `bridge_final`: questions `25`, EM `0.6800`, F1 `0.6800`

### what

- `adjacency`: questions `71`, EM `0.0000`, F1 `0.0876`
- `bridge_final`: questions `71`, EM `0.0000`, F1 `0.0858`

### how

- `adjacency`: questions `23`, EM `0.0000`, F1 `0.1156`
- `bridge_final`: questions `23`, EM `0.0000`, F1 `0.0927`

### which

- `adjacency`: questions `19`, EM `0.0000`, F1 `0.1063`
- `bridge_final`: questions `19`, EM `0.0000`, F1 `0.1011`

### other

- `adjacency`: questions `12`, EM `0.0000`, F1 `0.1606`
- `bridge_final`: questions `12`, EM `0.0000`, F1 `0.1624`
