"""VRIDDHI - build the normalised MySQL database from the cleaned data.

Three layers (industry-standard medallion-style layout):
  stg_*   STAGING  - the 4 original files loaded exactly as received (traceability / audit)
  dim_* fact_* bridge_* jds_* sds_*  CORE (3NF) - cleaned, normalised, with PK / FK / CHECK constraints
  v_*     VIEWS    - analysis-ready, denormalised views (derived values computed here, never stored)
  meta_*  METADATA - data-quality log

The schema is defined ONCE below (SCHEMA); the DDL, the ER diagram and the schema document are all generated
from it, and every table is validated in Python (PK unique, FK present, NOT NULL, CHECK) before SQL is written.

Outputs -> database/
  sql/01_create_schema.sql   sql/02_load_staging.sql   sql/03_load_core.sql   sql/04_views.sql   sql/05_verify.sql
  csv/<table>.csv            ERD.md (Mermaid)           SCHEMA.md
"""
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

from taxonomy import DIMS, DIM_NAMES, JDS_COLUMN, match_any

HERE = Path(__file__).resolve().parent
RAW = HERE.parent
CLEAN = HERE / "clean"
OUT = HERE / "database"
(OUT / "sql").mkdir(parents=True, exist_ok=True)
(OUT / "csv").mkdir(parents=True, exist_ok=True)
DB = "vriddhi"

# ======================================================================= load cleaned + raw
ds = pd.read_csv(CLEAN / "ds_jobs_clean.csv")
an = pd.read_csv(CLEAN / "analytics_jobs_clean.csv")
jd = pd.read_csv(CLEAN / "jds_clean.csv")
sd = pd.read_csv(CLEAN / "sds_clean.csv")
qlog = pd.read_csv(HERE / "outputs" / "data_quality_log.csv", keep_default_na=False)
r_ds = pd.read_csv(RAW / "DataScience Jobs.csv")
r_an = pd.read_csv(RAW / "Analytics Jobs.csv")
r_jd = pd.read_excel(RAW / "JDS Skill Traits.xlsx")
r_sd = pd.read_excel(RAW / "SDS Personality Traits.xlsx")
split = lambda s: [x for x in str(s).split("|") if x and x != "nan"] if pd.notna(s) else []

# ======================================================================= STAGING tables (raw, as received)
stg = {
    "stg_datascience_jobs": r_ds.rename(columns=str.strip).assign(stg_row_id=np.arange(1, len(r_ds) + 1)),
    "stg_analytics_jobs": r_an.copy(),
    "stg_jds_skill_traits": r_jd.rename(columns={"maths-stats_skills": "maths_stats_skills"}).assign(stg_row_id=np.arange(1, len(r_jd) + 1)),
    "stg_sds_personality_traits": r_sd.rename(columns=lambda c: re.sub(r"\s+", "", c)).assign(stg_row_id=np.arange(1, len(r_sd) + 1)),
}

# ======================================================================= CORE: DataScience Jobs
dim_company = (ds[["company_name", "company_group", "company_type", "is_placeholder_employer"]].drop_duplicates("company_name")
               .sort_values("company_name").reset_index(drop=True))
dim_company.insert(0, "company_id", np.arange(1, len(dim_company) + 1))
dim_job_title = ds[["job_title", "role", "seniority"]].drop_duplicates().sort_values(["role", "seniority"]).reset_index(drop=True)
dim_job_title = dim_job_title.rename(columns={"role": "base_role"})
dim_job_title.insert(0, "job_title_id", np.arange(1, len(dim_job_title) + 1))
fact_company_job_title = (ds.merge(dim_company[["company_id", "company_name"]], on="company_name")
                          .merge(dim_job_title[["job_title_id", "job_title"]], on="job_title")
                          .sort_values("row_id"))
fact_company_job_title = fact_company_job_title[[
    "row_id", "reference_no", "company_id", "job_title_id", "min_experience", "min_salary_lpa", "avg_salary_lpa",
    "max_salary_lpa", "num_of_jobs", "min_salary_implausible", "wide_salary_range", "senior_zero_exp",
    "num_jobs_outlier", "salary_outlier_in_title"]].rename(columns={
    "row_id": "company_job_title_id", "min_experience": "min_experience_years", "min_salary_implausible": "is_min_salary_implausible",
    "wide_salary_range": "is_wide_salary_range", "senior_zero_exp": "is_senior_zero_exp", "num_jobs_outlier": "is_num_jobs_outlier",
    "salary_outlier_in_title": "is_salary_outlier_in_title"})

# ======================================================================= CORE: Analytics Jobs
TIER1 = {"Bengaluru", "Mumbai", "Delhi NCR", "Hyderabad", "Pune", "Chennai", "Kolkata"}
cities = set(an.primary_city) | {c for l in an.cities.map(split) for c in l}


def city_category(c):
    if c in TIER1:
        return "Tier 1 metro"
    if c == "International":
        return "International"
    if c in ("Anywhere in India", "Unknown"):
        return "Unspecified"
    return "Tier 2/3"


dim_city = pd.DataFrame(sorted(cities), columns=["city_name"])
dim_city["city_category"] = dim_city.city_name.map(city_category)
dim_city.insert(0, "city_id", np.arange(1, len(dim_city) + 1))
cid = dict(zip(dim_city.city_name, dim_city.city_id))

ANALYTICS_FAMILIES = set(an.loc[an.is_analytics_role == 1, "role_family"])
dim_role_family = pd.DataFrame(sorted(an.role_family.unique()), columns=["role_family"])
dim_role_family["is_analytics"] = dim_role_family.role_family.isin(ANALYTICS_FAMILIES).astype(int)
dim_role_family.insert(0, "role_family_id", np.arange(1, len(dim_role_family) + 1))
SEN_ORDER = ["Entry", "Mid", "Senior", "Manager / Lead", "Leadership"]
dim_seniority = pd.DataFrame({"seniority_id": range(1, 6), "seniority": SEN_ORDER, "seniority_rank": range(1, 6)})
assert set(an.seniority) <= set(SEN_ORDER)
dim_salary_band = (an[["salary_band_ord", "salary", "salary_band", "salary_low_lpa", "salary_high_lpa"]].drop_duplicates()
                   .sort_values("salary_band_ord").rename(columns={"salary_band_ord": "salary_band_id", "salary": "band_code",
                                                                     "salary_band": "band_label", "salary_low_lpa": "low_lpa",
                                                                     "salary_high_lpa": "high_lpa"}))

