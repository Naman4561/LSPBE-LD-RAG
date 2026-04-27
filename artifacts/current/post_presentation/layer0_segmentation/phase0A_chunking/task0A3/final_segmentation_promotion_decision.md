# Final Segmentation Promotion Decision

## Main Promoted Candidates

- `semantic_coarse`: best overall and stable across harnesses, but keep a caution note that it benefits from larger retrieved contexts.
- `semantic_balanced`: safest lightweight semantic default and strongest corrected nonlocal specialist.
- `semantic_section_constrained`: keep as the hard-boundary semantic variant to test whether section constraints help or hurt later layers.

## Specialist / Control Promoted Candidates

- `fixed_220_60`: best fixed-window control and the only fixed family that stayed close enough to the top semantic group to remain scientifically useful.
- `semantic_lite`: semantic-size ablation for testing whether the gains require coarse units.
- `paragraph_triple`: best paragraph-derived ablation after reopening segmentation.

## Historical Control Only

- `paragraph_pair`: preserved as the serious-redo historical control, but not promoted as a future main candidate.
- `paragraph`: preserved as a simpler historical baseline only.

## Killed For Future Model Building

- `fixed_160_40`
- `fixed_120_30`

Killed here means not used in future model-building sweeps, while still remaining in artifacts for history and control reference.
