# M00 – Data exploration (raw data vs clean data)

**Chapter 0: The data. Feeds the Data Exploration section of the report (25 marks).**

## The question
What was wrong with the raw data, what did we keep, and what does the cleaned data look like before modelling?

## What we did (plain words)
These are charts, not a trained model. They show the problems we found and what we did about them:
- **Issues by cleaning stage:** how many data problems each stage (S1–S10) found, per file.
- **Missing values** in the raw files.
- **Funnel:** how 15,841 raw postings became the 5,127 core analytics postings. Only exact duplicates were deleted; everything else was flagged.
- **Role families:** what kinds of jobs are really inside "Analytics Jobs".
- **Skill recovery:** how much demand we would have missed if we had only read the truncated skill lists.
- **Distributions:** salary bands, experience, cities, DS Jobs openings and salaries, JDS and SDS scores.

## What we found
- **50 distinct issues** across the four files: duplicates, non-unique ids, numbers stored as text, spelling variants, truncated text, out-of-scope records, outliers, missing values.
- `job_type` is **76% missing** and `job_description` **22% missing** in the raw file.
- **Two-thirds of "Analytics Jobs" are not analytics roles** (software, BPO, sales, finance, medical coding), so using the file as-is would distort everything.
- Recovering skills from descriptions mostly lifts **storytelling (15.5% → 17.8%)** and **maths (13.8% → 15.8%)**. These are the skills people *describe* rather than list as keywords.
- DS Jobs openings range from 1 to 4,200 (log-transformed); top-firm salaries are real and kept.
- JDS scores show a **ceiling effect**: 18–58% of scores are a perfect 5.

## Why it matters
Each finding drove a modelling choice:
- ordinal model for bands;
- log transforms;
- core analytics sample;
- profile-shape tests for the JDS ceiling.

## Files
- `figures/01_issues_and_missing.png` … `figures/07_people_data_distributions.png`
- `results/*.csv`; VFL copies in `../vfl/M00_*.csv`
