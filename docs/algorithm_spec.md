# Algorithm Spec

## Objective

LSPBE asks a narrow question: can lightweight document-local expansion improve long-document retrieval on QASPER without moving to a full graph-RAG system?

## Final Retrieval Story

The final repo story is now intentionally simple:

1. segment each paper into section-aware paragraph chunks
2. retrieve hybrid seed chunks with dense BGE scores plus a smaller sparse signal
3. keep immediate adjacency behavior for local context
4. score only skip-local bridge candidates at distance 2
5. use IDF-weighted overlap as the continuity signal
6. stop there

The final model does not use section scoring, adaptive triggering, reranking, or diversification.

## Canonical QASPER Methods

- `adjacency`: immediate neighbors only
- `bridge_v1`: original adjacency + entity + section bridge baseline
- `bridge_v2`: skip-local Bridge v2 baseline with dense seeds
- `bridge_final`: locked streamlined model with hybrid seeds

## Locked Final Model

`bridge_final` uses:

- seed retrieval mode: `hybrid`
- dense weight: `1.00`
- sparse weight: `0.50`
- max skip distance: `2`
- continuity: `idf_overlap`
- section scoring: off
- adaptive trigger: off
- reranker: off
- diversification: off

## Locked 50-Paper QASPER Results

- adjacency: `0.7704`
- bridge v1: `0.7704`
- bridge v2: `0.8112`
- bridge_final: `0.8214`
- beyond-adjacency subset for `bridge_final`: `0.8511`

## Interpretation

- Hybrid seed retrieval was the meaningful gain over the earlier Bridge v2 baseline.
- Section scoring and diversification did not provide measurable value once isolated in the streamlined study.
- The repo therefore privileges `bridge_final` and keeps earlier sweeps mainly for reproducibility and diagnostics.
