"""Train every analysis model (M01-M14) on the cleaned data and save, per model:
figures/*.png (matplotlib), results/*.csv, log.txt - plus plot-ready tables for SAS VFL in models/vfl/.
Run:  python models/run_models.py          (fixed seeds -> identical numbers on every run)"""
import itertools
import json
import sys
import time
import warnings
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from sklearn.base import clone
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import (GradientBoostingClassifier, HistGradientBoostingClassifier, RandomForestClassifier,
                              RandomForestRegressor)
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (accuracy_score, brier_score_loss, cohen_kappa_score, confusion_matrix, f1_score, r2_score,
                             roc_auc_score, roc_curve, silhouette_score)
from sklearn.model_selection import (GridSearchCV, KFold, RandomizedSearchCV, RepeatedStratifiedKFold, StratifiedKFold,
                                     cross_val_predict, cross_val_score)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from statsmodels.miscmodels.ordinal_model import OrderedModel
from statsmodels.stats.outliers_influence import variance_inflation_factor

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
WORK = HERE.parent
sys.path.insert(0, str(WORK))
from taxonomy import DIM_NAMES  # noqa: E402

SEED = 42
VFL = HERE / "vfl"
VFL.mkdir(parents=True, exist_ok=True)
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 170, "font.size": 10.5, "axes.titleweight": "bold", "axes.titlesize": 12})
BLUE, GREY, RED, GREEN, GOLD = "#1D4ED8", "#94A3B8", "#B91C1C", "#15803D", "#D97706"

# ------------------------------------------------------------------ data
an = pd.read_csv(WORK / "clean" / "analytics_jobs_clean.csv")
ds = pd.read_csv(WORK / "clean" / "ds_jobs_clean.csv")
jds = pd.read_csv(WORK / "clean" / "jds_clean.csv")
sds = pd.read_csv(WORK / "clean" / "sds_clean.csv")
core = an[an.in_core_analytics == 1].copy()
sal = an[an.in_salary_model == 1].copy()
dsa = ds[ds.in_analysis_sample == 1].copy()
DIMS = list(DIM_NAMES)
DN = DIM_NAMES
JSK = {"big_data": "big_data_skills", "maths_stats": "maths_stats_skills", "coding": "coding_skills",
       "ai_ml": "ai_and_ml_skills", "dashboard_story": "dashboard_and_storytelling_skills"}
TR = ["neuroticism", "extraversion", "openness_to_experience", "agreeableness", "conscientiousness"]
TN = {"neuroticism": "Neuroticism", "extraversion": "Extraversion", "openness_to_experience": "Openness",
      "agreeableness": "Agreeableness", "conscientiousness": "Conscientiousness"}
SUMMARY = {}


class Ctx:
    """One model's output folder: figures/, results/, log.txt."""

    def __init__(self, code, name):
        self.code, self.dir = code, HERE / f"{code}_{name}"
        (self.dir / "figures").mkdir(parents=True, exist_ok=True)
        (self.dir / "results").mkdir(parents=True, exist_ok=True)
        self.logf = open(self.dir / "log.txt", "w", encoding="utf-8")
        self.t0 = time.time()
        self.log(f"{code} {name} - run {time.strftime('%Y-%m-%d %H:%M')} - seed {SEED}")

    def log(self, *a):
        msg = " ".join(str(x) for x in a)
        print(f"[{self.code}] {msg}")
        self.logf.write(msg + "\n"); self.logf.flush()

    def fig(self, f, name):
        f.savefig(self.dir / "figures" / f"{name}.png", bbox_inches="tight", facecolor="white"); plt.close(f)
        self.log(f"figure saved: figures/{name}.png")

    def csv(self, df, name, vfl=False):
        df.to_csv(self.dir / "results" / f"{name}.csv", index=False)
        if vfl:
            df.to_csv(VFL / f"{self.code}_{name}.csv", index=False)
        self.log(f"table saved: results/{name}.csv" + ("  (+ vfl copy)" if vfl else ""))

    def done(self):
        self.log(f"finished in {time.time() - self.t0:.1f}s"); self.logf.close()


def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def forest(ax, labels, est, lo, hi, color=BLUE, ref=1.0, log=True):
    y = np.arange(len(labels))[::-1]
    sig = [(l > ref) or (h < ref) for l, h in zip(lo, hi)]
    for yi, e, l, h, s in zip(y, est, lo, hi, sig):
        ax.plot([l, h], [yi, yi], color=color if s else GREY, lw=2)
        ax.plot(e, yi, "o", color=color if s else GREY, ms=7)
    ax.axvline(ref, color=RED, ls="--", lw=1)
    ax.set_yticks(y); ax.set_yticklabels(labels)
    if log:
        ax.set_xscale("log")


# ================================================================== M01 demand profile
def m01():
    c = Ctx("M01", "demand_profile")
    n = len(core); c.log(f"core analytics postings: {n}")
    rows = []
    for d in DIMS:
        k = int(core[f"dim_{d}"].sum()); lo, hi = wilson(k, n)
        rows.append(dict(skill_area=DN[d], postings=k, share=k / n, ci_low=lo, ci_high=hi))
    dem = pd.DataFrame(rows).sort_values("share", ascending=False)
    c.csv(dem, "skill_area_demand", vfl=True); c.log(dem.round(4).to_string(index=False))
    f, ax = plt.subplots(figsize=(8, 4))
    ax.barh(dem.skill_area[::-1], 100 * dem.share[::-1], xerr=[100 * (dem.share - dem.ci_low)[::-1], 100 * (dem.ci_high - dem.share)[::-1]],
            color=[BLUE if a == "Coding" else GREY for a in dem.skill_area[::-1]], capsize=3)
    for i, v in enumerate(100 * dem.share[::-1]):
        ax.text(v + 1, i, f"{v:.1f}%", va="center")
    ax.set_xlabel(f"% of core analytics postings asking for the skill area (n = {n:,}), 95% CI")
    ax.set_title("What job postings ask for: coding dominates")
    c.fig(f, "01_skill_area_demand")
    # role x dim
    rd = core.groupby("role_family")[[f"dim_{d}" for d in DIMS]].mean()
    rd.columns = [DN[d] for d in DIMS]; rd["postings"] = core.role_family.value_counts()
    rd = rd.sort_values("postings", ascending=False)
    long = rd.drop(columns="postings").reset_index().melt(id_vars="role_family", var_name="skill_area", value_name="share")
    long = long.merge(rd.postings.reset_index(), on="role_family")
    c.csv(long, "role_by_skill_area", vfl=True)
    f, ax = plt.subplots(figsize=(9, 5.2))
    m = rd.drop(columns="postings").values * 100
    im = ax.imshow(m, cmap="Blues", aspect="auto", vmin=0, vmax=100)
    ax.set_xticks(range(5)); ax.set_xticklabels(rd.columns[:5], rotation=20, ha="right")
    ax.set_yticks(range(len(rd))); ax.set_yticklabels([f"{r} (n={p:,})" for r, p in zip(rd.index, rd.postings)])
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            ax.text(j, i, f"{m[i, j]:.0f}%", ha="center", va="center", color="white" if m[i, j] > 55 else "black", fontsize=9)
    plt.colorbar(im, ax=ax, label="% of postings")
    ax.set_title("Skill areas asked for, by role family")
    c.fig(f, "02_role_by_skill_area_heatmap")
    # top individual skills + tools
    cnt = Counter(sk for s in core.skills_all.fillna("") for sk in set(s.split("|")) if sk)
    top = pd.DataFrame(cnt.most_common(25), columns=["skill", "postings"]); top["share"] = top.postings / n
    c.csv(top, "top_25_skills", vfl=True)
    f, ax = plt.subplots(figsize=(8, 7))
    ax.barh(top.skill[::-1], 100 * top.share[::-1], color=BLUE)
    ax.set_xlabel("% of core postings"); ax.set_title("Top 25 skills named in core analytics postings")
    c.fig(f, "03_top_25_skills")
    tools = pd.DataFrame([(t.replace("has_", "").replace("_", " "), core[t].mean()) for t in core if t.startswith("has_")],
                         columns=["tool", "share"]).sort_values("share", ascending=False)
    c.csv(tools, "tool_demand", vfl=True); c.log(tools.round(3).to_string(index=False))
    # by seniority
    sen = core.groupby("seniority")[[f"dim_{d}" for d in DIMS]].mean().reindex(["Entry", "Mid", "Senior", "Manager / Lead", "Leadership"])
    sen.columns = [DN[d] for d in DIMS]
    c.csv(sen.reset_index().melt(id_vars="seniority", var_name="skill_area", value_name="share"), "seniority_by_skill_area", vfl=True)
    SUMMARY["M01"] = dict(n=n, demand={r.skill_area: round(r.share, 4) for r in dem.itertuples()})
    c.done()


