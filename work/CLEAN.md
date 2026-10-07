# CLEAN.md - exactly what we cleaned

Every change below was made by `01_clean.py` (+ `role_rules.py`, `taxonomy.py`). Row counts come from the data-quality log; every example is a **real row**, pulled automatically from the original file and the cleaned file. An independent script (`verify_against_raw.py`) recomputed every figure from the original files: **58 of 58 checks pass** (see `VERIFICATION.md`).

**Golden rule:** nothing was silently deleted. The only removed rows are 1,001 exact duplicate postings. Everything else is kept and *flagged*, and the original values are kept next to the cleaned ones.


## 1. DataScience Jobs (1,602 rows -> 1,602 rows)

**Salary text -> numbers (all 1,602 rows).**

| company_name   | job_title      | min_salary   | avg_salary   | max_salary   |   min_salary_lpa |   avg_salary_lpa |   max_salary_lpa |
|:---------------|:---------------|:-------------|:-------------|:-------------|-----------------:|-----------------:|-----------------:|
| TCS            | Data Scientist | 4.5L         | 7.8L         | 16.0L        |              4.5 |              7.8 |               16 |
| Accenture      | Data Scientist | 5.8L         | 12.8L        | 23.0L        |              5.8 |             12.8 |               23 |
| IBM            | Data Scientist | 5.3L         | 13.4L        | 25.0L        |              5.3 |             13.4 |               25 |


**`reference_no` is not unique** (134 numbers shared by 276 *different* rows) -> new key `row_id`. Example:

|   reference_no | company_name                | job_title             |
|---------------:|:----------------------------|:----------------------|
|           1024 | Exl India                   | Business Analyst      |
|           1024 | IHS Markit                  | Senior Data Analyst   |
|           1048 | Happiest Minds Technologies | Senior Data Scientist |
|           1048 | InfoStretch                 | Senior Data Engineer  |


**Same employer group under two names** - the units list the same title with different salaries, so they stay separate companies and are linked by a new `company_group` column (13 rows):

| company_name                | company_group   | job_title               |   avg_salary_lpa |   num_of_jobs |
|:----------------------------|:----------------|:------------------------|-----------------:|--------------:|
| HSBC                        | HSBC            | Business Analyst        |             12.1 |           382 |
| BNP Paribas                 | BNP Paribas     | Business Analyst        |             10.7 |           105 |
| bnp paribas india solutions | BNP Paribas     | Business Analyst        |             10.2 |            96 |
| HSBC                        | HSBC            | Senior Business Analyst |             17.1 |           219 |
| bnp paribas india solutions | BNP Paribas     | Senior Business Analyst |             14.6 |            94 |
| BNP Paribas                 | BNP Paribas     | Senior Business Analyst |             15.8 |            82 |


**Placeholder employers flagged** (`is_placeholder_employer`, 12 rows):

| company_name          | job_title        |   avg_salary_lpa |
|:----------------------|:-----------------|-----------------:|
| Freelancer.com        | Data Scientist   |              7.1 |
| Freelance Consultants | Data Scientist   |             10.2 |
| Confidential          | Data Scientist   |              8.5 |
| Xyz Company           | Business Analyst |             12.3 |
| Confidential          | Business Analyst |              8.3 |


**Implausible minimum salary < 1 LPA flagged** (`min_salary_implausible`, 3 rows):

| company_name                     | job_title    |   min_salary_lpa |   avg_salary_lpa |   max_salary_lpa |
|:---------------------------------|:-------------|-----------------:|-----------------:|-----------------:|
| Intelligent Image Management Inc | Data Analyst |              0.2 |              1.4 |              2   |
| Data Entry                       | Data Analyst |              0.2 |              1.7 |              3.4 |
| Hexaware Technologies            | Data Analyst |              0.2 |              6.4 |             14   |


**'Senior' title with 0 years' experience flagged** (`senior_zero_exp`, 14 rows), e.g.:

| company_name   | job_title               |   min_experience |
|:---------------|:------------------------|-----------------:|
| HSBC           | Senior Data Scientist   |                0 |
| Merilytics     | Senior Business Analyst |                0 |
| MetLife        | Senior Business Analyst |                0 |


**Bulk-hiring outliers kept but flagged** (`num_jobs_outlier`, 98 rows) and log-transformed:

| company_name   | job_title        |   num_of_jobs |   log_num_jobs |
|:---------------|:-----------------|--------------:|---------------:|
| TCS            | Business Analyst |          4200 |         8.3431 |
| Accenture      | Business Analyst |          1900 |         7.5501 |
| Genpact        | Business Analyst |          1700 |         7.439  |


