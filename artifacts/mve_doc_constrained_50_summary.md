# 50-Paper Doc-Constrained Summary

## Best Overall Configs

- best overall: `adjacency|weights=na|k=8|radius=1|top_m=2|context_budget=20` with evidence_hit_rate `0.7704`
- best flat: `flat|weights=na|k=8|radius=1|top_m=2|context_budget=20` with evidence_hit_rate `0.6888`
- best adjacency: `adjacency|weights=na|k=8|radius=1|top_m=2|context_budget=20` with evidence_hit_rate `0.7704`
- best bridge overall: `bridge_full|weights=1.00,1.00,1.00|k=8|radius=1|top_m=2|context_budget=20` with evidence_hit_rate `0.7704`
- best bridge_adj_entity: `bridge_adj_entity|weights=1.00,1.00,0.00|k=5|radius=1|top_m=2|context_budget=20` with evidence_hit_rate `0.6939`
- best bridge_adj_section: `bridge_adj_section|weights=1.00,0.00,1.00|k=5|radius=1|top_m=2|context_budget=20` with evidence_hit_rate `0.6939`
- best bridge_full: `bridge_full|weights=1.00,1.00,1.00|k=8|radius=1|top_m=2|context_budget=20` with evidence_hit_rate `0.7704`

## Interpretation

- local expansion still beats flat: best adjacency `0.7704` vs best flat `0.6888`
- any bridge config beats adjacency: no
- entity overlap helps: no
- section continuity helps: no
- reducing adjacency weight helps: no

## Sensitivity

- best radius for `adjacency`: `1` with evidence_hit_rate `0.7704`
- best radius for `bridge_adj_entity`: `1` with evidence_hit_rate `0.6939`
- best radius for `bridge_adj_section`: `1` with evidence_hit_rate `0.6939`
- best radius for `bridge_full`: `1` with evidence_hit_rate `0.7704`
- best top_m for `adjacency`: `2` with evidence_hit_rate `0.7704`
- best top_m for `bridge_full`: `2` with evidence_hit_rate `0.7704`
- best k for `flat`: `8` with evidence_hit_rate `0.6888`
- best k for `adjacency`: `8` with evidence_hit_rate `0.7704`
- best k for `bridge_full`: `8` with evidence_hit_rate `0.7704`
- best context_budget for `flat`: `20` with evidence_hit_rate `0.6888`
- best context_budget for `adjacency`: `20` with evidence_hit_rate `0.7704`
- best context_budget for `bridge_full`: `20` with evidence_hit_rate `0.7704`

## Question-Type Breakdown

- adjacency breakdown for `adjacency|weights=na|k=8|radius=1|top_m=2|context_budget=20`:
- `boolean`: 0.619 hit rate over 42 questions
- `how`: 0.732 hit rate over 56 questions
- `other`: 0.750 hit rate over 4 questions
- `what`: 0.846 hit rate over 78 questions
- `which`: 0.938 hit rate over 16 questions
- best bridge breakdown for `bridge_full|weights=1.00,1.00,1.00|k=8|radius=1|top_m=2|context_budget=20`:
- `boolean`: 0.619 hit rate over 42 questions
- `how`: 0.732 hit rate over 56 questions
- `other`: 0.750 hit rate over 4 questions
- `what`: 0.846 hit rate over 78 questions
- `which`: 0.938 hit rate over 16 questions

## Distance-to-Evidence

- adjacency distance profile for `adjacency|weights=na|k=8|radius=1|top_m=2|context_budget=20`:
- distance `0`: 1.000 hit rate over 135 questions
- distance `1`: 1.000 hit rate over 16 questions
- distance `2`: 0.000 hit rate over 5 questions
- distance `3+`: 0.000 hit rate over 10 questions
- best bridge distance profile for `bridge_full|weights=1.00,1.00,1.00|k=8|radius=1|top_m=2|context_budget=20`:
- distance `0`: 1.000 hit rate over 135 questions
- distance `1`: 1.000 hit rate over 16 questions
- distance `2`: 0.000 hit rate over 5 questions
- distance `3+`: 0.000 hit rate over 10 questions

## Final Interpretation

- The 50-paper doc-constrained study is the right place to compare local expansion methods because cross-paper contamination is removed.
- On this study, adjacency reaches `0.7704` and the best bridge reaches `0.7704`.
- If those values tie, the bridge signals are currently acting as weak tie-breakers rather than adding measurable retrieval lift.
