# Bucket 4.5 Bridge Repair Summary

## Implementation

- Stage 1 method: `bridge_from_flat_seeds_current`
- Stage 1 seed reuse: exact same `flat_hybrid_current` top-20 hybrid paragraph-pair seed stage and same final 20-segment context budget.
- Stage 1 bridge behavior: `bridge_final`-style skip-local expansion on top of those flat seeds using `idf_overlap`, no section scoring, and no reranker.
- Stage 2 method: `bridge_from_flat_seeds_selective_current`
- Stage 2 selective rule: expand only for `how` / `which` questions, table-or-figure style prompts, or low-separation seed rankings where the top-two relative gap is below `0.12`.

## Retrieval Outcome

- prior `flat_hybrid_current`: hit `0.8617`, coverage `0.7833`, seed_hit `0.8617`
- prior `bridge_final_current`: hit `0.8438`, coverage `0.7567`, seed_hit `0.7741`
- Stage 1 `bridge_from_flat_seeds_current`: hit `0.8418`, coverage `0.7647`, seed_hit `0.8617`
- Stage 2 `bridge_from_flat_seeds_selective_current`: hit `0.8398`, coverage `0.7627`, seed_hit `0.8617`

## Conclusion

- Weak bridge seeds were a real fairness problem because Stage 1 exactly inherits flat's seed hit rate by construction.
- Always-on bridge expansion still did not fully close the flat gap once the seed stage was repaired.
- Selective expansion did not beat the always-on Stage 1 repair variant.
- Bucket 5 should remain unchanged with `flat_hybrid_current` as the selected path.

## Run Status

- Stage 1 smoke questions: `146`
- Stage 1 validation questions: `1005`
- Stage 2 smoke questions: `146`
- Stage 2 validation questions: `1005`
