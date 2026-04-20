# Answer Eval Resume Smoke Test

- dataset_path: `data/qasper_train_fast50.json`
- split: `train`
- cache_tag: `buckete_resume_proof_train5`
- resume_confirmed: `True`

## Step 1

- Ran the retrofitted answer-eval script on a 2-question chunk.
- computed_this_run: `{"adjacency": 2, "bridge_final": 2}`
- skipped_existing: `{"adjacency": 0, "bridge_final": 0}`

## Step 2

- Re-ran with the same cache tag and a 5-question chunk using `--resume`.
- computed_this_run: `{"adjacency": 3, "bridge_final": 3}`
- skipped_existing: `{"adjacency": 2, "bridge_final": 2}`
- The second run skipped the first 2 completed questions per method and computed only the remaining 3.

