# Experiment Chronology

## Bucket 1

- reset the evaluation protocol
- introduced paper-level train-side split roles
- materialized `train_dev`, `train_lockbox`, and `train_fast50`
- created method-independent subset labels and sanity outputs

## Bucket 2

- added a fixed answer-eval layer
- kept retrieval as the main comparison axis
- established empty-rate and token-F1 reporting as secondary diagnostics

## Bucket E

- stabilized the runtime environment
- added preflight and local-model audit reporting
- made long answer-eval runs more resumable

## Bucket 3

- tested structure-aware representation against the current representation
- preserved the mainline representation as `current`

## Bucket 4

- ran the real validation-only method-selection study
- compared flat, adjacency, bridge-family, and one fixed-chunk baseline
- selected `flat_hybrid_current` for the final stage

## Bucket 4.5

- tested whether bridge was losing because of an unfair seed stage
- repaired bridge by forcing it to reuse flat seeds
- found that repaired bridge still did not beat the flat mainline
- left Bucket 5 unchanged

## Bucket 5

- kept `flat_hybrid_current` locked
- ran the final held-out comparison against `bridge_final_current`
- produced the final report bundle, figures, presentation materials, and error audit

## Bucket 6

- reorganized the repo into clear code, artifact, and data taxonomies
- centralized caches and logs under support paths
- archived smoke and debug clutter instead of deleting the research trail
- rewrote the documentation layer around the final truth of the project
- added direct paired-bootstrap flat-vs-bridge significance outputs for validation and test
- left the repo in a release-style snapshot state
