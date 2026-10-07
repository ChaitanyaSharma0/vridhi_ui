# M04 – Do skills help predict pay at all? (Gradient boosting)

**Chapter 2: What companies pay for**

## The question
If we give a powerful machine-learning model everything we know about a posting, does adding the skills improve its salary-band prediction?

## What we did (plain words)
- **Gradient boosting** builds hundreds of small decision trees, each correcting the previous one's mistakes. It is one of the strongest standard ML methods for table data.
- We trained it **four times** with different information:
  1. experience only;
  2. + role, seniority and city;
  3. + all skills (5 areas, 14 tools, skill counts);
  4. skills only.
- **"Trained to the max":** for every version the model's settings were tuned automatically (15 combinations tried). It was then scored on postings it had **never seen** (nested 5-fold cross-validation), so the score is honest.
- Then we **scrambled** each group of inputs one at a time to see how much the model relies on it (permutation importance).

## What we found
| Information given | Exact band correct | Within one band |
|---|---|---|
| Guessing the most common band | 25.7% | 69.6% |
| **Experience only** | **35.9%** | 79.4% |
| + role, seniority, city | **38.4%** | 80.4% |
| + all skills | 37.9% | 80.9% |
| Skills only | 25.5%, no better than guessing | 67.2% |

What the model relies on, by how much its accuracy drops when the input is scrambled:
- **Experience 0.50**
- skills 0.05
- role 0.02
- seniority 0.01
- city 0.01

## What it means for the business
**Skills listed in a posting carry almost no information about the pay offered.** Pay is set by experience, with role and city as small adjustments. A long skill list doesn't buy a higher salary, so skills are not where organisations put their money at hiring.

## How sure are we
- Nested cross-validation means no score is inflated by tuning on the test data.
- The "skills add nothing" result holds in this flexible model *and* the simple one (M03).
- **Limit:** pay bands are coarse, which caps how accurate any model can be.

## If the jury asks
- *"35% accuracy is low. Is the model bad?"* No. The low ceiling *is* the finding: postings don't contain the information that sets pay beyond experience. Within one band it is right 80% of the time.

## Files
- `figures/01_model_comparison.png`, `figures/02_grouped_importance.png`
- `results/model_comparison.csv`, `results/grouped_permutation_importance.csv`; tuned settings in `log.txt`