# ================================================================== M02 association rules
GENERIC = {"analytics", "data analytics", "data analysis", "analysis", "analytical", "analyst", "data", "it", "business analysis",
           "data analyst", "analytical skills", "research", "management", "business", "reporting", "learning"}


def m02():
    c = Ctx("M02", "skill_pairs_association_rules")
    tx = [set(s.split("|")) - GENERIC - {""} for s in core.skills_all.fillna("")]
    n = len(tx); cnt = Counter(sk for t in tx for sk in t)
    freq = {k for k, v in cnt.items() if v / n >= 0.015}
    c.log(f"transactions {n}; generic tokens excluded: {sorted(GENERIC)}; items with support >= 1.5%: {len(freq)}")
    pc = Counter(p for t in tx for p in itertools.combinations(sorted(t & freq), 2))
    rows = []
    for (a, b), k in pc.items():
        sup = k / n
        if sup < 0.01:
            continue
        sa, sb = cnt[a] / n, cnt[b] / n
        rows.append(dict(skill_a=a, skill_b=b, together=k, support=sup, conf_a_to_b=k / cnt[a], conf_b_to_a=k / cnt[b], lift=sup / (sa * sb)))
    r = pd.DataFrame(rows).sort_values("lift", ascending=False)
    c.csv(r, "skill_pair_rules_all", vfl=False)
    top = r[r.lift > 1.5].head(25)
    c.csv(top, "top_25_skill_pairs_by_lift", vfl=True); c.log(top.round(3).to_string(index=False))
    f, ax = plt.subplots(figsize=(9, 7.5))
    lab = [f"{a} + {b}" for a, b in zip(top.skill_a, top.skill_b)]
    ax.barh(lab[::-1], top.lift[::-1], color=BLUE)
    for i, (l, s) in enumerate(zip(top.lift[::-1], top.support[::-1])):
        ax.text(l + .1, i, f"lift {l:.1f} | in {100 * s:.1f}% of ads", va="center", fontsize=8.5)
    ax.set_xlabel("Lift (how many times more often the pair appears together than by chance)")
    ax.set_title("Skill bundles: pairs employers ask for together")
    c.fig(f, "01_top_skill_pairs_lift")
    # network
    G = nx.Graph()
    for t in r[(r.lift > 1.5)].sort_values("support", ascending=False).head(45).itertuples():
        G.add_edge(t.skill_a, t.skill_b, w=t.lift)
    pos = nx.spring_layout(G, seed=SEED, k=0.9)
    f, ax = plt.subplots(figsize=(11, 8.5)); ax.axis("off")
    nx.draw_networkx_edges(G, pos, ax=ax, width=[0.6 * G[u][v]["w"] for u, v in G.edges()], edge_color=GREY, alpha=.7)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=[cnt[x] / n * 9000 for x in G.nodes()], node_color="#93C5FD", edgecolors=BLUE)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8.5)
    ax.set_title("Skill network: node size = how often asked for, edge width = lift")
    c.fig(f, "02_skill_network")
    edges = pd.DataFrame([(u, v, G[u][v]["w"]) for u, v in G.edges()], columns=["source", "target", "lift"])
    c.csv(edges, "network_edges", vfl=True)
    # dimension-level co-occurrence lift
    X = core[[f"dim_{d}" for d in DIMS]].values
    L = np.zeros((5, 5)); rows = []
    for i in range(5):
        for j in range(5):
            both = (X[:, i] & X[:, j]).mean(); L[i, j] = both / (X[:, i].mean() * X[:, j].mean())
            rows.append(dict(area_a=DN[DIMS[i]], area_b=DN[DIMS[j]], lift=L[i, j], both_share=both))
    c.csv(pd.DataFrame(rows), "skill_area_cooccurrence_lift", vfl=True)
    f, ax = plt.subplots(figsize=(6.5, 5.5))
    im = ax.imshow(L, cmap="Blues"); plt.colorbar(im, ax=ax, label="lift")
    ax.set_xticks(range(5)); ax.set_xticklabels([DN[d] for d in DIMS], rotation=25, ha="right")
    ax.set_yticks(range(5)); ax.set_yticklabels([DN[d] for d in DIMS])
    for i in range(5):
        for j in range(5):
            ax.text(j, i, f"{L[i, j]:.1f}", ha="center", va="center", fontsize=9)
    ax.set_title("Which skill areas are asked for together (lift)")
    c.fig(f, "03_skill_area_cooccurrence")
    SUMMARY["M02"] = dict(top_pairs=[f"{a} + {b} (lift {l:.1f})" for a, b, l in zip(top.skill_a[:8], top.skill_b[:8], top.lift[:8])])
    c.done()


# ================================================================== M03 ordinal logistic regression
def m03():
    c = Ctx("M03", "salary_band_ordinal_regression")
    d = sal.copy()
    roles = d.role_family.value_counts().index.tolist(); ref = "Data Analyst / Analytics"
    X = pd.DataFrame({"Experience (years, mid-point)": d.exp_mid})
    for r in roles:
        if r != ref:
            X[f"Role: {r}"] = (d.role_family == r).astype(float)
    for t in ["Tier 2/3", "Unspecified"]:
        X[f"City: {t}"] = (d.city_tier == t).astype(float)
    for k in DIMS:
        X[f"Asks for {DN[k]}"] = d[f"dim_{k}"].astype(float)
    y = d.salary_band_ord.astype(int)
    c.log(f"n = {len(d)}; reference role = {ref}; reference city = Tier 1 metro; outcome = 6 ordered salary bands")
    mod = OrderedModel(y, X, distr="logit").fit(method="bfgs", maxiter=2000, disp=False)
    freq = y.value_counts(normalize=True); llnull = float((y.map(np.log(freq))).sum())  # intercept-only model = band shares
    c.log(f"converged: {mod.mle_retvals.get('converged')}; log-likelihood {mod.llf:.1f}; null {llnull:.1f}; "
          f"pseudo R2 (McFadden) {1 - mod.llf / llnull:.3f}")
    k = X.shape[1]
    ci = mod.conf_int().iloc[:k]
    res = pd.DataFrame({"factor": X.columns, "coef": mod.params[:k].values, "odds_ratio": np.exp(mod.params[:k].values),
                        "or_ci_low": np.exp(ci[0].values), "or_ci_high": np.exp(ci[1].values), "p_value": mod.pvalues[:k].values})
    c.csv(res, "odds_ratios", vfl=True); c.log(res.round(4).to_string(index=False))
    f, ax = plt.subplots(figsize=(9, 8))
    forest(ax, res.factor, res.odds_ratio, res.or_ci_low, res.or_ci_high)
    ax.set_xlabel("Odds ratio of a higher salary band (log scale), 95% CI - grey = not significant")
    ax.set_title("What pushes a posting into a higher pay band (ordinal logistic regression)")
    c.fig(f, "01_odds_ratios_forest")
    # predicted probability of >= 15 LPA by experience for 3 roles
    grid = []
    for role in ["Data Analyst / Analytics", "Data Scientist / ML / AI", "Business Analyst"]:
        for e in np.arange(0, 21, 1.0):
            row = {col: 0.0 for col in X.columns}; row["Experience (years, mid-point)"] = e
            if role != ref:
                row[f"Role: {role}"] = 1.0
            for kk in DIMS:
                row[f"Asks for {DN[kk]}"] = X[f"Asks for {DN[kk]}"].mean()
            grid.append((role, e, row))
    G = pd.DataFrame([g[2] for g in grid])[X.columns]
    P = mod.predict(G.values)
    pr = pd.DataFrame({"role": [g[0] for g in grid], "experience": [g[1] for g in grid], "p_15plus_lpa": P[:, 4:].sum(1), "p_below_6_lpa": P[:, :2].sum(1)})
    c.csv(pr, "predicted_pay_by_experience", vfl=True)
    f, ax = plt.subplots(figsize=(8, 4.5))
    for role, col in zip(pr.role.unique(), [BLUE, GOLD, GREEN]):
        s = pr[pr.role == role]; ax.plot(s.experience, 100 * s.p_15plus_lpa, lw=2.5, color=col, label=role)
    ax.set_xlabel("Years of experience required"); ax.set_ylabel("Predicted chance of a 15+ LPA band (%)")
    ax.set_title("Experience drives the pay band (model prediction, Tier-1 city)"); ax.legend()
    c.fig(f, "02_predicted_pay_by_experience")
    # model-based skill premium summary
    sk = res[res.factor.str.startswith("Asks for")]
    SUMMARY["M03"] = dict(n=len(d), or_per_year=round(float(res.odds_ratio[0]), 3),
                          skill_or={r.factor.replace("Asks for ", ""): [round(r.odds_ratio, 2), round(r.p_value, 4)] for r in sk.itertuples()})
    c.done()


