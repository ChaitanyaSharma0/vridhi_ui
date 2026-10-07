-- VRIDDHI analysis views - derived values are computed here, never stored in the core tables
USE `vriddhi`;

CREATE OR REPLACE VIEW v_company_job_title AS
SELECT f.company_job_title_id, f.reference_no, c.company_name, c.company_type, c.is_placeholder_employer,
       t.job_title, t.base_role, t.seniority, f.min_experience_years,
       f.min_salary_lpa, f.avg_salary_lpa, f.max_salary_lpa,
       f.max_salary_lpa - f.min_salary_lpa AS salary_spread_lpa,
       ROUND(f.max_salary_lpa / f.min_salary_lpa, 2) AS salary_range_ratio,
       f.num_of_jobs, LN(1 + f.num_of_jobs) AS log_num_jobs,
       f.is_min_salary_implausible, f.is_wide_salary_range, f.is_senior_zero_exp, f.is_num_jobs_outlier, f.is_salary_outlier_in_title,
       (c.is_placeholder_employer = 0) AS in_analysis_sample
FROM fact_company_job_title f
JOIN dim_company c ON c.company_id = f.company_id
JOIN dim_job_title t ON t.job_title_id = f.job_title_id;

CREATE OR REPLACE VIEW v_job_posting AS
SELECT p.posting_id, p.job_title_raw, p.job_title_clean, r.role_family, r.is_analytics, p.role_source,
       sn.seniority, sn.seniority_rank, p.exp_min_years, p.exp_max_years,
       (p.exp_min_years + p.exp_max_years) / 2 AS exp_mid_years,
       b.salary_band_id AS salary_band_ord, b.band_label AS salary_band, b.low_lpa AS salary_low_lpa, b.high_lpa AS salary_high_lpa,
       (b.low_lpa + b.high_lpa) / 2 AS salary_mid_lpa, (b.salary_band_id >= 5) AS is_high_pay_15plus,
       c.city_name AS primary_city, c.city_category, COALESCE(pc.n_cities, 0) AS n_cities,
       p.location_raw, p.job_description,
       p.is_job_type_tagged, p.is_desc_missing, p.is_desc_truncated, p.is_skills_truncated,
       p.is_near_duplicate, p.is_possible_repost, p.is_spam, p.is_international, p.is_salary_exp_inconsistent,
       (p.is_spam = 0 AND p.is_international = 0 AND p.is_near_duplicate = 0) AS in_india_sample,
       (p.is_spam = 0 AND p.is_international = 0 AND p.is_near_duplicate = 0 AND r.is_analytics = 1) AS in_core_analytics,
       (p.is_spam = 0 AND p.is_international = 0 AND p.is_near_duplicate = 0 AND r.is_analytics = 1
        AND p.is_salary_exp_inconsistent = 0) AS in_salary_model
FROM fact_job_posting p
JOIN dim_role_family r ON r.role_family_id = p.role_family_id
JOIN dim_seniority sn ON sn.seniority_id = p.seniority_id
JOIN dim_salary_band b ON b.salary_band_id = p.salary_band_id
JOIN dim_city c ON c.city_id = p.primary_city_id
LEFT JOIN (SELECT posting_id, COUNT(*) AS n_cities FROM bridge_posting_city GROUP BY posting_id) pc ON pc.posting_id = p.posting_id;

CREATE OR REPLACE VIEW v_posting_skill AS
SELECT b.posting_id, s.skill_id, s.skill_name, s.skill_type, b.found_in
FROM bridge_posting_skill b
JOIN dim_skill s ON s.skill_id = b.skill_id;

CREATE OR REPLACE VIEW v_posting_dimension AS
SELECT p.posting_id,
  COALESCE(MAX(d.dimension_code = 'big_data'), 0) AS `dim_big_data`,
  COALESCE(MAX(d.dimension_code = 'maths_stats'), 0) AS `dim_maths_stats`,
  COALESCE(MAX(d.dimension_code = 'coding'), 0) AS `dim_coding`,
  COALESCE(MAX(d.dimension_code = 'ai_ml'), 0) AS `dim_ai_ml`,
  COALESCE(MAX(d.dimension_code = 'dashboard_story'), 0) AS `dim_dashboard_story`
FROM fact_job_posting p
LEFT JOIN bridge_posting_skill b ON b.posting_id = p.posting_id
LEFT JOIN map_skill_dimension m ON m.skill_id = b.skill_id
LEFT JOIN dim_skill_dimension d ON d.dimension_id = m.dimension_id
GROUP BY p.posting_id;

CREATE OR REPLACE VIEW v_skill_demand_core AS
SELECT s.skill_name, s.skill_type, COUNT(DISTINCT b.posting_id) AS postings,
       ROUND(COUNT(DISTINCT b.posting_id) / (SELECT COUNT(*) FROM v_job_posting WHERE in_core_analytics = 1), 4) AS share_of_core_postings
