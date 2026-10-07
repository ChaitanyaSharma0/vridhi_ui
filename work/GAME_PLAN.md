# VRIDDHI — SAS CU Hackathon Game Plan

## 0. What wins (from the brief)
- **Round 2 = 70% of final.** Word "Approach Note", 20–25 pages (+ appendix), Times New Roman 12, single spacing.
  | Section | Marks | What they want |
  |---|---|---|
  | Problem definition / Analytics objective | 10 | Sharp, scoped, deep |
  | Approach | 15 | Overall flow + **why** each method |
  | **Data exploration** (issues, fixes, derivation, consolidation) | **25** | Find every data issue, fix it, derive new variables |
  | **Data analysis** (stats / data mining / ML) | **30** | Descriptive + predictive + prescriptive |
  | Results & conclusions | 10 | Linked back to the problem |
  | Implications | 10 | For students, employers, universities, society |
- **Round 3 = 30%.** 15–25 slides, 10 min + 3–5 min jury Q&A. Q&A (25) + communication (25) + storyline (20) + conclusions (15) + graphics (10) + slide flow (5).
- **Use SAS** (VFL → Visual Analytics report + Model Studio pipeline) for visible edge; Python for heavy cleaning / text mining. Excel discouraged.

## 1. Problem statement (one line)
**"What does it actually take to get hired, paid well and grow as a data scientist in India — and how far is a given aspirant from it?"**

### Analytics objective
Using 2024–25 Indian data-science/analytics job data and workforce trait data, (1) quantify what the market **demands and pays for** (roles, skills, experience, cities), (2) identify which measurable **technical skills drive junior salary hikes** and which **personality traits drive senior success**, and (3) combine both into a **readiness & gap score** that tells an aspirant which role to target, what to improve first, and what salary to expect.

## 2. Structure — our 3 modules = 3 analysis pillars
| Pillar | Data | Question | Methods |
|---|---|---|---|
| **1. Market Intelligence** | DataScience Jobs, Analytics Jobs | Who hires, for what roles, which skills, at what pay, where? | Cleaning & standardisation, role-family text clustering, skill extraction + frequency, **association rules / co-occurrence** (skill bundles), salary ladder regression (title × experience), **ordinal salary-band model** (skills + experience + city + role) with skill premiums |
| **2. Success Drivers** | JDS Skill Traits, SDS Personality Traits | What separates high-hike juniors and successful seniors? | Group comparisons (t / Mann-Whitney + effect sizes), correlation, **logistic regression (odds ratios)**, **decision tree (rules)**, random forest / gradient boosting, cross-validated AUC, **k-means personas** |
| **3. Readiness & Matching** | All 4 (linked via a skill taxonomy) | For an aspirant: which role fits, what gap to close first, what salary? | Skill taxonomy mapping 5 JDS dimensions ↔ market key_skills, **demand-vs-impact quadrant**, readiness score (model probability), gap priority = model impact × market demand, role recommendation + salary band prediction |

**Key linking idea (consolidation marks):** the 4 files share no key. We bridge them through a **skill taxonomy** — the 5 JDS skill areas (big data, maths-stats, coding, AI/ML, dashboard & storytelling) are mapped to keywords in Analytics Jobs' key_skills. That lets us compare *what the market asks for* with *what actually drives salary hikes*.

## 3. Report outline (Word, ~22 pages)
1. Problem definition & objective (1.5 p)
2. Approach — flow diagram, why each method, tools (SAS VA, Model Studio, Python) (2 p)
3. Data exploration (6–7 p) — data audit table per file, issues found → fix → impact; derived variables; consolidation via skill taxonomy
4. Analysis (8–9 p) — Pillar 1, Pillar 2, Pillar 3 (each: method, result chart, interpretation)
5. Results & conclusions (1.5 p) — 6–8 headline findings with numbers
6. Implications (1.5 p) — students, employers, universities/training providers, policy
Appendix — code, model outputs, SAS screenshots, full tables

## 4. Deck (≈18 slides)
Title → The question → Data & its problems → How we cleaned/linked it → Market: roles & pay ladder → Market: skills that pay → Skill bundles → Junior success drivers → Senior success traits → Personas → Demand vs impact quadrant → Readiness score demo (one aspirant) → Results → Implications → Close.

## 5. Team split (adjust to team size)
- **A – Data & cleaning lead:** run `work/01_clean.py`, upload cleaned files to SAS VFL, write report §3.
- **B – Market analyst:** SAS VA report (Pillar 1 visuals), report §4.1.
- **C – Modeller:** SAS Model Studio pipelines for JDS / SDS / salary band (logistic, tree, GB, model comparison), report §4.2.
- **D – Storyteller:** Pillar 3, results, implications, deck + rehearsal.

## 6. Order of work
1. Clean + audit (Python) → cleaned CSVs → upload to VFL.
2. EDA + charts.
3. Models (Python for validation numbers, SAS Model Studio for the official pipeline/screenshots).
4. Pillar 3 linking + readiness score.
5. Write report while models run; deck last; rehearse Q&A.
