# M13 – Types of senior data scientist (K-means personas)

**Chapter 4: What makes seniors succeed**

## The question
Without telling the computer who succeeded, do seniors naturally fall into personality **types**? And do some types succeed far more than others?

## What we did (plain words)
- **K-means clustering** sorts people into groups of similar profiles, like sorting a mixed bag of sweets into piles by look.
- Traits were put on the same scale first (z-scores).
- **Choosing the number of groups:** tried 2 to 7. The "silhouette" score (how clearly separated the groups are) was best at **4 groups**. We limited the choice to 3–5 so the personas stay easy to explain.
- Named each persona after its strongest and weakest traits, then checked each persona's success rate.

## What we found
| Persona | People | Success rate |
|---|---|---|
| **High Conscientiousness & Openness** (also above-average extraversion) | 88 | **89%** |
| High Neuroticism, low Agreeableness | 22 | 32% |
| High Agreeableness, low Openness | 23 | **0%** |
| Low Agreeableness & Openness (low on most traits) | 28 | **0%** |

- The link between persona and success is extremely strong (chi-square p ≈ 10⁻²³).
- The 2-D map shows the successful persona as one clear cloud.

## What it means for the business
- Successful seniors are **one recognisable type: the "disciplined explorer"**, organised and curious.
- Friendly but incurious seniors ("High Agreeableness, low Openness") **never** reached high success here. Being pleasant is not enough for client-facing data science.
- **Use:** an easy-to-remember profile for senior hiring, promotion and coaching conversations.

## How sure are we
- The groups were found **without** using the success label, so the success differences are a genuine discovery, not built in.
- **Limits:**
  - 22–28 people in the smaller personas, so read their rates as approximate (see the confidence ranges on the chart).
  - Persona names are our labels.

## Files
- `figures/01_choosing_k.png`, `figures/02_personas.png`, `figures/03_persona_map.png`
- `results/personas.csv`, `results/choosing_k.csv`, `results/persona_assignments.csv`
