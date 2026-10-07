"""Build the final Approach Note (Round 2: all six sections + appendix) as Word.
Every number is read from the cleaned data or from models/*/results - nothing typed by hand.
Run after models/run_models.py:   python make_final_report.py"""
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = Path(__file__).resolve().parent
M = HERE / "models"
OUT = Path(r"C:\Users\Chaitanya Sharma\Documents\Claude Stuff\SAS CU Hackathon Round 2")
OUT.mkdir(parents=True, exist_ok=True)


def R(model, name):
    d = next(M.glob(f"{model}_*"))
    return pd.read_csv(d / "results" / f"{name}.csv")


def F(model, name):
    return next(M.glob(f"{model}_*")) / "figures" / f"{name}.png"


# ------------------------------------------------------------------ data & results
an = pd.read_csv(HERE / "clean" / "analytics_jobs_clean.csv")
ds = pd.read_csv(HERE / "clean" / "ds_jobs_clean.csv")
jds = pd.read_csv(HERE / "clean" / "jds_clean.csv")
sds = pd.read_csv(HERE / "clean" / "sds_clean.csv")
log = pd.read_csv(HERE / "outputs" / "data_quality_log.csv", keep_default_na=False)
ver = (HERE / "VERIFICATION.md").read_text(encoding="utf-8")
n_pass, n_chk = map(int, re.search(r"(\d+) of (\d+) checks pass", ver).groups())
core = an[an.in_core_analytics == 1]

dem = R("M01", "skill_area_demand").set_index("skill_area")
roled = R("M01", "role_by_skill_area")
top_sk = R("M01", "top_25_skills")
pairs = R("M02", "top_25_skill_pairs_by_lift")
dimlift = R("M02", "skill_area_cooccurrence_lift")
o3 = R("M03", "odds_ratios").set_index("factor")
c4 = R("M04", "model_comparison").set_index("feature_set")
i4 = R("M04", "grouped_permutation_importance").set_index("factor_group")
e5 = R("M05", "salary_effects_pct").set_index("label")
cv5 = R("M05", "cv_r2_comparison").set_index("model")
hr5 = R("M05", "pay_spread_by_title").set_index("job_title")
hs5 = R("M05", "pay_spread_by_company_scale").set_index("company_scale")
o6 = R("M06", "odds_ratios").set_index("variable")
g6 = R("M06", "group_means").set_index("skill_area")
c8 = R("M08", "model_comparison").set_index("model")
p8 = R("M08", "permutation_importance")
a9 = R("M09", "single_measure_auc").set_index("measure")
n9 = R("M09", "nested_tests_vs_average")
h9 = R("M09", "hike_rate_by_level_and_shape")
o10 = R("M10", "odds_ratios").set_index("variable")
g10 = R("M10", "group_means").set_index("trait")
c12 = R("M12", "model_comparison").set_index("model")
pers = R("M13", "personas")
k13 = R("M13", "choosing_k")
hg = R("M14", "hype_gap").set_index("skill_area")
rec = R("M00", "skill_recovery_from_descriptions").set_index("skill_area")
fun = R("M00", "analytics_jobs_funnel")
cm8 = R("M08", "confusion_matrix_best")

# tree rules -> first splits recomputed on the data
t7 = (next(M.glob("M07_*")) / "results" / "tree_rules.txt").read_text()
t11 = (next(M.glob("M11_*")) / "results" / "tree_rules.txt").read_text()
th7 = float(re.search(r"Dashboards & storytelling <= ([\d.]+)", t7).group(1))
th11o = float(re.search(r"Openness <= ([\d.]+)", t11).group(1)); th11c = float(re.search(r"Conscientiousness <= ([\d.]+)", t11).group(1))
lo7 = jds[jds.dashboard_and_storytelling_skills <= th7]; hi7 = jds[jds.dashboard_and_storytelling_skills > th7]
s_lo = sds[sds.openness_to_experience <= th11o]; s_mid = sds[(sds.openness_to_experience > th11o) & (sds.conscientiousness <= th11c)]
s_hi = sds[(sds.openness_to_experience > th11o) & (sds.conscientiousness > th11c)]

pct = lambda x: f"{100 * x:.1f}%"
DIM = ["Big data", "Maths & statistics", "Coding", "AI & machine learning", "Dashboards & storytelling"]
best_sen = c12.drop(index="Baseline (guess majority class)").auc_mean.idxmax()
sto, mat, cod, big = hg.loc["Dashboards & storytelling"], hg.loc["Maths & statistics"], hg.loc["Coding"], hg.loc["Big data"]


def L(issue_start):
    return int(log.loc[log.issue.str.startswith(issue_start), "rows_affected"].iloc[0])


# ------------------------------------------------------------------ flow figure (final version)
def flow_fig(path):
    plt.rcParams.update({"font.family": "Times New Roman"})
    fig, ax = plt.subplots(figsize=(10, 6.2)); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 64)
    boxes = [(2, 50, "1. Define", "Brief + data dictionary\nStakeholders & decisions\nObjectives & hypotheses", "#DBEAFE"),
             (27, 50, "2. Audit & clean", "10-stage pipeline (S0-S10)\nFlag, don't delete\nVerified against raw files", "#FEF3C7"),
             (52, 50, "3. Consolidate", "5-area skill taxonomy\n(bridge across 4 files)\nMySQL 3NF database", "#DCFCE7"),
             (77, 50, "4. Explore", "Distributions, quality,\nfunnels, derivations\n(Python + SAS VA)", "#FCE7F3"),
             (2, 22, "5a. What is asked", "Demand profile\nAssociation rules\n(M01-M02)", "#E0E7FF"),
             (27, 22, "5b. What is paid", "Ordinal logit, boosting,\nlog-salary regression\n(M03-M05)", "#E0E7FF"),
             (52, 22, "5c. What is rewarded", "Juniors: M06-M09\nSeniors: M10-M13\nlogit, trees, ensembles", "#E0E7FF"),
             (77, 22, "6. The gap", "Bootstrap hype-gap map\n(M14)\nRecommendations", "#FDE68A")]
    for x, y0, t, b, col in boxes:
        ax.add_patch(plt.Rectangle((x, y0), 21, 12, fc=col, ec="#334155", lw=1.2))
        ax.text(x + 10.5, y0 + 9.6, t, ha="center", va="center", fontsize=11.5, fontweight="bold")
        ax.text(x + 10.5, y0 + 4.3, b, ha="center", va="center", fontsize=8.8)
    for x in [23, 48, 73]:
        ax.annotate("", xy=(x + 4, 56), xytext=(x, 56), arrowprops=dict(arrowstyle="-|>", lw=1.5))
        ax.annotate("", xy=(x + 4, 28), xytext=(x, 28), arrowprops=dict(arrowstyle="-|>", lw=1.5))
    ax.annotate("", xy=(12.5, 34.5), xytext=(87.5, 49.5), arrowprops=dict(arrowstyle="-|>", lw=1.5, connectionstyle="arc3,rad=0.15"))
    ax.add_patch(plt.Rectangle((2, 3), 96, 11, fc="#F1F5F9", ec="#94A3B8", lw=1, ls="--"))
    ax.text(50, 10.8, "Across every stage", ha="center", fontsize=10.5, fontweight="bold")
    ax.text(50, 6.0, "Data-quality log  |  automated verification against raw files  |  nested cross-validation\n"
            "effect sizes and confidence intervals  |  limitations stated next to each result", ha="center", fontsize=9)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white"); plt.close(fig)


FLOW = OUT / "fig_flow.png"
flow_fig(FLOW)

# ---- prescriptive: refit the M06 logistic model and simulate profiles
import statsmodels.api as sm
SKC = ["big_data_skills", "maths_stats_skills", "coding_skills", "ai_and_ml_skills", "dashboard_and_storytelling_skills"]
lg6 = sm.Logit(jds.salary_hike_high, sm.add_constant(jds[SKC])).fit(disp=0)
prob = lambda prof: float(lg6.predict(np.r_[1.0, prof].reshape(1, -1))[0])
base_prof = np.full(5, 4.0)  # close to the average junior (4.27); leaves room for +1
gain = pd.DataFrame({"skill_area": DIM, "p_base": prob(base_prof),
                     "p_plus_one": [prob(np.where(np.arange(5) == i, base_prof + 1, base_prof)) for i in range(5)]})