# ================================================================== M04 gradient boosting: does pay depend on skills?
def m04():
    c = Ctx("M04", "salary_band_gradient_boosting")
    d = sal.copy()
    exp_cols = ["exp_min", "exp_max"]
    role = pd.get_dummies(d.role_family, prefix="role", dtype=float); city = pd.get_dummies(d.city_tier, prefix="city", dtype=float)
    sen = pd.get_dummies(d.seniority, prefix="sen", dtype=float)
    skills = d[[f"dim_{k}" for k in DIMS] + [x for x in d if x.startswith("has_")] + ["n_dims", "n_skills_all"]].astype(float)
    y = d.salary_band_ord.values
    sets = {"Experience only": d[exp_cols],
            "Experience + role + seniority + city": pd.concat([d[exp_cols], role, sen, city], axis=1),
            "Experience + role + seniority + city + skills": pd.concat([d[exp_cols], role, sen, city, skills], axis=1),
            "Skills only": skills}
    space = {"learning_rate": [0.03, 0.05, 0.1], "max_depth": [3, 5, None], "max_leaf_nodes": [15, 31, 63],
             "min_samples_leaf": [20, 50, 100], "l2_regularization": [0.0, 1.0, 5.0], "max_iter": [200, 400]}
    outer = StratifiedKFold(5, shuffle=True, random_state=SEED)
    rows, best_full = [], None
    base = np.full_like(y, pd.Series(y).mode()[0])
    rows.append(dict(feature_set="Baseline: always guess the most common band", exact_accuracy=accuracy_score(y, base),
                     within_one_band=(abs(base - y) <= 1).mean(), quadratic_kappa=0.0))
    for name, X in sets.items():
        search = RandomizedSearchCV(HistGradientBoostingClassifier(random_state=SEED), space, n_iter=15, cv=3, scoring="accuracy",
                                    random_state=SEED, n_jobs=-1)
        p = cross_val_predict(search, X, y, cv=outer)
        rows.append(dict(feature_set=name, exact_accuracy=accuracy_score(y, p), within_one_band=(abs(p - y) <= 1).mean(),
                         quadratic_kappa=cohen_kappa_score(y, p, weights="quadratic")))
        c.log(f"{name}: nested-CV exact {rows[-1]['exact_accuracy']:.3f}, within-1 {rows[-1]['within_one_band']:.3f}, QWK {rows[-1]['quadratic_kappa']:.3f}")
        if name.endswith("+ skills"):
            best_full = (X, search.fit(X, y))
            c.log("tuned params (full set, refit on all data):", best_full[1].best_params_)
    r = pd.DataFrame(rows); c.csv(r, "model_comparison", vfl=True)
    f, ax = plt.subplots(figsize=(9, 4.2))
    yy = np.arange(len(r))[::-1]
    ax.barh(yy + .2, 100 * r.exact_accuracy, .4, color=BLUE, label="Exact band")
    ax.barh(yy - .2, 100 * r.within_one_band, .4, color="#93C5FD", label="Within one band")
    for yi, a, b in zip(yy, r.exact_accuracy, r.within_one_band):
        ax.text(100 * a + 1, yi + .2, f"{100 * a:.1f}%", va="center", fontsize=9); ax.text(100 * b + 1, yi - .2, f"{100 * b:.1f}%", va="center", fontsize=9)
    ax.set_yticks(yy); ax.set_yticklabels(r.feature_set); ax.set_xlim(0, 100); ax.legend(loc="lower right")
    ax.set_xlabel("Accuracy on unseen postings (nested 5-fold CV)")
    ax.set_title("Adding skills does not help predict pay - experience does the work")
    c.fig(f, "01_model_comparison")
    # grouped permutation importance on a held-out split
    X, search = best_full
    groups = {"Experience": exp_cols, "Role family": list(role.columns), "Seniority": list(sen.columns), "City tier": list(city.columns),
              "Skills (areas, tools, counts)": list(skills.columns)}
    Xtr, Xte, ytr, yte = X.iloc[::1][d.index % 4 != 0], X[d.index % 4 == 0], y[d.index % 4 != 0], y[d.index % 4 == 0]
    mdl = clone(search.best_estimator_).fit(Xtr, ytr); basek = cohen_kappa_score(yte, mdl.predict(Xte), weights="quadratic")
    rng = np.random.default_rng(SEED); imp = []
    for g, cols in groups.items():
        drops = []
        for _ in range(20):
            Xp = Xte.copy(); idx = rng.permutation(len(Xp)); Xp[cols] = Xp[cols].values[idx]
            drops.append(basek - cohen_kappa_score(yte, mdl.predict(Xp), weights="quadratic"))
        imp.append(dict(factor_group=g, importance_drop_in_kappa=np.mean(drops), sd=np.std(drops)))
    imp = pd.DataFrame(imp).sort_values("importance_drop_in_kappa", ascending=False)
    c.csv(imp, "grouped_permutation_importance", vfl=True); c.log(imp.round(4).to_string(index=False))
    f, ax = plt.subplots(figsize=(8, 3.8))
    ax.barh(imp.factor_group[::-1], imp.importance_drop_in_kappa[::-1], xerr=imp.sd[::-1], color=BLUE, capsize=3)
    ax.set_xlabel("Drop in agreement (quadratic kappa) when the factor is scrambled")
    ax.set_title("What the pay model relies on")
    c.fig(f, "02_grouped_importance")
    SUMMARY["M04"] = dict(comparison=r.round(4).to_dict("records"), importance=imp.round(4).to_dict("records"))
    c.done()


# ================================================================== M05 DS Jobs salary regression
def m05():
    c = Ctx("M05", "salary_regression_ds_jobs")
    d = dsa.copy(); c.log(f"n = {len(d)} company x title rows (placeholder / implausible rows excluded: {len(ds) - len(d)})")
    form = ("np.log(avg_salary_lpa) ~ C(job_title, Treatment('Data Analyst')) + min_experience + "
            "C(company_scale, Treatment('Large (>100)')) + C(company_type, Treatment('IT services / consulting'))")
    m = smf.ols(form, d).fit(cov_type="HC3")
    c.log(m.summary().as_text())
    ci = m.conf_int()
    res = pd.DataFrame({"term": m.params.index, "coef": m.params.values, "pct_effect": 100 * (np.exp(m.params.values) - 1),
                        "pct_ci_low": 100 * (np.exp(ci[0].values) - 1), "pct_ci_high": 100 * (np.exp(ci[1].values) - 1), "p_value": m.pvalues.values})
    res = res[res.term != "Intercept"]
    res["label"] = (res.term.str.replace(r"C\(job_title, Treatment\('Data Analyst'\)\)\[T\.", "Title: ", regex=True)
                    .str.replace(r"C\(company_scale, Treatment\('Large \(>100\)'\)\)\[T\.", "Company: ", regex=True)
                    .str.replace(r"C\(company_type, Treatment\('IT services / consulting'\)\)\[T\.", "Type: ", regex=True)
                    .str.replace("]", "", regex=False).str.replace("min_experience", "+1 year min. experience"))
    c.csv(res, "salary_effects_pct", vfl=True)
    f, ax = plt.subplots(figsize=(9, 6))
    forest(ax, res.label, res.pct_effect, res.pct_ci_low, res.pct_ci_high, ref=0, log=False)
    ax.set_xlabel("% difference in average salary vs reference (Data Analyst, large company, IT services), 95% CI")
    ax.set_title(f"Pay ladder (log-salary regression, R² = {m.rsquared:.2f})")
    c.fig(f, "01_salary_effects")
    # CV R2: OLS vs random forest
    Xd = pd.get_dummies(d[["job_title", "company_scale", "company_type"]], dtype=float).assign(min_experience=d.min_experience)
    yl = np.log(d.avg_salary_lpa)
    kf = KFold(5, shuffle=True, random_state=SEED)
    r2_ols = cross_val_score(LinearRegression(), Xd, yl, cv=kf, scoring="r2")
    rf = GridSearchCV(RandomForestRegressor(random_state=SEED, n_estimators=400), {"max_depth": [4, 8, None], "min_samples_leaf": [3, 10, 25]}, cv=3)
    r2_rf = cross_val_score(rf, Xd, yl, cv=kf, scoring="r2")
    cv = pd.DataFrame([dict(model="Linear regression (log salary)", cv_r2_mean=r2_ols.mean(), cv_r2_sd=r2_ols.std()),
                       dict(model="Random forest (tuned)", cv_r2_mean=r2_rf.mean(), cv_r2_sd=r2_rf.std())])
    c.csv(cv, "cv_r2_comparison", vfl=True); c.log(cv.round(4).to_string(index=False))
    # descriptive ladders
    order = d.groupby("job_title").avg_salary_lpa.median().sort_values().index
    f, ax = plt.subplots(figsize=(9, 5))
    ax.boxplot([d.loc[d.job_title == t, "avg_salary_lpa"] for t in order], vert=False, tick_labels=order, showfliers=False,
               patch_artist=True, boxprops=dict(facecolor="#BFDBFE"))
    ax.set_xlabel("Average salary offered (LPA)"); ax.set_title("Salary by job title (company-level offers)")
    c.fig(f, "02_salary_by_title")
    lad = d.groupby(["job_title", "exp_band"]).avg_salary_lpa.agg(["median", "size"]).reset_index()
    c.csv(lad, "salary_by_title_and_experience", vfl=True)
    d["headroom_pct"] = 100 * (d.max_salary_lpa - d.avg_salary_lpa) / d.avg_salary_lpa
    hr = d.groupby("job_title").headroom_pct.median().sort_values().reset_index()
    hs = d.groupby("company_scale").agg(headroom_pct=("headroom_pct", "median"), avg_salary=("avg_salary_lpa", "median"), rows=("row_id", "size")).reset_index()
    c.csv(hr, "pay_spread_by_title", vfl=True); c.csv(hs, "pay_spread_by_company_scale", vfl=True)
    f, ax = plt.subplots(1, 2, figsize=(12, 4.5), gridspec_kw={"width_ratios": [1.6, 1]})
    ax[0].barh(hr.job_title, hr.headroom_pct, color=BLUE); ax[0].set_xlabel("Median % the maximum sits above the average")
    ax[0].set_title("Pay spread by title")
    ax[1].bar(hs.company_scale.str.replace(" ", "\n", 1), hs.headroom_pct, color=GOLD); ax[1].set_ylabel("Median spread %")
    for i, (h, a) in enumerate(zip(hs.headroom_pct, hs.avg_salary)):
        ax[1].text(i, h + 1, f"avg {a:.1f} LPA", ha="center", fontsize=9)
    ax[1].set_title("Pay spread by company size")
    c.fig(f, "03_pay_spread")
    SUMMARY["M05"] = dict(n=len(d), r2=round(m.rsquared, 3), cv=cv.round(3).to_dict("records"),
                          effects={r.label: [round(r.pct_effect, 1), round(r.p_value, 4)] for r in res.itertuples()})
    c.done()


