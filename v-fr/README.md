# VRIDDHI (वृद्धि) — Frontend Architecture & Design Foundation

AI-Powered Workforce & Career Intelligence Platform for India.

---

## 1. Overview & Tech Stack

This frontend is built strictly following the guidelines:
- **Plain HTML5** (`index.html`)
- **Modern Vanilla CSS** (`src/css/input.css`)
- **Tailwind CSS v4.x** via local CLI (`@tailwindcss/cli@4.3.3`) compiled to `dist/css/styles.css`
- **Vanilla Modern JavaScript** (ES Modules: `src/js/app.js`, `src/js/components.js`, `src/js/state.js`, `src/js/aiCounselor.js`)
- **Zero Framework Bloat:** No React, Next.js, Vue, Angular, or Svelte.
- **Clean Mock / Data Layer:** `src/data/mockData.js` strictly conforms to `outer.md` schemas for seamless transition to live APIs (`8001`, `8002`, `8003`, `/api/groq`).

---

## 2. Information Architecture & Modules

```
DISCOVER (M1) ──> DIAGNOSE (M2) ──> MATCH (M3) ──> ADVISE (Vriddhi AI)
```

### Module 1: Career Intelligence & 5-Year Outlook (Port 8001)
- **Role Search & Selector:** 4 core high-velocity tech occupations + domain query filter.
- **4 Metric Badges:** 5-Year Growth Score, Current Market Demand (0–100), Task-level AI Exposure Score, and Confidence Score.
- **10-Year Trend Visualizer (2020–2030):** Custom interactive SVG line chart mapping historical verified hiring volumes against ARIMA projected growth with hover tooltips.
- **Key Demand Drivers & Core Skill Matrix:** High-signal market drivers and technical competencies.

### Module 2: Skill Gap Diagnostics & Resume Engine (Port 8002)
- **Candidate Profile Presets:** 1-click loading for Aarav Mehta (Service-to-Product), Priya Sharma (Fresher), and Vikram Sen (Experienced Backend).
- **Resume Upload Dropzone:** Drag-and-drop file ingestion simulator with NER parsing feedback.
- **Composite Readiness Gauge:** Circular SVG gauge (0–100%) with animated stroke offset.
- **3-Column Skill Breakdown Matrix:** Matched (Green), Adjacent Quick Wins (Amber), and Critical Gatekeeper Gaps (Red).
- **Prerequisite DAG Roadmap:** Step-by-step phased curriculum with an interactive **Weekly Study Hours Slider (5 to 40 hrs/wk)** dynamically recalibrating the timeline in weeks and months.

### Module 3: Job Matching, Salary Calibrator & Negotiation (Port 8003)
- **3-Column Compensation Deck:** City Market Benchmark (P25–P75 in ₹ LPA), Calibrated Candidate Worth, and Recommended Target Ask / Walk-away Floor.
- **Percentile Visualizer:** Interactive range bar highlighting candidate valuation against metro bands.
- **High-Value Skill Unlocks ROI:** Quantified compensation uplift and extra job openings unlocked by mastering missing skills (e.g. Apache Spark, Docker, Kafka).
- **Data-Backed Negotiation Playbook:** Word-for-word counter-offer scripts and talking points with 1-click clipboard copy.
- **Ranked Live Job Feed:** Filterable by work mode (Hybrid, In-Office, Remote) with match %, matched/missing chips, and interactive job inspection modal.

### Vriddhi AI Career Counselor (/api/groq)
- **Slide-out Drawer Terminal:** Interactive conversational advisor grounded in 72,000+ Indian job postings and Tukey 1.5× IQR outlier filtering.
- **Quick-Launch Prompt Pills:** Pre-configured high-value questions (salary shift simulations, Pune vs. Bengaluru comparisons, Service-to-Product transition strategies).
- **Streaming Response Engine:** Realistic word-by-word streaming markdown renderer.

---

## 3. Project Directory Structure

```
v-fr/
├── index.html                 # Master application shell
├── package.json               # NPM scripts and Tailwind CLI dependency
├── outer.md                   # Product Source of Truth
├── README.md                  # Frontend Architecture & Documentation
├── src/
│   ├── css/
│   │   └── input.css          # Tailwind CSS v4 source with custom theme & typography
│   ├── data/
│   │   └── mockData.js        # Structured mock data layer conforming to outer.md
│   └── js/
│       ├── app.js             # Master controller and navigation orchestrator
│       ├── components.js      # Reusable SVG charts, gauges, cards & visualizers
│       ├── state.js           # Reactive state store
│       └── aiCounselor.js     # AI Counselor conversational engine
├── dist/
│   └── css/
│       └── styles.css         # Compiled, minified Tailwind v4 CSS bundle
└── demo/                      # Reference visual website (Sarvam.ai)
```

---

## 4. How to Run Locally

### Rebuilding Tailwind CSS:
```bash
# Build production minified CSS
npm run build:css

# Or watch mode for active styling changes
npm run watch:css
```

### Running the Local Web Server:
Open `index.html` in any modern web browser or serve via:
```bash
npx serve .
# or
python3 -m http.server 3000
```
Then navigate to `http://localhost:3000/`.

---

## 5. Transitioning from Mock Data to Live Backend Services

When backend services on ports `8001`, `8002`, `8003` and `/api/groq` are online, simply swap the import references in `src/js/app.js` and `src/js/aiCounselor.js` to `fetch()` calls matching the endpoints specified in `outer.md`:
- `POST http://localhost:8001/api/v1/career/analyze`
- `POST http://localhost:8002/api/v1/skills/analyze_resume`
- `POST http://localhost:8003/api/v1/jobs/search`
- `POST http://localhost:8003/api/v1/salary/negotiate`
- `POST /api/groq` (Streaming Groq Llama-3.3-70B completion)
