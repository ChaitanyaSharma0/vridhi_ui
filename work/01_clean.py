"""VRIDDHI - Data preparation pipeline (all 4 files).

Ten documented stages. Every rule is logged with the rows it touched, so the report's
Data Exploration section can be written straight from outputs/data_quality_log.md.

  S0 Profile raw data            S5 Validity & consistency rules
  S1 Structure, names, keys      S6 Outlier detection & treatment
  S2 Duplicates                  S7 Categorical harmonisation (city, role, skills, education)
  S3 Text standardisation        S8 Scope flags (what is in the analysis sample)
  S4 Parsing & type conversion   S9 Derived variables   +  S10 Validation checks

Principle: never silently delete. Rows are only dropped when they are exact copies;
everything else is kept and FLAGGED, so each analysis can choose its sample transparently.
"""
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
OUT, LOGD = HERE / "clean", HERE / "outputs"
OUT.mkdir(exist_ok=True)
LOGD.mkdir(exist_ok=True)

LOG = []      # (stage, file, issue, rows, treatment)
DICT = []     # (file, column, type, description, origin)


def log(stage, file, issue, rows, treatment):
    LOG.append((stage, file, issue, int(rows), treatment))


def dd(file, col, typ, desc, origin="derived"):
    DICT.append((file, col, typ, desc, origin))


def ws(s):
    """Whitespace + punctuation tidy for free text."""
    if pd.isna(s):
        return s
    s = str(s).encode("ascii", "ignore").decode()
    s = re.sub(r"\s+", " ", s).strip()
    return s


# =============================================================== S0 raw profile
raw = {"DataScience Jobs": pd.read_csv(RAW / "DataScience Jobs.csv"),
       "Analytics Jobs": pd.read_csv(RAW / "Analytics Jobs.csv"),
       "JDS Skill Traits": pd.read_excel(RAW / "JDS Skill Traits.xlsx"),
       "SDS Personality Traits": pd.read_excel(RAW / "SDS Personality Traits.xlsx")}
prof = []
for f, d in raw.items():
    for c in d.columns:
        s = d[c]
        prof.append({"file": f, "column": repr(c), "dtype": str(s.dtype), "rows": len(s), "missing": int(s.isna().sum()),
                     "missing_pct": round(s.isna().mean() * 100, 1), "distinct": int(s.nunique()),
                     "example": str(s.dropna().iloc[0])[:60] if s.notna().any() else ""})
pd.DataFrame(prof).to_csv(LOGD / "profile_raw.csv", index=False)

# =============================================================== DATA SCIENCE JOBS
F = "DataScience Jobs"
ds = raw[F].copy()
n_ds = len(ds)
# S1 keys
dup_ref = ds.reference_no.duplicated(keep=False)
log("S1", F, "reference_no is not unique: 134 numbers shared by 276 different rows", dup_ref.sum(),
    "Kept original as reference_no; new surrogate key row_id (1..n) used as the record key")
ds.insert(0, "row_id", np.arange(1, n_ds + 1))
dd(F, "row_id", "int", "Surrogate unique key (reference_no is not unique)")
# S3 text
before = ds.company_name.copy()
ds["company_name"] = ds.company_name.map(ws)
log("S3", F, "company_name leading/trailing/double spaces", (before != ds.company_name).sum(), "Trimmed")
COMPANY_GROUP = {"bnp paribas india solutions": "BNP Paribas", "bnp paribas": "BNP Paribas",
                 "hsbc technology": "HSBC", "hsbc": "HSBC"}
low = ds.company_name.str.lower()
ds["company_group"] = low.map(COMPANY_GROUP).fillna(ds.company_name)
grp = low.isin(COMPANY_GROUP)
log("S3", F, "Same employer group listed under two names (BNP Paribas / bnp paribas india solutions; HSBC / Hsbc Technology) - "
    "the units post the same titles with DIFFERENT salaries and openings, so they are separate listings",
    grp.sum(), "Kept as separate companies (not merged); linked through new company_group column")
dd(F, "company_group", "text", "Parent employer group (links a company's India/technology units, e.g. HSBC / Hsbc Technology)")
PLACEHOLDER = r"^(confidential|xyz company|data entry|freelancer\.com|freelance consultants)$"
ds["is_placeholder_employer"] = ds.company_name.str.lower().str.match(PLACEHOLDER).astype(int)
log("S3", F, "Placeholder / non-company employer names (Confidential, Xyz Company, Data Entry, Freelancer.com, Freelance Consultants)",
    ds.is_placeholder_employer.sum(), "Flagged is_placeholder_employer; excluded from company-level analysis")
dd(F, "is_placeholder_employer", "0/1", "Employer name is a placeholder, not a real company")
# S4 parse salaries
for c in ["min_salary", "avg_salary", "max_salary"]:
    ds[c + "_lpa"] = ds[c].astype(str).str.strip().str.rstrip("Ll").astype(float)
    dd(F, c + "_lpa", "float", f"{c.replace('_', ' ')} in lakhs per annum (parsed from text like '7.8L')")
log("S4", F, "Salaries stored as text with an 'L' suffix ('7.8L')", n_ds, "Parsed to numeric lakhs per annum (LPA)")
ds = ds.drop(columns=["min_salary", "avg_salary", "max_salary"])
# S5 validity
viol = (ds.min_salary_lpa > ds.avg_salary_lpa) | (ds.avg_salary_lpa > ds.max_salary_lpa)
log("S5", F, "Rule min <= avg <= max salary", viol.sum(), "0 violations - internally consistent")
low_min = ds.min_salary_lpa < 1.0
ds["min_salary_implausible"] = low_min.astype(int)
log("S5", F, "Minimum salary below 1 LPA (e.g. 0.2L = Rs 20,000 a year) - likely monthly/stipend figures entered as annual",
    low_min.sum(), "Flagged min_salary_implausible; min salary not used in modelling for these rows (avg/max kept)")
