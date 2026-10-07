/**
 * VRIDDHI (वृद्धि) — Reusable UI Components
 * Data visualizations, interactive cards, gauges, charts & visual widgets.
 */

/**
 * Render Interactive SVG Hiring Trend Chart (2020 - 2030)
 * Past Historical (2020-2024) vs. ARIMA Projected Forecast (2025-2030)
 */
export function renderTrendChart(containerId, historicalData, forecastData, roleTitle) {
  const container = document.getElementById(containerId);
  if (!container) return;

  // Combine data points
  const allPoints = [
    ...historicalData.map(d => ({ year: d.year, val: d.postings, isForecast: false })),
    ...forecastData.map(d => ({ year: d.year, val: d.projected, isForecast: true }))
  ];

  const width = container.clientWidth || 640;
  const height = 260;
  const padding = { top: 30, right: 35, bottom: 45, left: 55 };

  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;

  const minVal = Math.min(...allPoints.map(p => p.val)) * 0.85;
  const maxVal = Math.max(...allPoints.map(p => p.val)) * 1.1;

  const getX = (index) => padding.left + (index / (allPoints.length - 1)) * chartW;
  const getY = (val) => padding.top + chartH - ((val - minVal) / (maxVal - minVal)) * chartH;

  // Historical path & Forecast path
  const histPoints = allPoints.filter(p => !p.isForecast);
  // Include last historical point in forecast for continuous line
  const forecastPoints = [
    histPoints[histPoints.length - 1],
    ...allPoints.filter(p => p.isForecast)
  ];

  let histPath = '';
  histPoints.forEach((p, i) => {
    const idx = allPoints.indexOf(p);
    const x = getX(idx);
    const y = getY(p.val);
    histPath += (i === 0 ? `M ${x} ${y}` : ` L ${x} ${y}`);
  });

  let forecastPath = '';
  forecastPoints.forEach((p, i) => {
    const idx = allPoints.indexOf(p);
    const x = getX(idx);
    const y = getY(p.val);
    forecastPath += (i === 0 ? `M ${x} ${y}` : ` L ${x} ${y}`);
  });

  // Area under curve for historical
  const firstHistX = getX(0);
  const lastHistX = getX(histPoints.length - 1);
  const bottomY = padding.top + chartH;
  const histArea = `${histPath} L ${lastHistX} ${bottomY} L ${firstHistX} ${bottomY} Z`;

  // Grid lines
  let gridLines = '';
  const yTicks = 4;
  for (let i = 0; i <= yTicks; i++) {
    const tickVal = minVal + (i / yTicks) * (maxVal - minVal);
    const y = getY(tickVal);
    gridLines += `
      <line x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" stroke="#e7e5e4" stroke-width="1" stroke-dasharray="3 3"/>
      <text x="${padding.left - 10}" y="${y + 4}" fill="#78716c" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="end">${Math.round(tickVal / 1000)}k</text>
    `;
  }

  // X axis labels
  let xLabels = '';
  allPoints.forEach((p, i) => {
    if (i % 2 === 0 || i === allPoints.length - 1) {
      const x = getX(i);
      xLabels += `
        <text x="${x}" y="${height - 15}" fill="${p.isForecast ? '#c2410c' : '#78716c'}" font-size="11" font-weight="${p.isForecast ? '600' : '400'}" font-family="'JetBrains Mono', monospace" text-anchor="middle">${p.year}${p.isForecast ? '*' : ''}</text>
      `;
    }
  });

  // Data dots
  let dots = '';
  allPoints.forEach((p, i) => {
    const x = getX(i);
    const y = getY(p.val);
    dots += `
      <g class="chart-point-group cursor-pointer" data-year="${p.year}" data-val="${p.val.toLocaleString('en-IN')}" data-forecast="${p.isForecast}">
        <circle cx="${x}" cy="${y}" r="4" fill="${p.isForecast ? '#f97316' : '#1c1917'}" stroke="#ffffff" stroke-width="2" class="transition-all duration-200 hover:r-6"/>
      </g>
    `;
  });

  // Vertical split divider between past & forecast
  const splitX = getX(histPoints.length - 1);

  container.innerHTML = `
    <div class="relative w-full">
      <div class="flex items-center justify-between mb-3 text-xs text-stone-500">
        <div class="flex items-center gap-4">
          <span class="flex items-center gap-1.5"><span class="w-3 h-1 bg-stone-900 rounded-full inline-block"></span> Verified Postings (2020-2024)</span>
          <span class="flex items-center gap-1.5"><span class="w-3 h-1 bg-orange-500 border-dashed border-b-2 border-orange-500 rounded-full inline-block"></span> ARIMA 5-Yr Forecast (2025-2030)</span>
        </div>
        <div class="font-mono text-[11px] bg-stone-100 text-stone-700 px-2 py-0.5 rounded">Tukey 1.5× IQR Calibrated</div>
      </div>
      <svg viewBox="0 0 ${width} ${height}" class="w-full h-auto overflow-visible select-none">
        <defs>
          <linearGradient id="histGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#1c1917" stop-opacity="0.08"/>
            <stop offset="100%" stop-color="#1c1917" stop-opacity="0.0"/>
          </linearGradient>
        </defs>
        ${gridLines}
        <!-- Vertical Forecast Boundary -->
        <line x1="${splitX}" y1="${padding.top}" x2="${splitX}" y2="${bottomY}" stroke="#ea580c" stroke-width="1.5" stroke-dasharray="4 4" opacity="0.6"/>
        <text x="${splitX + 6}" y="${padding.top + 12}" fill="#ea580c" font-size="10" font-family="'Inter', sans-serif" font-weight="600">TODAY / FORECAST HORIZON</text>

        <!-- Historical Area & Path -->
        <path d="${histArea}" fill="url(#histGradient)"/>
        <path d="${histPath}" fill="none" stroke="#1c1917" stroke-width="2.5" stroke-linecap="round"/>

        <!-- Forecast Path (Dashed) -->
        <path d="${forecastPath}" fill="none" stroke="#f97316" stroke-width="2.5" stroke-dasharray="5 4" stroke-linecap="round"/>

        ${dots}
        ${xLabels}
      </svg>
      <div id="chart-tooltip" class="absolute hidden pointer-events-none bg-stone-900 text-white text-xs px-2.5 py-1.5 rounded-lg shadow-lg font-mono z-20"></div>
    </div>
  `;

  // Attach hover interactions
  const tooltip = container.querySelector('#chart-tooltip');
  const pointGroups = container.querySelectorAll('.chart-point-group');

  pointGroups.forEach(group => {
    group.addEventListener('mouseenter', (e) => {
      const year = group.dataset.year;
      const val = group.dataset.val;
      const isForecast = group.dataset.forecast === 'true';

      tooltip.innerHTML = `
        <div class="font-semibold">${year} ${isForecast ? '(Projected)' : '(Verified)'}</div>
        <div class="text-orange-300">${val} Annual Postings</div>
      `;
      tooltip.classList.remove('hidden');

      const rect = group.getBoundingClientRect();
      const parentRect = container.getBoundingClientRect();
      tooltip.style.left = `${rect.left - parentRect.left - 40}px`;
      tooltip.style.top = `${rect.top - parentRect.top - 48}px`;
    });

    group.addEventListener('mouseleave', () => {
      tooltip.classList.add('hidden');
    });
  });
}

