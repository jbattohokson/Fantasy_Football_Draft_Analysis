# ADP rankings aren't wrong.
### They're just not using the right variables.

> **[Live Report](https://jbattohokson.github.io/Fantasy_Football_Draft_Analysis/Fantasy_Football_Analysis.html)** | [GitHub Repo](https://github.com/jbattohokson/Fantasy_Football_Draft_Analysis)

---

## Executive Summary

Consensus ADP rankings are built from aggregate draft behavior — which means they encode the biases of the average drafter, not the optimal draft strategy. This analysis identifies where those biases create exploitable inefficiencies across five seasons (2021–2025) of NFL PPR data, covering QB, RB, WR, and TE positions in a MySQL data warehouse built from raw FantasyPros season stats.

Three patterns are consistent and predictable. Running backs in rounds 1–2 underperform their ADP by 15–20 points on average. Wide receivers in rounds 3–5 outperform ADP by 10–20 points. Targets are the single strongest predictor of fantasy production across all positions (correlation 0.72–0.81) — yet ADP rankings weight prior-season points more heavily than target share. A draft strategy that exploits these three inefficiencies is estimated to add 25–40 fantasy points over a full season — in a 12-team league, the margin between making the playoffs and missing them.

| Metric | Value |
|--------|-------|
| RB rounds 1–2 avg underperformance | −15 to −20 pts vs. ADP |
| WR rounds 3–5 avg outperformance | +10 to +20 pts vs. ADP |
| Target share correlation with production | 0.72–0.81 |
| QB cross-season predictability (R²) | 0.71 |
| TE cross-season predictability (R²) | 0.58 |
| Estimated season-long gain vs. consensus ADP | 25–40 pts |

---

## Tools & Technologies

| Tool | Purpose |
|------|---------|
| MySQL | Data warehouse — 5-season PPR dataset, ~4,000 player-season observations |
| Python (Statsmodels) | OLS regression: PPR points vs. target share, ADP, snap count, positional dummies |
| FantasyPros | Scoring datasets and ADP rankings source |
| Tableau | Draft value visualization, positional R² breakdowns |

---

## Findings: Five patterns in the data — and what each one suggests about consensus ADP

### Early-round RBs underperform — injury rates and committee backfields are the mechanism
Running backs drafted in rounds 1–2 underperform their ADP expectations by 15–20 fantasy points on average across 2021–2025. The drivers are structural: injury rates of 15–20% per season, usage volatility from game-script dependencies, and NFL teams increasingly deploying committee backfields that reduce any single back's target share. The exception is a true workhorse with demonstrated pass-catching volume — one who maintains relevance even when the team falls behind. For most early-round RBs, ADP reflects upside scenarios rather than median production.

### Mid-round WRs outperform — stable systems and target volume are the explanation
Wide receivers in rounds 3–5 consistently beat ADP expectations by 10–20 points. The position shows lower injury volatility than RB, more stable offensive systems, and — critically — target share is more predictable year-over-year than RB usage. The R² for WR production is 0.68, second only to QBs. Concentrating 3–4 WR picks in rounds 3–5 extracts more value per pick than any other draft strategy.

### Targets predict production better than any other variable — and ADP underweights them
Target share correlates 0.72–0.81 with fantasy production across RB, WR, and TE positions. Prior-season fantasy points, which ADP rankings weight heavily, explain only 45–54% of next-season variance. The gap between what predicts production and what ADP uses to set prices is where draft value is extracted. The correct pre-draft process: rank players by projected target share, flag those whose ADP sits below their target share rank, and prioritize those players in the relevant draft windows. Players whose ADP was depressed by a down prior season but whose target share held stable are the clearest value targets.

### QB streaming from round 10 or later matches early-round QB production
Quarterbacks drafted after round 10 match first-tier QB production on a point-per-game basis when matchup-selected weekly. QB scoring shows the highest year-to-year stability (R² = 0.71), which means the drop-off from QB1 to QB12 is smaller than ADP pricing implies. Spending a pick on a QB before round 10 in most formats costs a WR or RB selection in the highest-value windows. The exception is superflex and two-QB formats, where QB scarcity is real and early investment is warranted.

### Only 2 TEs are worth early investment — streaming is correct for every other TE slot
Tight end production has the lowest predictability of any position (R² = 0.58) and the steepest drop-off after the elite tier. After the top 2 TEs by target share, streaming produces equivalent results to drafting depth early. Spending round 4 capital on the third-best TE is a common ADP-driven mistake — positional scarcity is real only at the very top of the position.

---

## Draft Strategy: Recommended round-by-round approach

| Rounds | Target | Notes |
|--------|--------|-------|
| 1–2 | Elite WR or pass-catching RB | Avoid standard RBs unless confirmed top-3 workhorse |
| 3–5 | WR focus — 3 picks here | Best value window: +10 to +20 pts vs. ADP |
| 6–7 | RBs and flex WR | RBs offer better risk-adjusted value than rounds 1–2 |
| 8 | Elite TE only — or skip | Invest only if top-2 TE by target share is available |
| 9–12 | QB, backup RB/WR, Defense | Stream QB by matchup. Defense round 12–13. |
| Late | High-upside targets and handcuffs | Players with stable target share whose ADP reflects a down prior season |

---

## Recommended Draft Adjustments and Estimated Impact

### Avoid RB in rounds 1–2 unless workhorse confirmed
Early-round RBs underperform ADP by 15–20 pts on average. Redirecting those picks to elite WRs preserves the same ceiling with lower injury and usage risk. **Estimated gain: 15–20 pts recovered vs. consensus RB-heavy drafting.**

### Stack 3 WRs in rounds 3–5
Mid-round WRs outperform ADP by 10–20 pts — the single most consistent exploitable inefficiency across all five seasons of data. **Estimated gain: 10–20 pts per WR pick vs. ADP expectation in this range.**

### Stream QB from round 10 or later
QB predictability (R² = 0.71) makes the drop-off from QB1 to QB12 smaller than ADP implies. Streaming frees 6–8 picks for WR and RB windows where the value gap is larger. **Estimated gain: 6–8 picks of draft capital redirected to higher-value positions.**

### Draft players with stable target share whose ADP reflects a down prior season
Prior-season points explain only 45–54% of next-season variance. Target share (0.72–0.81 correlation) is the stronger signal. Identify players where target share rank and ADP rank diverge by 2+ rounds — that divergence is the price inefficiency. **Implementing all four adjustments is estimated to add 25–40 pts over a full season.**

---

## Model Results and Data Scope

| Position | R² | RMSE | Predictability |
|----------|----|------|----------------|
| QB | 0.71 | 42 | High — stable passing volume |
| WR | 0.68 | 38 | High when team situation stable |
| RB | 0.64 | 45 | Moderate — usage volatility |
| TE | 0.58 | 52 | Low — highest year-to-year variance |

R² values represent cross-season holdout predictability, not in-sample fit.

| Dimension | Value |
|-----------|-------|
| Analysis period | 2021–2025 (5 seasons) |
| Observations | ~4,000 player-season records |
| Scoring format | Full PPR |
| Sources | FantasyPros (scoring datasets), Fantasy Football Calculator (ADP) |
| Exclusions | Tom Brady excluded from QB analysis for post-2022 retirement seasons |
| Database | MySQL data warehouse built from raw FantasyPros season stats |
