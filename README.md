# LSPBE-LD-RAG

Local Structure-Preserving Bridge Expansion for long-document retrieval.

## Implemented components

- Section-aware paragraph segmentation with paragraph merge/split rules.
- Flat retrieval using `BAAI/bge-base-en-v1.5` via sentence-transformers.
- Adjacency-only local expansion.
- Multi-signal bridge expansion using adjacency, entity continuity, and section continuity.
- MVE runner for QASPER subset evaluation (`flat`, `adjacency`, `bridge`).

## Install

```bash
pip install -e .
pip install -e '.[retrieval,dev]'
```

## Run MVE

```bash
python scripts/run_mve.py --qasper-path /path/to/qasper_subset.json --max-papers 100 --max-qas 300 --k 5 --radius 1 --top-m 2 --context-budget 20
```

The script prints JSON metrics for Recall@k proxy, MRR proxy, and evidence hit rate.
