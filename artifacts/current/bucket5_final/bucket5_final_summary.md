# Bucket 5 Final Summary

- locked_final_model: `flat_hybrid_current`
- chosen_context_baseline: `bridge_final_current`
- held_out_dataset: `data/qasper_test_full.json`
- final_retrieval_hit: `0.8890`
- final_retrieval_coverage: `0.7862`
- baseline_retrieval_hit: `0.8739`
- final_answer_EM: `0.2074`
- final_answer_F1: `0.3022`
- final_empty_rate: `0.2419`

## Hard Subset Takeaways

- `skip_local`: flat hit `0.9904` vs baseline `0.9840`, F1 `0.3013` vs `0.2261`.
- `multi_span`: flat hit `0.9891` vs baseline `0.9891`, F1 `0.2971` vs `0.2248`.
- `float_table`: flat hit `0.9443` vs baseline `0.9319`, F1 `0.2764` vs `0.1903`.

## Key Error Categories

- `wrong seed / retrieval miss`: `8`
- `partial evidence recovery`: `8`
- `multi-span miss`: `8`
- `float/table-related miss`: `10`
- `annotation ambiguity / evaluation ambiguity`: `8`
- `answerer failure despite correct evidence`: `8`

## Final Story

Bucket 5 keeps the validation-selected `flat_hybrid_current` model locked, confirms it on the held-out test split against one compact bridge-family baseline, includes answer evaluation as a secondary signal, and shows through a compact audit that the remaining failures cluster around retrieval misses, incomplete evidence recovery, hard multi-span/float-table cases, and answerer mismatches even when evidence is present.
