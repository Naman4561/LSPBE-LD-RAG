# QASPER Model Selection Screen

- stage: `screening retrieval`
- dataset_path: `data/qasper_validation_full.json`
- questions: `240`
- papers: `238`
- main_representation: `current`
- main_segmentation: `seg_paragraph_pair`
- subset_counts: `{"adjacency_easy": 117, "boolean": 49, "float_table": 151, "how": 48, "multi_span": 88, "other": 44, "skip_local": 107, "what": 51, "which": 48}`

## Overall

### flat_hybrid_current

- evidence_hit_rate: `0.8708`
- evidence_coverage_rate: `0.8023`
- seed_hit_rate: `0.8708`
- first_evidence_rank: `4.2679`

### adjacency_hybrid_current

- evidence_hit_rate: `0.8542`
- evidence_coverage_rate: `0.7501`
- seed_hit_rate: `0.7917`
- first_evidence_rank: `3.2789`

### bridge_v2_hybrid_current

- evidence_hit_rate: `0.8583`
- evidence_coverage_rate: `0.7553`
- seed_hit_rate: `0.7917`
- first_evidence_rank: `3.2789`

### bridge_final_current

- evidence_hit_rate: `0.8750`
- evidence_coverage_rate: `0.7713`
- seed_hit_rate: `0.7917`
- first_evidence_rank: `3.2789`

### fixed_chunk_bridge_final

- evidence_hit_rate: `0.8583`
- evidence_coverage_rate: `0.7634`
- seed_hit_rate: `0.7333`
- first_evidence_rank: `3.2841`

## Targeted Subsets

### skip_local

- `flat_hybrid_current`: questions `107`, hit `0.9720`, coverage `0.8644`, seed_hit `0.9720`, first_rank `3.5962`
- `adjacency_hybrid_current`: questions `107`, hit `0.9626`, coverage `0.7784`, seed_hit `0.9252`, first_rank `3.1616`
- `bridge_v2_hybrid_current`: questions `107`, hit `0.9720`, coverage `0.7902`, seed_hit `0.9252`, first_rank `3.1616`
- `bridge_final_current`: questions `107`, hit `0.9720`, coverage `0.7824`, seed_hit `0.9252`, first_rank `3.1616`
- `fixed_chunk_bridge_final`: questions `107`, hit `0.9720`, coverage `0.8020`, seed_hit `0.8598`, first_rank `3.1739`

### multi_span

- `flat_hybrid_current`: questions `88`, hit `0.9886`, coverage `0.8741`, seed_hit `0.9886`, first_rank `3.6322`
- `adjacency_hybrid_current`: questions `88`, hit `0.9773`, coverage `0.7722`, seed_hit `0.9318`, first_rank `3.1098`
- `bridge_v2_hybrid_current`: questions `88`, hit `0.9886`, coverage `0.7846`, seed_hit `0.9318`, first_rank `3.1098`
- `bridge_final_current`: questions `88`, hit `0.9886`, coverage `0.7712`, seed_hit `0.9318`, first_rank `3.1098`
- `fixed_chunk_bridge_final`: questions `88`, hit `0.9886`, coverage `0.7938`, seed_hit `0.8636`, first_rank `3.2237`

### float_table

- `flat_hybrid_current`: questions `151`, hit `0.9338`, coverage `0.8318`, seed_hit `0.9338`, first_rank `4.0567`
- `adjacency_hybrid_current`: questions `151`, hit `0.9139`, coverage `0.7742`, seed_hit `0.8742`, first_rank `3.3712`
- `bridge_v2_hybrid_current`: questions `151`, hit `0.9205`, coverage `0.7783`, seed_hit `0.8742`, first_rank `3.3712`
- `bridge_final_current`: questions `151`, hit `0.9272`, coverage `0.7846`, seed_hit `0.8742`, first_rank `3.3712`
- `fixed_chunk_bridge_final`: questions `151`, hit `0.9205`, coverage `0.7874`, seed_hit `0.8146`, first_rank `3.3821`

## Question Types

### boolean

