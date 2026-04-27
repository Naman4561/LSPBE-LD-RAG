# Context Efficiency Table

- approximate gold evidence words retrieved is computed as `evidence_coverage × total unique gold evidence words` per question.
- this is an approximation, not an exact span-level overlap.

| family | harness | avg units | avg words | avg fraction paper | hit / 1k words | coverage / 1k words | gold density |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `fixed_120_30` | `simple_hybrid_minimal_adjacency_control` | 16.80 | 1719.0 | 0.5832 | 0.4457 | 0.3786 | 0.0686 |
| `fixed_160_40` | `simple_hybrid_minimal_adjacency_control` | 15.92 | 2048.6 | 0.6840 | 0.3891 | 0.3399 | 0.0625 |
| `fixed_220_60` | `simple_hybrid_minimal_adjacency_control` | 14.87 | 2429.3 | 0.7951 | 0.3363 | 0.3003 | 0.0567 |
| `paragraph` | `simple_hybrid_minimal_adjacency_control` | 17.52 | 1435.2 | 0.4832 | 0.5394 | 0.4517 | 0.0821 |
| `paragraph_pair` | `simple_hybrid_minimal_adjacency_control` | 15.62 | 2265.2 | 0.7480 | 0.3492 | 0.3003 | 0.0565 |
| `paragraph_triple` | `simple_hybrid_minimal_adjacency_control` | 14.64 | 2776.9 | 0.8985 | 0.2899 | 0.2553 | 0.0500 |
| `semantic_balanced` | `simple_hybrid_minimal_adjacency_control` | 13.32 | 2502.1 | 0.8063 | 0.3372 | 0.3038 | 0.0578 |
| `semantic_coarse` | `simple_hybrid_minimal_adjacency_control` | 10.78 | 2976.3 | 0.9225 | 0.2915 | 0.2687 | 0.0534 |
| `semantic_lite` | `simple_hybrid_minimal_adjacency_control` | 15.54 | 1945.9 | 0.6475 | 0.4157 | 0.3620 | 0.0670 |
| `semantic_section_constrained` | `simple_hybrid_minimal_adjacency_control` | 15.05 | 2196.2 | 0.7160 | 0.3761 | 0.3347 | 0.0625 |