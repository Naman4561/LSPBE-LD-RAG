# QASPER Test Answer Eval

- split: `test`
- dataset_path: `data/qasper_test_full.json`
- questions: `1451`
- answerer: `local_qa`
- answerer_note: Offline QA model 'distilbert-base-cased-distilled-squad' loaded successfully from the local Hugging Face cache.

## Overall

### flat_hybrid_current

- exact_match: `0.2074`
- token_f1: `0.3022`
- retrieval_evidence_hit_rate: `0.8890`
- empty_prediction_rate: `0.2419`
- yes_no_accuracy: `0.6495`

### bridge_final_current

- exact_match: `0.1992`
- token_f1: `0.2343`
- retrieval_evidence_hit_rate: `0.8739`
- empty_prediction_rate: `0.4431`
- yes_no_accuracy: `0.6495`

## Targeted Subsets

### skip_local

- `flat_hybrid_current`: questions `626`, EM `0.1981`, F1 `0.3013`, retrieval_hit `0.9904`
- `bridge_final_current`: questions `626`, EM `0.1789`, F1 `0.2261`, retrieval_hit `0.9840`

### multi_span

- `flat_hybrid_current`: questions `459`, EM `0.1983`, F1 `0.2971`, retrieval_hit `0.9891`
- `bridge_final_current`: questions `459`, EM `0.1808`, F1 `0.2248`, retrieval_hit `0.9891`

### float_table

- `flat_hybrid_current`: questions `808`, EM `0.1832`, F1 `0.2764`, retrieval_hit `0.9443`
- `bridge_final_current`: questions `808`, EM `0.1547`, F1 `0.1903`, retrieval_hit `0.9319`

## Interpretation

- Treat these answer metrics as secondary support only.
- The local offline QA layer is still imperfect, so retrieval remains the main Bucket 5 selection and reporting story.
