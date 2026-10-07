"""Proves the engine computes from real data (no canned values). Run: python work/api/test_engine.py
Also writes api/mock/*.json snapshots (real outputs) for the server's mock mode."""
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from engine import BANDS, SKILL_COLS, TRAITS, Engine  # noqa: E402
from role_rules import ROLE  # noqa: E402

t0 = time.time(); E = Engine(); print(f"engine startup {E.startup_s}s")
fails = []


def check(name, cond, info=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{info}]" if info else ""))
    if not cond:
        fails.append(name)


an = pd.read_csv(HERE.parent / "clean" / "analytics_jobs_clean.csv"); jds = pd.read_csv(HERE.parent / "clean" / "jds_clean.csv")
sds = pd.read_csv(HERE.parent / "clean" / "sds_clean.csv")
m = E.meta()
check("meta counts equal the cleaned files", m["counts"]["postings_dedup"] == len(an) and m["counts"]["jds_rows"] == len(jds) and m["counts"]["sds_rows"] == len(sds),
      f"{m['counts']['postings_dedup']} / {m['counts']['jds_rows']} / {m['counts']['sds_rows']}")
check("core postings = in_core_analytics flag", m["counts"]["core_postings"] == int(an.in_core_analytics.sum()))
check("baselines = observed positive rates", abs(m["baselines"]["junior"] - jds.salary_hike_high.mean()) < 1e-4 and abs(m["baselines"]["senior"] - sds.success_high.mean()) < 1e-4)

# --- junior model equals an independent refit
ind = sm.Logit(jds.salary_hike_high, sm.add_constant(jds[SKILL_COLS])).fit(disp=0)
prof = {"big_data_skills": 3, "maths_stats_skills": 4.5, "coding_skills": 5, "ai_and_ml_skills": 3.5, "dashboard_and_storytelling_skills": 2.5}
r = E.analyze({"profile": "junior", "title": "Data Scientist", "experience": 3, "skills_text": "python, oracle sql, tableau", "skills": prof})
p_ind = float(ind.predict(np.r_[1, [prof[c] for c in SKILL_COLS]].reshape(1, -1))[0])
check("junior probability = independent statsmodels refit", abs(E.junior_predict(prof)["probability"] - p_ind) < 1e-9 and abs(r["result"]["hike_probability"] - p_ind) < 1e-4, f"{r['result']['hike_probability']:.6f} vs {p_ind:.6f}")
check("waterfall ends exactly at the prediction", abs(r["result"]["waterfall"][-1]["p_to"] - r["result"]["hike_probability"]) < 1e-3)
check("trace has 8 steps in order", [e["node"] for e in r["trace"]] == ["load", "role_match", "skills", "demand", "junior_model", "senior_model", "band", "verdict"])
check("senior node skipped for a junior run", r["trace"][5].get("status") == "skipped")

# --- different inputs -> different outputs (not hard-coded)
probs = set()
for v in [1.5, 2.5, 3.5, 4.5]:
    q = dict(prof, maths_stats_skills=v)
    probs.add(round(E.analyze({"profile": "junior", "title": "Data Analyst", "skills": q})["result"]["hike_probability"], 6))
check("changing maths changes the probability (4 distinct values)", len(probs) == 4, str(sorted(probs)))
pm = [E.junior_predict(dict(prof, maths_stats_skills=v))["probability"] for v in [2, 3, 4, 5]]
check("probability rises with maths (positive coefficient)", all(a < b for a, b in zip(pm, pm[1:])))

# --- role rules: engine = first regex match, done independently here
for title in ["Data Scientist", "Financial Analyst", "Power BI Developer", "HR Data Analyst", "Credit Risk Analyst", "Java Developer"]:
    exp = next(((i + 1, f) for i, (f, p) in enumerate(ROLE) if re.search(p, title.lower())), (None, "Other"))
    got = E.match_role(title)
    check(f"role rule for '{title}'", (got["index"], got["family"]) == exp, f"rule {got['index']}: {got['family']}")

# --- taxonomy
ex = E.extract_skills("oracle sql, tableau, medical coding, basket weaving")
check("'oracle sql' -> coding", "oracle sql" in ex["buckets"]["coding"])
check("'tableau' -> dashboards", "tableau" in ex["buckets"]["dashboard_story"])
check("'medical coding' not coding; unknown chip unmatched", "medical coding" not in ex["buckets"]["coding"] and "basket weaving" in ex["unmatched"])
ext = E.extract_skills("", "We need strong SQL, Python and Power BI; regression modelling a plus.")
check("free-text extraction finds sql, python, power bi", {"sql", "python", "power bi"} <= {s["skill"] for s in ext["skills"]}, str([s["skill"] for s in ext["skills"]]))

# --- demand profile equals pandas groupby
core = an[an.in_core_analytics == 1]
g = core[core.role_family == "Data Scientist / ML / AI"].dim_coding.mean()
check("demand share = groupby on the data", abs(r["result"]["demand_profile"]["coding"] - g) < 1e-4, f"{g:.4f}")