# ================================================================== classification suite (JDS and SDS)
def suite(X, y, label, c_lr, c_tree, c_ens, feat_names, unit_note):
    out = {}
    # ---- logistic regression (statsmodels for odds ratios)
    Xs = (X - X.mean()) / X.std()
    lr_unit = sm.Logit(y, sm.add_constant(X)).fit(disp=0)
    lr_sd = sm.Logit(y, sm.add_constant(Xs)).fit(disp=0)
    c_lr.log(lr_unit.summary2().as_text())
    vif = [variance_inflation_factor(sm.add_constant(X).values, i + 1) for i in range(X.shape[1])]
    rows = []
    for i, col in enumerate(X.columns):
        cu, cs = lr_unit.conf_int().loc[col], lr_sd.conf_int().loc[col]
        uni = sm.Logit(y, sm.add_constant(Xs[[col]])).fit(disp=0)
        rows.append(dict(variable=feat_names[col], or_per_unit=np.exp(lr_unit.params[col]), or_unit_low=np.exp(cu[0]), or_unit_high=np.exp(cu[1]),
                         or_per_sd=np.exp(lr_sd.params[col]), or_sd_low=np.exp(cs[0]), or_sd_high=np.exp(cs[1]), p_value=lr_unit.pvalues[col],
                         univariate_or_per_sd=np.exp(uni.params[col]), univariate_p=uni.pvalues[col], vif=vif[i]))
    orr = pd.DataFrame(rows); c_lr.csv(orr, "odds_ratios", vfl=True); c_lr.log(orr.round(4).to_string(index=False))
    c_lr.log(f"pseudo R2 (McFadden) {lr_unit.prsquared:.3f}; {unit_note}")
    f, ax = plt.subplots(figsize=(8.5, 4.2))
    o = orr.sort_values("or_per_sd", ascending=False)
    forest(ax, o.variable, o.or_per_sd, o.or_sd_low, o.or_sd_high)
    ax.set_xlabel("Odds ratio per 1 standard deviation (log scale), 95% CI - grey = not significant")
    ax.set_title(f"{label}: how much each factor raises the odds (all factors together)")
    c_lr.fig(f, "01_odds_ratios_forest")
    # ---- model zoo with nested CV
    rkf_outer = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=SEED)
    inner = StratifiedKFold(5, shuffle=True, random_state=SEED)
    zoo = {
        "Logistic regression": GridSearchCV(make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000, solver="liblinear")),
                                            {"logisticregression__C": [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 100], "logisticregression__penalty": ["l1", "l2"]},
                                            cv=inner, scoring="roc_auc"),
        "Decision tree": GridSearchCV(DecisionTreeClassifier(random_state=SEED), {"max_depth": [2, 3, 4, 5], "min_samples_leaf": [3, 5, 8, 12],
                                                                                  "criterion": ["gini", "entropy"]}, cv=inner, scoring="roc_auc"),
        "Random forest": GridSearchCV(RandomForestClassifier(n_estimators=300, random_state=SEED, n_jobs=-1),
                                      {"max_depth": [2, 4, None], "min_samples_leaf": [1, 3, 6], "max_features": ["sqrt", None]}, cv=3, scoring="roc_auc"),
        "Gradient boosting": GridSearchCV(GradientBoostingClassifier(random_state=SEED),
                                          {"learning_rate": [0.03, 0.1], "max_depth": [1, 2, 3], "n_estimators": [100, 300], "subsample": [0.8, 1.0]},
                                          cv=3, scoring="roc_auc"),
    }
    outer_short = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=SEED)
    comp, roc_rows, cms, perm = [], [], {}, []
    for name, est in zoo.items():
        cvo = rkf_outer if name in ("Logistic regression", "Decision tree") else outer_short
        aucs, accs, f1s, brs = [], [], [], []
        for k, (tr, te) in enumerate(cvo.split(X, y)):
            m = clone(est).fit(X.iloc[tr], y.iloc[tr]); p = m.predict_proba(X.iloc[te])[:, 1]
            aucs.append(roc_auc_score(y.iloc[te], p)); accs.append(accuracy_score(y.iloc[te], p > .5))
            f1s.append(f1_score(y.iloc[te], p > .5)); brs.append(brier_score_loss(y.iloc[te], p))
            if k < 5 and name in ("Random forest", "Gradient boosting"):
                pi = permutation_importance(m.best_estimator_, X.iloc[te], y.iloc[te], scoring="roc_auc", n_repeats=20, random_state=SEED)
                perm += [dict(model=name, variable=feat_names[col], importance=v) for col, v in zip(X.columns, pi.importances_mean)]
        comp.append(dict(model=name, auc_mean=np.mean(aucs), auc_sd=np.std(aucs), accuracy=np.mean(accs), f1=np.mean(f1s), brier=np.mean(brs),
                         outer_folds=len(aucs)))
        pp = cross_val_predict(est, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=SEED), method="predict_proba")[:, 1]
        fpr, tpr, _ = roc_curve(y, pp)
        roc_rows += [dict(model=name, fpr=a, tpr=b) for a, b in zip(fpr, tpr)]
        cms[name] = confusion_matrix(y, pp > .5)
        best = clone(est).fit(X, y); comp[-1]["best_params_full_data"] = json.dumps(best.best_params_)
        (c_tree if name == "Decision tree" else c_ens if name in ("Random forest", "Gradient boosting") else c_lr).log(
            f"{name}: nested CV AUC {np.mean(aucs):.3f} +/- {np.std(aucs):.3f} over {len(aucs)} outer folds; acc {np.mean(accs):.3f}; "
            f"best params on full data {best.best_params_}")
        if name == "Decision tree":
            out["tree"] = best.best_estimator_
    base_acc = max(y.mean(), 1 - y.mean())
    comp.append(dict(model="Baseline (guess majority class)", auc_mean=0.5, auc_sd=0, accuracy=base_acc, f1=np.nan, brier=y.mean() * (1 - y.mean()),
                     outer_folds=0, best_params_full_data=""))
    comp = pd.DataFrame(comp); c_ens.csv(comp, "model_comparison", vfl=True); c_ens.log(comp.drop(columns="best_params_full_data").round(4).to_string(index=False))
    roc = pd.DataFrame(roc_rows); c_ens.csv(roc, "roc_points", vfl=True)
    f, ax = plt.subplots(figsize=(6.5, 6))
    for (name, g), col in zip(roc.groupby("model", sort=False), [BLUE, GOLD, GREEN, RED]):
        a = comp.loc[comp.model == name, "auc_mean"].iloc[0]
        ax.plot(g.fpr, g.tpr, lw=2, color=col, label=f"{name} (AUC {a:.2f})")
    ax.plot([0, 1], [0, 1], "--", color=GREY, label="Coin flip (AUC 0.50)")
    ax.set_xlabel("False positive rate"); ax.set_ylabel("True positive rate"); ax.legend(loc="lower right", fontsize=9)
    ax.set_title(f"{label}: ROC curves (unseen data)")
    c_ens.fig(f, "01_roc_curves")
    f, ax = plt.subplots(figsize=(8, 4))
    cc = comp[comp.outer_folds > 0]
    ax.barh(cc.model[::-1], cc.auc_mean[::-1], xerr=cc.auc_sd[::-1], color=BLUE, capsize=4)
    ax.axvline(0.5, color=RED, ls="--"); ax.set_xlim(0.4, 1.0)
    for i, (v, sd_) in enumerate(zip(cc.auc_mean[::-1], cc.auc_sd[::-1])):
        ax.text(min(v + sd_ + .01, .96), i + .28, f"{v:.3f}", va="center", fontsize=9.5, fontweight="bold")
    ax.set_xlabel("AUC on unseen data (nested cross-validation, mean +/- sd)"); ax.set_title(f"{label}: model comparison")
    c_ens.fig(f, "02_model_comparison_auc")
    pm = pd.DataFrame(perm).groupby(["model", "variable"]).importance.mean().reset_index()
    c_ens.csv(pm, "permutation_importance", vfl=True)
    f, ax = plt.subplots(figsize=(8.5, 4))
    piv = pm.pivot(index="variable", columns="model", values="importance").sort_values("Gradient boosting")
    piv.plot.barh(ax=ax, color=[GREEN, GOLD][::-1] if False else [GOLD, GREEN])
    ax.set_xlabel("Drop in AUC when the variable is scrambled (on unseen folds)"); ax.set_ylabel("")
    ax.set_title(f"{label}: which variables the models rely on")
    c_ens.fig(f, "03_permutation_importance")
    best_name = cc.sort_values("auc_mean").model.iloc[-1]
    cm = cms[best_name]
    f, ax = plt.subplots(figsize=(4.6, 4))
    ax.imshow(cm, cmap="Blues"); ax.grid(False)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=14, color="white" if cm[i, j] > cm.max() / 2 else "black")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["Pred. low", "Pred. high"]); ax.set_yticks([0, 1]); ax.set_yticklabels(["Actual low", "Actual high"])
    ax.set_title(f"Confusion matrix: {best_name}")
    c_ens.fig(f, "04_confusion_matrix_best")
    c_ens.csv(pd.DataFrame(cm, index=["actual_low", "actual_high"], columns=["pred_low", "pred_high"]).reset_index(), "confusion_matrix_best")
    # ---- decision tree picture + rules
    t = out["tree"]
    f, ax = plt.subplots(figsize=(16, 7.5))
    plot_tree(t, feature_names=[feat_names[x] for x in X.columns], class_names=["Low", "High"], filled=True, rounded=True,
              proportion=False, impurity=False, fontsize=9, ax=ax)
    ax.set_title(f"{label}: decision tree (tuned depth {t.get_depth()}, unseen-data AUC {comp.loc[comp.model == 'Decision tree', 'auc_mean'].iloc[0]:.2f})")
    c_tree.fig(f, "01_decision_tree")
    rules = export_text(t, feature_names=[feat_names[x] for x in X.columns], show_weights=True)
    (c_tree.dir / "results" / "tree_rules.txt").write_text(rules, encoding="utf-8"); c_tree.log("tree rules:\n" + rules)
    leaf = t.apply(X); lt = pd.DataFrame({"leaf": leaf, "y": y.values}).groupby("leaf").y.agg(["size", "mean"]).reset_index()
    lt.columns = ["leaf", "people", "share_high"]
    c_tree.csv(lt, "leaf_summary", vfl=True)
    out.update(lr=lr_unit, orr=orr, comp=comp)
    return out