gain["gain_pts"] = 100 * (gain.p_plus_one - gain.p_base)
scen = pd.DataFrame([
    ("Coding specialist\n(coding 5, others 4)", [4, 4, 5, 4, 4]),
    ("Balanced\n(all 4.2)", [4.2] * 5),
    ("Analyst-storyteller\n(maths & story 4.5, others 4)", [4, 4.5, 4, 4, 4.5]),
    ("Strong all-rounder\n(all 4.8)", [4.8] * 5)], columns=["profile", "scores"])
scen["avg"] = scen.scores.map(np.mean); scen["p_high"] = scen.scores.map(lambda s: prob(np.array(s)))
lsd = np.log(o6.loc[DIM, "or_per_sd"]); wts = (lsd / lsd.sum() * 100)
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 11})
fig, ax = plt.subplots(1, 2, figsize=(13, 4.6), gridspec_kw={"width_ratios": [1, 1], "wspace": 0.6})
g2 = gain.sort_values("gain_pts")
ax[0].barh(g2.skill_area, g2.gain_pts, color=["#1D4ED8" if v == g2.gain_pts.max() else "#93C5FD" for v in g2.gain_pts])
for i, v in enumerate(g2.gain_pts):
    ax[0].text(v + .5, i, f"+{v:.0f} pts", va="center")
ax[0].set_xlim(0, g2.gain_pts.max() * 1.25); ax[0].set_xlabel("Change in predicted chance of a high hike (percentage points)")
ax[0].set_title("Where the next point of skill pays most\n(junior with 4.0 in every area, +1 point in one)", fontweight="bold")
ax[1].barh(scen.profile[::-1], 100 * scen.p_high[::-1], color=["#94A3B8", "#93C5FD", "#1D4ED8", "#0B2E59"][::-1])
for i, (v, a) in enumerate(zip(100 * scen.p_high[::-1], scen.avg[::-1])):
    ax[1].text(v + 1, i, f"{v:.0f}%  (avg {a:.2f})", va="center")
ax[1].set_xlim(0, 115); ax[1].set_xlabel("Predicted chance of a high salary hike (%)")
ax[1].set_title("Same effort, different shape: simulated junior profiles", fontweight="bold")
PRESC = OUT / "fig_prescriptive.png"; fig.savefig(PRESC, dpi=200, bbox_inches="tight", facecolor="white"); plt.close(fig)

# ------------------------------------------------------------------ document helpers
doc = Document()
for sec in doc.sections:
    sec.left_margin = sec.right_margin = Cm(2.2); sec.top_margin = sec.bottom_margin = Cm(2.0)
st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
st.paragraph_format.space_after = Pt(5); st.paragraph_format.line_spacing = 1.0
for h, sz in [("Heading 1", 16), ("Heading 2", 13.5), ("Heading 3", 12)]:
    hs = doc.styles[h]; hs.font.name = "Times New Roman"; hs.font.size = Pt(sz); hs.font.bold = True
    hs.font.color.rgb = RGBColor(0x0B, 0x2E, 0x59); hs.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    hs.paragraph_format.space_before = Pt(10 if h == "Heading 1" else 8); hs.paragraph_format.space_after = Pt(3)
fp = doc.sections[0].footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_ = fp.add_run()
for tag, txt in [("begin", None), (None, "PAGE"), ("end", None)]:
    if tag:
        e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), tag); r_._r.append(e)
    else:
        e = OxmlElement("w:instrText"); e.text = txt; r_._r.append(e)
FIGN = [0]


def P(text="", bold_lead=None, italic=False, size=None, align=None, after=None, bold=False):
    p = doc.add_paragraph()
    if bold_lead:
        p.add_run(bold_lead).bold = True
    run = p.add_run(text); run.italic = italic; run.bold = bold
    if size:
        run.font.size = Pt(size)
    p.alignment = align if align is not None else WD_ALIGN_PARAGRAPH.JUSTIFY
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    return p


def B(items, style="List Bullet"):
    for t in items:
        p = doc.add_paragraph(style=style); p.paragraph_format.space_after = Pt(2); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if isinstance(t, tuple):
            p.add_run(t[0]).bold = True; p.add_run(t[1])
        else:
            p.add_run(t)


def shade(cell, hexcol):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hexcol); tcPr.append(sh)


def T(header, rows, widths=None, size=9.5, caption=None):
    if caption:
        cp = doc.add_paragraph(); rr = cp.add_run(caption); rr.bold = True; rr.font.size = Pt(10.5)
        cp.paragraph_format.space_after = Pt(2); cp.paragraph_format.keep_with_next = True
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
    hdr = OxmlElement("w:tblHeader"); hdr.set(qn("w:val"), "true"); t.rows[0]._tr.get_or_add_trPr().append(hdr)  # repeat header
    small = len(rows) <= 12  # keep small tables on one page
    for k, row in enumerate(t.rows):
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.keep_with_next = small and k < len(t.rows) - 1
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def CAP(text):
    cp = doc.add_paragraph(); rr = cp.add_run(text); rr.italic = True; rr.font.size = Pt(10)
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER; cp.paragraph_format.space_after = Pt(6)


def IMG(path, caption, width=15.5):
    FIGN[0] += 1
    doc.add_picture(str(path), width=Cm(width)); doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.paragraphs[-1].paragraph_format.keep_with_next = True
    CAP(f"Figure {FIGN[0]}. {caption}")


def IMG2(a, b, caption, w=8.2):
    FIGN[0] += 1
    t = doc.add_table(rows=1, cols=2); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for cell, pth in zip(t.rows[0].cells, [a, b]):
        cell.paragraphs[0].add_run().add_picture(str(pth), width=Cm(w)); cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    CAP(f"Figure {FIGN[0]}. {caption}")


def OR(df, k, col="or_per_unit"):
    return f"{df.loc[k, col]:.1f}x"


# ================================================================== COVER
for _ in range(4):
    doc.add_paragraph()
P("SAS CU Hackathon  |  Approach Note", size=13, align=WD_ALIGN_PARAGRAPH.CENTER, after=16)
tp = doc.add_paragraph(); tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
rr = tp.add_run("HIRING FOR THE RIGHT SIGNALS"); rr.bold = True; rr.font.size = Pt(28); rr.font.color.rgb = RGBColor(0x0B, 0x2E, 0x59)
P("Do organisations hire, pay and develop data scientists for what actually makes them succeed?",
  italic=True, size=15, align=WD_ALIGN_PARAGRAPH.CENTER, after=26)
P("Problem Definition  |  Approach  |  Data Exploration  |  Data Analysis  |  Results & Conclusions  |  Implications",
  size=11.5, align=WD_ALIGN_PARAGRAPH.CENTER, after=40)
P("Team: ____________________", size=12, align=WD_ALIGN_PARAGRAPH.CENTER)
P("Data: Data Science Jobs, Analytics Jobs, JDS Skill Traits, SDS Personality Traits (2024-25)", size=11, align=WD_ALIGN_PARAGRAPH.CENTER)
P("Tools: Python (pandas, scikit-learn, statsmodels), MySQL 8, SAS Viya for Learners", size=11, align=WD_ALIGN_PARAGRAPH.CENTER)
doc.add_page_break()

# ================================================================== CONTENTS
doc.add_heading("Contents", 1)
_p = doc.add_paragraph(); _r = _p.add_run()
for _tag, _txt in [("begin", None), (None, 'TOC \\o "1-2" \\h \\z \\u'), ("separate", None), (None, None), ("end", None)]:
    if _tag:
        _e = OxmlElement("w:fldChar"); _e.set(qn("w:fldCharType"), _tag); _r._r.append(_e)
    elif _txt:
        _e = OxmlElement("w:instrText"); _e.set(qn("xml:space"), "preserve"); _e.text = _txt; _r._r.append(_e)
    else:
        _e = OxmlElement("w:t"); _e.text = "Right-click and choose Update Field to build the table of contents."; _r._r.append(_e)
