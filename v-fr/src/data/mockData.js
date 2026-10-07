/**
 * VRIDDHI (वृद्धि) — Product Mock Data Layer
 * Conforming strictly to outer.md API specifications & Indian Tech Ecosystem.
 * 
 * Supports:
 * - Module 1: Career Outlook & 5-Year Forecast (Port 8001 schema)
 * - Module 2: Skill Gap Diagnostics & DAG Pathway (Port 8002 schema)
 * - Module 3: Job Matching, Salary Calibrator & Negotiation (Port 8003 schema)
 * - Vriddhi AI Counselor Knowledge Retrieval (/api/groq schema)
 */

export const CITIES = [
  { id: 'bengaluru', name: 'Bengaluru', tag: 'Tier 1 Product Baseline', multiplier: 1.0, activeListings: 28400 },
  { id: 'hyderabad', name: 'Hyderabad', tag: 'Cloud & GenAI Hub (+17.2% YoY)', multiplier: 0.94, activeListings: 16200 },
  { id: 'pune', name: 'Pune', tag: 'Enterprise Systems & Auto Tech', multiplier: 0.88, activeListings: 11800 },
  { id: 'delhi-ncr', name: 'Delhi-NCR', tag: 'Fintech & Consumer Tech', multiplier: 0.92, activeListings: 14500 },
  { id: 'mumbai', name: 'Mumbai', tag: 'BFSI & Digital Banking', multiplier: 0.95, activeListings: 13100 }
];