# ================================================================== M06-M09 juniors
def jds_models():
    X = jds[list(JSK.values())].copy(); y = jds.salary_hike_high
    names = {JSK[d]: DN[d] for d in DIMS}
    c6, c7, c8 = Ctx("M06", "junior_logistic_regression"), Ctx("M07", "junior_decision_tree"), Ctx("M08", "junior_ensembles_benchmark")
    c6.log(f"n = {len(y)}; high-hike share {y.mean():.3f}; skills on a 1-5 scale")
    corr = X.rename(columns=names).corr(); c6.csv(corr.reset_index().rename(columns={"index": "skill"}), "skill_correlations", vfl=True)
    o = suite(X, y, "Junior salary hike", c6, c7, c8, names, "odds ratio per unit = per 1 point on the 1-5 skill scale")
    # group means chart
    gm = jds.groupby("salary_hike_high")[list(JSK.values())].mean().T; gm.index = [names[i] for i in gm.index]; gm.columns = ["Low hike", "High hike"]
    c6.csv(gm.reset_index().rename(columns={"index": "skill_area"}), "group_means", vfl=True)
    f, ax = plt.subplots(figsize=(8.5, 4.2)); xx = np.arange(5)
    ax.bar(xx - .2, gm["Low hike"], .4, color=GREY, label="Low hike"); ax.bar(xx + .2, gm["High hike"], .4, color=BLUE, label="High hike")
    ax.set_xticks(xx); ax.set_xticklabels(gm.index, rotation=12); ax.set_ylim(1, 5.2); ax.set_ylabel("Mean score (1-5)"); ax.legend()
    ax.set_title("High-hike vs low-hike juniors: mean skill scores")
    c6.fig(f, "02_group_means")
    SUMMARY["M06"] = dict(odds_ratios=o["orr"][["variable", "or_per_unit", "or_unit_low", "or_unit_high", "p_value", "vif"]].round(3).to_dict("records"))
    SUMMARY["M08"] = dict(comparison=o["comp"].drop(columns="best_params_full_data").round(3).to_dict("records"))
    c6.done(); c7.done(); c8.done()
    # ---- M09 breadth vs spike
    c = Ctx("M09", "junior_breadth_vs_spike")
    j = jds.copy(); S = j[list(JSK.values())]
    j["skill_max"] = S.max(1); j["skill_sd"] = S.std(1)
    meas = {"Average of 5 skills": "skill_mean", "Weakest skill": "skill_min", "Strongest skill": "skill_max",
            "Gap strongest-weakest": "skill_range", "Unevenness (sd of 5 skills)": "skill_sd"}
    rows = []
    for k, v in meas.items():
        a = roc_auc_score(y, j[v]); rows.append(dict(measure=k, auc=a, direction="higher = high hike" if a >= .5 else "lower = high hike", auc_either_direction=max(a, 1 - a)))
    sa = pd.DataFrame(rows); c.csv(sa, "single_measure_auc", vfl=True); c.log(sa.round(3).to_string(index=False))
    Z = (j[list(meas.values())] - j[list(meas.values())].mean()) / j[list(meas.values())].std()
    base = sm.Logit(y, sm.add_constant(Z[["skill_mean"]])).fit(disp=0)
    nest = []
    for k, v in meas.items():
        if v == "skill_mean":
            continue
        m = sm.Logit(y, sm.add_constant(Z[["skill_mean", v]])).fit(disp=0)
        lr = 2 * (m.llf - base.llf)
        nest.append(dict(added_to_average=k, or_per_sd=np.exp(m.params[v]), p_value=m.pvalues[v], lr_stat=lr, lr_p=stats.chi2.sf(lr, 1)))
    nest = pd.DataFrame(nest); c.csv(nest, "nested_tests_vs_average", vfl=True); c.log(nest.round(4).to_string(index=False))
    f, ax = plt.subplots(figsize=(8.5, 3.8))
    sa2 = sa.iloc[::-1]
    ax.barh(sa2.measure, sa2.auc_either_direction, color=[BLUE if "high" in d_ and m_ != "Strongest skill" else (GOLD if "lower" in d_ else GREY)
                                                         for d_, m_ in zip(sa2.direction, sa2.measure)])
    for i, (v, d_) in enumerate(zip(sa2.auc_either_direction, sa2.direction)):
        ax.text(v + .005, i, f"{v:.2f}  ({d_})", va="center", fontsize=9)
    ax.axvline(.5, color=RED, ls="--"); ax.set_xlim(.45, 1.08)
    ax.set_xlabel("AUC: how well one number separates high- from low-hike juniors")
    ax.set_title("Breadth beats a spike: the average matters, the best skill barely does")
    c.fig(f, "01_breadth_vs_spike_auc")
    j["level"] = pd.qcut(j.skill_mean, 3, labels=["Lower average", "Middle average", "Top average"])
    j["shape"] = np.where(j.skill_range <= j.skill_range.median(), "Balanced profile", "Spiky profile")
    g = j.groupby(["level", "shape"], observed=False).salary_hike_high.agg(["mean", "size"]).reset_index()
    g.columns = ["average_level", "profile_shape", "high_hike_rate", "people"]
    c.csv(g, "hike_rate_by_level_and_shape", vfl=True); c.log(g.round(3).to_string(index=False))
    f, ax = plt.subplots(figsize=(8, 4.3)); xx = np.arange(3)
    for off, shp, col in [(-.2, "Balanced profile", BLUE), (.2, "Spiky profile", GOLD)]:
        s = g[g.profile_shape == shp]
        ax.bar(xx + off, 100 * s.high_hike_rate.fillna(0), .4, color=col, label=shp)
        for xi, r_, nn in zip(xx + off, s.high_hike_rate, s.people):
            ax.text(xi, 100 * (0 if pd.isna(r_) else r_) + 2, f"n={nn}", ha="center", fontsize=8.5)
    ax.set_xticks(xx); ax.set_xticklabels(["Lower average", "Middle average", "Top average"]); ax.set_ylim(0, 110)
    ax.set_ylabel("% with a high salary hike"); ax.legend(); ax.set_title("Same average level: balanced profiles do at least as well as spiky ones")
    c.fig(f, "02_hike_rate_by_level_and_shape")
    SUMMARY["M09"] = dict(single_auc=sa.round(3).to_dict("records"), nested=nest.round(4).to_dict("records"), groups=g.round(3).to_dict("records"))
    c.done()