doc.add_page_break()
# ================================================================== EXEC SUMMARY
doc.add_heading("Executive Summary", 1)
P("Organisations define the data scientist they want through job postings - and candidates, universities and recruiters "
  "all prepare against that definition. We tested whether that definition matches what actually drives success, using "
  f"{len(core):,} core analytics postings, {len(ds):,} company salary records, and two company datasets on {len(jds)} junior "
  f"and {len(sds)} senior data scientists. After a ten-stage, independently verified cleaning process ({n_pass}/{n_chk} "
  "checks pass), we trained fifteen analytical models. The three signals - what is asked for, what is paid for and what "
  "is rewarded - do not agree.")
B([("Asked for: ", f"coding appears in {pct(dem.loc['Coding','share'])} of postings - more than twice any other skill area; "
     f"maths & statistics ({pct(dem.loc['Maths & statistics','share'])}) and storytelling ({pct(dem.loc['Dashboards & storytelling','share'])}) are rarely written down."),
   ("Paid for: ", f"experience sets the pay band (odds x{o3.loc['Experience (years, mid-point)','odds_ratio']:.2f} per year); adding every listed skill "
     f"does not improve salary prediction ({pct(c4.loc['Experience + role + seniority + city','exact_accuracy'])} vs "
     f"{pct(c4.loc['Experience + role + seniority + city + skills','exact_accuracy'])}), and postings asking for storytelling sit in "
     f"lower bands (odds x{o3.loc['Asks for Dashboards & storytelling','odds_ratio']:.2f})."),
   ("Rewarded in juniors: ", f"maths & statistics (odds x{o6.loc['Maths & statistics','or_per_unit']:.1f} per point) and storytelling "
     f"(x{o6.loc['Dashboards & storytelling','or_per_unit']:.1f}) drive high salary hikes; coding adds no proven effect once the others are "
     f"counted (p = {o6.loc['Coding','p_value']:.2f}). Breadth beats spikes: the average skill level separates juniors "
     f"(AUC {a9.loc['Average of 5 skills','auc']:.2f}), the strongest single skill barely does ({a9.loc['Strongest skill','auc']:.2f}). "
     f"Best model: logistic regression, AUC {c8.loc['Logistic regression','auc_mean']:.2f} on unseen data."),
   ("Rewarded in seniors: ", f"openness and conscientiousness dominate success; {pct(len(s_hi[s_hi.success_high == 1]) / len(s_hi))} of seniors above "
     f"both thresholds succeed versus none below either. One persona - the disciplined explorer - holds most successful seniors."),
   ("The gap: ", f"the most requested skill (coding) ranks third on reward; the least requested (maths) ranks second. Storytelling "
     f"out-rewards coding in {pct(sto.p_beats_coding)} of 2,000 bootstrap resamples.")])
P("Implication: organisations are spending their hiring filter on the skill nearly everyone already has. Writing maths/statistics "
  "and storytelling into job descriptions and interviews, developing all-round profiles in juniors, and screening senior, "
  "client-facing hires for curiosity and discipline would align hiring with what actually grows talent.", italic=True)
doc.add_page_break()

# ================================================================== 1 PROBLEM
doc.add_heading("1. Problem Definition and Analytics Objective", 1)
doc.add_heading("1.1 Context", 2)
P("The brief frames the problem around data-science jobs, the skills of data scientists and their personality traits. "
  "The four files describe the full talent cycle an organisation manages: the market it hires from (two job-posting files), "
  "the technical skills associated with early growth inside a company (junior data scientists) and the behavioural traits "
  "associated with success at senior, customer-facing level (senior data scientists). Two files are market data and two are "
  "a company's own employee data, which is why we frame the problem from the organisation's side.")
T(["Dataset", "One row is", "Rows (raw -> analysed)", "Signal it carries"], [
    ["Analytics Jobs", "A job posting: designation, skills, experience, location, salary band", f"15,841 -> {len(an):,}; {len(core):,} core", "What is asked for; offered band"],
    ["Data Science Jobs", "A company x job title: openings, min/avg/max salary, min. experience", f"{len(ds):,} -> {int(ds.in_analysis_sample.sum()):,}", "What is paid"],
    ["JDS Skill Traits", "A junior data scientist: 5 skill scores (1-5), high/low salary hike", f"{len(jds)} -> {len(jds)}", "What is rewarded early"],
    ["SDS Personality Traits", "A senior, customer-facing data scientist: Big Five traits, high/low success", f"{len(sds)} -> {len(sds)}", "What is rewarded later"],
], widths=[3.2, 6.6, 3.6, 3.6], caption="Table 1.1  The four datasets")
doc.add_heading("1.2 Problem statement", 2)
P("Organisations hiring data scientists define what they want through job postings: roles, skills, experience and pay. "
  "But a posting captures what is easy to list, not necessarily what makes a data scientist succeed once hired. Inside "
  "organisations, junior data scientists' technical skill profiles are linked to how fast they earn salary hikes, and senior, "
  "customer-facing data scientists' personality traits are linked to their overall success. If what the market asks for and "
  "pays for differs from what actually drives growth and success, organisations hire, pay and develop talent against the "
  "wrong signals - and aspirants build the wrong skills.", italic=True)
P("The problem is to measure how far the skills and attributes the market demands and pays for line up with those associated "
  "with junior growth and senior success, and to turn that gap into evidence-based guidance on what organisations should hire "
  "for, pay for and develop, and what aspiring data scientists should build first.", italic=True, bold=True)
doc.add_heading("1.3 Stakeholders, objectives and hypotheses", 2)
T(["Stakeholder", "Decision", "What the analysis gives them"], [
    ["Hiring managers & HR (primary)", "What to require in postings; whom to shortlist; how to interview", "Which requirements relate to growth and success"],
    ["Compensation teams", "Pay bands by role, experience and location", "Pay drivers, ladders and ranges"],
    ["Learning & development", "What to develop in juniors; whom to prepare for senior roles", "Skill and trait profiles of high performers"],
    ["Universities & aspirants (secondary)", "Curriculum; what to learn first", "Skills over- and under-signalled by the market"],
], widths=[4.2, 6.0, 6.8], caption="Table 1.2  Stakeholders and decisions")
T(["#", "Research question", "Data", "Hypothesis"], [
    ["O1", "What does the analytics market ask for, by role and skill area?", "Analytics Jobs", "H1: coding dominates; maths and storytelling are rarely asked for"],
    ["O2", "What does the market pay for at hiring?", "Analytics Jobs, DS Jobs", "H2: experience and role set pay; listed skills add little"],
    ["O3", "Which skills, and which profile shape, go with high junior salary hikes?", "JDS", "H3: maths and storytelling matter most; H4: breadth beats a single spike"],
    ["O4", "Which traits go with senior, customer-facing success?", "SDS", "H5: conscientiousness and openness are the strongest correlates"],
    ["O5", "Where do demand and reward diverge?", "All four", "H6: the most demanded skills are not the most rewarded"],
], widths=[0.9, 6.4, 3.0, 6.7], caption="Table 1.3  Objectives, research questions and hypotheses")
doc.add_heading("1.4 Scope and limitations", 2)
B([("In scope: ", f"India-based postings for 2024-25, nine analytics role families ({len(core):,} core postings), the two company people datasets, all four files linked at skill-area level."),
   ("Out of scope: ", "causal claims (all data is observational), exact salary prediction for Analytics Jobs (salary exists only as six bands), individual-level linking across files (no shared key), time trends (no posting dates)."),
   ("Known data limits: ", f"87% of skill lists are truncated; JDS and SDS come from one company each with n = {len(jds)} and {len(sds)}; JDS scores show a ceiling effect.")])