export const CAREER_ROLES = {
  'data-engineer': {
    id: 'data-engineer',
    title: 'Data Engineer',
    category: 'Data & Infrastructure',
    outlook: 'Strong Growth',
    growth_score: 88,
    current_demand_score: 85,
    ai_exposure_score: 38, // 38% - Low / Shielded
    ai_exposure_level: 'Low / Task-Shielded',
    confidence_score: 91,
    sample_volume: '14,200+ Indian Postings',
    baseline_salary: { min: 14.5, p50: 18.0, max: 22.5 }, // LPA in Bengaluru
    historical_trend: [
      { year: 2020, postings: 12400 },
      { year: 2021, postings: 16800 },
      { year: 2022, postings: 21500 },
      { year: 2023, postings: 24200 },
      { year: 2024, postings: 28600 }
    ],
    forecast: [
      { year: 2025, projected: 32100 },
      { year: 2026, projected: 35800 },
      { year: 2027, projected: 39400 },
      { year: 2028, projected: 42900 },
      { year: 2029, projected: 45800 },
      { year: 2030, projected: 48500 }
    ],
    key_drivers: [
      'Rapid enterprise migration to distributed cloud data lakes and real-time streaming architectures',
      'Surge in GenAI & LLM pipeline engineering requiring high-throughput vector database integration',
      'BFSI and Fintech regulatory mandates for clean, auditable Indian data governance pipelines'
    ],
    top_skills: [
      { name: 'Python', importance: 'Critical', weight: 95 },
      { name: 'SQL & Query Optimization', importance: 'Critical', weight: 92 },
      { name: 'Apache Spark / PySpark', importance: 'High', weight: 88 },
      { name: 'Docker & Kubernetes', importance: 'High', weight: 82 },
      { name: 'AWS / Cloud Infra', importance: 'High', weight: 80 },
      { name: 'Kafka Streaming', importance: 'Moderate', weight: 75 }
    ]
  },
  'mlops-engineer': {
    id: 'mlops-engineer',
    title: 'MLOps & AI Platform Engineer',
    category: 'AI & Machine Learning',
    outlook: 'Exceptional Surge',
    growth_score: 94,
    current_demand_score: 89,
    ai_exposure_score: 29,
    ai_exposure_level: 'Very Low / Architecture-Centric',
    confidence_score: 93,
    sample_volume: '9,800+ Indian Postings',
    baseline_salary: { min: 18.0, p50: 24.5, max: 32.0 },
    historical_trend: [
      { year: 2020, postings: 3200 },
      { year: 2021, postings: 5600 },
      { year: 2022, postings: 9400 },
      { year: 2023, postings: 14100 },
      { year: 2024, postings: 21800 }
    ],
    forecast: [
      { year: 2025, projected: 27500 },
      { year: 2026, projected: 34200 },
      { year: 2027, projected: 41000 },
      { year: 2028, projected: 47800 },
      { year: 2029, projected: 53900 },
      { year: 2030, projected: 59200 }
    ],
    key_drivers: [
      'Production deployment of proprietary LLMs and SLMs across Indian enterprises',
      'GPU cluster resource orchestration, vLLM inference optimization and latency SLA management',
      'Model registry, continuous fine-tuning pipelines and automated RAG evaluation frameworks'
    ],
    top_skills: [
      { name: 'Python / PyTorch', importance: 'Critical', weight: 96 },
      { name: 'Kubernetes & Kubeflow', importance: 'Critical', weight: 94 },
      { name: 'Docker Containerization', importance: 'Critical', weight: 92 },
      { name: 'FastAPI & Triton Server', importance: 'High', weight: 86 },
      { name: 'MLflow & DVC', importance: 'High', weight: 84 },
      { name: 'CI/CD for Model Registry', importance: 'High', weight: 80 }
    ]
  },
  'cloud-architect': {
    id: 'cloud-architect',
    title: 'Cloud Systems Architect',
    category: 'Infrastructure & DevOps',
    outlook: 'Steady Expansion',
    growth_score: 82,
    current_demand_score: 88,
    ai_exposure_score: 34,
    ai_exposure_level: 'Low / Systems Strategy',
    confidence_score: 89,
    sample_volume: '16,500+ Indian Postings',
    baseline_salary: { min: 22.0, p50: 28.5, max: 38.0 },
    historical_trend: [
      { year: 2020, postings: 14200 },
      { year: 2021, postings: 18900 },
      { year: 2022, postings: 23400 },
      { year: 2023, postings: 26100 },
      { year: 2024, postings: 29800 }
    ],
    forecast: [
      { year: 2025, projected: 33400 },
      { year: 2026, projected: 36900 },
      { year: 2027, projected: 40200 },
      { year: 2028, projected: 43500 },
      { year: 2029, projected: 46200 },
      { year: 2030, projected: 48900 }
    ],
    key_drivers: [
      'Hybrid and multi-cloud resilience mandates from RBI and SEBI for financial enterprises',
      'FinOps cost containment post-hypergrowth cloud spending sprees',
      'Zero-trust security mesh architecture and compliance hardening'
    ],
    top_skills: [
      { name: 'AWS / GCP / Azure Architecture', importance: 'Critical', weight: 98 },
      { name: 'Terraform / IaC', importance: 'Critical', weight: 92 },
      { name: 'Kubernetes Cluster Hardening', importance: 'High', weight: 89 },
      { name: 'System Security & IAM', importance: 'High', weight: 85 },
      { name: 'Cost Optimization (FinOps)', importance: 'Moderate', weight: 78 }
    ]
  },
  'backend-platform': {
    id: 'backend-platform',
    title: 'Backend Platform Engineer',
    category: 'Software Engineering',
    outlook: 'High Demand',
    growth_score: 84,
    current_demand_score: 91,
    ai_exposure_score: 42,
    ai_exposure_level: 'Moderate / Logic & API',
    confidence_score: 94,
    sample_volume: '31,000+ Indian Postings',
    baseline_salary: { min: 12.0, p50: 16.5, max: 24.0 },
    historical_trend: [
      { year: 2020, postings: 24000 },
      { year: 2021, postings: 31000 },
      { year: 2022, postings: 37500 },
      { year: 2023, postings: 39800 },
      { year: 2024, postings: 43200 }
    ],
    forecast: [
      { year: 2025, projected: 46800 },
      { year: 2026, projected: 50400 },
      { year: 2027, projected: 54100 },
      { year: 2028, projected: 57600 },
      { year: 2029, projected: 61000 },
      { year: 2030, projected: 63800 }
    ],
    key_drivers: [
      'High-concurrency payment switches and ONDC integration microservices',
      'Evolution from monolithic codebases to distributed event-driven systems',
      'API gateway throughput and sub-millisecond p99 latency optimization'
    ],
    top_skills: [
      { name: 'Go / Java / Python Backend', importance: 'Critical', weight: 95 },
      { name: 'PostgreSQL / Distributed DBs', importance: 'Critical', weight: 90 },
      { name: 'Redis Caching & PubSub', importance: 'High', weight: 86 },
      { name: 'System Design & High Concurrency', importance: 'High', weight: 84 },
      { name: 'Kafka & Event Messaging', importance: 'High', weight: 82 }
    ]
  }
};

