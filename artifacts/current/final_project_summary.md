# Final Project Summary

The serious QASPER redo ends with `flat_hybrid_current` as the locked final method. Under the cleaned protocol it beat the bridge-family validation baseline, survived Bucket 4.5's bridge-fairness repair check, and stayed ahead of `bridge_final_current` on held-out test.

The final mainline is `representation_mode=current` with `segmentation_mode=seg_paragraph_pair`. Retrieval remained the primary decision layer because it best matched the long-document evidence-recovery problem and remained more trustworthy than the imperfect local answer layer.

Bucket 6 leaves the repo in a release-style state: final scripts are separated from studies and legacy runners, caches and logs are isolated under `artifacts/support/`, smoke clutter is archived, and the direct flat-vs-bridge paired-bootstrap addendum is saved under `artifacts/current/final_statistics/`.
