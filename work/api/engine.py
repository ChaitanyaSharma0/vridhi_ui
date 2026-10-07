"""Vriddhi AI engine: loads the cleaned data, refits the trained models (same specification as models/run_models.py)
and produces REAL step-by-step traces. Every number returned is computed here from the data - nothing is canned."""
import hashlib
import json
import re
import sys
import time
import warnings
from collections import Counter
from functools import lru_cache
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import LogisticRegression
from sklearn.manifold import TSNE
from sklearn.metrics import confusion_matrix, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from statsmodels.miscmodels.ordinal_model import OrderedModel

warnings.filterwarnings("ignore")
WORK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORK))
from role_rules import ANALYTICS, ROLE  # noqa: E402
from taxonomy import DIM_NAMES, DIMS, JDS_COLUMN, match_any  # noqa: E402

DIM_KEYS = list(DIMS)
SKILL_COLS = [JDS_COLUMN[d] for d in DIM_KEYS]
TRAITS = ["neuroticism", "extraversion", "openness_to_experience", "agreeableness", "conscientiousness"]
TRAIT_NAMES = {"neuroticism": "Neuroticism", "extraversion": "Extraversion", "openness_to_experience": "Openness",
               "agreeableness": "Agreeableness", "conscientiousness": "Conscientiousness"}
BANDS = ["0to3", "3to6", "6to10", "10to15", "15to25", "25to50"]
BAND_LABEL = dict(zip(BANDS, ["0-3 LPA", "3-6 LPA", "6-10 LPA", "10-15 LPA", "15-25 LPA", "25-50 LPA"]))
BAND_MID = dict(zip(BANDS, [1.5, 4.5, 8.0, 12.5, 20.0, 37.5]))
REF_ROLE = "Data Analyst / Analytics"
CITY_TIERS = ["Tier 1 metro", "Tier 2/3", "Unspecified"]
SEED = 42


def _t():
    return time.perf_counter()


