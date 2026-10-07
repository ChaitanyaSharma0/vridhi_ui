"""Independent verification: recompute every claim in the cleaning log directly from the ORIGINAL files,
and reconcile the cleaned files row-by-row against the originals. Writes VERIFICATION.md.

Nothing here reuses the cleaning code's results except to compare against them.
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
C = HERE / "clean"
rows = []


def check(area, claim, expected, actual, ok=None):
    ok = (expected == actual) if ok is None else ok
    rows.append((area, claim, str(expected), str(actual), "PASS" if ok else "FAIL"))


# ---------------------------------------------------------------- raw
rds = pd.read_csv(RAW / "DataScience Jobs.csv")
ran = pd.read_csv(RAW / "Analytics Jobs.csv")
rj = pd.read_excel(RAW / "JDS Skill Traits.xlsx")
rs = pd.read_excel(RAW / "SDS Personality Traits.xlsx")
ds = pd.read_csv(C / "ds_jobs_clean.csv")
an = pd.read_csv(C / "analytics_jobs_clean.csv")
j = pd.read_csv(C / "jds_clean.csv")
s = pd.read_csv(C / "sds_clean.csv")

# ---------------------------------------------------------------- shapes from the brief / data description
check("Raw shape", "DataScience Jobs has ~1,600 rows x 8 columns", (1602, 8), rds.shape)
check("Raw shape", "Analytics Jobs has ~15,800 rows x 8 columns", (15841, 8), ran.shape)
check("Raw shape", "JDS has ~140 rows x 7 columns", (139, 7), rj.shape)
check("Raw shape", "SDS has ~160 rows x 7 columns", (161, 7), rs.shape)
check("Raw columns", "DataScience Jobs columns match the data dictionary",
      ["reference_no", "company_name", "job_title", "min_experience", "avg_salary", "min_salary", "max_salary", "num_of_jobs"], list(rds.columns))
check("Raw columns", "Analytics Jobs columns match the data dictionary",
      ["s_no", "experience", "job_description", "job_desig", "job_type", "key_skills", "location", "salary"], list(ran.columns))

# ---------------------------------------------------------------- DataScience Jobs claims
dup_ref = rds.reference_no.duplicated(keep=False)
check("DS claims", "reference_no numbers shared by >1 row", 134, rds.loc[dup_ref, "reference_no"].nunique())
check("DS claims", "rows with a shared reference_no", 276, int(dup_ref.sum()))
num = {c: rds[c].str.rstrip("L").astype(float) for c in ["min_salary", "avg_salary", "max_salary"]}
check("DS claims", "min <= avg <= max violations", 0, int(((num["min_salary"] > num["avg_salary"]) | (num["avg_salary"] > num["max_salary"])).sum()))
check("DS claims", "min salary < 1 LPA", 3, int((num["min_salary"] < 1).sum()))
check("DS claims", "max salary > 6x min", 34, int((num["max_salary"] / num["min_salary"] > 6).sum()))
check("DS claims", "Senior titles with 0 min experience", 14, int((rds.job_title.str.startswith("Senior") & (rds.min_experience == 0)).sum()))
check("DS claims", "min_experience > 12 (all Data Architect)", (12, {"Data Architect"}),
      (int((rds.min_experience > 12).sum()), set(rds.loc[rds.min_experience > 12, "job_title"])))
check("DS claims", "num_of_jobs median / max", (22.0, 4200), (float(rds.num_of_jobs.median()), int(rds.num_of_jobs.max())))
check("DS claims", "max num_of_jobs is TCS Business Analyst", ("TCS", "Business Analyst"),
      tuple(rds.loc[rds.num_of_jobs.idxmax(), ["company_name", "job_title"]]))
ph = rds.company_name.str.lower().str.strip().isin(["confidential", "xyz company", "data entry", "freelancer.com", "freelance consultants"])
check("DS claims", "placeholder employer rows", 12, int(ph.sum()))
check("DS claims", "companies (distinct) / job titles (distinct)", (642, 10), (rds.company_name.nunique(), rds.job_title.nunique()))
check("DS claims", "rows of the BNP Paribas / HSBC groups (4 names, linked via company_group)", 13, int(rds.company_name.str.lower().isin(["bnp paribas india solutions", "hsbc technology", "bnp paribas", "hsbc"]).sum()))

# ---------------------------------------------------------------- Analytics Jobs claims
ex = ran.drop(columns="s_no").duplicated()
check("AN claims", "exact duplicate postings", 1001, int(ex.sum()))
check("AN claims", "distinct designations", 10097, ran.job_desig.nunique())
check("AN claims", "distinct location strings", 1355, ran.location.nunique())
check("AN claims", "job_type missing: 76% of original rows (12,011)", ("76%", 12011), (f"{ran.job_type.isna().mean():.0%}", int(ran.job_type.isna().sum())))
check("AN claims", "job_type missing: 78% after removing exact duplicates (11,567)", ("78%", 11567), (f"{ran.loc[~ex].job_type.isna().mean():.0%}", int(ran.loc[~ex].job_type.isna().sum())))
check("AN claims", "job_type spellings", {"Analytics", "analytics", "ANALYTICS", "analytic", "Analytic"}, set(ran.job_type.dropna().unique()))
check("AN claims", "job_description missing (raw)", 3508, int(ran.job_description.isna().sum()))
check("AN claims", "key_skills truncated with '...' share ~87%", "87%", f"{ran.key_skills.str.endswith('...', na=False).mean():.0%}")
check("AN claims", "salary has exactly 6 bands", {"0to3", "3to6", "6to10", "10to15", "15to25", "25to50"}, set(ran.salary.unique()))
check("AN claims", "experience always 'a-b yrs'", True, bool(ran.experience.str.fullmatch(r"\d+-\d+ yrs").all()))
check("AN claims", "multi-city locations ~16%", "16%", f"{ran.location.str.contains(r'[,/]').mean():.0%}")
check("AN claims", "';-' bullet descriptions", 1573, int(ran.job_description.str.contains(";-", na=False).sum()))

# ---------------------------------------------------------------- JDS / SDS claims
check("JDS claims", "duplicated ids / rows involved", (2, 4), (rj.id.duplicated().sum(), int(rj.id.duplicated(keep=False).sum())))
SKC = [c for c in rj.columns if c.endswith("_skills")]
check("JDS claims", "scores within 1-5", True, bool(((rj[SKC] >= 1) & (rj[SKC] <= 5)).all().all()))
check("JDS claims", "share of perfect 5.0 (big data 18% ... dashboards 58%)", [18, 41, 45, 49, 58], [round(v * 100) for v in (rj[SKC] == 5).mean()])
check("JDS claims", "high-hike share 53%", "53%", f"{rj.iloc[:, -1].mean():.0%}")
check("SDS claims", "duplicated ids / rows involved", (9, 18), (rs.id.duplicated().sum(), int(rs.id.duplicated(keep=False).sum())))
check("SDS claims", "column names with stray spaces", [" extraversion", "success_ classification_ high_low"],
      [c for c in rs.columns if c != c.strip() or "  " in c or "_ " in c])
check("SDS claims", "trait range 17-68", (17, 68), (int(rs.iloc[:, 1:6].min().min()), int(rs.iloc[:, 1:6].max().max())))
check("SDS claims", "success share 53%", "53%", f"{rs.iloc[:, -1].mean():.0%}")

# ---------------------------------------------------------------- reconciliation: cleaned vs raw
check("Reconcile DS", "row count unchanged", len(rds), len(ds))
m = rds.reset_index(drop=True)
check("Reconcile DS", "reference_no, job_title, min_experience, num_of_jobs identical row by row", True,
      bool((m.reference_no.values == ds.reference_no.values).all() and (m.job_title.values == ds.job_title.values).all()
           and (m.min_experience.values == ds.min_experience.values).all() and (m.num_of_jobs.values == ds.num_of_jobs.values).all()))
for c in ["min_salary", "avg_salary", "max_salary"]:
    check("Reconcile DS", f"{c}_lpa equals the raw text value", True, bool(np.allclose(num[c].values, ds[c + "_lpa"].values)))
same_co = (m.company_name.str.strip().values == ds.company_name.values)
check("Reconcile DS", "company_name identical to raw for every row (no merging)", 0, int((~same_co).sum()))
check("Reconcile DS", "total openings preserved", int(rds.num_of_jobs.sum()), int(ds.num_of_jobs.sum()))

kept = ran.loc[~ex].set_index("s_no")
an_i = an.set_index("s_no")
check("Reconcile AN", "rows = raw minus exact duplicates", len(ran) - int(ex.sum()), len(an))
check("Reconcile AN", "every cleaned s_no exists in raw and was not an exact duplicate", True, bool(an_i.index.isin(kept.index).all()))
check("Reconcile AN", "salary band identical to raw for every row", True, bool((kept.loc[an_i.index, "salary"].values == an_i.salary.values).all()))
check("Reconcile AN", "salary band counts identical to raw (after de-dup)", kept.salary.value_counts().sort_index().to_dict(),
      an.salary.value_counts().sort_index().to_dict())
e = kept.loc[an_i.index, "experience"].str.extract(r"(\d+)-(\d+)").astype(float)
check("Reconcile AN", "exp_min / exp_max equal the raw text", True,
      bool((e[0].values == an_i.exp_min.values).all() and (e[1].values == an_i.exp_max.values).all()))
ws = lambda x: re.sub(r"\s+", " ", str(x).encode("ascii", "ignore").decode()).strip()
check("Reconcile AN", "job_desig equals raw (after whitespace/ASCII normalisation)", True,
      bool((kept.loc[an_i.index, "job_desig"].map(ws).values == an_i.job_desig.astype(str).values).all()))
check("Reconcile AN", "location equals raw (after whitespace normalisation)", True,
      bool((kept.loc[an_i.index, "location"].map(ws).values == an_i.location.astype(str).values).all()))
check("Reconcile AN", "job_type_tagged equals raw non-missing job_type", True,
      bool((kept.loc[an_i.index, "job_type"].notna().astype(int).values == an_i.job_type_tagged.values).all()))
check("Reconcile AN", "original job_type column kept unchanged", True,
      bool(kept.loc[an_i.index, "job_type"].fillna("").values.tolist() == an_i.job_type.fillna("").values.tolist()))
# compound skills ('Oracle SQL', 'SQL Server', 'SAS SQL') must set has_sql ('No SQL' = NoSQL excluded): raw key_skills mentioning SQL -> flag 1
sql_raw = kept.loc[an_i.index, "key_skills"].fillna("").str.lower().str.contains(r"(?<![a-z])(?<!no )(?:sql|mysql|postgresql|plsql)(?![a-z])")
check("Reconcile AN", "raw key_skills mentioning SQL but has_sql = 0", 0, int((sql_raw.values & (an_i.has_sql.values == 0)).sum()))
# every clean skill must come from the raw key_skills or the raw description (no invented skills)
raw_txt = (kept.loc[an_i.index, "key_skills"].fillna("") + " " + kept.loc[an_i.index, "job_description"].fillna("")).str.lower()
norm_txt = raw_txt.str.replace(r"[^a-z0-9+#&]", "", regex=True)
bad = 0
SYN_REVERSE_OK = {"machine learning", "artificial intelligence", "natural language processing", "power bi", "excel", "big data",
                  "data visualization", "r", "python", "sas", "c++", "plsql", "fp&a", "node.js", "javascript", "angularjs",
                  "ecommerce", "servicenow", "data warehousing", "data warehouse", "web services", "presales", "frontend", "powerpoint",
                  "statistical modelling", "predictive modelling"}
for sk_all, t, nt in zip(an_i.skills_all.fillna(""), raw_txt, norm_txt):
    for sk in [x for x in sk_all.split("|") if x]:
        key = re.sub(r"[^a-z0-9+#&]", "", sk)
        if key and key not in nt and sk not in SYN_REVERSE_OK:
            bad += 1
check("Reconcile AN", "skills not traceable to the raw key_skills/description text (synonym targets excepted)", 0, bad)

check("Reconcile JDS", "all scores and targets identical to raw", True,
      bool(np.allclose(rj[SKC].values, j[[c.replace("-", "_") for c in SKC]].values) and (rj.iloc[:, -1].values == j.salary_hike_high.values).all()))
tr = ["neuroticism", "extraversion", "openness_to_experience", "agreeableness", "conscientiousness"]
check("Reconcile SDS", "all trait scores and targets identical to raw", True,
      bool((rs.iloc[:, 1:6].values == s[tr].values).all() and (rs.iloc[:, -1].values == s.success_high.values).all()))

res = pd.DataFrame(rows, columns=["area", "claim / check", "expected", "actual", "result"])
n_fail = (res.result == "FAIL").sum()
with open(HERE / "VERIFICATION.md", "w", encoding="utf-8") as f:
    f.write("# Verification against the original files\n\n"
            f"Every figure used in the cleaning log was recomputed **directly from the 4 original files**, and every cleaned file "
            f"was reconciled row by row against its original. **{len(res) - n_fail} of {len(res)} checks pass, {n_fail} fail.**\n\n")
    f.write(res.to_markdown(index=False) + "\n")
print(res.to_string(index=False))
print(f"\n{len(res) - n_fail}/{len(res)} PASS")
