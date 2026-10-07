# Models overview: what we trained and what it says

All models were trained by `run_models.py` on the cleaned data (fixed seed 42, so a rerun gives identical numbers).
- **Rerun everything:** `python models/run_models.py`
- **Rerun selected models:** `python models/run_models.py m03 jds`

The step names are `m00 m01 m02 m03 m04 m05 jds sds m14`. `jds` runs M06–M09 and `sds` runs M10–M13.

Each model folder has:
- `README.md`: plain-language explanation (start here);
- `figures/`: matplotlib charts;
- `results/`: tables;
- `log.txt`: everything the run printed, including tuned settings and full statistical output.

`vfl/` holds plot-ready copies of the tables for SAS Visual Analytics. See `vfl/VFL_GUIDE.md`.

## The story in one table
| # | Model | Chapter | One-line result |
|---|---|---|---|
| M00 | Data exploration | 0. Data | 50 issues found and fixed; two-thirds of "Analytics Jobs" are not analytics roles; 87% of skill lists truncated |
| M01 | Demand profile | 1. Asked for | Coding in 42.8% of postings, more than 2× any other area |
| M02 | Association rules | 1. Asked for | Skills come in bundles (big-data stack, AI stack, SAS + predictive modelling) |
| M03 | Ordinal logistic regression | 2. Paid for | Experience drives pay (×1.56 odds per year); storytelling postings pay *less* (×0.79) |
| M04 | Gradient boosting (4 feature sets) | 2. Paid for | Adding skills does not improve pay prediction; skills alone = guessing |
| M05 | Log-salary regression | 2. Paid for | Pay ladder by title and experience (+11.9% per year; Senior DS +203%); R² 0.59 on unseen data |
| M06 | Logistic regression (juniors) | 3. Rewarded | Maths ×6.2 and storytelling ×3.9 per point; coding not significant; AUC 0.90 |
| M07 | Decision tree (juniors) | 3. Rewarded | First question = storytelling; low storytelling → 7% high hike |
| M08 | Random forest / gradient boosting (juniors) | 3. Rewarded | Not better than logistic regression; same skill ranking |
| M09 | Breadth vs spike | 3. Rewarded | Average skill AUC 0.92 vs best skill 0.59: breadth beats spikes |
| M10 | Logistic regression (seniors) | 4. Rewarded | Conscientiousness and openness dominate; neuroticism only a statistical side-effect |
| M11 | Decision tree (seniors) | 4. Rewarded | Two gates: openness, then conscientiousness → 91% success |
| M12 | Random forest / gradient boosting (seniors) | 4. Rewarded | AUC 0.997, suspiciously clean, so we report the pattern, not the accuracy |
| M13 | K-means personas | 4. Rewarded | "Disciplined explorer" persona succeeds 89%; two personas never succeed |
| M14 | Bootstrap hype gap | 5. The gap | Ranking flips: most-asked coding is 3rd on reward; least-asked maths is 2nd |

## The headline
> **Organisations hire for the skill everyone already has. Coding gets you in the door; maths and storytelling get you ahead. Breadth beats spikes. At senior level, curiosity plus discipline wins.**

## Accuracy summary (unseen data)
| Question | Best model | Score | Baseline |
|---|---|---|---|
| Junior high hike | Logistic regression | AUC 0.90, accuracy 85% | AUC 0.50, 53% |
| Senior success | Random forest | AUC 0.997, accuracy 96% | AUC 0.50, 53% |
| Pay band | Gradient boosting | 38% exact, 80% within one band | 26% exact |
| Salary amount | Log-salary regression | R² 0.59 | 0 |
