// Vriddhi: live homepage + the Vriddhi AI "JD audit" view (original full-screen AI design).
// Every number shown comes from the local engine (work/api/server.py). Nothing here is hard-coded data.
import { countUp, esc } from "./engine/charts.js";
import { DIM } from "./engine/dims.js";

const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const pct = (x, d = 0) => `${(100 * x).toFixed(d)}%`;
const BAND = { "0to3": "0-3", "3to6": "3-6", "6to10": "6-10", "10to15": "10-15", "15to25": "15-25", "25to50": "25-50" };
async function get(path) { const r = await fetch(path); const j = await r.json(); if (!r.ok || j.error) throw new Error(j.error || r.status); return j; }
async function post(path, body) { const r = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }); const j = await r.json(); if (!r.ok || j.error) throw new Error(j.error || r.status); return j; }

// =============================================================== open / close the AI view (same choreography as the template)
const platform = $("#platform-view"), aiView = $("#vriddhi-ai-view"), hero = $("#ai-landing-hero"), scroll = $("#ai-conversation-scroll"),
  messages = $("#ai-conversation-messages"), form = $("#ai-persistent-form"), input = $("#ai-persistent-input"), workspace = $("#ai-workspace");
let open = false, savedY = 0, tmr = null;
function openAI() {
  if (open) return; open = true; clearTimeout(tmr); savedY = window.scrollY;
  document.body.style.overflow = "hidden"; aiView.classList.remove("hidden", "ai-closing");
  platform.style.visibility = "visible"; platform.classList.add("platform-dimmed");
  requestAnimationFrame(() => requestAnimationFrame(() => aiView.classList.add("ai-active")));
  tmr = setTimeout(() => open && (platform.style.visibility = "hidden"), 480);
  if (location.hash !== "#ai") history.pushState(null, "", "#ai");
  setTimeout(() => input.focus(), 350);
}
function closeAI() {
  if (!open) return; open = false; clearTimeout(tmr);
  platform.style.visibility = "visible"; window.scrollTo(0, savedY); requestAnimationFrame(() => platform.classList.remove("platform-dimmed"));
  aiView.classList.remove("ai-active"); aiView.classList.add("ai-closing"); document.body.style.overflow = "";
  tmr = setTimeout(() => aiView.classList.remove("ai-closing"), 480);
  if (location.hash === "#ai") history.pushState(null, "", location.pathname);
}
function toResults() {
  [workspace, aiView].forEach(e => e?.classList.add("conversation-mode"));
  Object.assign(hero.style, { maxHeight: "0px", opacity: "0", transform: "translateY(-30px)", pointerEvents: "none", paddingTop: "0px", paddingBottom: "0px" });
  scroll.classList.remove("h-0", "max-h-0", "opacity-0", "pointer-events-none"); scroll.classList.add("flex-1", "opacity-100"); scroll.style.maxHeight = "100%";
  input.placeholder = "Paste another job description to audit...";
}
function toLanding() {
  [workspace, aiView].forEach(e => e?.classList.remove("conversation-mode"));
  Object.assign(hero.style, { maxHeight: "", opacity: "1", transform: "none", pointerEvents: "auto", paddingTop: "", paddingBottom: "" });
  scroll.classList.add("h-0", "max-h-0", "opacity-0", "pointer-events-none"); scroll.classList.remove("flex-1", "opacity-100"); scroll.style.maxHeight = "0px";
  messages.innerHTML = ""; input.value = ""; input.placeholder = "Paste a job description here (title on the first line)..."; input.focus();
}
$$(".btn-open-counselor").forEach(b => b.addEventListener("click", e => { e.preventDefault(); openAI(); }));
$("#btn-ai-back")?.addEventListener("click", closeAI); $("#btn-ai-back-logo")?.addEventListener("click", closeAI);
$("#btn-ai-new-chat")?.addEventListener("click", toLanding);
window.addEventListener("popstate", () => (location.hash === "#ai" ? openAI() : closeAI()));
document.addEventListener("keydown", e => e.key === "Escape" && open && closeAI());

