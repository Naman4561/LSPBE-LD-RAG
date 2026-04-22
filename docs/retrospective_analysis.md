# Retrospective Analysis

## Methodological Perspective

The biggest early assumption that turned out to be wrong was that the old workflow's headline numbers still meant what they appeared to mean. Once development and reporting had touched the same data too often, those numbers no longer supported a clean final claim. Bucket 1 mattered because it re-established split discipline.

A second wrong assumption was that the strongest-looking hard cases should be defined around a method family. The serious redo corrected that by building method-independent subset labels.

## Modeling Perspective

The project began with a bridge-heavy intuition: local expansion looked like the right inductive bias for long-document evidence retrieval. That intuition remained competitive, and Bucket 4.5 confirmed that weak seeds had been hurting bridge fairness. But the final lesson was that the simpler flat seed-retrieval path generalized better under the cleaned protocol.

Why did flat win?

- flat's seed stage was already strong enough that later local expansion often added less than expected
- bridge expansion could improve some local cases while still losing enough precision or final ranking quality to fall behind overall
- once the context budget and segmentation were fixed, a better top-20 flat seed set was often more valuable than extra expansion behavior

## Representation Perspective

Bucket 3 looked at structure-aware choices for captions, inline references, and float-linked evidence. That was important because the final story should not pretend those ideas were ignored. But the result was still conservative: the current representation remained the mainline because the structure-aware path did not justify replacing it for the final run.

## Answer-Eval Perspective

Answer evaluation became useful only once it was framed correctly. It introduced a fixed answer layer, kept it method-comparable, and used it as a secondary readout. That made later results easier to communicate without letting answer noise dominate the scientific decision.

Why did the answer layer stay secondary?

- retrieval errors were more directly interpretable
- retrieval metrics aligned better with the project's core long-document evidence problem
- the answerer still failed even when retrieval evidence was present
- empty prediction behavior remained a major confounder

## Engineering And Runtime Perspective

The repo improved a lot during the redo, but it also accumulated research clutter: flat top-level script lists, bucket-local caches mixed with primary artifacts, smoke outputs beside final bundles, debug datasets living next to canonical datasets, and evolving docs that still told yesterday's story.

Bucket 6 addresses that by separating current artifacts, support artifacts, archived smoke material, and legacy pre-redo material.

## Why Flat Won In The End

Every major opportunity for the bridge family to overturn the result was explicitly tested and failed to do so.

- Bucket 3 did not reveal a representation change that rescued bridge.
- Bucket 4 put flat ahead on the actual selection split.
- Bucket 4.5 repaired the bridge seed-fairness objection.
- Bucket 5 re-ran the final comparison on held-out test.
- Bucket 6 added direct saved uncertainty estimates for that exact flat-vs-bridge comparison.

## What Changed The Conclusions

Three things changed the conclusion most:

- split-role cleanup
- retrieval-first selection discipline
- explicit bridge-fairness repair

## What We Would Improve Next

- stronger answering on top of the final flat retrieval path
- better tooling around cache cleanup and release snapshots
- more structured tests for artifact-writing scripts
- if bridge is revisited, do it only from repaired flat seeds and only with a narrow hypothesis
