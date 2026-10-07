# Vriddhi (वृद्धि) — Product & Frontend Architecture Blueprint

> **Quick Reference for Building the New Frontend**  
> **Platform:** Vriddhi (वृद्धि) — AI-Powered Workforce & Career Intelligence Platform for India  
> **Mission:** Guiding 1.5M+ annual Indian graduates from college confusion to high-conviction tech careers using empirical data.

---

## 1. What is Vriddhi & Why We Are Building

### The Core Problem (The Indian Engineering Paradox)
- **1.5M+ engineers graduate each year** in India, but **only ~25% are employable** in modern tech roles (NASSCOM).
- **Curriculum Lag:** Indian universities update syllabi once every 4–5 years (teaching outdated Waterfall models, manual testing, Turbo C++), while industry tech stacks evolve every 6 months (Docker, Kubernetes, MLOps, FastAPI, RAG, PyTorch).
- **Noisy & Distorted Advice:** Students rely on unverified advice, influencer hype, or US-centric salary figures that don't reflect Indian hiring realities.
- **The Solution:** **Vriddhi** (वृद्धि = *growth, elevation, progress*) is an empirical, end-to-end career intelligence system that replaces guesswork with verified data across 4 interconnected phases:
  $$\text{Market Discovery (M1)} \longrightarrow \text{Skill Diagnostics (M2)} \longrightarrow \text{Job \& Salary Match (M3)} \longleftrightarrow \text{Agentic Counselor (Vriddhi AI)}$$

### The Indian Touch & Ecosystem Grounding
- **Currency & Compensation:** All numbers formatted in **₹ Lakhs Per Annum (LPA)**. Breaks down **Fixed Base**, **Variable / Performance Bonus**, and **ESOPs**, reflecting Indian CTC (Cost to Company) vs. In-Hand realities.
- **Outlier-Proof Modeling:** Employs **Tukey 1.5× IQR outlier filtering** on 72,000+ Indian job postings and compensation records to eliminate distorted salary claims.
- **5 Major Tech Metros:** Models city-specific demand, living costs, and multiplier factors:
  - **Bengaluru:** The Tier 1 product and hyper-scale baseline.
  - **Hyderabad:** Rapidly growing Cloud, GenAI & enterprise data hub (+17.2% YoY).
  - **Pune:** Enterprise systems, cloud infra, and automotive software hub.
  - **Delhi-NCR:** Fintech, consumer tech, and startup scale.
  - **Mumbai:** BFSI tech, digital banking, and enterprise platforms.
- **Transition Dynamics:** Explicitly supports Indian career paths like **Service-to-Product transitions** (Wipro/TCS/Infosys $\rightarrow$ product startups/MNCs), notice periods, and appraisal cycles.

---

## 2. Architecture & The 3 Modules

```
                              ┌───────────────────────────────────┐
                              │       NEW VRIDDHI FRONTEND        │
                              │      Next.js / React / Tailwind   │
                              └─┬──────────────┬───────────────┬──┘
                                │              │               │
                 Port 8001      │   Port 8002  │    Port 8003  │   Next.js API
              ┌─────────────────┘              │               └────────────────┐
              ▼                                ▼                                ▼
    ┌───────────────────┐            ┌───────────────────┐            ┌───────────────────┐
    │     MODULE 1      │            │     MODULE 2      │            │     MODULE 3      │
    │ Career Intel &    │            │ Skill Gap Engine  │            │ Job Matching &    │
    │ 5-Year Outlook    │            │ & Resume Parser   │            │ Salary Calibrator │
    └───────────────────┘            └───────────────────┘            └───────────────────┘
              ▲                                │                                │
              │                                ▼                                ▼
              └───────────────────────────────┴────────────────────────────────┴───┐
                                              ▼                                     ▼
                                   ┌─────────────────────┐               ┌────────────────────┐
                                   │  Vriddhi SQLite DB  │               │  Vriddhi AI Agent  │
                                   │  (72k+ Postings,    │               │  (Groq Llama-3.3   │
                                   │   1k+ Cached Jobs)  │               │   + Indian RAG)    │
                                   └─────────────────────┘               └────────────────────┘
```

