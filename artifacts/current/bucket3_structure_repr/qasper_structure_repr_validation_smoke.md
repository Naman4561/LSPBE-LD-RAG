# QASPER Structure-Aware Validation Smoke

- dataset_path: `data/qasper_validation_full.json`
- segmentation_mode: `seg_paragraph_pair`
- representation_modes: `current, structure_aware`
- methods: `bridge_final`
- max_questions: `150`

## Overall

### current

- unit_type_counts: `{"paragraph_pair": 1495}`
- link_count: `0`

- `bridge_final`: seed-hit `0.8133`, evidence-hit `0.8933`, coverage `0.7810`, first-rank `3.1066`

### structure_aware

- unit_type_counts: `{"caption": 19, "float_like": 111, "inline_ref": 455, "paragraph_pair": 1495}`
- link_count: `630`

- `bridge_final`: seed-hit `0.7867`, evidence-hit `0.8867`, coverage `0.7804`, first-rank `2.8983`

## Deltas

- `bridge_final` current -> structure_aware: seed-hit `-0.0267`, evidence-hit `-0.0067`, coverage `-0.0006`, first-rank `-0.2083`

## Targeted Subsets

### skip_local

- `current` / `bridge_final`: queries `73`, seed-hit `0.9452`, evidence-hit `0.9863`, coverage `0.8213`, first-rank `2.7971`
- `structure_aware` / `bridge_final`: queries `73`, seed-hit `0.9315`, evidence-hit `0.9863`, coverage `0.8270`, first-rank `2.6765`

### multi_span

- `current` / `bridge_final`: queries `56`, seed-hit `0.9464`, evidence-hit `1.0000`, coverage `0.7942`, first-rank `3.0000`
- `structure_aware` / `bridge_final`: queries `56`, seed-hit `0.9286`, evidence-hit `1.0000`, coverage `0.8016`, first-rank `2.7885`

### float_table

- `current` / `bridge_final`: queries `98`, seed-hit `0.8673`, evidence-hit `0.9388`, coverage `0.7876`, first-rank `3.0824`
- `structure_aware` / `bridge_final`: queries `98`, seed-hit `0.8367`, evidence-hit `0.9286`, coverage `0.7867`, first-rank `2.8171`

### float_direct

- `current` / `bridge_final`: queries `0`, seed-hit `0.0000`, evidence-hit `0.0000`, coverage `0.0000`, first-rank `n/a`
- `structure_aware` / `bridge_final`: queries `0`, seed-hit `0.0000`, evidence-hit `0.0000`, coverage `0.0000`, first-rank `n/a`

### float_reference

- `current` / `bridge_final`: queries `98`, seed-hit `0.8673`, evidence-hit `0.9388`, coverage `0.7876`, first-rank `3.0824`
- `structure_aware` / `bridge_final`: queries `98`, seed-hit `0.8367`, evidence-hit `0.9286`, coverage `0.7867`, first-rank `2.8171`

### float_adjacent_prose

- `current` / `bridge_final`: queries `139`, seed-hit `0.8777`, evidence-hit `0.9640`, coverage `0.8428`, first-rank `3.1066`
- `structure_aware` / `bridge_final`: queries `139`, seed-hit `0.8489`, evidence-hit `0.9568`, coverage `0.8422`, first-rank `2.8983`