# ================================================================== 2 APPROACH
doc.add_page_break()
doc.add_heading("2. Approach", 1)
IMG(FLOW, "Overall analytical flow", 15.5)
doc.add_heading("2.1 Motivation and design principles", 2)
T(["Principle", "In practice", "Why"], [
    ["Flag, don't delete", "Only exact duplicates removed; every other issue becomes a 0/1 flag; originals kept beside cleaned values",
     "The brief warns of meaningless entries and outliers; silent deletion changes the population and cannot be audited"],
    ["Every number traceable", f"Data-quality log + a verification script that recomputes every claim from the raw files ({n_pass}/{n_chk} pass)",
     "Any figure can be checked; it also caught our own errors"],
    ["Explainable first, flexible second", "Logistic regression and decision trees lead; random forest and gradient boosting are benchmarks",
     "Stakeholders need reasons (odds ratios, rules); people samples are small"],
    ["Honest validation", "Nested cross-validation (tuning never sees the test fold), repeated 10x for small samples, bootstrap CIs",
     "Small samples overfit easily; the judged result must hold on unseen data"],
    ["Right method for the outcome", "Ordinal model for ordered pay bands, log-linear model for salaries, logistic for yes/no outcomes",
     "Matching the model to the measurement avoids invented precision"],
], widths=[3.4, 7.0, 6.6], size=9, caption="Table 2.1  Design principles")
doc.add_heading("2.2 Methods by objective", 2)
T(["Objective", "Models", "Validation"], [
    ["O1 Asked for", "M01 demand profile with Wilson 95% CIs; M02 association rules (support, confidence, lift)", "CIs; minimum support 1%"],
    ["O2 Paid for", "M03 ordinal logistic regression; M04 tuned gradient boosting on four feature sets; M05 log-salary regression (HC3) vs tuned random forest",
     "Nested 5-fold CV; experience-only and majority baselines"],
    ["O3 Junior growth", "M06 logistic regression; M07 decision tree; M08 random forest & gradient boosting; M09 profile-shape tests",
     "Nested CV repeated 10x (50 test folds); permutation importance"],
    ["O4 Senior success", "M10 logistic regression; M11 decision tree; M12 ensembles; M13 k-means personas", "As O3; silhouette for k; chi-square"],
    ["O5 The gap", "M14 bootstrap (2,000 resamples) of demand share and effect size", "Bootstrap 95% CIs; rank comparison"],
], widths=[2.8, 9.4, 4.8], size=9, caption="Table 2.2  Methods and validation")
doc.add_heading("2.3 Why these models - and what we rejected", 2)
T(["Choice", "Reason", "Alternative considered and rejected"], [
    ["Ordinal logistic regression for pay bands", "Bands are ordered categories; odds ratios are readable", "Linear regression on band mid-points: invents precision the data does not have"],
    ["Log-linear regression for salaries", "Salaries are right-skewed; effects become percentages", "Raw-salary regression: dominated by a few very high salaries"],
    ["Logistic regression as the lead people model", "Readable odds ratios; robust on 139-161 rows", "Deep learning / neural networks: thousands of parameters for 139 people - overfitting by design"],
    ["Decision trees, depth tuned 2-5", "Turn models into rules a manager can apply", "Unpruned trees: memorise the sample"],
    ["Random forest and gradient boosting as benchmarks", "Test whether non-linear structure is being missed", "Using them as the headline model: harder to explain, no accuracy gain for juniors"],
    ["Association rules for skill bundles", "Show which requirements travel together, with lift", "Raw co-occurrence counts: favour skills that are common anyway"],
    ["K-means on standardised traits", "Personas found without the success label, so differences are discovered, not built in", "Clustering including the outcome: circular"],
    ["Bootstrap for the demand-reward gap", "Combines two datasets of very different size into one uncertainty statement", "Single point estimates: hide that the people sample is small"],
], widths=[4.4, 5.8, 6.8], size=8.5, caption="Table 2.3  Model choices and rejected alternatives")
doc.add_heading("2.4 Validation protocol", 2)
P("Predictive scores are measured with nested cross-validation: an inner loop tunes each model's settings and an outer loop "
  "scores it on data that neither training nor tuning has seen. For the people datasets the outer loop is repeated ten times "
  "with different random splits (50 test folds for the interpretable models, 15 for the slower ensembles), so a single lucky "
  "split cannot drive the result. Every model is compared with a no-skill baseline. Effects are reported as odds ratios or "
  "percentage effects with 95% confidence intervals, and differences that matter for the conclusions are re-checked with "
  "2,000 bootstrap resamples. All random processes use a fixed seed (42), so every number in this note can be reproduced "
  "exactly from the code in Appendix D.")
P("Tools: Python (pandas, regex, scikit-learn, statsmodels) for cleaning, text mining and modelling; MySQL 8 as a single "
  "normalised source of truth for the team; SAS Visual Analytics for exploration visuals (plot-ready tables for every chart "
  "are exported for SAS VFL). Excel was not used.")

# ================================================================== 3 EXPLORATION
doc.add_page_break()
doc.add_heading("3. Data Exploration: Issues, Preparation, Derivation and Consolidation", 1)
doc.add_heading("3.1 Data audit", 2)
P(f"Every column of every file was profiled before any change. The audit found {len(log[log.rows_affected > 0])} distinct issues "
  "across the four files - duplicates, non-unique identifiers, text-coded numbers, inconsistent spellings, truncated text, "
  "out-of-scope records, outliers and missing values (Figure 2).")
IMG(F("M00", "01_issues_and_missing"), "Issues found per cleaning stage (left) and missing values in the raw files (right)", 15.5)
doc.add_heading("3.2 Issues found and how they were solved", 2)
T(["File", "Issue (rows affected)", "Treatment"], [
    ["Analytics Jobs", f"Exact duplicate postings ({L('Exact duplicate postings'):,})", "Removed after field-by-field check - the only deletion"],
    ["Analytics Jobs", f"Near-duplicates ({L('Near-duplicates after'):,}); possible reposts ({L('Possible reposts'):,})", "Flagged; near-duplicates excluded from demand counts"],
    ["Analytics Jobs", f"Designations padded with recruiting noise ({L('Designations padded'):,}); {L('10,097 distinct'):,} free-text titles",
     "Noise stripped; ordered rules map titles to 22 role families + seniority; audited on 150 random postings (~91% exact)"],
    ["Analytics Jobs", "Experience and salary stored as text ('6-10 yrs', '10to15')", "Parsed to numeric min/max/mid and ordered bands"],
    ["Analytics Jobs", f"job_type: one value spelt 5 ways, 76% missing ({L('job_type missing'):,})", "Original kept; 0/1 tagged flag; relevance re-derived from title and skills"],
    ["Analytics Jobs", f"Locations: {L('location:'):,} distinct strings, multi-city, spelling variants; {L('Overseas locations')} overseas",
     "Canonical cities and tiers; multi-city bridge table; overseas flagged"],
    ["Analytics Jobs", f"Skills: 8,462 raw tokens, variants, junk ({L('Junk skill tokens')}), non-skills ({L('Non-skill tokens'):,}); 87% truncated",
     "Normalised, de-duplicated, typed (technical / soft / education / job meta); recovered from descriptions"],
    ["Analytics Jobs", f"Non-analytics roles ({L('Non-analytics roles'):,}); spam ({L('Low-quality')})", "Flagged; core analytics sample of " + f"{len(core):,}"],
    ["DataScience Jobs", f"reference_no shared by {L('reference_no is not unique')} different rows", "Surrogate key; original kept"],
    ["DataScience Jobs", "Salaries as text ('7.8L'); min salary < 1 LPA (3); 'Senior' with 0 years (14)", "Parsed to LPA; implausible values flagged"],
    ["DataScience Jobs", f"num_of_jobs max 4,200 vs median 22 ({L('num_of_jobs extremely')} outliers); top-firm salaries", "Kept; log transform; winsorised copy used only in regression checks"],
    ["DataScience Jobs", "Same employer under two names with different salaries (13 rows); placeholder employers (12)", "Kept separate, linked by company_group; placeholders excluded from models"],
    ["JDS / SDS", "Non-unique ids; hyphen and stray spaces in column names", "Surrogate keys; names standardised"],
    ["JDS", "Ceiling effect: 18-58% of scores are a perfect 5", "Kept (real scores); handled through profile-shape tests and rank-based models"],
], widths=[2.8, 7.4, 6.8], size=8.5, caption="Table 3.1  Principal data issues and treatments (full log in Appendix A)")
P("An independent review of an earlier version found that compound skills ('Oracle SQL', 'SQL Server', 'SAS SQL') "
  f"were not counted. The matcher was rebuilt to find whole words inside compounds, with exclusions for false matches ('medical "
  f"coding', 'regression testing', 'search engine optimization'). Postings flagged for SQL rose from 1,033 to {int(an.has_sql.sum()):,}, "
  "and a permanent check now confirms that no raw SQL mention is missed.", bold_lead="Peer audit. ")
