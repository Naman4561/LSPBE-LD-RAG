# QASPER Protocol Sanity Check (train_fast50)

- segmentation_mode: `seg_paragraph_pair`
- queries: `146`
- subset_counts: `{"adjacency_easy": 100, "boolean": 27, "float_table": 74, "how": 36, "multi_span": 12, "other": 8, "skip_local": 17, "what": 62, "which": 13}`

## Headline Metrics

### adjacency

- evidence_hit_rate: `0.7466`
- evidence_coverage_rate: `0.7047`
- seed_hit_rate: `0.6712`
- first_evidence_rank: `3.0306122448979593`

### bridge_v2

- evidence_hit_rate: `0.7740`
- evidence_coverage_rate: `0.7481`
- seed_hit_rate: `0.7192`
- first_evidence_rank: `3.4571428571428573`

### bridge_final

- evidence_hit_rate: `0.7740`
- evidence_coverage_rate: `0.7481`
- seed_hit_rate: `0.7329`
- first_evidence_rank: `3.364485981308411`

## Hard Subsets

### adjacency_easy

- `adjacency`: queries `100`, evidence `0.9500`, coverage `0.9217`, seed `0.8400`
- `bridge_v2`: queries `100`, evidence `0.9800`, coverage `0.9517`, seed `0.9100`
- `bridge_final`: queries `100`, evidence `0.9800`, coverage `0.9517`, seed `0.9300`

### skip_local

- `adjacency`: queries `17`, evidence `0.9412`, coverage `0.7484`, seed `0.9412`
- `bridge_v2`: queries `17`, evidence `1.0000`, coverage `0.9444`, seed `0.9412`
- `bridge_final`: queries `17`, evidence `1.0000`, coverage `0.9444`, seed `0.9412`

### multi_span

- `adjacency`: queries `12`, evidence `0.9167`, coverage `0.7222`, seed `0.9167`
- `bridge_v2`: queries `12`, evidence `1.0000`, coverage `1.0000`, seed `0.9167`
- `bridge_final`: queries `12`, evidence `1.0000`, coverage `1.0000`, seed `0.9167`

### float_table

- `adjacency`: queries `74`, evidence `0.9189`, coverage `0.8498`, seed `0.8108`
- `bridge_v2`: queries `74`, evidence `0.9324`, coverage `0.8881`, seed `0.8514`
- `bridge_final`: queries `74`, evidence `0.9324`, coverage `0.8881`, seed `0.8784`
