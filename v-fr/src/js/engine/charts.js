// Native SVG charts (design system rule: no chart libraries). Each returns an SVG string or mounts into a container.
import { colorOf, DIM, DIMS } from "./dims.js";

export const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
export const pct = (x, d = 0) => (x == null ? "-" : `${(100 * x).toFixed(d)}%`);
const reduce = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// ---------------------------------------------------------------- tooltip (any element with data-tip)
const tip = () => document.getElementById("tip");
document.addEventListener("mousemove", e => {
  const t = e.target.closest?.("[data-tip]"); const el = tip(); if (!el) return;
  if (t) { el.innerHTML = t.getAttribute("data-tip"); el.style.opacity = 1; el.style.left = e.clientX + 14 + "px"; el.style.top = e.clientY + 12 + "px"; }
  else el.style.opacity = 0;
});

export function countUp(el, to, { dur = 900, fmt = v => Math.round(v).toLocaleString("en-IN") } = {}) {
  if (!el) return;
  if (reduce()) { el.textContent = fmt(to); return; }
  const t0 = performance.now();
  const step = t => { const k = Math.min(1, (t - t0) / dur); el.textContent = fmt(to * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(step); };
  requestAnimationFrame(step);
  setTimeout(() => (el.textContent = fmt(to)), dur + 60);  // guarantee the exact final value even if frames are throttled
}

// ---------------------------------------------------------------- gauge with baseline tick
export function gauge(p, base, label = "probability") {
  const r = 50, C = 2 * Math.PI * r, col = p >= 0.5 ? "#16a34a" : p >= 0.3 ? "#d97706" : "#dc2626";
  const a = 2 * Math.PI * base - Math.PI / 2, x1 = 60 + 44 * Math.cos(a), y1 = 60 + 44 * Math.sin(a), x2 = 60 + 58 * Math.cos(a), y2 = 60 + 58 * Math.sin(a);
  return `<svg viewBox="0 0 120 120" width="170" height="170" role="img" aria-label="${esc(label)} ${pct(p)}">
    <circle cx="60" cy="60" r="${r}" fill="none" stroke="#f5f5f4" stroke-width="9"/>
    <circle cx="60" cy="60" r="${r}" fill="none" stroke="${col}" stroke-width="9" stroke-linecap="round" transform="rotate(-90 60 60)"
      stroke-dasharray="${C}" stroke-dashoffset="${C}" class="g-arc" data-to="${C * (1 - p)}" style="transition:stroke-dashoffset .9s cubic-bezier(.16,1,.3,1)"/>
    <line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#1f1f1f" stroke-width="2" data-tip="Baseline ${pct(base, 1)} (share in the training data)"/>
    <text x="60" y="58" text-anchor="middle" style="font:800 22px 'JetBrains Mono';fill:#1c1917" class="g-num">${pct(p, p < 0.1 || p > 0.9 ? 1 : 0)}</text>
    <text x="60" y="76" text-anchor="middle" style="font:600 8px 'JetBrains Mono';fill:#a8a29e">BASELINE ${pct(base)}</text></svg>`;
}
export function animateGauges(root = document) {
  requestAnimationFrame(() => root.querySelectorAll(".g-arc").forEach(c => (c.style.strokeDashoffset = c.dataset.to)));
}

// ---------------------------------------------------------------- waterfall in probability space
export function waterfall(wf, nameOf, colorOfFeature, startLabel = "Average person in training data") {
  const W = 760, rowH = 34, top = 30, left = 220, right = 70, H = top + rowH * (wf.length + 2) + 30;
  const x = p => left + p * (W - left - right);
  let s = `<svg class="chart" viewBox="0 0 ${W} ${H}">`;
  for (let g = 0; g <= 1.0001; g += 0.25) s += `<line class="grid" x1="${x(g)}" x2="${x(g)}" y1="${top - 8}" y2="${H - 26}"/><text class="tick" x="${x(g)}" y="${H - 10}" text-anchor="middle">${Math.round(g * 100)}%</text>`;
  const p0 = wf[0].p_from, row = (i, label, a, b, col, tipTxt) => {
    const y = top + i * rowH, lo = Math.min(a, b), hi = Math.max(a, b);
    return `<text x="${left - 10}" y="${y + 19}" text-anchor="end" style="font-size:12px">${esc(label)}</text>
      <rect x="${x(lo)}" y="${y + 6}" width="${Math.max(2, x(hi) - x(lo))}" height="20" rx="5" fill="${col}" data-tip="${esc(tipTxt)}"/>
      <text class="tick" x="${x(hi) + 6}" y="${y + 20}">${b >= a ? "+" : ""}${((b - a) * 100).toFixed(1)} pts</text>`;
  };
  s += row(0, startLabel, 0, p0, "#d6d3d1", `Prediction for someone at the training-data average: ${pct(p0, 1)}`);
  wf.forEach((c, i) => {
    const up = c.p_to >= c.p_from;
    s += row(i + 1, `${nameOf(c)} = ${c.value}`, c.p_from, c.p_to, up ? "#16a34a" : "#dc2626",
      `${nameOf(c)}: value ${c.value} vs mean ${c.mean}. Logit effect ${c.logit_effect >= 0 ? "+" : ""}${c.logit_effect} = coefficient ${c.coef} x (value - mean). Moves ${pct(c.p_from, 1)} to ${pct(c.p_to, 1)}.`);
    s += `<circle cx="${left - 212}" cy="${top + (i + 1) * rowH + 16}" r="4" fill="${colorOfFeature(c)}"/>`;
  });
  const pe = wf[wf.length - 1].p_to, y = top + (wf.length + 1) * rowH;
  s += `<text x="${left - 10}" y="${y + 19}" text-anchor="end" style="font-size:12px;font-weight:700">This profile</text>
    <rect x="${x(0)}" y="${y + 6}" width="${x(pe) - x(0)}" height="20" rx="5" fill="#1e2033"/><text class="tick" x="${x(pe) + 6}" y="${y + 20}" style="font-weight:700;fill:#1c1917">${pct(pe, 1)}</text>`;
  return s + "</svg>";
}

// ---------------------------------------------------------------- radar
export function radar(axes, series, { size = 360, max = 1 } = {}) {
  const c = size / 2, R = size / 2 - 70, n = axes.length, ang = i => -Math.PI / 2 + (2 * Math.PI * i) / n;
  const pt = (i, v) => [c + R * (v / max) * Math.cos(ang(i)), c + R * (v / max) * Math.sin(ang(i))];
  let s = `<svg class="chart" viewBox="0 0 ${size} ${size}" style="max-width:${size + 40}px;margin:auto">`;
  [0.25, 0.5, 0.75, 1].forEach(k => (s += `<polygon points="${axes.map((_, i) => pt(i, k * max).join(",")).join(" ")}" fill="none" stroke="#e7e5e4"/>`));
  axes.forEach((a, i) => {
    const [x, y] = pt(i, max), [lx, ly] = pt(i, max * 1.2);
    s += `<line x1="${c}" y1="${c}" x2="${x}" y2="${y}" stroke="#e7e5e4"/>
      <text x="${lx}" y="${ly}" text-anchor="middle" dominant-baseline="middle" style="font-size:11.5px;font-weight:600;fill:${a.color}">${esc(a.label)}</text>`;
  });
  series.forEach(se => {
    const pts = se.values.map((v, i) => pt(i, Math.max(0, Math.min(max, v))).join(",")).join(" ");
    s += `<polygon points="${pts}" fill="${se.fill || "none"}" stroke="${se.color}" stroke-width="2.4" ${se.dash ? 'stroke-dasharray="6 4"' : ""}/>`;
    se.values.forEach((v, i) => { const [x, y] = pt(i, Math.max(0, Math.min(max, v))); s += `<circle cx="${x}" cy="${y}" r="4" fill="${se.color}" data-tip="${esc(se.name)}: ${esc(se.fmt ? se.fmt(v, i) : v)}"/>`; });
  });
  return s + "</svg>";
}

// ---------------------------------------------------------------- horizontal bars
export function hbars(rows, { W = 760, left = 230, max, fmt = v => v, unit = "", rowH = 26, minV = 0 } = {}) {
  max = max ?? Math.max(...rows.map(r => r.value), 1e-9);
  const lo = Math.min(minV, ...rows.map(r => r.value)), H = rows.length * rowH + 34, x = v => left + ((v - lo) / (max - lo)) * (W - left - 120);
  let s = `<svg class="chart" viewBox="0 0 ${W} ${H}">`;
  if (lo < 0) s += `<line x1="${x(0)}" x2="${x(0)}" y1="0" y2="${H - 24}" stroke="#a8a29e"/>`;
  rows.forEach((r, i) => {
    const y = i * rowH + 4, a = x(Math.min(0, r.value)), b = x(Math.max(0, r.value));
    s += `<text x="${left - 10}" y="${y + 15}" text-anchor="end" style="font-size:12px">${esc(r.label)}</text>
      <rect x="${a}" y="${y + 3}" width="${Math.max(1.5, b - a)}" height="${rowH - 9}" rx="4" fill="${r.color || "#6366f1"}" data-tip="${esc(r.tip || r.label + ": " + fmt(r.value) + unit)}"/>
      <text class="tick" x="${b + 6}" y="${y + 15}">${fmt(r.value)}${unit}${r.n != null ? `  n=${r.n.toLocaleString("en-IN")}` : ""}</text>`;
  });
  return s + `</svg>`;
}

// ---------------------------------------------------------------- vertical bars (salary bands)
export function vbars(rows, { W = 560, H = 230, fmt = v => pct(v), highlight } = {}) {
  const max = Math.max(...rows.map(r => r.value), 1e-9), bw = (W - 60) / rows.length;
  let s = `<svg class="chart" viewBox="0 0 ${W} ${H}">`;
  rows.forEach((r, i) => {
    const h = (r.value / max) * (H - 70), x = 40 + i * bw + 8, y = H - 40 - h;
    s += `<rect x="${x}" y="${y}" width="${bw - 16}" height="${h}" rx="6" fill="${r.key === highlight ? "#e96c2f" : "#c7d2fe"}" data-tip="${esc(r.label)}: ${fmt(r.value)}"/>
      <text class="tick" x="${x + (bw - 16) / 2}" y="${y - 6}" text-anchor="middle">${fmt(r.value)}</text>
      <text x="${x + (bw - 16) / 2}" y="${H - 22}" text-anchor="middle" style="font-size:11px">${esc(r.label)}</text>`;
  });
  return s + `<text class="tick" x="${W / 2}" y="${H - 4}" text-anchor="middle">salary band (Rs lakh per annum)</text></svg>`;
}

// ---------------------------------------------------------------- heatmap
export function heatmap(rowLabels, colLabels, cell, { W = 900, left = 230, rowH = 34, onClick } = {}) {
  const cw = (W - left) / colLabels.length, H = 46 + rowLabels.length * rowH;
  let s = `<svg class="chart" viewBox="0 0 ${W} ${H}">`;
  colLabels.forEach((c, j) => (s += `<text x="${left + j * cw + cw / 2}" y="18" text-anchor="middle" style="font-size:11.5px;font-weight:600;fill:${c.color || "#57534e"}">${esc(c.label)}</text>`));
  rowLabels.forEach((r, i) => {
    s += `<text x="${left - 10}" y="${40 + i * rowH + rowH / 2}" text-anchor="end" style="font-size:12px">${esc(r)}</text>`;
    colLabels.forEach((c, j) => {
      const v = cell(i, j);
      s += `<g class="hcell" data-i="${i}" data-j="${j}" style="cursor:${onClick ? "pointer" : "default"}"><rect x="${left + j * cw + 2}" y="${30 + i * rowH}" width="${cw - 4}" height="${rowH - 4}" rx="7" fill="${v.fill}" stroke="${v.stroke || "none"}" data-tip="${esc(v.tip)}"/>
        <text x="${left + j * cw + cw / 2}" y="${30 + i * rowH + rowH / 2 + 2}" text-anchor="middle" style="font:600 11px 'JetBrains Mono';fill:${v.ink || "#1c1917"}">${esc(v.text)}</text></g>`;
    });
  });
  return s + "</svg>";
}

// ---------------------------------------------------------------- sankey (3 columns)
export function sankey(data, { W = 1000, H = 560 } = {}) {
  const cols = { role: 0, dim: 1, band: 2 }, colX = [10, W / 2 - 80, W - 170], nw = 16, pad = 10;
  const nodes = data.nodes.map(n => ({ ...n, in: 0, out: 0 }));
  const byId = Object.fromEntries(nodes.map(n => [n.id, n]));
  data.links.forEach(l => { byId[l.source].out += l.value; byId[l.target].in += l.value; });
  nodes.forEach(n => (n.v = Math.max(n.in, n.out)));
  const scaleBy = Math.min(...[0, 1, 2].map(c => { const ns = nodes.filter(n => cols[n.kind] === c); return (H - pad * (ns.length - 1) - 20) / ns.reduce((a, n) => a + n.v, 0); }));
  [0, 1, 2].forEach(c => {
    let y = 10; nodes.filter(n => cols[n.kind] === c).sort((a, b) => (c === 2 ? 0 : b.v - a.v)).forEach(n => { n.x = colX[c]; n.y = y; n.h = Math.max(3, n.v * scaleBy); n.yo = y; n.yi = y; y += n.h + pad; });
  });
  let s = `<svg class="chart" viewBox="0 0 ${W} ${H}">`;
  const links = [...data.links].sort((a, b) => byId[a.source].y - byId[b.source].y || byId[a.target].y - byId[b.target].y);
  links.forEach(l => {
    const a = byId[l.source], b = byId[l.target], h = l.value * scaleBy, x0 = a.x + nw, x1 = b.x, y0 = a.yo + h / 2, y1 = b.yi + h / 2;
    a.yo += h; b.yi += h;
    const col = a.kind === "dim" ? colorOf(a.dim) : b.kind === "dim" ? colorOf(b.dim) : "#a8a29e", hi = b.kind === "band" && /15-25|25-50/.test(b.label);
    s += `<path d="M${x0},${y0} C${(x0 + x1) / 2},${y0} ${(x0 + x1) / 2},${y1} ${x1},${y1}" stroke="${col}" stroke-opacity="${hi ? 0.5 : 0.22}" stroke-width="${Math.max(1, h)}" fill="none"
      data-tip="${esc(a.label)} to ${esc(b.label)}: ${l.value.toLocaleString("en-IN")} postings"/>`;
  });
  nodes.forEach(n => {
    const col = n.kind === "dim" ? colorOf(n.dim) : n.kind === "band" ? "#1e2033" : "#a8a29e";
    s += `<rect x="${n.x}" y="${n.y}" width="${nw}" height="${n.h}" rx="3" fill="${col}" data-tip="${esc(n.label)}: ${n.v.toLocaleString("en-IN")}"/>
      <text x="${n.kind === "band" ? n.x + nw + 6 : n.x + nw + 6}" y="${n.y + n.h / 2 + 4}" style="font-size:11.5px;font-weight:600">${esc(n.label)}</text>`;
  });
  return s + "</svg>";
}

// ---------------------------------------------------------------- calibration + confusion
export function calibration(points) {
  const W = 360, H = 300, l = 46, b = 40, x = v => l + v * (W - l - 16), y = v => H - b - v * (H - b - 16);
  let s = `<svg class="chart" viewBox="0 0 ${W} ${H}" style="max-width:420px"><line x1="${x(0)}" y1="${y(0)}" x2="${x(1)}" y2="${y(1)}" stroke="#d6d3d1" stroke-dasharray="5 4"/>`;
  [0, 0.5, 1].forEach(g => (s += `<text class="tick" x="${x(g)}" y="${H - b + 16}" text-anchor="middle">${g}</text><text class="tick" x="${l - 8}" y="${y(g) + 3}" text-anchor="end">${g}</text>`));
  s += `<polyline fill="none" stroke="#6366f1" stroke-width="2.4" points="${points.map(p => `${x(p.pred)},${y(p.obs)}`).join(" ")}"/>`;
  points.forEach(p => (s += `<circle cx="${x(p.pred)}" cy="${y(p.obs)}" r="${3 + Math.sqrt(p.n)}" fill="#6366f1" fill-opacity=".35" stroke="#6366f1" data-tip="predicted ${pct(p.pred)} vs observed ${pct(p.obs)} (n=${p.n})"/>`));
  return s + `<text x="${W / 2}" y="${H - 6}" text-anchor="middle" style="font-size:11px">predicted probability (unseen folds)</text><text x="12" y="${H / 2}" transform="rotate(-90 12 ${H / 2})" text-anchor="middle" style="font-size:11px">observed share</text></svg>`;
}
export function confusion(cm, labels = ["Low", "High"]) {
  const v = [[cm.tn, cm.fp], [cm.fn, cm.tp]], mx = Math.max(cm.tn, cm.fp, cm.fn, cm.tp);
  let s = `<svg class="chart" viewBox="0 0 300 250" style="max-width:340px">`;
  [0, 1].forEach(i => [0, 1].forEach(j => {
    const a = v[i][j] / mx;
    s += `<rect x="${90 + j * 100}" y="${30 + i * 100}" width="96" height="96" rx="12" fill="rgba(99,102,241,${0.12 + 0.75 * a})"/>
      <text x="${138 + j * 100}" y="${84 + i * 100}" text-anchor="middle" style="font:800 22px 'JetBrains Mono';fill:${a > .55 ? "#fff" : "#1c1917"}">${v[i][j]}</text>`;
  }));
  return s + `<text x="138" y="20" text-anchor="middle">Pred. ${labels[0]}</text><text x="238" y="20" text-anchor="middle">Pred. ${labels[1]}</text>
    <text x="84" y="84" text-anchor="end">Actual ${labels[0]}</text><text x="84" y="184" text-anchor="end">Actual ${labels[1]}</text></svg>`;
}

// ---------------------------------------------------------------- force-directed knowledge graph (own simulation)
export function forceGraph(box, data, opts = {}) {
  const W = 1100, H = 560, nodes = data.nodes.map(n => ({ ...n })), byId = Object.fromEntries(nodes.map(n => [n.id, n]));
  const edges = data.edges.filter(e => byId[e.source] && byId[e.target]).map(e => ({ ...e, s: byId[e.source], t: byId[e.target] }));
  let seed = 7; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  nodes.forEach(n => { n.x = W / 2 + (rnd() - 0.5) * 600; n.y = H / 2 + (rnd() - 0.5) * 400; n.vx = 0; n.vy = 0; n.r = n.kind === "skill" ? 5 + Math.sqrt(n.count) / 4 : n.kind === "role" ? 11 : 10; });
  for (let it = 0; it < 320; it++) {
    const k = 1 - it / 320;
    for (let i = 0; i < nodes.length; i++) for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j]; let dx = a.x - b.x, dy = a.y - b.y, d2 = dx * dx + dy * dy + 0.01; const f = 2400 / d2;
      a.vx += dx * f * 0.02; a.vy += dy * f * 0.02; b.vx -= dx * f * 0.02; b.vy -= dy * f * 0.02;
    }
    edges.forEach(e => { const dx = e.t.x - e.s.x, dy = e.t.y - e.s.y, d = Math.sqrt(dx * dx + dy * dy) || 1, L = e.kind === "skill-skill" ? 70 : 120, f = (d - L) * 0.012; e.s.vx += dx / d * f * d * 0.05; e.s.vy += dy / d * f * d * 0.05; e.t.vx -= dx / d * f * d * 0.05; e.t.vy -= dy / d * f * d * 0.05; });
    nodes.forEach(n => { n.vx += (W / 2 - n.x) * 0.004; n.vy += (H / 2 - n.y) * 0.004; n.x += n.vx * 0.5 * k; n.y += n.vy * 0.5 * k; n.vx *= 0.6; n.vy *= 0.6; n.x = Math.max(30, Math.min(W - 30, n.x)); n.y = Math.max(20, Math.min(H - 20, n.y)); });
  }
  const nbr = {}; edges.forEach(e => { (nbr[e.s.id] ||= new Set()).add(e.t.id); (nbr[e.t.id] ||= new Set()).add(e.s.id); });
  const hl = new Set(opts.highlight || []), hlNbr = new Set(); hl.forEach(id => (nbr[id] || []).forEach(x => !hl.has(x) && byId[x]?.kind === "skill" && hlNbr.add(x)));
  const shape = n => n.kind === "role" ? `<rect x="${n.x - n.r}" y="${n.y - n.r}" width="${2 * n.r}" height="${2 * n.r}" rx="3"` :
    n.kind === "band" ? `<polygon points="${n.x},${n.y - n.r} ${n.x + n.r},${n.y} ${n.x},${n.y + n.r} ${n.x - n.r},${n.y}"` : `<circle cx="${n.x}" cy="${n.y}" r="${n.r}"`;
  const draw = () => {
    const dimF = opts.dimFilter;
    let s = `<g class="vp">`;
    edges.forEach(e => {
      const on = hl.size && (hl.has(e.s.id) || hl.has(e.t.id));
      s += `<line data-e="${e.s.id}|${e.t.id}" x1="${e.s.x}" y1="${e.s.y}" x2="${e.t.x}" y2="${e.t.y}" stroke="${on ? "#e96c2f" : "#d6d3d1"}" stroke-opacity="${on ? .9 : .45}" stroke-width="${e.kind === "skill-skill" ? Math.min(4, e.weight / 2) : 1}"/>`;
    });
    nodes.forEach(n => {
      const faded = dimF && n.kind === "skill" && n.dim !== dimF, fill = n.kind === "skill" ? colorOf(n.dim) : n.kind === "role" ? "#1e2033" : "#a5460f";
      const ring = hl.has(n.id) ? 'stroke="#e96c2f" stroke-width="3"' : hlNbr.has(n.id) ? 'stroke="#e96c2f" stroke-width="2.5" class="learn"' : 'stroke="#fff" stroke-width="1.5"';
      s += `<g class="gn" data-id="${esc(n.id)}" style="opacity:${faded ? .15 : 1}">${shape(n)} fill="${fill}" ${ring} data-tip="${esc(n.label)} (${n.kind}${n.count ? `, ${n.count.toLocaleString("en-IN")} postings` : ""})${hlNbr.has(n.id) ? "<br><b>learn next</b>: neighbour of your skills" : ""}"/>
        ${(n.kind !== "skill" || n.r > 10 || hl.has(n.id) || hlNbr.has(n.id)) ? `<text x="${n.x}" y="${n.y - n.r - 4}" text-anchor="middle" style="font-size:10.5px;font-weight:600;pointer-events:none">${esc(n.label)}</text>` : ""}</g>`;
    });
    return s + "</g>";
  };
  box.innerHTML = `<svg viewBox="0 0 ${W} ${H}">${draw()}</svg>`;
  const svg = box.querySelector("svg");
  let drag = null;
  svg.addEventListener("mousedown", e => { const g = e.target.closest(".gn"); if (g) drag = byId[g.dataset.id]; });
  window.addEventListener("mouseup", () => (drag = null));
  svg.addEventListener("mousemove", e => {
    if (drag) { const pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY; const p = pt.matrixTransform(svg.getScreenCTM().inverse()); drag.x = p.x; drag.y = p.y; svg.innerHTML = draw(); return; }
    const g = e.target.closest(".gn"); svg.querySelectorAll("line").forEach(l => { const [a, b] = l.dataset.e.split("|"); l.style.strokeOpacity = g ? (a === g.dataset.id || b === g.dataset.id ? 1 : .08) : ""; });
  });
  return { learnNext: [...hlNbr].map(id => byId[id].label) };
}

