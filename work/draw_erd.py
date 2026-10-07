"""Draw the ER diagram (core + metadata layers) as a PNG, parsed directly from database/sql/01_create_schema.sql,
so the picture always matches the real DDL."""
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent
ddl = (HERE / "database" / "sql" / "01_create_schema.sql").read_text(encoding="utf-8")

tables = {}
for m in re.finditer(r"CREATE TABLE `(\w+)` \((.*?)\n\) ENGINE", ddl, re.S):
    name, body = m.group(1), m.group(2)
    if name.startswith("stg_"):
        continue
    cols, pk, fk = [], [], {}
    for line in body.splitlines():
        line = line.strip().rstrip(",")
        c = re.match(r"`(\w+)` (\w+)", line)
        if c and not line.startswith(("PRIMARY", "KEY", "UNIQUE", "CONSTRAINT")):
            cols.append((c.group(1), c.group(2).lower()))
        p = re.match(r"PRIMARY KEY \((.*)\)", line)
        if p:
            pk = re.findall(r"`(\w+)`", p.group(1))
        f = re.match(r"CONSTRAINT `\w+` FOREIGN KEY \(`(\w+)`\) REFERENCES `(\w+)`", line)
        if f:
            fk[f.group(1)] = f.group(2)
    tables[name] = dict(cols=cols, pk=pk, fk=fk)

# layout: (x, y) of the top-left corner, in grid units
POS = {
    "dim_company": (0, 36), "dim_job_title": (0, 22), "fact_company_job_title": (12.5, 36),
    "dim_role_family": (25.5, 40), "dim_seniority": (25.5, 32), "dim_salary_band": (25.5, 24), "dim_city": (25.5, 14),
    "fact_job_posting": (38, 40), "bridge_posting_city": (38, 14),
    "bridge_posting_skill": (51.5, 40), "dim_skill": (51.5, 32), "map_skill_dimension": (51.5, 24), "dim_skill_dimension": (64, 24),
    "jds_employee": (76.5, 40), "fact_jds_skill_score": (76.5, 32),
    "sds_employee": (89, 40), "fact_sds_trait_score": (89, 32), "dim_personality_trait": (89, 24),
    "meta_data_quality_log": (0, 12),
}
W, RH = 11.5, 1.05
COL = {"dim": "#DBEAFE", "fact": "#FEF3C7", "bridge": "#DCFCE7", "map": "#DCFCE7", "jds": "#FCE7F3", "sds": "#FCE7F3", "meta": "#E5E7EB"}
fig, ax = plt.subplots(figsize=(30, 15))
ax.set_xlim(-1, 101)
ax.set_ylim(3, 45)
ax.axis("off")
anchor = {}
for name, t in tables.items():
    x, y = POS[name]
    h = RH * (len(t["cols"]) + 1)
    color = COL[name.split("_")[0]]
    ax.add_patch(FancyBboxPatch((x, y - h), W, h, boxstyle="round,pad=0.1", fc="white", ec="#334155", lw=1.4))
    ax.add_patch(FancyBboxPatch((x, y - RH), W, RH, boxstyle="round,pad=0.1", fc=color, ec="#334155", lw=1.4))
    ax.text(x + W / 2, y - RH / 2, name, ha="center", va="center", fontsize=10.5, fontweight="bold", color="#0F172A")
    for i, (c, typ) in enumerate(t["cols"]):
        yy = y - RH * (i + 1.5)
        key = ("PK " if c in t["pk"] else "") + ("FK" if c in t["fk"] else "")
        ax.text(x + 0.3, yy, key.strip(), fontsize=7.5, va="center", color="#B91C1C" if "PK" in key else "#1D4ED8", fontweight="bold")
        ax.text(x + 2.4, yy, c, fontsize=8, va="center", color="#0F172A")
        ax.text(x + W - 0.3, yy, typ, fontsize=7, va="center", ha="right", color="#64748B")
        anchor[(name, c)] = (x, x + W, yy)
    anchor[(name, "__box__")] = (x, x + W, y - RH / 2)

for name, t in tables.items():
    for col, ref in t["fk"].items():
        cx0, cx1, cy = anchor[(name, col)]
        rpk = tables[ref]["pk"][0]
        rx0, rx1, ry = anchor[(ref, rpk)]
        if rx1 <= cx0:
            sx, ex = cx0, rx1
        elif rx0 >= cx1:
            sx, ex = cx1, rx0
        else:
            sx, ex = cx0, rx0
        ax.annotate("", xy=(ex, ry), xytext=(sx, cy),
                    arrowprops=dict(arrowstyle="-|>", color="#475569", lw=1.1, connectionstyle="arc3,rad=0.08", shrinkA=2, shrinkB=2))
        ax.plot(sx, cy, marker="o", ms=4, color="#475569")

ax.text(0, 44.2, "Vriddhi database - entity-relationship diagram (core 3NF + metadata)", fontsize=18, fontweight="bold", color="#0F172A")
ax.text(0, 43.2, "Arrow points from a foreign key (child, many) to the primary key it references (parent, one).  "
        "Blue = lookup (dim)   Yellow = fact   Green = bridge / mapping (many-to-many)   Pink = people data (JDS / SDS)   Grey = metadata.  "
        "Staging tables (raw copies of the 4 files) are not shown.", fontsize=10, color="#475569")
fig.savefig(HERE / "database" / "ERD.png", dpi=130, bbox_inches="tight", facecolor="white")
print("saved database/ERD.png with", len(tables), "tables")
