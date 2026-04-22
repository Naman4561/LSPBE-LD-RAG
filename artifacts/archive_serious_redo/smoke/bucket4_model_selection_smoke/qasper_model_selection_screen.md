# QASPER Model Selection Screen

- stage: `screening retrieval`
- dataset_path: `data\qasper_validation_full.json`
- questions: `10`
- papers: `7`
- main_representation: `current`
- main_segmentation: `seg_paragraph_pair`
- subset_counts: `{"adjacency_easy": 5, "boolean": 1, "float_table": 6, "how": 1, "multi_span": 5, "other": 2, "skip_local": 6, "what": 3, "which": 3}`

## Overall

### flat_hybrid_current

- evidence_hit_rate: `0.9000`
- evidence_coverage_rate: `0.8667`
- seed_hit_rate: `0.9000`
- first_evidence_rank: `4.2222`

### adjacency_hybrid_current

- evidence_hit_rate: `0.8000`
- evidence_coverage_rate: `0.7167`
- seed_hit_rate: `0.8000`
- first_evidence_rank: `3.1250`

### bridge_v2_hybrid_current

- evidence_hit_rate: `0.8000`
- evidence_coverage_rate: `0.7167`
- seed_hit_rate: `0.8000`
- first_evidence_rank: `3.1250`

### bridge_final_current

- evidence_hit_rate: `0.9000`
- evidence_coverage_rate: `0.8167`
- seed_hit_rate: `0.8000`
- first_evidence_rank: `3.1250`

### fixed_chunk_bridge_final

- evidence_hit_rate: `1.0000`
- evidence_coverage_rate: `0.8667`
- seed_hit_rate: `0.8000`
- first_evidence_rank: `3.0000`

## Targeted Subsets

### skip_local

- `flat_hybrid_current`: questions `6`, hit `0.8333`, coverage `0.7778`, seed_hit `0.8333`, first_rank `3.6000`
- `adjacency_hybrid_current`: questions `6`, hit `0.8333`, coverage `0.6944`, seed_hit `0.8333`, first_rank `3.6000`
- `bridge_v2_hybrid_current`: questions `6`, hit `0.8333`, coverage `0.6944`, seed_hit `0.8333`, first_rank `3.6000`
- `bridge_final_current`: questions `6`, hit `0.8333`, coverage `0.6944`, seed_hit `0.8333`, first_rank `3.6000`
- `fixed_chunk_bridge_final`: questions `6`, hit `1.0000`, coverage `0.7778`, seed_hit `0.8333`, first_rank `3.8000`

### multi_span

- `flat_hybrid_current`: questions `5`, hit `1.0000`, coverage `0.9333`, seed_hit `1.0000`, first_rank `3.6000`
- `adjacency_hybrid_current`: questions `5`, hit `1.0000`, coverage `0.8333`, seed_hit `1.0000`, first_rank `3.6000`
- `bridge_v2_hybrid_current`: questions `5`, hit `1.0000`, coverage `0.8333`, seed_hit `1.0000`, first_rank `3.6000`
- `bridge_final_current`: questions `5`, hit `1.0000`, coverage `0.8333`, seed_hit `1.0000`, first_rank `3.6000`
- `fixed_chunk_bridge_final`: questions `5`, hit `1.0000`, coverage `0.8333`, seed_hit `1.0000`, first_rank `3.8000`

### float_table

- `flat_hybrid_current`: questions `6`, hit `0.8333`, coverage `0.7778`, seed_hit `0.8333`, first_rank `3.4000`
- `adjacency_hybrid_current`: questions `6`, hit `0.8333`, coverage `0.6944`, seed_hit `0.8333`, first_rank `3.4000`
- `bridge_v2_hybrid_current`: questions `6`, hit `0.8333`, coverage `0.6944`, seed_hit `0.8333`, first_rank `3.4000`
- `bridge_final_current`: questions `6`, hit `0.8333`, coverage `0.6944`, seed_hit `0.8333`, first_rank `3.4000`
- `fixed_chunk_bridge_final`: questions `6`, hit `1.0000`, coverage `0.7778`, seed_hit `0.8333`, first_rank `3.8000`

## Question Types

### boolean

- `flat_hybrid_current`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `3.0000`
- `adjacency_hybrid_current`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `3.0000`
- `bridge_v2_hybrid_current`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `3.0000`
- `bridge_final_current`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `3.0000`
- `fixed_chunk_bridge_final`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `6.0000`

### what

- `flat_hybrid_current`: questions `3`, hit `0.6667`, coverage `0.6667`, seed_hit `0.6667`, first_rank `7.5000`
- `adjacency_hybrid_current`: questions `3`, hit `0.3333`, coverage `0.3333`, seed_hit `0.3333`, first_rank `2.0000`
- `bridge_v2_hybrid_current`: questions `3`, hit `0.3333`, coverage `0.3333`, seed_hit `0.3333`, first_rank `2.0000`
- `bridge_final_current`: questions `3`, hit `0.6667`, coverage `0.6667`, seed_hit `0.3333`, first_rank `2.0000`
- `fixed_chunk_bridge_final`: questions `3`, hit `1.0000`, coverage `0.8333`, seed_hit `0.3333`, first_rank `1.0000`

### how

- `flat_hybrid_current`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `3.0000`
- `adjacency_hybrid_current`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `3.0000`
- `bridge_v2_hybrid_current`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `3.0000`
- `bridge_final_current`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `3.0000`
- `fixed_chunk_bridge_final`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `1.0000`

### which

- `flat_hybrid_current`: questions `3`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `2.3333`
- `adjacency_hybrid_current`: questions `3`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `2.3333`
- `bridge_v2_hybrid_current`: questions `3`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `2.3333`
- `bridge_final_current`: questions `3`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `2.3333`
- `fixed_chunk_bridge_final`: questions `3`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `2.6667`

### other

- `flat_hybrid_current`: questions `2`, hit `1.0000`, coverage `0.8333`, seed_hit `1.0000`, first_rank `5.0000`
- `adjacency_hybrid_current`: questions `2`, hit `1.0000`, coverage `0.5833`, seed_hit `1.0000`, first_rank `5.0000`
- `bridge_v2_hybrid_current`: questions `2`, hit `1.0000`, coverage `0.5833`, seed_hit `1.0000`, first_rank `5.0000`
- `bridge_final_current`: questions `2`, hit `1.0000`, coverage `0.5833`, seed_hit `1.0000`, first_rank `5.0000`
- `fixed_chunk_bridge_final`: questions `2`, hit `1.0000`, coverage `0.5833`, seed_hit `1.0000`, first_rank `4.0000`

## Screening Subset

- policy: `greedy_feature_balanced`
- selected_counts: `{"adjacency_easy": 5, "boolean": 1, "float_table": 6, "how": 1, "multi_span": 5, "other": 2, "skip_local": 6, "what": 3, "which": 3}`
