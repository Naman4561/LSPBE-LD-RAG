# Qasper Bridge Repair Stage1 Validation

- stage: `stage1 full validation retrieval`
- dataset_path: `data/qasper_validation_full.json`
- questions: `1005`
- papers: `281`
- main_representation: `current`
- main_segmentation: `seg_paragraph_pair`
- subset_counts: `{"adjacency_easy": 611, "boolean": 145, "float_table": 553, "how": 193, "multi_span": 231, "other": 60, "skip_local": 325, "what": 506, "which": 101}`

## Overall

### bridge_from_flat_seeds_current

- evidence_hit_rate: `0.8418`
- evidence_coverage_rate: `0.7647`
- seed_hit_rate: `0.8617`
- first_evidence_rank: `4.1824`

## Targeted Subsets

### skip_local

- `bridge_from_flat_seeds_current`: questions `325`, hit `0.9877`, coverage `0.8495`, seed_hit `0.9846`, first_rank `3.5344`

### multi_span

- `bridge_from_flat_seeds_current`: questions `231`, hit `0.9913`, coverage `0.8343`, seed_hit `0.9913`, first_rank `3.4629`

### float_table

- `bridge_from_flat_seeds_current`: questions `553`, hit `0.9096`, coverage `0.7931`, seed_hit `0.9277`, first_rank `4.0370`

## Question Types

### boolean

- `bridge_from_flat_seeds_current`: questions `145`, hit `0.7103`, coverage `0.6447`, seed_hit `0.6966`, first_rank `5.0990`

### what

- `bridge_from_flat_seeds_current`: questions `506`, hit `0.8636`, coverage `0.7784`, seed_hit `0.8814`, first_rank `4.0157`

### how

- `bridge_from_flat_seeds_current`: questions `193`, hit `0.8653`, coverage `0.7973`, seed_hit `0.9067`, first_rank `4.1314`

### which

- `bridge_from_flat_seeds_current`: questions `101`, hit `0.8812`, coverage `0.7988`, seed_hit `0.9010`, first_rank `3.9451`

### other

- `bridge_from_flat_seeds_current`: questions `60`, hit `0.8333`, coverage `0.7772`, seed_hit `0.8833`, first_rank `4.4151`

## Baseline Reference

- source: `artifacts/current/bucket4_model_selection/qasper_model_selection_validation.json`
- `flat_hybrid_current`: hit `0.8617`, coverage `0.7833`, seed_hit `0.8617`, first_rank `4.1813`
- `bridge_final_current`: hit `0.8438`, coverage `0.7567`, seed_hit `0.7741`, first_rank `3.0707`
