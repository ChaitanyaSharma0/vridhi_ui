# Vriddhi database - schema reference

Database `vriddhi` (MySQL 8, InnoDB, utf8mb4). 19 core/metadata tables, 4 staging tables, 8 views.


## Core (3NF)


### `dim_company` - 642 rows
Recruiting companies (DataScience Jobs); units of one group linked by company_group

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `company_id` | SMALLINT | PK | no | Surrogate key |
| `company_name` | VARCHAR(49) |  | no | Company name as listed (trimmed) |
| `company_group` | VARCHAR(49) |  | no | Parent group (e.g. HSBC for Hsbc Technology) |
| `company_type` | ENUM('IT services / consulting','Product / captive / other') |  | no | Curated classification |
| `is_placeholder_employer` | TINYINT(1) |  | no | 1 = 'Confidential', 'Xyz Company' etc. |

### `dim_job_title` - 10 rows
The 10 job titles in DataScience Jobs, split into base role and seniority

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `job_title_id` | TINYINT | PK | no | Surrogate key |
| `job_title` | VARCHAR(40) |  | no | Job title as published |
| `base_role` | VARCHAR(40) |  | no | Title without 'Senior' |
| `seniority` | ENUM('Junior/Mid','Senior') |  | no | Seniority |

### `dim_city` - 679 rows
Canonical cities / metro areas (100+ raw spellings and localities mapped)

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `city_id` | SMALLINT | PK | no | Surrogate key |
| `city_name` | VARCHAR(30) |  | no | Canonical name |
| `city_category` | ENUM('Tier 1 metro','Tier 2/3','Unspecified','International') |  | no | City tier |

### `dim_role_family` - 23 rows
Role families derived from 10,097 free-text designations

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `role_family_id` | TINYINT | PK | no | Surrogate key |
| `role_family` | VARCHAR(50) |  | no | Role family |
| `is_analytics` | TINYINT(1) |  | no | 1 = one of the 9 analytics families |

### `dim_seniority` - 5 rows
Seniority levels from job titles

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `seniority_id` | TINYINT | PK | no | Surrogate key |
| `seniority` | VARCHAR(20) |  | no | Level |
| `seniority_rank` | TINYINT |  | no | 1 = Entry ... 5 = Leadership |

### `dim_salary_band` - 6 rows
The 6 salary bands of Analytics Jobs

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `salary_band_id` | TINYINT | PK | no | Ordinal 1 (lowest) to 6 |
| `band_code` | VARCHAR(10) |  | no | Code as in source, e.g. '10to15' |
| `band_label` | VARCHAR(20) |  | no | Readable label |
| `low_lpa` | DECIMAL(5,1) |  | no | Lower bound (LPA) |
| `high_lpa` | DECIMAL(5,1) |  | no | Upper bound (LPA) |

Checks: `low_lpa < high_lpa`

### `dim_skill` - 8,301 rows
Every distinct skill / tag, typed (technical, soft, education, job meta)

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `skill_id` | SMALLINT | PK | no | Surrogate key |
| `skill_name` | VARCHAR(45) |  | no | Normalised skill name |
| `skill_type` | ENUM('technical_or_domain','soft','education','job_meta') |  | no | Type |

### `dim_skill_dimension` - 5 rows
The 5 skill dimensions measured in JDS - the bridge between market and people data

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `dimension_id` | TINYINT | PK | no | Surrogate key |
| `dimension_code` | VARCHAR(20) |  | no | Code |
| `dimension_name` | VARCHAR(40) |  | no | Name |
| `jds_score_column` | VARCHAR(40) |  | no | Matching column in the JDS file |

### `map_skill_dimension` - 470 rows
Which market skills belong to which JDS skill dimension (taxonomy)

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `skill_id` | SMALLINT | PK FK → dim_skill.skill_id | no | FK dim_skill |
| `dimension_id` | TINYINT | PK FK → dim_skill_dimension.dimension_id | no | FK dim_skill_dimension |

### `dim_personality_trait` - 5 rows
Big Five personality traits (SDS)

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `trait_id` | TINYINT | PK | no | Surrogate key |
| `trait_code` | VARCHAR(30) |  | no | Code |
| `trait_name` | VARCHAR(30) |  | no | Name |
| `description` | VARCHAR(200) |  | no | Meaning (from the data description) |

