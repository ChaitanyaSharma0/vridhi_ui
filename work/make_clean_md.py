"""Generate CLEAN.md: exactly what was cleaned, with REAL before/after examples pulled from the original and cleaned
files (nothing typed by hand), plus the rows-affected counts from the data-quality log."""
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
RAW = HERE.parent
r_ds = pd.read_csv(RAW / "DataScience Jobs.csv")
r_an = pd.read_csv(RAW / "Analytics Jobs.csv")
r_sd = pd.read_excel(RAW / "SDS Personality Traits.xlsx")
ds = pd.read_csv(HERE / "clean" / "ds_jobs_clean.csv")
an = pd.read_csv(HERE / "clean" / "analytics_jobs_clean.csv")
log = pd.read_csv(HERE / "outputs" / "data_quality_log.csv", keep_default_na=False)
ver = (HERE / "VERIFICATION.md").read_text(encoding="utf-8")
n_pass = re.search(r"\*\*(\d+) of (\d+) checks pass", ver)
raw_an = r_an.set_index("s_no")


def table(df):
    return df.to_markdown(index=False)


def ex(df, n=4):
    return table(df.head(n))


out = ["# CLEAN.md - exactly what we cleaned\n",
       "Every change below was made by `01_clean.py` (+ `role_rules.py`, `taxonomy.py`). Row counts come from the "
       "data-quality log; every example is a **real row**, pulled automatically from the original file and the cleaned "
       f"file. An independent script (`verify_against_raw.py`) recomputed every figure from the original files: "
       f"**{n_pass.group(1)} of {n_pass.group(2)} checks pass** (see `VERIFICATION.md`).\n",
       "**Golden rule:** nothing was silently deleted. The only removed rows are 1,001 exact duplicate postings. "
       "Everything else is kept and *flagged*, and the original values are kept next to the cleaned ones.\n"]

# ---------------------------------------------------------------- examples
out.append("\n## 1. DataScience Jobs (1,602 rows -> 1,602 rows)\n")
out.append("**Salary text -> numbers (all 1,602 rows).**\n")
e = r_ds.head(3)[["company_name", "job_title", "min_salary", "avg_salary", "max_salary"]].join(
    ds.head(3)[["min_salary_lpa", "avg_salary_lpa", "max_salary_lpa"]])
out.append(ex(e) + "\n")
dup = r_ds[r_ds.reference_no.duplicated(keep=False)].sort_values("reference_no").head(4)[["reference_no", "company_name", "job_title"]]
out.append("\n**`reference_no` is not unique** (134 numbers shared by 276 *different* rows) -> new key `row_id`. Example:\n\n" + ex(dup) + "\n")
grp = ds[ds.company_group.isin(["BNP Paribas", "HSBC"]) & ds.job_title.isin(["Business Analyst", "Senior Business Analyst"])][
    ["company_name", "company_group", "job_title", "avg_salary_lpa", "num_of_jobs"]]
out.append("\n**Same employer group under two names** - the units list the same title with different salaries, so they stay "
           "separate companies and are linked by a new `company_group` column (13 rows):\n\n" + ex(grp, 6) + "\n")
ph = ds[ds.is_placeholder_employer == 1][["company_name", "job_title", "avg_salary_lpa"]]
out.append(f"\n**Placeholder employers flagged** (`is_placeholder_employer`, {len(ph)} rows):\n\n" + ex(ph, 5) + "\n")
low = ds[ds.min_salary_implausible == 1][["company_name", "job_title", "min_salary_lpa", "avg_salary_lpa", "max_salary_lpa"]]
out.append(f"\n**Implausible minimum salary < 1 LPA flagged** (`min_salary_implausible`, {len(low)} rows):\n\n" + ex(low) + "\n")
sz = ds[ds.senior_zero_exp == 1][["company_name", "job_title", "min_experience"]]
out.append(f"\n**'Senior' title with 0 years' experience flagged** (`senior_zero_exp`, {len(sz)} rows), e.g.:\n\n" + ex(sz, 3) + "\n")
oj = ds.nlargest(3, "num_of_jobs")[["company_name", "job_title", "num_of_jobs", "log_num_jobs"]]
out.append(f"\n**Bulk-hiring outliers kept but flagged** (`num_jobs_outlier`, {int(ds.num_jobs_outlier.sum())} rows) and log-transformed:\n\n" + ex(oj, 3) + "\n")

