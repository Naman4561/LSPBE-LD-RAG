# QASPER Model Selection Answer Eval

- split: `validation`
- dataset_path: `data/qasper_validation_full.json`
- questions: `1005`
- answerer: `local_qa`
- answerer_note: Offline QA model 'distilbert-base-cased-distilled-squad' loaded successfully from the local Hugging Face cache.

## Overall

### flat_hybrid_current

- exact_match: `0.1682`
- token_f1: `0.2503`
- retrieval_evidence_hit_rate: `0.8617`
- empty_prediction_rate: `0.2697`
- yes_no_accuracy: `0.5490`

### bridge_final_current

- exact_match: `0.1343`
- token_f1: `0.1659`
- retrieval_evidence_hit_rate: `0.8438`
- empty_prediction_rate: `0.4627`
- yes_no_accuracy: `0.5392`

## Targeted Subsets

### skip_local

- `flat_hybrid_current`: questions `325`, EM `0.1231`, F1 `0.2261`, retrieval_hit `0.9846`
- `bridge_final_current`: questions `325`, EM `0.0677`, F1 `0.1081`, retrieval_hit `0.9723`

### multi_span

- `flat_hybrid_current`: questions `231`, EM `0.1299`, F1 `0.2400`, retrieval_hit `0.9913`
- `bridge_final_current`: questions `231`, EM `0.0693`, F1 `0.1077`, retrieval_hit `0.9870`

### float_table

- `flat_hybrid_current`: questions `553`, EM `0.1465`, F1 `0.2381`, retrieval_hit `0.9277`
- `bridge_final_current`: questions `553`, EM `0.1121`, F1 `0.1439`, retrieval_hit `0.9078`
