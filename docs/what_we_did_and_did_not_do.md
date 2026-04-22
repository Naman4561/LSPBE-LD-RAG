# What We Did And Did Not Do

## What We Actually Implemented And Tested

- reset the QASPER split protocol with paper-level train-side partitions
- materialized `train_dev`, `train_lockbox`, and `train_fast50`
- built method-independent subset labels for validation and test
- added a fixed answer-eval layer with consistent metrics
- ran a representation study comparing `current` and `structure_aware`
- ran a validation-only model-selection study across flat, adjacency, bridge-family, and one fixed-chunk baseline
- advanced only the top Bucket 4 finalists to answer evaluation
- ran a dedicated bridge-repair follow-up that forced bridge to reuse flat seeds
- ran a held-out final report with the locked final flat method versus `bridge_final_current`
- audited held-out errors and built presentation artifacts
- added a final paired-bootstrap significance addendum for direct flat-vs-bridge comparison on validation and test
- cleaned and reorganized the repo into final, study, diagnostic, utility, legacy, archive, and support paths

## What We Considered But Did Not Do

- broad new answer-model sweeps
- many new representation families after Bucket 3
- a reopened Bucket 4 or Bucket 5 selection stage in Bucket 6
- a large new bridge-family search after Bucket 4.5
- test-set iterative tuning
- replacing the retrieval-first decision rule with answer F1 as the main selector

## What Remains Future Work

- improve answer quality without breaking the cleaned protocol
- add more formal tests around runner scripts and artifact writers
- investigate targeted retrieval improvements for partial-evidence and multi-span failure modes
- revisit bridge-style expansion only with a clearly justified hypothesis and repaired seed parity from the start
