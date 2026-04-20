# QASPER Answer Eval

- split: `validation`
- dataset_path: `data/qasper_validation_full.json`
- segmentation_mode: `seg_paragraph_pair`
- questions: `1005`
- total_questions_available: `1005`
- start_index: `0`
- end_index: `1005`
- answerer: `local_qa`
- answerer_note: Offline QA model 'distilbert-base-cased-distilled-squad' loaded successfully from the local Hugging Face cache.
- subset_counts: `{"adjacency_easy": 698, "boolean": 145, "float_table": 616, "how": 193, "multi_span": 172, "other": 60, "skip_local": 202, "what": 506, "which": 101}`

## Overall

### adjacency

- exact_match: `0.1403`
- token_f1: `0.1675`
- retrieval_evidence_hit_rate: `0.8517`
- empty_prediction_rate: `0.4567`
- yes_no_accuracy: `0.5588`

### bridge_final

- exact_match: `0.1353`
- token_f1: `0.1619`
- retrieval_evidence_hit_rate: `0.8796`
- empty_prediction_rate: `0.4478`
- yes_no_accuracy: `0.5392`

## Subsets

- `float_table` is preserved here as a coarse subset label only; do not treat it as a perfectly precise category.

### adjacency_easy

- `adjacency`: questions `698`, EM `0.1103`, F1 `0.1406`, retrieval-hit `0.9556`
- `bridge_final`: questions `698`, EM `0.1074`, F1 `0.1377`, retrieval-hit `0.9957`

### skip_local

- `adjacency`: questions `202`, EM `0.0792`, F1 `0.1118`, retrieval-hit `0.9950`
- `bridge_final`: questions `202`, EM `0.0743`, F1 `0.1053`, retrieval-hit `0.9950`

### multi_span

- `adjacency`: questions `172`, EM `0.0930`, F1 `0.1264`, retrieval-hit `1.0000`
- `bridge_final`: questions `172`, EM `0.0872`, F1 `0.1175`, retrieval-hit `1.0000`

### float_table

- `adjacency`: questions `616`, EM `0.1088`, F1 `0.1305`, retrieval-hit `0.9334`
- `bridge_final`: questions `616`, EM `0.1023`, F1 `0.1245`, retrieval-hit `0.9448`

## Question Types

### boolean

- `adjacency`: questions `145`, EM `0.4897`, F1 `0.4924`
- `bridge_final`: questions `145`, EM `0.4690`, F1 `0.4717`

### what

- `adjacency`: questions `506`, EM `0.0830`, F1 `0.1080`
- `bridge_final`: questions `506`, EM `0.0771`, F1 `0.1048`

### how

- `adjacency`: questions `193`, EM `0.0829`, F1 `0.1178`
- `bridge_final`: questions `193`, EM `0.0829`, F1 `0.1115`

### which

- `adjacency`: questions `101`, EM `0.0495`, F1 `0.0925`
- `bridge_final`: questions `101`, EM `0.0495`, F1 `0.0841`

### other

- `adjacency`: questions `60`, EM `0.1167`, F1 `0.1703`
- `bridge_final`: questions `60`, EM `0.1333`, F1 `0.1885`

## Run Progress

- `adjacency`: completed `1005` / `1005`, computed_this_run `0`, skipped_existing `1005`
- `bridge_final`: completed `1005` / `1005`, computed_this_run `0`, skipped_existing `1005`