// =============================================================== JD audit
input.addEventListener("keydown", e => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) form.requestSubmit(); });
form.addEventListener("submit", e => { e.preventDefault(); const t = input.value.trim(); if (t) audit(t); });

async function audit(text) {
  toResults();
  messages.innerHTML = `<div class="jd-block"><p class="jd-step">Reading your job description</p><div class="jd-card"><div class="skel" style="min-height:120px"></div></div></div>`;
  try {
    const r = await post("/api/jd-audit", { text });
    render(text, r);
    input.value = "";
  } catch (e) {
    messages.innerHTML = `<div class="jd-err">Could not audit this job description: ${esc(e.message)}. Is the engine running? (python work/api/server.py)</div>`;
  }
  scroll.querySelector("#ai-conversation-messages").scrollTop = 0;
}

function highlight(text, skills) {
  // highlight every found skill word in its dimension colour (longest first so 'sql server' wins over 'sql')
  const list = [...skills].filter(s => s.dims.length).sort((a, b) => b.skill.length - a.skill.length);
  let html = esc(text);
  list.forEach(s => {
    const re = new RegExp(`(?<![\\w>])(${s.skill.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})(?![\\w<])`, "gi");
    html = html.replace(re, m => `<mark style="background:${DIM[s.dims[0]].color}">${m}</mark>`);
  });
  return html;
}