// ---------------------------------------------------------------- embedding scatter with zoom/pan and hull
export function scatter(box, pts, opts = {}) {
  const W = 1100, H = 560, xs = pts.map(p => p.x), ys = pts.map(p => p.y), [x0, x1, y0, y1] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
  const X = v => 30 + (v - x0) / (x1 - x0) * (W - 60), Y = v => 20 + (v - y0) / (y1 - y0) * (H - 40);
  const hl = new Set(opts.highlight || []), sug = new Set(opts.suggest || []);
  const mx = Math.max(...pts.map(p => p.count));
  let s = "";
  const hp = pts.filter(p => hl.has(p.id)).map(p => [X(p.x), Y(p.y)]);
  if (hp.length >= 3) s += `<polygon points="${hull(hp).map(p => p.join(",")).join(" ")}" fill="#e96c2f" fill-opacity=".08" stroke="#e96c2f" stroke-dasharray="5 4"/>`;
  pts.forEach(p => {
    const r = 3 + 9 * Math.sqrt(p.count / mx), on = hl.has(p.id), sg = sug.has(p.id);
    s += `<circle cx="${X(p.x)}" cy="${Y(p.y)}" r="${r}" fill="${colorOf(p.dimension)}" fill-opacity="${on || sg ? 1 : .55}" stroke="${on ? "#1c1917" : sg ? "#e96c2f" : "none"}" stroke-width="${on || sg ? 2.5 : 0}" ${sg ? 'class="learn"' : ""}
      data-tip="<b>${esc(p.label)}</b> (${p.count.toLocaleString("en-IN")} postings)<br>nearest: ${esc(p.neighbours.join(", "))}"/>`;
    if (on || sg || p.count > mx * 0.25) s += `<text x="${X(p.x) + r + 3}" y="${Y(p.y) + 4}" style="font-size:${on ? 12 : 10.5}px;font-weight:${on ? 700 : 500};pointer-events:none">${esc(p.label)}</text>`;
  });
  box.innerHTML = `<svg viewBox="0 0 ${W} ${H}"><g class="vp">${s}</g></svg>`;
  const svg = box.querySelector("svg"), vp = svg.querySelector(".vp"); let k = 1, tx = 0, ty = 0, pan = null;
  const apply = () => vp.setAttribute("transform", `translate(${tx},${ty}) scale(${k})`);
  svg.addEventListener("wheel", e => { e.preventDefault(); const f = e.deltaY < 0 ? 1.15 : 1 / 1.15, r = svg.getBoundingClientRect(), mx_ = (e.clientX - r.left) * W / r.width, my = (e.clientY - r.top) * H / r.height; tx = mx_ - (mx_ - tx) * f; ty = my - (my - ty) * f; k *= f; apply(); }, { passive: false });
  svg.addEventListener("mousedown", e => (pan = [e.clientX, e.clientY, tx, ty]));
  window.addEventListener("mouseup", () => (pan = null));
  svg.addEventListener("mousemove", e => { if (!pan) return; const r = svg.getBoundingClientRect(); tx = pan[2] + (e.clientX - pan[0]) * W / r.width; ty = pan[3] + (e.clientY - pan[1]) * H / r.height; apply(); });
}
function hull(P) {
  P = [...P].sort((a, b) => a[0] - b[0] || a[1] - b[1]); const cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lo = [], up = []; for (const p of P) { while (lo.length >= 2 && cr(lo[lo.length - 2], lo[lo.length - 1], p) <= 0) lo.pop(); lo.push(p); }
  for (const p of [...P].reverse()) { while (up.length >= 2 && cr(up[up.length - 2], up[up.length - 1], p) <= 0) up.pop(); up.push(p); }
  return lo.slice(0, -1).concat(up.slice(0, -1));
}

export const dimLegend = () => `<div class="legend">${DIMS.map(d => `<span><i class="dot" style="background:${d.color}"></i>${d.label}</span>`).join("")}<span><i class="dot" style="background:#78716c"></i>Other</span></div>`;
export const dimDot = k => `<i class="dot" style="background:${colorOf(k)}"></i>`;
export { DIM };