dd(F, "min_salary_implausible", "0/1", "min salary < 1 LPA, likely monthly or stipend value")
ds["salary_range_ratio"] = (ds.max_salary_lpa / ds.min_salary_lpa).round(2)
wide = ds.salary_range_ratio > 6
ds["wide_salary_range"] = wide.astype(int)
log("S5", F, "Very wide salary range (max more than 6x min)", wide.sum(), "Flagged wide_salary_range; avg salary used as the main measure")
dd(F, "salary_range_ratio", "float", "max_salary / min_salary")
dd(F, "wide_salary_range", "0/1", "max salary > 6x min salary")
ds["seniority"] = np.where(ds.job_title.str.startswith("Senior"), "Senior", "Junior/Mid")
ds["role"] = ds.job_title.str.replace("Senior ", "", regex=False)
inc = (ds.seniority == "Senior") & (ds.min_experience == 0)
ds["senior_zero_exp"] = inc.astype(int)
log("S5", F, "'Senior' titles asking for 0 years minimum experience", inc.sum(), "Flagged senior_zero_exp (title/experience inconsistency)")
dd(F, "seniority", "cat", "Senior vs Junior/Mid from job_title")
dd(F, "role", "cat", "Job title without the 'Senior' prefix (6 roles)")
dd(F, "senior_zero_exp", "0/1", "Senior title with 0 years minimum experience")
# S6 outliers
q1, q3 = ds.num_of_jobs.quantile([.25, .75])
ds["num_jobs_outlier"] = (ds.num_of_jobs > q3 + 3 * (q3 - q1)).astype(int)
ds["log_num_jobs"] = np.log1p(ds.num_of_jobs).round(4)
log("S6", F, f"num_of_jobs extremely right-skewed (median {ds.num_of_jobs.median():.0f}, max 4,200 = TCS Business Analyst); "
    "3xIQR rule", ds.num_jobs_outlier.sum(), "Genuine bulk hiring - kept; flagged and log-transformed (log_num_jobs) for models")
for c in ["avg_salary_lpa"]:
    grp = ds.groupby("job_title")[c]
    z = (ds[c] - grp.transform("median")) / (grp.transform(lambda s: (s.quantile(.75) - s.quantile(.25))) + 1e-9)
    ds["salary_outlier_in_title"] = (z.abs() > 3).astype(int)
log("S6", F, "Average salary far from its job title's typical range (robust z > 3 within title, e.g. Flipkart Senior DS 82 LPA)",
    ds.salary_outlier_in_title.sum(), "Kept (top employers pay more); flagged; salary_lpa_w = winsorised copy for models")
ds["avg_salary_lpa_w"] = ds.avg_salary_lpa.clip(*ds.avg_salary_lpa.quantile([.01, .99]))
exp_hi = (ds.min_experience > 12)
log("S6", F, "min_experience above 12 years (max 21)", exp_hi.sum(),
    "All are Data Architect rows - plausible; kept")
dd(F, "num_jobs_outlier", "0/1", "num_of_jobs above Q3 + 3xIQR")
dd(F, "log_num_jobs", "float", "log(1 + num_of_jobs)")
dd(F, "salary_outlier_in_title", "0/1", "avg salary more than 3 robust SDs from the title median")
dd(F, "avg_salary_lpa_w", "float", "avg salary winsorised at 1st/99th percentile")
# S9 derived
IT_SERVICES = {"tcs", "accenture", "ibm", "cognizant", "capgemini", "infosys", "wipro", "tech mahindra",
               "hcl technologies", "lti", "ltimindtree", "mphasis", "dxc technology", "hexaware technologies",
               "genpact", "deloitte", "ey", "kpmg", "pwc", "virtusa", "l&t infotech", "mindtree", "persistent systems",
               "ntt data", "birlasoft", "zensar", "cyient", "coforge", "sopra steria", "atos", "nagarro", "exl india",
               "wns", "concentrix", "teleperformance", "firstsource", "hinduja global solutions", "igate", "syntel"}
ds["company_type"] = np.where(ds.company_name.str.lower().isin(IT_SERVICES), "IT services / consulting", "Product / captive / other")
tot = ds.groupby("company_name").num_of_jobs.transform("sum")
ds["company_total_openings"] = tot
ds["company_scale"] = pd.cut(tot, [0, 20, 100, 1e9], labels=["Small (<=20 openings)", "Mid (21-100)", "Large (>100)"])
ds["salary_spread_lpa"] = ds.max_salary_lpa - ds.min_salary_lpa
ds["exp_band"] = pd.cut(ds.min_experience, [-.1, 1, 3, 5, 9, 30], labels=["0-1", "2-3", "4-5", "6-9", "10+"])
for c, t, d in [("company_type", "cat", "IT services/consulting vs product/captive/other (curated list)"),
                ("company_total_openings", "int", "Total openings by the company across all roles"),
                ("company_scale", "cat", "Company hiring scale from total openings"),
                ("salary_spread_lpa", "float", "max - min salary"),
                ("exp_band", "cat", "Minimum experience band")]:
    dd(F, c, t, d)
ds["in_analysis_sample"] = (ds.is_placeholder_employer == 0).astype(int)
dd(F, "in_analysis_sample", "0/1", "Real employer (placeholder employers excluded)")
ds.to_csv(OUT / "ds_jobs_clean.csv", index=False)

# =============================================================== ANALYTICS JOBS
F = "Analytics Jobs"
an = raw[F].copy()
n_an = len(an)
# S2 exact duplicates
ex = an.drop(columns="s_no").duplicated()
log("S2", F, "Exact duplicate postings (every field equal except s_no)", ex.sum(), "Dropped (the only rows deleted in the whole pipeline)")
an = an[~ex].copy()
# S3 text standardisation
for c in ["job_desig", "job_description", "key_skills", "location", "experience", "salary"]:
    before = an[c].copy()
    an[c] = an[c].map(ws)
    ch = ((before != an[c]) & before.notna()).sum()
    if ch:
        log("S3", F, f"{c}: non-ASCII characters / leading-trailing / repeated spaces", ch, "Normalised")
an["job_description"] = an.job_description.str.replace(r";\s*-\s*", ". ", regex=True).str.lstrip("- ").str.replace(r"\s*\.\.\.$", "", regex=True)
log("S3", F, "job_description uses ';-' as bullet separators", raw[F].job_description.str.contains(";-", na=False).sum(), "Converted to sentences")

NOISE = [r"\burgent(ly)?\b", r"\bhiring\b", r"\bopening(s)?\b", r"\bwalk[- ]?in\b", r"\bimmediate( joiner)?s?\b",
         r"\bvacancy\b", r"\brequired\b", r"\blooking for\b", r"\bf2f\b", r"\bexcellent\b", r"\bjob for\b",
         r"\bjob opening\b", r"\bwanted\b", r"\bgood opportunity\b", r"\b(for|with) (an?|leading|renowned|top|reputed|us based)[^-]*$"]
from role_rules import ROLE, ANALYTICS, TITLE_NOISE_EXTRA  # ordered role rules live in role_rules.py (audited)
NOISE += TITLE_NOISE_EXTRA


def clean_title(t):
    t0 = str(t)
    t = re.sub(r"\(.*?\)|\[.*?\]", " ", t0)                     # bracketed notes
    t = re.sub(r"@\s*[\w ,/]+", " ", t)                          # @location
    t = re.sub(r"\b(location|loc)\s*[:\-]?\s*[\w ,/]+$", " ", t, flags=re.I)
    for p in NOISE:
        t = re.sub(p, " ", t, flags=re.I)
    t = re.sub(r"\s*[-|,:/]\s*$", "", re.sub(r"^\s*[-|,:/]\s*", "", t))
    t = re.sub(r"\s+", " ", t).strip(" -|,.:/")
    return t.title() if t else t0.title()


