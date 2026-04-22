# QASPER Model Selection Validation

- stage: `full validation retrieval`
- dataset_path: `data\qasper_validation_full.json`
- questions: `20`
- papers: `7`
- main_representation: `current`
- main_segmentation: `seg_paragraph_pair`
- subset_counts: `{"adjacency_easy": 9, "boolean": 1, "float_table": 15, "how": 1, "multi_span": 10, "other": 2, "skip_local": 12, "what": 11, "which": 5}`

## Overall

### flat_hybrid_current

- evidence_hit_rate: `0.9000`
- evidence_coverage_rate: `0.8417`
- seed_hit_rate: `0.9000`
- first_evidence_rank: `3.2778`

### adjacency_hybrid_current

- evidence_hit_rate: `0.8500`
- evidence_coverage_rate: `0.7917`
- seed_hit_rate: `0.8500`
- first_evidence_rank: `2.7059`

### bridge_v2_hybrid_current

- evidence_hit_rate: `0.8500`
- evidence_coverage_rate: `0.7917`
- seed_hit_rate: `0.8500`
- first_evidence_rank: `2.7059`

### bridge_final_current

- evidence_hit_rate: `0.9000`
- evidence_coverage_rate: `0.8417`
- seed_hit_rate: `0.8500`
- first_evidence_rank: `2.7059`

### fixed_chunk_bridge_final

- evidence_hit_rate: `0.9500`
- evidence_coverage_rate: `0.8667`
- seed_hit_rate: `0.8000`
- first_evidence_rank: `2.0625`

## Targeted Subsets

### skip_local

- `flat_hybrid_current`: questions `12`, hit `0.9167`, coverage `0.8472`, seed_hit `0.9167`, first_rank `2.6364`
- `adjacency_hybrid_current`: questions `12`, hit `0.9167`, coverage `0.8472`, seed_hit `0.9167`, first_rank `2.6364`
- `bridge_v2_hybrid_current`: questions `12`, hit `0.9167`, coverage `0.8472`, seed_hit `0.9167`, first_rank `2.6364`
- `bridge_final_current`: questions `12`, hit `0.9167`, coverage `0.8472`, seed_hit `0.9167`, first_rank `2.6364`
- `fixed_chunk_bridge_final`: questions `12`, hit `1.0000`, coverage `0.8889`, seed_hit `0.9167`, first_rank `2.3636`

### multi_span

- `flat_hybrid_current`: questions `10`, hit `1.0000`, coverage `0.9417`, seed_hit `1.0000`, first_rank `2.8000`
- `adjacency_hybrid_current`: questions `10`, hit `1.0000`, coverage `0.9167`, seed_hit `1.0000`, first_rank `2.8000`
- `bridge_v2_hybrid_current`: questions `10`, hit `1.0000`, coverage `0.9167`, seed_hit `1.0000`, first_rank `2.8000`
- `bridge_final_current`: questions `10`, hit `1.0000`, coverage `0.9167`, seed_hit `1.0000`, first_rank `2.8000`
- `fixed_chunk_bridge_final`: questions `10`, hit `1.0000`, coverage `0.9167`, seed_hit `1.0000`, first_rank `2.5000`

### float_table

- `flat_hybrid_current`: questions `15`, hit `0.8667`, coverage `0.7889`, seed_hit `0.8667`, first_rank `2.8462`
- `adjacency_hybrid_current`: questions `15`, hit `0.8667`, coverage `0.7889`, seed_hit `0.8667`, first_rank `2.8462`
- `bridge_v2_hybrid_current`: questions `15`, hit `0.8667`, coverage `0.7889`, seed_hit `0.8667`, first_rank `2.8462`
- `bridge_final_current`: questions `15`, hit `0.8667`, coverage `0.7889`, seed_hit `0.8667`, first_rank `2.8462`
- `fixed_chunk_bridge_final`: questions `15`, hit `0.9333`, coverage `0.8222`, seed_hit `0.8000`, first_rank `2.2500`

## Question Types

### boolean

- `flat_hybrid_current`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `3.0000`
- `adjacency_hybrid_current`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `3.0000`
- `bridge_v2_hybrid_current`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `3.0000`
- `bridge_final_current`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `3.0000`
- `fixed_chunk_bridge_final`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `6.0000`

### what

- `flat_hybrid_current`: questions `11`, hit `0.8182`, coverage `0.7424`, seed_hit `0.8182`, first_rank `3.4444`
- `adjacency_hybrid_current`: questions `11`, hit `0.7273`, coverage `0.6970`, seed_hit `0.7273`, first_rank `2.2500`
- `bridge_v2_hybrid_current`: questions `11`, hit `0.7273`, coverage `0.6970`, seed_hit `0.7273`, first_rank `2.2500`
- `bridge_final_current`: questions `11`, hit `0.8182`, coverage `0.7879`, seed_hit `0.7273`, first_rank `2.2500`
- `fixed_chunk_bridge_final`: questions `11`, hit `0.9091`, coverage `0.8333`, seed_hit `0.6364`, first_rank `1.1429`

### how

- `flat_hybrid_current`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `3.0000`
- `adjacency_hybrid_current`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `3.0000`
- `bridge_v2_hybrid_current`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `3.0000`
- `bridge_final_current`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `3.0000`
- `fixed_chunk_bridge_final`: questions `1`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `1.0000`

### which

- `flat_hybrid_current`: questions `5`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `2.4000`
- `adjacency_hybrid_current`: questions `5`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `2.4000`
- `bridge_v2_hybrid_current`: questions `5`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `2.4000`
- `bridge_final_current`: questions `5`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `2.4000`
- `fixed_chunk_bridge_final`: questions `5`, hit `1.0000`, coverage `1.0000`, seed_hit `1.0000`, first_rank `2.0000`

### other

- `flat_hybrid_current`: questions `2`, hit `1.0000`, coverage `0.8333`, seed_hit `1.0000`, first_rank `5.0000`
- `adjacency_hybrid_current`: questions `2`, hit `1.0000`, coverage `0.5833`, seed_hit `1.0000`, first_rank `5.0000`
- `bridge_v2_hybrid_current`: questions `2`, hit `1.0000`, coverage `0.5833`, seed_hit `1.0000`, first_rank `5.0000`
- `bridge_final_current`: questions `2`, hit `1.0000`, coverage `0.5833`, seed_hit `1.0000`, first_rank `5.0000`
- `fixed_chunk_bridge_final`: questions `2`, hit `1.0000`, coverage `0.5833`, seed_hit `1.0000`, first_rank `4.0000`
