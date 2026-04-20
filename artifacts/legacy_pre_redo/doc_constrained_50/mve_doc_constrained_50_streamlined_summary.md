# Streamlined Bridge Summary

## Best Configs

- adjacency baseline: `adjacency_baseline|method=adjacency|k=8|seed_mode=dense|dense_w=1.00|sparse_w=0.00|section=current|diversify=0:0.15` with evidence_hit_rate `0.7704`
- bridge v1 baseline: `bridge_v1_baseline|method=bridge_v1_full|k=8|seed_mode=dense|dense_w=1.00|sparse_w=0.00|section=current|diversify=0:0.15` with evidence_hit_rate `0.7704`
- current Bridge v2 baseline: `bridge_v2_baseline|method=bridge_v2_baseline|k=10|seed_mode=dense|dense_w=1.00|sparse_w=0.00|section=current|diversify=0:0.15` with evidence_hit_rate `0.8112`
- best v2.1 hybrid_soft baseline: `bridge_v21_hybrid_soft|method=bridge_v21_streamlined|k=10|seed_mode=hybrid|dense_w=1.00|sparse_w=0.50|section=current|diversify=0:0.15` with evidence_hit_rate `0.8214`
- best streamlined model: `bridge_v21_hybrid_soft|method=bridge_v21_streamlined|k=10|seed_mode=hybrid|dense_w=1.00|sparse_w=0.50|section=current|diversify=0:0.15` with evidence_hit_rate `0.8214`

## Answers

1. what should be the final streamlined default model? `bridge_v21_hybrid_soft|method=bridge_v21_streamlined|k=10|seed_mode=hybrid|dense_w=1.00|sparse_w=0.50|section=current|diversify=0:0.15`
2. should section structure be removed, kept, or improved? kept as-is
3. is diversification worth keeping? no
4. best streamlined vs adjacency: `0.0510`
5. best streamlined vs bridge v1: `0.0510`
6. best streamlined vs current Bridge v2 baseline: `0.0102`
7. best streamlined vs best v2.1 hybrid_soft baseline: `0.0000`

## Section Study

- `none`: overall `0.8214`, beyond-adjacency `0.8511`
- `current`: overall `0.8214`, beyond-adjacency `0.8511`
- `improved`: overall `0.8214`, beyond-adjacency `0.8511`

## Diversification Check

- best no-diversification streamlined config: `bridge_v21_hybrid_soft|method=bridge_v21_streamlined|k=10|seed_mode=hybrid|dense_w=1.00|sparse_w=0.50|section=current|diversify=0:0.15` with `0.8214`
- best diversified streamlined config: `bridge_v21_streamlined_current_diverse|method=bridge_v21_streamlined|k=10|seed_mode=hybrid|dense_w=1.00|sparse_w=0.50|section=current|diversify=1:0.15` with `0.8214`

## Beyond-Adjacency Subset

- subset size: `94` questions
- current Bridge v2 baseline: `0.8404`
- best v2.1 hybrid_soft baseline: `0.8511`
- best streamlined: `0.8511`

## Question-Type Slices

- best streamlined for `bridge_v21_hybrid_soft|method=bridge_v21_streamlined|k=10|seed_mode=hybrid|dense_w=1.00|sparse_w=0.50|section=current|diversify=0:0.15`:
- `boolean`: 0.650 hit rate over 40 questions
- `how`: 0.768 hit rate over 56 questions
- `other`: 1.000 hit rate over 6 questions
- `what`: 0.910 hit rate over 78 questions
- `which`: 0.938 hit rate over 16 questions

## Final Interpretation

- The streamlined study deliberately keeps only the components that looked justified in the v2.1 diagnostics.
- Hybrid seed retrieval remains the backbone of the simplified model.
- The section-mode sweep answers whether section information is worth keeping once isolated from the noisier v2.1 extras.
