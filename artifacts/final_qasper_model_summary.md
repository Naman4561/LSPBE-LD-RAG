# Final QASPER Model Summary

## Fresh 50-Paper Revalidation

- validation set: `data/qasper_subset_debug_50.json`
- canonical model: `bridge_final`
- recomputed evidence_hit_rate: `0.8214`
- exact value: `0.8214285714285714`
- locked historical check: match
- fresh artifact source: `artifacts/final_qasper_50paper_recomputed_model_results.json`

## Locked Config

- hybrid seed retrieval
- dense weight `1.00`
- sparse weight `0.50`
- Bridge v2 skip-local design
- max skip distance `2`
- top bridge candidate per seed `1`
- continuity `idf_overlap`
- no section scoring
- no adaptive trigger
- no reranker
- no diversification

## Fresh Canonical 50-Paper Comparison

- adjacency: `0.7704`
- bridge v1: `0.7704`
- current Bridge v2 baseline: `0.8112`
- final streamlined model: `0.8214`

## Notes

- These values come from a fresh run of the cleaned canonical codepath.
- The beyond-adjacency subset result `0.8511` remains a locked historical diagnostic reference and was not recomputed by the new lightweight canonical script.