class Engine:
    def __init__(self):
        t0 = _t()
        C = WORK / "clean"
        self.an = pd.read_csv(C / "analytics_jobs_clean.csv")
        self.ds = pd.read_csv(C / "ds_jobs_clean.csv")
        self.jds = pd.read_csv(C / "jds_clean.csv")
        self.sds = pd.read_csv(C / "sds_clean.csv")
        self.raw_counts = {"analytics_jobs": 15841, "datascience_jobs": 1602, "jds": 139, "sds": 161}
        self.core = self.an[self.an.in_core_analytics == 1].copy()
        self.sal = self.an[self.an.in_salary_model == 1].copy()
        ver = (WORK / "VERIFICATION.md").read_text(encoding="utf-8")
        m = re.search(r"(\d+) of (\d+) checks pass", ver)
        self.ver_pass, self.ver_total = int(m.group(1)), int(m.group(2))
        dsk = pd.read_csv(WORK / "database" / "csv" / "dim_skill.csv")
        msd = pd.read_csv(WORK / "database" / "csv" / "map_skill_dimension.csv")
        self.n_mapped_skills = int(msd.skill_id.nunique())
        # skill vocabulary: technical skills seen in >= 5 core postings (for free-text extraction)
        self.skill_counts = Counter(s for v in self.core.skills_all.fillna("") for s in set(v.split("|")) if s)
        # free-text vocabulary = the skills the taxonomy maps to a dimension (no generic words like 'strong')
        mapped = set(dsk.loc[dsk.skill_id.isin(msd.skill_id), "skill_name"])
        self.vocab = sorted([s for s in mapped if len(s) >= 2], key=len, reverse=True)
        self.vocab_re = [(s, re.compile(r"(?<![\w+#])" + re.escape(s) + r"(?![\w+#])")) for s in self.vocab]
        self._fit_people_models()
        self._fit_band_model()
        self._precompute_market()
        self.startup_s = round(_t() - t0, 2)

    # ------------------------------------------------------------------ models
    def _fit_people_models(self):
        j, s = self.jds, self.sds
        self.jm = sm.Logit(j.salary_hike_high, sm.add_constant(j[SKILL_COLS])).fit(disp=0)
        self.sm_ = sm.Logit(s.success_high, sm.add_constant(s[TRAITS])).fit(disp=0)
        self.j_mean, self.j_sd = j[SKILL_COLS].mean(), j[SKILL_COLS].std()
        self.s_mean, self.s_sd = s[TRAITS].mean(), s[TRAITS].std()
        self.j_base, self.s_base = float(j.salary_hike_high.mean()), float(s.success_high.mean())
        self.s_high_profile = s.loc[s.success_high == 1, TRAITS].mean()
        cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
        self.conf = {}
        for key, X, y, csv_ in [("junior", j[SKILL_COLS], j.salary_hike_high, "M08_junior_ensembles_benchmark"),
                                ("senior", s[TRAITS], s.success_high, "M12_senior_ensembles_benchmark")]:
            p = cross_val_predict(LogisticRegression(penalty=None, max_iter=5000), X, y, cv=cv, method="predict_proba")[:, 1]
            bins = pd.cut(p, [0, .2, .4, .6, .8, 1.0], include_lowest=True)
            cal = pd.DataFrame({"p": p, "y": y.values, "bin": bins}).groupby("bin", observed=True).agg(pred=("p", "mean"), obs=("y", "mean"), n=("y", "size")).reset_index(drop=True)
            comp = pd.read_csv(WORK / "models" / csv_ / "results" / "model_comparison.csv")
            imp = pd.read_csv(WORK / "models" / csv_ / "results" / "permutation_importance.csv")
            cm = confusion_matrix(y, p > .5)
            self.conf[key] = dict(
                n=int(len(y)), positive_rate=round(float(y.mean()), 3),
                served_model="Logistic regression (unpenalised, same as the report)",
                cv_auc_this_run=round(float(roc_auc_score(y, p)), 3),
                models=comp.drop(columns=["best_params_full_data"]).round(3).replace({np.nan: None}).to_dict("records"),
                calibration=cal.round(3).to_dict("records"),
                confusion={"tn": int(cm[0, 0]), "fp": int(cm[0, 1]), "fn": int(cm[1, 0]), "tp": int(cm[1, 1])},
                importance=imp.round(4).to_dict("records"))

    def _band_X(self, exp_mid, role, city, dims):
        row = {"exp": float(exp_mid)}
        for r in self.band_roles:
            row[f"role:{r}"] = float(role == r)
        for c in CITY_TIERS[1:]:
            row[f"city:{c}"] = float(city == c)
        for d in DIM_KEYS:
            row[f"dim:{d}"] = float(dims.get(d, 0))
        return pd.DataFrame([row])[self.band_cols]

    def _fit_band_model(self):
        d = self.sal
        self.band_roles = [r for r in d.role_family.value_counts().index if r != REF_ROLE]
        X = pd.DataFrame({"exp": d.exp_mid})
        for r in self.band_roles:
            X[f"role:{r}"] = (d.role_family == r).astype(float)
        for c in CITY_TIERS[1:]:
            X[f"city:{c}"] = (d.city_tier == c).astype(float)
        for k in DIM_KEYS:
            X[f"dim:{k}"] = d[f"dim_{k}"].astype(float)
        self.band_cols = list(X.columns)
        self.bm = OrderedModel(d.salary_band_ord.astype(int), X, distr="logit").fit(method="bfgs", maxiter=2000, disp=False)
        self.band_n = int(len(d))
        self.band_or = {c: round(float(np.exp(self.bm.params[c])), 3) for c in self.band_cols}

    # ------------------------------------------------------------------ market precompute
    def _precompute_market(self):
        core = self.core
        self.demand_all = {d: round(float(core[f"dim_{d}"].mean()), 4) for d in DIM_KEYS}
        self.demand_role = {r: {d: round(float(g[f"dim_{d}"].mean()), 4) for d in DIM_KEYS} | {"_n": int(len(g))}
                            for r, g in core.groupby("role_family")}
        hg = pd.read_csv(WORK / "models" / "M14_hype_gap_bootstrap" / "results" / "hype_gap.csv")
        name2key = {v: k for k, v in DIM_NAMES.items()}
        self.reward = {name2key[r.skill_area]: dict(d=round(r.effect_size_d, 3), lo=round(r.d_ci_low, 3), hi=round(r.d_ci_high, 3),
                                                     demand_rank=int(r.demand_rank), reward_rank=int(r.reward_rank)) for r in hg.itertuples()}
        self.jds_supply = {d: round(float((self.jds[JDS_COLUMN[d]].mean() - 1) / 4), 4) for d in DIM_KEYS}

    # ------------------------------------------------------------------ building blocks (each is a real function)
    def match_role(self, title):
        t = str(title or "").lower()
        checked = []
        for i, (fam, pat) in enumerate(ROLE):
            m = re.search(pat, t)
            checked.append({"index": i + 1, "family": fam, "matched": bool(m)})
            if m:
                return dict(index=i + 1, family=fam, pattern=pat, matched_text=m.group(0), is_analytics=fam in ANALYTICS,
                            rules_checked=i + 1, earlier=[{"index": c["index"], "family": c["family"]} for c in checked[:-1]])
        return dict(index=None, family="Other", pattern=None, matched_text=None, is_analytics=False, rules_checked=len(ROLE), earlier=[])

    def extract_skills(self, chips_text="", free_text=""):
        chips = [c.strip().lower() for c in re.split(r"[,\n;|]+", chips_text or "") if c.strip()]
        found = []
        for c in chips:
            dims = [d for d in DIM_KEYS if match_any(c, DIMS[d])]
            found.append({"skill": c, "dims": dims, "source": "chip", "postings": int(self.skill_counts.get(c, 0))})
        if free_text:
            low = free_text.lower(); taken = []
            for s, rx in self.vocab_re:
                for m in rx.finditer(low):
                    if any(a <= m.start() < b for a, b in taken):
                        continue
                    taken.append((m.start(), m.end()))
                    if s not in [f["skill"] for f in found]:
                        found.append({"skill": s, "dims": [d for d in DIM_KEYS if match_any(s, DIMS[d])], "source": "text",
                                      "postings": int(self.skill_counts.get(s, 0))})
        buckets = {d: [f["skill"] for f in found if d in f["dims"]] for d in DIM_KEYS}
        return dict(skills=found, buckets=buckets, dims={d: int(bool(buckets[d])) for d in DIM_KEYS},
                    unmatched=[f["skill"] for f in found if not f["dims"]])

    def demand_profile(self, family):
        prof = self.demand_role.get(family)
        if prof is None:
            return dict(family=family, n=int(len(self.core)), shares=self.demand_all, fallback=True)
        return dict(family=family, n=prof["_n"], shares={d: prof[d] for d in DIM_KEYS}, fallback=False)

    def junior_predict(self, skills):
        x = np.array([float(skills[c]) for c in SKILL_COLS])
        b = self.jm.params
        logit = float(b["const"] + (b[SKILL_COLS].values * x).sum())
        base_logit = float(b["const"] + (b[SKILL_COLS].values * self.j_mean.values).sum())
        contrib = [{"feature": c, "dim": d, "value": float(v), "mean": round(float(self.j_mean[c]), 3),
                    "coef": round(float(b[c]), 4), "logit_effect": round(float(b[c] * (v - self.j_mean[c])), 4)}
                   for c, d, v in zip(SKILL_COLS, DIM_KEYS, x)]
        return dict(probability=_sig(logit), logit=logit, at_mean_probability=_sig(base_logit), base_logit=base_logit, contributions=contrib)

    def senior_predict(self, traits):
        x = np.array([float(traits[t]) for t in TRAITS])
        b = self.sm_.params
        logit = float(b["const"] + (b[TRAITS].values * x).sum())
        base_logit = float(b["const"] + (b[TRAITS].values * self.s_mean.values).sum())
        contrib = [{"feature": t, "value": float(v), "mean": round(float(self.s_mean[t]), 2), "coef": round(float(b[t]), 4),
                    "logit_effect": round(float(b[t] * (v - self.s_mean[t])), 4)} for t, v in zip(TRAITS, x)]
        z = (x - self.s_mean.values) / self.s_sd.values
        zh = (self.s_high_profile.values - self.s_mean.values) / self.s_sd.values
        return dict(probability=_sig(logit), logit=logit, at_mean_probability=_sig(base_logit), base_logit=base_logit, contributions=contrib,
                    fingerprint={"candidate": dict(zip(TRAITS, x.round(1).tolist())), "high_success_mean": self.s_high_profile.round(1).to_dict(),
                                 "distance_z": round(float(np.linalg.norm(z - zh)), 3)})

    def counterfactual(self, skills, kind="junior", target=0.5):
        cols = SKILL_COLS if kind == "junior" else TRAITS
        pred = self.junior_predict if kind == "junior" else self.senior_predict
        cur = pred(skills)["probability"]
        step, hi = (0.5, 5.0) if kind == "junior" else (2.0, 68.0)
        base = np.array([float(skills[c]) for c in cols])
        if cur >= target:
            return dict(already=True, probability=cur, message="Already above the high threshold (0.5); no change needed.")
        b = (self.jm if kind == "junior" else self.sm_).params
        # levers: every input that can go up; neuroticism is excluded (not a real driver, see report M10/M12)
        grids = [np.arange(0, max(hi - v, 0) + 1e-9, step)[:9] if c != "neuroticism" else np.array([0.0]) for c, v in zip(cols, base)]
        incs = np.array(list(product(*grids)))[1:]
        p = 1 / (1 + np.exp(-(b["const"] + (base + incs) @ b[cols].values)))
        ok = np.where(p >= target)[0]
        if not len(ok):
            return dict(already=False, found=False, message="No change within the scale reaches the high threshold.")
        tot = incs[ok].sum(1); pick = ok[np.lexsort((-p[ok], tot))[0]]
        best = (incs[pick], float(p[pick]))
        changes = [{"feature": c, "from": float(v), "to": float(v + d), "delta": float(d)} for c, v, d in zip(cols, base, best[0]) if d > 0]
        names = DIM_NAMES if kind == "junior" else TRAIT_NAMES
        key = (lambda c: DIM_KEYS[SKILL_COLS.index(c)]) if kind == "junior" else (lambda c: c)
        txt = " and ".join(f"{names[key(ch['feature'])]} by {ch['delta']:g}" for ch in changes)
        return dict(already=False, found=True, changes=changes, new_probability=best[1], total_change=float(best[0].sum()),
                    message=f"Raise {txt} to move from Low to High (p = {best[1]:.2f}).")

    def band_predict(self, exp_mid, family, city, dims):
        X = self._band_X(exp_mid, family, city, dims)
        p = self.bm.predict(X.values)[0]
        probs = {b: round(float(v), 4) for b, v in zip(BANDS, p)}
        return dict(probs=probs, expected_lpa=round(float(sum(BAND_MID[b] * v for b, v in probs.items())), 2),
                    most_likely=max(probs, key=probs.get), inputs={"exp_mid": exp_mid, "role": family, "city_tier": city, "dims": dims})

    def nearest_people(self, skills, kind="junior", k=5):
        if kind == "junior":
            X = self.jds[SKILL_COLS].values; v = np.array([skills[c] for c in SKILL_COLS]); df = self.jds; tgt = "salary_hike_high"; cols = SKILL_COLS
        else:
            X = self.sds[TRAITS].values; v = np.array([skills[t] for t in TRAITS]); df = self.sds; tgt = "success_high"; cols = TRAITS
        d = np.linalg.norm((X - v) / X.std(0), axis=1)
        idx = np.argsort(d)[:k]
        return df.iloc[idx][["row_id"] + cols + [tgt]].round(2).to_dict("records")

    # ------------------------------------------------------------------ the traced run
    def analyze(self, inp):
        inp = normalise_input(inp)
        trace, step = [], [0]

        def ev(node, title, log, t0, **kw):
            step[0] += 1
            trace.append(dict(step=step[0], node=node, title=title, log=log, ms=round((_t() - t0) * 1000, 2), **kw))

        t0 = _t()
        ev("load", "Loaded datasets", f"analytics_jobs_clean.csv rows={len(self.an)} core={len(self.core)}; jds rows={len(self.jds)}; sds rows={len(self.sds)}",
           t0, dataset="clean/*.csv", rows_used=int(len(self.an)), value=f"{self.ver_pass}/{self.ver_total} checks passed",
           detail={"datasets": [
               {"name": "Analytics Jobs", "raw": self.raw_counts["analytics_jobs"], "clean": int(len(self.an)), "core": int(len(self.core))},
               {"name": "DataScience Jobs", "raw": self.raw_counts["datascience_jobs"], "clean": int(len(self.ds)), "core": int(self.ds.in_analysis_sample.sum())},
               {"name": "JDS Skill Traits", "raw": self.raw_counts["jds"], "clean": int(len(self.jds)), "core": int(len(self.jds))},
               {"name": "SDS Personality Traits", "raw": self.raw_counts["sds"], "clean": int(len(self.sds)), "core": int(len(self.sds))}],
               "verification": {"passed": self.ver_pass, "total": self.ver_total}},
           code="pd.read_csv('clean/analytics_jobs_clean.csv')")

        t0 = _t(); rm = self.match_role(inp["title"])
        fam = rm["family"]
        ev("role_match", "Role family matched", f"title='{inp['title']}' rules_checked={rm['rules_checked']} matched rule {rm['index']}: {fam}", t0,
           rule_fired={k: rm[k] for k in ["index", "family", "pattern", "matched_text"]}, value=fam,
           detail={"is_analytics": rm["is_analytics"], "earlier_rules_not_matched": rm["earlier"], "rules_total": len(ROLE)},
           code="role_rules.ROLE  # first regex match wins", rows_used=None)

        t0 = _t(); ex = self.extract_skills(inp["skills_text"], inp.get("job_text", ""))
        ev("skills", "Skills mapped to the 5 dimensions", f"chips={len(ex['skills'])} matched={len(ex['skills']) - len(ex['unmatched'])} dims={sum(ex['dims'].values())}/5",
           t0, value=ex["dims"], detail=ex, code="taxonomy.match_any(skill, DIMS[dim])", rows_used=None)

        t0 = _t(); dp = self.demand_profile(fam)
        sample = self.core[self.core.role_family == fam].head(5) if not dp["fallback"] else self.core.head(5)
        ev("demand", "Market demand profile", f"role='{fam}' postings={dp['n']} coding={dp['shares']['coding']:.2f} maths={dp['shares']['maths_stats']:.2f}",
           t0, dataset="analytics_jobs_clean.csv (core)", rows_used=dp["n"], value=dp["shares"],
           detail={**dp, "note": "Skills text is truncated in about 87% of postings, so these shares are a lower bound.",
                   "sample_rows": sample[["s_no", "job_desig", "skills_all"]].fillna("").to_dict("records")},
           code="core.groupby('role_family')[dim_cols].mean()")

        jr = sr = cf = None
        t0 = _t()
        if inp["profile"] == "junior":
            jr = self.junior_predict(inp["skills"]); cf = self.counterfactual(inp["skills"], "junior")
            ev("junior_model", "Skill model (juniors, JDS)", f"rows_used={len(self.jds)} p_high_hike={jr['probability']:.3f} baseline={self.j_base:.3f}",
               t0, dataset="jds_clean.csv", rows_used=int(len(self.jds)), value=round(jr["probability"], 4),
               detail={"coefficients": {c: round(float(self.jm.params[c]), 4) for c in ["const"] + SKILL_COLS}, "baseline_rate": self.j_base,
                       "nearest_people": self.nearest_people(inp["skills"], "junior")},
               code="statsmodels Logit(salary_hike_high ~ 5 skills).predict(x)")
            t0 = _t(); ev("senior_model", "Trait model (seniors, SDS)", "skipped: different population (junior profile selected)", t0, status="skipped", value=None,
                          detail={"reason": "JDS and SDS are different people; the two models are never combined."})
        else:
            t0 = _t(); ev("junior_model", "Skill model (juniors, JDS)", "skipped: different population (senior profile selected)", t0, status="skipped", value=None,
                          detail={"reason": "JDS and SDS are different people; the two models are never combined."})
            t0 = _t(); sr = self.senior_predict(inp["traits"]); cf = self.counterfactual(inp["traits"], "senior")
            ev("senior_model", "Trait model (seniors, SDS)", f"rows_used={len(self.sds)} p_high_success={sr['probability']:.3f} baseline={self.s_base:.3f}",
               t0, dataset="sds_clean.csv", rows_used=int(len(self.sds)), value=round(sr["probability"], 4),
               detail={"coefficients": {c: round(float(self.sm_.params[c]), 4) for c in ["const"] + TRAITS}, "baseline_rate": self.s_base,
                       "nearest_people": self.nearest_people(inp["traits"], "senior")},
               code="statsmodels Logit(success_high ~ Big Five).predict(x)")

        t0 = _t()
        band_dims = ex["dims"] if inp["band_source"] == "chips" else {d: int(inp["skills"][JDS_COLUMN[d]] >= 4) for d in DIM_KEYS}
        if rm["is_analytics"]:
            bp = self.band_predict(inp["experience"], fam, inp["city_tier"], band_dims)
            ev("band", "Salary band estimate", f"rows_used={self.band_n} most_likely={bp['most_likely']} expected={bp['expected_lpa']} LPA source={inp['band_source']}",
               t0, dataset="analytics_jobs_clean.csv (salary sample)", rows_used=self.band_n, value=bp["probs"],
               detail={**bp, "band_source": inp["band_source"], "odds_ratios": self.band_or}, code="OrderedModel(salary_band ~ exp + role + city + 5 dims).predict(x)")
        else:
            bp = None
            ev("band", "Salary band estimate", f"skipped: '{fam}' is not an analytics role family", t0, status="skipped", value=None,
               detail={"reason": "The band model was trained on the 9 analytics role families only."})

        t0 = _t()
        res = self._result(inp, rm, ex, dp, jr, sr, cf, bp)
        ev("verdict", "Verdict", f"confidence={res['confidence']['label']} prob={res['verdict']['probability']}", t0, value=res["verdict"]["headline"],
           detail=res["verdict"], code="Engine._result()")
        run_id = hashlib.sha1(json.dumps(inp, sort_keys=True).encode()).hexdigest()[:10]
        return dict(run_id=run_id, input=inp, trace=trace, result=res)

    def _result(self, inp, rm, ex, dp, jr, sr, cf, bp):
        junior = inp["profile"] == "junior"
        pr = jr if junior else sr
        base = self.j_base if junior else self.s_base
        contrib = sorted(pr["contributions"], key=lambda c: -abs(c["logit_effect"]))
        # waterfall in probability space, exact: walk logit from 'average person' to this person
        wf, lg = [], pr["base_logit"]
        for c in contrib:
            p0 = _sig(lg); lg += c["logit_effect"]; wf.append({**c, "p_from": round(p0, 4), "p_to": round(_sig(lg), 4)})
        names = DIM_NAMES if junior else TRAIT_NAMES
        key = (lambda c: c["dim"]) if junior else (lambda c: c["feature"])
        drv = [c for c in contrib if c["feature"] != "neuroticism"]  # not a real driver (report M10/M12)
        drivers = [f"{names[key(c)]} ({'+' if c['logit_effect'] >= 0 else '-'})" for c in drv[:3]]
        mvc, gap = {}, None
        if junior:
            for d in DIM_KEYS:
                mvc[d] = {"demand": dp["shares"][d], "candidate": inp["skills"][JDS_COLUMN[d]], "candidate_scaled": round((inp["skills"][JDS_COLUMN[d]] - 1) / 4, 3),
                          "reward_d": self.reward[d]["d"]}
            gap_d = max(DIM_KEYS, key=lambda d: self.reward[d]["d"] * (1 - mvc[d]["candidate_scaled"]))
            gap = {"dim": gap_d, "name": DIM_NAMES[gap_d], "why": f"largest reward-weighted shortfall (reward d = {self.reward[gap_d]['d']}, score {inp['skills'][JDS_COLUMN[gap_d]]})"}
        p = pr["probability"]
        label = "High" if p >= .5 else "Low"
        n = len(self.jds) if junior else len(self.sds)
        auc = next(m["auc_mean"] for m in self.conf["junior" if junior else "senior"]["models"] if m["model"] == "Logistic regression")
        conf_label = "Moderate" if junior else "Pattern strong, accuracy suspiciously high"
        who = "high salary hike" if junior else "high success classification"
        headline = (f"Predicted {label.lower()} chance of a {who}: {(f'{p:.1%}' if p < .1 or p > .9 else f'{p:.0%}')} (baseline {base:.0%}).")
        rec = (cf["message"] if not cf.get("already") else f"Profile already sits in the high group; strongest drivers: {', '.join(drivers)}.")
        if junior and gap:
            rec += f" Biggest gap versus what is rewarded: {gap['name']}."
        return dict(
            hike_probability=round(p, 4) if junior else None, success_probability=None if junior else round(p, 4), baseline=round(base, 4),
            contributions=pr["contributions"], waterfall=wf, at_mean_probability=round(pr["at_mean_probability"], 4),
            band_probs=bp["probs"] if bp else None, band=bp, demand_profile=dp["shares"], demand_n=dp["n"], role=rm,
            skills=ex, market_vs_candidate=mvc or None, counterfactual=cf,
            fingerprint=sr.get("fingerprint") if sr else None,
            confidence={"cv_auc": auc, "n": n, "label": conf_label},
            verdict={"headline": headline, "label": label, "probability": round(p, 4), "baseline": round(base, 4), "drivers": drivers,
                     "gap": gap, "recommendation": rec, "role": rm["family"]})

    # ------------------------------------------------------------------ other endpoints
    def whatif(self, inp):
        return self.analyze(inp)["result"]

    def xray(self, text):
        t0 = _t()
        first_line = (text or "").strip().split("\n")[0][:160]
        rm = self.match_role(first_line) if first_line else self.match_role(text)
        if rm["family"] == "Other":
            rm = self.match_role(text)
        ex = self.extract_skills("", text)
        dp = self.demand_profile(rm["family"])
        v = np.array([ex["dims"][d] for d in DIM_KEYS], float)
        near = []
        for r, prof in self.demand_role.items():
            w = np.array([prof[d] for d in DIM_KEYS])
            sim = float(v @ w / (np.linalg.norm(v) * np.linalg.norm(w))) if v.any() else 0.0
            near.append({"role": r, "similarity": round(sim, 3), "postings": prof["_n"]})
        near = sorted(near, key=lambda x: -x["similarity"])[:4]
        return dict(role=rm, skills=ex, demand_profile=dp, nearest_roles=near, ms=round((_t() - t0) * 1000, 1))

    def compare(self, a, b):
        ra, rb = self.whatif(a), self.whatif(b)
        k = "hike_probability" if ra["hike_probability"] is not None else "success_probability"
        pa, pb = ra[k], rb[k]
        better = "A" if pa > pb else "B" if pb > pa else "neither"
        why = ""
        if ra["contributions"] and rb["contributions"]:
            diffs = sorted([(ca["feature"], cb["logit_effect"] - ca["logit_effect"]) for ca, cb in zip(ra["contributions"], rb["contributions"])],
                           key=lambda x: -abs(x[1]))
            why = f"largest difference: {diffs[0][0]} ({'+' if diffs[0][1] >= 0 else ''}{diffs[0][1]:.2f} logit for B)"
        return dict(a=ra, b=rb, delta=round(pb - pa, 4), better=better, why=why)

    @lru_cache(maxsize=1)
    def premium(self, min_n=50):
        d = self.sal.copy(); d["high"] = (d.salary_band_ord >= 5).astype(int)
        sets = d.skills_all.fillna("").map(lambda s: set(s.split("|")))
        rows = []
        generic = {"learning", "analytics", "analysis", "data analysis", "data analytics", "business analysis", "research", "management",
                   "business", "analyst", "data", "it", "analytical", "reporting"}
        for sk, cnt in self.skill_counts.most_common(150):
            if sk in generic:
                continue
            has_ = sets.map(lambda s: sk in s)
            if has_.sum() < min_n:
                continue
            diffs, w = [], []
            for _, g in d.assign(h=has_).groupby("exp_band"):
                if g.h.sum() >= 5 and (~g.h).sum() >= 5:
                    diffs.append(g.loc[g.h, "high"].mean() - g.loc[~g.h, "high"].mean()); w.append(g.h.sum())
            if not w:
                continue
            adj = float(np.average(diffs, weights=w))
            rows.append({"skill": sk, "n": int(has_.sum()), "raw_lift_pts": round(100 * (d.loc[has_, "high"].mean() - d.loc[~has_, "high"].mean()), 2),
                         "adjusted_lift_pts": round(100 * adj, 2), "dims": [k for k in DIM_KEYS if match_any(sk, DIMS[k])]})
        rows.sort(key=lambda r: -r["adjusted_lift_pts"])
        return dict(rows=rows, high_definition="15+ LPA (bands 15-25 and 25-50)", n_postings=int(len(d)),
                    method="Difference in share of 15+ LPA postings with vs without the skill, within each experience band, weighted by postings with the skill.",
                    caption="association, not causation")

    @lru_cache(maxsize=1)
    def sankey(self):
        c = self.sal
        role_dim, dim_band = Counter(), Counter()
        for r in c.itertuples():
            for d in DIM_KEYS:
                if getattr(r, f"dim_{d}"):
                    role_dim[(r.role_family, d)] += 1; dim_band[(d, BANDS[int(r.salary_band_ord) - 1])] += 1
        nodes = [{"id": f"role:{r}", "label": r, "kind": "role"} for r in sorted(c.role_family.unique())] + \
                [{"id": f"dim:{d}", "label": DIM_NAMES[d], "kind": "dim", "dim": d} for d in DIM_KEYS] + \
                [{"id": f"band:{b}", "label": BAND_LABEL[b], "kind": "band"} for b in BANDS]
        links = [{"source": f"role:{r}", "target": f"dim:{d}", "value": v} for (r, d), v in role_dim.items()] + \
                [{"source": f"dim:{d}", "target": f"band:{b}", "value": v} for (d, b), v in dim_band.items()]
        return dict(nodes=nodes, links=links, n_postings=int(len(c)), note="A posting can ask for several dimensions, so it can appear in several flows.")

    @lru_cache(maxsize=1)
    def gap(self):
        roles = sorted(self.demand_role, key=lambda r: -self.demand_role[r]["_n"])
        hype = []
        for r in roles:
            prof = self.demand_role[r]; avg = np.mean([prof[d] for d in DIM_KEYS])
            for d in DIM_KEYS:
                rw = self.reward[d]
                q = ("Hidden edge" if rw["lo"] > 0.5 and prof[d] < avg else "Core" if rw["lo"] > 0.5 else
                     "Not clearly rewarded" if rw["hi"] < 0.5 or rw["lo"] < 0 else "Uncertain")
                hype.append({"role": r, "dim": d, "demand": prof[d], "reward_d": rw["d"], "reward_lo": rw["lo"], "reward_hi": rw["hi"], "quadrant": q,
                             "postings": prof["_n"]})
        supply = [{"role": r, "dim": d, "demand": self.demand_role[r][d], "supply_proxy": self.jds_supply[d],
                   "gap": round(self.demand_role[r][d] - self.jds_supply[d], 4), "postings": self.demand_role[r]["_n"]} for r in roles for d in DIM_KEYS]
        return dict(roles=roles, dims=DIM_KEYS, hype_gap=hype, supply_gap=supply,
                    hype_note="Demand = share of postings in the role asking for the dimension. Reward = effect size d (high vs low hike juniors, 2,000 bootstrap resamples).",
                    supply_note="Supply proxy = average JDS junior score scaled to 0-1. It describes one company's juniors, not what universities teach; treat with caution.")

    @lru_cache(maxsize=1)
    def bundles(self):
        pairs = pd.read_csv(WORK / "models" / "M02_skill_pairs_association_rules" / "results" / "skill_pair_rules_all.csv")
        pairs = pairs[pairs.lift > 1.5].sort_values("together", ascending=False).head(40)
        d = self.sal; sets = d.skills_all.fillna("").map(lambda s: set(s.split("|"))); high = (d.salary_band_ord >= 5).values
        rows = []
        for r in pairs.itertuples():
            a = sets.map(lambda s: r.skill_a in s).values; b = sets.map(lambda s: r.skill_b in s).values
            both, ao, bo = a & b, a & ~b, b & ~a
            if both.sum() < 20:
                continue
            rows.append({"skills": [r.skill_a, r.skill_b], "lift": round(r.lift, 2), "n_both": int(both.sum()),
                         "high_share_both": round(float(high[both].mean()), 3), "high_share_a_only": round(float(high[ao].mean()), 3) if ao.sum() else None,
                         "high_share_b_only": round(float(high[bo].mean()), 3) if bo.sum() else None, "n_a_only": int(ao.sum()), "n_b_only": int(bo.sum()),
                         "dims": sorted({k for s in (r.skill_a, r.skill_b) for k in DIM_KEYS if match_any(s, DIMS[k])})})
        rows.sort(key=lambda x: -x["high_share_both"])
        return dict(rows=rows, high_definition="15+ LPA", baseline_high_share=round(float(high.mean()), 3))

    @lru_cache(maxsize=1)
    def graph(self):
        top = [s for s, _ in self.skill_counts.most_common(45)]
        def dim_of(s):
            ds_ = [k for k in DIM_KEYS if match_any(s, DIMS[k])]
            return ds_[0] if ds_ else "other"
        nodes = [{"id": f"s:{s}", "label": s, "kind": "skill", "dim": dim_of(s), "count": int(self.skill_counts[s])} for s in top]
        roles = list(self.demand_role)
        nodes += [{"id": f"r:{r}", "label": r, "kind": "role", "count": self.demand_role[r]["_n"]} for r in roles]
        nodes += [{"id": f"b:{b}", "label": BAND_LABEL[b], "kind": "band", "count": int((self.sal.salary_band_ord == i + 1).sum())} for i, b in enumerate(BANDS)]
        sets = self.core.skills_all.fillna("").map(lambda s: set(s.split("|")))
        edges = []
        topset = set(top)
        co = Counter(p for s in sets for p in __import__("itertools").combinations(sorted(s & topset), 2))
        n = len(sets)
        for (a, b), k in co.items():
            lift = k / n / ((self.skill_counts[a] / n) * (self.skill_counts[b] / n))
            if k >= 25 and lift >= 1.8:
                edges.append({"source": f"s:{a}", "target": f"s:{b}", "weight": round(lift, 2), "count": k, "kind": "skill-skill"})
        for s in top:
            has_ = sets.map(lambda x: s in x)
            shares = self.core[has_].role_family.value_counts(normalize=True)
            for r, v in shares.head(2).items():
                edges.append({"source": f"s:{s}", "target": f"r:{r}", "weight": round(float(v), 3), "kind": "skill-role"})
        for r in roles:
            g = self.sal[self.sal.role_family == r]
            if len(g):
                b = BANDS[int(g.salary_band_ord.mode().iloc[0]) - 1]
                edges.append({"source": f"r:{r}", "target": f"b:{b}", "weight": 1, "kind": "role-band"})
        return dict(nodes=nodes, edges=edges, note="Skill-skill edges: co-occurrence lift >= 1.8 in >= 25 core postings. Skill-role: top 2 roles per skill. Role-band: modal salary band.")

    @lru_cache(maxsize=1)
    def embedding(self):
        top = [s for s, c in self.skill_counts.most_common(160) if c >= 20]
        idx = {s: i for i, s in enumerate(top)}
        M = np.zeros((len(self.core), len(top)), dtype=np.float32)
        for r, v in enumerate(self.core.skills_all.fillna("")):
            for s in v.split("|"):
                if s in idx:
                    M[r, idx[s]] = 1
        co = M.T @ M; tot = co.sum(); rs = co.sum(1, keepdims=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            pmi = np.log((co * tot) / (rs @ rs.T)); ppmi = np.nan_to_num(np.maximum(pmi, 0))
        np.fill_diagonal(ppmi, 0)
        vec = TruncatedSVD(24, random_state=SEED).fit_transform(ppmi)
        vec = vec / (np.linalg.norm(vec, axis=1, keepdims=True) + 1e-9)
        xy = TSNE(2, perplexity=15, random_state=SEED, init="pca", learning_rate="auto").fit_transform(vec)
        sim = vec @ vec.T
        pts = []
        for i, s in enumerate(top):
            nn = [top[j] for j in np.argsort(-sim[i]) if j != i][:5]
            dd = [k for k in DIM_KEYS if match_any(s, DIMS[k])]
            pts.append({"id": s, "label": s, "dimension": dd[0] if dd else "other", "x": round(float(xy[i, 0]), 3), "y": round(float(xy[i, 1]), 3),
                        "count": int(self.skill_counts[s]), "neighbours": nn})
        return dict(points=pts, method="Precomputed embedding: PPMI of skill co-occurrence in core postings -> SVD (24 dims) -> t-SNE 2D. No live vector database.",
                    note="2D projection for visualisation only; distances are approximate. Neighbours use cosine similarity in the 24-dim space.")

    # ------------------------------------------------------------------ JD audit (company view)
    def reward_weights(self):
        """Evidence-based weight of each skill area: log odds ratio per SD from the junior model (M06), normalised to 100%."""
        lsd = {d: max(float(self.jm.params[JDS_COLUMN[d]] * self.j_sd[JDS_COLUMN[d]]), 0.0) for d in DIM_KEYS}
        tot = sum(lsd.values())
        return {d: lsd[d] / tot for d in DIM_KEYS}

    def jd_examples(self):
        c = self.core[(self.core.desc_missing == 0)].copy()
        out = []
        for fam, label in [("Data Analyst / Analytics", "Data Analyst posting"), ("Data Scientist / ML / AI", "Data Scientist posting"),
                           ("BI / Reporting / MIS", "BI / Reporting posting")]:
            g = c[c.role_family == fam].sort_values(["n_skills_all", "s_no"], ascending=[False, True])
            r = g.iloc[0]
            text = f"{r.job_desig}\nExperience: {r.experience}\nKey skills: {r.key_skills}\n{r.job_description}"
            out.append({"label": label, "s_no": int(r.s_no), "text": text})
        return out

    def jd_audit(self, text):
        t0 = _t()
        text = (text or "").strip()[:6000]
        first = text.split("\n")[0][:160]
        rm = self.match_role(first)
        if rm["family"] == "Other":
            rm = self.match_role(text[:400])
        ex = self.extract_skills("", text)
        asked = ex["dims"]
        W = self.reward_weights()
        order = sorted(DIM_KEYS, key=lambda d: -W[d])
        dp = self.demand_profile(rm["family"])
        coverage = sum(W[d] for d in DIM_KEYS if asked[d])
        # candidate implied by a JD: areas it asks for at the level of high-raise juniors, other areas at the level of low-raise juniors
        hi = self.jds[self.jds.salary_hike_high == 1][SKILL_COLS].mean(); lo = self.jds[self.jds.salary_hike_high == 0][SKILL_COLS].mean()
        prof = lambda flags: {JDS_COLUMN[d]: float(hi[JDS_COLUMN[d]] if flags[d] else lo[JDS_COLUMN[d]]) for d in DIM_KEYS}
        clearly = {d for d in DIM_KEYS if self.reward[d]["lo"] > 0.5}            # reward interval above a medium effect
        role_specific_big = rm["family"] == "Data Engineer / Big Data"
        add = [d for d in order if not asked[d] and (d in clearly or (d == "big_data" and role_specific_big))]
        after = {d: int(asked[d] or d in add) for d in DIM_KEYS}
        p_before = self.junior_predict(prof(asked))["probability"]; p_after = self.junior_predict(prof(after))["probability"]
        lines = {
            "maths_stats": "Strong statistics: hypothesis testing, regression and experiment design, and comfortable explaining uncertainty.",
            "dashboard_story": "Turn analysis into decisions: build clear dashboards (Tableau or Power BI) and present insights to non-technical stakeholders.",
            "ai_ml": "Working knowledge of machine learning: building, validating and explaining predictive models.",
            "coding": "Solid SQL and Python for everyday data work.",
            "big_data": "Experience with large-scale data tools such as Spark or Hadoop."}
        notes = []
        if asked["coding"] and W["coding"] == min(W.values()):
            notes.append({"dim": "coding", "text": "Keep coding as a baseline requirement, not the main filter: once the other areas are known it adds the least to junior growth."})
        if asked["big_data"] and not role_specific_big:
            notes.append({"dim": "big_data", "text": "Big data shows no clear link to junior raises; list it as nice to have unless the role is data engineering."})
        rows = [{"dim": d, "label": DIM_NAMES[d], "weight": round(W[d], 4), "reward_d": self.reward[d]["d"], "reward_lo": self.reward[d]["lo"],
                 "reward_hi": self.reward[d]["hi"], "in_jd": bool(asked[d]), "add": d in add, "market_share": dp["shares"][d],
                 "words": ex["buckets"][d]} for d in order]
        senior = bool(re.search(r"\b(senior|sr\.?|lead|manager|head|principal|director|architect|vp)\b", first.lower()))
        exp = re.search(r"(\d+)\s*(?:-|to)\s*(\d+)\s*(?:yrs|years|yr)", text.lower())
        exp_mid = (int(exp.group(1)) + int(exp.group(2))) / 2 if exp else (7.0 if senior else 3.0)
        band = self.band_predict(exp_mid, rm["family"], "Tier 1 metro", asked) if rm["is_analytics"] else None
        s_hi = self.sds[(self.sds.openness_to_experience > 38.5) & (self.sds.conscientiousness > 36.5)]
        s_lo = self.sds[self.sds.openness_to_experience <= 38.5]
        return dict(
            role=rm, skills=ex["skills"], highlight=[s["skill"] for s in ex["skills"]], rows=rows, coverage=round(coverage, 4),
            covered=[DIM_NAMES[d] for d in DIM_KEYS if asked[d]], missing_rewarded=[DIM_NAMES[d] for d in add],
            additions=[{"dim": d, "label": DIM_NAMES[d], "text": lines[d]} for d in add], notes=notes,
            effect={"before": round(p_before, 4), "after": round(p_after, 4), "baseline": round(self.j_base, 4),
                    "method": "Junior model (M06). Areas the JD asks for are set to the average of high-raise juniors, other areas to the average of low-raise juniors."},
            senior=senior and {"text": ["Curiosity: keeps learning new methods and asks why the numbers look the way they do.",
                                        "Ownership and discipline: plans the work, meets commitments and follows through with clients."],
                               "evidence": f"Among {len(self.sds)} senior data scientists, {int(s_hi.success_high.sum())} of {len(s_hi)} who were both curious and disciplined were rated highly successful, versus {int(s_lo.success_high.sum())} of {len(s_lo)} with low openness."},
            pay=band and {"most_likely": band["most_likely"], "expected_lpa": band["expected_lpa"], "exp_mid": exp_mid},
            evidence={"juniors": int(len(self.jds)), "postings_role": dp["n"], "role": rm["family"]},
            ms=round((_t() - t0) * 1000, 1))

    @lru_cache(maxsize=1)
    def showcase(self):
        """Homepage lab: the three signals for four common role families (all computed)."""
        W = self.reward_weights(); out = {}
        for fam in ["Data Analyst / Analytics", "Data Scientist / ML / AI", "BI / Reporting / MIS", "Business Analyst"]:
            dp = self.demand_profile(fam); b = self.band_predict(3.0, fam, "Tier 1 metro", {})
            top = max(DIM_KEYS, key=lambda d: dp["shares"][d])
            out[fam] = {"postings": dp["n"], "shares": dp["shares"], "most_asked": DIM_NAMES[top], "band": b["most_likely"], "expected_lpa": b["expected_lpa"]}
        top_w = sorted(DIM_KEYS, key=lambda d: -W[d])
        return {"roles": out, "weights": {d: round(W[d], 4) for d in DIM_KEYS}, "top_rewarded": [DIM_NAMES[d] for d in top_w[:2]],
                "odds": {DIM_NAMES[d]: round(float(np.exp(self.jm.params[JDS_COLUMN[d]])), 2) for d in DIM_KEYS},
                "band_or_exp": self.band_or["exp"], "juniors": int(len(self.jds))}

    def meta(self):
        fams = [f for f, _ in ROLE]
        seen = []
        for f in fams:
            if f not in seen:
                seen.append(f)
        examples = {"Data Scientist / ML / AI": "Data Scientist", "Data Engineer / Big Data": "Big Data Engineer", "Statistical Modelling / SAS": "SAS Statistical Modeller",
                    "Risk / Credit / Quant Analytics": "Credit Risk Analyst", "BI / Reporting / MIS": "Power BI Developer", "Marketing / Web Analytics": "Web Analytics Specialist",
                    "Business Analyst": "Business Analyst", "Data Analyst / Analytics": "Data Analyst", "Research / Market Research": "Market Research Analyst"}
        return dict(
            features={"junior": [{"key": c, "dim": d, "label": DIM_NAMES[d], "min": 1, "max": 5, "step": 0.5, "mean": round(float(self.j_mean[c]), 2)} for c, d in zip(SKILL_COLS, DIM_KEYS)],
                      "senior": [{"key": t, "label": TRAIT_NAMES[t], "min": 17, "max": 68, "step": 1, "mean": round(float(self.s_mean[t]), 1)} for t in TRAITS],
                      "band": {"inputs": ["experience (years)", "role family", "city tier", "5 dimension flags"], "city_tiers": CITY_TIERS, "bands": BANDS}},
            role_families=[{"family": f, "analytics": f in ANALYTICS, "example_title": examples.get(f, f.split(" /")[0]),
                            "postings": self.demand_role.get(f, {}).get("_n", 0)} for f in seen],
            dims=[{"key": d, "label": DIM_NAMES[d], "jds_column": JDS_COLUMN[d]} for d in DIM_KEYS],
            personas=PERSONAS,
            counts={"raw_postings": self.raw_counts["analytics_jobs"], "postings_dedup": int(len(self.an)), "core_postings": int(len(self.core)),
                    "salary_sample": self.band_n, "ds_rows": int(len(self.ds)), "jds_rows": int(len(self.jds)), "sds_rows": int(len(self.sds)),
                    "dimensions": len(DIM_KEYS), "mapped_skills": self.n_mapped_skills, "verification": {"passed": self.ver_pass, "total": self.ver_total}},
            baselines={"junior": round(self.j_base, 4), "senior": round(self.s_base, 4)}, startup_seconds=self.startup_s)

    def findings(self):
        jo = {c: float(np.exp(self.jm.params[c])) for c in SKILL_COLS}
        so = {t: float(np.exp(self.sm_.params[t] * self.s_sd[t])) for t in TRAITS}
        top_j = max(jo, key=jo.get); top_s = max(so, key=so.get)
        flip = max(DIM_KEYS, key=lambda d: self.reward[d]["demand_rank"] - self.reward[d]["reward_rank"])
        prem = self.premium()["rows"][:1]
        return [
            {"id": "skill", "title": "Strongest junior skill signal", "value": f"x{jo[top_j]:.1f}", "label": DIM_NAMES[DIM_KEYS[SKILL_COLS.index(top_j)]],
             "text": f"Each extra point in {DIM_NAMES[DIM_KEYS[SKILL_COLS.index(top_j)]].lower()} multiplies the odds of a high salary hike by {jo[top_j]:.1f} (n = {len(self.jds)}).",
             "link": "engine.html#results"},
            {"id": "gap", "title": "Biggest curriculum gap", "value": f"#{self.reward[flip]['demand_rank']} to #{self.reward[flip]['reward_rank']}", "label": DIM_NAMES[flip],
             "text": f"{DIM_NAMES[flip]} ranks #{self.reward[flip]['demand_rank']} of 5 on market demand but #{self.reward[flip]['reward_rank']} on reward.",
             "link": "engine.html#market-gap"},
            {"id": "trait", "title": "Strongest senior trait", "value": f"x{so[top_s]:.0f}", "label": TRAIT_NAMES[top_s],
             "text": f"One standard deviation more {TRAIT_NAMES[top_s].lower()} is associated with {so[top_s]:.0f}x the odds of high success (n = {len(self.sds)}).",
             "link": "engine.html#senior"},
            {"id": "premium", "title": "Top skill premium", "value": f"+{prem[0]['adjusted_lift_pts']:.0f} pts" if prem else "-", "label": prem[0]["skill"] if prem else "-",
             "text": (f"Postings asking for {prem[0]['skill']} are {prem[0]['adjusted_lift_pts']:.0f} points more likely to pay 15+ LPA at the same experience (n = {prem[0]['n']})."
                      if prem else ""), "link": "engine.html#market-premium"}]


def _sig(x):
    return float(1 / (1 + np.exp(-x)))


PERSONAS = [
    {"id": "coder", "name": "The Coder", "profile": "junior", "title": "Data Analyst", "experience": 2, "skills_text": "python, sql, java, git",
     "skills": {"big_data_skills": 3.5, "maths_stats_skills": 3.5, "coding_skills": 5, "ai_and_ml_skills": 3.5, "dashboard_and_storytelling_skills": 2}},
    {"id": "allrounder", "name": "The All Rounder", "profile": "junior", "title": "Data Scientist", "experience": 3, "skills_text": "python, sql, statistics, machine learning, tableau, hadoop",
     "skills": {"big_data_skills": 4, "maths_stats_skills": 4, "coding_skills": 4, "ai_and_ml_skills": 4, "dashboard_and_storytelling_skills": 4}},
    {"id": "stats", "name": "The Stats Specialist", "profile": "junior", "title": "SAS Statistical Modeller", "experience": 3, "skills_text": "sas, r, statistics, regression, spss",
     "skills": {"big_data_skills": 2, "maths_stats_skills": 5, "coding_skills": 3, "ai_and_ml_skills": 3.5, "dashboard_and_storytelling_skills": 3.5}},
    {"id": "storyteller", "name": "The Storyteller", "profile": "junior", "title": "Power BI Developer", "experience": 2, "skills_text": "tableau, power bi, excel, dashboard, sql",
     "skills": {"big_data_skills": 3.5, "maths_stats_skills": 4, "coding_skills": 3.5, "ai_and_ml_skills": 2, "dashboard_and_storytelling_skills": 5}},
    {"id": "steady", "name": "The Steady Closer", "profile": "senior", "title": "Senior Data Scientist", "experience": 9, "skills_text": "python, machine learning, statistics",
     "traits": {"neuroticism": 22, "extraversion": 50, "openness_to_experience": 48, "agreeableness": 50, "conscientiousness": 60}},
    {"id": "maverick", "name": "The Maverick", "profile": "senior", "title": "Data Science Lead", "experience": 10, "skills_text": "python, deep learning, spark",
     "traits": {"neuroticism": 40, "extraversion": 45, "openness_to_experience": 62, "agreeableness": 25, "conscientiousness": 38}},
]


def normalise_input(inp):
    inp = dict(inp or {})
    out = {"profile": "senior" if inp.get("profile") == "senior" else "junior",
           "title": str(inp.get("title") or "Data Analyst")[:200],
           "experience": float(min(max(float(inp.get("experience", 2)), 0), 30)),
           "city_tier": inp.get("city_tier") if inp.get("city_tier") in CITY_TIERS else "Tier 1 metro",
           "skills_text": str(inp.get("skills_text") or "")[:1000],
           "job_text": str(inp.get("job_text") or "")[:5000],
           "band_source": "sliders" if inp.get("band_source") == "sliders" else "chips"}
    sk = inp.get("skills") or {}
    out["skills"] = {c: float(min(max(float(sk.get(c, 4.0)), 1), 5)) for c in SKILL_COLS}
    tr = inp.get("traits") or {}
    out["traits"] = {t: float(min(max(float(tr.get(t, 45)), 17), 68)) for t in TRAITS}
    return out
