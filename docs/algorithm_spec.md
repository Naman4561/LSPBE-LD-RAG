# Algorithm Spec: Local Structure-Preserving Bridge Expansion for Long-Document RAG

## 1. Objective

Determine whether lightweight local bridge expansion improves long-document retrieval and downstream QA over:

- standard flat retrieval
- adjacency-only local expansion

The goal is **not** to build a full graph-RAG system. The goal is to test whether document-local structure is enough to recover missing context.

## 2. Core Hypothesis

Long-document RAG fails partly because chunks are treated independently, which breaks:

- adjacency-based context
- entity continuity
- section continuity

A lightweight bridge-expansion method should recover some of this lost structure without the cost of full graph construction.

## 3. Inputs and Outputs

### Inputs

- document `D`
- query `q`
- segmented document `S = {s1, s2, ..., sn}`

### Output

- ranked context set `C_q` of retrieved segments for query `q`

### Optional Downstream Output

- generated answer `a_q`

## 4. Segmentation Choice

Use **section-aware paragraph segmentation**.

### Rules

- one paragraph = one segment by default
- if paragraph is too short (`< 40` words), merge with the next paragraph in the same section
- if paragraph is too long (`> 220` words), split into 2 smaller sentence groups
- never merge across section headings

### Why This Choice

- more semantically natural than fixed-size chunks
- much simpler than semantic chunking
- preserves section structure for bridge features
- keeps the experiment focused on retrieval-time expansion rather than chunking optimization

## 5. Embedding Model

Use `BAAI/bge-base-en-v1.5`.

### Why This Choice

- strong retrieval quality
- lightweight enough for iteration
- stable and commonly used
- good enough to test the bridge-expansion hypothesis without turning the project into embedding-model tuning

## 6. Retrieval Setup

### Base Retriever

1. embed all segments
2. embed query
3. retrieve top-`k` seed segments by cosine similarity

### Held Fixed Across Methods

- segmentation
- embedding model
- retriever
- generator model (if generation is included)
- context budget

This ensures the only changing part is the expansion strategy.

## 7. Baselines

### Baseline 1: Flat Retrieval

- retrieve top-`k` seed segments
- return them directly

### Baseline 2: Adjacency-Only Local Expansion

- retrieve top-`k` seed segments
- for each seed `s_i`, expand to immediate neighbors:
  - `s_(i-1)`
  - `s_(i+1)`
- merge, deduplicate, and truncate to the context budget

### Why This Baseline Matters

This tests whether simple proximity alone is enough, or whether a more selective structure-aware method is needed.

## 8. Proposed Method: Multi-Signal Local Bridge Expansion

### Step 1: Retrieve Seeds

Retrieve top-`k` seed segments from flat retrieval.

### Step 2: Construct Local Bridge Candidates

For each seed segment `s_i`, consider nearby segments within radius `r`:

- `s_(i-r), ..., s_(i-1), s_(i+1), ..., s_(i+r)`

### Step 3: Score Bridges

Compute bridge scores using:

- **Adjacency**: distance-based or binary proximity signal
- **Entity continuity**: named entity or noun phrase overlap between segments
- **Section continuity**: whether both segments belong to the same section or heading group

### Step 4: Select Bridge Neighbors

For each seed, keep top-`m` nearby segments by bridge score.

### Step 5: Build Final Context

- combine seeds + selected neighbors
- deduplicate
- truncate to context budget

## 9. Bridge Score Formula

Use a simple linear score first:

`BridgeScore(s_i, s_j) = α * Adjacency(s_i, s_j) + β * EntityOverlap(s_i, s_j) + γ * SectionContinuity(s_i, s_j)`

### Initial Weights

Start with:

- `α = 1`
- `β = 1`
- `γ = 1`

No aggressive tuning in the MVE.

## 10. Why Choose `k=5`, `r=1`, and Top 1–2 Bridge Neighbors per Seed

These are MVE values, chosen to keep the method interpretable and controlled.

### Why `k=5`

- large enough to avoid over-relying on one lucky segment
- small enough to keep context focused and make comparisons interpretable
- a common practical retrieval size for first-pass QA experiments
- if `k` is too small, results become unstable
- if `k` is too large, the expansion effect gets diluted because flat retrieval already retrieves too much context

So `k=5` gives a middle ground:

- enough recall
- still sensitive to whether expansion helps

### Why `r=1`

- the hypothesis is about document-local structure
- the clearest first test is whether immediate neighbors matter
- radius 1 minimizes noise and keeps expansion truly local
- larger radius values make it harder to tell whether gains come from structural recovery or just adding more context

So `r=1` is the cleanest first test of immediate local structure.

### Why Top 1–2 Bridge Neighbors per Seed

- encourages selective expansion rather than context flooding
- expanding too many neighbors turns the method into crude windowing
- limiting to 1–2 neighbors forces bridge scoring to matter
- keeps context size manageable and fair versus adjacency-only expansion

## 11. Ablation Plan

Compare:

1. flat retrieval
2. adjacency-only expansion
3. adjacency + entity continuity
4. adjacency + section continuity
5. adjacency + entity continuity + section continuity

This identifies:

- whether expansion helps at all
- whether proximity alone is enough
- which structural cues matter most

## 12. Evaluation

### Retrieval-Level Metrics

- Recall@`k`
- MRR
- evidence hit rate (where available)

### Answer-Level Metrics

- Exact Match / F1 (if feasible)
- optional qualitative grounding analysis on a small sample

## 13. Minimum Viable Experiment (MVE)

### MVE Objective

Answer the smallest useful question:

> Does multi-signal local bridge expansion outperform flat retrieval and adjacency-only expansion on a small QASPER setup?

### MVE Dataset

Use **QASPER only**.

#### Why QASPER First

- cleaner long-document setting
- evidence often distributed across multiple parts of a paper
- easier to debug than FinanceBench
- lets you test mechanism validity before moving to noisier documents

### MVE Scope

- **50–100 papers**
- **100–300 QA pairs**

This is enough to see patterns without making debugging painful.

### Methods to Run

1. flat retrieval
2. adjacency-only expansion
3. multi-signal local bridge expansion

### Signals in MVE

Use only:

- adjacency
- entity continuity
- section continuity

Skip discourse continuity for now.

### MVE Deliverables

By the end of the MVE, provide:

- a working QASPER retrieval pipeline
- results for the 3 retrieval settings
- one ablation table
- 3–5 example cases:
  - one where bridge expansion helped
  - one where adjacency-only added noise
  - one where all methods failed

### MVE Success Criteria

The MVE is successful if any of the following are true:

- multi-signal bridge expansion beats flat retrieval
- multi-signal bridge expansion beats adjacency-only expansion
- results reveal a useful pattern (e.g., helps distributed-evidence questions, hurts localized questions, or entity continuity matters more than section continuity)

A mixed result is still useful.

## 14. What Comes After the MVE

### If the MVE Works

- scale to full QASPER
- run more systematic ablations
- test transfer on FinanceBench

### If the MVE Fails

- inspect example failures
- check whether segmentation is too coarse/fine
- check whether bridge signals are too weak
- try `r=2` or adjusted bridge weights

## 15. Immediate Next Tasks

1. build section-aware paragraph segmentation
2. implement flat retrieval with `bge-base-en-v1.5`
3. implement adjacency-only expansion
4. implement bridge scoring with the 3 signals
5. run the MVE on a QASPER subset
