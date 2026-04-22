# QASPER Presentation Slide Outline

## Slide 1: Problem / Motivation

- Long-document QA depends on retrieving the right evidence, not just producing a fluent answer.
- QASPER is a good stress test because evidence can be nonlocal, multi-span, and table-linked.
- Recommended visual: one question plus a long-paper context sketch.

## Slide 2: Task And Dataset

- Task: retrieve evidence for QASPER paper questions, then score answer quality secondarily.
- Evaluation slices include `skip_local`, `multi_span`, and `float_table`.
- Recommended visual: compact dataset/protocol table.

## Slide 3: Why The Original Setup Was Not Fully Defensible

- Earlier workflow mixed development and reporting roles too loosely.
- Saturated retrieval metrics and repeated split reuse made the story harder to defend.
- Recommended visual: old vs cleaned protocol schematic.

## Slide 4: Protocol Reset

- Validation used only for model selection; test reserved for final reporting.
- Retrieval became the primary selector, with answer eval kept as a secondary signal.
- Recommended visual: split-role timeline.

## Slide 5: Method Ladder And What Changed

- Compared flat, adjacency, bridge_v2, bridge_final, and one fixed-chunk bridge baseline.
- Bucket 4.5 then repaired bridge seeding fairness without reopening the whole search space.
- Recommended visual: model progression figure.

## Slide 6: Final Held-Out Results

- Present `flat_hybrid_current` against one compact context baseline on test.
- Highlight evidence hit, coverage, seed hit, EM, F1, and empty rate.
- Recommended visual: main results table.

## Slide 7: Hard-Subset Results

- Show overall, `skip_local`, `multi_span`, and `float_table`.
- Emphasize where flat stays stronger and where both methods still struggle.
- Recommended visual: subset performance bar chart.

## Slide 8: Error Analysis

- Summarize the final taxonomy: retrieval miss, partial recovery, multi-span, float/table, ambiguity, answerer failure.
- Use one or two curated examples to make the taxonomy concrete.
- Recommended visual: error taxonomy table plus one worked example.

## Slide 9: Limitations

- Local QA answerer is still imperfect, so answer metrics are secondary.
- Figure/table and annotation ambiguity remain real sources of noise.
- Recommended visual: short limitations box.

## Slide 10: Takeaway / Future Work

- The clean protocol changed the conclusion: the final winner is flat, not bridge.
- Bridge fairness mattered, but even repaired bridge did not overturn flat on validation or final reporting.
- Recommended visual: one-sentence takeaway banner plus future-work bullets.