# ================================================================== M10-M13 seniors
def sds_models():
    X = sds[TR].copy(); y = sds.success_high
    c10, c11, c12 = Ctx("M10", "senior_logistic_regression"), Ctx("M11", "senior_decision_tree"), Ctx("M12", "senior_ensembles_benchmark")
    c10.log(f"n = {len(y)}; high-success share {y.mean():.3f}; traits on a normalised score (observed 17-68)")
    corr = X.rename(columns=TN).corr(); c10.csv(corr.reset_index().rename(columns={"index": "trait"}), "trait_correlations", vfl=True)
    f, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1); plt.colorbar(im, ax=ax)
    ax.set_xticks(range(5)); ax.set_xticklabels(corr.columns, rotation=30, ha="right"); ax.set_yticks(range(5)); ax.set_yticklabels(corr.columns)
    for i in range(5):
        for k in range(5):
            ax.text(k, i, f"{corr.values[i, k]:.2f}", ha="center", va="center", fontsize=9)
    ax.grid(False); ax.set_title("How the five traits move together")
    c10.fig(f, "03_trait_correlations")
    o = suite(X, y, "Senior success", c10, c11, c12, TN, "odds ratio per unit = per 1 point of the normalised trait score")
    orr = o["orr"]
    f, ax = plt.subplots(figsize=(8.5, 4)); yy = np.arange(5)[::-1]
    ax.barh(yy + .2, orr.univariate_or_per_sd, .4, color=GREY, label="Trait on its own")
    ax.barh(yy - .2, orr.or_per_sd, .4, color=BLUE, label="Trait with the other four held constant")
    ax.set_yticks(yy); ax.set_yticklabels(orr.variable); ax.set_xscale("log"); ax.axvline(1, color=RED, ls="--"); ax.legend(fontsize=9)
    ax.set_xlabel("Odds ratio of high success per 1 SD (log scale)"); ax.set_title("Alone vs together: neuroticism only matters once the others are held constant")
    c10.fig(f, "04_univariate_vs_multivariate")
    gm = sds.groupby("success_high")[TR].mean().T; gm.index = [TN[i] for i in gm.index]; gm.columns = ["Low success", "High success"]
    c10.csv(gm.reset_index().rename(columns={"index": "trait"}), "group_means", vfl=True)
    f, ax = plt.subplots(figsize=(8.5, 4.2)); xx = np.arange(5)
    ax.bar(xx - .2, gm["Low success"], .4, color=GREY, label="Low success"); ax.bar(xx + .2, gm["High success"], .4, color=BLUE, label="High success")
    ax.set_xticks(xx); ax.set_xticklabels(gm.index); ax.set_ylabel("Mean normalised score"); ax.legend()
    ax.set_title("Successful vs other seniors: mean trait scores")
    c10.fig(f, "02_group_means")
    SUMMARY["M10"] = dict(odds_ratios=orr[["variable", "or_per_sd", "or_sd_low", "or_sd_high", "p_value", "univariate_or_per_sd", "univariate_p", "vif"]].round(3).to_dict("records"))
    SUMMARY["M12"] = dict(comparison=o["comp"].drop(columns="best_params_full_data").round(3).to_dict("records"))
    c10.done(); c11.done(); c12.done()
    # ---- M13 personas
    c = Ctx("M13", "senior_personas_kmeans")
    Z = StandardScaler().fit_transform(X)
    sel = []
    for k in range(2, 8):
        km = KMeans(k, n_init=50, random_state=SEED).fit(Z)
        sel.append(dict(k=k, silhouette=silhouette_score(Z, km.labels_), inertia=km.inertia_))
    sel = pd.DataFrame(sel); c.csv(sel, "choosing_k", vfl=True); c.log(sel.round(4).to_string(index=False))
    k = int(sel[sel.k.between(3, 5)].sort_values("silhouette").k.iloc[-1])
    c.log(f"chosen k = {k} (highest silhouette among 3-5 clusters, kept small enough to interpret)")
    f, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    ax[0].plot(sel.k, sel.silhouette, "o-", color=BLUE); ax[0].set_title("Silhouette (higher = clearer groups)"); ax[0].set_xlabel("k")
    ax[1].plot(sel.k, sel.inertia, "o-", color=GOLD); ax[1].set_title("Within-group spread (elbow)"); ax[1].set_xlabel("k")
    c.fig(f, "01_choosing_k")
    km = KMeans(k, n_init=50, random_state=SEED).fit(Z)
    s = sds.copy(); s["cluster"] = km.labels_
    zt = pd.DataFrame(Z, columns=TR); zt["cluster"] = km.labels_
    prof = zt.groupby("cluster")[TR].mean()
    names = {}
    for cl, row in prof.iterrows():
        hi = [TN[t] for t in row.sort_values(ascending=False).index if row[t] > .4][:2]
        lo = [TN[t] for t in row.sort_values().index if row[t] < -.4][:2]
        names[cl] = ("High " + " & ".join(hi)) if hi else ("Low " + " & ".join(lo) if lo else "Average on all traits")
        if hi and lo:
            names[cl] += f", low {lo[0]}"
    succ = s.groupby("cluster").success_high.agg(["sum", "size"])
    rows = []
    for cl in prof.index:
        kk, nn = succ.loc[cl, "sum"], succ.loc[cl, "size"]; lo_, hi_ = wilson(kk, nn)
        rows.append(dict(cluster=cl, persona=names[cl], people=nn, success_rate=kk / nn, ci_low=lo_, ci_high=hi_, **{TN[t] + "_z": prof.loc[cl, t] for t in TR}))
    pt = pd.DataFrame(rows).sort_values("success_rate", ascending=False)
    chi = stats.chi2_contingency(pd.crosstab(s.cluster, s.success_high))
    c.log(f"chi-square persona x success: chi2 {chi[0]:.2f}, p {chi[1]:.2e}")
    c.csv(pt, "personas", vfl=True); c.log(pt.round(3).to_string(index=False))
    f, ax = plt.subplots(1, 2, figsize=(14, 4.6), gridspec_kw={"width_ratios": [1.6, 1], "wspace": 0.08})
    M = pt[[TN[t] + "_z" for t in TR]].values
    im = ax[0].imshow(M, cmap="RdBu_r", vmin=-1.5, vmax=1.5, aspect="auto"); ax[0].grid(False)
    ax[0].set_xticks(range(5)); ax[0].set_xticklabels([TN[t] for t in TR], rotation=20)
    ax[0].set_yticks(range(len(pt))); ax[0].set_yticklabels([f"{p} (n={n_})" for p, n_ in zip(pt.persona, pt.people)])
    for i in range(M.shape[0]):
        for jj in range(5):
            ax[0].text(jj, i, f"{M[i, jj]:+.1f}", ha="center", va="center", fontsize=9)
    plt.colorbar(im, ax=ax[0], label="z-score vs all seniors"); ax[0].set_title("Senior personas: trait profile")
    yy = np.arange(len(pt))[::-1]
    ax[1].barh(yy, 100 * pt.success_rate, xerr=[100 * (pt.success_rate - pt.ci_low), 100 * (pt.ci_high - pt.success_rate)], color=BLUE, capsize=3)
    ax[1].set_yticks(yy); ax[1].set_yticklabels([]); ax[1].set_xlim(0, 110); ax[1].set_xlabel("% rated high success (95% CI)")
    ax[1].set_title("Success rate by persona")
    for yi, v in zip(yy, pt.success_rate):
        ax[1].text(100 * v + 2, yi, f"{100 * v:.0f}%", va="center")
    # put the bar chart rows in the same order as the heatmap rows
    ax[1].invert_yaxis(); ax[1].invert_yaxis()
    c.fig(f, "02_personas")
    pcs = PCA(2, random_state=SEED).fit(Z); P = pcs.transform(Z)
    f, ax = plt.subplots(figsize=(7.5, 6))
    for cl, col in zip(prof.index, [BLUE, GOLD, GREEN, RED, "#7C3AED"]):
        msk = km.labels_ == cl
        ax.scatter(P[msk & (y == 1), 0], P[msk & (y == 1), 1], color=col, marker="o", label=f"{names[cl]} - high success", alpha=.8)
        ax.scatter(P[msk & (y == 0), 0], P[msk & (y == 0), 1], color=col, marker="x", alpha=.8)
    ax.set_xlabel(f"Component 1 ({100 * pcs.explained_variance_ratio_[0]:.0f}% of variation)")
    ax.set_ylabel(f"Component 2 ({100 * pcs.explained_variance_ratio_[1]:.0f}%)")
    ax.legend(fontsize=8, loc="best"); ax.set_title("Seniors on a 2-D map (o = high success, x = low)")
    c.fig(f, "03_persona_map")
    c.csv(pd.DataFrame({"row_id": s.row_id, "persona": s.cluster.map(names), "success_high": y, "pc1": P[:, 0], "pc2": P[:, 1]}), "persona_assignments", vfl=True)
    SUMMARY["M13"] = dict(k=k, chi2_p=float(chi[1]), personas=pt.round(3).to_dict("records"))
    c.done()


