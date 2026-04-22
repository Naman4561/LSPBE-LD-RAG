# LSPBE-LD-RAG

Long-document evidence retrieval for QASPER, ending in a retrieval-first serious-redo workflow whose final selected method is `flat_hybrid_current`.

## Final State

The repo's final selected path is locked:

- final method: `flat_hybrid_current`
- comparison baseline: `bridge_final_current`
- representation: `current`
- segmentation: `seg_paragraph_pair`
- selection split: `validation`
- final report split: `test`

The important conclusion did not come from a single experiment. It came from a protocol reset plus a sequence of increasingly narrower studies:

- Bucket 1 reset split roles and subset labeling.
- Bucket 2 added an answer-eval layer but kept retrieval primary.
- Bucket 3 checked structure-aware representation and did not overturn the mainline.
- Bucket 4 selected `flat_hybrid_current` on validation.
- Bucket 4.5 repaired bridge fairness and still did not overturn the Bucket 4 winner.
- Bucket 5 confirmed the same winner on held-out test.
- Bucket 6 cleaned the repo, archived clutter, and added a direct flat-vs-bridge paired-bootstrap addendum.

## Start Here

Read these first if you want the final story instead of the full research trail:

- [docs/final_research_record.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/docs/final_research_record.md)
- [docs/final_repo_guide.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/docs/final_repo_guide.md)
- [docs/retrospective_analysis.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/docs/retrospective_analysis.md)
- [artifacts/current/final_project_summary.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/current/final_project_summary.md)
- [artifacts/current/final_statistics/flat_vs_bridge_significance_summary.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/current/final_statistics/flat_vs_bridge_significance_summary.md)
- [artifacts/ARTIFACTS_MAP.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/ARTIFACTS_MAP.md)

## Canonical Repo Layout

- `src/lspbe/`: library code for retrieval, protocol handling, studies, and reporting.
- `scripts/final/`: canonical rerun and release-prep scripts.
- `scripts/studies/`: important serious-redo studies that led to the final decision.
- `scripts/diagnostics/`: environment and sanity helpers.
- `scripts/utilities/`: format conversion and other support utilities.
- `scripts/legacy/`: preserved pre-redo and superseded runners.
- `artifacts/current/`: final serious-redo artifacts and release summaries.
- `artifacts/support/`: caches and logs kept separate from headline artifacts.
- `artifacts/archive_serious_redo/`: archived smoke or low-value serious-redo byproducts.
- `artifacts/legacy_pre_redo/`: pre-redo historical artifacts.
- `data/`: canonical current datasets and split manifests.
- `data/archive_debug/`: debug-only archived datasets retained for provenance.

Compatibility wrappers remain in `scripts/` so older commands still resolve, but the categorized subfolders are now the canonical script locations.

## Canonical Commands

```bash
C:\Users\naman\AppData\Local\Programs\Python\Python39\python.exe scripts/diagnostics/run_env_preflight.py
C:\Users\naman\AppData\Local\Programs\Python\Python39\python.exe scripts/final/audit_local_models.py
python scripts/final/build_qasper_protocol_assets.py
python scripts/final/run_qasper_protocol_sanity_check.py --also-validation
python scripts/studies/run_qasper_model_selection_study.py --dataset-path data/qasper_validation_full.json
python scripts/studies/run_qasper_bridge_repair_study.py --validation-dataset-path data/qasper_validation_full.json --smoke-dataset-path data/qasper_train_fast50.json
python scripts/final/run_qasper_final_reporting_bundle.py --dataset-path data/qasper_test_full.json
python scripts/final/run_flat_vs_bridge_significance.py
```

## Where To Look For Results

- [artifacts/current/final_project_summary.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/current/final_project_summary.md)
- [artifacts/current/bucket5_final/bucket5_final_summary.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/current/bucket5_final/bucket5_final_summary.md)
- [artifacts/current/final_statistics/flat_vs_bridge_significance_summary.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/artifacts/current/final_statistics/flat_vs_bridge_significance_summary.md)
- [docs/retrospective_analysis.md](/c:/Users/naman/OneDrive/Documents/GitHub/LSPBE-LD-RAG/docs/retrospective_analysis.md)

## Legacy And Archived Material

- `artifacts/legacy_pre_redo/` preserves the older project story before the serious redo.
- `artifacts/archive_serious_redo/` preserves smoke or low-value redo byproducts that are worth keeping but not worth foregrounding.
- `docs/archive/` keeps older plan documents that are still useful for provenance.
- `data/archive_debug/` keeps debug-only dataset slices used by superseded scripts.