| Module | Service | Port | Primary Question Answered | Core Tech |
|---|---|---|---|---|
| **Module 1** | Career Intelligence | `8001` | *"What career should I pursue and what is its 5-year outlook?"* | FastAPI, SQLite (72k records), ARIMA/Time-series, O*NET Taxonomy |
| **Module 2** | Skill Gap Engine | `8002` | *"What skills do I have and what exact gap separates me from my target role?"* | FastAPI, PDF/DOCX Parser, 483-Skill DAG Taxonomy, Vector Cosine |
| **Module 3** | Job & Salary Match | `8003` | *"Which real jobs can I apply for today, what am I worth, and how do I negotiate?"* | FastAPI, Adzuna/JSearch, 1056+ Prewarmed Jobs, Tukey IQR Model |
| **Counselor** | Vriddhi AI Agent | `/api/groq` | *"Can you explain my pathway, simulate salary jumps, and give strategic advice?"* | Groq Llama-3.3-70B-Versatile, System Prompt Grounding, Context Memory |

---

## 3. What We Changed in Vriddhi AI Assistant

Based on latest updates to `/api/groq`:
1. **Authoritative Professional Identity:** Vriddhi **never** refers to itself as a "hackathon project", "prototype", or "experiment". It acts as an authoritative, senior workforce intelligence advisor.
2. **Context-Aware Conversational Intelligence:** Previous versions gave repetitive canned responses when users said casual remarks like *"wow"*, *"nice"*, *"ok"*, or *"thanks"*. Now:
   - Retains full multi-turn conversation history.
   - Acknowledges brief user feedback warmly.
   - Guides the user into deeper high-value inquiries (e.g., simulating a +₹3.2L jump by adding Docker/Kubernetes).
3. **Resilient Local Fallback:** If Groq API rate limits or network issues occur, an intelligent regex/RAG fallback answers role, city salary comparison, and curriculum questions instantly.
4. **Markdown Formatting Standards:** Always bolds key metrics, technology stacks, and ₹ LPA values (`**₹18.8L LPA**`, `**Bengaluru**`, `**Docker**`).

---

## 4. What Data to Show on the Frontend (Screen-by-Screen)

### Screen 1: 5-Year Career Forecaster & Outlook Hub (Module 1)
- **Top 5-Year Trending Roles Banner:** Visual highlight of high-velocity roles (e.g., Machine Learning Engineer, Cloud Architect, Data Engineer).
- **Role Search & Selector:** Dropdown of 100+ standard O*NET occupations + free-text domain query.
- **Key Metrics Badges:**
  - **Growth Score (0–100%)** & 5-year forecast trajectory.
  - **Current Market Demand** index.
  - **Task-Level AI Exposure Score** (Low / Moderate / High automation risk).
  - **Confidence Score** based on sample volume.
- **Trend Visualizer:** Past vs. Future 5-Year hiring volume line graph (2020–2030).
- **Key Demand Drivers:** Plain-English bullet points explaining *why* demand is moving (e.g., enterprise cloud migration, vector DB adoption).
- **Core Skill Matrix:** Top technical and domain skills required for the role.

---

### Screen 2: Resume Intelligence & Skill Gap Diagnostics (Module 2)
- **Resume Upload & Profile Input:**
  - Drag-and-drop resume upload (`.pdf`, `.docx`, `.txt`) or 1-click candidate profile presets (e.g., Aarav Mehta, Priya Sharma).
  - Target role selection.
- **Diagnostic Overview:**
  - **Job Readiness Score Gauge:** 0–100% composite score.
  - Overall match summary (e.g., *"Match: 68% • 7 of 11 core competencies satisfied"*).
- **3-Column Skill Breakdown Matrix:**
  1. **Matched Skills (Green):** Verified skills present in candidate resume.
  2. **Adjacent Quick Wins (Yellow):** Skills closely related to candidate's existing background (low effort, high return).
  3. **Critical Gaps (Red):** Mandatory skills missing that block interview shortlists.
- **Prerequisite Learning Pathway (DAG Roadmap):**
  - Step-by-step phased roadmap showing which skills must be learned first before advanced ones (e.g., Python $\rightarrow$ SQL $\rightarrow$ Docker $\rightarrow$ PySpark).
  - **Dynamic Weekly Hours Slider (5 to 40 hrs/week):** Automatically recalibrates the estimated time-to-readiness in weeks/months.

