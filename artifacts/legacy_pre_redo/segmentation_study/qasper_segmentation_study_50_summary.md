# QASPER Segmentation Robustness Study

## Setup

- dataset: `data/qasper_subset_debug_50.json`
- fixed retrieval model: `bridge_final`
- only segmentation varies

## Results

- `seg_paragraph`: evidence `0.8214`, beyond-adjacency `0.9462`, seed hit `0.2551`, segments `1072`
- `seg_paragraph_pair`: evidence `0.8418`, beyond-adjacency `0.9885`, seed hit `0.2857`, segments `760`
- `seg_micro_chunk`: evidence `0.7347`, beyond-adjacency `0.8108`, seed hit `0.2092`, segments `1969`

## Answers

1. does paragraph segmentation remain the best? no, `seg_paragraph_pair` is higher on this study
2. does paragraph_pair improve over paragraph? yes
3. does micro_chunk improve over paragraph? no
4. does the bridge_final gain appear robust across segmentations? yes
5. which segmentation should be used for the final full-QASPER run? `seg_paragraph_pair`
6. should the project keep paragraph segmentation as the canonical default? no
