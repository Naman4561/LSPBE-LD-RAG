# Bucket 6.1 Public Path Audit

Bucket 6.1 was a public-safety and portability cleanup pass. The goal was to remove stale protocol wording, replace machine-specific commands in canonical docs, and reduce the chance that future generated reports reintroduce absolute local paths.

## Files Checked

Primary alignment pass:

- `README.md`
- `docs/answer_eval_protocol.md`
- `docs/runtime_run_policy.md`
- `scripts/README.md`
- `docs/final_research_record.md`
- `docs/final_repo_guide.md`
- `docs/what_we_did_and_did_not_do.md`
- `docs/retrospective_analysis.md`

Repo-wide path audit pass:

- public-facing docs under `docs/`
- root `README.md`
- scripts under `scripts/`
- library code under `src/lspbe/`
- a spot check of artifact files under `artifacts/current/` and `artifacts/legacy_pre_redo/`

## Files Changed

- `.gitignore`
- `README.md`
- `requirements.txt`
- `configs/reproduction.template.json`
- `docs/answer_eval_protocol.md`
- `docs/runtime_run_policy.md`
- `docs/bucket6_1_public_path_audit.md`
- `scripts/README.md`
- `scripts/diagnostics/audit_hardcoded_paths.py`
- `scripts/diagnostics/run_env_preflight.py`
- `scripts/final/audit_local_models.py`
- `scripts/final/run_qasper_answer_eval.py`
- `scripts/final/run_qasper_final_reporting_bundle.py`
- `scripts/studies/run_qasper_bridge_repair_study.py`
- `scripts/studies/run_qasper_model_selection_study.py`
- `scripts/studies/run_qasper_structure_repr_study.py`
- `scripts/utilities/sanitize_artifact_paths.py`
- `src/lspbe/run_control.py`
- `src/lspbe/qasper_answer_eval.py`
- `src/lspbe/qasper_bridge_repair.py`
- `src/lspbe/qasper_model_selection.py`

## Patterns Found

Main path-leak patterns discovered during Bucket 6.1:

- absolute Windows filesystem paths
- repo-location strings tied to one local machine layout
- machine-specific interpreter commands
- home-directory references
- generated artifact fields such as `artifact_path`, `source_path`, `cache_dir`, and `snapshot_dir` containing absolute local paths

## What Was Rewritten

- `docs/answer_eval_protocol.md` was fully rewritten to match the final repo truth: answer evaluation is now described as a fixed secondary layer on top of the cleaned retrieval protocol, not as an early Bucket 2 snapshot.
- `README.md` was de-hardcoded by replacing absolute links and Windows interpreter commands with repo-relative links and plain `python scripts/...` invocations.
- `docs/runtime_run_policy.md` was rewritten to use machine-agnostic commands while preserving the runtime guidance around smoke runs, cache tags, resume behavior, and output/cache separation.
- `scripts/diagnostics/run_env_preflight.py` now writes portable path strings in its generated reports instead of exposing the full local interpreter path and repo path layout.
- `scripts/final/audit_local_models.py` now reports cache and snapshot locations in a sanitized portable form rather than full machine-local paths.
- run-manifest generation was updated so the main study/final scripts write repo-relative path fields when the paths live inside the repo.
- answer-eval and study-side metadata handling was updated so common path fields such as `cache_dir`, `artifact_path`, and `source_path` are more portable in future outputs.
- `scripts/diagnostics/audit_hardcoded_paths.py` was added as a lightweight repeatable scanner for obvious hardcoded-path patterns.

## Historical Artifact Cleanup

Bucket 6.1 was later extended to sanitize tracked generated artifacts and archived historical outputs as well:

- tracked files under `artifacts/current/` were rewritten to use repo-relative or home-relative portable paths
- tracked files under `artifacts/legacy_pre_redo/` were rewritten the same way so the repo could be shared publicly without leaking one machine layout
- the sanitizing pass was applied conservatively as a path-text rewrite only; it did not change metrics, results, or conclusions

## Remaining Machine-Specific References

After the tracked artifact rewrite, no tracked non-ignored project files should contain the old machine-local repo path or local interpreter path.

The remaining caveats are operational rather than textual:

- local reruns can still generate machine-specific paths if they are produced by older code outside the updated runners
- oversized local rerun dumps should stay ignored unless they are intentionally curated for release

## Outcome

Bucket 6.1 leaves the public-facing documentation and active runner surface substantially safer to share:

- canonical docs no longer depend on a specific Windows interpreter path
- canonical commands are repo-root-relative and environment-agnostic
- the answer-eval protocol now matches the final project state
- tracked artifacts and archived historical outputs no longer expose the old local machine path layout
- future manifests and diagnostic reports are less likely to reintroduce personal filesystem details
