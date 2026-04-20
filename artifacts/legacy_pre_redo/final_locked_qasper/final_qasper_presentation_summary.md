# Final QASPER Presentation Summary

## Final Locked Model

- segmentation: `seg_paragraph_pair`
- hybrid seed retrieval with dense `1.00` and sparse `0.50`
- skip-local Bridge v2 expansion with `idf_overlap` continuity
- no section scoring, trigger, reranker, or diversification

## Why `seg_paragraph_pair`

- It won the targeted 50-paper segmentation robustness study.
- It improved the final model over paragraph segmentation and also improved the beyond-adjacency slice.

## Train

- final model: `0.8022` evidence hit, `0.9855` beyond adjacency
- adjacency baseline: `0.7779`
- bridge v1 baseline: `0.7782`
- bridge v2 baseline: `0.7968`

## Validation

- final model: `0.8796` evidence hit, `0.9903` beyond adjacency
- adjacency baseline: `0.8517`
- bridge v1 baseline: `0.8517`
- bridge v2 baseline: `0.8786`

## Test

- final model: `0.8987` evidence hit, `0.9910` beyond adjacency
- adjacency baseline: `0.8787`
- bridge v1 baseline: `0.8787`
- bridge v2 baseline: `0.8946`

## Strongest Overall Conclusion

- The final simplified `bridge_final` pipeline remains the strongest method across the full reporting path.

## Strongest Beyond-Adjacency Conclusion

- The clearest gains remain on the subset where the top seed is not already adjacent to the evidence, which is exactly where local bridging should matter.

## What Changed From The Original Proposal

- Bridge v1 did not beat adjacency in the final story, but redesigned Bridge v2 and the final hybrid version did.
- Section structure and other extra v2.1 features did not survive into the final simple model.
- `seg_paragraph_pair` beat the original paragraph segmentation and became the final segmentation choice.
