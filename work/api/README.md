# Vriddhi: how to run it

## Start
From the `New Vridhi` folder:
```
python work/api/server.py
```
Wait for `engine ready` (about 15 s: it loads the cleaned data and refits the models), then open **http://localhost:8770/**.

- **Homepage:** the original template, with live numbers from the engine.
- **Vriddhi AI:** the "Audit your job description" button. You can also open http://localhost:8770/#ai directly.

The server listens on this laptop only (127.0.0.1 and ::1). It never contacts the internet. Only the Google Fonts link does; without internet, the pages fall back to system fonts.

## The JD audit (Vriddhi AI)
Paste a job description, title on the first line. You get:

1. **What your JD asks for.** Skill words are highlighted, and the 5 skill areas are shown as lit or grey.
2. **What actually gets juniors a high raise.**
   - Each area's weight comes from the junior model (M06): log odds ratio per standard deviation, normalised to 100%.
   - Coverage = the sum of the weights of the areas the JD asks for.
3. **Updated JD.** The original text plus green lines for rewarded areas that are missing, and notes on coding and big data.
4. **The effect.** The chance of a high raise for a junior who matches the current JD vs the updated one.
   - Asked-for areas use the average score of high-raise juniors.
   - All other areas use the average score of low-raise juniors.

Senior titles get an extra card on curiosity and discipline (from the senior data).

## Prove it's real
```
python work/api/test_engine.py
```
There are 50 checks, 9 of them for the JD audit. The JD-audit checks confirm:
- the examples are real postings;
- coverage equals the sum of the weights;
- the "before" chance equals an independent refit;
- a coding-only JD is told to add maths and storytelling.

## Stage shortcuts
| URL | What it does |
|---|---|
| `http://localhost:8770/?ex=0` | Audits real example posting 0 (Data Analyst) |
| `?ex=1` | Example 1, Data Scientist; shows the senior card |
| `?ex=2` | Example 2, BI / Reporting |
| `?shot=1` | Turns animations off, for screenshots |

## Files
- `engine.py`: data, models, `jd_audit`, `jd_examples`, `showcase`, plus the earlier endpoints.
- `server.py`: standard-library server.
- `test_engine.py`: the checks.
- `shot.ps1`: headless screenshots.

Frontend (`v-fr/`):
- `index.html`: the original template with aligned content.
- `src/js/jdAudit.js`, `src/css/jd.css`.

The old engine page is archived in `work/_archive_engine_ui/`.
