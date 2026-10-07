# Vriddhi: Hiring for the Right Signals

> Organisations hire for coding, pay for experience, but reward maths, storytelling and breadth in juniors, and curiosity plus discipline in seniors. The signals don't match.

The app has two parts:
- a **homepage** with live numbers from the models;
- **Vriddhi AI**, a job-description audit. You paste the JD a company posts and see:
  - what it asks for;
  - what actually gets junior data scientists a high raise;
  - an updated JD;
  - the expected effect of the change.

Everything runs **locally**: a small Python server loads the cleaned data, refits the trained models, and serves the website. No internet is needed except for Google Fonts, and without internet the pages fall back to system fonts.

---

## Run it on a Mac (about 5 minutes)

### 1. Check Python (3.10 or newer)
```bash
python3 --version
```
If it says "command not found", or a version below 3.10, install Python from https://www.python.org/downloads/macos/ (or `brew install python@3.12`), then open a new Terminal window.

### 2. Get the code
```bash
git clone https://github.com/ChaitanyaSharma0/vridhi_ui.git
cd vridhi_ui
```

### 3. Create a virtual environment and install the libraries (one time)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Start the app
```bash
./run.sh
```
(or `python3 work/api/server.py`)

Wait until the Terminal prints `engine ready in ...s`. This takes about 15 seconds, because the models are refitted on start-up.

### 5. Open it
- Homepage: **http://localhost:8770/**
- Vriddhi AI (JD audit): click **"Audit your job description"**, or open **http://localhost:8770/#ai**

To stop the server, press `Ctrl + C` in the Terminal.

**Next time** you only need:
```bash
cd vridhi_ui
source .venv/bin/activate
./run.sh
```

---

## Demo shortcuts (handy on stage)
| URL | What it shows |
|---|---|
| http://localhost:8770/?ex=0 | A full audit of a real Data Analyst posting from our data |
| http://localhost:8770/?ex=1 | Data Scientist posting (also shows the senior "curiosity and discipline" card) |
| http://localhost:8770/?ex=2 | BI / Reporting posting |

## Check that the numbers are real (optional)
```bash
python3 work/api/test_engine.py
```
This runs 50 checks and should end with `ALL TESTS PASSED`. Among other things, it confirms:
- predictions match an independently refitted model;
- outputs change with inputs;
- the example JDs are real postings.

## Troubleshooting
| Problem | Fix |
|---|---|
| `permission denied: ./run.sh` | `chmod +x run.sh`, then `./run.sh` again |
| `Address already in use` | Something is using port 8770. Run `VRIDDHI_PORT=8771 python3 work/api/server.py` and open http://localhost:8771/ |
| `ModuleNotFoundError` | The virtual environment isn't active. Run `source .venv/bin/activate`, then `pip install -r requirements.txt` |
| Page says the engine is not running | Start the server first (step 4) and wait for `engine ready` |
| `pip install` fails building numpy/scipy | `pip install --upgrade pip`, then try again |

---

## What's in the repo
```
vridhi_ui/
├── run.sh                      start the app
├── requirements.txt            libraries needed to run the app
├── v-fr/                       frontend (HTML, CSS, vanilla JS; no build step)
│   ├── index.html              homepage + Vriddhi AI view
│   └── src/js/jdAudit.js       JD audit + live homepage logic
└── work/                       data and analysis
    ├── api/                    local server, engine, tests
    ├── clean/                  cleaned data (input to the models)
    ├── models/                 the 15 analysis models: figures, results, plain-language READMEs
    ├── database/               MySQL schema, SQL load files, ER diagram
    ├── 01_clean.py ...         cleaning pipeline, role rules, skill taxonomy
    └── requirements-full.txt   extra libraries to rerun the whole pipeline and reports
```

The organisers' raw files are **not** included. To rerun the cleaning (`work/01_clean.py`) or the raw-data verification, put the four original files in the folder **above** `work/` (the repo root).
