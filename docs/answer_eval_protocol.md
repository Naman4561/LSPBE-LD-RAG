# Answer Eval Protocol

Bucket 2 adds one fixed answer-evaluation layer on top of the locked retrieval setup and the Bucket 1 split protocol.

## Scope

- use one fixed answerer across compared retrieval methods
- compare at least `adjacency` vs `bridge_final`
- run `train_fast50` only as a sanity check
- use `validation` for answer comparison
- keep `test` reserved for later final reporting

Bucket 2 does not redesign retrieval, does not sweep many answer models, and does not move outputs outside `artifacts/current/bucket2_answer_eval/`.

## Canonical Runner

Use:

```bash
python scripts/final/run_qasper_answer_eval.py --dataset-path data/qasper_validation_full.json --split validation --methods adjacency,bridge_final --json-out artifacts/current/bucket2_answer_eval/qasper_answer_eval_validation.json --md-out artifacts/current/bucket2_answer_eval/qasper_answer_eval_validation.md --csv-out artifacts/current/bucket2_answer_eval/qasper_answer_eval_validation_per_question.csv
```

Useful flags:

- `--max-questions`: smoke-test a modest subset first
- `--cache-dir`: retrieval cache root, defaults to `artifacts/support/cache/bucket2_answer_eval`
- `--cache-tag`: explicit cache key so smoke and full runs do not overwrite each other

## Gold Answers

The cleaned repo JSON files keep question text and evidence, but not the original answer strings. Bucket 2 therefore reads gold answers from the locally cached original QASPER Hugging Face arrow files when they are available offline.

Supported gold-answer shapes:

- unanswerable
- yes/no
- extractive spans
- free-form answers
- multiple acceptable annotations

## Fixed Answerer

Bucket 2 freezes a deterministic extractive fallback answerer because no practical cached offline QA or generation model was available in the current environment.

The answerer:

- selects from the retrieved context only
- uses one fixed heuristic path for all compared retrieval methods
- keeps boolean handling deterministic
- does not tune per method

## Metrics

Required answer metrics:

- exact match
- token F1

Additional diagnostics:

- yes/no accuracy on yes/no gold questions
- empty prediction rate
- prediction length stats
- retrieval evidence hit rate carried alongside answer metrics

## Subset Reporting

Bucket 2 reports answer metrics by:

- `adjacency_easy`
- `skip_local`
- `multi_span`
- `float_table`
- `question_type`

Treat `float_table` as a coarse subset label, not a perfectly precise category.
