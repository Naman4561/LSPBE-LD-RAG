# Layer 0 Phase 0A Segmentation Registry

## Scope

- task: `T0A.1`
- purpose: build a reusable chunking/segmentation registry and materialize the first Layer 0 segmentation families
- non-goal: no major retrieval experiments are run here

## Common Output Schema

- every unit stores `paper_id`, `unit_id`, `segmentation_family`, `text`, `word_count`, and `char_count`
- section metadata is kept under `section`: primary section name, primary heading path, all heading paths, and section indices
- spans are stored under `span`: doc-level char span and doc-level word span when available
- source traceability is stored under `source`: paragraph ids and sentence ids
- compositional provenance is stored under `parent_links` for pair/triple windows
- family-specific settings are kept under `metadata`

## Families

### fixed_120_30

- description: Section-aware fixed windows of 120 words with 30-word overlap.
- parameters: `{"chunk_words": 120, "overlap_words": 30}`
- heading_policy: `primary+all`

### fixed_160_40

- description: Section-aware fixed windows of 160 words with 40-word overlap.
- parameters: `{"chunk_words": 160, "overlap_words": 40}`
- heading_policy: `primary+all`

### fixed_220_60

- description: Section-aware fixed windows of 220 words with 60-word overlap.
- parameters: `{"chunk_words": 220, "overlap_words": 60}`
- heading_policy: `primary+all`

### paragraph

- description: Single-paragraph units with sentence-aware splitting only when a paragraph exceeds the max length.
- parameters: `{"max_words": 220, "target_words": 170}`
- heading_policy: `primary+all`

### paragraph_pair

- description: Overlapping two-unit windows over the paragraph family within each section.
- parameters: `{"paragraph_basis_max_words": 220, "paragraph_basis_target_words": 170, "window_size": 2}`
- heading_policy: `primary+all`

### paragraph_triple

- description: Overlapping three-unit windows over the paragraph family within each section.
- parameters: `{"paragraph_basis_max_words": 220, "paragraph_basis_target_words": 170, "window_size": 3}`
- heading_policy: `primary+all`

### semantic_balanced

- description: Mid-size semantic grouping with a stronger cohesion threshold and moderate target length.
- parameters: `{"allow_cross_section": true, "max_words": 240, "min_words": 110, "similarity_floor": 0.12, "target_words": 170}`
- heading_policy: `primary+all`

### semantic_coarse

- description: Coarser semantic grouping that allows longer units before flushing.
- parameters: `{"allow_cross_section": true, "max_words": 360, "min_words": 170, "similarity_floor": 0.08, "target_words": 260}`
- heading_policy: `primary+all`

### semantic_lite

- description: Lightweight semantic grouping with smaller target units and limited cross-section carry-over.
- parameters: `{"allow_cross_section": true, "max_words": 150, "min_words": 70, "similarity_floor": 0.08, "target_words": 110}`
- heading_policy: `primary+all`

### semantic_section_constrained

- description: Semantic grouping with the same local cohesion heuristic as balanced but with hard section boundaries.
- parameters: `{"allow_cross_section": false, "max_words": 240, "min_words": 110, "similarity_floor": 0.12, "target_words": 170}`
- heading_policy: `primary+all`

## Notes

- fixed-window variants are deterministic and section-aware
- semantic variants are fully local and heuristic: sentence grouping plus lexical cohesion with no paid APIs
- `semantic_section_constrained` uses the same local cohesion heuristic as `semantic_balanced` but never crosses a section boundary
- this registry is intentionally separate from the frozen current control path so the existing serious-redo controls remain untouched
