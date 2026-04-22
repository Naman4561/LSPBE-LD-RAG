# Bucket 4 Model Selection Summary

## Scope

- split: `validation` only
- mainline representation: `current` on `seg_paragraph_pair`
- structure-aware diagnostic included: `no`
- fixed chunk baseline: one deterministic `bridge_final` comparator only

## Compared Methods

- `flat_hybrid_current`: family `flat`, representation `current`, segmentation `seg_paragraph_pair`, chunking `paragraph_pair`
- `adjacency_hybrid_current`: family `adjacency`, representation `current`, segmentation `seg_paragraph_pair`, chunking `paragraph_pair`
- `bridge_v2_hybrid_current`: family `bridge_v2`, representation `current`, segmentation `seg_paragraph_pair`, chunking `paragraph_pair`
- `bridge_final_current`: family `bridge_final`, representation `current`, segmentation `seg_paragraph_pair`, chunking `paragraph_pair`
- `fixed_chunk_bridge_final`: family `fixed_chunk_bridge_final`, representation `current`, segmentation `fixed_chunk`, chunking `fixed_chunk`

## Retrieval Ranking

- `fixed_chunk_bridge_final`: hit `0.9500`, coverage `0.8667`, seed_hit `0.8000`, first_rank `2.0625`
- `flat_hybrid_current`: hit `0.9000`, coverage `0.8417`, seed_hit `0.9000`, first_rank `3.2778`
- `bridge_final_current`: hit `0.9000`, coverage `0.8417`, seed_hit `0.8500`, first_rank `2.7059`
- `adjacency_hybrid_current`: hit `0.8500`, coverage `0.7917`, seed_hit `0.8500`, first_rank `2.7059`
- `bridge_v2_hybrid_current`: hit `0.8500`, coverage `0.7917`, seed_hit `0.8500`, first_rank `2.7059`

## Finalists

- advanced to answer eval: `fixed_chunk_bridge_final, flat_hybrid_current`

- `fixed_chunk_bridge_final`: EM `0.1000`, F1 `0.1161`, empty `0.6000`
- `flat_hybrid_current`: EM `0.2000`, F1 `0.3401`, empty `0.3500`

## Uncertainty

- `flat_hybrid_current` vs `adjacency_hybrid_current`: evidence-hit delta `+0.0500` with 95% CI [`+0.0000`, `+0.1500`]; coverage delta `+0.0500` with 95% CI [`-0.0375`, `+0.1750`]
- `adjacency_hybrid_current` vs `bridge_v2_hybrid_current`: evidence-hit delta `+0.0000` with 95% CI [`+0.0000`, `+0.0000`]; coverage delta `+0.0000` with 95% CI [`+0.0000`, `+0.0000`]
- `bridge_v2_hybrid_current` vs `bridge_final_current`: evidence-hit delta `-0.0500` with 95% CI [`-0.1500`, `+0.0000`]; coverage delta `-0.0500` with 95% CI [`-0.1500`, `+0.0000`]
- `fixed_chunk_bridge_final` vs `bridge_final_current`: evidence-hit delta `+0.0500` with 95% CI [`+0.0000`, `+0.1500`]; coverage delta `+0.0250` with 95% CI [`+0.0000`, `+0.0750`]

## Decision

- selected candidate for Bucket 5: `fixed_chunk_bridge_final`
- rationale: Retrieval remained the primary selector in Bucket 4, so the top retrieval method was kept as the Bucket 5 candidate.
- screening subset size: `10`