## 2. Analytics Jobs (15,841 rows -> 14,840 rows)

**1,001 exact duplicates removed** (every field identical except `s_no`). Example pair:

|   s_no | job_desig                                    | location   | salary   |
|-------:|:---------------------------------------------|:-----------|:---------|
|   1413 | .Net Developer Required at Edynamic- Gurgaon | Gurgaon    | 0to3     |
|  12336 | .Net Developer Required at Edynamic- Gurgaon | Gurgaon    | 0to3     |


**Designation noise stripped** into `job_title_clean` (3,548 rows):

| job_desig                                                              | job_title_clean                                                   |
|:-----------------------------------------------------------------------|:------------------------------------------------------------------|
| Business Analyst(p&c Domain)                                           | Business Analyst                                                  |
| Manual / Automation Tester - Software Test Engineer - Fresher for MNC  | Manual / Automation Tester - Software Test Engineer - Fresher For |
| Openings on Data Analytics with Adobe Analytics (aka Omniture / Siteca | On Data Analytics                                                 |
| Hiring Market Professionals - Paladin Org                              | Market Professionals - Paladin Org                                |
| Fresher (graphics Designer)                                            | Fresher                                                           |
| Analytics Solution Manager Opening                                     | Analytics Solution Manager                                        |


**Experience and salary text parsed** (all rows):

| experience   |   exp_min |   exp_max |   exp_mid | salary   |   salary_band_ord |   salary_low_lpa |   salary_high_lpa |
|:-------------|----------:|----------:|----------:|:---------|------------------:|-----------------:|------------------:|
| 2-5 yrs      |         2 |         5 |       3.5 | 0to3     |                 1 |                0 |                 3 |
| 1-6 yrs      |         1 |         6 |       3.5 | 3to6     |                 2 |                3 |                 6 |
| 4-9 yrs      |         4 |         9 |       6.5 | 3to6     |                 2 |                3 |                 6 |


**Locations mapped to canonical cities / metro areas** (1,355 raw strings):

| location                                                                | primary_city   | cities                      | city_tier    |
|:------------------------------------------------------------------------|:---------------|:----------------------------|:-------------|
| Gurgaon, Mumbai, Bengaluru                                              | Delhi NCR      | Delhi NCR|Mumbai|Bengaluru  | Tier 1 metro |
| Delhi NCR, Faridabad, Gurgaon                                           | Delhi NCR      | Delhi NCR                   | Tier 1 metro |
| Gurgaon(Electronic City)                                                | Delhi NCR      | Delhi NCR|Bengaluru         | Tier 1 metro |
| Noida(Sector-2 Noida)                                                   | Delhi NCR      | Delhi NCR                   | Tier 1 metro |
| Noida(Sector-132 Noida)                                                 | Delhi NCR      | Delhi NCR                   | Tier 1 metro |
| Delhi NCR(Binola), Gurgaon                                              | Delhi NCR      | Delhi NCR|Binola            | Tier 1 metro |
| Noida(Sector-63 Noida)                                                  | Delhi NCR      | Delhi NCR                   | Tier 1 metro |
| Delhi, Delhi NCR, Noida, Gurgaon, Faridabad, Jaipur, Mohali, Chandigarh | Delhi NCR      | Delhi NCR|Jaipur|Chandigarh | Tier 1 metro |


**Overseas-only postings flagged** (184 rows):

| location                     | primary_city   |   is_international |
|:-----------------------------|:---------------|-------------------:|
| Canada, Australia, Singapore | International  |                  1 |
| Germany, Hong Kong           | International  |                  1 |
| Uganda                       | International  |                  1 |
| Kuwait                       | International  |                  1 |


**Skills cleaned** - lower-cased, synonyms/variants merged, junk removed, non-skills separated (education, job tags, soft skills):

| key_skills_raw                                                                 | skills                                           | soft_skills     |   education_mentioned | job_meta_tags                                               |
|:-------------------------------------------------------------------------------|:-------------------------------------------------|:----------------|----------------------:|:------------------------------------------------------------|
| Excel, Word, Management Skills, Typing, Computer, Time Management...           | excel|word|management skills|computer            | time management |                   nan | typing                                                      |
| back office, non voice, backend, transaction processing, claims processing,... | backend|transaction processing|claims processing | nan             |                   nan | back office|non voice                                       |
| international bpo, customer service, international voice, ites, kpo...         | customer service|international voice|ites        | nan             |                   nan | international bpo|kpo                                       |
| part time, freelancing, data entry, present job, work from home...             | nan                                              | nan             |                   nan | part time|freelancing|data entry|present job|work from home |


**Skills recovered from descriptions** because 87% of skill lists were cut off with '...' (7,526 extra mentions):

|   s_no | skills                                                                | skills_from_desc                 |
|-------:|:----------------------------------------------------------------------|:---------------------------------|
|    103 | gap analysis|ux|prototyping|usability|user interface designing        | product management               |
|   6566 | sales management|key account management|strategy|dealing              | management consulting|consulting |
|  11428 | sales forecasting|business development|marketing|cold calling|inbound | outbound|inbound                 |


**10,097 designations -> 22 role families + 5 seniority levels** (manually audited on an independent sample of 150: ~91% exact, ~92% analytics vs non-analytics):

| job_title_clean                                                    | role_family                     | seniority      |   is_analytics_role |
|:-------------------------------------------------------------------|:--------------------------------|:---------------|--------------------:|
| Full Stack Web Developer                                           | Software / IT                   | Mid            |                   0 |
| Out-Patient Coding                                                 | Healthcare RCM / Medical Coding | Mid            |                   0 |
| In A Reputed                                                       | Customer Support / BPO          | Mid            |                   0 |
| Sales Manager Telesales                                            | Sales / Business Development    | Manager / Lead |                   0 |
| Manager - Catalogue & Listings                                     | Product / Project Management    | Manager / Lead |                   0 |
| On Data Analytics                                                  | Data Analyst / Analytics        | Mid            |                   1 |
| Credit Manager - Structured Finance                                | Risk / Credit / Quant Analytics | Manager / Lead |                   1 |
| Vp Analytics - Demand Planning / Scm - Apac & Me- Global Ecommerce | Marketing / Digital / Media     | Leadership     |                   0 |


**Spam postings flagged** (166 rows):

| job_desig                                       |   is_spam |
|:------------------------------------------------|----------:|
| Data Entry Operator                             |         1 |
| Data Management Associate                       |         1 |
| Freelance Content Writers for Political Website |         1 |


**`job_type` - 5 spellings of one value and 76% missing** -> original column kept unchanged, plus a 0/1 job_type_tagged flag:

| raw job_type   |   rows |
|:---------------|-------:|
| nan            |  12011 |
| Analytics      |   2971 |
| analytics      |    746 |
| ANALYTICS      |     64 |
| analytic       |     30 |
| Analytic       |     19 |


## 3. JDS Skill Traits (139 rows -> 139 rows) and SDS Personality Traits (161 -> 161)

- Column `maths-stats_skills` renamed `maths_stats_skills` (hyphen is invalid in SAS/SQL); `salary_hike_high_or_low` -> `salary_hike_high`.
- SDS columns with stray spaces renamed: `' extraversion'` -> `extraversion`, `'success_ classification_ high_low'` -> `success_high`.
- IDs are not unique (JDS: 2 ids shared by 4 different people; SDS: 9 ids shared by 18) -> surrogate `row_id`.
- Range checks: all JDS scores within 1-5, all SDS scores within 17-68; no missing values; targets balanced (53% / 47%).
- **No score was changed.** Ceiling effect documented (18-58% of JDS scores are a perfect 5.0).
- Derived (added, not replacing): skill mean/min/range, weakest/strongest skill; trait z-scores, emotional_stability_z (= -neuroticism_z), dominant trait. No composite indices or tiny segments.


## 4. Full list of issues and treatments (from the data-quality log)


### Analytics Jobs

| Stage | Issue | Rows | Treatment |
|---|---|---|---|
| S2 | Exact duplicate postings (every field equal except s_no) | 1,001 | Dropped (the only rows deleted in the whole pipeline) |
| S2 | Near-duplicates after normalisation (same clean title, skills, city, experience and salary band; repost with another description) | 78 | Flagged is_near_duplicate; excluded from demand counts |
| S2 | Possible reposts (same clean title, skills, city and experience, but a different salary band) | 2,777 | Flagged possible_repost only - kept in the sample (salary differs, may be a genuinely separate vacancy); used as a sensitivity check |
| S3 | job_desig: non-ASCII characters / leading-trailing / repeated spaces | 427 | Normalised |
| S3 | job_description: non-ASCII characters / leading-trailing / repeated spaces | 1,845 | Normalised |
| S3 | key_skills: non-ASCII characters / leading-trailing / repeated spaces | 20 | Normalised |
| S3 | job_description uses ';-' as bullet separators | 1,573 | Converted to sentences |
| S3 | Designations padded with recruiting noise ('Urgent Hiring', 'Walk-in', 'Opening for', '@Mumbai', bracketed notes) | 3,548 | Stripped into job_title_clean (original kept in job_desig) |
| S4 | Experience stored as text ('6-10 yrs') | 14,840 | Parsed to exp_min / exp_max / exp_mid / exp_range_width (years) |
| S4 | Salary only available as 6 text bands ('10to15') | 14,840 | Ordinal salary_band_ord 1-6, band low/high/mid (LPA), high_pay_15plus (target) |
| S5 | Unparseable or inverted experience ranges | 0 | None found |
| S5 | Lowest band (0-3 LPA) with 8+ years minimum experience - likely undisclosed salary coded as lowest band | 20 | Flagged salary_exp_inconsistent; excluded from salary models |
| S5 | Very wide experience ranges (more than 8 years between min and max) | 237 | Kept; exp_mid used with care |
| S7 | job_type: one value spelt 5 ways (Analytics, analytics, ANALYTICS, analytic, Analytic) | 3,273 | Merged to 'analytics' |
| S7 | job_type missing for 76% of the original rows (12,011 of 15,841); 78% after removing exact duplicates - not usable as a classifier | 11,567 | Original column kept unchanged + job_type_tagged (0/1); analytics relevance re-derived from title + skills |
| S7 | location: 1,355 distinct strings, 16% list several cities, variants (Bangalore/Bengaluru, Gurgaon/Gurugram, Mumbai Suburbs, Sohna Road, Hyderabad/Secunderabad), states instead of cities, 'Anywhere Inindia' | 1,355 | Tokenised; 100+ variants mapped to canonical cities / metro areas; states and 'anywhere' -> Anywhere in India; derived primary_city, cities, n_cities, is_multi_city, city_tier |
| S7 | Overseas locations (Dubai, Canada, US, Singapore, Nigeria, Sweden, New Jersey ...) in an India dataset | 184 | Flagged is_international; excluded from the India market sample |
| S7 | key_skills free text: 8,462 distinct tokens after lower-casing | 14,840 | Lower-cased, trimmed, trailing '...' removed, synonym map (ML->machine learning, PowerBI->power bi, Base SAS->sas ...), de-duplicated per posting |
| S7 | Spelling/format variants of the same skill (power bi/powerbi, big data/bigdata, javascript/java script, c / c++ ...) | 122 | Auto-merged by letters-only key to the most frequent spelling |
| S7 | Junk skill tokens (empty, numbers like '1120', stray quotes, whole sentences > 45 chars, single letters) | 965 | Removed |
| S7 | Non-skill tokens mixed into skills: education (MBA, B.Com, B.Tech), job meta (fresher, BPO, non voice, present job), soft skills | 2,153 | Separated into education_mentioned, job_meta_tags, soft_skills; 'skills' keeps technical/domain skills only |
| S7 | key_skills truncated with '...' (87%) - lists are incomplete | 12,907 | Flagged; supplemented by skills found in the description (skills_from_desc) |
| S7 | 10,097 distinct free-text designations | 10,097 | Ordered keyword rules on job_title_clean (skills used when the title is uninformative) -> 18 role families + 'Other'; non-analytics guards (RCM, BPO, HR, SEO, IT) run before the generic 'analyst' rule; seniority (5 levels) |
| S8 | Non-analytics roles inside 'Analytics Jobs' (software, BPO, HR, sales, finance, medical coding ...) | 9,609 | Flagged is_analytics_role=0; core analytics sample uses the 9 analytics families |
| S8 | Low-quality 'data entry / work from home / part-time / freelance' postings | 166 | Flagged is_spam; excluded |
| S8 | job_description missing (3,508 in the original file; count shown is after removing exact duplicates) | 3,371 | Not imputed (text); flagged desc_missing |
| S8 | job_description truncated with '...' | 11,469 | Flagged desc_truncated; text treated as partial |
| S9 | Skills recovered from job_description using a 488-skill vocabulary built from key_skills | 7,526 | skills_from_desc + union skills_all (descriptions also truncated, so a lower bound) |
| S9 | No common key between the 4 files | 14,840 | Built a 5-dimension skill taxonomy (big data, maths-stats, coding, AI-ML, dashboards-storytelling) matching the JDS scores; each posting flagged dim_* - this is the bridge for linking market demand to the JDS success data |
| S9 | Tool flags must catch compound skills ('Oracle SQL', 'SQL Server', 'SAS SQL', 'MS Excel') | 14,840 | has_* and dim_* use whole-word matching inside each skill (taxonomy.has), with exclusions such as 'medical coding' |
| S10 | Manual audit of role_family on a final independent random sample of 150 postings | 150 | Exact family correct ~91%; analytics vs non-analytics split correct ~92%. Residual errors are ambiguous titles (e.g. 'SOC Analyst', 'Investment Analyst - Real Estate'); reported as a limitation |

### DataScience Jobs

| Stage | Issue | Rows | Treatment |
|---|---|---|---|
| S1 | reference_no is not unique: 134 numbers shared by 276 different rows | 276 | Kept original as reference_no; new surrogate key row_id (1..n) used as the record key |
| S3 | company_name leading/trailing/double spaces | 0 | Trimmed |
| S3 | Same employer group listed under two names (BNP Paribas / bnp paribas india solutions; HSBC / Hsbc Technology) - the units post the same titles with DIFFERENT salaries and openings, so they are separate listings | 13 | Kept as separate companies (not merged); linked through new company_group column |
| S3 | Placeholder / non-company employer names (Confidential, Xyz Company, Data Entry, Freelancer.com, Freelance Consultants) | 12 | Flagged is_placeholder_employer; excluded from company-level analysis |
| S4 | Salaries stored as text with an 'L' suffix ('7.8L') | 1,602 | Parsed to numeric lakhs per annum (LPA) |
| S5 | Rule min <= avg <= max salary | 0 | 0 violations - internally consistent |
| S5 | Minimum salary below 1 LPA (e.g. 0.2L = Rs 20,000 a year) - likely monthly/stipend figures entered as annual | 3 | Flagged min_salary_implausible; min salary not used in modelling for these rows (avg/max kept) |
| S5 | Very wide salary range (max more than 6x min) | 34 | Flagged wide_salary_range; avg salary used as the main measure |
| S5 | 'Senior' titles asking for 0 years minimum experience | 14 | Flagged senior_zero_exp (title/experience inconsistency) |
| S6 | num_of_jobs extremely right-skewed (median 22, max 4,200 = TCS Business Analyst); 3xIQR rule | 98 | Genuine bulk hiring - kept; flagged and log-transformed (log_num_jobs) for models |
| S6 | Average salary far from its job title's typical range (robust z > 3 within title, e.g. Flipkart Senior DS 82 LPA) | 11 | Kept (top employers pay more); flagged; salary_lpa_w = winsorised copy for models |
| S6 | min_experience above 12 years (max 21) | 12 | All are Data Architect rows - plausible; kept |

### JDS Skill Traits

| Stage | Issue | Rows | Treatment |
|---|---|---|---|
| S1 | Column name with a hyphen ('maths-stats_skills') - invalid in SAS/SQL | 1 | Renamed maths_stats_skills |
| S1 | id not unique: 2 ids shared by different people (different scores) | 4 | Kept as different people; surrogate row_id used as key |
| S5 | Skill scores outside the documented 1-5 scale | 0 | None found |
| S5 | Target salary_hike_high not 0/1 | 0 | None; class balance 53% high / 47% low (balanced) |
| S5 | Missing values | 0 | None |
| S6 | Ceiling effect - share of perfect 5.0 scores: big_data 18%, maths_stats 41%, coding 45%, ai_and_ml 49%, dashboard_and_storytelling 58% | 293 | Kept (real scores); handled with rank tests, tree models and n_skills_at_max |
| S6 | Low outliers (|z| > 2.5) | 3 | Kept - genuine weak scores, scale is bounded |
| S9 | Derived profile variables | 139 | skill_mean, skill_min, skill_range, n_skills_at_max, weakest/strongest skill (no composite indices or segments: the 5 scores are used directly) |

### SDS Personality Traits

| Stage | Issue | Rows | Treatment |
|---|---|---|---|
| S1 | Column names with stray spaces (' extraversion', 'success_ classification_ high_low') | 2 | Trimmed; target renamed success_high |
| S1 | id not unique: 9 ids shared by different people | 18 | Kept; surrogate row_id used as key |
| S5 | Trait scores outside a plausible 0-100 normalised range | 0 | None (observed 17-68) |
| S5 | Missing values | 0 | None |
| S5 | Target success_high balance | 161 | 53% high / 47% low (balanced) |
| S6 | Trait outliers (|z| > 2.5) | 4 | Kept - extreme but valid personality scores |
| S9 | Derived variables | 161 | z-scores per trait, emotional_stability_z (= -neuroticism_z), trait_mean (positive traits), dominant_trait (highest z among emotional stability and the 4 positive traits) |


## 5. What we deliberately did NOT do
- No imputation of missing descriptions or salaries (would invent data).
- No deletion of outliers (bulk hiring and top-employer salaries are real market facts) - flagged instead.
- No change to any JDS / SDS score.
- No merging of companies whose units post different salaries.

