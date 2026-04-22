# Bucket 2 Answer Eval Summary

## Original Bucket 2 State

- original fixed answerer: `deterministic_extractive`
- original reason: earlier Bucket 2 work did not have a practical cached offline QA/generation model available to freeze
- completed before recovery:
  - `train_fast50` sanity
  - validation smoke on `150` questions
  - full validation for `adjacency` only
- missing before recovery:
  - full validation for `bridge_final`
  - a defensible full-validation answer-level comparison artifact

## Recovery-Pass Checks

- active interpreter verified in this runtime: `C:\Users\naman\anaconda3\envs\lspbe310\python.exe`
- active Python version verified in this runtime: `3.10.20`
- Bucket E tooling verified:
  - `scripts/run_env_preflight.py` runs successfully
  - `scripts/audit_local_models.py` runs successfully
  - `scripts/run_qasper_answer_eval.py` supports `--resume`, `--overwrite`, `--start-index`, `--chunk-size`, `--save-every`, `--cache-dir`, and `--cache-tag`
- prior Bucket 2 artifacts/caches verified:
  - legacy deterministic cache files exist for `train_fast50`, validation smoke, and full-validation `adjacency`
  - no prior full-validation `bridge_final` cache existed

## Recovery-Pass Answerer Decision

- chosen answerer after recovery: `local_qa`
- frozen model: `distilbert-base-cased-distilled-squad`
- why it was chosen now:
  - the refreshed local model audit found a cached offline QA model
  - offline load succeeded
  - a direct inference smoke check succeeded
- important note:
  - old deterministic answer caches were not reused for the final post-recovery comparison because they belong to a different answerer and would have mixed incompatible answer layers

## Recovery Execution

- cache tag used for the resumed recovery pass: `bucket2_recovery_validation_localqa`
- methods evaluated: `adjacency`, `bridge_final`
- split completed: full `validation`
- execution mode:
  - resumable chunked runs at `start_index` `0`, `250`, `500`, `750`, and `1000`
  - final full `--resume` consolidation pass wrote the required validation artifacts
- final cache state:
  - `adjacency`: `1005 / 1005` questions cached
  - `bridge_final`: `1005 / 1005` questions cached

## Post-Recovery Full Validation Results

### adjacency

- EM: `0.1403`
- F1: `0.1675`
- yes/no accuracy: `0.5588`
- empty prediction rate: `0.4567`
- retrieval evidence hit rate: `0.8517`

### bridge_final

- EM: `0.1353`
- F1: `0.1619`
- yes/no accuracy: `0.5392`
- empty prediction rate: `0.4478`
- retrieval evidence hit rate: `0.8796`

## Interpretation

- did resumed full validation complete: `yes`
- did better retrieval improve answers: `not in this recovery pass`
- answer-level comparison outcome:
  - `bridge_final` improved retrieval evidence hit rate over `adjacency` by about `+0.0279`
  - despite that, `bridge_final` was slightly worse on EM and F1 than `adjacency`
- answer-layer quality assessment:
  - the local QA answerer made the full comparison possible
  - but the answer layer is still weak as a selector because predictions are very short and the empty-prediction rate is still about `45%`
  - this makes the answer layer usable as a secondary diagnostic signal, not as a serious primary model-selection signal

## Bucket 3 Recommendation

- Bucket 2 after recovery is: `usable only as a weak secondary signal`
- recommended Bucket 3 treatment:
  - remain retrieval-first
  - include at most smoke-level or milestone-level answer reruns
  - do not promote full answer-level reruns into the main model-selection loop unless the answerer itself improves materially

## Key Outputs

- final validation JSON: [qasper_answer_eval_validation.json](artifacts/current/bucket2_answer_eval/qasper_answer_eval_validation.json)
- final validation Markdown: [qasper_answer_eval_validation.md](artifacts/current/bucket2_answer_eval/qasper_answer_eval_validation.md)
- final validation CSV: [qasper_answer_eval_validation_per_question.csv](artifacts/current/bucket2_answer_eval/qasper_answer_eval_validation_per_question.csv)
