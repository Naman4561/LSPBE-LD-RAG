# Subset Consistency Report

- validation questions: `1005`
- harness variation within family detected: `false`
- interpretation: subset labels were stable across harnesses for the same family, but varied across segmentation families.
- cause: `skip_local`, `multi_span`, and parts of `float_table` were built from segmentation-specific evidence-to-unit matching rather than from fixed question-level labels.

## Primary Harness Counts By Family

| family | skip_local | multi_span | float_table |
| --- | ---: | ---: | ---: |
| `fixed_120_30` | 330 | 288 | 498 |
| `fixed_160_40` | 300 | 264 | 526 |
| `fixed_220_60` | 277 | 237 | 561 |
| `paragraph` | 337 | 289 | 440 |
| `paragraph_pair` | 340 | 243 | 542 |
| `paragraph_triple` | 378 | 213 | 578 |
| `semantic_balanced` | 223 | 194 | 570 |
| `semantic_coarse` | 182 | 159 | 623 |
| `semantic_lite` | 279 | 243 | 518 |
| `semantic_section_constrained` | 245 | 224 | 540 |

## Corrected Fixed Question-Level Counts

- `skip_local`: `279`
- `multi_span`: `279`
- `float_table`: `440`

## Comparability

T0A.2 subset counts are comparable within a family across harnesses but not fully comparable across families, because the labels were recomputed from segmentation-specific evidence-to-unit matching.
