# M07 – Simple rules for junior growth (Decision tree)

**Chapter 3: What actually gets juniors ahead**

## The question
Can we turn the junior data into a few **if-then rules** a manager could use without any maths?

## What we did (plain words)
- A **decision tree** is a flowchart of yes/no questions, like "20 questions" or a bank's loan checklist.
- **Tuned:** we tried 32 settings (depth 2–5, minimum group size, split rule) and kept the best on unseen data. Best: **depth 4**, at least 5 people per final group.
- Tested with nested cross-validation repeated 10 times (50 rounds).

## What we found
**The very first question the tree asks is about storytelling, not coding.**
- **Storytelling ≤ 4.15:** only **3 of 41** juniors (7%) got a high hike.
- **Storytelling > 4.15:** 70 of 98 (71%) got a high hike. Within that group:
  - maths ≤ 3.55: **0 of 9**;
  - maths > 3.55 + coding > 4.65 + big data > 3.15: **41 of 43 (95%)**.

**Accuracy on unseen people: AUC 0.81**, a bit below the logistic regression (0.90), which is normal for a single tree.

## What it means for the business
A rule a hiring manager can remember:
> **"First check storytelling, then maths. Coding only matters once those two are in place."**

## How sure are we
- The tree is less accurate than M06, so we use it to **explain**, not to predict.
- Its message matches M06 and M08, which gives us confidence.
- **Limit:** with 139 people the exact cut-off values (4.15, 3.55) would shift a little with new data. The *order* of the questions is the robust part.

## Files
- `figures/01_decision_tree.png`: the tree picture (great for the report and deck)
- `results/tree_rules.txt` (the rules in text), `results/leaf_summary.csv`
