# Subset Definitions

## Why These Subsets Changed

The old strongest hard-case slice was tied to retrieval behavior. That makes it awkward as a scientific evaluation subset, because the subset definition itself changes with the method used to inspect it.

The Bucket 1 subsets are method-independent. They depend only on:

- gold evidence
- fixed segmentation
- document-local structure
- question text

That matters because a hard subset should be defined by the dataset, not by the winner.

## Fixed Frame

All subset labels here are defined under the locked Bucket 1 segmentation:

- `seg_paragraph_pair`

The labels are cached for validation and test in:

- `artifacts/current/bucket1_protocol/qasper_subset_labels_validation.json`
- `artifacts/current/bucket1_protocol/qasper_subset_labels_test.json`

## Core Subsets

`adjacency_easy`
- all gold evidence segments fit inside one immediate-neighbor window centered on a gold evidence segment
- operationally: there exists a gold evidence segment such that every other gold evidence segment is within distance 1 of it

`skip_local`
- the gold evidence contains at least one pair of evidence segments with distance 2 or more under the fixed segmentation
- this is the clean replacement for the old method-anchored beyond-adjacency concept

`multi_span`
- the gold evidence occupies multiple disjoint local regions
- operationally: after sorting gold evidence segment ids, there is at least one gap larger than 1 between consecutive evidence segments

`float_table`
- the matched gold evidence text or evidence-bearing segment includes figure/table/caption style signals such as `FIGREF`, `TABREF`, `figure`, `table`, or `caption`
- this is heuristic, but it is still method-independent because it only uses gold evidence and local document structure

`question_type`
- rough categories derived from the first question token:
- `boolean`
- `what`
- `how`
- `which`
- `other`

## Important Notes

- these labels are allowed to overlap
- `skip_local` is intended as a harder tag, not a strict partition
- `multi_span` is especially useful because evidence coverage matters more there than a simple hit flag
- the float/table label is heuristic and should be treated as a structured-evidence proxy until a later bucket adds richer float-aware indexing

## Layer 0 And Layer 1 Guardrail

- segmentation-specific subset labels can still be useful for diagnostics and implementation audits
- for primary cross-family segmentation comparisons, fixed question-level labels are required
- the recommended helper is `lspbe.fixed_subsets.require_fixed_question_level_subset_labels(...)`
- do not silently fall back to segmentation-specific evidence-to-unit matching when the goal is cross-family comparison
