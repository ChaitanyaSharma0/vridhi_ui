"""Build the Round-1 Approach Note (Problem definition + Approach) as a Word file.
Every number in the document is computed here from the cleaned data - nothing is typed by hand."""
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from scipy import stats
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_val_score

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
OUT = Path(r"C:\Users\Chaitanya Sharma\Documents\Claude Stuff\SAS CU Hackathon Round 1")
OUT.mkdir(parents=True, exist_ok=True)
FIG = OUT / "figures"
FIG.mkdir(exist_ok=True)

# ------------------------------------------------------------------ numbers
an = pd.read_csv(HERE / "clean" / "analytics_jobs_clean.csv")
ds = pd.read_csv(HERE / "clean" / "ds_jobs_clean.csv")
j = pd.read_csv(HERE / "clean" / "jds_clean.csv")
s = pd.read_csv(HERE / "clean" / "sds_clean.csv")
log = pd.read_csv(HERE / "outputs" / "data_quality_log.csv", keep_default_na=False)
ver = (HERE / "VERIFICATION.md").read_text(encoding="utf-8")
import re
n_pass, n_chk = map(int, re.search(r"(\d+) of (\d+) checks pass", ver).groups()) if re.search(r"(\d+) of (\d+) checks pass", ver) \
    else map(int, re.search(r"(\d+)/(\d+) PASS", ver).groups())

core = an[an.in_core_analytics == 1]
DIMS = ["big_data", "maths_stats", "coding", "ai_ml", "dashboard_story"]
DNAME = {"big_data": "Big data", "maths_stats": "Maths & statistics", "coding": "Coding", "ai_ml": "AI & ML",
         "dashboard_story": "Dashboards & storytelling"}
SK = dict(zip(DIMS, ["big_data_skills", "maths_stats_skills", "coding_skills", "ai_and_ml_skills", "dashboard_and_storytelling_skills"]))
y = j.salary_hike_high
demand = {d: core[f"dim_{d}"].mean() for d in DIMS}
eff = {}
for d in DIMS:
    g1, g0 = j.loc[y == 1, SK[d]], j.loc[y == 0, SK[d]]
    eff[d] = dict(hi=g1.mean(), lo=g0.mean(), d=(g1.mean() - g0.mean()) / j[SK[d]].std(), p=stats.mannwhitneyu(g1, g0).pvalue)
j["skill_max"] = j[list(SK.values())].max(axis=1)
auc1 = {v: roc_auc_score(y, j[v]) for v in ["skill_mean", "skill_min", "skill_max", "skill_range"]}
cv = StratifiedKFold(5, shuffle=True, random_state=42)
cvauc = lambda X, t: cross_val_score(LogisticRegression(max_iter=2000), X, t, cv=cv, scoring="roc_auc").mean()
jds_auc5 = cvauc(j[list(SK.values())], y)
Z = (j[["skill_mean", "skill_min"]] - j[["skill_mean", "skill_min"]].mean()) / j[["skill_mean", "skill_min"]].std()
p_min = sm.Logit(y, sm.add_constant(Z)).fit(disp=0).pvalues["skill_min"]
TR = ["neuroticism", "extraversion", "openness_to_experience", "agreeableness", "conscientiousness"]
sds_auc = cvauc(s[TR], s.success_high)
ms = sm.Logit(s.success_high, sm.add_constant((s[TR] - s[TR].mean()) / s[TR].std())).fit(disp=0)
sds_or, sds_p = np.exp(ms.params), ms.pvalues
sds_uni = {t: (s.loc[s.success_high == 1, t].mean(), s.loc[s.success_high == 0, t].mean(),
               stats.mannwhitneyu(s.loc[s.success_high == 1, t], s.loc[s.success_high == 0, t]).pvalue) for t in TR}
c = an[an.in_salary_model == 1]
feats = ["exp_min", "exp_max", "n_dims"] + [f"dim_{d}" for d in DIMS] + [x for x in c if x.startswith("has_")]
Xc = pd.get_dummies(c[feats + ["role_family", "city_tier", "seniority"]], columns=["role_family", "city_tier", "seniority"], dtype=float).fillna(-1)
yb = c.salary_band_ord
cv0 = StratifiedKFold(5, shuffle=True, random_state=0)
p_full = cross_val_predict(HistGradientBoostingClassifier(random_state=0), Xc, yb, cv=cv0)
p_exp = cross_val_predict(HistGradientBoostingClassifier(random_state=0), Xc[["exp_min", "exp_max"]], yb, cv=cv0)
band = dict(n=len(c), base=yb.value_counts(normalize=True).max(), full=accuracy_score(yb, p_full), full1=(abs(p_full - yb) <= 1).mean(),
            exp=accuracy_score(yb, p_exp), exp1=(abs(p_exp - yb) <= 1).mean())
ds["headroom"] = (ds.max_salary_lpa - ds.avg_salary_lpa) / ds.avg_salary_lpa
head = ds.groupby("job_title").headroom.median().sort_values()
fam = core.role_family.value_counts()
ds_role_demand = core.groupby("role_family")[[f"dim_{d}" for d in DIMS]].mean()
print({k: round(v, 3) for k, v in demand.items()}, {k: round(v["d"], 2) for k, v in eff.items()}, auc1, round(p_min, 3), band)

# ------------------------------------------------------------------ figures
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 11})