FROM bridge_posting_skill b
JOIN dim_skill s ON s.skill_id = b.skill_id
JOIN v_job_posting v ON v.posting_id = b.posting_id AND v.in_core_analytics = 1
GROUP BY s.skill_name, s.skill_type;

CREATE OR REPLACE VIEW v_jds_wide AS
SELECT e.jds_employee_id, e.source_id,
  MAX(CASE WHEN d.dimension_code = 'big_data' THEN s.score END) AS `big_data_skills`,
  MAX(CASE WHEN d.dimension_code = 'maths_stats' THEN s.score END) AS `maths_stats_skills`,
  MAX(CASE WHEN d.dimension_code = 'coding' THEN s.score END) AS `coding_skills`,
  MAX(CASE WHEN d.dimension_code = 'ai_ml' THEN s.score END) AS `ai_and_ml_skills`,
  MAX(CASE WHEN d.dimension_code = 'dashboard_story' THEN s.score END) AS `dashboard_and_storytelling_skills`,
  e.salary_hike_high
FROM jds_employee e
JOIN fact_jds_skill_score s ON s.jds_employee_id = e.jds_employee_id
JOIN dim_skill_dimension d ON d.dimension_id = s.dimension_id
GROUP BY e.jds_employee_id, e.source_id, e.salary_hike_high;

CREATE OR REPLACE VIEW v_sds_wide AS
SELECT w.*,
  ROUND((`neuroticism` - AVG(`neuroticism`) OVER ()) / STDDEV_SAMP(`neuroticism`) OVER (), 4) AS `neuroticism_z`,
  ROUND((`extraversion` - AVG(`extraversion`) OVER ()) / STDDEV_SAMP(`extraversion`) OVER (), 4) AS `extraversion_z`,
  ROUND((`openness_to_experience` - AVG(`openness_to_experience`) OVER ()) / STDDEV_SAMP(`openness_to_experience`) OVER (), 4) AS `openness_to_experience_z`,
  ROUND((`agreeableness` - AVG(`agreeableness`) OVER ()) / STDDEV_SAMP(`agreeableness`) OVER (), 4) AS `agreeableness_z`,
  ROUND((`conscientiousness` - AVG(`conscientiousness`) OVER ()) / STDDEV_SAMP(`conscientiousness`) OVER (), 4) AS `conscientiousness_z`
FROM (
  SELECT e.sds_employee_id, e.source_id,
    MAX(CASE WHEN t.trait_code = 'neuroticism' THEN s.score END) AS `neuroticism`,
  MAX(CASE WHEN t.trait_code = 'extraversion' THEN s.score END) AS `extraversion`,
  MAX(CASE WHEN t.trait_code = 'openness_to_experience' THEN s.score END) AS `openness_to_experience`,
  MAX(CASE WHEN t.trait_code = 'agreeableness' THEN s.score END) AS `agreeableness`,
  MAX(CASE WHEN t.trait_code = 'conscientiousness' THEN s.score END) AS `conscientiousness`,
    e.success_high
  FROM sds_employee e
  JOIN fact_sds_trait_score s ON s.sds_employee_id = e.sds_employee_id
  JOIN dim_personality_trait t ON t.trait_id = s.trait_id
  GROUP BY e.sds_employee_id, e.source_id, e.success_high
) w;

CREATE OR REPLACE VIEW v_market_vs_success AS
SELECT d.dimension_code, d.dimension_name,
       ROUND(SUM(CASE WHEN pd.flag = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS market_demand_share_core,
       (SELECT ROUND(AVG(s.score), 3) FROM fact_jds_skill_score s JOIN jds_employee e ON e.jds_employee_id = s.jds_employee_id
         WHERE s.dimension_id = d.dimension_id AND e.salary_hike_high = 1) AS jds_mean_score_high_hike,
       (SELECT ROUND(AVG(s.score), 3) FROM fact_jds_skill_score s JOIN jds_employee e ON e.jds_employee_id = s.jds_employee_id
         WHERE s.dimension_id = d.dimension_id AND e.salary_hike_high = 0) AS jds_mean_score_low_hike
FROM dim_skill_dimension d
CROSS JOIN (SELECT posting_id FROM v_job_posting WHERE in_core_analytics = 1) c
LEFT JOIN (
  SELECT DISTINCT b.posting_id, m.dimension_id, 1 AS flag
  FROM bridge_posting_skill b JOIN map_skill_dimension m ON m.skill_id = b.skill_id
) pd ON pd.posting_id = c.posting_id AND pd.dimension_id = d.dimension_id
GROUP BY d.dimension_id, d.dimension_code, d.dimension_name;
