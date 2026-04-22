# Flat Vs Bridge Significance: Held-Out Test

- split: `test`
- compared_methods: `flat_hybrid_current` vs `bridge_final_current`
- bootstrap_samples: `2000`
- retrieval_source: `data/qasper_test_full.json`
- answer_source: `data/qasper_test_full.json`

## Metric Deltas

- `evidence_hit_rate`: delta `+0.0152` with 95% CI [`+0.0069`, `+0.0241`] and supports a flat lead.
- `evidence_coverage_rate`: delta `+0.0173` with 95% CI [`+0.0088`, `+0.0261`] and supports a flat lead.
- `answer_f1`: delta `+0.0679` with 95% CI [`+0.0475`, `+0.0874`] and supports a flat lead.
- `empty_prediction_rate`: delta `-0.2012` with 95% CI [`-0.2309`, `-0.1730`] and supports a lower flat rate.

## Claim Boundary

- This addendum is a direct paired uncertainty check for the locked flat-vs-bridge comparison only.
- It supports claims about uncertainty around metric deltas on these saved runs.
- It does not reopen model selection or justify any broader claim beyond the compared split and metrics.