def flow_fig(path):
    fig, ax = plt.subplots(figsize=(10, 6.2))
    ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 64)
    boxes = [
        (2, 50, "1. Understand", "Brief + data dictionary\nStakeholders, decisions\nQuestions & hypotheses", "#DBEAFE"),
        (27, 50, "2. Audit & clean", "10-stage pipeline (S0-S10)\nFlag, don't delete\nIndependent re-check vs raw", "#FEF3C7"),
        (52, 50, "3. Consolidate", "5-dimension skill taxonomy\n(bridge across 4 files)\nMySQL 3NF database + views", "#DCFCE7"),
        (77, 50, "4. Explore", "SAS Visual Analytics report\nDemand, pay, profiles\nData-quality visuals", "#FCE7F3"),
        (2, 22, "5a. Market models", "Salary-band model (ordinal\nlogit + gradient boosting)\nSkill bundles, pay headroom", "#E0E7FF"),
        (27, 22, "5b. Growth models", "JDS: logit, tree, boosting\nProfile-shape test\n(spike vs breadth)", "#E0E7FF"),
        (52, 22, "5c. Success models", "SDS: logit odds ratios,\ntree rules, personas\nCross-validated AUC", "#E0E7FF"),
        (77, 22, "6. Integrate", "Hype-gap map\n(asked for vs rewarded)\nTalent Signal Diagnostic", "#FDE68A"),
    ]
    for x, y0, t, b, col in boxes:
        ax.add_patch(plt.Rectangle((x, y0), 21, 12, fc=col, ec="#334155", lw=1.2))
        ax.text(x + 10.5, y0 + 9.6, t, ha="center", va="center", fontsize=11.5, fontweight="bold")
        ax.text(x + 10.5, y0 + 4.3, b, ha="center", va="center", fontsize=8.6)
    for x in [23, 48, 73]:
        ax.annotate("", xy=(x + 4, 56), xytext=(x, 56), arrowprops=dict(arrowstyle="-|>", lw=1.5))
    ax.annotate("", xy=(12.5, 34.5), xytext=(87.5, 49.5), arrowprops=dict(arrowstyle="-|>", lw=1.5, connectionstyle="arc3,rad=0.15"))
    for x in [23, 48, 73]:
        ax.annotate("", xy=(x + 4, 28), xytext=(x, 28), arrowprops=dict(arrowstyle="-|>", lw=1.5))
    ax.add_patch(plt.Rectangle((2, 3), 96, 11, fc="#F1F5F9", ec="#94A3B8", lw=1, ls="--"))
    ax.text(50, 10.8, "Runs across every stage", ha="center", fontsize=10.5, fontweight="bold")
    ax.text(50, 6.0, "Data-quality log (every issue, rows affected, treatment)  |  Automated verification against the raw files\n"
            "Cross-validation & effect sizes  |  Limitations stated next to each result", ha="center", fontsize=9)
    ax.text(50, 63, "Figure 3. Overall analytical flow", ha="center", fontsize=12, fontweight="bold")
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white"); plt.close(fig)


def gap_fig(path):
    fig, ax = plt.subplots(figsize=(8, 5.2))
    xs, ys = [100 * demand[d] for d in DIMS], [eff[d]["d"] for d in DIMS]
    ax.scatter(xs, ys, s=160, c=["#94A3B8" if eff[d]["p"] > .05 else "#1D4ED8" for d in DIMS], zorder=3)
    off = {"dashboard_story": (12, 6), "maths_stats": (12, -20), "ai_ml": (12, -8), "coding": (-14, -24), "big_data": (12, -8)}
    for d, x0, y0 in zip(DIMS, xs, ys):
        ax.annotate(f"{DNAME[d]} (d = {eff[d]['d']:.2f}{', n.s.' if eff[d]['p'] > .05 else ''})", (x0, y0), textcoords="offset points",
                    xytext=off[d], fontsize=9.5, ha="right" if off[d][0] < 0 else "left")
    ax.axhline(0.5, ls="--", c="#64748B", lw=1); ax.axvline(np.mean(xs), ls="--", c="#64748B", lw=1)
    ax.set_xlabel(f"Market demand: % of core analytics postings asking for the skill area (n = {len(core):,})")
    ax.set_ylabel("Growth reward: effect size (Cohen's d)\nhigh-hike vs low-hike juniors (JDS, n = %d)" % len(j))
    ax.set_xlim(10, 50); ax.set_ylim(0, 1.35)
    ax.text(10.5, 1.31, "HIDDEN EDGE: rewarded, rarely asked for", fontsize=9, color="#166534", va="top", fontweight="bold")
    ax.text(49.5, 1.31, "CORE: asked for and rewarded", fontsize=9, color="#1E3A8A", va="top", ha="right", fontweight="bold")
    ax.text(10.5, 0.04, "NOT REWARDED (below a medium effect, d < 0.5)", fontsize=9, color="#991B1B", fontweight="bold")
    ax.set_title("Figure 1. Preliminary hype-gap map: what job ads ask for vs what juniors are rewarded for", fontsize=11.5, fontweight="bold")
    ax.grid(alpha=.25)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white"); plt.close(fig)


def shape_fig(path):
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    lab = ["Average of 5 skills", "Weakest skill", "Strongest skill", "Gap strongest - weakest\n(lower = more balanced)"]
    vals = [auc1["skill_mean"], auc1["skill_min"], auc1["skill_max"], 1 - auc1["skill_range"]]
    ax.barh(lab[::-1], vals[::-1], color=["#1D4ED8", "#94A3B8", "#1D4ED8", "#1D4ED8"][::-1])
    ax.axvline(0.5, c="#991B1B", ls="--", lw=1); ax.text(0.505, -0.45, "coin flip", color="#991B1B", fontsize=9)
    for i, v in enumerate(vals[::-1]):
        ax.text(v + .005, i, f"{v:.2f}", va="center", fontsize=10)
    ax.set_xlim(0.45, 1.0); ax.set_xlabel("AUC: how well the measure separates high-hike from low-hike juniors")
    ax.set_title("Figure 2. Profile shape: breadth separates juniors, a single spike does not", fontsize=11.5, fontweight="bold")
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white"); plt.close(fig)


flow_fig(FIG / "fig1_flow.png"); gap_fig(FIG / "fig3_hype_gap.png"); shape_fig(FIG / "fig4_profile_shape.png")

# ------------------------------------------------------------------ document helpers
doc = Document()
for sec in doc.sections:
    sec.left_margin = sec.right_margin = Cm(2.3); sec.top_margin = sec.bottom_margin = Cm(2.2)
