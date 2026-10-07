# M06 – Which skills get juniors a high salary hike? (Logistic regression)

**Chapter 3: What actually gets juniors ahead. This is the core model.**

## The question
Among 139 junior data scientists (scored 1–5 on five skill areas), which skills separate those who got a **high performance-based salary hike** from those who didn't?

## What we did (plain words)
- **Logistic regression** estimates the odds of a yes/no outcome. It's how a doctor estimates heart-attack risk from age, smoking and blood pressure.
- All 5 skills go in **together**, so each skill's effect is measured *with the other four held equal*.
- Output: an **odds ratio** per skill. "×6" means each extra point on that skill multiplies the odds of a high hike by 6.
- **Trained to the max:** a tuned version (strength of a "brake" against over-fitting, L1 vs L2) tested on unseen people with **nested cross-validation, repeated 10 times = 50 test rounds**.
- Also checked that the skills aren't so similar they confuse each other (VIF; all fine).

## What we found
Simple comparison first:
- High-hike juniors average **4.85 vs 3.81** in storytelling and **4.71 vs 3.83** in maths.
- In big data the two groups barely differ (3.94 vs 3.75).

With all skills together:
| Skill (per +1 point) | Odds ratio | Proven? |
|---|---|---|
| **Maths & statistics** | **6.2×** | Yes (p < 0.001) |
| **Dashboards & storytelling** | **3.9×** | Yes (p < 0.001) |
| AI & machine learning | 3.5× | Yes |
| Big data | 2.7× | Yes |
| **Coding** | **1.8×** | **No** (p = 0.08) |

**Accuracy on unseen people: AUC 0.90** (0.5 = coin flip, 1.0 = perfect), 85% correctly classified.

## What it means for the business
**Coding is what job ads ask for most (M01) and the only skill without a proven link to a high hike once the others are counted.** Maths and storytelling, the two areas ads ask for least, matter most.
> "Coding gets you in the door. Maths and storytelling get you ahead."

**Action:** test maths/stats and storytelling at interview, write them into job descriptions, and develop them in junior training.

## How sure are we
- AUC 0.90 on unseen data across 50 test rounds; the simple model beats or matches random forest and gradient boosting (M08).
- **Limits:**
  - 139 people from **one company**.
  - Association, not cause.
  - Many juniors score a perfect 5 in their strong areas (a ceiling effect).
  - Coding's effect isn't *zero*, just not proven once the others are included. High-hike juniors are better coders too, but so is everyone who is good at everything.

## If the jury asks
- *"Isn't coding important?"* Yes, it's necessary. But it doesn't *separate* the people who grow, because the strong juniors are also strong in maths and storytelling, and those carry the extra signal.

## Files
- `figures/01_odds_ratios_forest.png`, `figures/02_group_means.png`
- `results/odds_ratios.csv` (per point and per standard deviation, with ranges and VIF), `results/skill_correlations.csv`, `results/group_means.csv`; full model in `log.txt`