# ================================================================== M14 bootstrap hype-gap
def m14():
    c = Ctx("M14", "hype_gap_bootstrap")
    B = 2000; rng = np.random.default_rng(SEED)
    D = core[[f"dim_{d}" for d in DIMS]].values.astype(float); n = len(D)
    J = jds[[JSK[d] for d in DIMS]].values; y = jds.salary_hike_high.values; m = len(J)
    dem_b = np.empty((B, 5)); eff_b = np.empty((B, 5))
    for b in range(B):
        dem_b[b] = D[rng.integers(0, n, n)].mean(0)
        idx = rng.integers(0, m, m); Jb, yb = J[idx], y[idx]
        eff_b[b] = (Jb[yb == 1].mean(0) - Jb[yb == 0].mean(0)) / Jb.std(0, ddof=1)
    dem = D.mean(0); eff = (J[y == 1].mean(0) - J[y == 0].mean(0)) / J.std(0, ddof=1)
    res = pd.DataFrame({"skill_area": [DN[d] for d in DIMS], "demand_share": dem, "demand_ci_low": np.percentile(dem_b, 2.5, 0),
                        "demand_ci_high": np.percentile(dem_b, 97.5, 0), "effect_size_d": eff, "d_ci_low": np.percentile(eff_b, 2.5, 0),
                        "d_ci_high": np.percentile(eff_b, 97.5, 0)})
    res["demand_rank"] = res.demand_share.rank(ascending=False).astype(int); res["reward_rank"] = res.effect_size_d.rank(ascending=False).astype(int)
    res["quadrant"] = np.where(res.d_ci_low > 0.5, np.where(res.demand_share > res.demand_share.mean(), "Core: asked for and rewarded", "Hidden edge: rewarded, rarely asked"),
                               np.where(res.d_ci_high < 0.5, "Not clearly rewarded", "Uncertain"))
    # share of bootstrap samples where storytelling / maths beat coding on reward
    for d in ["dashboard_story", "maths_stats"]:
        p = (eff_b[:, DIMS.index(d)] > eff_b[:, DIMS.index("coding")]).mean()
        c.log(f"bootstrap: {DN[d]} effect > Coding effect in {100 * p:.1f}% of {B} resamples")
        res.loc[res.skill_area == DN[d], "p_beats_coding"] = p
    c.csv(res, "hype_gap", vfl=True); c.log(res.round(3).to_string(index=False))
    f, ax = plt.subplots(figsize=(9, 6))
    for r in res.itertuples():
        sig = r.d_ci_low > 0
        ax.errorbar(100 * r.demand_share, r.effect_size_d, xerr=[[100 * (r.demand_share - r.demand_ci_low)], [100 * (r.demand_ci_high - r.demand_share)]],
                    yerr=[[r.effect_size_d - r.d_ci_low], [r.d_ci_high - r.effect_size_d]], fmt="o", ms=11, capsize=4, color=BLUE if sig else GREY, lw=1.5)
        ax.annotate(f"{r.skill_area}\nd = {r.effect_size_d:.2f} [{r.d_ci_low:.2f}, {r.d_ci_high:.2f}]", (100 * r.demand_share, r.effect_size_d),
                    textcoords="offset points", fontsize=9, xytext={"Maths & statistics": (-14, -4), "AI & machine learning": (14, -22)}.get(r.skill_area, (14, 4)),
                    ha="right" if r.skill_area == "Maths & statistics" else "left")
    ax.axhline(0.5, ls="--", color=GREY); ax.axvline(100 * res.demand_share.mean(), ls="--", color=GREY)
    ax.text(1, 1.62, "HIDDEN EDGE\nrewarded, rarely asked for", color=GREEN, fontweight="bold", fontsize=9, va="top")
    ax.text(49, 1.62, "CORE\nasked for and rewarded", color="#1E3A8A", fontweight="bold", fontsize=9, va="top", ha="right")
    ax.text(1, -0.02, "NOT CLEARLY REWARDED (d < 0.5)", color=RED, fontweight="bold", fontsize=9)
    ax.set_xlim(0, 50); ax.set_ylim(-0.1, 1.7)
    ax.set_xlabel(f"Market demand: % of core postings asking for it (n = {n:,}), 95% bootstrap CI")
    ax.set_ylabel(f"Reward: effect size d, high- vs low-hike juniors (n = {m}), 95% CI")
    ax.set_title("The hype gap: what job ads ask for vs what juniors are rewarded for")
    c.fig(f, "01_hype_gap_map")
    f, ax = plt.subplots(figsize=(7, 5)); ax.axis("off")
    for r in res.itertuples():
        a, b = 6 - r.demand_rank, 6 - r.reward_rank
        col = GREEN if r.reward_rank < r.demand_rank else (RED if r.reward_rank > r.demand_rank else GREY)
        ax.plot([0, 1], [a, b], "-o", color=col, lw=2.5, ms=9)
        ax.text(-0.05, a, f"#{r.demand_rank} {r.skill_area}", ha="right", va="center")
        ax.text(1.05, b, f"#{r.reward_rank} {r.skill_area}", ha="left", va="center")
    ax.text(0, 5.7, "What job ads ask for", ha="center", fontweight="bold"); ax.text(1, 5.7, "What gets juniors a high hike", ha="center", fontweight="bold")
    ax.set_xlim(-0.9, 1.9); ax.set_ylim(0.5, 6)
    ax.set_title("Ranking flip: demand vs reward (green = under-asked, red = over-asked)")
    c.fig(f, "02_rank_flip")
    SUMMARY["M14"] = res.round(4).to_dict("records")
    c.done()


