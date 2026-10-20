"""
load_raw_tables.py

TESTED 2026-09-16: Fantasy_Football_MYSQL.sql assumes 20 raw tables already
exist (fantasypros_qb_2021 ... fantasypros_te_2025) but nothing in this repo
ever created them. Testing the pipeline from a clean checkout surfaced this:
there is no CREATE TABLE or LOAD DATA statement anywhere for the raw tables,
which means the SQL file alone is not reproducible — it silently assumes
someone previously imported all 20 CSVs by hand (e.g. via MySQL Workbench's
Table Data Import Wizard). This script closes that gap: it loads every CSV in
../data/ into MySQL with the exact table names Fantasy_Football_MYSQL.sql
expects, so `python load_raw_tables.py` followed by running the .sql file is
a complete, repeatable pipeline from a fresh clone.

Run this BEFORE Fantasy_Football_MYSQL.sql:
    pip install pandas sqlalchemy pymysql
    python load_raw_tables.py --host localhost --user root --password *** --database Fantasy_Football_MYSQ

Environment variables also work: FF_DB_HOST, FF_DB_USER, FF_DB_PASSWORD, FF_DB_NAME
"""
import argparse
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

POSITIONS = ["QB", "RB", "WR", "TE"]
YEARS = [2021, 2022, 2023, 2024, 2025]
DATASETS_DIR = Path(__file__).resolve().parent.parent / "data"


def main():
    parser = argparse.ArgumentParser(description="Load FantasyPros CSVs into MySQL raw tables.")
    parser.add_argument("--host", default=os.environ.get("FF_DB_HOST", "localhost"))
    parser.add_argument("--user", default=os.environ.get("FF_DB_USER", "root"))
    parser.add_argument("--password", default=os.environ.get("FF_DB_PASSWORD", ""))
    parser.add_argument("--database", default=os.environ.get("FF_DB_NAME", "Fantasy_Football_MYSQ"))
    parser.add_argument("--port", default=os.environ.get("FF_DB_PORT", "3306"))
    args = parser.parse_args()

    conn_str = f"mysql+pymysql://{args.user}:{args.password}@{args.host}:{args.port}/{args.database}"
    engine = create_engine(conn_str)

    loaded, missing = 0, []
    for pos in POSITIONS:
        for yr in YEARS:
            csv_path = DATASETS_DIR / f"FantasyPros_{pos}_{yr}.csv"
            table_name = f"fantasypros_{pos.lower()}_{yr}"
            if not csv_path.exists():
                missing.append(csv_path.name)
                continue
            df = pd.read_csv(csv_path)
            df.to_sql(table_name, engine, if_exists="replace", index=False)
            print(f"  Loaded {csv_path.name} -> {table_name} ({len(df):,} rows)")
            loaded += 1

    print(f"\n{loaded}/20 raw tables loaded.")
    if missing:
        print(f"WARNING: {len(missing)} source CSV(s) not found: {missing}")
    print("Next step: run Fantasy_Football_MYSQL.sql against the same database.")


if __name__ == "__main__":
    main()
