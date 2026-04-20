# QASPER Answer Eval (train_fast50)

- split: `train`
- dataset_path: `data/qasper_train_fast50.json`
- segmentation_mode: `seg_paragraph_pair`
- questions: `146`
- answerer: `deterministic_extractive`
- answerer_note: No practical cached offline QA/generation model was available; Bucket 2 freezes a deterministic fallback.
- subset_counts: `{"adjacency_easy": 100, "boolean": 27, "float_table": 74, "how": 36, "multi_span": 12, "other": 8, "skip_local": 17, "what": 62, "which": 13}`

## Overall

### adjacency

- exact_match: `0.0685`
- token_f1: `0.1383`
- retrieval_evidence_hit_rate: `0.7466`
- empty_prediction_rate: `0.0000`
- yes_no_accuracy: `0.4762`

### bridge_final

- exact_match: `0.0616`
- token_f1: `0.1312`
- retrieval_evidence_hit_rate: `0.7740`
- empty_prediction_rate: `0.0000`
- yes_no_accuracy: `0.4286`

## Subsets

- `float_table` is preserved here as a coarse subset label only; do not treat it as a perfectly precise category.

### adjacency_easy

- `adjacency`: questions `100`, EM `0.0900`, F1 `0.1684`, retrieval-hit `0.9500`
- `bridge_final`: questions `100`, EM `0.0800`, F1 `0.1572`, retrieval-hit `0.9800`

### skip_local

- `adjacency`: questions `17`, EM `0.0000`, F1 `0.1309`, retrieval-hit `0.9412`
- `bridge_final`: questions `17`, EM `0.0000`, F1 `0.1311`, retrieval-hit `1.0000`

### multi_span

- `adjacency`: questions `12`, EM `0.0000`, F1 `0.1698`, retrieval-hit `0.9167`
- `bridge_final`: questions `12`, EM `0.0000`, F1 `0.1747`, retrieval-hit `1.0000`

### float_table

- `adjacency`: questions `74`, EM `0.0676`, F1 `0.1684`, retrieval-hit `0.9189`
- `bridge_final`: questions `74`, EM `0.0541`, F1 `0.1551`, retrieval-hit `0.9324`

## Question Types

### boolean

- `adjacency`: questions `27`, EM `0.3704`, F1 `0.3704`
- `bridge_final`: questions `27`, EM `0.3333`, F1 `0.3333`

### what

- `adjacency`: questions `62`, EM `0.0000`, F1 `0.0633`
- `bridge_final`: questions `62`, EM `0.0000`, F1 `0.0640`

### how

- `adjacency`: questions `36`, EM `0.0000`, F1 `0.1408`
- `bridge_final`: questions `36`, EM `0.0000`, F1 `0.1359`

### which

- `adjacency`: questions `13`, EM `0.0000`, F1 `0.0415`
- `bridge_final`: questions `13`, EM `0.0000`, F1 `0.0419`

### other

- `adjacency`: questions `8`, EM `0.0000`, F1 `0.0823`
- `bridge_final`: questions `8`, EM `0.0000`, F1 `0.0932`