function render(text, r) {
  const rows = r.rows, cov = r.coverage, e = r.effect;
  const tiles = rows.map(x => `<div class="jd-tile ${x.in_jd ? "on" : ""}" style="${x.in_jd ? `background:${DIM[x.dim].color}` : ""}">${esc(x.label)}<small>${x.in_jd ? esc(x.words.slice(0, 3).join(", ")) : "not mentioned"}</small></div>`).join("");
  const seg = rows.map(x => `<i title="${esc(x.label)} ${pct(x.weight)}" style="width:${100 * x.weight}%;background:${DIM[x.dim].color};opacity:${x.in_jd ? 1 : 0.15}"></i>`).join("");
  const maxW = Math.max(...rows.map(x => x.weight));
  const rowHtml = rows.map(x => `<div class="jd-row">
      <div class="nm"><i class="dot9" style="background:${DIM[x.dim].color}"></i><span>${esc(x.label)}<small>${pct(x.market_share)} of similar postings ask for it</small></span></div>
      <div class="bar"><i style="width:${(100 * x.weight) / maxW}%;background:${DIM[x.dim].color}"></i><span>${pct(x.weight)}</span></div>
      <span class="jd-pill ${x.in_jd ? "ok" : x.add ? "add" : "na"}">${x.in_jd ? "In your JD" : x.add ? "Missing: add it" : "Not needed"}</span></div>`).join("");
  const adds = r.additions.map(a => `<ins><b>Add: ${esc(a.label)}</b>${esc(a.text)}</ins>`).join("");
  const notes = r.notes.map(n => `<div class="jd-note">${esc(n.text)}</div>`).join("");
  const newText = esc(text) + (adds ? `\n${adds}` : "");
  messages.innerHTML = `
    <div class="jd-block">
      <p class="jd-step">Step 1</p><h2 class="jd-h">What your job description asks for</h2>
      <span class="jd-role">Role matched: <b>${esc(r.role.family)}</b> <span style="color:#a8a29e">(rule ${r.role.index ?? "-"})</span></span>
      <div class="jd-card"><div class="jd-text">${highlight(text, r.skills)}</div></div>
      <div class="jd-tiles">${tiles}</div>
    </div>

    <div class="jd-block">
      <p class="jd-step">Step 2</p><h2 class="jd-h">What actually gets juniors a high raise</h2>
      <p class="jd-sub">Bar length = how strongly each skill area separated juniors who got a high raise from those who did not (${r.evidence.juniors} junior data scientists, one company).</p>
      <div class="jd-card">
        <div class="jd-cover"><span class="big" id="cov-num">0%</span><span class="txt">of what drives junior raises is covered by this job description.${r.missing_rewarded.length ? ` Missing: <b>${esc(r.missing_rewarded.join(", "))}</b>.` : " Nothing important is missing."}</span></div>
        <div class="jd-segbar">${seg}</div>
        ${rowHtml}
      </div>
    </div>

    <div class="jd-block">
      <p class="jd-step">Step 3</p><h2 class="jd-h">Your updated job description</h2>
      <p class="jd-sub">${r.additions.length ? "Your original text, with the lines to add highlighted in green." : "Your job description already covers the rewarded areas."}</p>
      <div class="jd-card"><div class="jd-new" id="jd-new">${newText}</div>${notes}
        <div class="jd-actions"><button class="jd-btn dark" id="jd-copy">Copy updated JD</button><button class="jd-btn" id="jd-again">Audit another JD</button></div></div>
    </div>

    <div class="jd-block">
      <p class="jd-step">The effect</p><h2 class="jd-h">Who you would hire</h2>
      <div class="jd-effect">
        <div class="side"><div class="num" id="eff-a">0%</div><div class="lbl">chance of a high raise for a junior who matches your <b>current</b> JD</div></div>
        <div class="arrow">&#8594;</div>
        <div class="side after"><div class="num" id="eff-b">0%</div><div class="lbl">for a junior who matches the <b>updated</b> JD</div></div>
      </div>
      <p class="jd-cap">From the trained junior model (AUC 0.90 on unseen people). ${esc(e.method)} Baseline: ${pct(e.baseline)} of juniors got a high raise.</p>
    </div>

    ${r.senior ? `<div class="jd-block"><p class="jd-step">Senior role</p><h2 class="jd-h">Also hire for curiosity and discipline</h2>
      <div class="ai-card-recommendation" style="padding:1rem 1.25rem;border-radius:16px"><span class="ai-card-rec-tag">Add to the JD</span>
      <div class="ai-card-rec-text">${r.senior.text.map(esc).join("<br>")}</div></div><p class="jd-cap">${esc(r.senior.evidence)}</p></div>` : ""}

    ${r.pay ? `<p class="jd-foot">Typical pay band for postings like this (about ${r.pay.exp_mid} years, Tier 1 city): <b>${BAND[r.pay.most_likely]} LPA</b>.</p>` : ""}
    <p class="jd-foot">Based on ${r.evidence.postings_role.toLocaleString("en-IN")} ${esc(r.evidence.role)} postings and ${r.evidence.juniors} junior data scientists from one company. Association, not causation. A guide for writing job descriptions, not a hiring decision.</p>`;
  countUp($("#cov-num"), 100 * cov, { fmt: v => `${Math.round(v)}%` });
  countUp($("#eff-a"), 100 * e.before, { fmt: v => `${Math.round(v)}%` });
  countUp($("#eff-b"), 100 * e.after, { fmt: v => `${Math.round(v)}%`, dur: 1400 });
  $("#jd-again").onclick = toLanding;
  $("#jd-copy").onclick = async () => {
    const out = `${text}\n${r.additions.map(a => `- ${a.text}`).join("\n")}`;
    try { await navigator.clipboard.writeText(out); $("#jd-copy").textContent = "Copied"; } catch { $("#jd-copy").textContent = "Select and copy the text above"; }
  };
}

async function loadExamples() {
  try {
    const ex = await get("/api/jd-examples");
    $("#jd-examples").innerHTML = `<span class="text-xs text-stone-400">Try a real posting from our data:</span>` + ex.map((x, i) =>
      `<button class="ai-prompt-chip" data-i="${i}" title="Posting #${x.s_no} from Analytics Jobs">${esc(x.label)}</button>`).join("");
    $$("#jd-examples [data-i]").forEach(b => (b.onclick = () => { input.value = ex[+b.dataset.i].text; audit(input.value); }));
    const q = new URLSearchParams(location.search).get("ex");  // ?ex=0#ai auto-runs a real example (stage shortcut)
    if (q !== null && ex[+q]) { openAI(); input.value = ex[+q].text; audit(input.value); }
  } catch { $("#jd-examples").innerHTML = `<span class="text-xs text-rose-600">Engine not running: start python work/api/server.py</span>`; }
}

