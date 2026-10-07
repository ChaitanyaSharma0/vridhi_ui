# Rebuilding our charts in SAS Visual Analytics (VFL)

Every chart we made in Python has a **plot-ready table** in this folder. In SAS VA you only need to upload the CSV and drag columns onto a chart. No calculations are needed; the numbers are already final and match the report.

## How to load (once per file)
1. SAS Viya for Learners → **Manage Data** (or *Data* in Visual Analytics) → **Import** → **Local file** → pick the CSV.
2. Keep the table name (e.g. `M14_HYPE_GAP`). Click **Import item**.
3. Open **Visual Analytics** → *New report* → *Add data* → pick the table.
4. Check that text columns are **categories** and numbers are **measures**. Change the type in the data pane if VA guesses wrong.
5. Tip: set share columns (0–1) to the **percent format** in the data pane.

## Which chart to build from which file

### Chapter 0 – Data exploration
| File | VA object | Roles |
|---|---|---|
| `M00_analytics_jobs_funnel.csv` | Bar chart (horizontal) | Category: step · Measure: rows |
| `M00_role_family_counts.csv` | Bar chart | Category: role_family · Measure: postings · Colour: analytics |
| `M00_salary_band_distribution.csv` | Bar chart | Category: salary_band · Measure: postings |
| `M00_top_cities.csv` | Bar chart (or geo map by city) | Category: city · Measure: postings |
| `M00_skill_recovery_from_descriptions.csv` | Bar chart, grouped (two measures) | Category: skill_area · Measures: from_key_skills_only, after_description_recovery |
| `M00_jds_ceiling_effect.csv` | Bar chart | Category: skill_area · Measure: share_at_5 |
| `M00_data_quality_log.csv` | List table (or bar of rows_affected by stage) | All columns |
| `M00_raw_profile.csv` | List table / bar of missing_pct | Category: column · Measure: missing_pct |

### Chapter 1 – What companies ask for
| File | VA object | Roles |
|---|---|---|
| `M01_skill_area_demand.csv` | Bar chart | Category: skill_area · Measure: share (add ci_low/ci_high as data labels) |
| `M01_role_by_skill_area.csv` | **Heat map** | X: skill_area · Y: role_family · Colour: share |
| `M01_seniority_by_skill_area.csv` | Heat map or line chart | X: seniority · Group: skill_area · Measure: share |
| `M01_top_25_skills.csv` | Bar chart | Category: skill · Measure: share |
| `M01_tool_demand.csv` | Bar chart | Category: tool · Measure: share |
| `M02_top_25_skill_pairs_by_lift.csv` | Bar chart | Category: skill_a + skill_b (create a calculated item joining them) · Measure: lift |
| `M02_network_edges.csv` | **Network analysis** object | Source: source · Target: target · Link width: lift |
| `M02_skill_area_cooccurrence_lift.csv` | Heat map | X: area_a · Y: area_b · Colour: lift |

### Chapter 2 – What companies pay for
| File | VA object | Roles |
|---|---|---|
| `M03_odds_ratios.csv` | Bar chart or **schedule chart** (range bars) for the forest plot | Category: factor · Measure: odds_ratio; or range from or_ci_low to or_ci_high |
| `M03_predicted_pay_by_experience.csv` | **Line chart** | X: experience · Y: p_15plus_lpa · Group: role |
| `M04_model_comparison.csv` | Bar chart, grouped | Category: feature_set · Measures: exact_accuracy, within_one_band |
| `M04_grouped_permutation_importance.csv` | Bar chart | Category: factor_group · Measure: importance_drop_in_kappa |
| `M05_salary_effects_pct.csv` | Bar chart (forest) | Category: label · Measure: pct_effect |
| `M05_salary_by_title_and_experience.csv` | Line chart or heat map | X: exp_band · Group: job_title · Measure: median |
| `M05_pay_spread_by_title.csv` | Bar chart | Category: job_title · Measure: headroom_pct |
| `M05_pay_spread_by_company_scale.csv` | Bar chart (dual axis) | Category: company_scale · Measures: headroom_pct, avg_salary |
| `M05_cv_r2_comparison.csv` | Bar chart | Category: model · Measure: cv_r2_mean |