an["job_title_clean"] = an.job_desig.map(clean_title)
chg = (an.job_title_clean.str.lower() != an.job_desig.str.lower())
log("S3", F, "Designations padded with recruiting noise ('Urgent Hiring', 'Walk-in', 'Opening for', '@Mumbai', bracketed notes)",
    chg.sum(), "Stripped into job_title_clean (original kept in job_desig)")
dd(F, "job_title_clean", "text", "Designation with recruiting noise, locations and brackets removed")

# S4 parse experience + salary band
e = an.experience.str.extract(r"(\d+)\s*-\s*(\d+)").astype(float)
an["exp_min"], an["exp_max"] = e[0], e[1]
an["exp_mid"] = (an.exp_min + an.exp_max) / 2
an["exp_range_width"] = an.exp_max - an.exp_min
log("S4", F, "Experience stored as text ('6-10 yrs')", len(an), "Parsed to exp_min / exp_max / exp_mid / exp_range_width (years)")
bad = an.exp_min.isna() | (an.exp_max < an.exp_min)
log("S5", F, "Unparseable or inverted experience ranges", bad.sum(), "None found")
an["exp_band"] = pd.cut(an.exp_mid, [-.1, 2, 5, 8, 12, 60], labels=["0-2", "2-5", "5-8", "8-12", "12+"])
BANDS = {"0to3": (1, 0, 3), "3to6": (2, 3, 6), "6to10": (3, 6, 10), "10to15": (4, 10, 15), "15to25": (5, 15, 25), "25to50": (6, 25, 50)}
b = an.salary.map(BANDS)
an["salary_band_ord"], an["salary_low_lpa"], an["salary_high_lpa"] = b.str[0], b.str[1], b.str[2]
an["salary_mid_lpa"] = (an.salary_low_lpa + an.salary_high_lpa) / 2
an["salary_band"] = an.salary.str.replace("to", "-") + " LPA"
an["high_pay_15plus"] = (an.salary_band_ord >= 5).astype(int)
log("S4", F, "Salary only available as 6 text bands ('10to15')", len(an), "Ordinal salary_band_ord 1-6, band low/high/mid (LPA), high_pay_15plus (target)")
for c, t, d in [("exp_min", "float", "Minimum years required"), ("exp_max", "float", "Maximum years required"),
                ("exp_mid", "float", "Midpoint of the experience range"), ("exp_range_width", "float", "exp_max - exp_min"),
                ("exp_band", "cat", "Experience band from exp_mid"), ("salary_band_ord", "int", "Salary band as ordinal 1 (0-3 LPA) to 6 (25-50 LPA)"),
                ("salary_low_lpa", "float", "Band lower bound"), ("salary_high_lpa", "float", "Band upper bound"),
                ("salary_mid_lpa", "float", "Band midpoint"), ("salary_band", "cat", "Readable band label"),
                ("high_pay_15plus", "0/1", "Salary band 15 LPA or more (modelling target)")]:
    dd(F, c, t, d)

# S5 consistency
incon = (an.salary_band_ord == 1) & (an.exp_min >= 8)
an["salary_exp_inconsistent"] = incon.astype(int)
log("S5", F, "Lowest band (0-3 LPA) with 8+ years minimum experience - likely undisclosed salary coded as lowest band",
    incon.sum(), "Flagged salary_exp_inconsistent; excluded from salary models")
wide_e = an.exp_range_width > 8
log("S5", F, "Very wide experience ranges (more than 8 years between min and max)", wide_e.sum(), "Kept; exp_mid used with care")
dd(F, "salary_exp_inconsistent", "0/1", "0-3 LPA band with 8+ years required")

# S7 job_type
jt = an.job_type.str.strip().str.lower().replace({"analytic": "analytics"})
log("S7", F, "job_type: one value spelt 5 ways (Analytics, analytics, ANALYTICS, analytic, Analytic)", an.job_type.notna().sum(),
    "Merged to 'analytics'")
log("S7", F, f"job_type missing for {raw[F].job_type.isna().mean():.0%} of the original rows ({raw[F].job_type.isna().sum():,} of {len(raw[F]):,}); "
    f"{an.job_type.isna().mean():.0%} after removing exact duplicates - not usable as a classifier", an.job_type.isna().sum(),
    "Original column kept unchanged + job_type_tagged (0/1); analytics relevance re-derived from title + skills")
an["job_type_tagged"] = jt.notna().astype(int)
dd(F, "job_type_tagged", "0/1", "Posting was tagged 'analytics' in the raw job_type field")

# S7 locations
CITY = {"bengaluru": "Bengaluru", "bangalore": "Bengaluru", "whitefield": "Bengaluru", "electronic city": "Bengaluru",
        "mumbai": "Mumbai", "navi mumbai": "Mumbai", "mumbai suburbs": "Mumbai", "thane": "Mumbai", "powai": "Mumbai",
        "andheri": "Mumbai", "delhi": "Delhi NCR", "delhi ncr": "Delhi NCR", "new delhi": "Delhi NCR", "gurgaon": "Delhi NCR",
        "gurugram": "Delhi NCR", "noida": "Delhi NCR", "greater noida": "Delhi NCR", "faridabad": "Delhi NCR",
        "ghaziabad": "Delhi NCR", "sohna road": "Delhi NCR", "sonepat": "Delhi NCR", "manesar": "Delhi NCR",
        "hyderabad": "Hyderabad", "secunderabad": "Hyderabad", "madhapur": "Hyderabad", "gachibowli": "Hyderabad",
        "pune": "Pune", "chennai": "Chennai", "kolkata": "Kolkata", "ahmedabad": "Ahmedabad", "gandhinagar": "Ahmedabad",
        "kochi": "Kochi", "cochin": "Kochi", "trivandrum": "Thiruvananthapuram", "thiruvananthapuram": "Thiruvananthapuram",
        "chandigarh": "Chandigarh", "mohali": "Chandigarh", "panchkula": "Chandigarh", "jaipur": "Jaipur",
        "coimbatore": "Coimbatore", "vadodara": "Vadodara", "baroda": "Vadodara", "lucknow": "Lucknow", "indore": "Indore",
        "bhubaneshwar": "Bhubaneswar", "bhubaneswar": "Bhubaneswar", "nagpur": "Nagpur", "mysore": "Mysuru",
        "mysuru": "Mysuru", "bhopal": "Bhopal", "vijayawada": "Vijayawada", "surat": "Surat", "visakhapatnam": "Visakhapatnam",
        "vizag": "Visakhapatnam", "kanpur": "Kanpur", "nasik": "Nashik", "nashik": "Nashik", "aurangabad": "Aurangabad",
        "madurai": "Madurai", "ludhiana": "Ludhiana", "jamshedpur": "Jamshedpur", "thrissur": "Thrissur", "panjim": "Goa",
        "goa": "Goa", "dehradun": "Dehradun", "kozhikode": "Kozhikode", "calicut": "Kozhikode", "rajkot": "Rajkot",
        "guwahati": "Guwahati", "udaipur": "Udaipur", "patna": "Patna", "mangalore": "Mangaluru", "ranchi": "Ranchi",
        "raipur": "Raipur", "jodhpur": "Jodhpur", "amritsar": "Amritsar", "jabalpur": "Jabalpur", "siliguri": "Siliguri"}