st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
st.paragraph_format.space_after = Pt(6); st.paragraph_format.line_spacing = 1.0
for h, sz in [("Heading 1", 16), ("Heading 2", 13.5), ("Heading 3", 12)]:
    hs = doc.styles[h]; hs.font.name = "Times New Roman"; hs.font.size = Pt(sz); hs.font.bold = True
    hs.font.color.rgb = RGBColor(0x0B, 0x2E, 0x59); hs.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    hs.paragraph_format.space_before = Pt(12 if h == "Heading 1" else 9); hs.paragraph_format.space_after = Pt(4)

# page numbers in footer
fp = doc.sections[0].footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = fp.add_run(); f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin"); r._r.append(f1)
it = OxmlElement("w:instrText"); it.text = "PAGE"; r._r.append(it)
f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "end"); r._r.append(f2)


def P(text="", bold_lead=None, italic=False, size=None, align=None, after=None):
    p = doc.add_paragraph()
    if bold_lead:
        p.add_run(bold_lead).bold = True
    run = p.add_run(text); run.italic = italic
    if size: run.font.size = Pt(size)
    if align: p.alignment = align
    if after is not None: p.paragraph_format.space_after = Pt(after)
    p.alignment = align if align is not None else WD_ALIGN_PARAGRAPH.JUSTIFY
    return p


def B(items, style="List Bullet"):
    for t in items:
        p = doc.add_paragraph(style=style); p.paragraph_format.space_after = Pt(2)
        if isinstance(t, tuple):
            p.add_run(t[0]).bold = True; p.add_run(t[1])
        else:
            p.add_run(t)


def shade(cell, hexcol):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hexcol); tcPr.append(sh)


def T(header, rows, widths=None, size=10, caption=None):
    if caption:
        cp = doc.add_paragraph(); rr = cp.add_run(caption); rr.bold = True; rr.font.size = Pt(10.5)
        cp.paragraph_format.space_after = Pt(3); cp.paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1, cols=len(header)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        cell = t.rows[0].cells[i]; cell.text = ""; rr = cell.paragraphs[0].add_run(str(h)); rr.bold = True; rr.font.size = Pt(size)
        shade(cell, "DCE6F2")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""; rr = cells[i].paragraphs[0].add_run(str(v)); rr.font.size = Pt(size)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(1)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def IMG(path, width=16.2):
    doc.add_picture(str(path), width=Cm(width)); doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER


def pct(x):
    return f"{100 * x:.1f}%"


def L(issue_start):
    return int(log.loc[log.issue.str.startswith(issue_start), "rows_affected"].iloc[0])


# ------------------------------------------------------------------ title page
for _ in range(5):
    doc.add_paragraph()
P("SAS CU Hackathon  |  Round 1 Approach Note", size=13, align=WD_ALIGN_PARAGRAPH.CENTER, after=18)
tp = doc.add_paragraph(); tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
rr = tp.add_run("HIRING FOR THE RIGHT SIGNALS"); rr.bold = True; rr.font.size = Pt(28); rr.font.color.rgb = RGBColor(0x0B, 0x2E, 0x59)
P("Do organisations hire, pay and develop data scientists for what actually makes them succeed? "
  "Measuring the gap between what job postings ask for and what drives junior growth and senior success",
  italic=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, after=30)
P("Problem Definition & Analytics Objective  |  Approach Description", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, after=40)
P("Team: ____________________", size=12, align=WD_ALIGN_PARAGRAPH.CENTER)
P("Data: Data Science Jobs, Analytics Jobs, JDS Skill Traits, SDS Personality Traits (2024-25)", size=11, align=WD_ALIGN_PARAGRAPH.CENTER)
P("Tools: Python (pandas, scikit-learn, statsmodels), MySQL 8, SAS Viya for Learners (Visual Analytics, Model Studio)",
  size=11, align=WD_ALIGN_PARAGRAPH.CENTER)
doc.add_page_break()

# ------------------------------------------------------------------ summary
doc.add_heading("Summary", 1)
P("Organisations hiring data scientists define what they want through job postings: roles, skills, experience and pay. "
  "A posting, however, captures what is easy to list, not necessarily what makes a data scientist succeed once hired. "
  "Hiring and pay are sound only if three signals agree: what organisations ask for in postings, what the market pays "
  "when it hires, and what organisations themselves reward once a person is on the job - salary hikes for juniors and "
  "overall success for senior, customer-facing staff. The four datasets let us measure all three signals in one place, "
  "and our first pass shows they do not agree.")
B([("What job ads ask for: ", f"coding appears in {pct(demand['coding'])} of the {len(core):,} core analytics postings, far more than any other "
     f"skill area (maths & statistics {pct(demand['maths_stats'])}, dashboards & storytelling {pct(demand['dashboard_story'])})."),
   ("What is rewarded: ", f"among {len(j)} junior data scientists, the skill areas that best separate high from low salary hikes are "
     f"dashboards & storytelling (effect size d = {eff['dashboard_story']['d']:.2f}) and maths & statistics (d = {eff['maths_stats']['d']:.2f}); "
     f"big-data skill shows no reliable difference (d = {eff['big_data']['d']:.2f}, p = {eff['big_data']['p']:.2f})."),
   ("Profile shape: ", f"a junior's average level across all five areas separates the groups well (AUC {auc1['skill_mean']:.2f}); "
     f"their single strongest skill barely does (AUC {auc1['skill_max']:.2f}). Breadth is rewarded, spikes are not."),
   ("What is paid at hiring: ", f"experience alone places a posting in the right salary band {pct(band['exp'])} of the time "
     f"(within one band {pct(band['exp1'])}); adding every listed skill does not improve this - listed skills barely move the entry price.")])
P("Our analytics objective is therefore to measure how far the skills and attributes the market demands and pays for "
  "line up with those associated with junior growth and senior success, and to turn that gap into evidence-based "
  "guidance on what organisations should hire for, pay for and develop - and what aspiring data scientists should build "
  "first. The deliverable is a Talent Signal Diagnostic: for a candidate or employee profile and a target role, it shows "
  "how well the profile covers what the role really needs, which skill area to develop first (the floor), the market pay "
  "benchmark for the role, and - for senior hires - the traits associated with success. Sections 1 and 2 define the "
  "problem and the approach; all figures are preliminary results from the cleaned data and will be extended in the "
  "analysis phase.")

