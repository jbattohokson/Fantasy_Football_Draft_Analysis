"""
load_raw_tables.py

Loads the 20 FantasyPros CSVs in ../data/ into raw tables named
fantasypros_<pos>_<year>, which Fantasy_Football_MYSQL.sql reads.

TESTED 2026-09-16: nothing in the repo used to create these tables; they had
only ever been imported by hand (e.g. MySQL Workbench's import wizard), so the
SQL file alone wasn't reproducible from a fresh clone.

AUDITED 2026-10-21: three changes.
  * --sqlite PATH loads into a SQLite file instead of MySQL, so the whole
    pipeline runs without a database server (see run_sqlite.py).
  * Player is "Name (TEAM)". FantasyPros labels every season with the team at
    export time (Tyreek Hill shows as "(FA)" in 2023), so the suffix is split
    into player_name / team here, and seasons join on player_name.
  * The two blank trailing rows in every export are dropped.

MySQL:
    pip install pandas sqlalchemy pymysql
    python load_raw_tables.py --host localhost --user root --password *** --database Fantasy_Football_MYSQ
    Environment variables also work: FF_DB_HOST, FF_DB_USER, FF_DB_PASSWORD, FF_DB_NAME

SQLite (no server):
    python load_raw_tables.py --sqlite fantasy_football.db
"""
import argparse
import os
import sqlite3
from pathlib import Path

import pandas as pd

POSITIONS = ["QB", "RB", "WR", "TE"]
YEARS = [2021, 2022, 2023, 2024, 2025]
DATASETS_DIR = Path(__file__).resolve().parent.parent / "data"

_NAME_TEAM = r"^(?P<player_name>.*?)\s*\((?P<team>[A-Z]{2,3})\)\s*$"


def read_export(csv_path: Path) -> pd.DataFrame:
    """One FantasyPros export, with blank rows dropped and Player split into name/team."""
    df = pd.read_csv(csv_path)
    df = df[df["Player"].notna()].copy()
    parts = df["Player"].str.extract(_NAME_TEAM)
    df["player_name"] = parts["player_name"].fillna(df["Player"]).str.strip()
    df["team"] = parts["team"]
    return df


def load_all(con) -> int:
    """Write every export to `con` (a SQLAlchemy engine or sqlite3 connection). Returns tables loaded."""
    loaded, missing = 0, []
    for pos in POSITIONS:
        for yr in YEARS:
            csv_path = DATASETS_DIR / f"FantasyPros_{pos}_{yr}.csv"
            table_name = f"fantasypros_{pos.lower()}_{yr}"
            if not csv_path.exists():
                missing.append(csv_path.name)
                continue
            df = read_export(csv_path)
            df.to_sql(table_name, con, if_exists="replace", index=False)
            print(f"  Loaded {csv_path.name} -> {table_name} ({len(df):,} rows)")
            loaded += 1
    print(f"\n{loaded}/20 raw tables loaded.")
    if missing:
        print(f"WARNING: {len(missing)} source CSV(s) not found: {missing}")
    return loaded


def main():
    parser = argparse.ArgumentParser(description="Load FantasyPros CSVs into raw tables (MySQL or SQLite).")
    parser.add_argument("--sqlite", help="Path to a SQLite file. If set, MySQL options are ignored.")
    parser.add_argument("--host", default=os.environ.get("FF_DB_HOST", "localhost"))
    parser.add_argument("--user", default=os.environ.get("FF_DB_USER", "root"))
    parser.add_argument("--password", default=os.environ.get("FF_DB_PASSWORD", ""))
    parser.add_argument("--database", default=os.environ.get("FF_DB_NAME", "Fantasy_Football_MYSQ"))
    parser.add_argument("--port", default=os.environ.get("FF_DB_PORT", "3306"))
    args = parser.parse_args()

    if args.sqlite:
        con = sqlite3.connect(args.sqlite)
        load_all(con)
        con.commit()
        con.close()
        print("Next step: python run_sqlite.py")
        return

    from sqlalchemy import create_engine
    engine = create_engine(
        f"mysql+pymysql://{args.user}:{args.password}@{args.host}:{args.port}/{args.database}"
    )
    load_all(engine)
    print("Next step: run Fantasy_Football_MYSQL.sql against the same database.")


if __name__ == "__main__":
    main()
