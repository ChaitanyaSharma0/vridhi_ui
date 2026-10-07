# M09 – All-rounders or specialists? (Breadth vs spike test)

**Chapter 3: What actually gets juniors ahead**

## The question
Do juniors get ahead by being **excellent at one thing** (a "spike") or **solid at everything** ("breadth")?

## What we did (plain words)
- Gave each junior five summary numbers: average of the 5 skills, weakest skill, strongest skill, gap between strongest and weakest, and unevenness.
- Measured how well **each single number** separates high- from low-hike juniors (AUC: 0.5 = coin flip).
- **Nested tests:** starting from the average, does adding "strongest skill" or "weakest skill" explain anything *extra*?
- Compared hike rates of balanced vs spiky juniors **at the same average level**.

## What we found
| Single number | How well it separates the groups (AUC) |
|---|---|
| **Average of 5 skills** | **0.92** |
| Weakest skill | 0.85 |
| Gap strongest–weakest (smaller = better) | 0.81 |
| **Strongest skill** | **0.59, barely better than a coin flip** |

- Once the average is known, **nothing else adds information** (all extra tests p > 0.4). A spike doesn't help, and the weakest skill on its own doesn't either.
- **Same average, different shape**, % with a high hike:

| Average level | Balanced | Spiky |
|---|---|---|
| Lower | 13% (n=8) | 8% (n=39) |
| Middle | **72%** (n=25) | **52%** (n=29) |
| Top | 95% (n=38) | no one is spiky at the top |

## What it means for the business
> **"Organisations hire for spikes; success rewards breadth."**

Being the best coder in the room isn't what gets juniors ahead; being solid across all five areas is. In practice:
- Interview for **all-round competence**, not one star skill.
- In development, **lift each person's weakest area**. Scores are capped at 5, so strong areas can't grow much more; the room is in the weak ones.

## How sure are we
- Clear and consistent signal.
- **We were honest:** we tested a stricter "weakest-link law" and it did **not** hold beyond the average (p = 0.70), so we don't claim it.
- **Limit:** the balanced vs spiky comparison has small groups (8–39 people).

## Files
- `figures/01_breadth_vs_spike_auc.png`, `figures/02_hike_rate_by_level_and_shape.png`
- `results/single_measure_auc.csv`, `results/nested_tests_vs_average.csv`, `results/hike_rate_by_level_and_shape.csv`