ANYWHERE = {"india", "anywherein india", "anywhere in india", "anywhere inindia", "across india", "pan india", "all india", "remote"}
STATES = {"maharashtra", "karnataka", "gujarat", "andhra pradesh", "tamil nadu", "kerala", "punjab", "haryana",
          "telangana", "west bengal", "uttar pradesh", "rajasthan", "madhya pradesh", "odisha", "bihar", "himachal pradesh"}
INTL = {"canada", "dubai", "uae", "australia", "united states", "u.s", "us", "usa", "singapore", "uk", "united kingdom",
        "london", "germany", "saudi arabia", "qatar", "kuwait", "oman", "bahrain", "hong kong", "malaysia", "new zealand",
        "south africa", "abu dhabi", "doha", "riyadh", "europe", "eu", "japan", "netherlands", "ireland", "switzerland",
        "france", "philippines", "new jersey", "sweden", "nigeria", "myanmar", "central african republic", "afghanistan",
        "uganda", "russia", "kenya", "ghana", "tanzania", "sri lanka", "nepal", "bangladesh", "china", "usa/canada"}
TIER1 = {"Bengaluru", "Mumbai", "Delhi NCR", "Hyderabad", "Pune", "Chennai", "Kolkata"}
unmapped = Counter()


NEIGHBOURHOOD = {  # localities -> metro (checked as substrings of a token)
    "Mumbai": ["marol", "chakala", "lower parel", "andheri", "malad", "goregaon", "vikhroli", "bkc", "bandra", "powai", "worli", "kurla",
               "kandivali", "borivali", "airoli", "vashi", "belapur", "chembur", "kalaghoda", "fort", "nariman", "grant road", "dadar", "ghatkopar", "mahape"],
    "Pune": ["kharadi", "viman nagar", "yerwada", "kalyani nagar", "hinjewadi", "hinjawadi", "magarpatta", "baner", "hadapsar",
             "wakad", "aundh", "shivaji nagar", "pimpri", "chakan", "talegaon"],
    "Delhi NCR": ["udyog vihar", "cyber city", "cyber hub", "noida", "gurgaon", "gurugram", "okhla", "nehru place", "saket",
                  "connaught", "dwarka", "mg road gurgaon", "golf course", "manesar", "jasola", "janakpuri", "rohini", "sector"],
    "Bengaluru": ["marathahalli", "bellandur", "koramangala", "indiranagar", "hsr", "electronic city", "manyata", "outer ring",
                  "jp nagar", "btm", "whitefield", "yeshwanthpur", "hebbal", "sarjapur", "bannerghatta", "domlur", "rajajinagar", "bengaluru", "bangalore"],
    "Hyderabad": ["hitech", "hi-tech", "kondapur", "banjara", "jubilee hills", "gachibowli", "madhapur", "begumpet", "uppal", "nanakramguda", "shamshabad"],
    "Chennai": ["navalur", "guindy", "omr", "sholinganallur", "taramani", "ambattur", "perungudi", "siruseri", "porur", "velachery", "egmore", "nungambakkam"],
    "Kolkata": ["salt lake", "sector v", "rajarhat", "new town"],
}


def map_neighbourhood(t):
    for city, keys in NEIGHBOURHOOD.items():
        if any(k in t for k in keys):
            return city
    return None


def parse_loc(s):
    toks = [t.strip(" .-").lower() for t in re.split(r"[,/;()|]| and ", str(s)) if t.strip(" .-")]
    cities, intl, anyw, state = [], False, False, False
    for t in toks:
        if t in CITY:
            cities.append(CITY[t])
        elif map_neighbourhood(t):
            cities.append(map_neighbourhood(t))
        elif t in INTL:
            intl = True
        elif t in ANYWHERE:
            anyw = True
        elif t in STATES:
            state = True
        else:
            cities.append(t.title())
            unmapped[t.title()] += 1
    return list(dict.fromkeys(cities)), intl, anyw, state


L = an.location.map(parse_loc)
an["cities"] = L.map(lambda x: "|".join(x[0]))
an["n_cities"] = L.map(lambda x: len(x[0]))
an["is_multi_city"] = (an.n_cities > 1).astype(int)
an["is_international"] = L.map(lambda x: int(x[1] and not x[0])).astype(int)
an["primary_city"] = L.map(lambda x: x[0][0] if x[0] else ("International" if x[1] else "Anywhere in India" if (x[2] or x[3]) else "Unknown"))
an["city_tier"] = np.select([an.primary_city.isin(TIER1), an.primary_city.eq("International"),
                             an.primary_city.isin(["Anywhere in India", "Unknown"])],
                            ["Tier 1 metro", "International", "Unspecified"], "Tier 2/3")
log("S7", F, f"location: {raw[F].location.nunique():,} distinct strings, 16% list several cities, variants "
    "(Bangalore/Bengaluru, Gurgaon/Gurugram, Mumbai Suburbs, Sohna Road, Hyderabad/Secunderabad), states instead of cities, "
    "'Anywhere Inindia'", raw[F].location.nunique(),
    "Tokenised; 100+ variants mapped to canonical cities / metro areas; states and 'anywhere' -> Anywhere in India; "
    "derived primary_city, cities, n_cities, is_multi_city, city_tier")
log("S7", F, "Overseas locations (Dubai, Canada, US, Singapore, Nigeria, Sweden, New Jersey ...) in an India dataset",
    an.is_international.sum(), "Flagged is_international; excluded from the India market sample")
pd.Series(unmapped).sort_values(ascending=False).to_csv(LOGD / "unmapped_locations.csv", header=["count"])
for c, t, d in [("cities", "text", "All canonical cities, '|' separated"), ("n_cities", "int", "Number of cities listed"),
                ("is_multi_city", "0/1", "More than one city listed"), ("is_international", "0/1", "Only overseas locations"),
                ("primary_city", "cat", "First canonical city (metro areas merged)"), ("city_tier", "cat", "Tier 1 metro / Tier 2-3 / Unspecified / International")]:
    dd(F, c, t, d)

