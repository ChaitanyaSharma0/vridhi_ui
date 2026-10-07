# M10 – Which personality traits go with senior success? (Logistic regression)

**Chapter 4: What makes seniors succeed**

## The question
Among 161 senior, customer-facing data scientists (Big Five personality scores), which traits separate those rated **highly successful** in the organisation?

## What we did (plain words)
- Same method as M06: **logistic regression** with all 5 traits together, giving each trait's effect with the others held equal.
- Effects are shown **per standard deviation** (a "typical step up" in that trait), so traits are comparable.
- We also ran each trait **on its own**, to see how the picture changes when the others are included.
- Tuned and tested on unseen people (nested cross-validation, 50 rounds). Checked overlap between traits (VIF; all fine).

## What we found
| Trait | Successful vs other (mean) | Odds ratio per typical step (all together) | Alone |
|---|---|---|---|
| **Conscientiousness** (organised, responsible) | 53.7 vs 35.7 | **26.8×** | 9.7× |
| **Openness** (curious, open to ideas) | 48.5 vs 33.3 | **21.0×** | 10.7× |
| Extraversion (outgoing) | 48.9 vs 36.9 | 3.9× | 3.4× |
| Agreeableness (cooperative) | 47.7 vs 41.1 | 2.5× (not proven, p = 0.056) | 1.9× |
| Neuroticism (anxiety-prone) | 36.1 vs 36.3 | 3.9× | **1.0×, no effect alone** |

**Accuracy on unseen people: AUC 0.96**, 91% correctly classified.

## What it means for the business
**Conscientiousness and openness dominate senior success**: being disciplined *and* curious. Use them in senior / client-facing hiring and promotion assessments, and in leadership development.

## The neuroticism puzzle (don't over-sell it)
- On its own, neuroticism makes **no difference** (both groups average about 36).
- Inside the full model it turns positive. This is a statistical side-effect called *suppression*: it only "matters" after adjusting for traits it is slightly linked to.
- The random forest and gradient boosting **ignore it completely** (M12).

**Our honest position:** neuroticism is **not** a meaningful driver. Don't screen on it.

## How sure are we
- Very strong separation. The odds ratios are large with wide ranges because the groups are almost perfectly separable.
- **Limits:**
  - One company's data.
  - The near-perfect separation (see M12) suggests the data may be simulated or very clean, so we focus on **which traits matter**, not on the exact multipliers.

## Files
- `figures/01_odds_ratios_forest.png`, `figures/02_group_means.png`, `figures/03_trait_correlations.png`, `figures/04_univariate_vs_multivariate.png`
- `results/odds_ratios.csv`, `results/group_means.csv`, `results/trait_correlations.csv`; full model in `log.txt`