export const CANDIDATE_PRESETS = [
  {
    id: 'aarav-mehta',
    name: 'Aarav Mehta',
    role: 'Service-to-Product Transitioner',
    currentTitle: 'Systems Engineer at Infosys',
    experience_years: 2.8,
    education: 'B.Tech in Computer Science (Tier-3 College)',
    location: 'Bengaluru',
    target_role: 'Data Engineer',
    summary: 'Strong relational SQL & core Python scripting in service accounts; aiming to transition to product scale data engineering.',
    current_ctc: 5.4,
    skills: [
      { name: 'Python', level: 3, evidence: 'ETL script automation in client enterprise project' },
      { name: 'SQL', level: 3, evidence: 'Complex joins, indexing, and view creation on Oracle DB' },
      { name: 'Git & Version Control', level: 3, evidence: 'Standard branch workflows and pull requests' },
      { name: 'Linux Basics', level: 2, evidence: 'Cron jobs, shell scripting, log inspection' }
    ]
  },
  {
    id: 'priya-sharma',
    name: 'Priya Sharma',
    role: 'Fresher / Campus Graduate',
    currentTitle: 'Final Year B.Tech Student',
    experience_years: 0.5,
    education: 'B.E. Information Technology (Pune University)',
    location: 'Pune',
    target_role: 'Backend Platform Engineer',
    summary: 'Built academic microservices project in Node.js and basic Go; looking for high-learning product team.',
    current_ctc: 3.6,
    skills: [
      { name: 'JavaScript / Node.js', level: 3, evidence: 'REST APIs for campus management capstone' },
      { name: 'PostgreSQL', level: 2, evidence: 'Relational schema design and basic indexing' },
      { name: 'HTML & CSS', level: 3, evidence: 'Responsive frontend development' },
      { name: 'Git', level: 2, evidence: 'GitHub portfolio repositories' }
    ]
  },
  {
    id: 'vikram-sen',
    name: 'Vikram Sen',
    role: 'Experienced Backend Engineer',
    currentTitle: 'Senior Software Engineer at Swiggy Partner Ops',
    experience_years: 4.2,
    education: 'B.Tech Computer Science (Tier-1 NIT)',
    location: 'Bengaluru',
    target_role: 'MLOps & AI Platform Engineer',
    summary: 'Deep expertise in Kubernetes, Docker, and distributed APIs; upskilling to orchestrate model inference clusters.',
    current_ctc: 16.5,
    skills: [
      { name: 'Docker & Kubernetes', level: 4, evidence: 'Production cluster management with Helm' },
      { name: 'Python', level: 4, evidence: 'Asyncio microservices, FastAPI gateways' },
      { name: 'AWS Cloud', level: 3, evidence: 'EC2, S3, RDS, IAM policy design' },
      { name: 'CI/CD Pipelines', level: 4, evidence: 'GitHub Actions, automated canary deployments' }
    ]
  }
];