---

### Screen 3: Live Job Matches, Salary Calibration & Negotiation (Module 3)
- **3-Column Compensation Intelligence Deck:**
  1. **City Market Benchmark:** 25th–75th percentile market range for the city (e.g., `₹16.0 – 22.0 LPA`).
  2. **Personalized Candidate Value:** Candidate's calibrated worth adjusted for skill match percentage and years of experience (e.g., `₹17.5 – 19.2 LPA`).
  3. **Recommended Target & Walk-away Minimum:** The aggressive target to ask for and the floor walk-away minimum (e.g., Target: `₹19.5 LPA`, Walk-away: `₹16.5 LPA`).
- **High-Value Skill Unlocks Banner:**
  - Shows direct ROI of missing skills (e.g., *"Learn Docker & Kubernetes to unlock +8 new job listings and +₹3.2L higher median offer"*).
- **Data-Backed Negotiation Playbook:**
  - Ready-to-use scripts and counter-offer talking points grounded in posted market percentiles.
- **Ranked Live Job Feed:**
  - Cards sorted by match percentage (e.g., 85% Match).
  - Company name, location, work mode (Remote / Hybrid / In-office), and posted/predicted salary.
  - Tag chips: Green for Matched skills, Amber for Missing skills.
  - Direct apply button.

---

### Screen 4: Vriddhi AI Career Counselor (Chat Terminal / Drawer)
- **Quick-Launch Prompt Pills:**
  - *"What is the expected salary shift if I add Docker to Backend?"*
  - *"Compare Data Engineer compensation between Pune and Bengaluru."*
  - *"How does my college syllabus compare to live market demand?"*
- **Streaming Multi-Turn Chat:** Full markdown with code blocks, metric highlights, and natural conversation.
- **Live Grounding Badges:** Display active intelligence sources: `72k+ Naukri Records`, `Tukey 1.5× IQR`, `Groq Llama-3.3-70B`.

---

## 5. Complete API Reference for Frontend

### Module 1: Career Intelligence (Port `8001`)

#### 1. Analyze Career Outlook
- **Endpoint:** `POST http://localhost:8001/api/v1/career/analyze`
- **Request Body:**
  ```json
  {
    "occupation": "Data Engineer",
    "region": "India"
  }
  ```
- **Response Shape:**
  ```json
  {
    "occupation": "Data Engineer",
    "outlook": "Strong Growth",
    "growth_score": 0.88,
    "current_demand_score": 0.85,
    "ai_exposure_score": 0.38,
    "confidence_score": 0.91,
    "historical_trend": [
      {"year": 2020, "postings": 12400},
      {"year": 2024, "postings": 28600}
    ],
    "forecast": [
      {"year": 2025, "projected_postings": 32100},
      {"year": 2029, "projected_postings": 45800}
    ],
    "top_skills": ["python", "sql", "spark", "docker", "aws"],
    "key_drivers": [
      "Rapid enterprise migration to distributed cloud data lakes",
      "Surge in LLM pipeline engineering and vector database integration"
    ]
  }
  ```

#### 2. Search Careers by Domain / Keywords
- **Endpoint:** `POST http://localhost:8001/api/v1/career/search_by_domain`
- **Request Body:**
  ```json
  {
    "domain_query": "Artificial Intelligence",
    "top_k": 5
  }
  ```

#### 3. Rank Multiple Careers
- **Endpoint:** `POST http://localhost:8001/api/v1/career/rank`
- **Request Body:**
  ```json
  {
    "occupations": ["Data Engineer", "Frontend Developer", "DevOps Engineer"],
    "weights": { "growth": 0.4, "demand": 0.3, "ai_safety": 0.3 }
  }
  ```

#### 4. List All Available Occupations
- **Endpoint:** `GET http://localhost:8001/api/v1/career/occupations?limit=100`

---

### Module 2: Skill Gap Engine (Port `8002`)

#### 1. Health Check
- **Endpoint:** `GET http://localhost:8002/api/v1/health`

