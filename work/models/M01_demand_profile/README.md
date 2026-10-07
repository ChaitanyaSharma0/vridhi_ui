# M01 – What do job postings ask for? (Demand profile)

**Chapter 1: What companies ask for**

## The question
Across the 5,127 core analytics job postings, how often is each of the 5 skill areas asked for? Does it change by role?

## What we did (plain words)
- Counted, for every posting, whether it asks for each skill area: big data, maths & stats, coding, AI & ML, dashboards & storytelling.
- Turned the counts into percentages, with a **95% confidence range**: the band the true value very likely falls in.
- Split the counts by role family and seniority, and listed the 25 most-named individual skills.

This is counting, not a trained model, but it is the baseline every other model is compared against.

## What we found
| Skill area | % of postings asking for it |
|---|---|
| **Coding** | **42.8%** |
| AI & machine learning | 19.5% |
| Dashboards & storytelling | 17.8% |
| Big data | 16.3% |
| Maths & statistics | 15.8% |

- Coding is asked for **more than twice as often** as any other area.
- Most-named single skills: SQL, Python, SAS, machine learning, R.
- By role:
  - Data Engineers ask for big data (80%).
  - Data Scientists ask for AI/ML (86%) and coding (72%).
  - BI/MIS roles ask for dashboards (63%).
  - Even Statistical Modelling roles ask for coding (73%) more than maths (46%).

## What it means for the business
Job postings define a data scientist mainly as **someone who codes**. Maths and storytelling are rarely written down, even for roles that depend on them.

## How sure are we
- The confidence ranges are tiny (±1%), so the ranking is solid.
- **Limit:** 87% of skill lists were cut off ("...") in the raw data. We recovered skills from the descriptions, but the true percentages may be a little higher for every area.

## If the jury asks
- *"How did you decide which skill belongs to which area?"* A documented taxonomy maps 470 skill names to the 5 areas. Every mapping is listed in the database (`map_skill_dimension`).

## Files
- `figures/01_skill_area_demand.png`: the main chart
- `figures/02_role_by_skill_area_heatmap.png`, `figures/03_top_25_skills.png`
- `results/*.csv`; SAS VFL copies are in `../vfl/M01_*.csv`
