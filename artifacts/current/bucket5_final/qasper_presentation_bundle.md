# QASPER Presentation Bundle

## Problem

- Goal: recover evidence for long-document QASPER questions and report the final held-out result under the cleaned serious-redo protocol.
- Final Bucket 5 question: with the model locked, what is the true held-out performance, where does it fail, and what is the most defensible 8-minute story?

## Dataset And Protocol

- Held-out reporting split: `test` from `data/qasper_test_full.json`.
- Retrieval is the primary evaluation story; answer evaluation is included as a secondary signal because the local QA layer is still imperfect.
- Locked mainline settings: representation `current`, segmentation `seg_paragraph_pair`, final method `flat_hybrid_current`.

## Method Progression

- The clean validation ladder showed flat hybrid seeds outperforming adjacency and the bridge-family variants on evidence hit and coverage.
- Bucket 4.5 repaired the bridge fairness issue by giving bridge the exact same flat seed stage, then tested always-on and selective repair variants.
- That repair closed the seed-gap fairness objection, but it still did not overturn the flat winner.

## Final Results Story

- Locked final method: `flat_hybrid_current`.
- Comparison baseline: `bridge_final_current`. Preferred Bucket 5 comparator: strongest bridge-family validation baseline from Bucket 4.
- Held-out retrieval: flat hit `0.8890` vs baseline `0.8739`; coverage `0.7862` vs `0.7690`.
- Held-out answer eval: flat EM `0.2074`, F1 `0.3022`, empty rate `0.2419`.

## Main Failure Modes

- wrong seed / retrieval miss: `8` audited examples.
- partial evidence recovery: `8` audited examples.
- multi-span miss: `8` audited examples.

## Limitations

- Answer metrics are informative but secondary because they depend on a locally cached QA layer that can miss even when evidence is present.
- The `float_table` subset is only a coarse proxy for figure/table-linked reasoning difficulty.
- The error audit is compact and presentation-oriented rather than a full annotation adjudication pass.

## Future Work

- Improve the answerer before using answer metrics as a primary selector.
- Add a more explicit evidence-chain analysis for nonlocal and multi-span failures.
- Explore better table/figure handling without reopening the locked Bucket 5 model choice.