# skills: one row per distinct name, typed by the column it came from
SKILL_COLS = [("skills", "technical_or_domain"), ("skills_from_desc", "technical_or_domain"), ("soft_skills", "soft"),
              ("education_mentioned", "education"), ("job_meta_tags", "job_meta")]
stype = {}
for col, typ in SKILL_COLS:
    for l in an[col].map(split):
        for sk in l:
            stype.setdefault(sk, typ)
conflict = sum(1 for col, typ in SKILL_COLS for l in an[col].map(split) for sk in l if stype[sk] != typ)
assert conflict == 0, f"{conflict} skills appear with two different types"
dim_skill = pd.DataFrame(sorted(stype.items()), columns=["skill_name", "skill_type"])
dim_skill.insert(0, "skill_id", np.arange(1, len(dim_skill) + 1))
sid = dict(zip(dim_skill.skill_name, dim_skill.skill_id))
dim_skill_dimension = pd.DataFrame({"dimension_id": range(1, 6), "dimension_code": list(DIMS),
                                    "dimension_name": [DIM_NAMES[d] for d in DIMS],
                                    "jds_score_column": [JDS_COLUMN[d] for d in DIMS]})
did = dict(zip(dim_skill_dimension.dimension_code, dim_skill_dimension.dimension_id))
map_skill_dimension = pd.DataFrame([(sid[s], did[d]) for d, kws in DIMS.items() for s in sid
                                    if stype[s] == "technical_or_domain" and match_any(s, kws)],
                                   columns=["skill_id", "dimension_id"]).drop_duplicates()

fact_job_posting = pd.DataFrame({
    "posting_id": an.s_no,
    "job_title_raw": an.job_desig,
    "job_title_clean": an.job_title_clean,
    "role_family_id": an.role_family.map(dict(zip(dim_role_family.role_family, dim_role_family.role_family_id))),
    "role_source": an.role_source,
    "seniority_id": an.seniority.map(dict(zip(dim_seniority.seniority, dim_seniority.seniority_id))),
    "exp_min_years": an.exp_min.astype(int),
    "exp_max_years": an.exp_max.astype(int),
    "salary_band_id": an.salary_band_ord.astype(int),
    "primary_city_id": an.primary_city.map(cid),
    "location_raw": an.location,
    "job_description": an.job_description,
    "is_job_type_tagged": an.job_type_tagged,
    "is_desc_missing": an.desc_missing,
    "is_desc_truncated": an.desc_truncated,
    "is_skills_truncated": an.skills_truncated,
    "is_near_duplicate": an.is_near_duplicate,
    "is_possible_repost": an.possible_repost,
    "is_spam": an.is_spam,
    "is_international": an.is_international,
    "is_salary_exp_inconsistent": an.salary_exp_inconsistent,
}).sort_values("posting_id")
bridge_posting_city = pd.DataFrame([(pid, cid[c], i + 1) for pid, l in zip(an.s_no, an.cities.map(split)) for i, c in enumerate(l)],
                                   columns=["posting_id", "city_id", "city_order"]).drop_duplicates(["posting_id", "city_id"])
rows = []
for pid, k, d, so, ed, mt in zip(an.s_no, an.skills.map(split), an.skills_from_desc.map(split), an.soft_skills.map(split),
                                 an.education_mentioned.map(split), an.job_meta_tags.map(split)):
    in_key = set(k) | set(so) | set(ed) | set(mt)
    for sk in in_key | set(d):
        rows.append((pid, sid[sk], "both" if (sk in in_key and sk in d) else ("key_skills" if sk in in_key else "description")))
bridge_posting_skill = pd.DataFrame(rows, columns=["posting_id", "skill_id", "found_in"])

# ======================================================================= CORE: JDS / SDS (scores stored long -> 1NF/3NF)
jds_employee = jd[["row_id", "id", "salary_hike_high"]].rename(columns={"row_id": "jds_employee_id", "id": "source_id"})
fact_jds_skill_score = pd.DataFrame([(r.row_id, did[d], getattr(r, JDS_COLUMN[d])) for r in jd.itertuples() for d in DIMS],
                                    columns=["jds_employee_id", "dimension_id", "score"])
TRAITS = [("neuroticism", "Neuroticism", "Tendency to experience negative emotions such as anxiety, anger and self-doubt"),
          ("extraversion", "Extraversion", "Outgoing, energetic and assertive (high) vs. quiet and reserved (low)"),
          ("openness_to_experience", "Openness to experience", "Creativity, curiosity and willingness to embrace new ideas"),
          ("agreeableness", "Agreeableness", "Compassionate, cooperative and trusting rather than antagonistic"),
          ("conscientiousness", "Conscientiousness", "Organised, responsible, hardworking and goal-directed")]
dim_personality_trait = pd.DataFrame([(i + 1, c, n, d) for i, (c, n, d) in enumerate(TRAITS)],
                                     columns=["trait_id", "trait_code", "trait_name", "description"])
sds_employee = sd[["row_id", "id", "success_high"]].rename(columns={"row_id": "sds_employee_id", "id": "source_id"})
fact_sds_trait_score = pd.DataFrame([(r.row_id, i + 1, int(getattr(r, c))) for r in sd.itertuples() for i, (c, _, _) in enumerate(TRAITS)],
                                    columns=["sds_employee_id", "trait_id", "score"])
meta_data_quality_log = qlog.reset_index(drop=True)
meta_data_quality_log.insert(0, "issue_id", np.arange(1, len(qlog) + 1))
meta_data_quality_log = meta_data_quality_log.rename(columns={"file": "source_file", "issue": "issue_found"})

# ======================================================================= SCHEMA (single source of truth)
# column: (name, mysql type, nullable, comment) ; table: (name, layer, comment, columns, pk, fks, checks, indexes, data)
VC = lambda df, c: max(8, int(df[c].astype(str).str.len().max()))


