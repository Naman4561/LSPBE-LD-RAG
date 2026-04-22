# Bucket 4.5 Bridge Repair Comparison

- baseline_validation_source: `artifacts/current/bucket4_model_selection/qasper_model_selection_validation.json`
- stage1_validation_source: `artifacts/current/bucket4_5_bridge_repair/qasper_bridge_repair_stage1_validation.json`
- stage2_validation_source: `artifacts/current/bucket4_5_bridge_repair/qasper_bridge_repair_stage2_validation.json`

## Overall

- `flat_hybrid_current` (bucket4_baseline): hit `0.8617`, coverage `0.7833`, seed_hit `0.8617`, first_rank `4.1813`
- `bridge_final_current` (bucket4_baseline): hit `0.8438`, coverage `0.7567`, seed_hit `0.7741`, first_rank `3.0707`
- `bridge_from_flat_seeds_current` (bucket4_5_stage1): hit `0.8418`, coverage `0.7647`, seed_hit `0.8617`, first_rank `4.1824`
- `bridge_from_flat_seeds_selective_current` (bucket4_5_stage2): hit `0.8398`, coverage `0.7627`, seed_hit `0.8617`, first_rank `4.1824`

## Key Deltas

- `stage1_vs_flat`: hit `-0.0199`, coverage `-0.0186`, seed_hit `+0.0000`, first_rank `+0.0012`
- `stage1_vs_old_bridge`: hit `-0.0020`, coverage `+0.0080`, seed_hit `+0.0876`, first_rank `+1.1118`
- `stage2_vs_stage1`: hit `-0.0020`, coverage `-0.0020`, seed_hit `+0.0000`, first_rank `+0.0000`
- `stage2_vs_old_bridge`: hit `-0.0040`, coverage `+0.0061`, seed_hit `+0.0876`, first_rank `+1.1118`
- `stage2_vs_flat`: hit `-0.0219`, coverage `-0.0206`, seed_hit `+0.0000`, first_rank `+0.0012`

## Decision Flags

- stage1_reused_exact_flat_seed_stage: `True`
- stage1_closed_seed_hit_gap_vs_old_bridge: `True`
- stage1_improved_vs_old_bridge: `False`
- stage2_helped_vs_stage1: `False`
- bucket5_should_remain_flat: `True`
