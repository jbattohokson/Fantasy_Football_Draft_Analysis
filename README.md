# Fantasy Football Draft Analysis (2021–2025)

## The problem

Which players give the most draft value relative to where they're drafted, and which positions are predictable enough to draft on data rather than consensus ADP? (Case study framing: `docs/Fantasy_Football_Case_Study.docx`.)

## What the data can and can't answer

The data is 20 FantasyPros **advanced-stat** exports (QB, RB, WR, TE × 2021–2025, 2,663 player-seasons). They have **no touchdowns and no ADP**, so:

- **Can't answer:** value relative to draft slot. The `Rank` column is the export's sort order (by yards), not draft position, so any "steal" measured against it is circular.
- **Can answer:** how predictable each position is from one season to the next, how steeply value falls off by positional finish (value over replacement), and whether target share predicts next season.

Scoring is one PPR scale with no touchdowns: **QB** passing yards × 0.04; **RB** rushing yards × 0.1 + receptions; **WR/TE** receiving yards × 0.1 + receptions. The files also lack QB rushing and RB receiving yards, so compare players **within** a position.

## Findings

Qualifying season = 8+ games. Predictability compares points per game in consecutive seasons.

1. **Every position regresses, and no starter group is clearly safer.** Across all players, year-over-year r is 0.80 WR, 0.79 TE, 0.78 RB, 0.61 QB, but much of that is backups staying backups. Among players who finished as **starters** (QB12/RB24/WR36/TE12), r drops to TE 0.59, WR 0.56, RB 0.44, QB 0.42, and the 95% intervals overlap (QB 0.14–0.64, TE 0.36–0.75). Starters lose 0.7–1.1 points per game the next season on average.
2. **RB and TE starters fall off most often; QBs rarely do.** 36% of TE, 31% of RB and 28% of WR starters lost 20%+ of their per-game production the next season, against 7% of QBs. These are floors: a starter who missed most of the next season isn't counted.
3. **Scarcity is at elite WR and the top TE.** Average season points above replacement: #1 WR +171, #1 TE +116, #1 RB +109, #1 QB +49. TE value collapses fastest (#3 +55, #6 +30). QB value is understated because touchdowns are missing.
4. **Target share adds a small, real signal.** For WR/TE it predicts next-season points per game almost as well as points per game itself (r 0.76 / 0.78). Added to last season's points per game, it raises R² from 0.644 to 0.651 for WRs (p = 0.003) and from 0.618 to 0.634 for TEs (p = 0.001).

## Recommendations

- **Draft early-round value at WR and the top TE,** where the gap to replacement is largest. Discount any projection that just repeats last season: even starters regress about a point per game.
- **Don't pay for QB certainty early.** QBs rarely collapse, but the replacement-level QB is close behind in these (touchdown-free) numbers.
- **For WR/TE, use target share as a tiebreaker** between receivers with similar points per game.
- **To answer the original draft-value question:** add historical ADP (join on player and season) and touchdown data (weekly box scores), then measure points above what each draft slot usually returns.

## Pipeline

```bash
pip install -r requirements.txt

# No database server: SQLite
python sql/load_raw_tables.py --sqlite sql/fantasy_football.db
python sql/run_sqlite.py --db sql/fantasy_football.db        # writes sql/Result1.csv ... Result7.csv
python python/Fantasy_Football_Model.py                      # writes python/Outputs/

# Or MySQL
python sql/load_raw_tables.py --host localhost --user root --password *** --database Fantasy_Football_MYSQ
mysql -u root -p Fantasy_Football_MYSQ < sql/Fantasy_Football_MYSQL.sql   # export Query N as Result<N>.csv

python -m pytest tests/
```

| Result | Query |
|---|---|
| 1 | Position summary |
| 2 | Season trends (qualifying seasons) |
| 3 | Multi-season players: per-game average and spread |
| 4 | Positional finish and tier each season |
| 5 | Value over replacement |
| 6 | Consecutive-season pairs (feeds the predictability model) |
| 7 | Complete export |

`python/Outputs/`: `position_predictability.csv`, `vor_summary.csv`, `vor_by_finish.csv`, `target_share_signal.csv`, `consistent_starters.csv`, `top_players.csv`, `season_trends.csv`, plus 5 charts.

## Tools

MySQL / SQLite, Python (pandas, NumPy, SciPy, statsmodels, matplotlib), Tableau Public, pytest.

## Dashboard

Tableau workbook and PDFs are in `tableau/`. *(Public link still to be added. The dashboards were built on the version one numbers, including the RB scoring bug, and need rebuilding from the new Result CSVs.)*

## Audit log

**2026-10-21 audit and rebuild**
- **RB points were not points.** RBs were scored from `YACON_2`, which isn't a points column (Saquon Barkley 2024: 130, against ~355 real PPR points; McCaffrey 2023: 74, against ~391). Every RB number, and every cross-position comparison, was wrong. RBs now use rushing yards × 0.1 + receptions. QB scoring dropped its passer rating × 0.1 term, which no league uses.
- **Committed results didn't come from the committed SQL.** Result4 and Result10 had columns no query produced, Result15 stopped at exactly 1,000 rows (MySQL Workbench's default export limit), and Result-file numbers were off by one from query numbers. `sql/run_sqlite.py` now runs the SQL file on SQLite, writes Result N for Query N, and removes stale files. Three fresh runs were byte-identical.
- **The Python model was rebuilt.** Weekly PPR cutoffs (25/20/12) had been applied to season totals, putting every top-15 player in "Elite". "Steals" were ranked by an end-of-season rank, and "consistency" by raw season totals, so zero-point players ranked most consistent. These are replaced by per-game metrics, positional-finish tiers, value over replacement, and year-over-year predictability with confidence intervals.
- Player names are split from the team suffix (`Josh Allen (BUF)`), because FantasyPros stamps every season with the export-time team; seasons join on name. The two blank trailing rows in every CSV are dropped.
- Corrected counts: 2,663 player-seasons, 517 TE (the page said 2,662 / 516).
- Tests added (`tests/test_pipeline.py`): the full SQL run on SQLite, row counts, scoring checked against hand-computed players, VOR zero at replacement, consecutive-season pairs, the MySQL→SQLite translation, population STDDEV matching MySQL, name parsing, and the predictability model on synthetic data.

**2026-09-16**
1. Nothing created the 20 raw tables the SQL expects; `load_raw_tables.py` was added.
2. All five TE inserts referenced a misspelled table (`fantasypross_te_*`). Fixed.
