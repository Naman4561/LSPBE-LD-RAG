# Flat Vs Bridge Significance Summary

- compared_methods: `flat_hybrid_current` vs `bridge_final_current`
- purpose: Final paired-bootstrap addendum for the locked validation and held-out test comparison.

## Validation

- `evidence_hit_rate`: delta `+0.0179` with 95% CI [`+0.0070`, `+0.0299`] and supports a flat lead.
- `evidence_coverage_rate`: delta `+0.0267` with 95% CI [`+0.0153`, `+0.0387`] and supports a flat lead.
- `answer_f1`: delta `+0.0844` with 95% CI [`+0.0632`, `+0.1051`] and supports a flat lead.
- `empty_prediction_rate`: delta `-0.1940` with 95% CI [`-0.2289`, `-0.1592`] and supports a lower flat rate.

## Held-Out Test

- `evidence_hit_rate`: delta `+0.0152` with 95% CI [`+0.0069`, `+0.0241`] and supports a flat lead.
- `evidence_coverage_rate`: delta `+0.0173` with 95% CI [`+0.0088`, `+0.0261`] and supports a flat lead.
- `answer_f1`: delta `+0.0679` with 95% CI [`+0.0475`, `+0.0874`] and supports a flat lead.
- `empty_prediction_rate`: delta `-0.2012` with 95% CI [`-0.2309`, `-0.1730`] and supports a lower flat rate.

## What Can Be Claimed

- Validation and test both show positive flat-minus-bridge deltas on retrieval hit and coverage.
- The held-out test addendum also favors flat on answer F1 and on lower empty-prediction rate.
- The answer layer remains secondary because the project's final decision rule stayed retrieval-first.
- If any interval crosses zero, the correct reading is uncertainty rather than a hard significance claim.