export const SKILL_GAP_ANALYSES = {
  'aarav-mehta_data-engineer': {
    target_role: 'Data Engineer',
    readiness_score: 68,
    match_percentage: 68,
    competencies_met: '7 of 11 core competencies satisfied',
    matched_skills: [
      { id: 'python', name: 'Python Core', confidence: 95, evidence: 'ETL scripting & pandas' },
      { id: 'sql', name: 'Relational SQL', confidence: 92, evidence: 'Subqueries, window functions, indexing' },
      { id: 'git', name: 'Git & Branching', confidence: 88, evidence: 'Standard collaborative workflow' },
      { id: 'linux', name: 'Linux Shell', confidence: 78, evidence: 'Bash scripting & process management' }
    ],
    adjacent_skills: [
      { id: 'docker', name: 'Docker Containerization', reason: 'Basic VM knowledge makes Docker a 10-day quick win', est_days: 10, roi: '+18% Interview Call Rate' },
      { id: 'airflow', name: 'Apache Airflow DAGs', reason: 'Logical extension of existing cron job pipelines', est_days: 14, roi: '+14% Recruiter Shortlist' }
    ],
    missing_skills: [
      { id: 'spark', name: 'Apache Spark / PySpark', importance: 'Critical Gatekeeper', reason: 'Mandatory in 84% of mid-level Indian product postings', unlock_jobs: 6 },
      { id: 'aws-s3-athena', name: 'AWS Data Lake (S3/Glue/Athena)', importance: 'Critical Gatekeeper', reason: 'Cloud data pipeline foundational requirement', unlock_jobs: 5 }
    ],
    learning_roadmap: [
      {
        phase: 1,
        title: 'Phase 1: Containerization & Cloud Storage',
        skill: 'Docker & AWS S3 Basics',
        est_hours: 18,
        status: 'next_up',
        prerequisites: ['Linux Shell', 'Python'],
        description: 'Package ETL jobs into Docker containers and configure IAM credentials with AWS S3.'
      },
      {
        phase: 2,
        title: 'Phase 2: Distributed Processing Engine',
        skill: 'Apache Spark & PySpark',
        est_hours: 32,
        status: 'locked',
        prerequisites: ['Python', 'SQL', 'Docker'],
        description: 'Understand RDDs, DataFrames, partitioning, shuffle operations, and memory optimization.'
      },
      {
        phase: 3,
        title: 'Phase 3: Workflow Orchestration & Data Lakehouse',
        skill: 'Airflow + Delta Lake',
        est_hours: 24,
        status: 'locked',
        prerequisites: ['Apache Spark', 'Docker'],
        description: 'Build automated end-to-end DAGs with alerting, retries, and parquet lakehouse tables.'
      }
    ]
  },
  'priya-sharma_backend-platform': {
    target_role: 'Backend Platform Engineer',
    readiness_score: 54,
    match_percentage: 54,
    competencies_met: '5 of 10 core competencies satisfied',
    matched_skills: [
      { id: 'js-node', name: 'Node.js & Express', confidence: 88, evidence: 'REST endpoints & middleware' },
      { id: 'postgresql', name: 'PostgreSQL Basics', confidence: 75, evidence: 'CRUD schemas & foreign keys' },
      { id: 'git', name: 'Git / GitHub', confidence: 82, evidence: 'Public repo commits' }
    ],
    adjacent_skills: [
      { id: 'redis', name: 'Redis Caching', reason: 'Direct cache layer on top of Node.js endpoints', est_days: 7, roi: '+22% System Design Score' },
      { id: 'docker', name: 'Docker Dev Setup', reason: 'Packaging local express servers', est_days: 8, roi: '+15% Shortlist Rate' }
    ],
    missing_skills: [
      { id: 'concurrency', name: 'System Design & High Concurrency', importance: 'Critical Gatekeeper', reason: 'Expected in all Tier 1 product interviews', unlock_jobs: 8 },
      { id: 'kafka', name: 'Kafka / Event-Driven Queues', importance: 'Critical Gatekeeper', reason: 'Required for asynchronous decoupled architectures', unlock_jobs: 6 }
    ],
    learning_roadmap: [
      {
        phase: 1,
        title: 'Phase 1: In-Memory Caching & Indexing',
        skill: 'Redis & DB Index Optimization',
        est_hours: 15,
        status: 'next_up',
        prerequisites: ['PostgreSQL'],
        description: 'Implement cache invalidation, rate limiting, and write-through patterns.'
      },
      {
        phase: 2,
        title: 'Phase 2: Asynchronous Event Queuing',
        skill: 'Kafka Message Bus & Worker Nodes',
        est_hours: 28,
        status: 'locked',
        prerequisites: ['Node.js', 'Redis'],
        description: 'Decouple long-running tasks into consumer-producer event queues with retries.'
      },
      {
        phase: 3,
        title: 'Phase 3: High Scale Architecture',
        skill: 'Distributed System Design Patterns',
        est_hours: 30,
        status: 'locked',
        prerequisites: ['Kafka', 'Docker'],
        description: 'Load balancing, database sharding, CAP theorem trade-offs, and idempotency.'
      }
    ]
  },
  'vikram-sen_mlops-engineer': {
    target_role: 'MLOps & AI Platform Engineer',
    readiness_score: 79,
    match_percentage: 79,
    competencies_met: '8 of 10 core competencies satisfied',
    matched_skills: [
      { id: 'docker-k8s', name: 'Docker & Kubernetes', confidence: 96, evidence: 'Production Helm charts & ingress' },
      { id: 'python', name: 'Python Asyncio', confidence: 94, evidence: 'High-throughput microservices' },
      { id: 'aws', name: 'AWS Cloud Services', confidence: 90, evidence: 'VPC, EC2, IAM, S3' },
      { id: 'cicd', name: 'CI/CD Automation', confidence: 92, evidence: 'GitHub Actions & ArgoCD' }
    ],
    adjacent_skills: [
      { id: 'fastapi-triton', name: 'FastAPI & Triton Inference Server', reason: 'Natural shift from web APIs to model serving endpoints', est_days: 7, roi: '+20% AI Platform Matching' },
      { id: 'mlflow', name: 'MLflow Tracking & Registry', reason: 'Applies existing artifact storage concepts to weights & metrics', est_days: 9, roi: '+15% MLOps Call Velocity' }
    ],
    missing_skills: [
      { id: 'vllm-gpu', name: 'vLLM & GPU Memory Optimization', importance: 'Critical Gatekeeper', reason: 'Mandatory for high-margin LLM serving clusters', unlock_jobs: 5 },
      { id: 'rag-vector', name: 'Distributed Vector Databases (Milvus/Qdrant)', importance: 'High Impact', reason: 'Needed for enterprise retrieval at scale', unlock_jobs: 4 }
    ],
    learning_roadmap: [
      {
        phase: 1,
        title: 'Phase 1: Model Serving Architecture',
        skill: 'Triton Server & vLLM Engine',
        est_hours: 20,
        status: 'next_up',
        prerequisites: ['Docker', 'Python'],
        description: 'Setup continuous batching, PagedAttention, and quantization (AWQ/GPTQ) for open-source models.'
      },
      {
        phase: 2,
        title: 'Phase 2: Model Registry & Drift Monitoring',
        skill: 'MLflow & Evidently AI',
        est_hours: 18,
        status: 'locked',
        prerequisites: ['Triton Server'],
        description: 'Deploy automated lineage tracking, model cards, and distribution drift alerts in production.'
      }
    ]
  }
};