def T(name, layer, comment, cols, pk, fks=(), checks=(), idx=(), data=None):
    return dict(name=name, layer=layer, comment=comment, cols=cols, pk=pk, fks=list(fks), checks=list(checks), idx=list(idx), data=data)


S = []
# ---- staging
S.append(T("stg_datascience_jobs", "staging", "Original 'DataScience Jobs.csv' exactly as received (salaries still text, e.g. '7.8L')", [
    ("stg_row_id", "INT", False, "Surrogate key added on load (reference_no is not unique)"),
    ("reference_no", "INT", False, "Original row id - NOT unique (134 values shared by 276 rows)"),
    ("company_name", f"VARCHAR({VC(r_ds, 'company_name')})", False, "Recruiting company"),
    ("job_title", "VARCHAR(40)", False, "Job title"),
    ("min_experience", "TINYINT", False, "Minimum required experience (years)"),
    ("avg_salary", "VARCHAR(10)", False, "Average salary as text"),
    ("min_salary", "VARCHAR(10)", False, "Minimum salary as text"),
    ("max_salary", "VARCHAR(10)", False, "Maximum salary as text"),
    ("num_of_jobs", "INT", False, "Number of postings")], ["stg_row_id"], data=stg["stg_datascience_jobs"]))
S.append(T("stg_analytics_jobs", "staging", "Original 'Analytics Jobs.csv' exactly as received (incl. the 1,001 exact duplicates)", [
    ("s_no", "INT", False, "Original row id (unique)"),
    ("experience", "VARCHAR(20)", False, "Experience range as text, e.g. '6-10 yrs'"),
    ("job_description", "TEXT", True, "Description as received"),
    ("job_desig", f"VARCHAR({VC(r_an, 'job_desig')})", False, "Designation as received"),
    ("job_type", "VARCHAR(20)", True, "Job type as received (76% missing)"),
    ("key_skills", "TEXT", True, "Key skills as received"),
    ("location", f"VARCHAR({VC(r_an, 'location')})", False, "Location as received"),
    ("salary", "VARCHAR(10)", False, "Salary band as received, e.g. '10to15'")], ["s_no"], data=stg["stg_analytics_jobs"]))
S.append(T("stg_jds_skill_traits", "staging", "Original 'JDS Skill Traits.xlsx' (column maths-stats_skills renamed maths_stats_skills)", [
    ("stg_row_id", "INT", False, "Surrogate key (id is not unique)"), ("id", "INT", False, "Original id - NOT unique"),
    ("big_data_skills", "DECIMAL(2,1)", False, "Score 1-5"), ("maths_stats_skills", "DECIMAL(2,1)", False, "Score 1-5"),
    ("coding_skills", "DECIMAL(2,1)", False, "Score 1-5"), ("ai_and_ml_skills", "DECIMAL(2,1)", False, "Score 1-5"),
    ("dashboard_and_storytelling_skills", "DECIMAL(2,1)", False, "Score 1-5"),
    ("salary_hike_high_or_low", "TINYINT", False, "1 = high hike, 0 = low")], ["stg_row_id"], data=stg["stg_jds_skill_traits"]))
S.append(T("stg_sds_personality_traits", "staging", "Original 'SDS Personality Traits.xlsx' (stray spaces removed from column names)", [
    ("stg_row_id", "INT", False, "Surrogate key (id is not unique)"), ("id", "INT", False, "Original id - NOT unique"),
    ("neuroticism", "SMALLINT", False, "Normalised score"), ("extraversion", "SMALLINT", False, "Normalised score"),
    ("openness_to_experience", "SMALLINT", False, "Normalised score"), ("agreeableness", "SMALLINT", False, "Normalised score"),
    ("conscientiousness", "SMALLINT", False, "Normalised score"),
    ("success_classification_high_low", "TINYINT", False, "1 = high success, 0 = low")], ["stg_row_id"], data=stg["stg_sds_personality_traits"]))

# ---- core: lookups
S.append(T("dim_company", "core", "Recruiting companies (DataScience Jobs); units of one group linked by company_group", [
    ("company_id", "SMALLINT", False, "Surrogate key"), ("company_name", f"VARCHAR({VC(dim_company, 'company_name')})", False, "Company name as listed (trimmed)"),
    ("company_group", f"VARCHAR({VC(dim_company, 'company_group')})", False, "Parent group (e.g. HSBC for Hsbc Technology)"),
    ("company_type", "ENUM('IT services / consulting','Product / captive / other')", False, "Curated classification"),
    ("is_placeholder_employer", "TINYINT(1)", False, "1 = 'Confidential', 'Xyz Company' etc.")],
    ["company_id"], idx=[("uq_company_name", ["company_name"], True), ("ix_company_group", ["company_group"], False)], data=dim_company))
S.append(T("dim_job_title", "core", "The 10 job titles in DataScience Jobs, split into base role and seniority", [
    ("job_title_id", "TINYINT", False, "Surrogate key"), ("job_title", "VARCHAR(40)", False, "Job title as published"),
    ("base_role", "VARCHAR(40)", False, "Title without 'Senior'"), ("seniority", "ENUM('Junior/Mid','Senior')", False, "Seniority")],
    ["job_title_id"], idx=[("uq_job_title", ["job_title"], True)], data=dim_job_title))
S.append(T("dim_city", "core", "Canonical cities / metro areas (100+ raw spellings and localities mapped)", [
    ("city_id", "SMALLINT", False, "Surrogate key"), ("city_name", f"VARCHAR({VC(dim_city, 'city_name')})", False, "Canonical name"),
    ("city_category", "ENUM('Tier 1 metro','Tier 2/3','Unspecified','International')", False, "City tier")],
    ["city_id"], idx=[("uq_city_name", ["city_name"], True)], data=dim_city))
S.append(T("dim_role_family", "core", "Role families derived from 10,097 free-text designations", [
    ("role_family_id", "TINYINT", False, "Surrogate key"), ("role_family", "VARCHAR(50)", False, "Role family"),
    ("is_analytics", "TINYINT(1)", False, "1 = one of the 9 analytics families")],
    ["role_family_id"], idx=[("uq_role_family", ["role_family"], True)], data=dim_role_family))
