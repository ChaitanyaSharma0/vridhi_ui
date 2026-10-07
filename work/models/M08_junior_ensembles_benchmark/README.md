# M08 – Is the simple model good enough? (Random forest, gradient boosting, model comparison for juniors)

**Chapter 3: What actually gets juniors ahead**

## The question
Would powerful machine-learning models predict junior hikes better than our simple logistic regression? And do they rely on the same skills?

## What we did (plain words)
- **Random forest:** hundreds of trees vote; like asking a crowd instead of one person.
- **Gradient boosting:** trees built one after another, each fixing the last one's mistakes.
- Both were **tuned** (18 and 24 settings tried) and tested on unseen people with nested cross-validation.
- All four models were compared on the same test rounds, plus a "guess the majority" baseline.
- **Permutation importance:** scramble one skill at a time and see how much the model's accuracy drops. A big drop means the model relies on that skill.
- Outputs: ROC curves and a confusion matrix.

## What we found
| Model | AUC on unseen data | Accuracy |
|---|---|---|
| **Logistic regression** | **0.90** | 85% |
| Random forest | 0.89 | 84% |
| Gradient boosting | 0.88 | 83% |
| Decision tree | 0.81 | 77% |
| Baseline (guess majority) | 0.50 | 53% |

What the flexible models rely on:
- **storytelling and maths most**;
- AI/ML and coding much less;
- big data about zero.

Confusion matrix (logistic regression): 65 of 73 high-hike juniors and 51 of 66 low-hike juniors correctly identified.

## What it means for the business
- The **simple, explainable model is the best one**, so we lose nothing by using its easy-to-read odds ratios.
- Three different methods agree on the same ranking: **maths & storytelling > AI/ML > coding > big data.**

## How sure are we
- Agreement across methods is strong evidence the finding isn't an artefact of one technique.
- **Limit:** same as M06 (139 people, one company).

## If the jury asks
- *"Why not use the most complex model?"* We tried it. It wasn't better, and the simple model is the one managers can understand.

## Files
- `figures/01_roc_curves.png`, `figures/02_model_comparison_auc.png`, `figures/03_permutation_importance.png`, `figures/04_confusion_matrix_best.png`
- `results/model_comparison.csv` (incl. tuned settings), `results/roc_points.csv`, `results/permutation_importance.csv`