// =============================================================== live homepage
async function homepage() {
  let meta, sc, fi;
  try { [meta, sc, fi] = await Promise.all([get("/api/meta"), get("/api/showcase"), get("/api/findings")]); }
  catch { $("#offline")?.classList.add("on"); return; }
  const c = meta.counts;
  $("#ticker-text").textContent = `${c.postings_dedup.toLocaleString("en-IN")} postings, ${c.jds_rows} juniors, ${c.sds_rows} seniors. ${c.verification.passed} of ${c.verification.total} verification checks passed`;
  const io = new IntersectionObserver(es => es.forEach(en => {
    if (!en.isIntersecting) return; io.unobserve(en.target);
    if (en.target.id === "ver-count") countUp(en.target, c.verification.passed, { fmt: v => `${Math.round(v)} of ${c.verification.total}` });
    else countUp(en.target, c[en.target.dataset.count]);
  }), { threshold: .3 });
  $$("[data-count], #ver-count").forEach(el => io.observe(el));
  // pillar stats (all core postings)
  const core = await get("/api/market/gap").catch(() => null);
  const set = (k, v) => $$(`[data-stat="${k}"]`).forEach(el => (el.textContent = v));
  const gap = core ? core.hype_gap : [];
  const share = d => { const rows = gap.filter(x => x.dim === d); const tot = rows.reduce((a, x) => a + x.postings, 0); return rows.reduce((a, x) => a + x.demand * x.postings, 0) / tot; };
  if (gap.length) { set("coding", pct(share("coding"), 1)); set("maths", pct(share("maths_stats"), 1)); set("story", pct(share("dashboard_story"), 1)); }
  set("exp", `x${sc.band_or_exp.toFixed(2)}`); set("salary_n", meta.counts.salary_sample.toLocaleString("en-IN"));
  set("odds_maths", `x${sc.odds["Maths & statistics"]}`); set("odds_story", `x${sc.odds["Dashboards & storytelling"]}`); set("odds_coding", `x${sc.odds["Coding"]}`);
  $$("[data-n]").forEach(el => (el.textContent = (sc.roles[el.dataset.n]?.postings ?? "-").toLocaleString("en-IN")));
  // findings -> feature cards (original card style with the module symbols)
  const icons = ["model-01", "model-03", "model-07", "model-11"];
  $("#features .grid.grid-cols-1.md\\:grid-cols-2").innerHTML = fi.map((f, i) => `
    <a href="#" class="${f.id === "gap" || f.id === "skill" ? "btn-open-counselor " : ""}sarvam-card p-8 flex flex-col justify-between min-h-[220px] relative overflow-hidden group" style="text-decoration:none;color:inherit">
      <img src="public/assets/${icons[i % 4]}.svg" class="absolute top-6 right-6 w-16 h-16 object-contain opacity-80 group-hover:scale-110 transition-transform">
      <div><span class="text-xs font-mono uppercase text-stone-400 block mb-2">${esc(f.title)}</span>
        <h3 class="text-xl font-semibold text-[#1f1f1f] mb-1">${esc(f.label)}</h3>
        <p class="font-mono font-bold text-[26px] text-[#581c87] mb-2">${esc(f.value)}</p>
        <p class="text-sm text-[#666666] max-w-sm">${esc(f.text)}</p></div></a>`).join("");
  $$("#features .btn-open-counselor").forEach(b => b.addEventListener("click", e => { e.preventDefault(); openAI(); }));
  $("#trust-1").textContent = `${c.verification.passed} of ${c.verification.total} automated checks re-compute every cleaned number from the raw files.`;
  $("#trust-2").textContent = `${c.jds_rows} juniors and ${c.sds_rows} seniors from one company each; outcomes are proxies; association, not causation.`;
  initLab(sc);
}

