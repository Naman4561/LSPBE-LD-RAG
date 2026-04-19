# Final Verification Note

- The canonical 50-paper validation was freshly recomputed from the cleaned final codepath.
- The recomputed results match the locked historical expectations to four decimals:
- `adjacency = 0.7704`
- `bridge_v1 = 0.7704`
- `bridge_v2 = 0.8112`
- `bridge_final = 0.8214`
- The direct `run_qasper_final_model.py` and `run_qasper_baseline_compare.py` commands were attempted first, but a one-process bundle was needed in this session because repeated BGE initialization and offline-model handling made the separate commands impractical.
- Full-QASPER execution was prepared but not completed in this session.
- The repo is now ready for presentation and 50-paper reporting.
- The full-QASPER path is documented and ready for a long-running execution pass.
- FinanceBench transfer work can proceed after the full-QASPER run is completed and logged.