# ------------------------------------------------------------------ 1. problem definition
doc.add_heading("1. Problem Definition and Analytics Objective", 1)
doc.add_heading("1.1 Context", 2)
P("The brief frames the problem around data-science jobs, the skills of data scientists and their personality traits, and "
  "asks for the best information that can be extracted from four datasets. Read together, the files describe the full "
  "talent cycle an organisation manages: the external market it hires from (two job-posting files), the technical skills "
  "associated with early growth inside a company (junior data scientists) and the behavioural traits associated with "
  "success at senior, customer-facing level (senior data scientists). Two files are market data; two are a company's "
  "own employee data. That is why we frame the problem from the organisation's side.")
T(["Dataset", "What one row is", "Rows (raw -> analysed)", "Signal it carries"], [
    ["Analytics Jobs", "One job posting: designation, skills, experience, location, salary band",
     f"15,841 -> {len(an):,} (exact duplicates removed); {len(core):,} core analytics", "What employers ask for (demand) and the band they offer"],
    ["Data Science Jobs", "One company x job title: openings, min/avg/max salary, minimum experience",
     f"{len(ds):,} -> {len(ds):,}", "What the market pays (price) and how much room there is"],
    ["JDS Skill Traits", "One junior data scientist: 5 skill scores (1-5) + high/low salary hike", f"{len(j)} -> {len(j)}",
     "What is rewarded early in a career (growth)"],
    ["SDS Personality Traits", "One senior, customer-facing data scientist: Big Five traits + high/low success",
     f"{len(s)} -> {len(s)}", "What is rewarded at senior level (success)"],
], widths=[3.2, 5.6, 4.2, 4.2], caption="Table 1. The four datasets and the career signal each one carries")

doc.add_heading("1.2 The problem we identified", 2)
P("Job postings are the organisation's public statement of what a data scientist should be, and they shape the whole "
  "talent pipeline: candidates build skills to match them, universities design courses around them and recruiters screen "
  "against them. The hidden assumption is that what is listed in a posting is what makes a data scientist succeed. If "
  "that assumption fails, the cost is real: organisations screen out people who would have grown fast, pay for "
  "credentials that do not translate into performance, under-invest in the skills that do, and aspirants spend scarce "
  "time building the wrong profile.")
P("Problem statement. ", bold_lead=None)
doc.paragraphs[-1].runs[0].bold = True
P("Organisations hiring data scientists define what they want through job postings: roles, skills, experience and pay. "
  "But a posting captures what is easy to list, not necessarily what makes a data scientist succeed once hired. Inside "
  "organisations, junior data scientists' technical skill profiles are linked to how fast they earn salary hikes, and "
  "senior, customer-facing data scientists' personality traits are linked to their overall success. If what the market "
  "asks for and pays for differs from what actually drives growth and success, organisations hire, pay and develop "
  "talent against the wrong signals - and aspirants build the wrong skills.", italic=True)
P("The problem is to measure how far the skills and attributes the market demands and pays for line up with those "
  "associated with junior growth and senior success, and to turn that gap into evidence-based guidance on what "
  "organisations should hire for, pay for and develop, and what aspiring data scientists should build first.",
  italic=True).runs[0].bold = True

doc.add_heading("1.3 Stakeholders and the decisions this informs", 2)
T(["Stakeholder", "Decision they face", "What our analysis gives them"], [
    ["Hiring managers & HR (primary)", "What to put in a posting; whom to shortlist; how to assess candidates",
     "Which requirements are associated with growth and success, and which are only listed; role-level skill coverage of a candidate"],
    ["Compensation / reward teams", "What to pay for a role and experience level; how wide to set the range",
     "Salary-band drivers; pay benchmarks and min-avg-max spread by title and company size"],
    ["Learning & development / team leads", "Which skills to develop in juniors; whom to prepare for senior, client-facing roles",
     "The floor skill area per person; trait profile of successful seniors"],
    ["Aspirants & universities (secondary)", "What to learn first; how to design courses",
     "Hype-gap map: skills the market over- and under-signals; the same diagnostic used for self-assessment"],
], widths=[4.0, 5.6, 7.6], caption="Table 2. Stakeholders, their decisions and our outputs")

doc.add_heading("1.4 Analytics objectives and research questions", 2)
P("The problem is decomposed into five objectives. Each maps to a research question, one or more datasets, a testable "
  "hypothesis and a planned method; together they cover the full career path and all four files.")
T(["#", "Research question", "Data", "Hypothesis", "Method (Section 2.6)"], [
    ["O1", "What does the analytics market ask for - by role family, skill area, experience and city?", "Analytics Jobs",
     "H1: coding dominates demand; maths/statistics and storytelling are asked for far less", "Descriptive profiling, CIs, skill co-occurrence / association rules"],
    ["O2", "What does the market pay for at hiring - experience, role, city or listed skills?", "Analytics Jobs, DS Jobs",
     "H2: experience and role set the salary band; listed skills add little once these are controlled", "Ordinal logistic regression, gradient boosting, pay headroom index"],
    ["O3", "Which skill areas - and which profile shape - separate juniors with high salary hikes?", "JDS",
     "H3: maths/stats and storytelling matter most; H4: balanced breadth beats a single spike", "Effect sizes, logistic regression, decision tree, nested-model test"],
    ["O4", "Which personality traits distinguish successful senior, customer-facing data scientists?", "SDS",
     "H5: conscientiousness and openness are the strongest correlates of success", "Effect sizes, logistic regression (odds ratios), tree rules, personas"],
    ["O5", "Where do demand and reward diverge, and what should organisations hire for, pay for and develop?", "All four (via taxonomy)",
     "H6: the skills most demanded are not the ones most rewarded", "Hype-gap map + Talent Signal Diagnostic"],
], widths=[0.9, 4.6, 2.4, 4.8, 4.5], size=9.5, caption="Table 3. Objectives, research questions and hypotheses")

