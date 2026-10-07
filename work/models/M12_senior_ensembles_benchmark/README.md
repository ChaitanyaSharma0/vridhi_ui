# M12 – Senior models compared (Random forest, gradient boosting, model comparison)

**Chapter 4: What makes seniors succeed**

## The question
Do flexible ML models predict senior success better, and which traits do they rely on?

## What we did (plain words)
The same set-up as M08: tuned random forest and gradient boosting, nested cross-validation, ROC curves, permutation importance and a confusion matrix.

## What we found
| Model | AUC on unseen data | Accuracy |
|---|---|---|
| **Random forest** | **0.997** | 96% |
| Gradient boosting | 0.988 | 93% |
| Logistic regression | 0.963 | 91% |
| Decision tree | 0.941 | 92% |
| Baseline | 0.50 | 53% |

What the models rely on:
- **Openness** (biggest);
- **conscientiousness**;
- a little agreeableness and extraversion;
- **neuroticism ≈ 0**.

Confusion matrix (random forest): only 6 of 161 seniors misclassified.

## What it means for the business
- The flexible models agree with M10 and M11: **openness and conscientiousness are the core of senior success**, and neuroticism is irrelevant.
- The random forest scores slightly higher because traits combine in a non-linear way: you need *both* gates (see M11).

## A caution we should state ourselves
An AUC of 0.997 is **unusually high** for real personality data. It suggests the dataset is simulated or the success label was partly defined from these traits.
- We therefore present the **pattern**, which traits matter and in what order, and not the near-perfect accuracy, as the result.
- Saying this openly protects us in jury Q&A.

## Files
- `figures/01_roc_curves.png`, `figures/02_model_comparison_auc.png`, `figures/03_permutation_importance.png`, `figures/04_confusion_matrix_best.png`
- `results/model_comparison.csv`, `results/roc_points.csv`, `results/permutation_importance.csv`
