// One fixed colour per skill dimension, used everywhere (chips, radar, waterfall, heatmap, graph, map).
export const DIMS = [
  { key: "big_data", label: "Big data", col: "big_data_skills", color: "#2563eb" },
  { key: "maths_stats", label: "Maths & statistics", col: "maths_stats_skills", color: "#7c3aed" },
  { key: "coding", label: "Coding", col: "coding_skills", color: "#16a34a" },
  { key: "ai_ml", label: "AI & machine learning", col: "ai_and_ml_skills", color: "#ea580c" },
  { key: "dashboard_story", label: "Dashboards & storytelling", col: "dashboard_and_storytelling_skills", color: "#db2777" },
];
export const DIM = Object.fromEntries(DIMS.map(d => [d.key, d]));
export const BY_COL = Object.fromEntries(DIMS.map(d => [d.col, d]));
export const OTHER = "#78716c";
export const colorOf = k => (DIM[k] ? DIM[k].color : OTHER);
export const TRAITS = [
  { key: "neuroticism", label: "Neuroticism", color: "#64748b" },
  { key: "extraversion", label: "Extraversion", color: "#0284c7" },
  { key: "openness_to_experience", label: "Openness", color: "#7c3aed" },
  { key: "agreeableness", label: "Agreeableness", color: "#16a34a" },
  { key: "conscientiousness", label: "Conscientiousness", color: "#e96c2f" },
];
export const TRAIT = Object.fromEntries(TRAITS.map(t => [t.key, t]));
export const BANDS = ["0to3", "3to6", "6to10", "10to15", "15to25", "25to50"];
export const BAND_LABEL = { "0to3": "0-3", "3to6": "3-6", "6to10": "6-10", "10to15": "10-15", "15to25": "15-25", "25to50": "25-50" };