### `fact_company_job_title` - 1,602 rows
One row per company x job title (DataScience Jobs) - salaries numeric

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `company_job_title_id` | INT | PK | no | Key (= stg_row_id) |
| `reference_no` | INT |  | no | Original id (not unique) |
| `company_id` | SMALLINT | FK → dim_company.company_id | no | FK dim_company |
| `job_title_id` | TINYINT | FK → dim_job_title.job_title_id | no | FK dim_job_title |
| `min_experience_years` | TINYINT |  | no | Minimum experience |
| `min_salary_lpa` | DECIMAL(6,2) |  | no | Minimum salary (LPA) |
| `avg_salary_lpa` | DECIMAL(6,2) |  | no | Average salary (LPA) |
| `max_salary_lpa` | DECIMAL(6,2) |  | no | Maximum salary (LPA) |
| `num_of_jobs` | INT |  | no | Number of postings |
| `is_min_salary_implausible` | TINYINT(1) |  | no | min < 1 LPA (monthly/stipend) |
| `is_wide_salary_range` | TINYINT(1) |  | no | max > 6 x min |
| `is_senior_zero_exp` | TINYINT(1) |  | no | Senior title, 0 yrs |
| `is_num_jobs_outlier` | TINYINT(1) |  | no | num_of_jobs > Q3 + 3 IQR |
| `is_salary_outlier_in_title` | TINYINT(1) |  | no | avg salary > 3 robust SD from title median |

Checks: `min_salary_lpa <= avg_salary_lpa`; `avg_salary_lpa <= max_salary_lpa`; `min_experience_years >= 0`; `num_of_jobs > 0`

### `fact_job_posting` - 14,840 rows
One row per job posting (Analytics Jobs, exact duplicates removed)

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `posting_id` | INT | PK | no | Original s_no |
| `job_title_raw` | VARCHAR(70) |  | no | Designation (whitespace-normalised) |
| `job_title_clean` | VARCHAR(70) |  | no | Designation without recruiting noise |
| `role_family_id` | TINYINT | FK → dim_role_family.role_family_id | no | FK dim_role_family |
| `role_source` | ENUM('title','skills','none') |  | no | How the family was decided |
| `seniority_id` | TINYINT | FK → dim_seniority.seniority_id | no | FK dim_seniority |
| `exp_min_years` | TINYINT |  | no | Minimum experience |
| `exp_max_years` | TINYINT |  | no | Maximum experience |
| `salary_band_id` | TINYINT | FK → dim_salary_band.salary_band_id | no | FK dim_salary_band |
| `primary_city_id` | SMALLINT | FK → dim_city.city_id | no | FK dim_city |
| `location_raw` | VARCHAR(103) |  | no | Location as posted |
| `job_description` | TEXT |  | yes | Description (bullets turned into sentences) |
| `is_job_type_tagged` | TINYINT(1) |  | no | Raw job_type was filled |
| `is_desc_missing` | TINYINT(1) |  | no | No description |
| `is_desc_truncated` | TINYINT(1) |  | no | Description cut off |
| `is_skills_truncated` | TINYINT(1) |  | no | Skill list cut off |
| `is_near_duplicate` | TINYINT(1) |  | no | Repeat after normalisation |
| `is_possible_repost` | TINYINT(1) |  | no | Same as earlier but other salary band |
| `is_spam` | TINYINT(1) |  | no | Data entry / WFH spam |
| `is_international` | TINYINT(1) |  | no | Overseas-only location |
| `is_salary_exp_inconsistent` | TINYINT(1) |  | no | 0-3 LPA with 8+ years |

Checks: `exp_max_years >= exp_min_years`; `exp_min_years >= 0`

### `bridge_posting_city` - 17,774 rows
Posting x city (many-to-many: 16% of postings list several cities)

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `posting_id` | INT | PK FK → fact_job_posting.posting_id | no | FK fact_job_posting |
| `city_id` | SMALLINT | PK FK → dim_city.city_id | no | FK dim_city |
| `city_order` | TINYINT |  | no | Position in the original location list |

### `bridge_posting_skill` - 81,279 rows
Posting x skill (many-to-many), with where the skill was found

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `posting_id` | INT | PK FK → fact_job_posting.posting_id | no | FK fact_job_posting |
| `skill_id` | SMALLINT | PK FK → dim_skill.skill_id | no | FK dim_skill |
| `found_in` | ENUM('key_skills','description','both') |  | no | Source of the mention |

### `jds_employee` - 139 rows
Junior data scientists (JDS)

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `jds_employee_id` | SMALLINT | PK | no | Surrogate key |
| `source_id` | INT |  | no | Original id (not unique) |
| `salary_hike_high` | TINYINT(1) |  | no | 1 = high performance-based hike |

### `fact_jds_skill_score` - 695 rows
JDS skill scores, one row per employee x skill dimension

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `jds_employee_id` | SMALLINT | PK FK → jds_employee.jds_employee_id | no | FK jds_employee |
| `dimension_id` | TINYINT | PK FK → dim_skill_dimension.dimension_id | no | FK dim_skill_dimension |
| `score` | DECIMAL(2,1) |  | no | Score 1.0-5.0 |