S.append(T("dim_seniority", "core", "Seniority levels from job titles", [
    ("seniority_id", "TINYINT", False, "Surrogate key"), ("seniority", "VARCHAR(20)", False, "Level"),
    ("seniority_rank", "TINYINT", False, "1 = Entry ... 5 = Leadership")],
    ["seniority_id"], idx=[("uq_seniority", ["seniority"], True)], data=dim_seniority))
S.append(T("dim_salary_band", "core", "The 6 salary bands of Analytics Jobs", [
    ("salary_band_id", "TINYINT", False, "Ordinal 1 (lowest) to 6"), ("band_code", "VARCHAR(10)", False, "Code as in source, e.g. '10to15'"),
    ("band_label", "VARCHAR(20)", False, "Readable label"), ("low_lpa", "DECIMAL(5,1)", False, "Lower bound (LPA)"),
    ("high_lpa", "DECIMAL(5,1)", False, "Upper bound (LPA)")],
    ["salary_band_id"], checks=["low_lpa < high_lpa"], idx=[("uq_band_code", ["band_code"], True)], data=dim_salary_band))
S.append(T("dim_skill", "core", "Every distinct skill / tag, typed (technical, soft, education, job meta)", [
    ("skill_id", "SMALLINT", False, "Surrogate key"), ("skill_name", f"VARCHAR({VC(dim_skill, 'skill_name')})", False, "Normalised skill name"),
    ("skill_type", "ENUM('technical_or_domain','soft','education','job_meta')", False, "Type")],
    ["skill_id"], idx=[("uq_skill_name", ["skill_name"], True), ("ix_skill_type", ["skill_type"], False)], data=dim_skill))
S.append(T("dim_skill_dimension", "core", "The 5 skill dimensions measured in JDS - the bridge between market and people data", [
    ("dimension_id", "TINYINT", False, "Surrogate key"), ("dimension_code", "VARCHAR(20)", False, "Code"),
    ("dimension_name", "VARCHAR(40)", False, "Name"), ("jds_score_column", "VARCHAR(40)", False, "Matching column in the JDS file")],
    ["dimension_id"], idx=[("uq_dimension_code", ["dimension_code"], True)], data=dim_skill_dimension))
S.append(T("map_skill_dimension", "core", "Which market skills belong to which JDS skill dimension (taxonomy)", [
    ("skill_id", "SMALLINT", False, "FK dim_skill"), ("dimension_id", "TINYINT", False, "FK dim_skill_dimension")],
    ["skill_id", "dimension_id"], fks=[("skill_id", "dim_skill", "skill_id"), ("dimension_id", "dim_skill_dimension", "dimension_id")],
    data=map_skill_dimension))
S.append(T("dim_personality_trait", "core", "Big Five personality traits (SDS)", [
    ("trait_id", "TINYINT", False, "Surrogate key"), ("trait_code", "VARCHAR(30)", False, "Code"),
    ("trait_name", "VARCHAR(30)", False, "Name"), ("description", "VARCHAR(200)", False, "Meaning (from the data description)")],
    ["trait_id"], idx=[("uq_trait_code", ["trait_code"], True)], data=dim_personality_trait))

# ---- core: facts & bridges
S.append(T("fact_company_job_title", "core", "One row per company x job title (DataScience Jobs) - salaries numeric", [
    ("company_job_title_id", "INT", False, "Key (= stg_row_id)"), ("reference_no", "INT", False, "Original id (not unique)"),
    ("company_id", "SMALLINT", False, "FK dim_company"), ("job_title_id", "TINYINT", False, "FK dim_job_title"),
    ("min_experience_years", "TINYINT", False, "Minimum experience"), ("min_salary_lpa", "DECIMAL(6,2)", False, "Minimum salary (LPA)"),
    ("avg_salary_lpa", "DECIMAL(6,2)", False, "Average salary (LPA)"), ("max_salary_lpa", "DECIMAL(6,2)", False, "Maximum salary (LPA)"),
    ("num_of_jobs", "INT", False, "Number of postings"),
    ("is_min_salary_implausible", "TINYINT(1)", False, "min < 1 LPA (monthly/stipend)"),
    ("is_wide_salary_range", "TINYINT(1)", False, "max > 6 x min"), ("is_senior_zero_exp", "TINYINT(1)", False, "Senior title, 0 yrs"),
    ("is_num_jobs_outlier", "TINYINT(1)", False, "num_of_jobs > Q3 + 3 IQR"),
    ("is_salary_outlier_in_title", "TINYINT(1)", False, "avg salary > 3 robust SD from title median")],
    ["company_job_title_id"], fks=[("company_id", "dim_company", "company_id"), ("job_title_id", "dim_job_title", "job_title_id")],
    checks=["min_salary_lpa <= avg_salary_lpa", "avg_salary_lpa <= max_salary_lpa", "min_experience_years >= 0", "num_of_jobs > 0"],
    idx=[("uq_company_title", ["company_id", "job_title_id"], True), ("ix_reference_no", ["reference_no"], False)],
    data=fact_company_job_title))
