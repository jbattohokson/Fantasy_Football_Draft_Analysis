"""End-to-end and unit tests. Runs the real SQL on SQLite in a temp folder.

Run: python -m pytest tests/
"""
import sqlite3
import statistics
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "sql"))
sys.path.insert(0, str(ROOT / "python"))
import load_raw_tables  # noqa: E402
import run_sqlite  # noqa: E402
import Fantasy_Football_Model as model  # noqa: E402


@pytest.fixture(scope="module")
def results(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("ff")
    db = tmp / "ff.db"
    con = sqlite3.connect(db)
    assert load_raw_tables.load_all(con) == 20
    con.commit()
    con.close()
    run_sqlite.run(db, tmp)
    return {key: pd.read_csv(tmp / f) for key, f in model.RESULT_FILES.items()}


def test_every_player_season_loads(results):
    allr = results["all_seasons"]
    assert len(allr) == 2663
    assert allr.groupby("pos").size().to_dict() == {"QB": 431, "RB": 739, "TE": 517, "WR": 976}
    assert not allr.duplicated(["player_name", "pos", "yr"]).any()
    assert allr["player_name"].str.contains(r"\(").sum() == 0  # team suffix split off


def test_scoring_uses_the_same_ppr_scale_at_every_position(results):
    a = results["all_seasons"].set_index(["player_name", "pos", "yr"])
    # Saquon Barkley 2024: 2,005 rush yds, 33 rec -> 233.5 (the old YACON_2 "points" said 130)
    assert a.loc[("Saquon Barkley", "RB", 2024), "pts"] == pytest.approx(200.5 + 33)
    # Josh Allen 2025: 3,668 pass yds * 0.04; no passer-rating term
    assert a.loc[("Josh Allen", "QB", 2025), "pts"] == pytest.approx(3668 * 0.04, abs=0.01)
    wr = a.xs("WR", level="pos")
    assert np.allclose(wr["pts"], (wr["yards"] * 0.1 + wr["rec_count"].fillna(0)).round(2))
    q = a[a["games_played"] > 0]
    assert np.allclose(q["ppg"], (q["pts"] / q["games_played"]).round(2), atol=0.011)


def test_target_share_is_parsed_for_receivers_only(results):
    a = results["all_seasons"]
    assert a.loc[a["pos"].isin(["WR", "TE"]), "target_share"].between(0, 60).all()
    assert a.loc[a["pos"].isin(["QB", "RB"]), "target_share"].isna().all()


def test_replacement_player_has_zero_vor(results):
    v = results["vor"]
    for pos, n in model.STARTERS.items():
        assert (v.loc[(v["pos"] == pos) & (v["pos_finish"] == n), "vor"] == 0).all()


def test_pairs_are_consecutive_qualifying_seasons(results):
    p = results["pairs"]
    assert (p["next_yr"] == p["yr"] + 1).all()
    assert (p["games"] >= 8).all() and (p["next_games"] >= 8).all()


def test_stddev_matches_mysql_population_stddev():
    agg = run_sqlite.PopStdDev()
    for v in [2, 4, 4, 4, 5, 5, 7, 9, None]:
        agg.step(v)
    assert agg.finalize() == pytest.approx(statistics.pstdev([2, 4, 4, 4, 5, 5, 7, 9]))
    assert run_sqlite.PopStdDev().finalize() is None


def test_mysql_translation():
    stmts = run_sqlite.mysql_to_sqlite(
        "USE db;\n-- a comment; with a semicolon\nCREATE TABLE t (a INT,\n  INDEX i (a));\nSTART TRANSACTION;\nSELECT 1;"
    )
    assert stmts == ["CREATE TABLE t (a INT)", "BEGIN", "SELECT 1"]


def test_name_parsing_handles_suffixes_and_no_team(tmp_path):
    csv = tmp_path / "x.csv"
    pd.DataFrame({"Rank": [1, 2, None], "Player": ["Patrick Mahomes II (KC)", "Player Without Team", None],
                  "G": [17, 3, None], "YDS": ["4,183", "10", None]}).to_csv(csv, index=False)
    df = load_raw_tables.read_export(csv)
    assert df["player_name"].tolist() == ["Patrick Mahomes II", "Player Without Team"]
    assert df["team"].tolist()[0] == "KC" and pd.isna(df["team"].tolist()[1])


def test_predictability_on_synthetic_pairs():
    rng = np.random.default_rng(0)
    rows = []
    for pos, noise in [("QB", 3.0), ("RB", 0.5), ("WR", 0.5), ("TE", 0.5)]:
        ppg = rng.uniform(3, 15, 200)
        for i, x in enumerate(ppg):
            rows.append({"player_name": f"{pos}{i}", "pos": pos, "yr": 2023, "ppg": x,
                         "next_ppg": x + rng.normal(0, noise)})
    pairs = pd.DataFrame(rows)
    finishes = pairs[["player_name", "pos", "yr"]].copy()
    finishes["pos_finish"] = pairs.groupby("pos")["ppg"].rank(ascending=False).astype(int)
    pred = model.position_predictability(pairs, finishes).set_index("pos")
    assert pred.loc["WR", "yoy_r"] > 0.95 and pred.loc["QB", "yoy_r"] < pred.loc["WR", "yoy_r"]
    assert pred.loc["QB", "ci_low"] < pred.loc["QB", "yoy_r"] < pred.loc["QB", "ci_high"]
    assert pred.loc["WR", "starter_pairs"] == 36


def test_corr_with_ci_degenerate_input():
    r, lo, hi, n, p = model.corr_with_ci([1, 1, 1, 1, 1], [1, 2, 3, 4, 5])
    assert np.isnan(r) and n == 5