/**
 * Render Circular SVG Readiness Score Gauge
 */
export function renderReadinessGauge(containerId, score) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const radius = 52;
  const circumference = 2 * Math.PI * radius; // ~326.7
  const offset = circumference - (score / 100) * circumference;

  let strokeColor = '#16a34a'; // Green
  let labelText = 'Ready for Product Interviews';
  let badgeClass = 'bg-emerald-50 text-emerald-700 border-emerald-200';

  if (score < 60) {
    strokeColor = '#dc2626'; // Red
    labelText = 'Foundational Gaps Present';
    badgeClass = 'bg-rose-50 text-rose-700 border-rose-200';
  } else if (score < 75) {
    strokeColor = '#d97706'; // Amber
    labelText = 'Interview Eligible with Quick Wins';
    badgeClass = 'bg-amber-50 text-amber-700 border-amber-200';
  }

  container.innerHTML = `
    <div class="flex items-center gap-6">
      <div class="relative w-32 h-32 flex-shrink-0">
        <svg class="w-full h-full -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="${radius}" fill="none" stroke="#f5f5f4" stroke-width="9"/>
          <circle cx="60" cy="60" r="${radius}" fill="none" stroke="${strokeColor}" stroke-width="9"
            stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"
            stroke-linecap="round" class="transition-all duration-1000 ease-out"/>
        </svg>
        <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span class="font-mono text-3xl font-bold tracking-tight text-stone-900">${score}%</span>
          <span class="text-[10px] uppercase font-mono tracking-wider text-stone-500">Readiness</span>
        </div>
      </div>
      <div>
        <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${badgeClass} mb-1.5">
          <span class="w-1.5 h-1.5 rounded-full bg-current"></span>
          ${labelText}
        </div>
        <p class="text-sm text-stone-600 leading-snug">Composite readiness based on **483-Skill DAG Ontology** and current job requirements.</p>
        <div class="mt-2 text-xs text-stone-500 font-mono flex items-center gap-3">
          <span>Target Fit: <strong class="text-stone-800">High</strong></span>
          <span>•</span>
          <span>Shortlist Rate: <strong class="text-stone-800">~68%</strong></span>
        </div>
      </div>
    </div>
  `;
}