export const COMPENSATION_BENCHMARKS = {
  'data-engineer': {
    bengaluru: { p25: 14.5, p50: 18.0, p75: 22.5, sampleCount: 28, outlierFiltered: 142 },
    hyderabad: { p25: 13.5, p50: 16.8, p75: 21.0, sampleCount: 22, outlierFiltered: 110 },
    pune: { p25: 12.2, p50: 15.5, p75: 19.5, sampleCount: 18, outlierFiltered: 88 },
    'delhi-ncr': { p25: 13.0, p50: 16.5, p75: 20.8, sampleCount: 24, outlierFiltered: 96 },
    mumbai: { p25: 13.8, p50: 17.2, p75: 21.8, sampleCount: 20, outlierFiltered: 104 }
  },
  'mlops-engineer': {
    bengaluru: { p25: 18.0, p50: 24.5, p75: 32.0, sampleCount: 25, outlierFiltered: 95 },
    hyderabad: { p25: 17.0, p50: 23.0, p75: 29.5, sampleCount: 19, outlierFiltered: 72 },
    pune: { p25: 15.5, p50: 21.2, p75: 27.5, sampleCount: 14, outlierFiltered: 58 },
    'delhi-ncr': { p25: 16.5, p50: 22.8, p75: 29.0, sampleCount: 17, outlierFiltered: 65 },
    mumbai: { p25: 17.5, p50: 23.5, p75: 30.5, sampleCount: 16, outlierFiltered: 61 }
  },
  'cloud-architect': {
    bengaluru: { p25: 22.0, p50: 28.5, p75: 38.0, sampleCount: 31, outlierFiltered: 120 },
    hyderabad: { p25: 20.5, p50: 26.5, p75: 35.0, sampleCount: 24, outlierFiltered: 94 },
    pune: { p25: 19.0, p50: 24.8, p75: 33.0, sampleCount: 21, outlierFiltered: 82 },
    'delhi-ncr': { p25: 20.0, p50: 26.0, p75: 34.5, sampleCount: 23, outlierFiltered: 90 },
    mumbai: { p25: 21.0, p50: 27.5, p75: 36.5, sampleCount: 22, outlierFiltered: 86 }
  },
  'backend-platform': {
    bengaluru: { p25: 12.0, p50: 16.5, p75: 24.0, sampleCount: 42, outlierFiltered: 180 },
    hyderabad: { p25: 11.2, p50: 15.2, p75: 22.0, sampleCount: 30, outlierFiltered: 140 },
    pune: { p25: 10.5, p50: 14.0, p75: 20.5, sampleCount: 26, outlierFiltered: 112 },
    'delhi-ncr': { p25: 11.5, p50: 15.5, p75: 22.8, sampleCount: 32, outlierFiltered: 135 },
    mumbai: { p25: 11.8, p50: 16.0, p75: 23.2, sampleCount: 28, outlierFiltered: 124 }
  }
};