S.append(T("fact_job_posting", "core", "One row per job posting (Analytics Jobs, exact duplicates removed)", [
    ("posting_id", "INT", False, "Original s_no"), ("job_title_raw", f"VARCHAR({VC(an, 'job_desig')})", False, "Designation (whitespace-normalised)"),
    ("job_title_clean", f"VARCHAR({VC(an, 'job_title_clean')})", False, "Designation without recruiting noise"),
    ("role_family_id", "TINYINT", False, "FK dim_role_family"), ("role_source", "ENUM('title','skills','none')", False, "How the family was decided"),
    ("seniority_id", "TINYINT", False, "FK dim_seniority"), ("exp_min_years", "TINYINT", False, "Minimum experience"),
    ("exp_max_years", "TINYINT", False, "Maximum experience"), ("salary_band_id", "TINYINT", False, "FK dim_salary_band"),
    ("primary_city_id", "SMALLINT", False, "FK dim_city"), ("location_raw", f"VARCHAR({VC(an, 'location')})", False, "Location as posted"),
    ("job_description", "TEXT", True, "Description (bullets turned into sentences)"),
    ("is_job_type_tagged", "TINYINT(1)", False, "Raw job_type was filled"), ("is_desc_missing", "TINYINT(1)", False, "No description"),
    ("is_desc_truncated", "TINYINT(1)", False, "Description cut off"), ("is_skills_truncated", "TINYINT(1)", False, "Skill list cut off"),
    ("is_near_duplicate", "TINYINT(1)", False, "Repeat after normalisation"), ("is_possible_repost", "TINYINT(1)", False, "Same as earlier but other salary band"),
    ("is_spam", "TINYINT(1)", False, "Data entry / WFH spam"), ("is_international", "TINYINT(1)", False, "Overseas-only location"),
    ("is_salary_exp_inconsistent", "TINYINT(1)", False, "0-3 LPA with 8+ years")],
    ["posting_id"], fks=[("role_family_id", "dim_role_family", "role_family_id"), ("seniority_id", "dim_seniority", "seniority_id"),
                         ("salary_band_id", "dim_salary_band", "salary_band_id"), ("primary_city_id", "dim_city", "city_id")],
    checks=["exp_max_years >= exp_min_years", "exp_min_years >= 0"],
    idx=[("ix_posting_role", ["role_family_id"], False), ("ix_posting_city", ["primary_city_id"], False),
         ("ix_posting_band", ["salary_band_id"], False)], data=fact_job_posting))
S.append(T("bridge_posting_city", "core", "Posting x city (many-to-many: 16% of postings list several cities)", [
    ("posting_id", "INT", False, "FK fact_job_posting"), ("city_id", "SMALLINT", False, "FK dim_city"),
    ("city_order", "TINYINT", False, "Position in the original location list")],
    ["posting_id", "city_id"], fks=[("posting_id", "fact_job_posting", "posting_id"), ("city_id", "dim_city", "city_id")],
    idx=[("ix_pc_city", ["city_id"], False)], data=bridge_posting_city))
S.append(T("bridge_posting_skill", "core", "Posting x skill (many-to-many), with where the skill was found", [
    ("posting_id", "INT", False, "FK fact_job_posting"), ("skill_id", "SMALLINT", False, "FK dim_skill"),
    ("found_in", "ENUM('key_skills','description','both')", False, "Source of the mention")],
    ["posting_id", "skill_id"], fks=[("posting_id", "fact_job_posting", "posting_id"), ("skill_id", "dim_skill", "skill_id")],
    idx=[("ix_ps_skill", ["skill_id"], False)], data=bridge_posting_skill))
S.append(T("jds_employee", "core", "Junior data scientists (JDS)", [
    ("jds_employee_id", "SMALLINT", False, "Surrogate key"), ("source_id", "INT", False, "Original id (not unique)"),
    ("salary_hike_high", "TINYINT(1)", False, "1 = high performance-based hike")],
    ["jds_employee_id"], idx=[("ix_jds_source", ["source_id"], False)], data=jds_employee))
S.append(T("fact_jds_skill_score", "core", "JDS skill scores, one row per employee x skill dimension", [
    ("jds_employee_id", "SMALLINT", False, "FK jds_employee"), ("dimension_id", "TINYINT", False, "FK dim_skill_dimension"),
    ("score", "DECIMAL(2,1)", False, "Score 1.0-5.0")],
    ["jds_employee_id", "dimension_id"], fks=[("jds_employee_id", "jds_employee", "jds_employee_id"),
                                              ("dimension_id", "dim_skill_dimension", "dimension_id")],
    checks=["score BETWEEN 1 AND 5"], data=fact_jds_skill_score))
S.append(T("sds_employee", "core", "Senior / client-facing data scientists (SDS)", [
    ("sds_employee_id", "SMALLINT", False, "Surrogate key"), ("source_id", "INT", False, "Original id (not unique)"),
    ("success_high", "TINYINT(1)", False, "1 = high success")],
    ["sds_employee_id"], idx=[("ix_sds_source", ["source_id"], False)], data=sds_employee))
S.append(T("fact_sds_trait_score", "core", "SDS personality scores, one row per employee x trait", [
    ("sds_employee_id", "SMALLINT", False, "FK sds_employee"), ("trait_id", "TINYINT", False, "FK dim_personality_trait"),
    ("score", "SMALLINT", False, "Normalised score")],
    ["sds_employee_id", "trait_id"], fks=[("sds_employee_id", "sds_employee", "sds_employee_id"),
                                          ("trait_id", "dim_personality_trait", "trait_id")],
    checks=["score BETWEEN 0 AND 100"], data=fact_sds_trait_score))
S.append(T("meta_data_quality_log", "metadata", "Every data issue found, rows affected and treatment", [
    ("issue_id", "SMALLINT", False, "Key"), ("stage", "VARCHAR(4)", False, "Pipeline stage S1-S10"),
    ("source_file", "VARCHAR(30)", False, "File"), ("issue_found", "VARCHAR(400)", False, "Issue"),
    ("rows_affected", "INT", False, "Rows affected"), ("treatment", "VARCHAR(400)", False, "Treatment")],
    ["issue_id"], data=meta_data_quality_log))

# ======================================================================= validate everything in Python first
by = {t["name"]: t for t in S}
problems = []
for t in S:
    df, cols = t["data"], [c[0] for c in t["cols"]]
    missing = set(cols) - set(df.columns)
    if missing:
        problems.append(f"{t['name']}: columns missing in data {missing}")
        continue
    t["data"] = df = df[cols]
    if df.duplicated(t["pk"]).any():
        problems.append(f"{t['name']}: duplicate primary key")
    for c, typ, nullable, _ in t["cols"]:
        if not nullable and df[c].isna().any():
            problems.append(f"{t['name']}.{c}: NULL in NOT NULL column ({df[c].isna().sum()})")
        m = re.match(r"VARCHAR\((\d+)\)", typ)
        if m and df[c].astype(str).str.len().max() > int(m.group(1)):
            problems.append(f"{t['name']}.{c}: value longer than {typ}")
    for col, rt, rc in t["fks"]:
        if not df[col].isin(by[rt]["data"][rc]).all():
            problems.append(f"{t['name']}.{col}: orphan foreign keys")
    for idx_name, idx_cols, unique in t["idx"]:
        if unique and df.duplicated(idx_cols).any():
            problems.append(f"{t['name']}: unique index {idx_name} violated")