/**
 * Render Interactive Salary Range Visualizer
 */
export function renderSalaryRangeVisual(containerId, min, p50, max, candMin, candMax) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const totalMin = Math.floor(min * 0.85);
  const totalMax = Math.ceil(max * 1.15);
  const totalRange = totalMax - totalMin;

  const getPercent = (val) => ((val - totalMin) / totalRange) * 100;

  const p25Pct = getPercent(min);
  const p50Pct = getPercent(p50);
  const p75Pct = getPercent(max);

  const candMinPct = getPercent(candMin);
  const candMaxPct = getPercent(candMax);

  container.innerHTML = `
    <div class="space-y-4">
      <div class="relative pt-6 pb-4">
        <!-- Baseline track -->
        <div class="h-3 bg-stone-100 rounded-full w-full relative">
          <!-- Market Range (P25 to P75) -->
          <div class="absolute top-0 bottom-0 bg-stone-200 rounded-full"
               style="left: ${p25Pct}%; width: ${p75Pct - p25Pct}%"></div>
          
          <!-- Candidate Value (Orange highlight) -->
          <div class="absolute top-0 bottom-0 bg-gradient-to-r from-orange-400 to-orange-500 rounded-full shadow-sm"
               style="left: ${candMinPct}%; width: ${candMaxPct - candMinPct}%"></div>
        </div>

        <!-- P25 Marker -->
        <div class="absolute top-0 text-[11px] font-mono text-stone-500 -translate-x-1/2" style="left: ${p25Pct}%">
          ₹${min.toFixed(1)}L <span class="text-[9px] block text-stone-400">P25</span>
        </div>

        <!-- P50 Marker -->
        <div class="absolute top-0 text-[11px] font-mono font-semibold text-stone-900 -translate-x-1/2" style="left: ${p50Pct}%">
          ₹${p50.toFixed(1)}L <span class="text-[9px] block text-stone-600">P50 (Median)</span>
        </div>

        <!-- P75 Marker -->
        <div class="absolute top-0 text-[11px] font-mono text-stone-500 -translate-x-1/2" style="left: ${p75Pct}%">
          ₹${max.toFixed(1)}L <span class="text-[9px] block text-stone-400">P75</span>
        </div>

        <!-- Candidate Value Pin -->
        <div class="absolute bottom-0 text-[11px] font-mono text-orange-600 font-semibold -translate-x-1/2 flex flex-col items-center"
             style="left: ${(candMinPct + candMaxPct) / 2}%">
          <span class="w-2 h-2 rounded-full bg-orange-600 mb-0.5"></span>
          <span>₹${candMin.toFixed(1)}L – ₹${candMax.toFixed(1)}L</span>
          <span class="text-[9px] text-orange-500 uppercase tracking-wider font-sans">Your Calibrated Worth</span>
        </div>
      </div>
      <div class="flex items-center justify-between text-xs text-stone-500 border-t border-stone-100 pt-2 font-mono">
        <span>Low Bound: ₹${totalMin}L LPA</span>
        <span class="text-stone-400">Fixed Base + Performance Bonus</span>
        <span>Upper Bound: ₹${totalMax}L LPA</span>
      </div>
    </div>
  `;
}

