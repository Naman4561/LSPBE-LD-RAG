# Qasper Bridge Repair Stage2 Smoke

- stage: `stage2 smoke retrieval`
- dataset_path: `data/qasper_train_fast50.json`
- questions: `146`
- papers: `50`
- main_representation: `current`
- main_segmentation: `seg_paragraph_pair`
- subset_counts: `{"adjacency_easy": 90, "boolean": 27, "float_table": 67, "how": 36, "multi_span": 17, "other": 8, "skip_local": 28, "what": 62, "which": 13}`

## Overall

### bridge_from_flat_seeds_selective_current

- evidence_hit_rate: `0.6849`
- evidence_coverage_rate: `0.6365`
- seed_hit_rate: `0.7260`
- first_evidence_rank: `5.0660`

## Targeted Subsets

### skip_local

- `bridge_from_flat_seeds_selective_current`: questions `28`, hit `1.0000`, coverage `0.8458`, seed_hit `0.9643`, first_rank `3.5185`

### multi_span

- `bridge_from_flat_seeds_selective_current`: questions `17`, hit `1.0000`, coverage `0.9275`, seed_hit `0.9412`, first_rank `2.8750`

### float_table

- `bridge_from_flat_seeds_selective_current`: questions `67`, hit `0.8060`, coverage `0.7189`, seed_hit `0.8657`, first_rank `4.4655`

## Question Types

### boolean

- `bridge_from_flat_seeds_selective_current`: questions `27`, hit `0.5185`, coverage `0.5000`, seed_hit `0.5926`, first_rank `5.6250`

### what

- `bridge_from_flat_seeds_selective_current`: questions `62`, hit `0.7097`, coverage `0.6478`, seed_hit `0.7419`, first_rank `5.1739`

### how

- `bridge_from_flat_seeds_selective_current`: questions `36`, hit `0.8056`, coverage `0.7477`, seed_hit `0.8611`, first_rank `4.8387`

### which

- `bridge_from_flat_seeds_selective_current`: questions `13`, hit `0.5385`, coverage `0.4885`, seed_hit `0.5385`, first_rank `3.8571`

### other

- `bridge_from_flat_seeds_selective_current`: questions `8`, hit `0.7500`, coverage `0.7500`, seed_hit `0.7500`, first_rank `5.3333`
