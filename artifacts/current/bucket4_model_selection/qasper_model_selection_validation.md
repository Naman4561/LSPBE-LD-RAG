# QASPER Model Selection Validation

- stage: `full validation retrieval`
- dataset_path: `data/qasper_validation_full.json`
- questions: `1005`
- papers: `281`
- main_representation: `current`
- main_segmentation: `seg_paragraph_pair`
- subset_counts: `{"adjacency_easy": 611, "boolean": 145, "float_table": 553, "how": 193, "multi_span": 231, "other": 60, "skip_local": 325, "what": 506, "which": 101}`

## Overall

### flat_hybrid_current

- evidence_hit_rate: `0.8617`
- evidence_coverage_rate: `0.7833`
- seed_hit_rate: `0.8617`
- first_evidence_rank: `4.1813`

### adjacency_hybrid_current

- evidence_hit_rate: `0.8358`
- evidence_coverage_rate: `0.7459`
- seed_hit_rate: `0.7741`
- first_evidence_rank: `3.0707`

### bridge_v2_hybrid_current

- evidence_hit_rate: `0.8388`
- evidence_coverage_rate: `0.7525`
- seed_hit_rate: `0.7741`
- first_evidence_rank: `3.0707`

### bridge_final_current

- evidence_hit_rate: `0.8438`
- evidence_coverage_rate: `0.7567`
- seed_hit_rate: `0.7741`
- first_evidence_rank: `3.0707`

### fixed_chunk_bridge_final

- evidence_hit_rate: `0.8299`
- evidence_coverage_rate: `0.7386`
- seed_hit_rate: `0.7294`
- first_evidence_rank: `3.3861`

## Targeted Subsets

### skip_local

- `flat_hybrid_current`: questions `325`, hit `0.9846`, coverage `0.8490`, seed_hit `0.9846`, first_rank `3.5312`
- `adjacency_hybrid_current`: questions `325`, hit `0.9631`, coverage `0.7885`, seed_hit `0.9169`, first_rank `2.8255`
- `bridge_v2_hybrid_current`: questions `325`, hit `0.9662`, coverage `0.8029`, seed_hit `0.9169`, first_rank `2.8255`
- `bridge_final_current`: questions `325`, hit `0.9723`, coverage `0.8086`, seed_hit `0.9169`, first_rank `2.8255`
- `fixed_chunk_bridge_final`: questions `325`, hit `0.9662`, coverage `0.7893`, seed_hit `0.8769`, first_rank `3.0737`

### multi_span

- `flat_hybrid_current`: questions `231`, hit `0.9913`, coverage `0.8492`, seed_hit `0.9913`, first_rank `3.4672`
- `adjacency_hybrid_current`: questions `231`, hit `0.9740`, coverage `0.7754`, seed_hit `0.9264`, first_rank `2.8084`
- `bridge_v2_hybrid_current`: questions `231`, hit `0.9784`, coverage `0.7911`, seed_hit `0.9264`, first_rank `2.8084`
- `bridge_final_current`: questions `231`, hit `0.9870`, coverage `0.7928`, seed_hit `0.9264`, first_rank `2.8084`
- `fixed_chunk_bridge_final`: questions `231`, hit `0.9784`, coverage `0.7808`, seed_hit `0.8831`, first_rank `3.0931`

### float_table

- `flat_hybrid_current`: questions `553`, hit `0.9277`, coverage `0.8047`, seed_hit `0.9277`, first_rank `4.0351`
- `adjacency_hybrid_current`: questions `553`, hit `0.9042`, coverage `0.7682`, seed_hit `0.8463`, first_rank `3.0812`
- `bridge_v2_hybrid_current`: questions `553`, hit `0.9060`, coverage `0.7739`, seed_hit `0.8463`, first_rank `3.0812`
- `bridge_final_current`: questions `553`, hit `0.9078`, coverage `0.7764`, seed_hit `0.8463`, first_rank `3.0812`
- `fixed_chunk_bridge_final`: questions `553`, hit `0.8987`, coverage `0.7627`, seed_hit `0.7957`, first_rank `3.4682`