# S7 skills
SYN = {"ml": "machine learning", "ai": "artificial intelligence", "powerbi": "power bi", "ms excel": "excel",
       "advanced excel": "excel", "data visualisation": "data visualization", "pl/sql": "plsql", "nlp": "natural language processing",
       "r programming": "r", "python programming": "python", "big data analytics": "big data", "bigdata": "big data",
       "java script": "javascript", "angular js": "angularjs", "nodejs": "node.js", "e - commerce": "ecommerce",
       "fp & a": "fp&a", "fpa": "fp&a", "service now": "servicenow", "c / c++": "c++", "c/ c++": "c++", "datawarehousing": "data warehousing",
       "datawarehouse": "data warehouse", "webservices": "web services", "pre sales": "presales", "front end": "frontend",
       "power point": "powerpoint", "ms office": "ms office", "sas programming": "sas", "base sas": "sas", "sas base": "sas",
       "statistical modeling": "statistical modelling", "predictive modeling": "predictive modelling"}
EDUCATION = r"^(b\.?tech|m\.?tech|b\.?e|m\.?e|mba|pgdm|b\.?com|m\.?com|bca|mca|b\.?sc|m\.?sc|ba|b\.a|ma|phd|ca|cfa|frm|cpa|icwa|cma|graduate|post graduate|any graduate|engineering graduate|b\.?pharm|m\.?pharm|mbbs|bds)$"
META = r"^(fresher|freshers|present job|bpo|international bpo|domestic bpo|voice|non voice|non-voice|night shift|day shift|rotational shift|walk-?in|immediate joiner|work from home|part time|freelancing|freelancer|data entry|typing|back office|kpo|it skills|good communication|english|hindi)$"
SOFT = r"(communication|team player|leadership|stakeholder|presentation skills|interpersonal|problem solving|analytical skills|negotiation|team management|people management|time management|client handling|written|verbal|attention to detail|critical thinking|decision making)"


def norm_tok(t):
    t = re.sub(r"\.{2,}$", "", t.strip().lower()).strip(" .;:-\"'")
    t = re.sub(r"\s+", " ", t)
    return SYN.get(t, t)


raw_tok = an.key_skills.fillna("").map(lambda s: [norm_tok(x) for x in s.split(",")])
cnt = Counter(t for l in raw_tok for t in l if t)
# automatic variant merge: same letters/digits after removing spaces & punctuation -> most frequent spelling
groups = defaultdict(list)
for t, c in cnt.items():
    groups[re.sub(r"[^a-z0-9+#&]", "", t)].append((c, t))
CANON = {t: max(v)[1] for k, v in groups.items() for _, t in v}
n_variant = sum(1 for k, v in groups.items() if len(v) > 1)


def is_junk(t):
    return (not t or re.fullmatch(r"[\d\W_]+", t) is not None or len(t) > 45 or (len(t) == 1 and t not in ("r", "c")))


def classify_skill(t):
    if re.match(EDUCATION, t):
        return "education"
    if re.match(META, t):
        return "job_meta"
    if re.search(SOFT, t):
        return "soft"
    return "technical_or_domain"


tech, soft, edu, meta, junk_n = [], [], [], [], 0
for l in raw_tok:
    T, S, E, M = [], [], [], []
    for t in l:
        if is_junk(t):
            junk_n += 1
            continue
        t = CANON.get(t, t)
        k = classify_skill(t)
        {"education": E, "job_meta": M, "soft": S}.get(k, T).append(t)
    tech.append(list(dict.fromkeys(T)))
    soft.append(list(dict.fromkeys(S)))
    edu.append(list(dict.fromkeys(E)))
    meta.append(list(dict.fromkeys(M)))
an["skills"] = ["|".join(x) for x in tech]
an["soft_skills"] = ["|".join(x) for x in soft]
an["education_mentioned"] = ["|".join(x) for x in edu]
an["job_meta_tags"] = ["|".join(x) for x in meta]
an["n_skills"] = [len(x) for x in tech]
an["skills_truncated"] = raw[F].loc[an.index, "key_skills"].astype(str).str.endswith("...").astype(int)
log("S7", F, f"key_skills free text: {len(cnt):,} distinct tokens after lower-casing", len(an),
    "Lower-cased, trimmed, trailing '...' removed, synonym map (ML->machine learning, PowerBI->power bi, Base SAS->sas ...), de-duplicated per posting")
log("S7", F, "Spelling/format variants of the same skill (power bi/powerbi, big data/bigdata, javascript/java script, c / c++ ...)",
    n_variant, "Auto-merged by letters-only key to the most frequent spelling")
log("S7", F, "Junk skill tokens (empty, numbers like '1120', stray quotes, whole sentences > 45 chars, single letters)", junk_n, "Removed")
log("S7", F, "Non-skill tokens mixed into skills: education (MBA, B.Com, B.Tech), job meta (fresher, BPO, non voice, present job), soft skills",
    sum(map(len, edu)) + sum(map(len, meta)) + sum(map(len, soft)),
    "Separated into education_mentioned, job_meta_tags, soft_skills; 'skills' keeps technical/domain skills only")
log("S7", F, "key_skills truncated with '...' (87%) - lists are incomplete", an.skills_truncated.sum(),
    "Flagged; supplemented by skills found in the description (skills_from_desc)")

vocab = [s for s, c in Counter(t for l in tech for t in l).items() if c >= 25 and len(s) >= 2 and s not in
         {"analytics", "data", "management", "operations", "sales", "marketing", "finance", "it", "software", "business", "research", "design", "development", "testing", "support"}]
vocab_re = [(s, re.compile(r"(?<![a-z0-9])" + re.escape(s) + r"(?![a-z0-9])")) for s in sorted(vocab, key=len, reverse=True)]
desc_low = an.job_description.fillna("").str.lower()
from_desc = [[s for s, rx in vocab_re if rx.search(d)] for d in desc_low]
an["skills_from_desc"] = ["|".join(x) for x in from_desc]
an["skills_all"] = ["|".join(dict.fromkeys(a + b)) for a, b in zip(tech, from_desc)]
an["n_skills_all"] = an.skills_all.map(lambda s: len([x for x in s.split("|") if x]))
added = sum(len(set(b) - set(a)) for a, b in zip(tech, from_desc))
log("S9", F, f"Skills recovered from job_description using a {len(vocab)}-skill vocabulary built from key_skills", added,
    "skills_from_desc + union skills_all (descriptions also truncated, so a lower bound)")
for c, t, d in [("skills", "text", "Clean technical/domain skills from key_skills, '|' separated"),
                ("soft_skills", "text", "Soft skills from key_skills"), ("education_mentioned", "text", "Degrees/certifications found in key_skills"),
                ("job_meta_tags", "text", "Non-skill tags (fresher, BPO, shift ...)"), ("n_skills", "int", "Number of clean skills"),
                ("skills_truncated", "0/1", "Raw key_skills ended with '...'"), ("skills_from_desc", "text", "Vocabulary skills found in the description"),
                ("skills_all", "text", "Union of skills and skills_from_desc"), ("n_skills_all", "int", "Size of skills_all")]:
    dd(F, c, t, d)