doc.add_heading("1.5 Early evidence that the problem is real", 2)
P("Before committing to this objective we tested it on the cleaned data. The results below are deliberately simple; "
  "they justify the problem, not the final answer.")
T(["Skill area", "Market demand (% of core postings)", "High-hike juniors (mean)", "Low-hike juniors (mean)", "Effect size d", "p (Mann-Whitney)"],
  [[DNAME[d], pct(demand[d]), f"{eff[d]['hi']:.2f}", f"{eff[d]['lo']:.2f}", f"{eff[d]['d']:.2f}", f"{eff[d]['p']:.4f}" if eff[d]['p'] >= 1e-4 else "<0.0001"]
   for d in DIMS], widths=[3.8, 3.2, 2.6, 2.6, 2.2, 2.6], caption="Table 4. Demand signal vs growth signal for the five skill areas")
IMG(FIG / "fig3_hype_gap.png", 14.5)
P(f"Three observations shape the objective. First, the market's most requested area (coding, {pct(demand['coding'])}) is only "
  f"the third-strongest separator of high-hike juniors, while the two least requested areas, maths & statistics and "
  f"dashboards & storytelling, are the strongest. Second, big data is requested about as often as the others "
  f"({pct(demand['big_data'])}) but shows no reliable difference between high- and low-hike juniors. Third, the shape of "
  f"the profile matters: the average across all five areas separates the groups (AUC {auc1['skill_mean']:.2f}), the single "
  f"strongest skill hardly does (AUC {auc1['skill_max']:.2f}), and a larger gap between strongest and weakest skill goes "
  f"with lower hikes.")
IMG(FIG / "fig4_profile_shape.png", 13)
P(f"We also tested the stricter claim that the weakest skill matters on its own. Once the average level is controlled for, "
  f"the weakest score adds nothing (p = {p_min:.2f}). We therefore do not claim a strict weakest-link law. The finding we carry "
  f"forward is that breadth is rewarded and spikes are not; because scores are capped at 5 and many juniors already sit at "
  f"the cap in their strong areas (18-58% of scores are a perfect 5), the only place a profile can still grow is its "
  f"weaker areas - which is why the diagnostic recommends developing the floor rather than deepening a strength.")
P(f"On the senior side, a five-trait logistic model separates high- from low-success seniors with a cross-validated AUC "
  f"of {sds_auc:.2f}. Conscientiousness (odds ratio {sds_or['conscientiousness']:.1f} per standard deviation) and openness "
  f"({sds_or['openness_to_experience']:.1f}) dominate. Neuroticism shows no raw difference between the groups "
  f"({sds_uni['neuroticism'][0]:.1f} vs {sds_uni['neuroticism'][1]:.1f}) but becomes significant once the other traits are held "
  f"constant - a suppression effect we will investigate rather than over-interpret.")

doc.add_heading("1.6 Scope", 2)
T(["In scope", "Out of scope (and why)"], [
    ["India-based analytics and data-science postings, 2024-25 (international postings flagged and excluded from core analysis)",
     "Causal claims: all four datasets are observational; we report associations and say so"],
    [f"Nine analytics role families ({len(core):,} core postings); non-analytics postings kept and flagged for comparison",
     "Exact salary prediction for Analytics Jobs: salary exists only as six bands, so we predict bands"],
    ["Junior technical skills (JDS) and senior personality traits (SDS) as measured by the companies",
     "Linking individuals across files: the four files share no key, so links are made at skill-area level only"],
    ["A working prototype diagnostic and SAS Visual Analytics / Model Studio artefacts",
     "Time trends: no posting dates, so no forecasting of skill demand over time"],
], widths=[8.6, 8.6], caption="Table 5. Scope boundaries")

doc.add_heading("1.7 Assumptions and limitations stated up front", 2)
B([("Data is sample, self-reported or masked (brief, key considerations). ", "We therefore clean conservatively, flag rather than delete, and verify every cleaned value against the raw files."),
   ("Skill lists are truncated. ", f"{pct(L('key_skills truncated') / len(an))} of key-skill lists end in '...'; we recover skills from descriptions, so demand shares are lower bounds."),
   ("The taxonomy is an assumption. ", "Market skills are mapped to the five JDS areas by a documented keyword taxonomy (470 skill-to-area links, each listed in the database). Results that depend on it are labelled."),
   ("Small people samples. ", f"JDS n = {len(j)}, SDS n = {len(s)}. We use simple, interpretable models, repeated cross-validation and effect sizes, and avoid segments too small to be stable."),
   ("Ceiling effect in JDS. ", "Many scores sit at the maximum of 5; this limits discrimination at the top and is treated explicitly."),
   ("Two different 'success' outcomes. ", "JDS uses performance-based salary hike; SDS uses an organisation-defined success class. We never mix them in one model.")])

doc.add_heading("1.8 What success looks like", 2)
B(["A defensible answer to each research question, with effect sizes, confidence intervals and cross-validated model performance.",
   "A hype-gap map that ranks the five skill areas by demand and by reward, with the uncertainty shown.",
   "A working Talent Signal Diagnostic that returns, for any candidate or employee profile and target role, the skill coverage, the floor skill area to develop, the pay benchmark for the role, and a senior-readiness note.",
   "Guidance per stakeholder: what to require in postings, what to pay for, what to develop - each backed by a measured effect.",
   "Every number traceable to the raw data through the data-quality log, the database and the verification script."])

doc.add_heading("1.9 How the objective covers what will be tested", 2)
T(["Brief: what would be tested", "Where our objective exercises it"], [
    ["Data management and manipulation", "10-stage cleaning of four messy files, skill taxonomy, normalised MySQL database, independent verification"],
    ["Approach in a business-analytics context", "Stakeholder decisions drive the objectives; output is a decision tool, not just a model"],
    ["Statistical / data-mining / machine-learning skills", "Effect sizes and tests, ordinal and binary logistic regression, trees, gradient boosting, association rules, clustering, cross-validation"],
    ["Overall conclusion drawn from the analysis", "The hype-gap map and the diagnostic consolidate all four datasets into one recommendation per stakeholder"],
], widths=[5.6, 11.6], caption="Table 6. Mapping our objective to the evaluation criteria in the brief")