# ================================================================== M00 data exploration (raw vs clean)
def m00():
    c = Ctx("M00", "data_exploration")
    RAW = WORK.parent
    r_an = pd.read_csv(RAW / "Analytics Jobs.csv")
    log = pd.read_csv(WORK / "outputs" / "data_quality_log.csv", keep_default_na=False)
    prof = pd.read_csv(WORK / "outputs" / "profile_raw.csv")
    # 1 raw missingness
    pm = prof[prof.missing_pct > 0].assign(column=lambda d: d.column.str.strip("'"))
    c.csv(prof.assign(column=prof.column.str.strip("'")), "raw_profile", vfl=True)
    # 2 issues per file / stage
    lg = log[log.rows_affected > 0].groupby(["file", "stage"]).size().reset_index(name="issues")
    c.csv(log, "data_quality_log", vfl=True)
    f, ax = plt.subplots(1, 2, figsize=(14, 4.3), gridspec_kw={"width_ratios": [1.2, 1], "wspace": 0.45})
    piv = lg.pivot(index="stage", columns="file", values="issues").fillna(0)
    piv = piv.reindex(sorted(piv.index, key=lambda s: int(s[1:])))
    bottom = np.zeros(len(piv))
    for col_, colr in zip(piv.columns, [BLUE, GOLD, GREEN, RED]):
        ax[0].bar(piv.index, piv[col_], bottom=bottom, color=colr, label=col_); bottom += piv[col_].values
    ax[0].set_ylabel("Issues found"); ax[0].set_ylim(0, bottom.max() + 4); ax[0].legend(fontsize=8.5, ncol=2, loc="upper left"); ax[0].set_title(f"{int(bottom.sum())} data issues found, by cleaning stage")
    ax[1].barh(pm.column + "\n(" + pm.file + ")", pm.missing_pct, color=RED, height=.5)
    for i, v in enumerate(pm.missing_pct):
        ax[1].text(v + 1, i, f"{v:.1f}%", va="center")
    ax[1].set_xlim(0, 100); ax[1].set_xlabel("% missing in the raw file"); ax[1].set_title("Missing values in the raw data")
    c.fig(f, "01_issues_and_missing")
    # 3 funnel
    fun = pd.DataFrame({"step": ["Raw postings", "Exact duplicates removed", "India sample (no spam, overseas,\nnear-duplicates)",
                                 "Core analytics roles", "Salary-model sample"],
                        "rows": [len(r_an), len(an), int(an.in_india_sample.sum()), len(core), len(sal)]})
    c.csv(fun.assign(step=fun.step.str.replace("\n", " ")), "analytics_jobs_funnel", vfl=True)
    f, ax = plt.subplots(figsize=(9, 3.8))
    ax.barh(fun.step[::-1], fun.rows[::-1], color=[GREY, GREY, "#93C5FD", BLUE, BLUE][::-1])
    for i, v in enumerate(fun.rows[::-1]):
        ax.text(v + 150, i, f"{v:,}", va="center")
    ax.set_xlim(0, 18500); ax.set_xlabel("Postings"); ax.set_title("Analytics Jobs: from raw file to analysis sample (nothing else deleted - flagged)")
    c.fig(f, "02_analytics_jobs_funnel")
    # 4 role families: analytics vs not
    rf = an[an.in_india_sample == 1].role_family.value_counts().reset_index(); rf.columns = ["role_family", "postings"]
    rf["analytics"] = rf.role_family.isin(core.role_family.unique())
    c.csv(rf, "role_family_counts", vfl=True)
    f, ax = plt.subplots(figsize=(9, 6.5))
    ax.barh(rf.role_family[::-1], rf.postings[::-1], color=[BLUE if a else GREY for a in rf.analytics[::-1]])
    ax.set_xlabel("Postings (India sample)"); ax.set_title("Two-thirds of 'Analytics Jobs' are not analytics roles (blue = kept as core)")
    c.fig(f, "03_role_families")
    # 5 salary bands, experience, cities
    sb = sal.salary_band.value_counts().reindex(["0-3 LPA", "3-6 LPA", "6-10 LPA", "10-15 LPA", "15-25 LPA", "25-50 LPA"]).reset_index()
    sb.columns = ["salary_band", "postings"]; c.csv(sb, "salary_band_distribution", vfl=True)
    ct = core.primary_city.value_counts().head(10).reset_index(); ct.columns = ["city", "postings"]; c.csv(ct, "top_cities", vfl=True)
    f, ax = plt.subplots(1, 3, figsize=(15, 4))
    ax[0].bar(sb.salary_band, sb.postings, color=BLUE); ax[0].set_title("Salary bands (core postings)"); ax[0].tick_params(axis="x", rotation=30)
    ax[1].hist(core.exp_mid, bins=range(0, 26), color=GOLD, edgecolor="white"); ax[1].set_title("Experience asked for (mid-point, years)")
    ax[2].barh(ct.city[::-1], ct.postings[::-1], color=GREEN); ax[2].set_title("Top 10 cities (core postings)")
    c.fig(f, "04_salary_experience_city")
    # 6 skills recovered from descriptions (derivation)
    from taxonomy import DIMS as TAX, match_any
    rows = []
    for k in DIMS:
        kws = TAX[k]
        ks = core.skills.fillna("").map(lambda s: any(match_any(x, kws) for x in s.split("|") if x)).mean()
        rows.append(dict(skill_area=DN[k], from_key_skills_only=ks, after_description_recovery=core[f"dim_{k}"].mean()))
    rec = pd.DataFrame(rows); c.csv(rec, "skill_recovery_from_descriptions", vfl=True); c.log(rec.round(3).to_string(index=False))
    f, ax = plt.subplots(figsize=(8.5, 4)); xx = np.arange(5)
    ax.bar(xx - .2, 100 * rec.from_key_skills_only, .4, color=GREY, label="key_skills only (87% truncated)")
    ax.bar(xx + .2, 100 * rec.after_description_recovery, .4, color=BLUE, label="+ skills recovered from descriptions")
    ax.set_xticks(xx); ax.set_xticklabels(rec.skill_area, rotation=12); ax.set_ylabel("% of core postings"); ax.set_ylim(0, 58); ax.legend(loc="upper left")
    ax.set_title("Derivation: recovering skills hidden in job descriptions")
    c.fig(f, "05_skill_recovery")
    # 7 DS jobs skew + log transform
    f, ax = plt.subplots(1, 3, figsize=(15, 4))
    ax[0].hist(ds.num_of_jobs, bins=60, color=GREY); ax[0].set_title("num_of_jobs: raw (max 4,200)"); ax[0].set_yscale("log")
    ax[1].hist(ds.log_num_jobs, bins=40, color=BLUE); ax[1].set_title("num_of_jobs: log-transformed")
    ax[2].hist(ds.avg_salary_lpa, bins=50, color=GOLD); ax[2].axvline(ds.avg_salary_lpa.quantile(.99), color=RED, ls="--", label="99th percentile (winsorising cap)")
    ax[2].legend(fontsize=8.5); ax[2].set_title("Average salary (LPA): long right tail kept")
    c.fig(f, "06_ds_jobs_distributions")
    # 8 JDS ceiling + SDS distributions
    f, ax = plt.subplots(1, 2, figsize=(14, 4.4))
    ax[0].boxplot([jds[JSK[k]] for k in DIMS], tick_labels=[DN[k].replace(" & ", "\n& ") for k in DIMS], patch_artist=True, boxprops=dict(facecolor="#BFDBFE"))
    for i, k in enumerate(DIMS):
        ax[0].text(i + 1, 5.15, f"{100 * (jds[JSK[k]] == 5).mean():.0f}% at 5", ha="center", fontsize=8.5, color=RED)
    ax[0].set_ylim(0.8, 5.4); ax[0].set_title("JDS skill scores: ceiling effect (share scoring a perfect 5)")
    ax[1].boxplot([sds[t] for t in TR], tick_labels=[TN[t] for t in TR], patch_artist=True, boxprops=dict(facecolor="#FDE68A"))
    ax[1].tick_params(axis="x", rotation=15); ax[1].set_title("SDS trait scores (normalised, observed 17-68)")
    c.fig(f, "07_people_data_distributions")
    jd = pd.DataFrame({"skill_area": [DN[k] for k in DIMS], "share_at_5": [(jds[JSK[k]] == 5).mean() for k in DIMS],
                       "mean": [jds[JSK[k]].mean() for k in DIMS]})
    c.csv(jd, "jds_ceiling_effect", vfl=True)
    c.done()


if __name__ == "__main__":
    t0 = time.time()
    steps = {"m00": m00, "m01": m01, "m02": m02, "m03": m03, "m04": m04, "m05": m05, "jds": jds_models, "sds": sds_models, "m14": m14}
    pick = sys.argv[1:] or list(steps)  # e.g. python run_models.py m05 jds sds m14
    sf = HERE / "summary.json"
    if sys.argv[1:] and sf.exists():
        SUMMARY.update(json.loads(sf.read_text(encoding="utf-8")))
    for k in pick:
        steps[k]()
        sf.write_text(json.dumps(SUMMARY, indent=1, default=str), encoding="utf-8")
    print(f"ALL MODELS DONE in {time.time() - t0:.0f}s")
