# Fantasy Football Draft Value Analysis (2021-2025)

**Business question:** which players provide the most draft value relative to their expected fantasy production, and which positions are predictable enough to draft on data rather than consensus ADP? Full case study framing in `docs/Fantasy_Football_Case_Study.docx`.

## Key finding

Across 2,662 player-season observations (2021-2025), the pipeline ranks each player's season against his position average ("value gained"), groups players into PPR tiers, and flags consistent producers. **What it doesn't do yet:** the `draft_rank` column is FantasyPros' end-of-season rank, not draft position, and there's no ADP dataset in `data/`, so the project can't yet measure value relative to where players were drafted. Adding a historical ADP file and joining on player and season is the next step.

## Pipeline

1. **`load_raw_tables.py`** *(new — see Known limitation below)* — loads the 20 raw FantasyPros CSVs (`data/`) into MySQL under the exact table names `Fantasy_Football_MYSQL.sql` expects.
2. **`Fantasy_Football_MYSQL.sql`** — combines all 20 raw tables into one `fantasy_football_combined` table with position-specific fantasy point approximations, then runs 16 analysis queries (draft value scoring, season trends, tier classification, etc.), exporting `Result1.csv`-`Result16.csv`.
3. **`Fantasy_Football_Model.py`** — reads the 16 result CSVs, classifies players into PPR performance tiers, and produces the charts and analysis CSVs in `python/Outputs/`.

```bash
pip install -r requirements.txt
python "sql/load_raw_tables.py" --host localhost --user root --password *** --database Fantasy_Football_MYSQ
mysql -u root -p Fantasy_Football_MYSQ < "sql/Fantasy_Football_MYSQL.sql"
python "python/Fantasy_Football_Model.py"
```

## Tools

MySQL, Python (pandas, NumPy, SciPy, matplotlib, seaborn), Tableau Public.

## Dashboard

*(Add the public.tableau.com link for `FF_PPR_Player_Production_Analysis`.)*

## Bugs found and fixed while testing this pipeline (2026-09-16)

1. **The pipeline was not actually reproducible from a fresh clone.** Nothing in the repo created the 20 raw `fantasypros_<pos>_<year>` tables that `Fantasy_Football_MYSQL.sql` assumes already exist — they had only ever been imported by hand. Added `load_raw_tables.py` to close that gap.
2. **All five years of tight end data referenced a misspelled table name** (`fantasypross_te_2021` through `_2025` — double "s"), left over from an earlier debugging pass with only the first occurrence flagged as "intentional error, please rename" and never actually fixed. In MySQL this would fail with "table doesn't exist" for every TE insert; since it sits inside a `START TRANSACTION`/`COMMIT` block, depending on how the SQL client handles a failed statement mid-transaction, this could mean tight ends never load at all. Fixed all 5 occurrences and verified against a SQLite-equivalent run of the corrected logic, 3 times, with identical row counts each run (431 QB, 739 RB, 517 TE, 976 WR — 2,663 total).

## Known limitation — disclose this, don't bury it

The source FantasyPros exports have no touchdown data. The SQL scoring formulas are documented approximations: QB = `yards * 0.04 + passer_rating * 0.1`, WR/TE = `yards * 0.1 + receptions`, RB = a pre-calculated PPR column from FantasyPros. **QB/WR/TE and RB point totals are not on the same scale** until touchdown data is added — say this explicitly in any write-up or interview.
