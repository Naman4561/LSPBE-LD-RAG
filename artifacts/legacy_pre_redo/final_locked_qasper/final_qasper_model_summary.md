# Final QASPER Model Summary

Legacy pre-redo artifact: this summary preserves the earlier full-split reporting story and is no longer the default serious-redo protocol.

## Final Locked Model

- canonical model: `bridge_final`
- segmentation: `seg_paragraph_pair`
- seed retrieval: hybrid
- dense weight: `1.00`
- sparse weight: `0.50`
- bridge design: Bridge v2 skip-local
- continuity: `idf_overlap`
- no section scoring
- no adaptive trigger
- no reranker
- no diversification

## Final All-Splits Results

- train: `0.8022` evidence hit, `0.2526` seed hit, `0.9855` beyond adjacency over subset size `1107`
- validation: `0.8796` evidence hit, `0.3154` seed hit, `0.9903` beyond adjacency over subset size `414`
- test: `0.8987` evidence hit, `0.3680` seed hit, `0.9910` beyond adjacency over subset size `558`

## Baseline Context

- train: adjacency `0.7779`, bridge_v1 `0.7782`, bridge_v2 `0.7968`, bridge_final `0.8022`
- validation: adjacency `0.8517`, bridge_v1 `0.8517`, bridge_v2 `0.8786`, bridge_final `0.8796`
- test: adjacency `0.8787`, bridge_v1 `0.8787`, bridge_v2 `0.8946`, bridge_final `0.8987`

## Notes

- `seg_paragraph_pair` became the final segmentation after the targeted 50-paper robustness study.
- The strongest gains remain on the beyond-adjacency subset, where the final model reaches `0.9855` on train, `0.9903` on validation, and `0.9910` on test.
- Full split-level details are recorded in the `final_qasper_*_model_results.json` and `final_qasper_*_baseline_compare.json` artifacts.