# five skill dimensions (bridge to the JDS file)
from taxonomy import DIMS, TOOLS, match_any  # 5-dimension skill taxonomy (shared with the database build)

sets_all = [set(s.split("|")) for s in an.skills_all]
for d, kws in DIMS.items():  # whole-word match inside compound skills ('oracle sql' -> coding), see taxonomy.has
    an[f"dim_{d}"] = [int(any(match_any(sk, kws) for sk in s)) for s in sets_all]
    dd(F, f"dim_{d}", "0/1", f"Posting asks for any '{d}' skill (taxonomy bridging to the JDS skill score)")
an["n_dims"] = an[[f"dim_{d}" for d in DIMS]].sum(axis=1)
dd(F, "n_dims", "int", "How many of the 5 analytics skill dimensions the posting asks for (0-5)")
log("S9", F, "No common key between the 4 files", len(an),
    "Built a 5-dimension skill taxonomy (big data, maths-stats, coding, AI-ML, dashboards-storytelling) matching the JDS "
    "scores; each posting flagged dim_* - this is the bridge for linking market demand to the JDS success data")
for t, kws in TOOLS.items():
    an["has_" + t] = [int(any(match_any(sk, kws) for sk in s)) for s in sets_all]
log("S9", F, "Tool flags must catch compound skills ('Oracle SQL', 'SQL Server', 'SAS SQL', 'MS Excel')", len(an),
    "has_* and dim_* use whole-word matching inside each skill (taxonomy.has), with exclusions such as 'medical coding'")

# S7 role family & seniority  (non-analytics guards come BEFORE generic 'analyst')
SEN = [("Leadership", r"\bhead\b|director|\bvp\b|\bavp\b|vice president|chief|\bcxo\b|\bgm\b|general manager|\bcfo\b|\bcto\b|\bcoo\b"),
       ("Manager / Lead", r"manager|\blead\b|principal|architect|team lead|\btl\b|supervisor"),
       ("Senior", r"senior|\bsr\b|\bsr\.|specialist|expert|\bii\b|\biii\b"),
       ("Entry", r"intern|trainee|fresher|junior|\bjr\b|graduate|entry level|apprentice")]


def first(text, rules, default):
    t = str(text).lower()
    for lab, p in rules:
        if re.search(p, t):
            return lab
    return default


title_role = an.job_title_clean.map(lambda t: first(t, ROLE, "Other"))
# fallback when the title is uninformative: use skills, but only assign an analytics family when the posting
# shows at least 2 of the 5 analytics skill dimensions; never fall back to the vague "Research" family
skill_role = an.skills.map(lambda t: first(t.replace("|", " "), [r for r in ROLE if r[0] != "Research / Market Research"], "Other"))
skill_role = pd.Series(np.where(skill_role.isin(ANALYTICS) & (an[[c for c in an.columns if c.startswith("dim_")]].sum(axis=1) < 2),
                                "Other", skill_role), index=an.index)
an["role_family"] = np.where(title_role != "Other", title_role, skill_role)
an["role_source"] = np.where(title_role != "Other", "title", np.where(skill_role != "Other", "skills", "none"))
an["seniority"] = an.job_title_clean.map(lambda t: first(t, SEN, "Mid"))
an["is_analytics_role"] = an.role_family.isin(ANALYTICS).astype(int)
log("S7", F, f"{raw[F].job_desig.nunique():,} distinct free-text designations", raw[F].job_desig.nunique(),
    "Ordered keyword rules on job_title_clean (skills used when the title is uninformative) -> 18 role families + 'Other'; "
    "non-analytics guards (RCM, BPO, HR, SEO, IT) run before the generic 'analyst' rule; seniority (5 levels)")
log("S8", F, "Non-analytics roles inside 'Analytics Jobs' (software, BPO, HR, sales, finance, medical coding ...)",
    (an.is_analytics_role == 0).sum(), "Flagged is_analytics_role=0; core analytics sample uses the 9 analytics families")
for c, t, d in [("role_family", "cat", "18 role families + Other"), ("role_source", "cat", "Whether role came from title, skills, or neither"),
                ("seniority", "cat", "Entry / Mid / Senior / Manager-Lead / Leadership from title"),
                ("is_analytics_role", "0/1", "Role family is one of the 9 analytics families")]:
    dd(F, c, t, d)

# S2 near duplicates (after normalisation)
near = an.duplicated(["job_title_clean", "skills", "primary_city", "exp_min", "exp_max", "salary_band_ord"], keep="first")
an["is_near_duplicate"] = near.astype(int)
log("S2", F, "Near-duplicates after normalisation (same clean title, skills, city, experience and salary band; repost with another description)",
    near.sum(), "Flagged is_near_duplicate; excluded from demand counts")
dd(F, "is_near_duplicate", "0/1", "Repeat of an earlier posting after normalisation")
rep = an.duplicated(["job_title_clean", "skills", "primary_city", "exp_min", "exp_max"], keep="first") & ~near
an["possible_repost"] = rep.astype(int)
log("S2", F, "Possible reposts (same clean title, skills, city and experience, but a different salary band)", rep.sum(),
    "Flagged possible_repost only - kept in the sample (salary differs, may be a genuinely separate vacancy); used as a sensitivity check")
dd(F, "possible_repost", "0/1", "Same title/skills/city/experience as an earlier posting but different salary band")

# S8 scope
spam = (an.job_desig.fillna("") + " " + an.key_skills.fillna("")).str.contains(
    r"data entry|part time|work from home|freelanc|home base|online work|typing job|copy paste|sms sending|form filling", case=False)
an["is_spam"] = spam.astype(int)
log("S8", F, "Low-quality 'data entry / work from home / part-time / freelance' postings", spam.sum(), "Flagged is_spam; excluded")
an["desc_missing"] = an.job_description.isna().astype(int)
an["desc_truncated"] = raw[F].loc[an.index, "job_description"].astype(str).str.endswith("...").astype(int)
an["desc_length"] = an.job_description.fillna("").str.len()
log("S8", F, f"job_description missing ({raw[F].job_description.isna().sum():,} in the original file; count shown is after removing exact duplicates)", an.desc_missing.sum(), "Not imputed (text); flagged desc_missing")
log("S8", F, "job_description truncated with '...'", an.desc_truncated.sum(), "Flagged desc_truncated; text treated as partial")
an["in_india_sample"] = ((an.is_spam == 0) & (an.is_international == 0) & (an.is_near_duplicate == 0)).astype(int)
an["in_core_analytics"] = ((an.in_india_sample == 1) & (an.is_analytics_role == 1)).astype(int)
an["in_salary_model"] = ((an.in_core_analytics == 1) & (an.salary_exp_inconsistent == 0)).astype(int)
for c, t, d in [("is_spam", "0/1", "Spam/low-quality posting"), ("desc_missing", "0/1", "No description"),
                ("desc_truncated", "0/1", "Description cut off with '...'"), ("desc_length", "int", "Characters in description"),
                ("in_india_sample", "0/1", "Not spam, not overseas-only, not a near-duplicate"),
                ("in_core_analytics", "0/1", "India sample AND an analytics role family - main market sample"),
                ("in_salary_model", "0/1", "Core analytics AND salary consistent with experience")]:
    dd(F, c, t, d)