/**
 * Render Ranked Job Card
 */
export function renderJobCard(job) {
  const matchColor = job.match_score >= 80 ? 'text-emerald-700 bg-emerald-50 border-emerald-200' :
                     job.match_score >= 70 ? 'text-amber-700 bg-amber-50 border-amber-200' :
                     'text-stone-700 bg-stone-50 border-stone-200';

  const modeBadge = job.work_mode === 'Remote' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                    job.work_mode === 'Hybrid' ? 'bg-purple-50 text-purple-700 border-purple-200' :
                    'bg-stone-100 text-stone-700 border-stone-200';

  return `
    <div class="job-card group relative bg-white border border-stone-200 rounded-2xl p-6 hover:border-orange-300 hover:shadow-lg transition-all duration-300">
      <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-3 mb-4">
        <div>
          <div class="flex items-center gap-2 mb-1 flex-wrap">
            <span class="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-mono font-medium border ${modeBadge}">
              ${job.work_mode}
            </span>
            <span class="text-xs text-stone-400 font-mono">• ${job.city} (${job.area})</span>
            <span class="text-xs text-stone-400 font-mono">• ${job.posted_ago}</span>
          </div>
          <h4 class="text-lg font-semibold text-stone-900 group-hover:text-orange-600 transition-colors">
            ${job.title}
          </h4>
          <p class="text-sm font-medium text-stone-600">${job.company}</p>
        </div>

        <div class="flex sm:flex-col items-end justify-between sm:justify-start gap-1">
          <div class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-mono font-semibold border ${matchColor}">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            ${job.match_score}% Match
          </div>
          <div class="font-mono text-base font-bold text-stone-900">
            ₹${job.salary_min.toFixed(1)}L – ₹${job.salary_max.toFixed(1)}L <span class="text-xs font-normal text-stone-500">LPA</span>
          </div>
        </div>
      </div>

      <p class="text-xs text-stone-600 leading-relaxed line-clamp-2 mb-4">
        ${job.description}
      </p>

      <div class="space-y-2 border-t border-stone-100 pt-3 mb-4">
        <div class="flex items-center gap-1.5 flex-wrap">
          <span class="text-[11px] text-stone-400 font-mono mr-1">Matched:</span>
          ${job.matched_skills.map(s => `
            <span class="inline-flex items-center text-[11px] px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 font-medium border border-emerald-200">
              ✓ ${s}
            </span>
          `).join('')}
        </div>
        ${job.missing_skills.length ? `
          <div class="flex items-center gap-1.5 flex-wrap">
            <span class="text-[11px] text-stone-400 font-mono mr-1">Missing:</span>
            ${job.missing_skills.map(s => `
              <span class="inline-flex items-center text-[11px] px-2 py-0.5 rounded bg-rose-50 text-rose-700 font-medium border border-rose-200">
                + ${s}
              </span>
            `).join('')}
          </div>
        ` : ''}
      </div>

      <div class="flex items-center justify-between pt-2">
        <div class="text-xs text-stone-500 font-mono">
          <span class="text-stone-700 font-semibold">${job.applicants_count}</span> applicants • ${job.experience_req}
        </div>
        <div class="flex items-center gap-2">
          <button class="btn-direct-apply btn-secondary text-xs py-1.5 px-3 rounded-full" data-job-id="${job.job_id}">
            Inspect Insights
          </button>
          <a href="${job.apply_url}" target="_blank" rel="noopener noreferrer"
             class="btn-primary text-xs py-1.5 px-4 rounded-full inline-flex items-center gap-1">
            Apply Now
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
          </a>
        </div>
      </div>
    </div>
  `;
}