assert not problems, "\n".join(problems)
# business checks mirrored from CHECK constraints
assert (fact_company_job_title.min_salary_lpa <= fact_company_job_title.avg_salary_lpa).all()
assert (fact_company_job_title.avg_salary_lpa <= fact_company_job_title.max_salary_lpa).all()
assert fact_jds_skill_score.score.between(1, 5).all() and fact_sds_trait_score.score.between(0, 100).all()
assert (fact_job_posting.exp_max_years >= fact_job_posting.exp_min_years).all()

# the normalised model must reproduce the cleaned flags exactly
core_flag = ((fact_job_posting.is_spam == 0) & (fact_job_posting.is_international == 0) & (fact_job_posting.is_near_duplicate == 0)
             & fact_job_posting.role_family_id.map(dict(zip(dim_role_family.role_family_id, dim_role_family.is_analytics))).eq(1))
assert core_flag.sum() == an.in_core_analytics.sum(), (core_flag.sum(), an.in_core_analytics.sum())
tech = bridge_posting_skill.merge(dim_skill, on="skill_id").query("skill_type == 'technical_or_domain'")
dimflags = tech.merge(map_skill_dimension, on="skill_id").merge(dim_skill_dimension, on="dimension_id")
for d in DIMS:
    ids = set(dimflags.loc[dimflags.dimension_code == d, "posting_id"])
    assert ids == set(an.loc[an[f"dim_{d}"] == 1, "s_no"]), d

# ======================================================================= emit SQL


def lit(v):
    if v is None or (isinstance(v, float) and math.isnan(v)) or (v is pd.NA):
        return "NULL"
    if isinstance(v, (bool, np.bool_)):
        return "1" if v else "0"
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    if isinstance(v, (float, np.floating)):
        return repr(round(float(v), 6))
    s = str(v).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r").replace("\x00", "\\0").replace("\x1a", "\\Z")
    return f"'{s}'"


def ddl(t):
    lines = [f"  `{c}` {typ}{'' if n else ' NOT NULL'} COMMENT {lit(cm)}" for c, typ, n, cm in t["cols"]]
    lines.append(f"  PRIMARY KEY ({', '.join(f'`{c}`' for c in t['pk'])})")
    for name, cols, unique in t["idx"]:
        lines.append(f"  {'UNIQUE ' if unique else ''}KEY `{name}` ({', '.join(f'`{c}`' for c in cols)})")
    for i, (col, rt, rc) in enumerate(t["fks"], 1):
        lines.append(f"  CONSTRAINT `fk_{t['name']}_{col}` FOREIGN KEY (`{col}`) REFERENCES `{rt}` (`{rc}`)")
    for i, ck in enumerate(t["checks"], 1):
        lines.append(f"  CONSTRAINT `ck_{t['name']}_{i}` CHECK ({ck})")
    return (f"CREATE TABLE `{t['name']}` (\n" + ",\n".join(lines) +
            f"\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT={lit(t['comment'])};\n")


ORDER = [t["name"] for t in S]  # parents are defined before children
header = f"-- VRIDDHI database - generated by build_database.py. Do not edit by hand.\n"
with open(OUT / "sql" / "01_create_schema.sql", "w", encoding="utf-8") as f:
    f.write(header + f"CREATE DATABASE IF NOT EXISTS `{DB}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;\nUSE `{DB}`;\n")
    f.write("SET FOREIGN_KEY_CHECKS = 0;\n")
    for n in reversed(ORDER):
        f.write(f"DROP VIEW IF EXISTS `{n}`;\n" if n.startswith("v_") else f"DROP TABLE IF EXISTS `{n}`;\n")
    f.write("SET FOREIGN_KEY_CHECKS = 1;\n\n")
    for t in S:
        f.write(f"-- [{t['layer']}] {t['comment']}\n" + ddl(t) + "\n")


def inserts(f, t, batch=400):
    df = t["data"]
    cols = ", ".join(f"`{c}`" for c in df.columns)
    vals = [f"({', '.join(lit(v) for v in row)})" for row in df.itertuples(index=False, name=None)]
    for i in range(0, len(vals), batch):
        f.write(f"INSERT INTO `{t['name']}` ({cols}) VALUES {', '.join(vals[i:i + batch])};\n")


for fname, layer in [("02_load_staging.sql", "staging"), ("03_load_core.sql", ("core", "metadata"))]:
    with open(OUT / "sql" / fname, "w", encoding="utf-8") as f:
        f.write(header + f"USE `{DB}`;\nSET FOREIGN_KEY_CHECKS = 1;\nSET autocommit = 0;\n")
        for t in S:
            if t["layer"] in (layer if isinstance(layer, tuple) else (layer,)):
                f.write(f"-- {t['name']}: {len(t['data']):,} rows\n")
                inserts(f, t)
        f.write("COMMIT;\n")
for t in S:
    t["data"].to_csv(OUT / "csv" / f"{t['name']}.csv", index=False)

