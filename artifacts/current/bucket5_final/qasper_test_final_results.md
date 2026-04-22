# QASPER Test Final Results

- stage: `final held-out retrieval`
- dataset_path: `data/qasper_test_full.json`
- questions: `1451`
- papers: `416`
- main_representation: `current`
- main_segmentation: `seg_paragraph_pair`
- subset_counts: `{"adjacency_easy": 764, "boolean": 247, "float_table": 808, "how": 294, "multi_span": 459, "other": 72, "skip_local": 626, "what": 689, "which": 149}`

## Overall

### flat_hybrid_current

- evidence_hit_rate: `0.8890`
- evidence_coverage_rate: `0.7862`
- seed_hit_rate: `0.8890`
- first_evidence_rank: `3.7868`

### bridge_final_current

- evidence_hit_rate: `0.8739`
- evidence_coverage_rate: `0.7690`
- seed_hit_rate: `0.8119`
- first_evidence_rank: `2.7810`

## Targeted Subsets

### skip_local

- `flat_hybrid_current`: questions `626`, hit `0.9904`, coverage `0.8456`, seed_hit `0.9904`, first_rank `3.5387`
- `bridge_final_current`: questions `626`, hit `0.9840`, coverage `0.8302`, seed_hit `0.9185`, first_rank `2.6939`

### multi_span

- `flat_hybrid_current`: questions `459`, hit `0.9891`, coverage `0.8418`, seed_hit `0.9891`, first_rank `3.4648`
- `bridge_final_current`: questions `459`, hit `0.9891`, coverage `0.8220`, seed_hit `0.9216`, first_rank `2.7045`

### float_table

- `flat_hybrid_current`: questions `808`, hit `0.9443`, coverage `0.7967`, seed_hit `0.9443`, first_rank `3.5452`
- `bridge_final_current`: questions `808`, hit `0.9319`, coverage `0.7822`, seed_hit `0.8738`, first_rank `2.6813`

## Question Types

### boolean

- `flat_hybrid_current`: questions `247`, hit `0.8462`, coverage `0.7645`, seed_hit `0.8462`, first_rank `4.1148`
- `bridge_final_current`: questions `247`, hit `0.8178`, coverage `0.7278`, seed_hit `0.7530`, first_rank `2.8495`

### what

- `flat_hybrid_current`: questions `689`, hit `0.9129`, coverage `0.7978`, seed_hit `0.9129`, first_rank `3.8347`
- `bridge_final_current`: questions `689`, hit `0.9028`, coverage `0.7822`, seed_hit `0.8389`, first_rank `2.8893`

### how

- `flat_hybrid_current`: questions `294`, hit `0.8503`, coverage `0.7615`, seed_hit `0.8503`, first_rank `3.8320`
- `bridge_final_current`: questions `294`, hit `0.8299`, coverage `0.7313`, seed_hit `0.7619`, first_rank `2.6607`

### which

- `flat_hybrid_current`: questions `149`, hit `0.9396`, coverage `0.8404`, seed_hit `0.9396`, first_rank `3.3071`
- `bridge_final_current`: questions `149`, hit `0.9329`, coverage `0.8589`, seed_hit `0.8792`, first_rank `2.5191`

### other

- `flat_hybrid_current`: questions `72`, hit `0.8611`, coverage `0.7388`, seed_hit `0.8611`, first_rank `3.0968`
- `bridge_final_current`: questions `72`, hit `0.8472`, coverage `0.7516`, seed_hit `0.8194`, first_rank `2.5424`

## Lock Status

- locked_final_model: `flat_hybrid_current`
- comparison_baseline: `bridge_final_current`
- note: Bucket 5 does not reopen model selection; it only reports the held-out result for the locked model plus one compact baseline.