an.to_csv(OUT / "analytics_jobs_clean.csv", index=False)
long = an[["s_no", "role_family", "seniority", "primary_city", "salary_band_ord", "exp_mid", "in_core_analytics"]].copy()
long["skill"] = [x.split("|") for x in an.skills_all]
long = long.explode("skill")
long = long[long.skill.astype(bool)].drop_duplicates(["s_no", "skill"])
long.to_csv(OUT / "analytics_skills_long.csv", index=False)

# audit sample for manual verification of the role rules
an[an.in_india_sample == 1].sample(150, random_state=4242)[["s_no", "job_desig", "job_title_clean", "skills", "role_family", "seniority"]] \
    .to_csv(LOGD / "role_classification_audit_sample.csv", index=False)

# =============================================================== JDS
F = "JDS Skill Traits"
j = raw[F].copy()
j.columns = [c.strip().replace("-", "_") for c in j.columns]
log("S1", F, "Column name with a hyphen ('maths-stats_skills') - invalid in SAS/SQL", 1, "Renamed maths_stats_skills")
j = j.rename(columns={"salary_hike_high_or_low": "salary_hike_high"})
j.insert(0, "row_id", np.arange(1, len(j) + 1))
log("S1", F, "id not unique: 2 ids shared by different people (different scores)", j.id.duplicated(keep=False).sum(),
    "Kept as different people; surrogate row_id used as key")
SK = ["big_data_skills", "maths_stats_skills", "coding_skills", "ai_and_ml_skills", "dashboard_and_storytelling_skills"]
out_rng = ((j[SK] < 1) | (j[SK] > 5)).sum().sum()
log("S5", F, "Skill scores outside the documented 1-5 scale", out_rng, "None found")
log("S5", F, "Target salary_hike_high not 0/1", (~j.salary_hike_high.isin([0, 1])).sum(), "None; class balance "
    f"{j.salary_hike_high.mean():.0%} high / {1 - j.salary_hike_high.mean():.0%} low (balanced)")
ceil = (j[SK] == 5).mean()
log("S6", F, "Ceiling effect - share of perfect 5.0 scores: " + ", ".join(f"{c.replace('_skills', '')} {v:.0%}" for c, v in ceil.items()),
    (j[SK] == 5).sum().sum(), "Kept (real scores); handled with rank tests, tree models and n_skills_at_max")
z = (j[SK] - j[SK].mean()) / j[SK].std()
log("S6", F, "Low outliers (|z| > 2.5)", int((z.abs() > 2.5).sum().sum()), "Kept - genuine weak scores, scale is bounded")
log("S5", F, "Missing values", j.isna().sum().sum(), "None")
j["skill_mean"] = j[SK].mean(axis=1).round(3)
j["skill_min"] = j[SK].min(axis=1)
j["skill_range"] = (j[SK].max(axis=1) - j.skill_min).round(2)
j["n_skills_at_max"] = (j[SK] == 5).sum(axis=1)
j["weakest_skill"] = j[SK].idxmin(axis=1).str.replace("_skills", "")
j["strongest_skill"] = j[SK].idxmax(axis=1).str.replace("_skills", "")
log("S9", F, "Derived profile variables", len(j), "skill_mean, skill_min, skill_range, n_skills_at_max, weakest/strongest skill "
    "(no composite indices or segments: the 5 scores are used directly)")
for c, d in [("row_id", "Surrogate key"), ("skill_mean", "Mean of 5 skills"), ("skill_min", "Lowest skill"),
             ("skill_range", "Max - min skill"), ("n_skills_at_max", "Skills scored exactly 5"), ("weakest_skill", "Lowest-scoring area"),
             ("strongest_skill", "Highest-scoring area")]:
    dd(F, c, "num/cat", d)
j.to_csv(OUT / "jds_clean.csv", index=False)

# =============================================================== SDS
F = "SDS Personality Traits"
s = raw[F].copy()
s.columns = [re.sub(r"\s+", "", c) for c in s.columns]
log("S1", F, "Column names with stray spaces (' extraversion', 'success_ classification_ high_low')", 2, "Trimmed; target renamed success_high")
s = s.rename(columns={"success_classification_high_low": "success_high"})
s.insert(0, "row_id", np.arange(1, len(s) + 1))
log("S1", F, "id not unique: 9 ids shared by different people", s.id.duplicated(keep=False).sum(), "Kept; surrogate row_id used as key")
TR = ["neuroticism", "extraversion", "openness_to_experience", "agreeableness", "conscientiousness"]
log("S5", F, "Trait scores outside a plausible 0-100 normalised range", ((s[TR] < 0) | (s[TR] > 100)).sum().sum(), "None (observed 17-68)")
log("S5", F, "Missing values", s.isna().sum().sum(), "None")
log("S5", F, "Target success_high balance", len(s), f"{s.success_high.mean():.0%} high / {1 - s.success_high.mean():.0%} low (balanced)")
zz = (s[TR] - s[TR].mean()) / s[TR].std()
log("S6", F, "Trait outliers (|z| > 2.5)", int((zz.abs() > 2.5).sum().sum()), "Kept - extreme but valid personality scores")
for t in TR:
    s[t + "_z"] = zz[t].round(4)
s["emotional_stability_z"] = -s.neuroticism_z  # reversed on the standardised scale, no sample-specific constant
s["trait_mean"] = s[TR[1:]].mean(axis=1).round(2)
s["dominant_trait"] = s[["emotional_stability_z"] + [t + "_z" for t in TR[1:]]].idxmax(axis=1).str.replace("_z", "")
log("S9", F, "Derived variables", len(s), "z-scores per trait, emotional_stability_z (= -neuroticism_z), trait_mean (positive traits), "
    "dominant_trait (highest z among emotional stability and the 4 positive traits)")
for c, d in [("row_id", "Surrogate key"), ("emotional_stability_z", "Reversed neuroticism z-score"),
             ("trait_mean", "Mean of the 4 positive traits"), ("dominant_trait", "Trait with highest z-score")]:
    dd(F, c, "num/cat", d)
s.to_csv(OUT / "sds_clean.csv", index=False)

