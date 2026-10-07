# M11 – Simple rules for senior success (Decision tree)

**Chapter 4: What makes seniors succeed**

## The question
Can senior success be described with a few if-then rules?

## What we did (plain words)
- The same flowchart method as M07, tuned over 32 settings. Best: **depth 4**, at least 12 people per final group.
- Tested on unseen people (50 rounds).

## What we found
**The first question is about openness. The second is about conscientiousness.**
- **Openness ≤ 38.5:** **0 of 52** seniors were rated high success.
- **Openness > 38.5 but conscientiousness ≤ 36.5:** **0 of 16**.
- **Openness > 38.5 and conscientiousness > 36.5:** **85 of 93 (91%)** high success.

**Accuracy on unseen people: AUC 0.94**, 92% correctly classified.

## What it means for the business
A two-gate rule for senior, client-facing roles:
> **"Curious enough? Then disciplined enough? If both, they almost always succeed."**

Neither trait alone is enough. A curious but disorganised senior, or a disciplined but closed-minded one, does not succeed in this data.

## How sure are we
- Very clean splits (no successful seniors at all below the openness cut-off), confirmed by M10 and M12.
- **Limit:** the exact cut-off values are specific to this scoring scale and company. The *two-gate* pattern is the takeaway.

## Files
- `figures/01_decision_tree.png`
- `results/tree_rules.txt`, `results/leaf_summary.csv`
