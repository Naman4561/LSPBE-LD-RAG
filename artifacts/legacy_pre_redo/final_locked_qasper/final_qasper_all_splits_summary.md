# Final QASPER All-Splits Summary

Legacy pre-redo artifact: this file keeps the historical all-splits reporting pass, including train, and should not be treated as the new serious-redo evaluation protocol.

## Locked Final Model

- segmentation: `seg_paragraph_pair`
- hybrid seed retrieval
- dense weight `1.00`
- sparse weight `0.50`
- Bridge v2 skip-local design
- continuity `idf_overlap`
- no section scoring
- no adaptive trigger
- no reranker
- no diversification

## Train

- queries: `2593`
- beyond_adjacency_subset_size: `1107`
- bridge_final evidence_hit_rate: `0.8022`
- bridge_final seed_hit_rate: `0.2526`
- bridge_final beyond_adjacency_evidence_hit_rate: `0.9855`

Baseline comparison:
- adjacency: evidence `0.7779`, beyond `0.9277`
- bridge_v1: evidence `0.7782`, beyond `0.9286`
- bridge_v2: evidence `0.7968`, beyond `0.9711`
- bridge_final: evidence `0.8022`, beyond `0.9855`

## Validation

- queries: `1005`
- beyond_adjacency_subset_size: `414`
- bridge_final evidence_hit_rate: `0.8796`
- bridge_final seed_hit_rate: `0.3154`
- bridge_final beyond_adjacency_evidence_hit_rate: `0.9903`

Baseline comparison:
- adjacency: evidence `0.8517`, beyond `0.9227`
- bridge_v1: evidence `0.8517`, beyond `0.9227`
- bridge_v2: evidence `0.8786`, beyond `0.9879`
- bridge_final: evidence `0.8796`, beyond `0.9903`

## Test

- queries: `1451`
- beyond_adjacency_subset_size: `558`
- bridge_final evidence_hit_rate: `0.8987`
- bridge_final seed_hit_rate: `0.3680`
- bridge_final beyond_adjacency_evidence_hit_rate: `0.9910`

Baseline comparison:
- adjacency: evidence `0.8787`, beyond `0.9391`
- bridge_v1: evidence `0.8787`, beyond `0.9391`
- bridge_v2: evidence `0.8946`, beyond `0.9803`
- bridge_final: evidence `0.8987`, beyond `0.9910`
