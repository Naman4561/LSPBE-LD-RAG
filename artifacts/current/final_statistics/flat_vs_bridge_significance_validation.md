# Flat Vs Bridge Significance: Validation

- split: `validation`
- compared_methods: `flat_hybrid_current` vs `bridge_final_current`
- bootstrap_samples: `2000`
- retrieval_source: `data\qasper_validation_full.json`
- answer_source: `data\qasper_validation_full.json`

## Metric Deltas

- `evidence_hit_rate`: delta `+0.0179` with 95% CI [`+0.0070`, `+0.0299`] and supports a flat lead.
- `evidence_coverage_rate`: delta `+0.0267` with 95% CI [`+0.0153`, `+0.0387`] and supports a flat lead.
- `answer_f1`: delta `+0.0844` with 95% CI [`+0.0632`, `+0.1051`] and supports a flat lead.
- `empty_prediction_rate`: delta `-0.1940` with 95% CI [`-0.2289`, `-0.1592`] and supports a lower flat rate.

## Claim Boundary

- This addendum is a direct paired uncertainty check for the locked flat-vs-bridge comparison only.
- It supports claims about uncertainty around metric deltas on these saved runs.
- It does not reopen model selection or justify any broader claim beyond the compared split and metrics.
