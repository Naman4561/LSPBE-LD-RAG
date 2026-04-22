# QASPER Model Selection Answer Eval

- split: `validation`
- dataset_path: `data\qasper_validation_full.json`
- questions: `20`
- answerer: `local_qa`
- answerer_note: Offline QA model 'distilbert-base-cased-distilled-squad' loaded successfully from the local Hugging Face cache.

## Overall

### fixed_chunk_bridge_final

- exact_match: `0.1000`
- token_f1: `0.1161`
- retrieval_evidence_hit_rate: `0.9500`
- empty_prediction_rate: `0.6000`
- yes_no_accuracy: `1.0000`

### flat_hybrid_current

- exact_match: `0.2000`
- token_f1: `0.3401`
- retrieval_evidence_hit_rate: `0.9000`
- empty_prediction_rate: `0.3500`
- yes_no_accuracy: `1.0000`

## Targeted Subsets

### skip_local

- `fixed_chunk_bridge_final`: questions `12`, EM `0.0833`, F1 `0.1013`, retrieval_hit `1.0000`
- `flat_hybrid_current`: questions `12`, EM `0.1667`, F1 `0.2358`, retrieval_hit `0.9167`

### multi_span

- `fixed_chunk_bridge_final`: questions `10`, EM `0.1000`, F1 `0.1216`, retrieval_hit `1.0000`
- `flat_hybrid_current`: questions `10`, EM `0.2000`, F1 `0.2258`, retrieval_hit `1.0000`

### float_table

- `fixed_chunk_bridge_final`: questions `15`, EM `0.0667`, F1 `0.0797`, retrieval_hit `0.9333`
- `flat_hybrid_current`: questions `15`, EM `0.1333`, F1 `0.2922`, retrieval_hit `0.8667`