- `flat_hybrid_current`: questions `49`, hit `0.7347`, coverage `0.6550`, seed_hit `0.7347`, first_rank `4.5278`
- `adjacency_hybrid_current`: questions `49`, hit `0.7551`, coverage `0.6514`, seed_hit `0.6939`, first_rank `4.0882`
- `bridge_v2_hybrid_current`: questions `49`, hit `0.7551`, coverage `0.6543`, seed_hit `0.6939`, first_rank `4.0882`
- `bridge_final_current`: questions `49`, hit `0.7551`, coverage `0.6373`, seed_hit `0.6939`, first_rank `4.0882`
- `fixed_chunk_bridge_final`: questions `49`, hit `0.7551`, coverage `0.6730`, seed_hit `0.5510`, first_rank `3.8519`

### what

- `flat_hybrid_current`: questions `51`, hit `0.9020`, coverage `0.8363`, seed_hit `0.9020`, first_rank `4.2174`
- `adjacency_hybrid_current`: questions `51`, hit `0.8824`, coverage `0.7845`, seed_hit `0.8235`, first_rank `3.2143`
- `bridge_v2_hybrid_current`: questions `51`, hit `0.8824`, coverage `0.7932`, seed_hit `0.8235`, first_rank `3.2143`
- `bridge_final_current`: questions `51`, hit `0.9020`, coverage `0.8150`, seed_hit `0.8235`, first_rank `3.2143`
- `fixed_chunk_bridge_final`: questions `51`, hit `0.8627`, coverage `0.7824`, seed_hit `0.7647`, first_rank `3.5641`

### how

- `flat_hybrid_current`: questions `48`, hit `0.9375`, coverage `0.8708`, seed_hit `0.9375`, first_rank `3.9778`
- `adjacency_hybrid_current`: questions `48`, hit `0.9167`, coverage `0.7868`, seed_hit `0.8333`, first_rank `2.7500`
- `bridge_v2_hybrid_current`: questions `48`, hit `0.9167`, coverage `0.7938`, seed_hit `0.8333`, first_rank `2.7500`
- `bridge_final_current`: questions `48`, hit `0.9375`, coverage `0.8274`, seed_hit `0.8333`, first_rank `2.7500`
- `fixed_chunk_bridge_final`: questions `48`, hit `0.9167`, coverage `0.8174`, seed_hit `0.8333`, first_rank `2.8750`

### which

- `flat_hybrid_current`: questions `48`, hit `0.8958`, coverage `0.8309`, seed_hit `0.8958`, first_rank `3.9302`
- `adjacency_hybrid_current`: questions `48`, hit `0.8958`, coverage `0.8104`, seed_hit `0.8542`, first_rank `3.4390`
- `bridge_v2_hybrid_current`: questions `48`, hit `0.8958`, coverage `0.8104`, seed_hit `0.8542`, first_rank `3.4390`
- `bridge_final_current`: questions `48`, hit `0.9167`, coverage `0.8300`, seed_hit `0.8542`, first_rank `3.4390`
- `fixed_chunk_bridge_final`: questions `48`, hit `0.8750`, coverage `0.7841`, seed_hit `0.7917`, first_rank `3.2368`

### other

- `flat_hybrid_current`: questions `44`, hit `0.8864`, coverage `0.8212`, seed_hit `0.8864`, first_rank `4.7949`
- `adjacency_hybrid_current`: questions `44`, hit `0.8182`, coverage `0.7144`, seed_hit `0.7500`, first_rank `2.9697`
- `bridge_v2_hybrid_current`: questions `44`, hit `0.8409`, coverage `0.7220`, seed_hit `0.7500`, first_rank `2.9697`
- `bridge_final_current`: questions `44`, hit `0.8636`, coverage `0.7447`, seed_hit `0.7500`, first_rank `2.9697`
- `fixed_chunk_bridge_final`: questions `44`, hit `0.8864`, coverage `0.7606`, seed_hit `0.7273`, first_rank `3.0312`

## Screening Subset

- policy: `greedy_feature_balanced`
- selected_counts: `{"adjacency_easy": 117, "boolean": 49, "float_table": 151, "how": 48, "multi_span": 88, "other": 44, "skip_local": 107, "what": 51, "which": 48}`
