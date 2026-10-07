# Data Preparation — Approach

*(Ready for Report §3 "Data Exploration: data derivation, modification, deduction, reduction".)*

## 1. Starting point
We received four files that describe the Indian data-science job market and the people in it:

| File | Rows | Columns | What one row is |
|---|---|---|---|
| DataScience Jobs | 1,602 | 8 | A company × job title, with salary range, minimum experience and number of openings (2024-25) |
| Analytics Jobs | 15,841 | 8 | One job posting: designation, description, key skills, location, experience range, salary band |
| JDS Skill Traits | 139 | 7 | A junior data scientist: five measured skill scores (1-5) and whether they got a high salary hike |
| SDS Personality Traits | 161 | 7 | A senior / client-facing data scientist: Big Five personality scores and success (high/low) |

The brief warns the data is *"public, self-reported or masked … may contain meaningless / misspelled / mistyped entries … outliers and other problems."* Our audit confirmed this, and found more.

## 2. Principles we followed
1. **Never delete silently.** The only rows removed are 1,001 exact duplicate postings. Every other problem is **flagged** with a 0/1 column, so each analysis chooses its sample transparently and the reader can reproduce it.
2. **Keep the original.** Raw fields stay next to their cleaned versions (`job_desig` → `job_title_clean`, `location` → `primary_city`, `key_skills` → `skills`).
3. **Evidence before rules.** Every rule came from profiling the actual values (distinct-value counts, frequency tables, random samples), not from assumptions.
4. **Measure our own accuracy.** Rule-based classifications were checked by hand on independent random samples, and the accuracy is reported.
5. **Everything logged and reproducible.** One script (`01_clean.py` + `role_rules.py`) rebuilds every output; every rule writes the number of rows it touched to the data-quality log.

## 3. Pipeline (10 stages)

```
 Raw files ─► S0 Profile ─► S1 Structure & keys ─► S2 Duplicates ─► S3 Text standardisation
          ─► S4 Parsing & types ─► S5 Validity & consistency ─► S6 Outliers
          ─► S7 Harmonisation (cities, roles, skills, education) ─► S8 Scope flags
          ─► S9 Derived variables & linking taxonomy ─► S10 Validation (11 automatic checks + manual audit)
          ─► Clean CSVs + Excel workbook + data dictionary + quality log
```

| Stage | What it does | Examples of what it caught |
|---|---|---|
| **S0 Profile** | Type, missing %, distinct values, examples for every raw column | 78% of `job_type` missing; 10,097 distinct designations; 1,355 distinct location strings |
| **S1 Structure & keys** | Column names made SAS/SQL-safe; unique keys checked | `reference_no` is **not unique** (134 numbers shared by 276 different rows); JDS/SDS `id`s collide across different people; `maths-stats_skills` hyphen; `' extraversion'` leading space → surrogate `row_id` keys, renamed columns |
| **S2 Duplicates** | Exact and normalised duplicates | 1,001 exact duplicate postings (dropped); 78 near-duplicates after normalisation (flagged); 2,777 possible reposts with a different salary band (flagged for sensitivity checks) |
| **S3 Text standardisation** | Whitespace, encoding, recruiting noise | 3,548 designations padded with "Urgent Hiring", "Walk-in", "@Mumbai", "Top IT MNC", bracketed notes → `job_title_clean`; ';-' bullets in descriptions; employer name variants (BNP Paribas / *bnp paribas india solutions*, HSBC / *Hsbc Technology*); 12 placeholder employers ("Confidential", "Xyz Company", "Data Entry") |
| **S4 Parsing & types** | Text → numbers | "7.8L" → 7.8 LPA; "6-10 yrs" → min/max/mid/width; "10to15" → ordinal band 1-6 + low/high/mid LPA + 15+ LPA target |
| **S5 Validity & consistency** | Business rules | min ≤ avg ≤ max salary (0 violations); minimum salary 0.2 LPA (monthly/stipend entered as annual, 3 rows); max > 6× min (34); "Senior" titles with 0 years' experience (14); 0-3 LPA band with 8+ years required (20, likely undisclosed salary); JDS scores within 1-5 and SDS within 0-100 (0 violations) |
| **S6 Outliers** | IQR / robust z, decided case by case | `num_of_jobs` up to 4,200 (TCS bulk hiring — real, kept, log-transformed); salaries far from their title's norm (e.g. Flipkart Senior DS 82 LPA — kept, flagged, winsorised copy); 21 years' experience (Data Architects — plausible); JDS **ceiling effect** (18-58% of scores are a perfect 5.0) |
| **S7 Harmonisation** | Map messy categories to clean ones | **Cities:** 100+ spellings and localities (Bangalore/Bengaluru, Gurgaon/Gurugram/Cyber City/Udyog Vihar/Sector-62 Noida, Kharadi→Pune, Lower Parel→Mumbai) → canonical cities and metro areas, tier, multi-city flag; states and "Anywhere Inindia" → *Anywhere in India*; 184 overseas-only postings flagged. **job_type:** 5 spellings of one value merged. **Skills:** 8,462 raw tokens → synonyms merged (ML → machine learning, PowerBI → power bi, Base SAS → sas), 122 spelling variants auto-merged, 965 junk tokens removed (numbers, quotes, whole sentences), 2,153 non-skills split out (education: MBA/B.Com; job meta: fresher/BPO/non-voice; soft skills). **Roles:** 10,097 designations → 22 role families + seniority (5 levels) |
| **S8 Scope flags** | Decide what belongs in each analysis | 9,673 non-analytics roles inside "Analytics Jobs" (software, BPO, HR, sales, medical coding…); 166 spam postings (data entry / work from home); missing (3,371) and truncated (11,469) descriptions |
| **S9 Derived variables** | New, analysis-ready features | Skills recovered from descriptions (7,526 extra skill mentions, since 87% of skill lists were truncated); 5-dimension skill taxonomy flags; JDS profile features (mean, min, range, weakest, strongest skill); SDS z-scores, emotional stability (= −neuroticism z), dominant trait; company type & scale |
| **S10 Validation** | Prove it worked | 11 automatic checks (all pass) + manual audit of role classification |