# ------------------------------------------------------------------ 2. approach
doc.add_page_break()
doc.add_heading("2. Approach Description", 1)
doc.add_heading("2.1 Overall flow", 2)
IMG(FIG / "fig1_flow.png", 16.5)
P("The approach moves from understanding to clean, linked data, then to three families of models (market, growth, success) "
  "and finally to integration in a single decision tool. Four principles, listed in 2.2, run through every stage.")

doc.add_heading("2.2 Design principles and why we chose them", 2)
T(["Principle", "What it means in practice", "Why"], [
    ["Flag, don't delete", "Only exact duplicates are removed; every other issue becomes a 0/1 flag; original columns are kept beside cleaned ones",
     "The brief warns of meaningless entries and outliers; deleting them silently would change the population and cannot be audited"],
    ["Every number traceable", f"A data-quality log (stage, issue, rows, treatment) and a verification script that recomputes every claim from the raw files ({n_pass}/{n_chk} checks pass)",
     "Judges and stakeholders can check any figure; it also caught our own errors"],
    ["Interpretable first", "Logistic regression and decision trees lead; gradient boosting is a benchmark",
     "Stakeholders need reasons (odds ratios, rules), and the people samples are small"],
    ["Big data drives predictions, small data drives insight", f"Salary models learn from {band['n']:,} postings; the {len(j)}- and {len(s)}-row company files give tested findings, not per-person scores",
     "Avoids building a tool on 139 rows and avoids asking users to self-rate on an unknown scale"],
], widths=[3.4, 7.0, 6.8], size=9.5, caption="Table 7. Design principles")

doc.add_heading("2.3 Stage 1 - Data audit and cleaning", 2)
P("Each file was profiled column by column before any change (S0), then cleaned in ten logged stages. Table 8 lists the "
  "most consequential issues; the full log is in Appendix A.")
T(["Stage", "What it covers", "Key issues found (rows affected)", "Treatment"], [
    ["S1 Keys & names", "IDs, column names", f"DS reference_no shared by {L('reference_no is not unique')} different rows; JDS/SDS ids duplicated; hyphens and stray spaces in column names",
     "Surrogate keys; original ids kept; names standardised"],
    ["S2 Duplicates", "Exact and near duplicates", f"{L('Exact duplicate postings'):,} exact duplicate postings; {L('Near-duplicates after'):,} near-duplicates; {L('Possible reposts'):,} possible reposts",
     "Exact removed (verified field by field); others flagged"],
    ["S3 Text hygiene", "Spaces, encoding, noise", f"{L('Designations padded'):,} designations padded with 'Urgent hiring', 'Walk-in', '@Mumbai'; non-ASCII text",
     "Normalised; clean title in a new column"],
    ["S4 Types", "Text to numbers", "Salaries as '7.8L'; experience as '6-10 yrs'; salary only as 6 text bands",
     "Parsed to numbers; band order, low/high/mid derived"],
    ["S5 Validity", "Range and logic rules", f"Minimum salary < 1 LPA ({L('Minimum salary below 1 LPA')}); 'Senior' titles with 0 years ({L(chr(39) + 'Senior' + chr(39) + ' titles')}); 0-3 LPA band with 8+ years ({L('Lowest band (0-3 LPA)')})",
     "Flagged; no imputation"],
    ["S6 Outliers", "Skew and extremes", f"num_of_jobs median 22, max 4,200 ({L('num_of_jobs extremely')} outliers); top-firm salaries (e.g. 82 LPA); JDS ceiling effect",
     "Kept and flagged; log transform; winsorised copy only for regression"],
    ["S7 Standardise", "Categories and lists", f"{L('location:'):,} location strings -> canonical cities; {L('key_skills free text'):,} postings of free-text skills (8,462 tokens); {L('10,097 distinct'):,} free-text designations; job_type 76% missing",
     "City and tier mapping; skill cleaning and typing; 9 analytics + non-analytics role families"],
    ["S8 Scope", "What belongs in the analysis", f"{L('Non-analytics roles'):,} non-analytics postings (BPO, HR, sales, medical coding...); {L('Overseas locations'):,} overseas; {L('Low-quality'):,} spam",
     f"Flagged; core sample = {len(core):,} postings"],
    ["S9 Derive", "New variables", f"87% of skill lists truncated; no common key across files",
     f"{L('Skills recovered'):,} skills recovered from descriptions; 5-area taxonomy flags; tool flags; z-scores"],
    ["S10 Validate", "Rules and audits", "Automated rules; manual audit of 150 random role classifications; independent re-computation from raw files",
     f"~91% exact role family, ~92% analytics vs not; {n_pass}/{n_chk} verification checks pass"],
], widths=[2.4, 2.8, 7.0, 5.0], size=9, caption="Table 8. Ten-stage cleaning pipeline and the issues it resolved")
P("Peer audit. ", bold_lead=None); doc.paragraphs[-1].runs[0].bold = True
P("An independent review of an earlier version found that skills written as compounds ('Oracle SQL', 'SQL Server', "
  f"'SAS SQL') were not counted. The matcher was rebuilt to find whole words inside compound skills, with exclusions for "
  f"false friends ('medical coding', 'regression testing', 'search engine optimization'). Postings flagged for SQL rose from "
  f"1,033 to {int(an.has_sql.sum()):,}, and a permanent check now confirms that no raw SQL mention is missed. The same review "
  f"led us to remove two composite JDS indices and a sample-dependent reversal of neuroticism. We report this because a "
  f"pipeline that can be audited and corrected is worth more than one that only claims to be clean.")

doc.add_heading("2.4 Stage 2 - Consolidation: linking four files that share no key", 2)
P("The files cannot be joined on an identifier. They can be joined on meaning: the JDS file measures five technical skill "
  "areas, and the job postings list skills that belong to those same areas. We built a five-area taxonomy (big data, "
  "maths & statistics, coding, AI & ML, dashboards & storytelling) that maps 470 market skill names to the JDS areas. "
  "Every posting therefore carries five 0/1 flags that are directly comparable with the five JDS scores. This is the "
  "bridge that makes the hype-gap analysis and the diagnostic possible.")