// =============================================================== showcase lab: the three signals per role
function initLab(sc) {
  let tab = "asked", role = "Data Analyst / Analytics";
  const draw = () => {
    const r = sc.roles[role], s = r.shares, short = role.split(" /")[0];
    const title = { asked: `${short}: what is asked for`, paid: `${short}: what it pays`, rewarded: "Juniors: what is rewarded" }[tab];
    $("#showcase-center-title").textContent = title;
    const order = Object.entries(s).sort((a, b) => b[1] - a[1]);
    const box = $("#showcase-bubbles-container");
    if (tab === "asked") box.innerHTML = `
      <div class="bubble-blue"><strong>${pct(s.coding)}</strong> of ${r.postings.toLocaleString("en-IN")} ${esc(short)} postings ask for coding; most asked area: <strong>${esc(r.most_asked)}</strong>.</div>
      <div class="bubble-peach">Only <strong>${pct(s.maths_stats)}</strong> ask for maths and statistics, and <strong>${pct(s.dashboard_story)}</strong> for storytelling.</div>
      <div class="bubble-green">Ranking for this role: ${order.map(([k, v]) => `${esc(DIM[k].label)} ${pct(v)}`).join(", ")}.</div>`;
    else if (tab === "paid") box.innerHTML = `
      <div class="bubble-blue">Each extra year of experience multiplies the odds of a higher pay band by <strong>x${sc.band_or_exp.toFixed(2)}</strong>.</div>
      <div class="bubble-peach">Typical band for a ${esc(short)} posting at 3 years in a Tier 1 city: <strong>${BAND[r.band]} LPA</strong> (expected ${r.expected_lpa} LPA).</div>
      <div class="bubble-green">Adding every listed skill to the pay model does <strong>not</strong> improve its predictions. Skills barely move the offer.</div>`;
    else box.innerHTML = `
      <div class="bubble-blue">Per extra skill point, maths multiplies the odds of a high raise by <strong>x${sc.odds["Maths & statistics"]}</strong> and storytelling by <strong>x${sc.odds["Dashboards & storytelling"]}</strong>.</div>
      <div class="bubble-peach">Coding, the most asked skill, adds the least once the others are known (<strong>x${sc.odds["Coding"]}</strong>, not significant).</div>
      <div class="bubble-green">Based on ${sc.juniors} junior data scientists. The same evidence powers the JD audit.</div>`;
  };
  $$(".showcase-tab-btn").forEach(b => b.addEventListener("click", () => {
    if (b.dataset.tabId === "counselor") return openAI();
    tab = b.dataset.tabId;
    $$(".showcase-tab-btn").forEach(x => { const on = x === b; x.classList.toggle("border-[#e96c2f]", on); x.classList.toggle("text-[#a5460f]", on); x.classList.toggle("border-transparent", !on); x.classList.toggle("text-stone-500", !on); });
    draw();
  }));
  $$(".showcase-option-btn").forEach(b => b.addEventListener("click", () => {
    role = b.dataset.roleId;
    $$(".showcase-option-btn").forEach(x => { const on = x === b; x.classList.toggle("bg-[#feede6]", on); x.classList.toggle("text-[#a5460f]", on); x.classList.toggle("text-[#3d3d3d]", !on); });
    draw();
  }));
  $("#btn-showcase-action").addEventListener("click", () => { const bx = $("#showcase-bubbles-container"); bx.style.opacity = .4; setTimeout(() => { bx.style.opacity = 1; draw(); }, 300); });
  draw();
}

if (new URLSearchParams(location.search).get("shot") === "1") {  // screenshot mode: no transitions
  const st = document.createElement("style"); st.textContent = "*,*::before,*::after{transition:none!important;animation:none!important}"; document.head.appendChild(st);
}
homepage(); loadExamples();
if (location.hash === "#ai") openAI();