Checks: `score BETWEEN 1 AND 5`

### `sds_employee` - 161 rows
Senior / client-facing data scientists (SDS)

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `sds_employee_id` | SMALLINT | PK | no | Surrogate key |
| `source_id` | INT |  | no | Original id (not unique) |
| `success_high` | TINYINT(1) |  | no | 1 = high success |

### `fact_sds_trait_score` - 805 rows
SDS personality scores, one row per employee x trait

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `sds_employee_id` | SMALLINT | PK FK → sds_employee.sds_employee_id | no | FK sds_employee |
| `trait_id` | TINYINT | PK FK → dim_personality_trait.trait_id | no | FK dim_personality_trait |
| `score` | SMALLINT |  | no | Normalised score |

Checks: `score BETWEEN 0 AND 100`

## Metadata


### `meta_data_quality_log` - 58 rows
Every data issue found, rows affected and treatment

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `issue_id` | SMALLINT | PK | no | Key |
| `stage` | VARCHAR(4) |  | no | Pipeline stage S1-S10 |
| `source_file` | VARCHAR(30) |  | no | File |
| `issue_found` | VARCHAR(400) |  | no | Issue |
| `rows_affected` | INT |  | no | Rows affected |
| `treatment` | VARCHAR(400) |  | no | Treatment |

## Staging (raw)


### `stg_datascience_jobs` - 1,602 rows
Original 'DataScience Jobs.csv' exactly as received (salaries still text, e.g. '7.8L')

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `stg_row_id` | INT | PK | no | Surrogate key added on load (reference_no is not unique) |
| `reference_no` | INT |  | no | Original row id - NOT unique (134 values shared by 276 rows) |
| `company_name` | VARCHAR(49) |  | no | Recruiting company |
| `job_title` | VARCHAR(40) |  | no | Job title |
| `min_experience` | TINYINT |  | no | Minimum required experience (years) |
| `avg_salary` | VARCHAR(10) |  | no | Average salary as text |
| `min_salary` | VARCHAR(10) |  | no | Minimum salary as text |
| `max_salary` | VARCHAR(10) |  | no | Maximum salary as text |
| `num_of_jobs` | INT |  | no | Number of postings |

### `stg_analytics_jobs` - 15,841 rows
Original 'Analytics Jobs.csv' exactly as received (incl. the 1,001 exact duplicates)

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `s_no` | INT | PK | no | Original row id (unique) |
| `experience` | VARCHAR(20) |  | no | Experience range as text, e.g. '6-10 yrs' |
| `job_description` | TEXT |  | yes | Description as received |
| `job_desig` | VARCHAR(70) |  | no | Designation as received |
| `job_type` | VARCHAR(20) |  | yes | Job type as received (76% missing) |
| `key_skills` | TEXT |  | yes | Key skills as received |
| `location` | VARCHAR(103) |  | no | Location as received |
| `salary` | VARCHAR(10) |  | no | Salary band as received, e.g. '10to15' |

### `stg_jds_skill_traits` - 139 rows
Original 'JDS Skill Traits.xlsx' (column maths-stats_skills renamed maths_stats_skills)

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `stg_row_id` | INT | PK | no | Surrogate key (id is not unique) |
| `id` | INT |  | no | Original id - NOT unique |
| `big_data_skills` | DECIMAL(2,1) |  | no | Score 1-5 |
| `maths_stats_skills` | DECIMAL(2,1) |  | no | Score 1-5 |
| `coding_skills` | DECIMAL(2,1) |  | no | Score 1-5 |
| `ai_and_ml_skills` | DECIMAL(2,1) |  | no | Score 1-5 |
| `dashboard_and_storytelling_skills` | DECIMAL(2,1) |  | no | Score 1-5 |
| `salary_hike_high_or_low` | TINYINT |  | no | 1 = high hike, 0 = low |

### `stg_sds_personality_traits` - 161 rows
Original 'SDS Personality Traits.xlsx' (stray spaces removed from column names)

| Column | Type | Key | Null | Description |
|---|---|---|---|---|
| `stg_row_id` | INT | PK | no | Surrogate key (id is not unique) |
| `id` | INT |  | no | Original id - NOT unique |
| `neuroticism` | SMALLINT |  | no | Normalised score |
| `extraversion` | SMALLINT |  | no | Normalised score |
| `openness_to_experience` | SMALLINT |  | no | Normalised score |
| `agreeableness` | SMALLINT |  | no | Normalised score |
| `conscientiousness` | SMALLINT |  | no | Normalised score |
| `success_classification_high_low` | TINYINT |  | no | 1 = high success, 0 = low |