#### 2. Analyze Resume (File Upload + Diagnostics)
- **Endpoint:** `POST http://localhost:8002/api/v1/skills/analyze_resume`
- **Content-Type:** `multipart/form-data`
- **Form Data Fields:**
  - `file`: Resume file (`.pdf`, `.docx`, or `.txt`, max 5MB).
  - `target_role`: Target occupation title (e.g., `"Data Engineer"`).
  - `required_skills`: Comma-separated list of required skills (e.g., `"python,sql,docker,aws,spark"`).
  - `location`: Optional candidate city (e.g., `"Bengaluru"`).
  - `use_llm`: Boolean (`true` for Groq LLM NER fallback).
- **Response Shape:**
  ```json
  {
    "profile": {
      "user_id": "usr_9f82...",
      "skills": [
        {"name": "python", "level": 3, "evidence": ["Built ETL pipelines in Python"]},
        {"name": "sql", "level": 3, "evidence": ["Optimized PostgreSQL queries"]}
      ],
      "experience_years": 3.0,
      "education": ["B.Tech in Computer Science"],
      "location": "Bengaluru",
      "target_occupation": "Data Engineer"
    },
    "gap_analysis": {
      "readiness_score": 68,
      "matched_skills": [
        {"id": "python", "name": "Python", "confidence": 0.95},
        {"id": "sql", "name": "SQL", "confidence": 0.92}
      ],
      "adjacent_skills": [
        {"id": "docker", "name": "Docker", "reason": "Basic container knowledge detected"}
      ],
      "missing_skills": [
        {"id": "spark", "name": "Apache Spark", "importance": "high"},
        {"id": "aws", "name": "AWS Cloud", "importance": "high"}
      ],
      "learning_roadmap": [
        {"phase": 1, "skill": "Docker", "est_hours": 15},
        {"phase": 2, "skill": "Apache Spark", "est_hours": 30, "prerequisites": ["python", "sql"]}
      ]
    }
  }
  ```

#### 3. Direct Gap Analysis (Without File Upload)
- **Endpoint:** `POST http://localhost:8002/api/v1/skills/gap_analysis`
- **Request Body:**
  ```json
  {
    "target_role": "Data Engineer",
    "required_skills": ["python", "sql", "spark", "docker", "aws"],
    "profile": {
      "skills": [{"name": "python", "level": 3}, {"name": "sql", "level": 2}],
      "experience_years": 2.5,
      "location": "Bengaluru"
    }
  }
  ```

---

### Module 3: Job Matching & Salary Intelligence (Port `8003`)

#### 1. Health Check & Cache Stats
- **Endpoint:** `GET http://localhost:8003/api/v1/health`
- **Response:**
  ```json
  {
    "status": "ok",
    "module": "module-3-job-matching-salary",
    "cache": { "total_jobs": 1056, "unique_keys": 50 }
  }
  ```

#### 2. Search & Match Ranked Jobs
- **Endpoint:** `POST http://localhost:8003/api/v1/jobs/search`
- **Request Body:**
  ```json
  {
    "target_role": "Data Engineer",
    "city": "Bengaluru",
    "candidate": {
      "skills": ["python", "sql", "docker", "aws"],
      "experience_years": 3.0
    },
    "limit": 15
  }
  ```
- **Response Shape:**
  ```json
  {
    "target_role": "Data Engineer",
    "location": "Bengaluru",
    "market_salary": {
      "p25": 14.5,
      "p50": 18.0,
      "p75": 22.5,
      "sample_count": 28
    },
    "candidate_value": {
      "estimated_min": 17.2,
      "estimated_max": 19.5,
      "confidence": "high"
    },
    "skill_unlocks": [
      {"skill": "spark", "additional_jobs": 6, "potential_salary_boost_lpa": 2.8},
      {"skill": "kubernetes", "additional_jobs": 4, "potential_salary_boost_lpa": 2.2}
    ],
    "jobs": [
      {
        "job_id": "job_bgl_882",
        "title": "Software Engineer - Data Systems",
        "company": "Sunquest Information Systems",
        "city": "Bengaluru",
        "work_mode": "Hybrid",
        "salary_min": 16.0,
        "salary_max": 20.0,
        "salary_is_predicted": false,
        "match_score": 78,
        "matched_skills": ["python", "sql", "aws"],
        "missing_skills": ["spark"]
      }
    ]
  }
  ```

