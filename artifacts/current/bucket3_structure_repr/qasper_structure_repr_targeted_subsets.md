# QASPER Structure-Aware Targeted Subsets

- dataset_path: `data/qasper_validation_full.json`
- segmentation_mode: `seg_paragraph_pair`
- representation_modes: `current, structure_aware`
- methods: `bridge_final`
- max_questions: `1005`

## Overall

### current

- unit_type_counts: `{"paragraph_pair": 8955}`
- link_count: `0`

- `bridge_final`: seed-hit `0.7741`, evidence-hit `0.8438`, coverage `0.7567`, first-rank `3.0707`

### structure_aware

- unit_type_counts: `{"caption": 118, "float_like": 849, "inline_ref": 2623, "paragraph_pair": 8955}`
- link_count: `3807`

- `bridge_final`: seed-hit `0.7701`, evidence-hit `0.8408`, coverage `0.7567`, first-rank `3.0491`

## Deltas

- `bridge_final` current -> structure_aware: seed-hit `-0.0040`, evidence-hit `-0.0030`, coverage `+0.0001`, first-rank `-0.0216`

## Targeted Subsets

### skip_local

- `current` / `bridge_final`: queries `325`, seed-hit `0.9169`, evidence-hit `0.9723`, coverage `0.8086`, first-rank `2.8255`
- `structure_aware` / `bridge_final`: queries `325`, seed-hit `0.9262`, evidence-hit `0.9723`, coverage `0.8164`, first-rank `2.8904`

### multi_span

- `current` / `bridge_final`: queries `231`, seed-hit `0.9264`, evidence-hit `0.9870`, coverage `0.7928`, first-rank `2.8084`
- `structure_aware` / `bridge_final`: queries `231`, seed-hit `0.9351`, evidence-hit `0.9870`, coverage `0.8038`, first-rank `2.8657`

### float_table

- `current` / `bridge_final`: queries `553`, seed-hit `0.8463`, evidence-hit `0.9078`, coverage `0.7764`, first-rank `3.0812`
- `structure_aware` / `bridge_final`: queries `553`, seed-hit `0.8463`, evidence-hit `0.9024`, coverage `0.7755`, first-rank `2.9722`

### float_direct

- `current` / `bridge_final`: queries `0`, seed-hit `0.0000`, evidence-hit `0.0000`, coverage `0.0000`, first-rank `n/a`
- `structure_aware` / `bridge_final`: queries `0`, seed-hit `0.0000`, evidence-hit `0.0000`, coverage `0.0000`, first-rank `n/a`

### float_reference

- `current` / `bridge_final`: queries `553`, seed-hit `0.8463`, evidence-hit `0.9078`, coverage `0.7764`, first-rank `3.0812`
- `structure_aware` / `bridge_final`: queries `553`, seed-hit `0.8463`, evidence-hit `0.9024`, coverage `0.7755`, first-rank `2.9722`

### float_adjacent_prose

- `current` / `bridge_final`: queries `888`, seed-hit `0.8761`, evidence-hit `0.9550`, coverage `0.8564`, first-rank `3.0707`
- `structure_aware` / `bridge_final`: queries `888`, seed-hit `0.8716`, evidence-hit `0.9516`, coverage `0.8564`, first-rank `3.0491`