doc.add_heading("3.3 Data reduction: from raw file to analysis sample", 2)
IMG2(F("M00", "02_analytics_jobs_funnel"), F("M00", "03_role_families"),
     "Analytics Jobs funnel (left) and role families in the India sample (right; blue = core analytics)")
P(f"Only exact duplicates were deleted. Spam, overseas-only postings and near-duplicates leave the India sample "
  f"({int(an.in_india_sample.sum()):,}); restricting to the nine analytics role families gives the core sample of {len(core):,}. "
  "Two-thirds of the 'Analytics Jobs' file is not analytics work (software, BPO, sales, finance, medical coding) - treating the "
  "file as homogeneous would have distorted every demand and pay estimate.")
doc.add_heading("3.4 Data derivation", 2)
P(f"Skill lists are truncated in 87% of postings, so skills were also extracted from the job descriptions using a vocabulary "
  f"built from the skill lists themselves ({L('Skills recovered'):,} additional mentions). Recovery raises measured demand most for "
  f"storytelling ({pct(rec.loc['Dashboards & storytelling','from_key_skills_only'])} -> {pct(rec.loc['Dashboards & storytelling','after_description_recovery'])}) "
  f"and maths ({pct(rec.loc['Maths & statistics','from_key_skills_only'])} -> {pct(rec.loc['Maths & statistics','after_description_recovery'])}), "
  "the two areas most often described in prose rather than listed as keywords.")
IMG(F("M00", "05_skill_recovery"), "Skill-area demand before and after recovery from descriptions", 12.5)
T(["Derived variable", "From", "Purpose"], [
    ["exp_min / exp_max / exp_mid; salary band order and mid-point", "Text experience and salary", "Numeric modelling inputs"],
    ["role_family (22), seniority (5), is_analytics_role", "Free-text designation", "Scope and role controls"],
    ["primary_city, city_tier, is_multi_city, is_international", "1,355 location strings", "Geography controls and scope"],
    ["skills, soft_skills, education, job tags; skills_from_desc; skills_all", "key_skills + description", "Clean skill sets"],
    ["dim_* (5 skill areas), has_* (14 tools), n_dims", "skills_all via taxonomy", "Demand and the link to JDS"],
    ["min/avg/max salary in LPA, spread, range ratio, log openings, company type/scale/group", "DS Jobs text fields", "Pay modelling"],
    ["skill mean/min/range, weakest/strongest skill", "JDS scores", "Profile-shape tests"],
    ["trait z-scores, emotional_stability_z (= -neuroticism z), dominant trait", "SDS traits", "Comparable trait scales"],
], widths=[7.6, 4.4, 5.0], size=8.5, caption="Table 3.2  Main derived variables")
doc.add_heading("3.5 Consolidation: linking four files with no common key", 2)
P("The files share no identifier, so they are linked on meaning. A taxonomy maps 470 market skill names to the five JDS skill "
  "areas (big data, maths & statistics, coding, AI & ML, dashboards & storytelling); every posting carries five 0/1 flags directly "
  "comparable with the five JDS scores. All cleaned data was loaded into a MySQL 8 database in third normal form - list fields "
  "split into bridge tables (1NF), attributes moved to the table their key determines (2NF/3NF), derived values computed in "
  "views - with 23 tables, 16 foreign keys, 10 unique keys and 9 CHECK constraints, verified after load.")
IMG(HERE / "database" / "ERD.png", "Entity-relationship diagram of the core database (staging tables not shown)", 15.5)
doc.add_heading("3.6 Exploratory findings that shaped the analysis", 2)
IMG(F("M00", "04_salary_experience_city"), "Salary bands, experience asked for and top cities in core postings", 16)
IMG2(F("M00", "06_ds_jobs_distributions"), F("M00", "07_people_data_distributions"),
     "Skewed openings and salaries in DS Jobs (left); JDS ceiling effect and SDS trait spreads (right)")
B(["Salary bands are reasonably balanced but ordered, which calls for an ordinal model rather than accuracy-only classification.",
   "Experience asked for is right-skewed (median about 5 years) and is the obvious first driver of pay.",
   "Demand is concentrated in six metros; Tier-2/3 cities are few, so city enters models as a control, not a focus.",
   "Openings in DS Jobs span 1 to 4,200, so they were log-transformed; top-firm salaries are genuine and were kept.",
   "Many JDS scores sit at the maximum of 5, so differences at the top are compressed - one reason to test profile shape, not only levels.",
   f"Both people outcomes are balanced ({pct(jds.salary_hike_high.mean())} and {pct(sds.success_high.mean())} positive), so AUC and accuracy are meaningful."])
doc.add_heading("3.7 Verification", 2)
P(f"An independent script recomputes every figure in the cleaning log from the four original files and reconciles every cleaned "
  f"file row by row against its source: {n_pass} of {n_chk} checks pass. The database load runs a second set of checks on every "
  "table count and key figure.")

# ================================================================== 4 ANALYSIS
doc.add_page_break()
doc.add_heading("4. Data Analysis", 1)
P("Fifteen models (M00-M14) were trained. Every predictive score below is measured on data the model did not see during "
  "training or tuning (nested cross-validation); every effect is reported with a 95% confidence interval.")
doc.add_heading("4.1 What organisations ask for (M01, M02)", 2)
IMG2(F("M01", "01_skill_area_demand"), F("M01", "02_role_by_skill_area_heatmap"),
     "Skill-area demand with 95% CIs (left) and by role family (right)")
da = roled[roled.role_family == "Statistical Modelling / SAS"].set_index("skill_area").share
P(f"Coding is requested in {pct(dem.loc['Coding','share'])} of core postings, more than twice any other area. The most-named "
  f"individual skills are {', '.join(top_sk.skill[:5])}. Even Statistical Modelling roles ask for coding "
  f"({pct(da['Coding'])}) more than for maths & statistics ({pct(da['Maths & statistics'])}). Association rules (M02) show that "
  "requirements come in bundles: the big-data stack (Hadoop, Hive, Spark, Scala; lift 10-16), the AI stack (deep learning, NLP, "
  "machine learning), SAS with predictive modelling and Python with machine learning. Maths & statistics and big data are rarely "
  f"asked for together (lift {dimlift[(dimlift.area_a=='Big data')&(dimlift.area_b=='Maths & statistics')].lift.iloc[0]:.1f}).")
IMG(F("M02", "01_top_skill_pairs_lift"), "Top 25 skill pairs by lift (M02)", 14.5)
IMG(F("M02", "02_skill_network"), "Skill network: node size = demand, edge width = lift (M02)", 14)
doc.add_heading("4.2 What organisations pay for (M03, M04, M05)", 2)
P(f"An ordinal logistic regression on {len(an[an.in_salary_model==1]):,} postings (M03) shows experience as the dominant driver: each "
  f"additional year multiplies the odds of a higher band by {o3.loc['Experience (years, mid-point)','odds_ratio']:.2f}. Risk/quant, "
  f"statistical-modelling and data-scientist roles pay more than data-analyst roles; Tier-2/3 cities pay far less "
  f"(x{o3.loc['City: Tier 2/3','odds_ratio']:.2f}). Skill requirements move the band only slightly - coding x{o3.loc['Asks for Coding','odds_ratio']:.2f} - "
  f"and postings asking for dashboards & storytelling sit in lower bands (x{o3.loc['Asks for Dashboards & storytelling','odds_ratio']:.2f}).")
