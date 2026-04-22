# Final Model Selection Note

- selected method for Bucket 5: `flat_hybrid_current`
- mainline representation: `current` / `seg_paragraph_pair`
- structure-aware diagnostic included in Bucket 4: `no`
- flat implementation: hybrid top-20 paragraph-pair seeds with no local expansion
- fixed chunk implementation: deterministic section-aware fixed chunks with `160` words and `40` word overlap under `bridge_final`
- retrieval evidence hit rate: `0.8617`
- retrieval evidence coverage rate: `0.7833`
- retrieval seed hit rate: `0.8617`
- retrieval first evidence rank: `4.1813`
- selection note: Retrieval remained the primary selector in Bucket 4, so the top retrieval method was kept as the Bucket 5 candidate.