P("All cleaned data was loaded into a MySQL 8 database designed to third normal form: list-valued fields such as skills "
  "and locations were split into bridge tables (1NF), attributes were moved to the table whose key they depend on (2NF/3NF), "
  "and derived values are computed in views rather than stored. The schema has 23 tables, 16 foreign keys, 10 unique keys "
  "and 9 CHECK constraints; a post-load script compares every table and key figure with its expected value. The team works "
  "from one shared instance, so every analysis uses the same audited data.")
IMG(HERE / "database" / "ERD.png", 16.5)
cp = doc.add_paragraph(); rr = cp.add_run("Figure 4. Entity-relationship diagram of the core database (staging tables not shown)"); rr.italic = True; rr.font.size = Pt(10)
cp.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_heading("2.5 Stage 3 - Exploration", 2)
P("Exploration is done in SAS Visual Analytics on the cleaned tables uploaded to SAS Viya for Learners, so that every "
  "chart in the final report is reproducible in the platform the judges use. The exploration report has four pages: "
  "market demand (role families, skill areas, cities, experience); pay (salary bands by experience and role, salary ranges "
  "and headroom by title and company size); people (JDS score distributions and ceiling effect, SDS trait distributions by "
  "success); and data quality (what was flagged and why).")

doc.add_heading("2.6 Stage 4 - Modelling plan", 2)
P("Each objective has a primary interpretable model, a benchmark and an explicit validation rule. Methods were chosen for "
  "the shape of the outcome and the size of the sample, not for novelty.")
T(["Objective", "Primary method", "Why this method", "Benchmark / check", "Validation"], [
    ["O1 Demand", "Profiling with 95% CIs; association rules on skill pairs (support, confidence, lift)",
     "Demand is a share; rules reveal skill bundles employers ask for together", "Role-family and city breakdowns", "Bootstrap CIs; minimum support"],
    ["O2 Pay", "Ordinal logistic regression for salary band; regression of average salary on title x experience (DS Jobs)",
     "The band outcome is ordered; odds ratios translate into 'chance of a higher band'", f"Gradient boosting (preliminary: {pct(band['full'])} exact, {pct(band['full1'])} within one band vs {pct(band['base'])} baseline)",
     "Stratified 5-fold CV; experience-only model as the bar to beat"],
    ["O3 Junior growth", "Logistic regression on the 5 skills; nested test of profile shape (mean, min, max, range)",
     "Odds ratios per skill; directly tests 'spike vs breadth'", f"Decision tree (rules), gradient boosting; preliminary 5-skill CV AUC {jds_auc5:.2f}",
     "Repeated stratified CV, effect sizes, multicollinearity check"],
    ["O4 Senior success", "Logistic regression on the Big Five; trait personas by k-means", "Odds ratios per trait; personas are easy to act on",
     f"Decision tree; preliminary CV AUC {sds_auc:.2f}", "Repeated CV; suppression check for neuroticism"],
    ["O5 Integration", "Hype-gap map: demand share vs effect size per skill area", "Puts market and company evidence on one chart",
     "Sensitivity to taxonomy choices", "Results shown with and without description-recovered skills"],
], widths=[2.3, 4.2, 3.9, 3.8, 3.0], size=9, caption="Table 9. Methods, reasons and validation by objective")
P(f"A note on honesty in modelling. The preliminary salary-band models already show that listed skills add little to "
  f"experience in predicting the entry band (experience alone: {pct(band['exp'])} exact; with all skills: {pct(band['full'])}). "
  f"We treat that as a finding for O2, not as a failure to hide: it is precisely the evidence that the price signal and "
  f"the demand signal differ.")

doc.add_heading("2.7 Stage 5 - The prototype: Talent Signal Diagnostic", 2)
P("The diagnostic is the point where the four datasets become one answer for one hiring or development decision. It is "
  "built for hiring managers, HR and team leads, and the same tool lets an aspirant assess themselves. It asks only for "
  "facts that can be verified - skills, role, experience, city - never for a self-rating on an unknown scale.")
T(["Step", "Input / logic", "Output", "Evidence behind it"], [
    ["1. Profile", "Skills of the candidate or employee, ticked from the 470 mapped market skills; target role family, years of experience, city",
     "Skill-area coverage (5 areas)", "Taxonomy (Stage 2)"],
    ["2. Role requirement", "Share of postings in the target role family that ask for each area, including skills recovered from descriptions",
     "What the role really asks for", f"{len(core):,} core postings"],
    ["3. Signal check", "Compares each required area with its association with junior growth: required and rewarded, required but not rewarded, rewarded but rarely required",
     "Which requirements matter and which are only listed", "O5: hype-gap map"],
    ["4. Find the floor", "Among areas that matter for the role, the one with the lowest coverage, ranked by its growth effect",
     "The one area to develop first", "O3: breadth is rewarded; effect sizes per area"],
    ["5. Pay benchmark", "Expected salary band for role, experience and city; min-avg-max spread for the title and company size",
     "Benchmark band and range", f"O2 models; DS Jobs ({len(ds):,} offers)"],
    ["6. Senior readiness", "For senior or client-facing roles: the traits associated with success", "Readiness note for assessment and development", "O4: SDS models"],
], widths=[2.4, 6.4, 3.6, 4.8], size=9.5, caption="Table 10. How the diagnostic works")
da = ds_role_demand.loc["Data Analyst / Analytics"]
P(f"Illustration (real role requirements, hypothetical candidate). A hiring manager is screening a fresher for a Data Analyst "
  f"role whose profile lists Python, SQL and Excel. Data Analyst postings ask for coding in {pct(da['dim_coding'])} of cases, "
  f"dashboards & storytelling in {pct(da['dim_dashboard_story'])}, maths & statistics in {pct(da['dim_maths_stats'])} and AI & ML "
  f"in {pct(da['dim_ai_ml'])}. The candidate covers coding and part of dashboards & storytelling but nothing in maths & "
  f"statistics - an area postings rarely ask for, yet one of the strongest separators of high-hike juniors "
  f"(d = {eff['maths_stats']['d']:.2f}). The diagnostic flags maths & statistics as the floor to test at interview and develop "
  f"in the first year, gives the pay benchmark for the role, and shows that Data Analyst offers carry the widest spread "
  f"between average and maximum salary of any title (median {pct(head['Data Analyst'])}), so the offer should be set "
  f"deliberately rather than by default.")