export const SKILL_UNLOCKS = {
  'data-engineer': [
    {
      skill: 'Apache Spark / PySpark',
      additional_jobs: 6,
      potential_salary_boost_lpa: 2.8,
      demand_percentage: '84% of product companies',
      difficulty: 'Moderate (3-4 weeks)',
      rationale: 'Moves candidate from junior scripting to distributed big data pipelines capable of multi-terabyte processing.'
    },
    {
      skill: 'Docker & Kubernetes Infra',
      additional_jobs: 4,
      potential_salary_boost_lpa: 2.2,
      demand_percentage: '71% of high-paying postings',
      difficulty: 'Easy (10-14 days)',
      rationale: 'Signals immediate day-1 deployment autonomy without requiring DevOps handover.'
    },
    {
      skill: 'Kafka Real-Time Streaming',
      additional_jobs: 3,
      potential_salary_boost_lpa: 1.9,
      demand_percentage: '58% of fintech & e-commerce roles',
      difficulty: 'Moderate (2 weeks)',
      rationale: 'Unlocks low-latency event ingestion architectures critical for payment and order tracking pipelines.'
    }
  ],
  'mlops-engineer': [
    {
      skill: 'vLLM & TensorRT Inference',
      additional_jobs: 5,
      potential_salary_boost_lpa: 3.8,
      demand_percentage: '89% of GenAI platform teams',
      difficulty: 'Moderate (2 weeks)',
      rationale: 'Directly impacts company GPU cloud costs by 40-60%, making it the highest ROI engineering skill in 2025.'
    },
    {
      skill: 'Kubeflow & Pipeline Orchestration',
      additional_jobs: 4,
      potential_salary_boost_lpa: 2.6,
      demand_percentage: '67% of enterprise AI teams',
      difficulty: 'Moderate (3 weeks)',
      rationale: 'Automates model training DAGs on top of Kubernetes clusters.'
    }
  ],
  'backend-platform': [
    {
      skill: 'Kafka & Distributed Event Queues',
      additional_jobs: 7,
      potential_salary_boost_lpa: 2.5,
      demand_percentage: '74% of high-scale startups',
      difficulty: 'Moderate (2-3 weeks)',
      rationale: 'Transforms monolithic synchronous APIs into high-throughput asynchronous services.'
    },
    {
      skill: 'Redis Caching & Concurrency Design',
      additional_jobs: 5,
      potential_salary_boost_lpa: 1.8,
      demand_percentage: '81% of mid-to-senior product jobs',
      difficulty: 'Quick Win (10 days)',
      rationale: 'Solves database bottleneck and race condition questions in technical design rounds.'
    }
  ]
};

export const MATCHED_JOBS = [
  {
    job_id: 'job_bgl_882',
    title: 'Software Engineer - Data Systems',
    company: 'Sunquest Information Systems',
    city: 'Bengaluru',
    area: 'Outer Ring Road, Bellandur',
    work_mode: 'Hybrid',
    work_mode_detail: '2 days office / 3 days remote',
    salary_min: 16.0,
    salary_max: 20.0,
    salary_is_predicted: false,
    match_score: 78,
    matched_skills: ['Python', 'SQL', 'AWS'],
    missing_skills: ['Apache Spark'],
    experience_req: '2 - 4 YOE',
    posted_ago: '3 days ago',
    applicants_count: 42,
    urgency: 'Active Hiring',
    apply_url: 'https://careers.sunquest.com/jobs/882',
    description: 'Looking for a data systems engineer to maintain high-throughput clinical data lake pipelines. Must have strong Python, relational SQL tuning, and AWS experience.'
  },
  {
    job_id: 'job_bgl_914',
    title: 'Data Platform Engineer',
    company: 'Razorpay',
    city: 'Bengaluru',
    area: 'Koramangala',
    work_mode: 'In-office',
    work_mode_detail: '5 days in-office',
    salary_min: 18.5,
    salary_max: 23.0,
    salary_is_predicted: false,
    match_score: 85,
    matched_skills: ['Python', 'SQL', 'Git', 'Linux'],
    missing_skills: ['Kafka', 'PySpark'],
    experience_req: '2 - 5 YOE',
    posted_ago: '1 day ago',
    applicants_count: 89,
    urgency: 'High Priority',
    apply_url: 'https://razorpay.com/jobs/platform-eng',
    description: 'Join the Core Banking Data Platform. Build resilient reconciliation pipelines handling ₹15,000+ Cr monthly transaction telemetry.'
  },
  {
    job_id: 'job_hyd_403',
    title: 'Associate Cloud Data Engineer',
    company: 'FactSet Systems',
    city: 'Hyderabad',
    area: 'HITEC City',
    work_mode: 'Hybrid',
    work_mode_detail: 'Flexible 2 days office',
    salary_min: 14.0,
    salary_max: 18.0,
    salary_is_predicted: false,
    match_score: 82,
    matched_skills: ['Python', 'SQL', 'Linux Shell'],
    missing_skills: ['Airflow'],
    experience_req: '1 - 3 YOE',
    posted_ago: '5 days ago',
    applicants_count: 36,
    urgency: 'Immediate Joining',
    apply_url: 'https://factset.com/careers/hyd-403',
    description: 'Financial telemetry processing for global equity analytics. Strong SQL aggregation and automated Python batch processing required.'
  },
  {
    job_id: 'job_pun_719',
    title: 'Data Infrastructure Developer',
    company: 'Nice Systems',
    city: 'Pune',
    area: 'Kalyani Nagar',
    work_mode: 'Remote',
    work_mode_detail: '100% Work from Anywhere in India',
    salary_min: 15.0,
    salary_max: 19.5,
    salary_is_predicted: false,
    match_score: 74,
    matched_skills: ['Python', 'SQL'],
    missing_skills: ['Docker', 'AWS Athena'],
    experience_req: '2 - 4 YOE',
    posted_ago: '2 days ago',
    applicants_count: 114,
    urgency: 'Remote Screening',
    apply_url: 'https://nice.com/careers/data-dev-pune',
    description: 'Build automated speech analytics ETL workflows. We value clean code, reproducible queries, and continuous integration.'
  },
  {
    job_id: 'job_del_551',
    title: 'Data Engineer - Consumer Analytics',
    company: 'Zomato / Blinkit',
    city: 'Delhi-NCR',
    area: 'Gurugram Cyber City',
    work_mode: 'In-office',
    work_mode_detail: 'Campus Gurugram',
    salary_min: 17.0,
    salary_max: 22.0,
    salary_is_predicted: true,
    match_score: 71,
    matched_skills: ['Python', 'SQL', 'Git'],
    missing_skills: ['Apache Spark', 'Redis'],
    experience_req: '2 - 4 YOE',
    posted_ago: '4 days ago',
    applicants_count: 78,
    urgency: 'Fast Track 7-Day Cycle',
    apply_url: 'https://zomato.com/careers/data-eng',
    description: 'Handle 10-minute instant delivery logistics data feeds. High-volume clickstream logs, rider dispatch analytics, and real-time inventory reconciliation.'
  },
  {
    job_id: 'job_mum_622',
    title: 'Data Engineering Analyst',
    company: 'JPMorgan Chase & Co.',
    city: 'Mumbai',
    area: 'Powai, Mindspace',
    work_mode: 'Hybrid',
    work_mode_detail: '3 days office / 2 days remote',
    salary_min: 18.0,
    salary_max: 23.5,
    salary_is_predicted: false,
    match_score: 79,
    matched_skills: ['Python', 'SQL', 'Linux Shell', 'Git'],
    missing_skills: ['AWS Glue', 'PySpark'],
    experience_req: '2 - 4 YOE',
    posted_ago: '6 days ago',
    applicants_count: 92,
    urgency: 'Active Review',
    apply_url: 'https://jpmorganchase.com/careers/mumbai-de',
    description: 'Global Asset Wealth Management data architecture. Regulatory audit compliance, distributed data pipelines, and database optimization.'
  }
];

