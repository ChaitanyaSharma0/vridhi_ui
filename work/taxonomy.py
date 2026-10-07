"""Five skill dimensions measured in the JDS file, with the market skill names that belong to each.
This is the bridge between the job-posting files and the JDS skill-trait file (shared by cleaning and database build)."""
import re

DIMS = {
    "big_data": ["hadoop", "spark", "pyspark", "hive", "big data", "kafka", "nosql", "mongodb", "hbase", "aws", "azure", "gcp",
                 "cloud", "data lake", "etl", "data warehousing", "data warehouse", "data engineering", "snowflake", "databricks",
                 "informatica", "teradata", "scala", "impala", "pig", "sqoop"],
    "maths_stats": ["statistics", "statistical", "statistical modelling", "regression", "linear regression", "logistic regression",
                    "probability", "mathematics", "econometrics", "hypothesis testing", "time series", "forecasting", "anova",
                    "chaid", "predictive modelling", "spss", "stata", "optimization", "quantitative analysis", "multivariate",
                    "sampling", "biostatistics", "statistical analysis", "eviews", "minitab"],
    "coding": ["python", "r", "sql", "mysql", "postgresql", "tsql", "sas", "java", "scala", "c++", "programming", "coding", "plsql", "vba", "matlab",
               "javascript", "c", "c#", "perl", "shell scripting", "unix", "sas macros"],
    "ai_ml": ["machine learning", "deep learning", "artificial intelligence", "natural language processing", "computer vision",
              "neural networks", "tensorflow", "keras", "pytorch", "data science", "data mining", "text mining", "scikit-learn",
              "image processing", "predictive analytics", "recommendation", "opencv", "reinforcement learning"],
    "dashboard_story": ["tableau", "power bi", "qlikview", "qlik sense", "qlik", "dashboard", "dashboards", "data visualization",
                        "visualization", "reporting", "mis", "mis reporting", "management reporting", "data reporting", "business reporting",
                        "reporting tools", "analytics reporting", "excel", "storytelling", "spotfire", "looker",
                        "business objects", "cognos", "microstrategy", "powerpoint", "presentation"],
}
DIM_NAMES = {"big_data": "Big data", "maths_stats": "Maths & statistics", "coding": "Coding",
             "ai_ml": "AI & machine learning", "dashboard_story": "Dashboards & storytelling"}
JDS_COLUMN = {"big_data": "big_data_skills", "maths_stats": "maths_stats_skills", "coding": "coding_skills",
              "ai_ml": "ai_and_ml_skills", "dashboard_story": "dashboard_and_storytelling_skills"}

TOOLS = {"python": ["python"], "r": ["r"], "sql": ["sql", "mysql", "postgresql", "plsql", "tsql"], "sas": ["sas"],
         "excel": ["excel"], "tableau": ["tableau"], "power_bi": ["power bi"], "hadoop": ["hadoop"], "spark": ["spark", "pyspark"],
         "machine_learning": ["machine learning"], "deep_learning": ["deep learning"],
         "statistics": ["statistics", "statistical", "biostatistics"], "java": ["java"], "aws": ["aws"]}
# compound skills that contain a keyword but mean something else
EXCLUDE = re.compile(r"medical cod|regression test|search engine optim|conversion rate optim|neuro ?linguistic|financial reporting|rtl cod")
# too generic to match inside compounds ("on-page optimization", "bug reporting", "marketing cloud") - whole skill only
EXACT_ONLY = {"optimization", "reporting", "cloud"}


def has(skill, kw):
    """Keyword appears in the skill as a whole word ('oracle sql' has 'sql', 'excellence' has no 'excel').
    1-2 letter keywords (r, c) only as the whole skill or its first word ('r programming'), never inside 'r&d'."""
    if EXCLUDE.search(skill):
        return False
    if kw in EXACT_ONLY:
        return skill == kw
    if len(kw) <= 2:
        return skill == kw or skill.startswith(kw + " ")
    return re.search(r"(?<![\w+#])" + re.escape(kw) + r"(?![\w+#])", skill) is not None


def match_any(skill, kws):
    return any(has(skill, k) for k in kws)


if __name__ == "__main__":
    assert has("oracle sql", "sql") and has("sql server", "sql") and has("pl/sql", "sql") and not has("nosql", "sql")
    assert has("ms excel", "excel") and not has("process excellence", "excel")
    assert has("r programming", "r") and not has("r&d", "r") and not has("ar caller", "r")
    assert has("core java", "java") and not has("javascript", "java") and not has("c++", "c")
    assert not has("medical coding", "coding") and not has("regression testing", "regression")
    assert not has("on - page optimization", "optimization") and not has("bug reporting", "reporting")
    print("taxonomy self-check ok")
