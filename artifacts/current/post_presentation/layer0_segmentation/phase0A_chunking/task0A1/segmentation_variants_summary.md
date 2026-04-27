# Layer 0 Phase 0A Segmentation Variant Summary

- task: `T0A.1`
- control generalist remains fixed elsewhere: `flat_hybrid_current`
- control bridge remains fixed elsewhere: `bridge_final_current`
- datasets materialized here: `train_fast50`, `train_dev`, `validation`

## qasper_train_fast50

| family | units | avg unit words | length distribution | per-paper unit counts | headings/metadata |
| --- | ---: | ---: | --- | --- | --- |
| `fixed_120_30` | 2590 | 106.22 | `000_080:444, 081_140:2146, 141_220:0, 221_320:0, 321_plus:0` | avg 51.80, median 43.00, p95 114, min 2, max 245 | yes |
| `fixed_160_40` | 1971 | 136.60 | `000_080:269, 081_140:336, 141_220:1366, 221_320:0, 321_plus:0` | avg 39.42, median 32.50, p95 86, min 2, max 187 | yes |
| `fixed_220_60` | 1542 | 174.40 | `000_080:186, 081_140:265, 141_220:1091, 221_320:0, 321_plus:0` | avg 30.84, median 26.50, p95 64, min 2, max 143 | yes |
| `paragraph` | 3315 | 65.88 | `000_080:2218, 081_140:708, 141_220:387, 221_320:2, 321_plus:0` | avg 66.30, median 45.50, p95 220, min 2, max 293 | yes |
| `paragraph_pair` | 2827 | 118.85 | `000_080:1183, 081_140:627, 141_220:576, 221_320:367, 321_plus:74` | avg 56.54, median 35.50, p95 204, min 2, max 268 | yes |
| `paragraph_triple` | 2472 | 159.90 | `000_080:801, 081_140:483, 141_220:503, 221_320:393, 321_plus:292` | avg 49.44, median 29.00, p95 188, min 2, max 248 | yes |
| `semantic_balanced` | 1140 | 191.58 | `000_080:20, 081_140:78, 141_220:761, 221_320:281, 321_plus:0` | avg 22.80, median 19.00, p95 50, min 1, max 111 | yes |
| `semantic_coarse` | 766 | 285.12 | `000_080:9, 081_140:14, 141_220:94, 221_320:358, 321_plus:291` | avg 15.32, median 13.00, p95 33, min 1, max 71 | yes |
| `semantic_lite` | 1726 | 126.54 | `000_080:67, 081_140:1184, 141_220:475, 221_320:0, 321_plus:0` | avg 34.52, median 29.00, p95 78, min 1, max 168 | yes |
| `semantic_section_constrained` | 1425 | 153.27 | `000_080:286, 081_140:208, 141_220:716, 221_320:215, 321_plus:0` | avg 28.50, median 26.00, p95 63, min 2, max 124 | yes |

## qasper_train_dev

| family | units | avg unit words | length distribution | per-paper unit counts | headings/metadata |
| --- | ---: | ---: | --- | --- | --- |
| `fixed_120_30` | 27576 | 104.46 | `000_080:5291, 081_140:22285, 141_220:0, 221_320:0, 321_plus:0` | avg 44.33, median 42.00, p95 86, min 0, max 294 | yes |
| `fixed_160_40` | 21430 | 131.71 | `000_080:3734, 081_140:3943, 141_220:13753, 221_320:0, 321_plus:0` | avg 34.45, median 33.00, p95 66, min 0, max 220 | yes |
| `fixed_220_60` | 16716 | 167.05 | `000_080:2409, 081_140:3193, 141_220:11114, 221_320:0, 321_plus:0` | avg 26.87, median 25.00, p95 52, min 0, max 161 | yes |
| `paragraph` | 33079 | 70.06 | `000_080:21187, 081_140:8232, 141_220:3639, 221_320:21, 321_plus:0` | avg 53.18, median 46.00, p95 107, min 0, max 443 | yes |
| `paragraph_pair` | 27294 | 126.65 | `000_080:9595, 081_140:7015, 141_220:6506, 221_320:3537, 321_plus:641` | avg 43.88, median 38.00, p95 97, min 0, max 408 | yes |
| `paragraph_triple` | 23039 | 170.45 | `000_080:6021, 081_140:4763, 141_220:5270, 221_320:4203, 321_plus:2782` | avg 37.04, median 30.50, p95 86, min 0, max 378 | yes |
| `semantic_balanced` | 12227 | 189.54 | `000_080:260, 081_140:1049, 141_220:7961, 221_320:2957, 321_plus:0` | avg 19.66, median 19.00, p95 37, min 0, max 130 | yes |
| `semantic_coarse` | 8249 | 280.94 | `000_080:175, 081_140:168, 141_220:1115, 221_320:3863, 321_plus:2928` | avg 13.26, median 13.00, p95 25, min 0, max 88 | yes |
| `semantic_lite` | 18383 | 126.07 | `000_080:840, 081_140:12599, 141_220:4941, 221_320:3, 321_plus:0` | avg 29.55, median 28.00, p95 57, min 0, max 198 | yes |
| `semantic_section_constrained` | 15658 | 148.01 | `000_080:3516, 081_140:2669, 141_220:7147, 221_320:2326, 321_plus:0` | avg 25.17, median 24.00, p95 47, min 0, max 144 | yes |

