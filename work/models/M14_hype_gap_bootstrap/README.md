# M14 – The hype gap: what ads ask for vs what is rewarded (Bootstrap)

**Chapter 5: The gap. This is the centrepiece chart.**

## The question
Put the two signals side by side for each skill area:
- **demand**: % of job ads asking for it (M01);
- **reward**: how strongly it separates high-hike juniors (effect size d, from M06's data).

Is the mismatch real, or could it be luck?

## What we did (plain words)
- **Bootstrap:** reshuffle the data 2,000 times (resampling postings and juniors with replacement) and recompute both numbers each time. The spread of answers gives a **95% confidence range**, like re-running a survey 2,000 times.
- Effect size **d**: the difference between high- and low-hike juniors in "typical spreads". 0.5 = medium, 0.8+ = large.
- Placed each skill area on a map: demand (across) vs reward (up).

## What we found
| Skill area | Demand rank | Reward rank | Reward (d, 95% range) | Quadrant |
|---|---|---|---|---|
| Dashboards & storytelling | #3 (17.8%) | **#1** | 1.11 [0.86–1.35] | **Hidden edge** |
| Maths & statistics | **#5** (15.8%) | **#2** | 1.05 [0.82–1.27] | **Hidden edge** |
| Coding | **#1** (42.8%) | #3 | 0.89 [0.59–1.17] | Core |
| AI & machine learning | #2 (19.5%) | #4 | 0.81 [0.57–1.05] | Hidden edge |
| Big data | #4 (16.3%) | **#5** | 0.22 [−0.13–0.57] | Not clearly rewarded |

- In **91%** of the 2,000 reshuffles, storytelling's reward beat coding's; maths beat coding in **83%**.
- The **ranking flip** chart shows it in one picture: the least-asked skill (maths) is the 2nd most rewarded, and the most-asked skill (coding) drops to 3rd.

## What it means for the business
> **Job ads are spending their attention on the wrong skills.**

- Coding is asked for 2.5× more than maths or storytelling, yet those two separate the high-growth juniors more.
- Big data is asked for as often as maths but shows **no clear link** to growth.
- **Action:**
  - Rebalance job descriptions and interviews toward maths/stats and storytelling.
  - Keep coding as a baseline requirement, not *the* requirement.
  - Treat big data as role-specific (Data Engineers), not universal.

## How sure are we
- The demand numbers are very precise (±1%).
- The reward numbers have wider ranges (139 people), so storytelling > coding is **likely (91%) but not certain**. We say "likely", not "proven".
- **Limits:**
  - Linking ads to juniors relies on our 5-area taxonomy.
  - Juniors come from one company.

## Files
- `figures/01_hype_gap_map.png`: the money chart
- `figures/02_rank_flip.png`: the simplest version for slides
- `results/hype_gap.csv`