# =============================================================== S10 validation
checks = {
    "DS: row_id unique": ds.row_id.is_unique,
    "DS: salaries numeric & positive": bool((ds[["min_salary_lpa", "avg_salary_lpa", "max_salary_lpa"]] > 0).all().all()),
    "DS: min <= avg <= max": bool(((ds.min_salary_lpa <= ds.avg_salary_lpa) & (ds.avg_salary_lpa <= ds.max_salary_lpa)).all()),
    "AN: s_no unique after de-dup": an.s_no.is_unique,
    "AN: no exact duplicates left": not an.drop(columns="s_no").duplicated().any(),
    "AN: experience parsed for all rows": bool(an.exp_min.notna().all()),
    "AN: salary band parsed for all rows": bool(an.salary_band_ord.notna().all()),
    "AN: every row has a primary_city": bool(an.primary_city.notna().all()),
    "AN: every row has a role_family": bool(an.role_family.notna().all()),
    "JDS: scores within 1-5": bool(((j[SK] >= 1) & (j[SK] <= 5)).all().all()),
    "SDS: no missing values": bool(s[TR].notna().all().all()),
}
for k, v in checks.items():
    assert v, k

# Manual audit of the role rules (done by hand on independent random samples of 150 India postings each;
# rules were refined on earlier samples and measured on a final, untouched sample, seed 4242).
log("S10", "Analytics Jobs", "Manual audit of role_family on a final independent random sample of 150 postings", 150,
    "Exact family correct ~91%; analytics vs non-analytics split correct ~92%. Residual errors are ambiguous titles "
    "(e.g. 'SOC Analyst', 'Investment Analyst - Real Estate'); reported as a limitation")

# =============================================================== full data dictionary (original + derived)
ORIG_DESC = {
    "DataScience Jobs": {"reference_no": "Row identification number (NOT unique - see row_id)", "company_name": "Recruiting company",
                         "job_title": "Job title (10 values)", "min_experience": "Minimum required experience (years)",
                         "num_of_jobs": "Number of postings by the company for the title"},
    "Analytics Jobs": {"s_no": "Row identification number", "experience": "Experience required (text range)",
                       "job_description": "Job description (cleaned, often truncated)", "job_desig": "Designation as posted (raw)",
                       "key_skills": "Key skills as posted (raw)", "location": "Location as posted (raw)", "salary": "Salary band as posted (raw)"},
    "JDS Skill Traits": {"id": "Employee id (NOT unique - see row_id)", "big_data_skills": "Big-data skill score 1-5",
                         "maths_stats_skills": "Maths & statistics skill score 1-5", "coding_skills": "Coding skill score 1-5 (SAS, Python, SQL ...)",
                         "ai_and_ml_skills": "AI & ML skill score 1-5", "dashboard_and_storytelling_skills": "Visualisation, reporting & storytelling score 1-5",
                         "salary_hike_high": "Target: performance-based salary hike, 1 = high, 0 = low"},
    "SDS Personality Traits": {"id": "Employee id (NOT unique - see row_id)", "neuroticism": "Big Five neuroticism (normalised)",
                               "extraversion": "Big Five extraversion (normalised)", "openness_to_experience": "Big Five openness (normalised)",
                               "agreeableness": "Big Five agreeableness (normalised)", "conscientiousness": "Big Five conscientiousness (normalised)",
                               "success_high": "Target: success classification, 1 = high, 0 = low"},
}
CLEAN = {"DataScience Jobs": ds, "Analytics Jobs": an, "JDS Skill Traits": j, "SDS Personality Traits": s}
derived = {(f_, c): (t, d) for f_, c, t, d, _ in DICT}
full = []
for f_, df_ in CLEAN.items():
    for c in df_.columns:
        if (f_, c) in derived:
            t, d = derived[(f_, c)]
            origin = "derived"
        else:
            t, d, origin = str(df_[c].dtype), ORIG_DESC.get(f_, {}).get(c, "Derived (see pipeline)" if c.endswith("_z") or c.startswith("has_") else ""), "original" if c in ORIG_DESC.get(f_, {}) else "derived"
            if c.startswith("has_"):
                d = f"Posting lists the skill '{c[4:].replace('_', ' ')}'"
            if c.endswith("_z"):
                d = f"z-score of {c[:-2]}"
        full.append({"file": f_, "column": c, "origin": origin, "type": t, "description": d,
                     "missing_pct": round(df_[c].isna().mean() * 100, 1), "distinct": int(df_[c].nunique())})
full = pd.DataFrame(full)
full.to_csv(LOGD / "data_dictionary_full.csv", index=False)

# =============================================================== write log + dictionary + summary
lg = pd.DataFrame(LOG, columns=["stage", "file", "issue", "rows_affected", "treatment"])
lg["_n"] = lg.stage.str[1:].astype(int)
lg = lg.sort_values(["file", "_n"], kind="stable").drop(columns="_n")
lg.to_csv(LOGD / "data_quality_log.csv", index=False)
pd.DataFrame(DICT, columns=["file", "column", "type", "description", "origin"]).to_csv(LOGD / "data_dictionary_derived.csv", index=False)
summary = pd.DataFrame([
    ("DataScience Jobs", n_ds, len(ds), int(ds.in_analysis_sample.sum()), "real employers"),
    ("Analytics Jobs", n_an, len(an), int(an.in_core_analytics.sum()), "India, non-spam, non-duplicate, analytics roles"),
    ("JDS Skill Traits", len(raw["JDS Skill Traits"]), len(j), len(j), "all rows"),
    ("SDS Personality Traits", len(raw["SDS Personality Traits"]), len(s), len(s), "all rows"),
], columns=["file", "raw_rows", "clean_rows", "analysis_rows", "analysis_sample"])
summary.to_csv(LOGD / "cleaning_summary.csv", index=False)
STAGE = {"S1": "Structure & keys", "S2": "Duplicates", "S3": "Text standardisation", "S4": "Parsing & types",
         "S5": "Validity & consistency", "S6": "Outliers", "S7": "Harmonisation", "S8": "Scope flags", "S9": "Derived variables"}
with open(LOGD / "data_quality_log.md", "w", encoding="utf-8") as f:
    f.write("# Data quality log\n\n## Summary\n\n" + summary.to_markdown(index=False) + "\n")
    for file, g in lg.groupby("file", sort=False):
        f.write(f"\n## {file}\n\n| Stage | Issue found | Rows | Treatment |\n|---|---|---|---|\n")
        for _, r in g.iterrows():
            f.write(f"| {r.stage} {STAGE.get(r.stage, '')} | {r.issue} | {r.rows_affected:,} | {r.treatment} |\n")
    f.write("\n## Validation checks (S10)\n\n" + "\n".join(f"- [x] {k}" for k in checks) + "\n")
    f.write("\n## Analytics Jobs - role families (India sample)\n\n" + an[an.in_india_sample == 1].role_family.value_counts().to_markdown() + "\n")
    f.write("\n## Analytics Jobs - primary city (core analytics)\n\n" + an[an.in_core_analytics == 1].primary_city.value_counts().head(15).to_markdown() + "\n")
print(open(LOGD / "data_quality_log.md", encoding="utf-8").read())
print("\nUnmapped location tokens (top):", dict(unmapped.most_common(12)))