out.append("\n## 2. Analytics Jobs (15,841 rows -> 14,840 rows)\n")
exd = r_an[r_an.drop(columns="s_no").duplicated(keep=False)].sort_values(["job_desig", "location"]).head(2)[["s_no", "job_desig", "location", "salary"]]
out.append("**1,001 exact duplicates removed** (every field identical except `s_no`). Example pair:\n\n" + ex(exd, 2) + "\n")
tc = an[an.job_desig.str.lower() != an.job_title_clean.str.lower()].sample(6, random_state=3)[["job_desig", "job_title_clean"]]
out.append(f"\n**Designation noise stripped** into `job_title_clean` ({int(log.loc[log.issue.str.startswith('Designations padded'), 'rows_affected'].iloc[0]):,} rows):\n\n" + ex(tc, 6) + "\n")
exs = an.sample(3, random_state=8)[["experience", "exp_min", "exp_max", "exp_mid", "salary", "salary_band_ord", "salary_low_lpa", "salary_high_lpa"]]
out.append("\n**Experience and salary text parsed** (all rows):\n\n" + ex(exs, 3) + "\n")
lc = an[an.location.str.contains(r"Gurgaon|Gurugram|Bangalore|Sector|Kharadi|Lower Parel|Secunderabad|Anywhere|Thane", regex=True)]\
    .drop_duplicates("location").sample(8, random_state=1)[["location", "primary_city", "cities", "city_tier"]]
out.append("\n**Locations mapped to canonical cities / metro areas** (1,355 raw strings):\n\n" + ex(lc, 8) + "\n")
intl = an[an.is_international == 1].drop_duplicates("location").head(5)[["location", "primary_city", "is_international"]]
out.append(f"\n**Overseas-only postings flagged** ({int(an.is_international.sum())} rows):\n\n" + ex(intl) + "\n")
sk = an[(an.education_mentioned.notna()) | (an.job_meta_tags.notna())].sample(4, random_state=4)
sk = sk[["s_no", "skills", "soft_skills", "education_mentioned", "job_meta_tags"]].assign(key_skills_raw=raw_an.loc[sk.s_no, "key_skills"].values)
out.append("\n**Skills cleaned** - lower-cased, synonyms/variants merged, junk removed, non-skills separated "
           "(education, job tags, soft skills):\n\n" + ex(sk[["key_skills_raw", "skills", "soft_skills", "education_mentioned", "job_meta_tags"]], 4) + "\n")
fd = an[an.skills_from_desc.notna() & an.skills_truncated.eq(1)].sample(3, random_state=5)[["s_no", "skills", "skills_from_desc"]]
out.append(f"\n**Skills recovered from descriptions** because 87% of skill lists were cut off with '...' "
           f"({int(log.loc[log.issue.str.startswith('Skills recovered'), 'rows_affected'].iloc[0]):,} extra mentions):\n\n" + ex(fd, 3) + "\n")
rf = an.sample(8, random_state=11)[["job_title_clean", "role_family", "seniority", "is_analytics_role"]]
out.append("\n**10,097 designations -> 22 role families + 5 seniority levels** (manually audited on an independent sample of 150: "
           "~91% exact, ~92% analytics vs non-analytics):\n\n" + ex(rf, 8) + "\n")
sp = an[an.is_spam == 1].head(3)[["job_desig", "is_spam"]]
out.append(f"\n**Spam postings flagged** ({int(an.is_spam.sum())} rows):\n\n" + ex(sp, 3) + "\n")
jt = r_an.job_type.value_counts(dropna=False).rename_axis("raw job_type").reset_index(name="rows")
out.append("\n**`job_type` - 5 spellings of one value and 76% missing** -> original column kept unchanged, plus a 0/1 job_type_tagged flag:\n\n" + table(jt) + "\n")

out.append("\n## 3. JDS Skill Traits (139 rows -> 139 rows) and SDS Personality Traits (161 -> 161)\n")
out.append("- Column `maths-stats_skills` renamed `maths_stats_skills` (hyphen is invalid in SAS/SQL); `salary_hike_high_or_low` -> `salary_hike_high`.\n"
           f"- SDS columns with stray spaces renamed: `{r_sd.columns[2]!r}` -> `extraversion`, `{r_sd.columns[-1]!r}` -> `success_high`.\n"
           "- IDs are not unique (JDS: 2 ids shared by 4 different people; SDS: 9 ids shared by 18) -> surrogate `row_id`.\n"
           "- Range checks: all JDS scores within 1-5, all SDS scores within 17-68; no missing values; targets balanced (53% / 47%).\n"
           "- **No score was changed.** Ceiling effect documented (18-58% of JDS scores are a perfect 5.0).\n"
           "- Derived (added, not replacing): skill mean/min/range, weakest/strongest skill; trait z-scores, emotional_stability_z (= -neuroticism_z), dominant trait. No composite indices or tiny segments.\n")

out.append("\n## 4. Full list of issues and treatments (from the data-quality log)\n")
for f_, g in log.groupby("file", sort=False):
    out.append(f"\n### {f_}\n\n| Stage | Issue | Rows | Treatment |\n|---|---|---|---|")
    for _, r in g.iterrows():
        out.append(f"| {r.stage} | {r.issue} | {int(r.rows_affected):,} | {r.treatment} |")
out.append("\n\n## 5. What we deliberately did NOT do\n"
           "- No imputation of missing descriptions or salaries (would invent data).\n"
           "- No deletion of outliers (bulk hiring and top-employer salaries are real market facts) - flagged instead.\n"
           "- No change to any JDS / SDS score.\n"
           "- No merging of companies whose units post different salaries.\n")
(HERE / "CLEAN.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("CLEAN.md written:", len("\n".join(out)), "chars")
