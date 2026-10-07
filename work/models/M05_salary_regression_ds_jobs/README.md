# M05 – The pay ladder in actual rupees (Linear regression on DataScience Jobs)

**Chapter 2: What companies pay for**

## The question
DataScience Jobs gives real salary figures (min, average, max) for each company × job title. How much more does each role, each year of experience and each type of company pay?

## What we did (plain words)
- **Linear regression on log salary:** like estimating a house price from size and location. Using the log of salary means each effect comes out as a **percentage** ("+20%"), which is fair across low and high salaries.
- **Robust errors (HC3)** keep the confidence ranges honest even though pay varies more for some roles.
- Inputs: job title (compared with Data Analyst), minimum experience, company size (by number of openings) and company type (IT services vs product/captive).
- 1,590 rows (placeholder employers such as "Confidential" excluded).
- **Check:** a tuned random forest was trained on the same data to see whether a flexible model does better.

## What we found
The model explains **60% of salary differences** (R² = 0.60).

| Factor | Salary vs a Data Analyst at a large IT-services firm |
|---|---|
| **+1 year minimum experience** | **+11.9%** |
| Senior Data Scientist | **+203%** (about 3×) |
| Senior Data Engineer | +141% |
| Data Scientist | +136% |
| Data Engineer | +100% |
| Data Architect | +78% |
| Senior Business Analyst | +73% |
| Machine Learning Engineer | +72% |
| Business Analyst | +49% |
| Senior Data Analyst | +38% |
| Product / captive company (vs IT services) | +21% |
| Mid-size / small hirer (vs large) | −12% / −16% |

**Simple vs flexible:** on unseen data the linear regression scores R² 0.588 and the tuned random forest 0.595. They are essentially the same, so the easy-to-read model is enough.

**Pay spread** (how far the advertised maximum sits above the average):
- Data Analyst **62%**, Business Analyst 57%
- Senior Data Engineer **28%**, Senior Data Scientist 30%
- Large hirers 52% spread, average 11.7 LPA; small specialist hirers 28% spread, average 13.6 LPA

## What it means for the business
- Pay is a clear **ladder by title and experience**.
- Product/captive firms pay about 21% more than IT services for the same title.
- Junior titles have the **widest pay ranges**, so pricing for them is the least consistent. That is a lever for pay teams (and a negotiation opportunity for candidates).

## How sure are we
- Robust errors, confidence ranges well away from zero, and cross-validated R² close to the in-sample R².
- **Limit:** these are company-level averages across postings, not individual pay slips.

## Files
- `figures/01_salary_effects.png`, `figures/02_salary_by_title.png`, `figures/03_pay_spread.png`
- `results/salary_effects_pct.csv`, `results/cv_r2_comparison.csv`, `results/pay_spread_*.csv`; full regression table in `log.txt`