# --- band model
b = r["result"]["band_probs"]
check("band probabilities sum to 1", abs(sum(b.values()) - 1) < 1e-6)
e_lo = E.band_predict(1, "Data Analyst / Analytics", "Tier 1 metro", {})["expected_lpa"]; e_hi = E.band_predict(12, "Data Analyst / Analytics", "Tier 1 metro", {})["expected_lpa"]
check("expected pay rises with experience", e_hi > e_lo, f"{e_lo} -> {e_hi} LPA")
t2 = E.band_predict(5, "Data Analyst / Analytics", "Tier 2/3", {})["expected_lpa"]; t1 = E.band_predict(5, "Data Analyst / Analytics", "Tier 1 metro", {})["expected_lpa"]
check("Tier 2/3 city lowers expected pay (as in M03)", t2 < t1, f"{t1} vs {t2}")
rs = E.analyze({"profile": "junior", "title": "Data Analyst", "skills_text": "python", "band_source": "sliders",
                "skills": {c: 5 for c in SKILL_COLS}})["result"]["band"]["inputs"]["dims"]
rc = E.analyze({"profile": "junior", "title": "Data Analyst", "skills_text": "python", "band_source": "chips",
                "skills": {c: 5 for c in SKILL_COLS}})["result"]["band"]["inputs"]["dims"]
check("band source toggle changes the band inputs", rs != rc, f"sliders {rs} vs chips {rc}")
nb = E.analyze({"profile": "junior", "title": "Java Developer", "skills": prof})
check("non-analytics role skips the band model", nb["trace"][6].get("status") == "skipped")

# --- counterfactual really flips the outcome
low = {c: 3.0 for c in SKILL_COLS}
cf = E.counterfactual(low, "junior")
new = dict(low); [new.__setitem__(ch["feature"], ch["to"]) for ch in cf.get("changes", [])]
check("counterfactual change reaches p >= 0.5", cf.get("found") and E.junior_predict(new)["probability"] >= 0.5, cf.get("message", ""))
# independent brute force with the independently refit model: no grid change with a smaller total reaches 0.5
from itertools import product as _prod
G = np.array(list(_prod(*[np.arange(0, 2.01, .5)] * 5)))
G = G[G.sum(1) < cf["total_change"] - 1e-9]
pp = ind.predict(np.c_[np.ones(len(G)), 3.0 + G])
check("counterfactual is minimal (brute force finds nothing smaller)", (pp < 0.5).all(), f"total change {cf['total_change']}, {len(G)} smaller combos checked")

# --- senior
sr = E.analyze({"profile": "senior", "title": "Senior Data Scientist", "traits": {"neuroticism": 30, "extraversion": 50, "openness_to_experience": 55,
                                                                                 "agreeableness": 50, "conscientiousness": 58}})
ind_s = sm.Logit(sds.success_high, sm.add_constant(sds[TRAITS])).fit(disp=0)
ps = float(ind_s.predict(np.r_[1, [30, 50, 55, 50, 58]].reshape(1, -1))[0])
check("senior probability = independent refit", abs(sr["result"]["success_probability"] - ps) < 1e-4, f"{ps:.4f}")
check("junior node skipped for a senior run", sr["trace"][4].get("status") == "skipped")
cfs = E.counterfactual({"neuroticism": 30, "extraversion": 40, "openness_to_experience": 35, "agreeableness": 40, "conscientiousness": 35}, "senior")
check("senior counterfactual never raises neuroticism", all(ch["feature"] != "neuroticism" for ch in cfs.get("changes", [])), cfs.get("message", ""))

# --- determinism
r2 = E.analyze({"profile": "junior", "title": "Data Scientist", "experience": 3, "skills_text": "python, oracle sql, tableau", "skills": prof})
check("same input -> same run id and result", r2["run_id"] == r["run_id"] and r2["result"]["hike_probability"] == r["result"]["hike_probability"])

