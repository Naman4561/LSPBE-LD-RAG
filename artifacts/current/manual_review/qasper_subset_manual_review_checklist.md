# QASPER Subset Manual Review Checklist

## adjacency_easy

- Should look like all gold evidence is inside one immediate local neighborhood.
- Red flags: evidence ids spread across distant segments or multiple far-apart regions.

## skip_local

- Should include at least one distance-2-or-more jump between gold evidence segments.
- Red flags: only one segment, or only tightly adjacent evidence despite the label.

## multi_span

- Should show two or more disjoint local evidence regions.
- Red flags: all evidence sits in one continuous segment block.

## float_table

- Should show figure/table/caption style evidence or evidence-bearing segments with those markers.
- Red flags: label fires only because of broad document context with no obvious table/figure signal in the evidence area.

## question_type

- Should match the first-token heuristic: boolean, what, how, which, or other.
- Red flags: obvious mismatch between the question wording and the assigned coarse type.
