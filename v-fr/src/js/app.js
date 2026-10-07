/**
 * VRIDDHI (वृद्धि) — Frontend App Orchestrator
 * High-performance, minimal editorial experience matching Sarvam AI design aesthetics.
 */

import { store } from './state.js';
import { 
  CAREER_ROLES, 
  CITIES, 
  CANDIDATE_PRESETS, 
  SKILL_GAP_ANALYSES, 
  COMPENSATION_BENCHMARKS,
  SKILL_UNLOCKS
} from '../data/mockData.js';
import { initAICounselor } from './aiCounselor.js';

document.addEventListener('DOMContentLoaded', () => {
  initShowcaseTerminal();
  initAICounselor();
  initGlobalCitySelector();

  // Subscribe to state changes
  store.subscribe((state) => {
    updateShowcaseData(state);
  });
});

/**
 * Global Metro City Selector
 */
function initGlobalCitySelector() {
  const citySelect = document.getElementById('global-city-select');
  if (!citySelect) return;

  citySelect.addEventListener('change', (e) => {
    store.setState({ selectedCity: e.target.value });
  });
}

/**
 * Interactive Showcase Terminal Logic (Matching Reference Screenshot 1)
 */
function initShowcaseTerminal() {
  const tabButtons = document.querySelectorAll('.showcase-tab-btn');
  const optionButtons = document.querySelectorAll('.showcase-option-btn');
  const actionButton = document.getElementById('btn-showcase-action');

  // Handle Tab Switch
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.dataset.tabId;
      tabButtons.forEach(b => {
        b.classList.remove('active', 'border-[#e96c2f]', 'text-[#a5460f]');
        b.classList.add('border-transparent', 'text-stone-500');
      });
      btn.classList.add('active', 'border-[#e96c2f]', 'text-[#a5460f]');
      btn.classList.remove('border-transparent', 'text-stone-500');

      if (tabId === 'counselor') {
        document.querySelector('.btn-open-counselor')?.click();
      } else {
        updateShowcaseMode(tabId);
      }
    });
  });

  // Handle Option Clicks (Left Column)
  optionButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const roleId = btn.dataset.roleId;
      optionButtons.forEach(b => {
        b.classList.remove('active', 'bg-[#feede6]', 'text-[#a5460f]');
        b.classList.add('text-[#3d3d3d]');
      });
      btn.classList.add('active', 'bg-[#feede6]', 'text-[#a5460f]');
      btn.classList.remove('text-[#3d3d3d]');

      store.setState({ selectedRole: roleId });
    });
  });

  // Action Button in Center Stage
  actionButton?.addEventListener('click', () => {
    const bubbles = document.getElementById('showcase-bubbles-container');
    if (!bubbles) return;
    bubbles.classList.add('opacity-40');
    actionButton.textContent = 'Analyzing...';
    setTimeout(() => {
      bubbles.classList.remove('opacity-40');
      actionButton.textContent = 'Inspect Signals';
      updateShowcaseData(store.getState());
    }, 350);
  });
}

function updateShowcaseMode(tabId) {
  const centerTitle = document.getElementById('showcase-center-title');
  const centerSubtext = document.getElementById('showcase-center-subtext');
  const actionBtn = document.getElementById('btn-showcase-action');

  if (tabId === 'career') {
    if (centerTitle) centerTitle.textContent = 'Career Outlook Intelligence';
    if (centerSubtext) centerSubtext.textContent = 'Press Inspect Signals to evaluate 5-year ARIMA trajectory and AI automation risk.';
    if (actionBtn) actionBtn.textContent = 'Inspect Signals';
  } else if (tabId === 'skills') {
    if (centerTitle) centerTitle.textContent = '483-Skill DAG Diagnostics';
    if (centerSubtext) centerSubtext.textContent = 'Press Diagnose Gaps to parse competencies against production interview bars.';
    if (actionBtn) actionBtn.textContent = 'Diagnose Gaps';
  } else if (tabId === 'salary') {
    if (centerTitle) centerTitle.textContent = 'Tukey IQR Salary Calibration';
    if (centerSubtext) centerSubtext.textContent = 'Press Calibrate Compensation to view P25-P75 percentiles in ₹ LPA.';
    if (actionBtn) actionBtn.textContent = 'Calibrate CTC';
  }

  updateShowcaseData(store.getState(), tabId);
}

function updateShowcaseData(state, activeTab = 'career') {
  const role = CAREER_ROLES[state.selectedRole] || CAREER_ROLES['data-engineer'];
  const city = CITIES.find(c => c.id === state.selectedCity) || CITIES[0];
  const bench = (COMPENSATION_BENCHMARKS[state.selectedRole] && COMPENSATION_BENCHMARKS[state.selectedRole][state.selectedCity])
    ? COMPENSATION_BENCHMARKS[state.selectedRole][state.selectedCity]
    : COMPENSATION_BENCHMARKS['data-engineer']['bengaluru'];

  const bubblesContainer = document.getElementById('showcase-bubbles-container');
  if (!bubblesContainer) return;

  const unlock = (SKILL_UNLOCKS[state.selectedRole] && SKILL_UNLOCKS[state.selectedRole][0]) 
    ? SKILL_UNLOCKS[state.selectedRole][0] 
    : SKILL_UNLOCKS['data-engineer'][0];

  bubblesContainer.innerHTML = `
    <!-- Blue Bubble -->
    <div class="bubble-blue">
      <strong>${role.title} (${city.name}):</strong> 5-Year Outlook projects <strong class="font-semibold text-stone-900">+${role.growth_score}% Growth</strong>. Task AI Exposure is <strong class="text-stone-900">${role.ai_exposure_score}%</strong> (${role.ai_exposure_level}).
    </div>
    <!-- Peach Bubble -->
    <div class="bubble-peach">
      High-Impact Unlock: Mastering <strong>${unlock.skill}</strong> unlocks <strong class="text-[#a5460f]">+${unlock.additional_jobs} active job listings</strong> and an estimated <strong class="text-[#a5460f]">+₹${unlock.potential_salary_boost_lpa}L LPA</strong> median boost.
    </div>
    <!-- Green Bubble -->
    <div class="bubble-green">
      Calibrated Compensation: <strong>₹${bench.p25.toFixed(1)}L – ₹${bench.p75.toFixed(1)}L LPA</strong> in ${city.name} (Tukey Median: <strong class="text-stone-900">₹${bench.p50.toFixed(1)}L</strong>).
    </div>
  `;
}
