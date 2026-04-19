# Bridge v2 Summary

## Best Configs

- best flat: `flat|weights=na|k=8|radius=1|top_m=2|context_budget=20|bridge_v2_max_skip_distance=na|bridge_v2_top_per_seed=na` with evidence_hit_rate `0.6888`
- best adjacency: `adjacency|weights=na|k=8|radius=1|top_m=2|context_budget=20|bridge_v2_max_skip_distance=na|bridge_v2_top_per_seed=na` with evidence_hit_rate `0.7704`
- best bridge v1: `bridge_v1_full|weights=1.00,1.00,1.00|k=8|radius=1|top_m=2|context_budget=20|bridge_v2_max_skip_distance=na|bridge_v2_top_per_seed=na` with evidence_hit_rate `0.7704`
- best bridge_v2_skip2: `bridge_v2_skip2|weights=1.00,1.00,0.50|k=10|radius=1|top_m=2|context_budget=20|bridge_v2_max_skip_distance=2|bridge_v2_top_per_seed=1` with evidence_hit_rate `0.8112`
- best bridge_v2_full: `bridge_v2_full|weights=1.00,1.00,0.50|k=10|radius=1|top_m=2|context_budget=20|bridge_v2_max_skip_distance=3|bridge_v2_top_per_seed=1` with evidence_hit_rate `0.8112`

## Main Answers

1. does Bridge v2 beat adjacency overall? yes
2. does Bridge v2 beat bridge v1? yes
3. does Bridge v2 help on the beyond-adjacency subset? yes
4. which Bridge v2 variant is better: full
5. which weights work best? best skip2 `1.00,1.00,0.50`, best full `1.00,1.00,0.50`
6. does query relevance matter more than continuity? likely yes
7. do section signals help at all? no clear evidence
8. does adding distance-3 candidates help or just add noise? no clear gain

## Beyond-Adjacency Subset

- subset size: `94` questions
- adjacency hit rate: `0.7872`
- bridge v1 hit rate: `0.7872`
- bridge_v2_skip2 hit rate: `0.8404`
- bridge_v2_full hit rate: `0.8404`

## Question-Type Slices

- adjacency for `adjacency|weights=na|k=8|radius=1|top_m=2|context_budget=20|bridge_v2_max_skip_distance=na|bridge_v2_top_per_seed=na`:
- `boolean`: 0.600 hit rate over 40 questions
- `how`: 0.732 hit rate over 56 questions
- `other`: 0.833 hit rate over 6 questions
- `what`: 0.846 hit rate over 78 questions
- `which`: 0.938 hit rate over 16 questions
- best bridge_v2 for `bridge_v2_full|weights=1.00,1.00,0.50|k=10|radius=1|top_m=2|context_budget=20|bridge_v2_max_skip_distance=3|bridge_v2_top_per_seed=1`:
- `boolean`: 0.650 hit rate over 40 questions
- `how`: 0.768 hit rate over 56 questions
- `other`: 1.000 hit rate over 6 questions
- `what`: 0.885 hit rate over 78 questions
- `which`: 0.938 hit rate over 16 questions

## Final Interpretation

- Bridge v2 was designed to only score non-immediate skip-local candidates, so any gain here is genuinely beyond adjacency.
- Best adjacency reached `0.7704` while best Bridge v2 reached `0.8112`.
- If those values still tie, the redesigned bridge still is not buying measurable evidence recovery on this QASPER slice.