## Question Types

### boolean

- `flat_hybrid_current`: questions `145`, hit `0.6966`, coverage `0.6225`, seed_hit `0.6966`, first_rank `5.1089`
- `adjacency_hybrid_current`: questions `145`, hit `0.6897`, coverage `0.6161`, seed_hit `0.6000`, first_rank `3.8276`
- `bridge_v2_hybrid_current`: questions `145`, hit `0.6897`, coverage `0.6171`, seed_hit `0.6000`, first_rank `3.8276`
- `bridge_final_current`: questions `145`, hit `0.7034`, coverage `0.6243`, seed_hit `0.6000`, first_rank `3.8276`
- `fixed_chunk_bridge_final`: questions `145`, hit `0.6897`, coverage `0.6165`, seed_hit `0.5172`, first_rank `3.9200`

### what

- `flat_hybrid_current`: questions `506`, hit `0.8814`, coverage `0.7942`, seed_hit `0.8814`, first_rank `4.0112`
- `adjacency_hybrid_current`: questions `506`, hit `0.8577`, coverage `0.7604`, seed_hit `0.8043`, first_rank `3.0221`
- `bridge_v2_hybrid_current`: questions `506`, hit `0.8617`, coverage `0.7690`, seed_hit `0.8043`, first_rank `3.0221`
- `bridge_final_current`: questions `506`, hit `0.8617`, coverage `0.7689`, seed_hit `0.8043`, first_rank `3.0221`
- `fixed_chunk_bridge_final`: questions `506`, hit `0.8399`, coverage `0.7378`, seed_hit `0.7628`, first_rank `3.4378`

### how

- `flat_hybrid_current`: questions `193`, hit `0.9067`, coverage `0.8371`, seed_hit `0.9067`, first_rank `4.1314`
- `adjacency_hybrid_current`: questions `193`, hit `0.8653`, coverage `0.7766`, seed_hit `0.7979`, first_rank `2.7532`
- `bridge_v2_hybrid_current`: questions `193`, hit `0.8653`, coverage `0.7861`, seed_hit `0.7979`, first_rank `2.7532`
- `bridge_final_current`: questions `193`, hit `0.8705`, coverage `0.7940`, seed_hit `0.7979`, first_rank `2.7532`
- `fixed_chunk_bridge_final`: questions `193`, hit `0.8808`, coverage `0.7953`, seed_hit `0.7668`, first_rank `3.1284`

### which

- `flat_hybrid_current`: questions `101`, hit `0.9010`, coverage `0.8260`, seed_hit `0.9010`, first_rank `3.9451`
- `adjacency_hybrid_current`: questions `101`, hit `0.9010`, coverage `0.8138`, seed_hit `0.8416`, first_rank `3.3176`
- `bridge_v2_hybrid_current`: questions `101`, hit `0.9010`, coverage `0.8138`, seed_hit `0.8416`, first_rank `3.3176`
- `bridge_final_current`: questions `101`, hit `0.9109`, coverage `0.8206`, seed_hit `0.8416`, first_rank `3.3176`
- `fixed_chunk_bridge_final`: questions `101`, hit `0.8713`, coverage `0.7979`, seed_hit `0.7822`, first_rank `3.4810`

### other

- `flat_hybrid_current`: questions `60`, hit `0.8833`, coverage `0.8356`, seed_hit `0.8833`, first_rank `4.4151`
- `adjacency_hybrid_current`: questions `60`, hit `0.8000`, coverage `0.7239`, seed_hit `0.7500`, first_rank `2.6667`
- `bridge_v2_hybrid_current`: questions `60`, hit `0.8167`, coverage `0.7294`, seed_hit `0.7500`, first_rank `2.6667`
- `bridge_final_current`: questions `60`, hit `0.8333`, coverage `0.7461`, seed_hit `0.7500`, first_rank `2.6667`
- `fixed_chunk_bridge_final`: questions `60`, hit `0.8500`, coverage `0.7578`, seed_hit `0.7500`, first_rank `2.7333`