/**
 * Render Dynamic Prerequisite Learning Pathway with Hours Slider recalibration
 */
export function renderRoadmap(containerId, roadmap, weeklyHours = 15) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const totalHours = roadmap.reduce((acc, phase) => acc + phase.est_hours, 0);
  const totalWeeks = (totalHours / weeklyHours).toFixed(1);
  const totalMonths = (totalWeeks / 4.2).toFixed(1);

  container.innerHTML = `
    <div class="space-y-6">
      <div class="bg-stone-50 border border-stone-200 rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div class="text-xs uppercase font-mono tracking-wider text-stone-500">Curriculum Velocity Estimator</div>
          <div class="text-stone-900 font-semibold text-sm">
            Total Path Effort: <span class="font-mono text-orange-600">${totalHours} Hours</span>
            <span class="text-stone-400 mx-2">•</span>
            Estimated Timeline: <span class="font-mono text-stone-900 font-bold">${totalWeeks} Weeks</span> (~${totalMonths} Months)
          </div>
        </div>
        <div class="flex items-center gap-3">
          <label class="text-xs font-mono text-stone-600 whitespace-nowrap">Dedication:</label>
          <input type="range" id="weekly-hours-slider" min="5" max="40" step="5" value="${weeklyHours}"
                 class="w-32 accent-orange-600 cursor-pointer"/>
          <span class="font-mono text-xs font-semibold text-stone-900 w-16 text-right">${weeklyHours} hrs/wk</span>
        </div>
      </div>

      <div class="relative pl-6 space-y-6 before:content-[''] before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-stone-200">
        ${roadmap.map((phase, idx) => {
          const phaseWeeks = (phase.est_hours / weeklyHours).toFixed(1);
          return `
            <div class="relative group">
              <!-- Dot Indicator -->
              <div class="absolute -left-6 top-1.5 w-4 h-4 rounded-full border-2 ${idx === 0 ? 'bg-orange-500 border-white ring-2 ring-orange-200' : 'bg-white border-stone-300'}"></div>
              
              <div class="bg-white border border-stone-200 rounded-xl p-4 hover:border-stone-300 transition-all">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-2">
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-stone-100 text-stone-700">
                      Phase ${phase.phase}
                    </span>
                    <h5 class="text-sm font-semibold text-stone-900">${phase.skill}</h5>
                  </div>
                  <div class="font-mono text-xs text-stone-500">
                    ${phase.est_hours} hrs • <strong class="text-stone-800">~${phaseWeeks} wks</strong>
                  </div>
                </div>

                <p class="text-xs text-stone-600 leading-relaxed mb-3">
                  ${phase.description}
                </p>

                <div class="flex items-center gap-2 flex-wrap text-[11px] font-mono text-stone-500">
                  <span>Prerequisites:</span>
                  ${phase.prerequisites.map(p => `
                    <span class="px-1.5 py-0.5 rounded bg-stone-100 text-stone-700 font-medium">
                      ${p}
                    </span>
                  `).join('')}
                </div>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    </div>
  `;
}

/**
 * Toast Notification Helper
 */
export function showToast(message, type = 'info') {
  let toastContainer = document.getElementById('vriddhi-toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'vriddhi-toast-container';
    toastContainer.className = 'fixed bottom-5 right-5 z-50 flex flex-col gap-2 pointer-events-none';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  const bgClass = type === 'success' ? 'bg-emerald-900 text-emerald-100 border-emerald-700' :
                  type === 'warning' ? 'bg-amber-900 text-amber-100 border-amber-700' :
                  'bg-stone-900 text-stone-100 border-stone-700';

  toast.className = `pointer-events-auto flex items-center gap-2 px-4 py-3 rounded-xl border text-xs font-sans shadow-xl transform translate-y-4 opacity-0 transition-all duration-300 ${bgClass}`;
  toast.innerHTML = `
    <span class="w-1.5 h-1.5 rounded-full bg-orange-400"></span>
    <span>${message}</span>
  `;

  toastContainer.appendChild(toast);

  // Trigger animation
  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-4', 'opacity-0');
    toast.classList.add('translate-y-0', 'opacity-100');
  });

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