# --- market endpoints against the data
sk = E.sankey(); sal = an[an.in_salary_model == 1]
tot = sum(l["value"] for l in sk["links"] if l["source"].startswith("role:"))
check("sankey role->dim total = sum of dim flags in salary sample", tot == int(sal[[f"dim_{d}" for d in ["big_data", "maths_stats", "coding", "ai_ml", "dashboard_story"]]].values.sum()), str(tot))
gp = E.gap(); check("gap matrix has roles x 5 cells (both variants)", len(gp["hype_gap"]) == len(gp["roles"]) * 5 == len(gp["supply_gap"]))
pr = E.premium(); check("premium rows all have n >= 50", all(x["n"] >= 50 for x in pr["rows"]) and len(pr["rows"]) > 10, f"{len(pr['rows'])} skills")
bu = E.bundles(); check("bundles computed from postings", len(bu["rows"]) > 5 and all(x["n_both"] >= 20 for x in bu["rows"]))
gr = E.graph(); check("graph has skill, role and band nodes", {n["kind"] for n in gr["nodes"]} == {"skill", "role", "band"} and len(gr["edges"]) > 20)
em = E.embedding(); check("embedding points have neighbours", len(em["points"]) > 50 and all(len(p["neighbours"]) == 5 for p in em["points"]))
xr = E.xray("Senior Data Scientist\nNeed Python, SQL, machine learning, statistics and Tableau dashboards.")
check("x-ray finds the role and skills", xr["role"]["family"] == "Data Scientist / ML / AI" and xr["skills"]["dims"]["coding"] == 1, xr["role"]["family"])
c = E.compare({"profile": "junior", "skills": {c: 3 for c in SKILL_COLS}}, {"profile": "junior", "skills": {c: 4.5 for c in SKILL_COLS}})
check("compare: stronger profile has higher probability", c["better"] == "B" and c["delta"] > 0, f"delta {c['delta']}")
cf_ = E.conf; check("confidence numbers present for both models", cf_["junior"]["n"] == 139 and cf_["senior"]["n"] == 161)

# --- JD audit (company view)
exs = E.jd_examples()
check("JD examples are real postings from the data", all(int(x["s_no"]) in set(an.s_no) and an.set_index("s_no").loc[x["s_no"], "job_desig"] in x["text"] for x in exs))
ja = E.jd_audit(exs[0]["text"])
W = E.reward_weights()
check("reward weights sum to 1 and come from the junior model", abs(sum(W.values()) - 1) < 1e-9 and max(W, key=W.get) == "maths_stats", str({k: round(v, 3) for k, v in W.items()}))
check("coverage = sum of weights of areas the JD asks for", abs(ja["coverage"] - sum(W[r["dim"]] for r in ja["rows"] if r["in_jd"])) < 1e-3, f"{ja['coverage']}")
check("updated JD never lowers the predicted chance", ja["effect"]["after"] >= ja["effect"]["before"], f"{ja['effect']['before']} -> {ja['effect']['after']}")
hi = jds[jds.salary_hike_high == 1][SKILL_COLS].mean(); lo = jds[jds.salary_hike_high == 0][SKILL_COLS].mean()
flags = {r["dim"]: r["in_jd"] for r in ja["rows"]}
from engine import JDS_COLUMN as _JC
prof0 = {_JC[d]: (hi[_JC[d]] if flags[d] else lo[_JC[d]]) for d in flags}
pb = float(ind.predict(np.r_[1, [prof0[c] for c in SKILL_COLS]].reshape(1, -1))[0])
check("'before' chance = independent refit on the implied profile", abs(pb - ja["effect"]["before"]) < 1e-4, f"{pb:.4f}")
full = E.jd_audit("Data Scientist\nPython, SQL, statistics, regression, machine learning, Tableau dashboards, Spark")
check("a JD covering every area has nothing rewarded missing", full["missing_rewarded"] == [] and full["coverage"] > 0.99, f"{full['coverage']}")
thin = E.jd_audit("Data Analyst\nStrong Python and SQL coding")
check("a coding-only JD is told to add maths and storytelling", {"Maths & statistics", "Dashboards & storytelling"} <= set(thin["missing_rewarded"]), str(thin["missing_rewarded"]))
check("senior titles get the traits card, junior titles do not", bool(E.jd_audit("Senior Data Scientist\nPython")["senior"]) and not thin["senior"])
sc = E.showcase(); check("showcase shares equal the demand profile", abs(sc["roles"]["Data Analyst / Analytics"]["shares"]["coding"] - E.demand_role["Data Analyst / Analytics"]["coding"]) < 1e-9)

# speed
t = time.time()
for _ in range(20):
    E.whatif({"profile": "junior", "title": "Data Analyst", "skills": prof})
check("what-if is fast enough for live sliders", (time.time() - t) / 20 < 0.3, f"{(time.time() - t) / 20 * 1000:.0f} ms per call")

# mock snapshots (real outputs) for VRIDDHI_MOCK=1
MD = HERE / "mock"; MD.mkdir(exist_ok=True)
snap = {"api_meta": m, "api_findings": E.findings(), "api_market_premium": pr, "api_market_sankey": sk, "api_market_gap": gp, "api_market_bundles": bu,
        "api_graph": gr, "api_embedding": em, "api_confidence": cf_, "api_analyze": r, "api_whatif": r["result"], "api_xray": xr, "api_compare": c,
        "api_counterfactual": cf}
for k, v in snap.items():
    (MD / f"{k}.json").write_text(json.dumps(v, default=lambda o: o.item() if hasattr(o, "item") else str(o)), encoding="utf-8")
print(f"\n{'ALL TESTS PASSED' if not fails else str(len(fails)) + ' FAILED: ' + ', '.join(fails)}  ({time.time() - t0:.0f}s)")
sys.exit(1 if fails else 0)
