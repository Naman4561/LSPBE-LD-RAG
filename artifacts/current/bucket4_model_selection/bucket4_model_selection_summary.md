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

- `flat_hybrid_current`: hit `0.8617`, coverage `0.7833`, seed_hit `0.8617`, first_rank `4.1813`
- `bridge_final_current`: hit `0.8438`, coverage `0.7567`, seed_hit `0.7741`, first_rank `3.0707`
- `bridge_v2_hybrid_current`: hit `0.8388`, coverage `0.7525`, seed_hit `0.7741`, first_rank `3.0707`
- `adjacency_hybrid_current`: hit `0.8358`, coverage `0.7459`, seed_hit `0.7741`, first_rank `3.0707`
- `fixed_chunk_bridge_final`: hit `0.8299`, coverage `0.7386`, seed_hit `0.7294`, first_rank `3.3861`

## Finalists

- advanced to answer eval: `flat_hybrid_current, bridge_final_current`

- `flat_hybrid_current`: EM `0.1682`, F1 `0.2503`, empty `0.2697`
- `bridge_final_current`: EM `0.1343`, F1 `0.1659`, empty `0.4627`

## Uncertainty

- `flat_hybrid_current` vs `adjacency_hybrid_current`: evidence-hit delta `+0.0259` with 95% CI [`+0.0139`, `+0.0398`]; coverage delta `+0.0375` with 95% CI [`+0.0245`, `+0.0507`]
- `adjacency_hybrid_current` vs `bridge_v2_hybrid_current`: evidence-hit delta `-0.0030` with 95% CI [`-0.0070`, `+0.0000`]; coverage delta `-0.0066` with 95% CI [`-0.0102`, `-0.0035`]
- `bridge_v2_hybrid_current` vs `bridge_final_current`: evidence-hit delta `-0.0050` with 95% CI [`-0.0149`, `+0.0040`]; coverage delta `-0.0042` with 95% CI [`-0.0136`, `+0.0059`]

## Decision

- selected candidate for Bucket 5: `flat_hybrid_current`
- rationale: Retrieval remained the primary selector in Bucket 4, so the top retrieval method was kept as the Bucket 5 candidate.
- screening subset size: `240`
