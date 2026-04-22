# Technical Debt And Next Steps

## Remaining Code Issues

- runner scripts still exist as compatibility wrappers at the root of `scripts/`; they are useful, but they add a small amount of duplication by design
- the repo has only lightweight tests and does not deeply cover all reporting or artifact-writing paths
- some support-path conventions are documented rather than enforced by a single central config module

## Remaining Repo Imperfections

- historical artifacts are still large because reproducibility was prioritized over aggressive deletion
- `artifacts/legacy_pre_redo/` and `scripts/legacy/` remain noisy, even though they are now clearly de-emphasized
- some protocol-era docs still exist alongside the final retrospective layer because they remain valuable as source material

## Highest-Value Next Steps

- add regression tests for the final reporting and significance scripts
- factor repeated repo-root and output-path conventions into a small shared helper
- automate release-snapshot generation so the final summaries and artifact map can be regenerated together
- improve answer extraction on top of the locked final flat retrieval path
- investigate retrieval fixes for partial evidence recovery and multi-span failures