#### 3. Estimate Compensation Benchmark
- **Endpoint:** `POST http://localhost:8003/api/v1/salary/estimate`
- **Request Body:** Same shape as search request without `limit`.

#### 4. Generate Negotiation Playbook
- **Endpoint:** `POST http://localhost:8003/api/v1/salary/negotiate`
- **Request Body:**
  ```json
  {
    "target_role": "Data Engineer",
    "city": "Bengaluru",
    "candidate": {
      "skills": ["python", "sql", "docker", "aws"],
      "experience_years": 3.0
    },
    "job_id": "job_bgl_882",
    "posted_salary_min": 15.0,
    "posted_salary_max": 18.0
  }
  ```
- **Response Shape:**
  ```json
  {
    "negotiation": {
      "recommended_ask_lpa": 19.0,
      "walk_away_floor_lpa": 16.5,
      "talking_points": [
        "Your skill alignment (78%) sits in the top quartile of applicants for this role in Bengaluru.",
        "Market 50th percentile for 3 years experience is ₹18.0L LPA; cite current multi-cloud and data pipeline demand.",
        "Highlight your verified containerization and AWS experience to counter lower initial fixed bands."
      ]
    }
  }
  ```

---

### Frontend AI Assistant Route: Vriddhi AI (`/api/groq`)

- **Endpoint:** `POST /api/groq` (Internal Next.js Route)
- **Request Body:**
  ```json
  {
    "messages": [
      {"role": "user", "content": "I know Python and SQL. How much more can I earn if I learn Docker?"}
    ]
  }
  ```
- **Response Shape:**
  ```json
  {
    "success": true,
    "reply": "Based on **14,200+ verified Indian listings**, adding **Docker** and containerization yields an estimated **+₹2.8L to +₹3.5L LPA** compensation uplift in **Bengaluru**.\n\nKey Market Insights:\n• Cloud containerization is demanded in **71%** of high-paying backend roles.\n• Boosts interview shortlist velocity by **1.35×**."
  }
  ```

---

## 6. End-to-End User Flow (Integration Pipeline)

```
[1. User lands on Forecaster (M1)]
         │
         ▼
[Selects Target Role: "Data Engineer" in "Bengaluru"]
  • Fetches: 5-yr demand forecast, AI exposure score, core skills
         │
         ▼
[2. Moves to Skill Gap Lab (M2)]
  • Uploads Resume or picks Candidate Preset
  • M2 parses resume, runs LLM NER, maps to 483-skill DAG
  • Outputs: Readiness Score (68%), 3-Bucket Matrix, Prerequisite Learning Path
         │
         ▼
[3. Passes Profile to Job & Salary Calibrator (M3)]
  • M3 matches candidate skills against 1,056 cached Indian tech jobs
  • Outputs:
    - City Range: ₹14.5L – 22.5L LPA
    - Candidate Worth: ₹17.2L – 19.5L LPA
    - Skill Unlocks: +6 jobs with Apache Spark
    - Ranked Job Cards with match percentages & direct apply links
         │
         ▼
[4. Engages Vriddhi AI Counselor]
  • User asks counterfactual questions or requests negotiation scripts
  • Vriddhi AI answers with real Indian context & grounded metrics
```

---

## 7. Development Quick-Start

To run all 3 backend services and the frontend simultaneously:

```bash
# Terminal 1: Module 1 (Career Intelligence)
cd vriddhi/module-1-career-intelligence
source ../venv/bin/activate
uvicorn src.api.main:app --port 8001 --reload

# Terminal 2: Module 2 (Skill Gap Engine)
cd vriddhi/module-2-skill-gap
source ../venv/bin/activate
HF_HUB_OFFLINE=1 uvicorn src.api.main:app --port 8002 --reload

# Terminal 3: Module 3 (Job Matching & Salary)
cd vriddhi/module-3-job-matching-salary
source ../venv/bin/activate
uvicorn src.api.main:app --port 8003 --reload

# Terminal 4: Next.js Frontend
cd fr
npm run dev
```
