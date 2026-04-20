# Retrieval Metrics

## Goal

The serious redo keeps retrieval-only evaluation for now, but it moves away from saturated headline metrics and focuses on evidence recovery quality.

## Headline Metrics

These are the primary retrieval-side metrics going forward:

- `evidence_hit_rate`
- `evidence_coverage_rate`
- `seed_hit_rate`
- `first_evidence_rank`

## Definitions

`queries`
- number of evaluated questions

`seed_hit_rate`
- fraction of queries where the seed ranking already contains at least one gold evidence segment
- lower-level diagnostic for how often the initial seed stage touches the right area

`evidence_hit_rate`
- fraction of queries where the final retrieved context contains at least one gold evidence unit
- this remains the clearest retrieval success metric before answer generation is added

`evidence_coverage_rate`
- for each query, compute recovered gold evidence units divided by total gold evidence units
- report the average of that fraction over queries
- this distinguishes partial evidence recovery from fuller evidence recovery

`first_evidence_rank`
- the earliest 1-based seed rank position containing a gold evidence segment
- the aggregate value in result tables is the mean over queries with at least one seed hit
- lower is better
- accompanying rank stats can also report count, median, min, and max

## Secondary Or Legacy Metrics

`recall_at_k`
- retained in raw outputs for compatibility
- currently aligned with seed-stage evidence presence rather than used as a headline claim

`mrr`
- retained in raw outputs for compatibility
- computed from the earliest seed evidence rank
- useful as a diagnostic, not as the main story

## Why These Are Better For The Redo

- they stay focused on evidence, which is what the retrieval layer is supposed to recover
- `evidence_coverage_rate` is harder to saturate than a simple hit flag
- `first_evidence_rank` is more interpretable than a generic MRR number when debugging seed retrieval
- they remain compatible with later answer-generation evaluation without pretending retrieval is the full task