## qasper_validation_full

| family | units | avg unit words | length distribution | per-paper unit counts | headings/metadata |
| --- | ---: | ---: | --- | --- | --- |
| `fixed_120_30` | 11558 | 104.02 | `000_080:2288, 081_140:9270, 141_220:0, 221_320:0, 321_plus:0` | avg 41.13, median 39.00, p95 70, min 9, max 163 | yes |
| `fixed_160_40` | 9008 | 130.77 | `000_080:1635, 081_140:1679, 141_220:5694, 221_320:0, 321_plus:0` | avg 32.06, median 31.00, p95 53, min 9, max 123 | yes |
| `fixed_220_60` | 6994 | 166.07 | `000_080:1023, 081_140:1337, 141_220:4634, 221_320:0, 321_plus:0` | avg 24.89, median 24.00, p95 42, min 7, max 94 | yes |
| `paragraph` | 13474 | 71.92 | `000_080:8377, 081_140:3651, 141_220:1438, 221_320:7, 321_plus:1` | avg 47.95, median 44.00, p95 83, min 7, max 290 | yes |
| `paragraph_pair` | 10979 | 130.47 | `000_080:3569, 081_140:2847, 141_220:2895, 221_320:1435, 321_plus:233` | avg 39.07, median 35.00, p95 73, min 5, max 276 | yes |
| `paragraph_triple` | 9133 | 175.62 | `000_080:2218, 081_140:1814, 141_220:2161, 221_320:1863, 321_plus:1077` | avg 32.50, median 29.00, p95 59, min 4, max 263 | yes |
| `semantic_balanced` | 5130 | 188.91 | `000_080:132, 081_140:499, 141_220:3213, 221_320:1285, 321_plus:1` | avg 18.26, median 17.00, p95 30, min 3, max 74 | yes |
| `semantic_coarse` | 3488 | 277.84 | `000_080:91, 081_140:65, 141_220:549, 221_320:1583, 321_plus:1200` | avg 12.41, median 12.00, p95 20, min 3, max 48 | yes |
| `semantic_lite` | 7706 | 125.76 | `000_080:401, 081_140:5299, 141_220:2004, 221_320:1, 321_plus:1` | avg 27.42, median 26.00, p95 47, min 5, max 111 | yes |
| `semantic_section_constrained` | 6601 | 146.81 | `000_080:1561, 081_140:1114, 141_220:2900, 221_320:1025, 321_plus:1` | avg 23.49, median 23.00, p95 41, min 7, max 80 | yes |

## Notes

- `paragraph_pair` and `paragraph_triple` carry `parent_links` back to the paragraph-family units they were composed from.
- all families preserve heading metadata; semantic variants may span multiple headings, so they keep both a primary heading and `all_heading_paths`.
- fixed-window variants are section-aware word windows, not tokenizer-dependent subword windows.
- semantic chunking remains lightweight and local: no external paid APIs and no embedding model dependency in the chunker itself.

## Artifacts

- manifest: `artifacts/current/post_presentation/layer0_segmentation/phase0A_chunking/task0A1/segmentation_manifest.json`
- design doc: `artifacts/current/post_presentation/layer0_segmentation/phase0A_chunking/task0A1/segmentation_registry_design.md`
