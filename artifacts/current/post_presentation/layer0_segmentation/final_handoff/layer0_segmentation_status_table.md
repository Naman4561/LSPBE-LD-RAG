# Layer 0 Segmentation Status Table

| family_name | layer0_status | layer1_eligible | role | source_task | reason |
| --- | --- | ---: | --- | --- | --- |
| `semantic_balanced__plain` | `layer1_eligible` | `true` | `lightweight_default` | `T0A.3` | Safest lightweight semantic default after T0A.3 fairness and budget diagnostics. |
| `semantic_coarse__plain` | `layer1_eligible` | `true` | `high_recall` | `T0A.3` | Strongest high-context recall candidate under promoted Layer 0 plain segmentations. |
| `semantic_section_constrained__plain` | `layer1_eligible` | `true` | `section_boundary_control` | `T0A.3` | Promoted hard section-boundary semantic control for later-layer comparison. |
| `fixed_220_60__plain` | `layer1_eligible` | `true` | `fixed_window_control` | `T0A.3` | Best fixed-window control retained for future model-building sweeps. |
| `semantic_lite__plain` | `layer1_eligible` | `true` | `semantic_size_ablation` | `T0A.3` | Retained semantic-size ablation for testing whether gains require coarser units. |
| `paragraph_triple__plain` | `layer1_eligible` | `true` | `paragraph_ablation` | `T0A.3` | Best paragraph-derived ablation after reopening segmentation. |
| `semantic_coarse__structure_lite_caption` | `audit_only` | `false` | `structure_audit_only` | `T0B.2` | Partial BGE verification tied the plain control and did not justify Layer 1 promotion. |
| `semantic_balanced__structure_lite_heading` | `audit_only` | `false` | `structure_audit_only` | `T0B.2` | Technically safe structure-lite finalist but real-embedder verification was not completed. |
| `fixed_220_60__structure_lite_caption` | `audit_only` | `false` | `structure_audit_only` | `T0B.2` | Technically safe audit-only structure-lite control not promoted into Layer 1 defaults. |
| `semantic_lite__structure_lite_heading` | `audit_only` | `false` | `structure_audit_only` | `T0B.2` | Retained only as an audit trail because real-embedder verification was not completed. |
| `paragraph_triple__structure_lite_heading` | `audit_only` | `false` | `structure_audit_only` | `T0B.2` | Retained only as an audit trail because real-embedder verification was not completed. |
| `paragraph_pair` | `historical_control` | `false` | `historical_control` | `T0A.3` | Preserved as the serious-redo historical control but no longer the default backbone. |
| `paragraph` | `historical_control` | `false` | `historical_control` | `T0A.3` | Preserved as a simpler historical baseline only. |
| `fixed_160_40` | `dropped` | `false` | `dropped` | `T0A.3` | Removed from future model-building sweeps after T0A.3. |
| `fixed_120_30` | `dropped` | `false` | `dropped` | `T0A.3` | Removed from future model-building sweeps after T0A.3. |
| `all structure_lite_inline_ref` | `dropped` | `false` | `dropped` | `T0B.2` | All inline-reference-enriched structure-lite variants are preserved historically but dropped from future model-building sweeps. |
| `all mixed_structure_bundle` | `dropped` | `false` | `dropped` | `T0B.2` | All mixed structure bundles displaced useful base chunks under fixed unit budgets and were dropped from future sweeps. |
| `all structure_full_*` | `dropped` | `false` | `dropped` | `T0B.2` | All heavy explicit-structure unit variants are historical only unless Layer 0 is explicitly reopened. |