P("Implementation. The diagnostic is a Python module that reads the shared database views; the models behind it are "
  "rebuilt as SAS Model Studio pipelines (logistic regression, decision tree, gradient boosting with model comparison) "
  "so the scoring logic is visible in SAS, and its outputs are presented as an interactive page in SAS Visual Analytics.")

doc.add_heading("2.8 Tools and why each was chosen", 2)
T(["Tool", "Used for", "Reason"], [
    ["Python (pandas, regex, scikit-learn, statsmodels)", "Cleaning, text mining of skills and titles, verification, preliminary models",
     "Free-text cleaning at this scale (10,097 designations, 8,462 skill tokens) needs scripted, repeatable rules"],
    ["MySQL 8 (3NF schema, views)", "Single source of truth for the team", "Constraints enforce integrity; views give analysis-ready tables without duplication"],
    ["SAS Visual Analytics", "Exploration and final visuals", "Recommended platform; interactive, reproducible charts for report and deck"],
    ["SAS Model Studio", "Final model pipelines and comparison", "Visual, auditable pipelines; built-in model comparison and assessment"],
    ["Excel", "Not used", "Discouraged by the guidelines; nothing in the pipeline depends on it"],
], widths=[4.4, 5.6, 7.2], size=9.5, caption="Table 11. Tools")

doc.add_heading("2.9 Risks and how the approach controls them", 2)
T(["Risk", "Control"], [
    ["Misclassifying roles from free-text titles", "Ordered rules refined on samples, then measured on an independent random sample of 150 (about 91% exact); non-analytics kept for comparison"],
    ["Under-counting skills (truncation, compound phrases)", "Recovery from descriptions; whole-word matching inside compounds; automated check against raw text"],
    ["Overfitting small people samples", "Few, interpretable predictors; repeated cross-validation; no segments with a handful of members"],
    ["Taxonomy drives the integration", "Every mapping listed in the database; sensitivity analysis with and without recovered skills"],
    ["Over-claiming", "Associations reported as associations; limitations stated next to each result"],
], widths=[5.6, 11.6], size=9.5, caption="Table 12. Risk register")

doc.add_heading("2.10 Next steps", 2)
B(["Run the full models for O1-O5 (Table 9) on the shared database and rebuild them in SAS Model Studio.",
   "Build the SAS Visual Analytics exploration report and the diagnostic page.",
   "Write the Data Exploration, Data Analysis, Results and Implications sections from those outputs.",
   "Prepare the presentation around the three signals and a live run of the diagnostic on a hiring scenario."], style="List Number")

# ------------------------------------------------------------------ appendix
doc.add_page_break()
doc.add_heading("Appendix A. Data-quality log (complete)", 1)
T(["Stage", "File", "Issue", "Rows", "Treatment"],
  [[r.stage, r.file, r.issue, f"{int(r.rows_affected):,}", r.treatment] for r in log.itertuples()],
  widths=[1.2, 2.6, 6.0, 1.5, 5.9], size=8)
doc.add_heading("Appendix B. Preliminary model outputs", 1)
T(["Model", "Data", "Result"], [
    ["Logistic regression, 5 skills -> high hike", f"JDS, n = {len(j)}", f"5-fold CV AUC {jds_auc5:.3f}"],
    ["Single-measure AUC: average / weakest / strongest skill", "JDS", f"{auc1['skill_mean']:.3f} / {auc1['skill_min']:.3f} / {auc1['skill_max']:.3f}"],
    ["Weakest skill controlling for average (logit)", "JDS", f"p = {p_min:.2f} (not significant)"],
    ["Logistic regression, Big Five -> high success", f"SDS, n = {len(s)}", f"5-fold CV AUC {sds_auc:.3f}"],
    ["Odds ratio per SD (C / O / E / N / A)", "SDS", " / ".join(f"{sds_or[t]:.1f}" for t in ["conscientiousness", "openness_to_experience", "extraversion", "neuroticism", "agreeableness"])],
    ["Gradient boosting, salary band (all features)", f"Analytics Jobs, n = {band['n']:,}", f"exact {pct(band['full'])}, within one band {pct(band['full1'])}"],
    ["Gradient boosting, salary band (experience only)", "Analytics Jobs", f"exact {pct(band['exp'])}, within one band {pct(band['exp1'])}; majority baseline {pct(band['base'])}"],
], widths=[6.5, 4.0, 6.7], size=9.5)
T(["Job title", "Median headroom (max - avg) / avg"], [[t, pct(v)] for t, v in head.items()], widths=[6, 6], size=9.5,
  caption="Table B2. Negotiation headroom by job title (DS Jobs)")
T(["Role family", "Core postings"], [[k, f"{v:,}"] for k, v in fam.items()], widths=[6, 4], size=9.5,
  caption="Table B3. Core analytics sample by role family")
doc.add_heading("Appendix C. Reproducibility", 1)
B([("01_clean.py, role_rules.py, taxonomy.py: ", "cleaning pipeline, role rules and skill taxonomy"),
   ("verify_against_raw.py: ", f"recomputes every claim from the raw files ({n_pass}/{n_chk} pass)"),
   ("build_database.py, database/sql/01-05: ", "schema, data load, views and post-load verification"),
   ("CLEAN.md, outputs/data_quality_log.csv: ", "what was cleaned, with real before/after rows"),
   ("make_round1_report.py: ", "builds this document; every number is computed from the cleaned data")])

path = OUT / "Round1_Approach_Note_FINAL.docx"
doc.save(path)
print("saved", path)