## 4. Key decisions and why

**4.1 Role classification — ordered rules, then audited.** Designations are free text ("Senior Manager/AVP - Analytics - KPO - IIT/NIT"). We built ordered keyword rules (`role_rules.py`): specific analytics roles first, then guards for look-alike non-analytics roles (medical-coding "AR Analyst", BPO "Quality Analyst", "SEO Analyst", SAP "Analyst"), and only then the generic word "analyst". When a title says nothing ("Associate", "Process Manager"), skills decide — but an analytics family is assigned only if the posting shows at least two analytics skill dimensions. We refined the rules on three random samples and then measured them on a **fresh, untouched sample of 150 postings, checked by hand: ~91% exact family, ~92% correct on analytics vs. non-analytics** (the split that defines our sample). The remaining errors are genuinely ambiguous titles ("SOC Analyst", "Investment Analyst – Real Estate").

**4.2 Skills — clean, separate, recover.** Skill lists were truncated in 87% of postings. Rather than accept the undercount, we built a 488-skill vocabulary from the clean skill lists and searched the descriptions for it, recovering 7,526 additional skill mentions. Skills, soft skills, education and job tags are now separate columns.

**4.3 Linking four unrelated files.** The files share no key — different companies, different people. We bridged them with a **five-dimension skill taxonomy** that mirrors the JDS measured skills: *big data, maths & statistics, coding, AI & ML, dashboards & storytelling*. Every posting gets a 0/1 flag per dimension (`dim_*`). This lets us compare *what the market asks for* (postings) with *what actually earns a salary hike* (JDS) on the same five dimensions. (In the core sample: coding 39%, AI-ML 19%, dashboards-storytelling 17%, big data 16%, maths-stats 15% of postings.)

**4.4 Salary.** DataScience Jobs gives numeric company-level salaries (used for the salary ladder). Analytics Jobs only gives bands, so we model the band as an ordinal variable and as a binary "15+ LPA" target, and exclude the 20 rows whose band contradicts their experience.

**4.5 Outliers are information, not noise.** Bulk hiring (4,200 openings) and very high salaries at top employers are real market facts, so we keep them, flag them, and give models log/winsorised versions.

## 5. From raw to analysis samples

| File | Raw | After cleaning | Main analysis sample |
|---|---|---|---|
| DataScience Jobs | 1,602 | 1,602 | **1,590** real employers |
| Analytics Jobs | 15,841 | 14,840 (exact duplicates removed) | 14,429 India sample (no spam, no overseas-only, no near-duplicates) → **5,127 core analytics postings** (9 analytics families) → 5,122 for salary models |
| JDS Skill Traits | 139 | 139 | **139** (balanced: 53% high hike) |
| SDS Personality Traits | 161 | 161 | **161** (balanced: 53% high success) |

Core analytics families: Data Analyst / Analytics 1,232 · Business Analyst 722 · Data Scientist / ML / AI 675 · Data Engineer / Big Data 580 · Risk / Credit / Quant 570 · Statistical Modelling / SAS 475 · BI / Reporting / MIS 388 · Research 302 · Marketing / Web Analytics 120.
Top cities: Delhi NCR 1,419 · Bengaluru 1,361 · Mumbai 892 · Pune 367 · Chennai 333 · Hyderabad 326.

## 6. Limitations we state openly
- Skill lists and descriptions are truncated; skill counts are lower bounds.
- Salary in Analytics Jobs is banded, not exact; the 0-3 LPA band likely mixes low pay with undisclosed salaries.
- Role classification is rule-based (~91-92% accurate on an independent audit).
- JDS and SDS are small (139, 161) and come from single companies; personality scores are normalised, so only relative comparisons are meaningful. Strong ceiling effects in JDS scores.
- The four files cannot be joined record by record; the skill taxonomy links them at the level of skill dimensions, not people.

## 7. Outputs (folder `work/`)
| File | Contents |
|---|---|
| `clean/ds_jobs_clean.csv`, `clean/analytics_jobs_clean.csv`, `clean/jds_clean.csv`, `clean/sds_clean.csv` | Clean, analysis-ready data (upload these to SAS VFL) |
| `clean/analytics_skills_long.csv` | One row per posting × skill (for skill-demand charts, word clouds, association rules) |
| `clean/Vriddhi_Clean_Data.xlsx` | All of the above + data dictionary + quality log in one workbook |
| `outputs/data_quality_log.md` / `.csv` | Every issue, rows affected, treatment |
| `outputs/data_dictionary_full.csv` | Every column of every clean file: origin, type, description, missing %, distinct values |
| `outputs/profile_raw.csv` | Raw column profile (before cleaning) |
| `outputs/role_classification_audit_sample.csv` | The 150 postings used for the manual audit |
| `01_clean.py`, `role_rules.py` | The reproducible pipeline |