pivot_jds = ",\n  ".join(f"MAX(CASE WHEN d.dimension_code = '{d}' THEN s.score END) AS `{JDS_COLUMN[d]}`" for d in DIMS)
pivot_sds = ",\n  ".join(f"MAX(CASE WHEN t.trait_code = '{c}' THEN s.score END) AS `{c}`" for c, _, _ in TRAITS)
zs = ",\n  ".join(f"ROUND((`{c}` - AVG(`{c}`) OVER ()) / STDDEV_SAMP(`{c}`) OVER (), 4) AS `{c}_z`" for c, _, _ in TRAITS)
dimcols = ",\n  ".join(f"COALESCE(MAX(d.dimension_code = '{d}'), 0) AS `dim_{d}`" for d in DIMS)
VIEWS = f"""-- VRIDDHI analysis views - derived values are computed here, never stored in the core tables
USE `{DB}`;

CREATE OR REPLACE VIEW v_company_job_title AS
SELECT f.company_job_title_id, f.reference_no, c.company_name, c.company_type, c.is_placeholder_employer,
       t.job_title, t.base_role, t.seniority, f.min_experience_years,
       f.min_salary_lpa, f.avg_salary_lpa, f.max_salary_lpa,
       f.max_salary_lpa - f.min_salary_lpa AS salary_spread_lpa,
       ROUND(f.max_salary_lpa / f.min_salary_lpa, 2) AS salary_range_ratio,
       f.num_of_jobs, LN(1 + f.num_of_jobs) AS log_num_jobs,
       f.is_min_salary_implausible, f.is_wide_salary_range, f.is_senior_zero_exp, f.is_num_jobs_outlier, f.is_salary_outlier_in_title,
       (c.is_placeholder_employer = 0) AS in_analysis_sample
FROM fact_company_job_title f
JOIN dim_company c ON c.company_id = f.company_id
JOIN dim_job_title t ON t.job_title_id = f.job_title_id;

CREATE OR REPLACE VIEW v_job_posting AS
SELECT p.posting_id, p.job_title_raw, p.job_title_clean, r.role_family, r.is_analytics, p.role_source,
       sn.seniority, sn.seniority_rank, p.exp_min_years, p.exp_max_years,
       (p.exp_min_years + p.exp_max_years) / 2 AS exp_mid_years,
       b.salary_band_id AS salary_band_ord, b.band_label AS salary_band, b.low_lpa AS salary_low_lpa, b.high_lpa AS salary_high_lpa,
       (b.low_lpa + b.high_lpa) / 2 AS salary_mid_lpa, (b.salary_band_id >= 5) AS is_high_pay_15plus,
       c.city_name AS primary_city, c.city_category, COALESCE(pc.n_cities, 0) AS n_cities,
       p.location_raw, p.job_description,
       p.is_job_type_tagged, p.is_desc_missing, p.is_desc_truncated, p.is_skills_truncated,
       p.is_near_duplicate, p.is_possible_repost, p.is_spam, p.is_international, p.is_salary_exp_inconsistent,
       (p.is_spam = 0 AND p.is_international = 0 AND p.is_near_duplicate = 0) AS in_india_sample,
       (p.is_spam = 0 AND p.is_international = 0 AND p.is_near_duplicate = 0 AND r.is_analytics = 1) AS in_core_analytics,
       (p.is_spam = 0 AND p.is_international = 0 AND p.is_near_duplicate = 0 AND r.is_analytics = 1
        AND p.is_salary_exp_inconsistent = 0) AS in_salary_model
FROM fact_job_posting p
JOIN dim_role_family r ON r.role_family_id = p.role_family_id
JOIN dim_seniority sn ON sn.seniority_id = p.seniority_id
JOIN dim_salary_band b ON b.salary_band_id = p.salary_band_id
JOIN dim_city c ON c.city_id = p.primary_city_id
LEFT JOIN (SELECT posting_id, COUNT(*) AS n_cities FROM bridge_posting_city GROUP BY posting_id) pc ON pc.posting_id = p.posting_id;

CREATE OR REPLACE VIEW v_posting_skill AS
SELECT b.posting_id, s.skill_id, s.skill_name, s.skill_type, b.found_in
FROM bridge_posting_skill b
JOIN dim_skill s ON s.skill_id = b.skill_id;

CREATE OR REPLACE VIEW v_posting_dimension AS
SELECT p.posting_id,
  {dimcols}
FROM fact_job_posting p
LEFT JOIN bridge_posting_skill b ON b.posting_id = p.posting_id
LEFT JOIN map_skill_dimension m ON m.skill_id = b.skill_id
LEFT JOIN dim_skill_dimension d ON d.dimension_id = m.dimension_id
GROUP BY p.posting_id;

CREATE OR REPLACE VIEW v_skill_demand_core AS
SELECT s.skill_name, s.skill_type, COUNT(DISTINCT b.posting_id) AS postings,
       ROUND(COUNT(DISTINCT b.posting_id) / (SELECT COUNT(*) FROM v_job_posting WHERE in_core_analytics = 1), 4) AS share_of_core_postings
FROM bridge_posting_skill b
JOIN dim_skill s ON s.skill_id = b.skill_id
JOIN v_job_posting v ON v.posting_id = b.posting_id AND v.in_core_analytics = 1
GROUP BY s.skill_name, s.skill_type;

CREATE OR REPLACE VIEW v_jds_wide AS
SELECT e.jds_employee_id, e.source_id,
  {pivot_jds},
  e.salary_hike_high
FROM jds_employee e
JOIN fact_jds_skill_score s ON s.jds_employee_id = e.jds_employee_id
JOIN dim_skill_dimension d ON d.dimension_id = s.dimension_id
GROUP BY e.jds_employee_id, e.source_id, e.salary_hike_high;

CREATE OR REPLACE VIEW v_sds_wide AS
SELECT w.*,
  {zs}
FROM (
  SELECT e.sds_employee_id, e.source_id,
    {pivot_sds},
    e.success_high
  FROM sds_employee e
  JOIN fact_sds_trait_score s ON s.sds_employee_id = e.sds_employee_id
  JOIN dim_personality_trait t ON t.trait_id = s.trait_id
  GROUP BY e.sds_employee_id, e.source_id, e.success_high
) w;

CREATE OR REPLACE VIEW v_market_vs_success AS
SELECT d.dimension_code, d.dimension_name,
       ROUND(SUM(CASE WHEN pd.flag = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS market_demand_share_core,
       (SELECT ROUND(AVG(s.score), 3) FROM fact_jds_skill_score s JOIN jds_employee e ON e.jds_employee_id = s.jds_employee_id
         WHERE s.dimension_id = d.dimension_id AND e.salary_hike_high = 1) AS jds_mean_score_high_hike,
       (SELECT ROUND(AVG(s.score), 3) FROM fact_jds_skill_score s JOIN jds_employee e ON e.jds_employee_id = s.jds_employee_id
         WHERE s.dimension_id = d.dimension_id AND e.salary_hike_high = 0) AS jds_mean_score_low_hike
FROM dim_skill_dimension d
CROSS JOIN (SELECT posting_id FROM v_job_posting WHERE in_core_analytics = 1) c
LEFT JOIN (
  SELECT DISTINCT b.posting_id, m.dimension_id, 1 AS flag
  FROM bridge_posting_skill b JOIN map_skill_dimension m ON m.skill_id = b.skill_id
) pd ON pd.posting_id = c.posting_id AND pd.dimension_id = d.dimension_id
GROUP BY d.dimension_id, d.dimension_code, d.dimension_name;
"""
(OUT / "sql" / "04_views.sql").write_text(VIEWS, encoding="utf-8")