export const NEGOTIATION_PLAYBOOK = {
  candidate_worth_summary: {
    target_role: 'Data Engineer',
    city: 'Bengaluru',
    candidate_skills_count: 4,
    recommended_ask_lpa: 19.5,
    walk_away_floor_lpa: 16.5,
    current_benchmark_median: 18.0
  },
  talking_points: [
    {
      category: 'Market Positioning',
      script: 'Based on empirical percentile data for Bengaluru (NASSCOM & 72k+ calibrated job postings), the 50th percentile for a Data Engineer with 2.8 YOE sits at ₹18.0L LPA, with the upper quartile reaching ₹22.5L LPA. My verified profile matches 78% of your core stack.',
      rationale: 'Frames compensation around empirical city percentiles rather than previous company pay.'
    },
    {
      category: 'Service-to-Product Transition Anchor',
      script: 'While my previous CTC was anchored in IT services bands, my actual day-to-day contributions encompassed writing production ETL pipelines, query optimization, and automating data ingestion scripts. I am interviewing for this role because my engineering output delivers immediate Day-1 product velocity.',
      rationale: 'Breaks the artificial "30% hike on previous CTC" trap common in Indian HR discussions.'
    },
    {
      category: 'Countering the Initial Lowball Offer',
      script: 'Thank you for the initial offer of ₹15.5L LPA. Given that the market median for this role is ₹18.0L LPA and I have already demonstrated end-to-end execution on Python and SQL optimization, I would be excited to sign immediately at ₹19.2L LPA (Fixed Base + Variable) with standard joining bonus.',
      rationale: 'Gives the recruiter a clear, defensible compromise number within approved band budget.'
    },
    {
      category: 'Walk-away Boundary Formulation',
      script: 'I have benchmarked my minimum floor at ₹16.5L LPA Fixed Base. Below this figure, the compensation does not reflect the specialized data engineering responsibilities and Bangalore living index.',
      rationale: 'Establishes clear conviction without appearing confrontational.'
    }
  ]
};