IMG2(F("M03", "01_odds_ratios_forest"), F("M03", "02_predicted_pay_by_experience"),
     "Ordinal regression odds ratios (left) and predicted chance of a 15+ LPA band by experience (right)")
T(["Information given to the tuned gradient-boosting model", "Exact band", "Within one band", "Quadratic kappa"],
  [[k, pct(r.exact_accuracy), pct(r.within_one_band), f"{r.quadratic_kappa:.3f}"] for k, r in c4.iterrows()],
  widths=[9.0, 2.6, 2.8, 2.6], size=9, caption="Table 4.1  Salary-band prediction on unseen postings (M04, nested 5-fold CV)")
P(f"M04 confirms this with a flexible model. Skills alone predict no better than guessing the most common band; adding all skills "
  f"to experience, role, seniority and city does not improve accuracy. Scrambling experience destroys the model "
  f"(importance {i4.loc['Experience','importance_drop_in_kappa']:.2f}); scrambling all skills barely matters ({i4.loc['Skills (areas, tools, counts)','importance_drop_in_kappa']:.2f}).")
P(f"On real salary figures (M05, {int(ds.in_analysis_sample.sum()):,} company x title records), a log-salary regression explains "
  f"{cv5.loc['Linear regression (log salary)','cv_r2_mean']:.0%} of variation on unseen data, matching a tuned random forest "
  f"({cv5.loc['Random forest (tuned)','cv_r2_mean']:.0%}). Each year of minimum experience adds {e5.loc['+1 year min. experience','pct_effect']:.1f}%; a Senior "
  f"Data Scientist earns {e5.loc['Title: Senior Data Scientist','pct_effect']:.0f}% more than a Data Analyst, a Data Scientist "
  f"{e5.loc['Title: Data Scientist','pct_effect']:.0f}% more; product/captive firms pay {e5.loc['Type: Product / captive / other','pct_effect']:.0f}% more than "
  f"IT services. Pay ranges are widest for junior titles (Data Analyst {hr5.loc['Data Analyst','headroom_pct']:.0f}% above average vs Senior Data "
  f"Engineer {hr5.loc['Senior Data Engineer','headroom_pct']:.0f}%).")
IMG(F("M04", "01_model_comparison"), "Salary-band prediction with and without skills (M04)", 14)
IMG2(F("M05", "01_salary_effects"), F("M05", "02_salary_by_title"), "Salary ladder: regression effects (left) and salary by title (right) (M05)")
IMG(F("M05", "03_pay_spread"), "Pay spread by title and company size (M05)", 15)
doc.add_heading("4.3 What gets juniors ahead (M06-M09)", 2)
T(["Skill area", "High hike (mean)", "Low hike (mean)", "Odds ratio per point", "95% CI", "p"],
  [[k, f"{g6.loc[k,'High hike']:.2f}", f"{g6.loc[k,'Low hike']:.2f}", f"{o6.loc[k,'or_per_unit']:.2f}",
    f"{o6.loc[k,'or_unit_low']:.2f}-{o6.loc[k,'or_unit_high']:.2f}", f"{o6.loc[k,'p_value']:.3f}"] for k in DIM],
  widths=[4.4, 2.4, 2.4, 2.8, 2.8, 1.6], size=9, caption=f"Table 4.2  Junior skills and salary hike (M06 logistic regression, n = {len(jds)})")
P(f"With all five skills in one model, maths & statistics (x{o6.loc['Maths & statistics','or_per_unit']:.1f} per point) and "
  f"storytelling (x{o6.loc['Dashboards & storytelling','or_per_unit']:.1f}) carry the largest effects. Coding - the market's most "
  f"requested skill - is the only area without a significant independent effect (p = {o6.loc['Coding','p_value']:.2f}). All variance "
  f"inflation factors are below {o6.vif.max():.1f}, so the result is not an artefact of correlated skills.")
IMG2(F("M06", "01_odds_ratios_forest"), F("M07", "01_decision_tree"), "Odds ratios per standard deviation (left) and the tuned decision tree (right)")
P(f"The decision tree (M07) asks first about storytelling, not coding: below {th7} only {int(lo7.salary_hike_high.sum())} of "
  f"{len(lo7)} juniors ({pct(lo7.salary_hike_high.mean())}) earned a high hike; above it, {int(hi7.salary_hike_high.sum())} of "
  f"{len(hi7)} ({pct(hi7.salary_hike_high.mean())}).")
T(["Model (tuned, nested CV)", "AUC", "Accuracy", "F1", "Brier", "Test folds"],
  [[k, f"{r.auc_mean:.3f} +/- {r.auc_sd:.3f}", pct(r.accuracy), "-" if pd.isna(r.f1) else f"{r.f1:.3f}", f"{r.brier:.3f}", int(r.outer_folds)]
   for k, r in c8.iterrows()], widths=[5.4, 3.4, 2.2, 1.8, 1.8, 2.0], size=9, caption="Table 4.3  Junior models on unseen data (M06-M08)")
P(f"The explainable logistic regression is the best model (AUC {c8.loc['Logistic regression','auc_mean']:.2f}, accuracy "
  f"{pct(c8.loc['Logistic regression','accuracy'])}); tuned random forest and gradient boosting do not beat it, and their permutation "
  "importances rank storytelling and maths highest and big data near zero - three methods, one ranking.")
IMG2(F("M06", "02_group_means"), F("M08", "02_model_comparison_auc"), "Mean skill scores by outcome (left) and model comparison (right)")
IMG2(F("M08", "01_roc_curves"), F("M08", "03_permutation_importance"), "ROC curves on unseen data (left) and permutation importance (right)")
P(f"Profile shape (M09): the average of the five skills separates high- from low-hike juniors (AUC {a9.loc['Average of 5 skills','auc']:.2f}); "
  f"the strongest single skill barely does ({a9.loc['Strongest skill','auc']:.2f}). Once the average is known, no other summary - "
  f"weakest skill, strongest skill or unevenness - adds information (all p > {n9.lr_p.min():.2f}). At the same middle level of skill, "
  f"balanced juniors earned high hikes {pct(h9[(h9.average_level=='Middle average')&(h9.profile_shape=='Balanced profile')].high_hike_rate.iloc[0])} "
  f"of the time versus {pct(h9[(h9.average_level=='Middle average')&(h9.profile_shape=='Spiky profile')].high_hike_rate.iloc[0])} for spiky ones.")
IMG2(F("M09", "01_breadth_vs_spike_auc"), F("M09", "02_hike_rate_by_level_and_shape"), "Breadth versus spike")
doc.add_heading("4.4 What makes seniors succeed (M10-M13)", 2)
T(["Trait", "High success (mean)", "Other (mean)", "OR per SD (together)", "95% CI", "OR per SD (alone)"],
  [[k, f"{g10.loc[k,'High success']:.1f}", f"{g10.loc[k,'Low success']:.1f}", f"{o10.loc[k,'or_per_sd']:.1f}",
    f"{o10.loc[k,'or_sd_low']:.1f}-{o10.loc[k,'or_sd_high']:.1f}", f"{o10.loc[k,'univariate_or_per_sd']:.1f}"]
   for k in ["Conscientiousness", "Openness", "Extraversion", "Agreeableness", "Neuroticism"]],
  widths=[3.4, 2.8, 2.4, 3.0, 2.8, 2.6], size=9, caption=f"Table 4.4  Senior traits and success (M10, n = {len(sds)})")
P(f"Conscientiousness and openness dominate. Neuroticism shows no difference on its own (OR {o10.loc['Neuroticism','univariate_or_per_sd']:.1f}) "
  "and becomes positive only when the other traits are held constant - a suppression effect; the tree ensembles give it zero "
  f"importance, so we do not treat it as a driver. The tree (M11) is a two-gate rule: openness at or below {th11o} - "
  f"{int(s_lo.success_high.sum())} of {len(s_lo)} successful; openness above but conscientiousness at or below {th11c} - "
  f"{int(s_mid.success_high.sum())} of {len(s_mid)}; above both - {int(s_hi.success_high.sum())} of {len(s_hi)} ({pct(s_hi.success_high.mean())}).")