# expected values for the post-load verification script
exp_counts = {t["name"]: len(t["data"]) for t in S}
dim_share = {d: round(an.loc[an.in_core_analytics == 1, f"dim_{d}"].mean(), 4) for d in DIMS}
ver = [f"-- Run after loading. Every 'expected' value was computed from the cleaned data by build_database.py.\nUSE `{DB}`;\n"]
ver.append("SELECT 'row counts' AS check_name, t.table_name, t.actual, t.expected, IF(t.actual = t.expected, 'PASS', 'FAIL') AS result FROM (\n" +
           "\nUNION ALL ".join(f"SELECT '{n}' AS table_name, (SELECT COUNT(*) FROM `{n}`) AS actual, {c} AS expected" for n, c in exp_counts.items()) +
           "\n) t;\n")
ver.append(f"SELECT 'core analytics postings' AS check_name, COUNT(*) AS actual, {int(an.in_core_analytics.sum())} AS expected FROM v_job_posting WHERE in_core_analytics = 1;\n")
ver.append(f"SELECT 'india sample postings' AS check_name, COUNT(*) AS actual, {int(an.in_india_sample.sum())} AS expected FROM v_job_posting WHERE in_india_sample = 1;\n")
ver.append(f"SELECT 'total openings (DS)' AS check_name, SUM(num_of_jobs) AS actual, {int(ds.num_of_jobs.sum())} AS expected FROM fact_company_job_title;\n")
ver.append("SELECT 'orphan postings without role family' AS check_name, COUNT(*) AS actual, 0 AS expected FROM fact_job_posting p LEFT JOIN dim_role_family r ON r.role_family_id = p.role_family_id WHERE r.role_family_id IS NULL;\n")
ver.append("SELECT 'dimension demand (core)' AS check_name, dimension_code, market_demand_share_core AS actual, CASE dimension_code " +
           " ".join(f"WHEN '{d}' THEN {v}" for d, v in dim_share.items()) + " END AS expected FROM v_market_vs_success;\n")
(OUT / "sql" / "05_verify.sql").write_text("".join(ver), encoding="utf-8")

# ======================================================================= ERD (Mermaid) + schema doc


def mtype(t):
    return re.sub(r"\(.*", "", t.split()[0]).lower().replace("enum", "enum").replace("tinyint", "tinyint")


rel = {"bridge_posting_city": "}o--||", "bridge_posting_skill": "}o--||"}
erd = ["erDiagram"]
for t in S:
    if t["layer"] == "staging":
        continue
    erd.append(f"    {t['name']} {{")
    fkcols = {c for c, _, _ in t["fks"]}
    for c, typ, n, cm in t["cols"]:
        keys = ",".join(k for k, cond in (("PK", c in t["pk"]), ("FK", c in fkcols)) if cond)
        erd.append(f"        {mtype(typ)} {c}{(' ' + keys) if keys else ''}")
    erd.append("    }")
for t in S:
    for col, rt, rc in t["fks"]:
        erd.append(f'    {rt} ||--o{{ {t["name"]} : "{col}"')
mermaid = "\n".join(erd)
staging_note = "\n".join(f"- `{t['name']}` ({len(t['data']):,} rows) - {t['comment']}" for t in S if t["layer"] == "staging")
(OUT / "ERD.md").write_text(
    "# Entity-Relationship Diagram (core + metadata layer)\n\n"
    "Rendered automatically on GitHub / VS Code / any Mermaid viewer. Generated from the same schema definition as the DDL.\n\n"
    "```mermaid\n" + mermaid + "\n```\n\n**Staging layer** (raw copies, no relationships, kept for audit):\n\n" + staging_note + "\n", encoding="utf-8")

doc = ["# Vriddhi database - schema reference\n",
       f"Database `{DB}` (MySQL 8, InnoDB, utf8mb4). {sum(1 for t in S if t['layer'] != 'staging')} core/metadata tables, "
       f"{sum(1 for t in S if t['layer'] == 'staging')} staging tables, {VIEWS.count('CREATE OR REPLACE VIEW')} views.\n"]
for layer, title in [("core", "Core (3NF)"), ("metadata", "Metadata"), ("staging", "Staging (raw)")]:
    doc.append(f"\n## {title}\n")
    for t in S:
        if t["layer"] != layer:
            continue
        fk = {c: f"{rt}.{rc}" for c, rt, rc in t["fks"]}
        doc.append(f"\n### `{t['name']}` - {len(t['data']):,} rows\n{t['comment']}\n\n| Column | Type | Key | Null | Description |\n|---|---|---|---|---|")
        for c, typ, n, cm in t["cols"]:
            key = " ".join(x for x in ["PK" if c in t["pk"] else "", f"FK → {fk[c]}" if c in fk else ""] if x)
            doc.append(f"| `{c}` | {typ} | {key} | {'yes' if n else 'no'} | {cm} |")
        if t["checks"]:
            doc.append("\nChecks: " + "; ".join(f"`{c}`" for c in t["checks"]))
(OUT / "SCHEMA.md").write_text("\n".join(doc) + "\n", encoding="utf-8")

print("Validation: all PK / FK / NOT NULL / CHECK / unique constraints hold; normalised model reproduces cleaned flags.")
for t in S:
    print(f"  {t['layer']:9} {t['name']:28} {len(t['data']):>8,} rows")
print("\nFiles:", sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.suffix in (".sql", ".md")))
for p in sorted((OUT / "sql").glob("*.sql")):
    print(f"  {p.name}: {p.stat().st_size / 1e6:.1f} MB")
