# SAS VFL — what to build (gives us the SAS edge + report screenshots)

## 1. Upload to SAS VFL (Data → Import → Local file)
From `work/clean/`:
| File | Use |
|---|---|
| `analytics_jobs_clean.csv` | Market report + salary-band model |
| `ds_jobs_clean.csv` | Salary ladder report |
| `analytics_skills_long.csv` | Skill demand / word cloud / network |
| `jds_clean.csv` | Junior skills → hike model |
| `sds_clean.csv` | Senior traits → success model + clusters |

Filter for market analysis: `in_core_sample = 1` and `is_analytics_role = 1` (5,663 postings).

## 2. SAS Visual Analytics report (4 pages) — screenshot each page
1. **Market overview** — KPI tiles (postings, companies, openings); bar: openings by job_title (ds); bar: median avg_salary_lpa by job_title (the salary ladder).
2. **Where & how much** — geo/bar: postings by primary_city; 100% stacked bar: salary_band by primary_city; line: median salary_mid_lpa by exp_band.
3. **Skills** — word cloud of `skill` (skills_long, in_core_sample=1); bar: top 25 skills; heat map: role_family × dim_* (mean).
4. **People** — box plots of each JDS skill by salary_hike_high; box plots of each SDS trait by success_high; correlation matrix.
Use the colours: blue #2563EB, green #059669 (good), red #DC2626 (bad).

## 3. SAS Model Studio pipelines — screenshot pipeline + model comparison + variable importance
**Project A: JDS (target salary_hike_high, binary)**
- Data: `jds_clean.csv`; inputs = 5 *_skills columns; reject id and derived columns.
- Partition: 70/30 (or use cross-validation if available).
- Nodes: Data Exploration → Logistic Regression, Decision Tree (max depth 3), Forest, Gradient Boosting → Model Comparison.
- Expect: logistic best (our Python CV AUC ≈ 0.90), forest ≈ 0.88, tree ≈ 0.81.

**Project B: SDS (target success_high)**
- Inputs = 5 traits (raw, not _z). Same nodes + a **Clustering** node (k = 4) on the traits.
- Expect: forest/GB ≈ 0.99, logistic ≈ 0.96, tree ≈ 0.94. Mention small n (161) → risk of overfitting.

**Project C: salary band (Analytics Jobs, filtered as above)**
- Target: create `high_pay = (salary_band_ord >= 5)`; inputs: exp_mid, city_tier, seniority, role_family, has_* skill flags, dim_* flags.
- Nodes: Logistic Regression, Gradient Boosting, Forest → Model Comparison. Expect AUC ≈ 0.84.

## 4. What to capture for the report appendix
Pipeline diagram, model comparison table (AUC, misclassification), ROC chart, variable importance, decision tree diagram, cluster profile chart, each VA page.
