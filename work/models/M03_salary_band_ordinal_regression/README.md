# M03 – What pushes a job into a higher pay band? (Ordinal logistic regression)

**Chapter 2: What companies pay for**

## The question
In Analytics Jobs, salary is given only as 6 ordered bands (0–3, 3–6, 6–10, 10–15, 15–25, 25–50 LPA). With experience, role and city held equal, does asking for a skill change the pay band?

## What we did (plain words)
- **Ordinal logistic regression** is built for outcomes that have an order but are not exact numbers, like star ratings.
- It estimates the **odds of being in a higher band**.
- Inputs: years of experience, role family (compared with Data Analyst), city tier (compared with Tier-1 metros), and the 5 skill-area flags.
- Trained on **5,122 postings**.

**How to read it:** the **odds ratio**.
- Above 1 = pushes pay up; below 1 = pushes pay down.
- If the confidence range crosses 1 (grey dot on the chart), there is no proven effect.

## What we found
| Factor | Odds ratio | In words |
|---|---|---|
| **+1 year of experience** | **1.56×** | The biggest driver; each year raises the odds of a higher band by 56% |
| Risk/Quant, Stats/SAS, Data Scientist roles | 1.8–2.1× | Pay more than Data Analyst roles |
| Business Analyst | 1.40× | Pays more |
| BI / Reporting / MIS | 0.73× | Pays less |
| Tier-2/3 city | **0.31×** | Pays far less than metros |
| Asks for coding | 1.43× | Small premium |
| Asks for AI & ML / maths / big data | 1.25–1.33× | Small premium |
| **Asks for dashboards & storytelling** | **0.79×** | **Pays *less*** |

The prediction chart shows a fresher's chance of a 15+ LPA band climbing from almost 0% to over 90% between 0 and 15 years of experience.

## What it means for the business
At hiring, the market prices **experience, role and city**. Skills move the band only a little, and **storytelling is priced *below* average**. Chapter 3 shows storytelling is one of the strongest predictors of junior growth. That mismatch is our story: **the market under-asks for and under-pays the skill that best predicts growth.**

## How sure are we
- Very large sample, very narrow confidence ranges; all skill effects are statistically significant.
- **Limits:**
  - Bands, not exact salaries.
  - Advertised pay, not actual pay.
  - Association, not cause: storytelling ads may come from lower-paying reporting-style teams. We control for role family (including BI/MIS), but not for everything.

## If the jury asks
- *"Why not ordinary regression?"* Bands are ordered categories, not numbers. Treating "3–6 LPA" as the number 4.5 would invent precision we don't have.

## Files
- `figures/01_odds_ratios_forest.png`, `figures/02_predicted_pay_by_experience.png`
- `results/odds_ratios.csv`, `results/predicted_pay_by_experience.csv`; full model output in `log.txt`
