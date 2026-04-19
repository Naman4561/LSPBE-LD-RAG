# Final QASPER Model Summary

## Canonical Model

- name: `bridge_final`
- seed retrieval: `hybrid`
- dense weight: `1.00`
- sparse weight: `0.50`
- bridge design: Bridge v2 skip-local
- max skip distance: `2`
- top bridge candidate per seed: `1`
- continuity: `idf_overlap`
- section scoring: off
- adaptive trigger: off
- reranker: off
- diversification: off

## Locked 50-Paper Results

- adjacency: `0.7704`
- bridge v1: `0.7704`
- current Bridge v2 baseline: `0.8112`
- final streamlined model: `0.8214`
- beyond-adjacency subset hit rate: `0.8511`

## What Was Removed

- section scoring: removed from the final default because `none`, `current`, and `improved` tied exactly at `0.8214`
- diversification: removed because it tied exactly with no diversification
- adaptive trigger: removed because it was not part of the clean winning streamlined result
- reranker: removed because it was not part of the clean winning streamlined result

## Final Interpretation

- The main improvement over the earlier Bridge v2 baseline came from hybrid seed retrieval.
- The simplest model that preserves the gain is now the canonical default.
- Earlier study scripts remain available for reproducibility, but the repo should be presented around `bridge_final`.
