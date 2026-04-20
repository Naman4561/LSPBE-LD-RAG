# Bucket 2 Recovery Pass Note

## Scope

- this was a Bucket 2 recovery pass, not a new bucket
- retrieval and bridge logic were left unchanged
- the goal was to use Bucket E run reliability to finish the missing validation answer comparison as far as practical

## Runtime Verification

- interpreter used: `C:\Users\naman\anaconda3\envs\lspbe310\python.exe`
- Python version: `3.10.20`
- preflight status: healthy for long runs
- local model audit status: refreshed audit found one offline QA model, `distilbert-base-cased-distilled-squad`

## Answerer Freeze

- recovery-pass answerer: `local_qa`
- model: `distilbert-base-cased-distilled-squad`
- rationale: a cached offline QA model is now available and loadable, so the recovery pass used one fixed QA answerer rather than the old deterministic fallback

## Cache Reuse Decision

- inspected and reused for context:
  - prior deterministic `train_fast50` cache files
  - prior deterministic validation smoke cache files
  - prior deterministic full-validation `adjacency` cache/output
- not reused for final post-recovery answer scoring:
  - deterministic answer caches, because they were produced by a different answerer
- reused operationally during the recovery pass:
  - resumable local-QA cache at `artifacts/current/bucket2_answer_eval/cache/bucket2_recovery_validation_localqa/`

## Recovery Run Shape

- chunked validation runs:
  - `start_index 0`, `chunk_size 250`
  - `start_index 250`, `chunk_size 250`
  - `start_index 500`, `chunk_size 250`
  - `start_index 750`, `chunk_size 250`
  - `start_index 1000`, `chunk_size 250`
- final consolidation:
  - full-range `--resume` run with the same cache tag to write the required final validation artifacts

## Outcome

- full validation completed for both `adjacency` and `bridge_final`
- retrieval evidence improved under `bridge_final`, but answer EM/F1 did not
- recommendation: keep Bucket 3 retrieval-first and use answer eval only as a weak secondary check for now
