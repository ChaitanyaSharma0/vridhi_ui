# M02 – Which skills are asked for together? (Association rules)

**Chapter 1: What companies ask for**

## The question
Employers rarely want one skill. Which skills come as a **package**?

## What we did (plain words)
This is the supermarket "people who buy bread also buy butter" method, applied to job ads.
- Each posting is a "basket" of skills.
- For every pair of common skills we measured three things:
  - **Support:** how often the pair appears together (share of all ads).
  - **Confidence:** if an ad asks for A, how often it also asks for B.
  - **Lift:** how many times *more often* they appear together than chance. Lift 1 = pure coincidence; lift 10 = ten times more than chance.
- Very generic words ("analytics", "data analysis", "learning", "management") were removed so they don't create meaningless pairs.

## What we found
Clear **skill bundles**:
| Bundle | Example lift |
|---|---|
| Big-data engineering stack: Hadoop + Hive + Spark + Scala | 10–16× |
| AI stack: deep learning + NLP + machine learning | 6–14× |
| Classic analytics: SAS + predictive modelling; R + statistical modelling | about 4.5× |
| Python + machine learning | 4.5×, and very common (6.6% of all ads) |
| Excel + VBA | 9× |

At the skill-area level, coding pairs with everything, but **maths/stats and big data rarely appear together** (lift 0.4).

## What it means for the business
Roles are really defined by 3–4 core skills that travel together. Long wish-list job descriptions can be replaced by **one bundle per role**, which makes postings clearer and attracts better-matched candidates.

## How sure are we
- Pairs are kept only if they appear in at least 1% of ads (50+ postings), so they are not flukes.
- **Limit:** truncated skill lists hide some pairs, so lift is a lower bound.

## If the jury asks
- *"Why lift and not just counts?"* Counts favour skills that are common anyway. Lift shows pairs that are *deliberately* asked for together.

## Files
- `figures/01_top_skill_pairs_lift.png`, `figures/02_skill_network.png`, `figures/03_skill_area_cooccurrence.png`
- `results/skill_pair_rules_all.csv` (every pair), `results/top_25_skill_pairs_by_lift.csv`
- VFL: `../vfl/M02_*.csv` (the network edges can be drawn as a network diagram in SAS VA)
