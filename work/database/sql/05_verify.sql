-- Run after loading. Every 'expected' value was computed from the cleaned data by build_database.py.
USE `vriddhi`;
SELECT 'row counts' AS check_name, t.table_name, t.actual, t.expected, IF(t.actual = t.expected, 'PASS', 'FAIL') AS result FROM (
SELECT 'stg_datascience_jobs' AS table_name, (SELECT COUNT(*) FROM `stg_datascience_jobs`) AS actual, 1602 AS expected
UNION ALL SELECT 'stg_analytics_jobs' AS table_name, (SELECT COUNT(*) FROM `stg_analytics_jobs`) AS actual, 15841 AS expected
UNION ALL SELECT 'stg_jds_skill_traits' AS table_name, (SELECT COUNT(*) FROM `stg_jds_skill_traits`) AS actual, 139 AS expected
UNION ALL SELECT 'stg_sds_personality_traits' AS table_name, (SELECT COUNT(*) FROM `stg_sds_personality_traits`) AS actual, 161 AS expected
UNION ALL SELECT 'dim_company' AS table_name, (SELECT COUNT(*) FROM `dim_company`) AS actual, 642 AS expected
UNION ALL SELECT 'dim_job_title' AS table_name, (SELECT COUNT(*) FROM `dim_job_title`) AS actual, 10 AS expected
UNION ALL SELECT 'dim_city' AS table_name, (SELECT COUNT(*) FROM `dim_city`) AS actual, 679 AS expected
UNION ALL SELECT 'dim_role_family' AS table_name, (SELECT COUNT(*) FROM `dim_role_family`) AS actual, 23 AS expected
UNION ALL SELECT 'dim_seniority' AS table_name, (SELECT COUNT(*) FROM `dim_seniority`) AS actual, 5 AS expected
UNION ALL SELECT 'dim_salary_band' AS table_name, (SELECT COUNT(*) FROM `dim_salary_band`) AS actual, 6 AS expected
UNION ALL SELECT 'dim_skill' AS table_name, (SELECT COUNT(*) FROM `dim_skill`) AS actual, 8301 AS expected
UNION ALL SELECT 'dim_skill_dimension' AS table_name, (SELECT COUNT(*) FROM `dim_skill_dimension`) AS actual, 5 AS expected
UNION ALL SELECT 'map_skill_dimension' AS table_name, (SELECT COUNT(*) FROM `map_skill_dimension`) AS actual, 470 AS expected
UNION ALL SELECT 'dim_personality_trait' AS table_name, (SELECT COUNT(*) FROM `dim_personality_trait`) AS actual, 5 AS expected
UNION ALL SELECT 'fact_company_job_title' AS table_name, (SELECT COUNT(*) FROM `fact_company_job_title`) AS actual, 1602 AS expected
UNION ALL SELECT 'fact_job_posting' AS table_name, (SELECT COUNT(*) FROM `fact_job_posting`) AS actual, 14840 AS expected
UNION ALL SELECT 'bridge_posting_city' AS table_name, (SELECT COUNT(*) FROM `bridge_posting_city`) AS actual, 17774 AS expected
UNION ALL SELECT 'bridge_posting_skill' AS table_name, (SELECT COUNT(*) FROM `bridge_posting_skill`) AS actual, 81279 AS expected
UNION ALL SELECT 'jds_employee' AS table_name, (SELECT COUNT(*) FROM `jds_employee`) AS actual, 139 AS expected
UNION ALL SELECT 'fact_jds_skill_score' AS table_name, (SELECT COUNT(*) FROM `fact_jds_skill_score`) AS actual, 695 AS expected
UNION ALL SELECT 'sds_employee' AS table_name, (SELECT COUNT(*) FROM `sds_employee`) AS actual, 161 AS expected
UNION ALL SELECT 'fact_sds_trait_score' AS table_name, (SELECT COUNT(*) FROM `fact_sds_trait_score`) AS actual, 805 AS expected
UNION ALL SELECT 'meta_data_quality_log' AS table_name, (SELECT COUNT(*) FROM `meta_data_quality_log`) AS actual, 58 AS expected
) t;
SELECT 'core analytics postings' AS check_name, COUNT(*) AS actual, 5127 AS expected FROM v_job_posting WHERE in_core_analytics = 1;
SELECT 'india sample postings' AS check_name, COUNT(*) AS actual, 14429 AS expected FROM v_job_posting WHERE in_india_sample = 1;
SELECT 'total openings (DS)' AS check_name, SUM(num_of_jobs) AS actual, 93005 AS expected FROM fact_company_job_title;
SELECT 'orphan postings without role family' AS check_name, COUNT(*) AS actual, 0 AS expected FROM fact_job_posting p LEFT JOIN dim_role_family r ON r.role_family_id = p.role_family_id WHERE r.role_family_id IS NULL;
SELECT 'dimension demand (core)' AS check_name, dimension_code, market_demand_share_core AS actual, CASE dimension_code WHEN 'big_data' THEN 0.1629 WHEN 'maths_stats' THEN 0.1576 WHEN 'coding' THEN 0.4277 WHEN 'ai_ml' THEN 0.195 WHEN 'dashboard_story' THEN 0.1783 END AS expected FROM v_market_vs_success;
