# Bucket 3 Structure-Aware Representation Summary

## What Changed

- new unit types: `{"caption": 118, "float_like": 849, "inline_ref": 2623, "paragraph_pair": 8955}`
- linking rules: `ref_to_caption`, `caption_to_backbone`, `float_to_backbone`, and `backbone_to_inline_ref`
- float/table refinement: added `float_direct`, `float_reference`, `float_adjacent_prose`, and `float_signal_mode` metadata on top of the coarse `float_table` label

## Retrieval Outcome

- smoke retrieval artifact: [qasper_structure_repr_validation_smoke.md](C:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/current/bucket3_structure_repr/qasper_structure_repr_validation_smoke.md)
- targeted subset artifact: [qasper_structure_repr_targeted_subsets.md](C:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/current/bucket3_structure_repr/qasper_structure_repr_targeted_subsets.md)
- full validation artifact: [qasper_structure_repr_validation.md](C:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/current/bucket3_structure_repr/qasper_structure_repr_validation.md)
- `bridge_final` current -> structure_aware: seed-hit `-0.0040`, evidence-hit `-0.0030`, coverage `+0.0001`, first-rank `-0.0216`
- strongest subset deltas under `bridge_final`:
- `skip_local`: evidence-hit `+0.0000`, coverage `+0.0079`
- `multi_span`: evidence-hit `+0.0000`, coverage `+0.0110`
- `float_table`: evidence-hit `-0.0054`, coverage `-0.0008`
- `float_reference`: evidence-hit `-0.0054`, coverage `-0.0008`
- `float_adjacent_prose`: evidence-hit `-0.0034`, coverage `+0.0001`

## Answer Smoke

- answer smoke was skipped on purpose because Bucket 2 established answer evaluation as a weak secondary signal and Bucket 3 is retrieval-first.

## Bucket 4 Carryover

- decide whether the structure-aware representation is stable enough to keep as the new default for validation-first retrieval
- if helpful, tighten float-specific analysis further before any broader benchmark or reporting work
