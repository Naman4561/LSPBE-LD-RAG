# Bridge v2.1 Summary

## Best Configs

- best adjacency: `adjacency_baseline|method=adjacency|k=8|context_budget=20|seed_mode=dense|dense_w=1.00|sparse_w=0.00|cont=idf_overlap|trigger=always:0.72|rerank=none|diversify=0:0.15` with evidence_hit_rate `0.7704`
- best bridge v1: `bridge_v1_baseline|method=bridge_v1_full|k=8|context_budget=20|seed_mode=dense|dense_w=1.00|sparse_w=0.00|cont=idf_overlap|trigger=always:0.72|rerank=none|diversify=0:0.15` with evidence_hit_rate `0.7704`
- best current Bridge v2: `bridge_v2_baseline|method=bridge_v2_baseline|k=10|context_budget=20|seed_mode=dense|dense_w=1.00|sparse_w=0.00|cont=idf_overlap|trigger=always:0.72|rerank=none|diversify=0:0.15` with evidence_hit_rate `0.8112`
- best overall Bridge v2.1 variant: `hybrid_soft|method=bridge_v21|k=10|context_budget=20|seed_mode=hybrid|dense_w=1.00|sparse_w=0.50|cont=idf_overlap|trigger=always:0.72|rerank=none|diversify=0:0.15` with evidence_hit_rate `0.8214`
- best upgraded pipeline: `full_upgraded_pipeline|method=bridge_v21|k=10|context_budget=20|seed_mode=hybrid|dense_w=1.00|sparse_w=0.50|cont=idf_overlap|trigger=low_confidence:0.72|rerank=lightweight|diversify=1:0.15` with evidence_hit_rate `0.8163`

## Component Answers

1. does hybrid retrieval improve seed quality? yes
2. does stronger continuity help? no
3. does adaptive triggering help? no
4. does local reranking help? yes, but only in combination
5. does diversification help? yes
6. what is the best full upgraded pipeline? `full_upgraded_pipeline|method=bridge_v21|k=10|context_budget=20|seed_mode=hybrid|dense_w=1.00|sparse_w=0.50|cont=idf_overlap|trigger=low_confidence:0.72|rerank=lightweight|diversify=1:0.15`
7. how much does it beat current Bridge v2? `0.0051` evidence_hit_rate
8. does it improve the beyond-adjacency subset? yes

## Beyond-Adjacency Subset

- subset size: `94` questions
- current Bridge v2 hit rate: `0.8404`
- best overall Bridge v2.1 hit rate: `0.8511`
- best upgraded pipeline hit rate: `0.8511`

## What Helped Most

- best hybrid-only config: `hybrid_soft|method=bridge_v21|k=10|context_budget=20|seed_mode=hybrid|dense_w=1.00|sparse_w=0.50|cont=idf_overlap|trigger=always:0.72|rerank=none|diversify=0:0.15` with overall `0.8214` and seed hit `0.2551`
- best continuity-only config: `bridge_v2_baseline|method=bridge_v2_baseline|k=10|context_budget=20|seed_mode=dense|dense_w=1.00|sparse_w=0.00|cont=idf_overlap|trigger=always:0.72|rerank=none|diversify=0:0.15` with overall `0.8112`
- best trigger-only config: `trigger_low_conf|method=bridge_v21|k=10|context_budget=20|seed_mode=dense|dense_w=1.00|sparse_w=0.00|cont=idf_overlap|trigger=low_confidence:0.72|rerank=none|diversify=0:0.15` with overall `0.8112`
- rerank-only config: `rerank_only|method=bridge_v21|k=10|context_budget=20|seed_mode=dense|dense_w=1.00|sparse_w=0.00|cont=idf_overlap|trigger=always:0.72|rerank=lightweight|diversify=0:0.15` with overall `0.8061`
- diversify-only config: `diversify_only|method=bridge_v21|k=10|context_budget=20|seed_mode=dense|dense_w=1.00|sparse_w=0.00|cont=idf_overlap|trigger=always:0.72|rerank=none|diversify=1:0.15` with overall `0.8163`

## Question-Type Slices

- current Bridge v2 for `bridge_v2_baseline|method=bridge_v2_baseline|k=10|context_budget=20|seed_mode=dense|dense_w=1.00|sparse_w=0.00|cont=idf_overlap|trigger=always:0.72|rerank=none|diversify=0:0.15`:
- `boolean`: 0.650 hit rate over 40 questions
- `how`: 0.768 hit rate over 56 questions
- `other`: 1.000 hit rate over 6 questions
- `what`: 0.885 hit rate over 78 questions
- `which`: 0.938 hit rate over 16 questions
- best upgraded pipeline for `full_upgraded_pipeline|method=bridge_v21|k=10|context_budget=20|seed_mode=hybrid|dense_w=1.00|sparse_w=0.50|cont=idf_overlap|trigger=low_confidence:0.72|rerank=lightweight|diversify=1:0.15`:
- `boolean`: 0.650 hit rate over 40 questions
- `how`: 0.750 hit rate over 56 questions
- `other`: 1.000 hit rate over 6 questions
- `what`: 0.910 hit rate over 78 questions
- `which`: 0.938 hit rate over 16 questions

## Final Interpretation

- Tier 1 is about putting better seeds and better bridge triggers into the same skip-local bridge design.
- Tier 2 is about ordering and selecting that local pool more intelligently without adding a heavy reranker.
- The strongest single v2.1 change was `hybrid_soft` at `0.8214`.
- Current Bridge v2 reaches `0.8112`; the best upgraded pipeline reaches `0.8163`.
