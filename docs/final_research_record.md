# Final Research Record

## Project Goal

This project studies long-document evidence retrieval for QASPER under a cleaned evaluation protocol. The serious-redo objective was not to produce one more incremental retrieval variant. It was to rebuild the evidence base for the project so that the final claim would be defensible: split roles had to be clean, hard subsets had to be method-independent, validation had to be used for model selection, and held-out test had to be saved for final reporting.

## Dataset And Task

The repo works on QASPER, a long-document question answering benchmark where the retrieval problem is not just finding a relevant paper. The system must recover the specific evidence spans or span neighborhoods that support the answer. The project therefore centers retrieval-first metrics:

- `evidence_hit_rate`
- `evidence_coverage_rate`
- `first_evidence_rank`

Answer evaluation was kept, but it remained secondary because the local answer layer was much less stable and much less interpretable than the retrieval layer.

## Why The Evaluation Was Reset

The earlier workflow mixed development, selection, and reporting roles too loosely. Full-train reporting could no longer serve as clean headline evidence once that split had already informed method choices. Bucket 1 fixed that by redefining split roles and materializing train-side subsets at the paper level.

## Method Progression

Bucket 2 asked whether a fixed answer-eval layer changed the main story. It did not.

Bucket 3 asked whether structure-aware representation should replace the simpler current representation under the locked retrieval backbone. It did not overturn the mainline.

Bucket 4 became the real model-selection stage. On validation, under the locked mainline representation and segmentation, `flat_hybrid_current` beat the bridge-family candidates on evidence hit and evidence coverage. Bucket 4 advanced only the top finalists to answer evaluation and still found the flat model stronger.

Bucket 4.5 asked the most important follow-up question after Bucket 4: was bridge losing only because its seed stage was unfairly weaker? The bridge-repair study repaired that fairness issue by forcing bridge variants to start from the same flat seeds. This removed an obvious objection. But the repaired bridge variants still did not beat the flat baseline on final retrieval quality, so Bucket 5 remained unchanged.

Bucket 5 then locked the final method and evaluated it once on held-out test against a compact bridge-family baseline. The same winner held: `flat_hybrid_current` remained ahead on retrieval-first evidence recovery, while answer evaluation still favored flat but was interpreted as supporting evidence rather than the primary decision rule.

Bucket 6 did not reopen experimentation. It cleaned the repo, archived clutter, rewrote the documentation layer, and added a direct paired-bootstrap flat-vs-bridge significance addendum for validation and test.

## Final Selected Model

- method: `flat_hybrid_current`
- representation: `current`
- segmentation: `seg_paragraph_pair`
- bridge-family baseline for final comparison: `bridge_final_current`

## Main Findings

- The protocol cleanup changed the project's conclusion more than any single modeling tweak did.
- Under the cleaned protocol, flat seed retrieval without local expansion became the strongest final method.
- Bridge repair fixed a real fairness problem at the seed stage, but once repaired it still did not overturn the flat advantage.
- Retrieval remained the most reliable decision layer.
- Answer evaluation was useful for diagnosis and communication, but it stayed secondary because the answerer itself remained imperfect.

Bucket 6's direct paired-bootstrap addendum strengthens the same story. On both validation and held-out test, `flat_hybrid_current` stays ahead of `bridge_final_current` on evidence hit and evidence coverage, with saved confidence intervals in `artifacts/current/final_statistics/`.

## Major Limitations

- The answer layer is still weak and often empty.
- The project compared a narrow set of answerers and kept the answer side deliberately fixed.
- Bridge-family exploration was intentionally stopped once Bucket 4.5 answered the fairness objection.
- Runtime remains heavier than an ideal release repo because the project preserves reproducibility artifacts and historical bundles.

## Future Directions

The most defensible continuation is to start from the locked flat mainline and extend in targeted ways:

- improve answering on top of the current final retrieval stack
- test better evidence aggregation and answer extraction without changing the split protocol
- revisit bridge-style expansion only if it starts from the already-fixed flat seed stage and is justified by a specific hypothesis
- add more automation around release snapshots and artifact indexing
