# Layer 0 Final Handoff Summary

- task: `T0-Final`
- layer: `Layer 0 - Segmentation`
- scope: documentation, registry cleanup, and guardrails only
- test split used: `no`
- new retrieval screens run: `no`

## Layer 1 Candidates

- `semantic_balanced__plain`
- `semantic_coarse__plain`
- `semantic_section_constrained__plain`
- `fixed_220_60__plain`
- `semantic_lite__plain`
- `paragraph_triple__plain`

## Audit-Only Structure Variants

- `semantic_coarse__structure_lite_caption`
- `semantic_balanced__structure_lite_heading`
- `fixed_220_60__structure_lite_caption`
- `semantic_lite__structure_lite_heading`
- `paragraph_triple__structure_lite_heading`

## Historical Controls

- `paragraph_pair`
- `paragraph`

## Dropped From Future Sweeps

- `fixed_160_40`
- `fixed_120_30`
- all `structure_lite_inline_ref`
- all `mixed_structure_bundle`
- all `structure_full_*`

Dropped means preserved in artifacts, not deleted, and not used in future model-building sweeps unless Layer 0 is explicitly reopened.

## Guardrails

- primary cross-family subset reporting must use fixed question-level labels
- segmentation-specific subset labels may still be used for diagnostics, but not as the primary cross-family slice view
- ranking may use `retrieval_text`, but evidence matching must use `text` / `raw_text`
- context assembly must state whether it uses raw or enriched text
- structure variants are not automatically Layer 1 eligible
- plain promoted segmentations are the only default Layer 1 segmentation candidates

Canonical narrative handoff: `docs/layer0_segmentation_handoff.md`