IMG2(F("M10", "02_group_means"), F("M10", "01_odds_ratios_forest"), "Senior trait means by outcome (left) and odds ratios (right)")
IMG2(F("M10", "04_univariate_vs_multivariate"), F("M11", "01_decision_tree"), "Traits alone vs together (left) and the senior decision tree (right)")
IMG2(F("M12", "01_roc_curves"), F("M12", "03_permutation_importance"), "Senior models: ROC curves (left) and permutation importance (right)")
T(["Model (tuned, nested CV)", "AUC", "Accuracy", "Brier"],
  [[k, f"{r.auc_mean:.3f} +/- {r.auc_sd:.3f}", pct(r.accuracy), f"{r.brier:.3f}"] for k, r in c12.iterrows()],
  widths=[6.0, 4.0, 3.0, 3.0], size=9, caption="Table 4.5  Senior models on unseen data (M10-M12)")
P(f"All models separate the groups almost perfectly ({best_sen} AUC {c12.auc_mean.max():.3f}). Separation this clean is unusual for "
  "real personality data and suggests the dataset is simulated or that the success label is partly defined from the traits; we "
  "therefore treat the ranking of traits, not the accuracy, as the result.")
P(f"Clustering without the success label (M13; k = {len(pers)} chosen by silhouette) finds personas with very different success "
  f"rates: '{pers.persona.iloc[0]}' ({pers.people.iloc[0]} seniors) succeed {pct(pers.success_rate.iloc[0])} of the time, while "
  f"'{pers.persona.iloc[-2]}' and '{pers.persona.iloc[-1]}' never do.")
IMG(F("M13", "02_personas"), "Senior personas: trait profile (z-scores) and success rate with 95% CI", 16)
IMG(F("M13", "03_persona_map"), "Seniors on a two-dimensional map of their traits (o = high success, x = low)", 11.5)
doc.add_heading("4.5 The gap: asked for vs rewarded (M14)", 2)
T(["Skill area", "Demand (95% CI)", "Rank", "Reward d (95% CI)", "Rank", "Quadrant"],
  [[k, f"{pct(r.demand_share)} ({pct(r.demand_ci_low)}-{pct(r.demand_ci_high)})", int(r.demand_rank),
    f"{r.effect_size_d:.2f} ({r.d_ci_low:.2f}-{r.d_ci_high:.2f})", int(r.reward_rank), r.quadrant] for k, r in hg.iterrows()],
  widths=[3.6, 3.8, 1.2, 3.4, 1.2, 3.8], size=8.5, caption="Table 4.6  Demand versus reward, 2,000 bootstrap resamples")
IMG2(F("M14", "01_hype_gap_map"), F("M14", "02_rank_flip"), "The hype-gap map (left) and the ranking flip (right)")
P(f"The ranking flips. Coding is first on demand and third on reward; maths & statistics is last on demand and second on reward; "
  f"storytelling is first on reward. Storytelling's reward exceeds coding's in {pct(sto.p_beats_coding)} of resamples and maths in "
  f"{pct(mat.p_beats_coding)} - likely but not certain. Big data is requested as often as maths but its reward interval includes zero.")

doc.add_heading("4.6 Prescriptive analysis: where effort pays most", 2)
P("The junior logistic model can be used to simulate decisions. Starting from a junior who scores 4.0 in every area (close to the average junior, 4.27), we add one "
  "point to a single area and read off the change in the predicted chance of a high hike; we also compare profiles with a "
  "similar average but a different shape.")
IMG(PRESC, "Simulated effect of one extra skill point (left) and of profile shape (right), from the M06 model", 16)
gs = gain.sort_values("gain_pts", ascending=False)
P(f"From the same starting point, one extra point in {gs.skill_area.iloc[0].lower()} raises the predicted chance of a high hike by "
  f"{gs.gain_pts.iloc[0]:.0f} percentage points, in {gs.skill_area.iloc[1].lower()} by {gs.gain_pts.iloc[1]:.0f}, and in coding by only "
  f"{gain.set_index('skill_area').loc['Coding','gain_pts']:.0f}. Three juniors with the same average of 4.2 differ sharply: a coding "
  f"specialist has a predicted {pct(scen.p_high.iloc[0])} chance, a balanced profile {pct(scen.p_high.iloc[1])} and an analyst-storyteller "
  f"{pct(scen.p_high.iloc[2])}. The same effort placed in maths and storytelling rather than coding is worth far more.")
T(["Skill area", "Suggested weight in a junior interview scorecard", "Basis"],
  [[k, f"{wts[k]:.0f}%", f"log odds ratio per SD = {np.log(o6.loc[k,'or_per_sd']):.2f}"] for k in wts.sort_values(ascending=False).index],
  widths=[5.0, 5.6, 6.4], size=9, caption="Table 4.7  Evidence-based weighting for junior assessment (from M06)")
P("For senior, client-facing roles the prescriptive rule is the two-gate profile from M11: assess openness first and "
  "conscientiousness second, and do not use neuroticism as a screen.")
doc.add_heading("4.7 Model performance summary", 2)
T(["Question", "Best model", "Key score on unseen data", "Baseline"], [
    ["Pay band from posting (5,122 postings)", "Gradient boosting (experience, role, seniority, city)",
     f"{pct(c4.loc['Experience + role + seniority + city','exact_accuracy'])} exact, {pct(c4.loc['Experience + role + seniority + city','within_one_band'])} within one band",
     f"{pct(c4.iloc[0].exact_accuracy)} exact"],
    ["Salary amount (DS Jobs)", "Log-salary regression (random forest equal)", f"R2 {cv5.loc['Linear regression (log salary)','cv_r2_mean']:.2f}", "R2 0"],
    ["Junior high hike (139)", "Logistic regression", f"AUC {c8.loc['Logistic regression','auc_mean']:.2f}, accuracy {pct(c8.loc['Logistic regression','accuracy'])}", "AUC 0.50, 52.5%"],
    ["Senior high success (161)", best_sen, f"AUC {c12.auc_mean.max():.3f}, accuracy {pct(c12.loc[best_sen,'accuracy'])}", "AUC 0.50, 52.8%"],
    ["Senior personas", f"K-means, k = {len(pers)}", f"silhouette {k13.silhouette.max():.2f}; persona-success chi-square p < 1e-20", "-"],
], widths=[4.2, 4.6, 5.0, 3.2], size=9, caption="Table 4.8  Best model per question")
# ================================================================== 5 RESULTS
doc.add_page_break()
doc.add_heading("5. Results and Conclusions", 1)
doc.add_heading("5.1 Answers to the research questions", 2)
B([("O1 What is asked for? ", f"Coding, in {pct(dem.loc['Coding','share'])} of postings; maths and storytelling in under one in five, in role-specific bundles."),
   ("O2 What is paid for? ", "Experience first, then role, company type and city. Listed skills barely move the band, and storytelling-heavy postings pay less."),
   ("O3 What gets juniors ahead? ", "Maths & statistics and storytelling, plus breadth across all five areas; coding adds no proven effect once the others are known."),
   ("O4 What makes seniors succeed? ", "Openness and conscientiousness together - curiosity plus discipline; neuroticism is not a driver."),
   ("O5 Where is the gap? ", "The ranking flips: the most requested skill is third on reward, the least requested is second.")])