export const AI_COUNSELOR_KNOWLEDGE = [
  {
    triggers: ['docker', 'earn more', 'salary shift', 'compensation jump', 'uplift'],
    role: 'system',
    reply: `Based on **14,200+ verified Indian tech postings** in our Tukey-filtered dataset, adding **Docker & Containerization** to a backend or data profile delivers an estimated **+₹2.8L to +₹3.5L LPA** compensation uplift in **Bengaluru** and **Hyderabad**.

### Why This Shift Happens in Indian Hiring:
1. **Removes DevOps Friction:** 71% of product companies now require software engineers to containerize their own microservices, eliminating handoff delays to operations teams.
2. **Shortlist Velocity:** Resumes showcasing Docker and containerized test runners experience a **1.35× higher shortlist conversion** in mid-sized Indian product startups (Razorpay, Swiggy, Zepto).
3. **Band Upgrade:** Moves candidate evaluation from *Junior Scripting (Band L1)* to *Autonomous Platform Execution (Band L2)*.

**Recommended Next Step:** Spend 10 days completing our Phase 1 Containerization module before initiating your interview push.`
  },
  {
    triggers: ['pune', 'bengaluru', 'compare', 'city', 'cost of living'],
    role: 'system',
    reply: `Here is the empirical compensation comparison between **Bengaluru** and **Pune** for a **Data Engineer (2–4 YOE)**:

| Metric | Bengaluru (Tier 1 Baseline) | Pune (Enterprise Hub) | Difference |
|---|---|---|---|
| **25th Percentile** | ₹14.5L LPA | ₹12.2L LPA | -15.8% |
| **50th Percentile (Median)** | **₹18.0L LPA** | **₹15.5L LPA** | **-13.9%** |
| **75th Percentile** | ₹22.5L LPA | ₹19.5L LPA | -13.3% |
| **Active Postings Volume** | 28,400+ | 11,800+ | 2.4× more roles in BLR |
| **Rent & Cost Index** | ₹28,000 / mo (avg 2BHK) | ₹18,500 / mo (avg 2BHK) | ~34% cheaper in Pune |

**Strategic Guidance:** 
If saving potential is your primary metric, an **₹16L LPA offer in Pune** delivers roughly equivalent disposable income to an **₹18.5L LPA offer in Bengaluru**. However, Bengaluru offers **2.4× higher switching liquidity** for subsequent promotions.`
  },
  {
    triggers: ['service', 'product', 'infosys', 'tcs', 'wipro', 'switch', 'transition'],
    role: 'system',
    reply: `### The Indian Service-to-Product Transition Strategy (2025 Market)

Transitioning from an IT services firm (Infosys, TCS, Wipro, Cognizant) to a product startup or tech MNC requires breaking three systemic biases:

1. **The "30% Hike Ceiling" Trap:**
   - Standard Indian HR will attempt to anchor your offer to a 30% hike on your service CTC (e.g. ₹5.4L $\\rightarrow$ ₹7.0L LPA).
   - **Counter-strategy:** Refuse to disclose current payslips during initial technical screening rounds. Anchor discussions firmly to the **Role Market Benchmark (₹16.0L–19.5L LPA)** using Vriddhi's percentile reports.

2. **The 90-Day Notice Period Barrier:**
   - Most Tier-1 product firms reject candidates on 90-day notice.
   - **Counter-strategy:** Complete 80% of your interview preparation *before* resigning, or negotiate buyouts/early release once you reach final round conversations.

3. **Proof-of-Work Verification:**
   - Service resumes frequently describe vague client maintenance tickets (*"Worked on support for European retail client"*).
   - **Correction:** Rewrite bullet points to emphasize **high-scale system outcomes**: *"Optimized PostgreSQL indexing across 12M rows, reducing query latency from 4.2s to 180ms."*`
  },
  {
    triggers: ['spark', 'prerequisite', 'how to learn', 'learning path', 'pyspark'],
    role: 'system',
    reply: `### Apache Spark Learning Path & Dependencies

In Vriddhi's **483-Skill DAG Taxonomy**, attempting to learn Apache Spark without foundational prerequisites leads to 60%+ abandonment rates. Here is the verified sequence:

1. **Foundational Pre-requisites (Must have):**
   - **Python Core:** Advanced iterators, lambda functions, and OOP principles.
   - **Relational SQL:** Group by, Window Functions (\`ROW_NUMBER()\`, \`DENSE_RANK()\`), and inner/outer joins.
   - **Linux & Memory Concepts:** RAM allocation vs. disk I/O, JVM heap concepts.

2. **Core Spark Execution:**
   - Understand **Lazy Evaluation** and RDD lineage before touching high-level code.
   - Practice with **PySpark DataFrames** on local single-node clusters via Docker.
   - Master the difference between **Narrow Transformations** (\`map\`, \`filter\`) and **Wide Transformations** (\`groupBy\`, \`join\` triggering network shuffles).

3. **Target ROI in India:**
   - Spark mastery unlocks **+6 immediate job listings** in your profile and commands a median offer boost of **+₹2.8L LPA**.`
  }
];