### Chapter 3 – What gets juniors ahead
| File | VA object | Roles |
|---|---|---|
| `M06_odds_ratios.csv` | Bar chart (forest) | Category: variable · Measure: or_per_unit (or or_per_sd) |
| `M06_group_means.csv` | Bar chart, grouped | Category: skill_area · Measures: Low hike, High hike |
| `M06_skill_correlations.csv` | Heat map / correlation matrix | Rows: skill · Columns: each skill |
| `M07_leaf_summary.csv` | Bar chart | Category: leaf · Measures: people, share_high |
| `M08_model_comparison.csv` | Bar chart | Category: model · Measure: auc_mean |
| `M08_roc_points.csv` | **Line chart** (ROC) | X: fpr · Y: tpr · Group: model |
| `M08_permutation_importance.csv` | Bar chart, grouped | Category: variable · Group: model · Measure: importance |
| `M09_single_measure_auc.csv` | Bar chart | Category: measure · Measure: auc_either_direction |
| `M09_hike_rate_by_level_and_shape.csv` | Bar chart, grouped | Category: average_level · Group: profile_shape · Measure: high_hike_rate |
| `M09_nested_tests_vs_average.csv` | List table | All columns |

### Chapter 4 – What makes seniors succeed
| File | VA object | Roles |
|---|---|---|
| `M10_odds_ratios.csv` | Bar chart (forest) | Category: variable · Measures: or_per_sd and univariate_or_per_sd (grouped = "alone vs together") |
| `M10_group_means.csv` | Bar chart, grouped | Category: trait · Measures: Low success, High success |
| `M10_trait_correlations.csv` | Heat map | Rows: trait · Columns: each trait |
| `M11_leaf_summary.csv` | Bar chart | Category: leaf · Measures: people, share_high |
| `M12_model_comparison.csv`, `M12_roc_points.csv`, `M12_permutation_importance.csv` | As M08 | As M08 |
| `M13_personas.csv` | Bar chart (success_rate by persona) + heat map of the *_z columns | Category: persona |
| `M13_persona_assignments.csv` | **Scatter plot** | X: pc1 · Y: pc2 · Colour: persona · Shape: success_high |
| `M13_choosing_k.csv` | Line chart | X: k · Y: silhouette |

### Chapter 5 – The gap (centrepiece)
| File | VA object | Roles |
|---|---|---|
| `M14_hype_gap.csv` | **Scatter plot** | X: demand_share · Y: effect_size_d · Label: skill_area · Colour: quadrant. Add reference lines at y = 0.5 and x = average demand |
| `M14_hype_gap.csv` | Bar chart, grouped (simple slide version) | Category: skill_area · Measures: demand_rank, reward_rank |

## Optional: rebuild the people models in SAS Model Studio (for screenshots)
1. Upload `clean/jds_clean.csv` (and `clean/sds_clean.csv`).
2. Model Studio → *New project* → data = JDS → target = `salary_hike_high` (binary).
3. Set the five `*_skills` columns as **inputs**. Reject all the other columns: `row_id`, `id`, and the derived skill_mean/min/range/etc.
4. Pipeline: *Data* → **Logistic Regression**, **Decision Tree** (max depth 4), **Forest**, **Gradient Boosting** → **Model Comparison**.
5. Run. Screenshot the pipeline, the model comparison (ROC / misclassification), the decision tree and the logistic regression odds ratios.
6. Repeat for SDS with target `success_high` and the five trait columns as inputs.

Expect numbers close to (not identical with) ours: SAS uses its own data partition, and ours uses repeated nested cross-validation. The *ranking* of variables should match.
