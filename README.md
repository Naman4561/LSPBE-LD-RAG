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
pip install datasets
```

## Convert QASPER

Start with a tiny subset so it is easy to debug:

```bash
python scripts/convert_qasper_hf_to_subset.py --split train --max-papers 2 --max-qas 3 --output data/qasper_train_tiny.json
```

To randomize which papers land in the subset, add `--seed 7`.

## Run MVE

```bash
python scripts/run_mve.py --qasper-path data/qasper_train_tiny.json --max-papers 2 --max-qas 3 --k 5 --radius 1 --top-m 2 --context-budget 20 --embedder hash
```

The script prints JSON metrics for Recall@k proxy, MRR proxy, and evidence hit rate.