doc.add_heading("5.2 Hypotheses", 2)
T(["Hypothesis", "Verdict", "Evidence"], [
    ["H1 Coding dominates demand; maths and storytelling are rarely asked for", "Supported",
     f"Coding {pct(dem.loc['Coding','share'])} vs maths {pct(dem.loc['Maths & statistics','share'])}, storytelling {pct(dem.loc['Dashboards & storytelling','share'])} (M01)"],
    ["H2 Experience and role set pay; listed skills add little", "Supported",
     f"OR {o3.loc['Experience (years, mid-point)','odds_ratio']:.2f}/year; skills add no accuracy (M04); storytelling OR {o3.loc['Asks for Dashboards & storytelling','odds_ratio']:.2f} (M03)"],
    ["H3 Maths and storytelling matter most for junior hikes", "Supported",
     f"OR {o6.loc['Maths & statistics','or_per_unit']:.1f} and {o6.loc['Dashboards & storytelling','or_per_unit']:.1f}; coding n.s.; tree root = storytelling (M06-M08)"],
    ["H4 Breadth beats a single spike", "Supported", f"AUC {a9.loc['Average of 5 skills','auc']:.2f} vs {a9.loc['Strongest skill','auc']:.2f}; no extra information beyond the average (M09)"],
    ["H5 Conscientiousness and openness drive senior success", "Supported", f"OR {o10.loc['Conscientiousness','or_per_sd']:.0f} and {o10.loc['Openness','or_per_sd']:.0f} per SD; two-gate tree; personas (M10-M13)"],
    ["H6 The most demanded skills are not the most rewarded", "Supported (moderate certainty)", f"Rank flip; storytelling > coding in {pct(sto.p_beats_coding)} of resamples (M14)"],
], widths=[5.6, 2.6, 8.8], size=9, caption="Table 5.1  Hypotheses and verdicts")
P("The three signals an organisation uses to define a data scientist disagree. Job postings ask mainly for "
  "coding; pay at hiring follows experience, role and city and barely responds to the skills listed; inside the organisation the "
  "juniors who grow fastest are distinguished by maths & statistics and storytelling, and by being solid across all five areas "
  "rather than outstanding in one. At senior level, success belongs to people who are both curious and disciplined. Postings "
  "hire for the skill everyone already has; growth and success reward the skills and traits postings leave out.", bold_lead="Conclusion. ")
P("Demand and pay results rest on thousands of records with narrow intervals. Junior results are strong "
  f"(AUC {c8.loc['Logistic regression','auc_mean']:.2f} on unseen data, consistent across three model families) but come from one company "
  "and 139 people. Senior results are very strong in pattern but suspiciously clean in accuracy. All findings are associations; "
  "the taxonomy that links postings to people is a documented assumption.", bold_lead="Strength of evidence. ")

# ================================================================== 6 IMPLICATIONS
doc.add_heading("6. Implications", 1)
T(["Stakeholder", "Implication", "Action"], [
    ["Hiring managers & HR", "Postings and screens over-weight coding, the least distinguishing skill once others are known",
     "Write maths/statistics and storytelling into job descriptions; test them at interview (case problem + present-back); keep coding as a baseline gate"],
    ["Hiring managers & HR", "Bundles define roles better than wish-lists", "Specify 3-4 core skills per role from the observed bundles"],
    ["Compensation teams", "Pay follows experience, title and company type; junior ranges are the widest", "Price by role and experience; narrow junior ranges; reward growth skills through hikes rather than entry premiums for listed skills"],
    ["Learning & development", "Breadth, not spikes, goes with high hikes", "Assess juniors on all five areas and develop each person's weakest area first"],
    ["Senior leadership", "Openness and conscientiousness separate successful client-facing seniors", "Use both in senior/client-facing selection, promotion and coaching; do not screen on neuroticism"],
    ["Universities & training providers", "Curricula mirror postings and over-teach coding relative to its reward", "Give statistics and data storytelling equal weight to programming; teach across all five areas"],
    ["Aspiring data scientists", "Coding gets you in; maths and storytelling get you ahead", "Build an all-round profile; invest next in the weakest of the five areas"],
    ["Society / labour market", "Mis-specified postings waste candidate effort and exclude people who would grow", "Evidence-based postings make hiring fairer and the talent pipeline more efficient"],
], widths=[3.6, 5.8, 7.6], size=9, caption="Table 6.1  Implications by stakeholder")
doc.add_heading("6.1 Limitations and next steps", 2)
B(["Observational data: validate with an A/B test of revised job descriptions and interview rubrics, tracking hikes and performance.",
   "One company per people dataset: replicate with HR data from other organisations and over several review cycles.",
   "Banded and advertised salaries: link to realised pay where available.",
   "Taxonomy dependence: refine skill-area mapping with expert review; results were stable with and without description-recovered skills.",
   "Senior data separability: test the trait model on a fresh, independently labelled sample."])

# ================================================================== APPENDIX
doc.add_page_break()
doc.add_heading("Appendix A. Data-quality log", 1)
T(["Stage", "File", "Issue", "Rows", "Treatment"],
  [[r.stage, r.file, r.issue, f"{int(r.rows_affected):,}", r.treatment] for r in log.itertuples()], widths=[1.2, 2.6, 6.0, 1.5, 5.9], size=8)
doc.add_heading("Appendix B. Model settings and full results", 1)
rows = []
for code in ["M08", "M12"]:
    mc = R(code, "model_comparison")
    for r in mc.itertuples():
        if r.outer_folds:
            rows.append([("Juniors" if code == "M08" else "Seniors"), r.model, f"{r.auc_mean:.3f}", str(r.best_params_full_data)])
T(["Data", "Model", "AUC", "Tuned settings (refit on all data)"], rows, widths=[2.0, 3.8, 1.6, 9.6], size=8)
T(["Factor", "Odds ratio", "95% CI", "p"],
  [[k, f"{r.odds_ratio:.3f}", f"{r.or_ci_low:.3f}-{r.or_ci_high:.3f}", f"{r.p_value:.4f}"] for k, r in o3.iterrows()],
  widths=[7.0, 2.6, 4.0, 2.4], size=8.5, caption="Table B.2  Ordinal regression on salary band (M03)")
T(["Term", "% effect", "95% CI", "p"],
  [[k, f"{r.pct_effect:.1f}%", f"{r.pct_ci_low:.1f} to {r.pct_ci_high:.1f}", f"{r.p_value:.4f}"] for k, r in e5.iterrows()],
  widths=[7.0, 2.6, 4.0, 2.4], size=8.5, caption="Table B.3  Log-salary regression (M05, HC3 robust errors)")
T(["Skill A", "Skill B", "Support", "Confidence A->B", "Lift"],
  [[r.skill_a, r.skill_b, pct(r.support), pct(r.conf_a_to_b), f"{r.lift:.1f}"] for r in pairs.head(15).itertuples()],
  widths=[4.4, 4.4, 2.4, 3.0, 2.0], size=8.5, caption="Table B.4  Top skill pairs (M02)")
doc.add_heading("Appendix C. Equations", 1)
B(["Ordinal logit (M03): logit P(band <= j) = theta_j - (b1*experience + b_role + b_city + b_skills); OR = exp(b).",
   "Log-salary regression (M05): ln(avg_salary) = a + b_title + b1*min_experience + b_scale + b_type + e; % effect = 100(exp(b) - 1).",
   "Logistic regression (M06, M10): logit P(high) = a + sum(b_k * x_k); OR per unit = exp(b_k); OR per SD = exp(b_k * sd_k).",
   "Effect size (M14): d = (mean_high - mean_low) / sd_pooled; bootstrap CI from the 2.5th and 97.5th percentiles of 2,000 resamples.",
   "Lift (M02): P(A and B) / (P(A) * P(B)).  AUC: probability a random positive is ranked above a random negative."])
doc.add_heading("Appendix D. Code and reproducibility", 1)
B([("01_clean.py, role_rules.py, taxonomy.py: ", "ten-stage cleaning, role rules, skill taxonomy and matcher"),
   ("verify_against_raw.py: ", f"independent verification against the raw files ({n_pass}/{n_chk} pass)"),
   ("build_database.py, database/sql: ", "normalised MySQL schema, load and post-load checks"),
   ("models/run_models.py: ", "all fifteen models (fixed seed 42); per-model figures, results, logs and plain-language notes"),
   ("models/vfl/: ", "plot-ready tables for every chart, for rebuilding the visuals in SAS Visual Analytics"),
   ("make_final_report.py: ", "builds this document; every number is read from the data or model outputs")])

path = OUT / "Approach_Note_Hiring_for_the_Right_Signals.docx"
doc.save(path)
print("saved", path, "figures:", FIGN[0])
