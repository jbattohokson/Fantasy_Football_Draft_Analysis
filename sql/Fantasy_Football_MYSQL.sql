USE Fantasy_Football_MYSQ;

-- =============================================================================
-- Fantasy_Football_MYSQL.sql
--
-- Combines the 20 raw FantasyPros tables (loaded by load_raw_tables.py) into
-- one player-season table, then runs the analysis queries. Result<N>.csv in
-- this folder is the output of Query <N>. run_sqlite.py runs this same file
-- against SQLite and writes those CSVs, so no MySQL server is needed.
--
-- SCORING (AUDITED 2026-10-21)
-- The source files are FantasyPros *advanced* stat exports: no touchdowns, no
-- QB rushing, no RB receiving yards. Every position is now scored on the same
-- PPR scale from the columns that exist ("PPR without touchdowns"):
--   QB      passing yards * 0.04
--   RB      rushing yards * 0.1 + receptions
--   WR/TE   receiving yards * 0.1 + receptions
-- Previously RB points were the YACON_2 column, which is not a points column
-- (Saquon Barkley 2024 = 130, against ~355 real PPR points), and QB points
-- added passer rating * 0.1, which no league scores.
-- Totals are still well below real PPR, and QB and RB are missing a scoring
-- component each, so compare players WITHIN a position, not across positions.
--
-- season_rank is the row order of the FantasyPros export (sorted by yards). It
-- is NOT draft position; the old column name draft_rank implied it was.
-- =============================================================================

DROP TABLE IF EXISTS fantasy_football_combined;

CREATE TABLE fantasy_football_combined (
  `season_rank`   INT,
  `player_name`   VARCHAR(255),
  `team`          VARCHAR(10),
  `games_played`  INT,
  `yards`         DECIMAL(10,2),
  `rec_count`     INT,
  `target_count`  INT,
  `target_share`  DECIMAL(5,2),
  `pts`           DECIMAL(10,2),
  `ppg`           DECIMAL(10,2),
  `pos`           VARCHAR(10),
  `yr`            INT,
  INDEX idx_pos (`pos`),
  INDEX idx_yr  (`yr`),
  INDEX idx_player (`player_name`)
);

-- One transaction for all 20 inserts, so a failure leaves no partial table.
START TRANSACTION;

-- QB 2021
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  NULL, NULL, NULL,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.04, 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.04, 2) / NULLIF(`G`, 0), 2),
  'QB', 2021
FROM fantasypros_qb_2021 WHERE `YDS` IS NOT NULL;

-- QB 2022
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  NULL, NULL, NULL,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.04, 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.04, 2) / NULLIF(`G`, 0), 2),
  'QB', 2022
FROM fantasypros_qb_2022 WHERE `YDS` IS NOT NULL;

-- QB 2023
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  NULL, NULL, NULL,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.04, 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.04, 2) / NULLIF(`G`, 0), 2),
  'QB', 2023
FROM fantasypros_qb_2023 WHERE `YDS` IS NOT NULL;

-- QB 2024
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  NULL, NULL, NULL,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.04, 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.04, 2) / NULLIF(`G`, 0), 2),
  'QB', 2024
FROM fantasypros_qb_2024 WHERE `YDS` IS NOT NULL;

-- QB 2025
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  NULL, NULL, NULL,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.04, 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.04, 2) / NULLIF(`G`, 0), 2),
  'QB', 2025
FROM fantasypros_qb_2025 WHERE `YDS` IS NOT NULL;

-- RB 2021
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`, NULL,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2) / NULLIF(`G`, 0), 2),
  'RB', 2021
FROM fantasypros_rb_2021 WHERE `YDS` IS NOT NULL;

-- RB 2022
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`, NULL,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2) / NULLIF(`G`, 0), 2),
  'RB', 2022
FROM fantasypros_rb_2022 WHERE `YDS` IS NOT NULL;

-- RB 2023
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`, NULL,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2) / NULLIF(`G`, 0), 2),
  'RB', 2023
FROM fantasypros_rb_2023 WHERE `YDS` IS NOT NULL;

-- RB 2024
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`, NULL,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2) / NULLIF(`G`, 0), 2),
  'RB', 2024
FROM fantasypros_rb_2024 WHERE `YDS` IS NOT NULL;

-- RB 2025
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`, NULL,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2) / NULLIF(`G`, 0), 2),
  'RB', 2025
FROM fantasypros_rb_2025 WHERE `YDS` IS NOT NULL;

-- WR 2021
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`, CAST(REPLACE(`PCT__TM`, '%', '') AS DECIMAL(5,2)),
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2) / NULLIF(`G`, 0), 2),
  'WR', 2021
FROM fantasypros_wr_2021 WHERE `YDS` IS NOT NULL;

-- WR 2022
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`, CAST(REPLACE(`PCT__TM`, '%', '') AS DECIMAL(5,2)),
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2) / NULLIF(`G`, 0), 2),
  'WR', 2022
FROM fantasypros_wr_2022 WHERE `YDS` IS NOT NULL;

-- WR 2023
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`, CAST(REPLACE(`PCT__TM`, '%', '') AS DECIMAL(5,2)),
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2) / NULLIF(`G`, 0), 2),
  'WR', 2023
FROM fantasypros_wr_2023 WHERE `YDS` IS NOT NULL;

-- WR 2024
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`, CAST(REPLACE(`PCT__TM`, '%', '') AS DECIMAL(5,2)),
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2) / NULLIF(`G`, 0), 2),
  'WR', 2024
FROM fantasypros_wr_2024 WHERE `YDS` IS NOT NULL;

-- WR 2025
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`, CAST(REPLACE(`PCT__TM`, '%', '') AS DECIMAL(5,2)),
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2) / NULLIF(`G`, 0), 2),
  'WR', 2025
FROM fantasypros_wr_2025 WHERE `YDS` IS NOT NULL;

-- TE 2021
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`, CAST(REPLACE(`PCT__TM`, '%', '') AS DECIMAL(5,2)),
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2) / NULLIF(`G`, 0), 2),
  'TE', 2021
FROM fantasypros_te_2021 WHERE `YDS` IS NOT NULL;

-- TE 2022
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`, CAST(REPLACE(`PCT__TM`, '%', '') AS DECIMAL(5,2)),
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2) / NULLIF(`G`, 0), 2),
  'TE', 2022
FROM fantasypros_te_2022 WHERE `YDS` IS NOT NULL;

-- TE 2023
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`, CAST(REPLACE(`PCT__TM`, '%', '') AS DECIMAL(5,2)),
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2) / NULLIF(`G`, 0), 2),
  'TE', 2023
FROM fantasypros_te_2023 WHERE `YDS` IS NOT NULL;

-- TE 2024
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`, CAST(REPLACE(`PCT__TM`, '%', '') AS DECIMAL(5,2)),
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2) / NULLIF(`G`, 0), 2),
  'TE', 2024
FROM fantasypros_te_2024 WHERE `YDS` IS NOT NULL;

-- TE 2025
INSERT INTO fantasy_football_combined
SELECT `Rank`, `player_name`, `team`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`, CAST(REPLACE(`PCT__TM`, '%', '') AS DECIMAL(5,2)),
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  ROUND(ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2) / NULLIF(`G`, 0), 2),
  'TE', 2025
FROM fantasypros_te_2025 WHERE `YDS` IS NOT NULL;

COMMIT;

-- Qualifying season: enough games that per-game numbers mean something.
-- 8 games = about half a 17-game season.

-- Query 1: Position summary
SELECT
  `pos`,
  COUNT(*)                                        AS player_seasons,
  COUNT(DISTINCT `player_name`)                   AS players,
  SUM(CASE WHEN `games_played` >= 8 THEN 1 ELSE 0 END) AS qualifying_seasons,
  ROUND(AVG(`pts`), 2)                            AS avg_pts,
  ROUND(AVG(CASE WHEN `games_played` >= 8 THEN `ppg` END), 2) AS avg_ppg_qualifying,
  ROUND(MAX(`pts`), 2)                            AS max_pts,
  ROUND(STDDEV(`pts`), 2)                         AS std_pts
FROM fantasy_football_combined
GROUP BY `pos`
ORDER BY `pos`;

-- Query 2: Season trends (qualifying seasons only)
SELECT
  `yr`, `pos`,
  COUNT(*)                 AS qualifying_seasons,
  ROUND(AVG(`ppg`), 2)     AS avg_ppg,
  ROUND(STDDEV(`ppg`), 2)  AS std_ppg
FROM fantasy_football_combined
WHERE `games_played` >= 8
GROUP BY `yr`, `pos`
ORDER BY `pos`, `yr`;

-- Query 3: Multi-season players (2+ qualifying seasons), per-game production
-- and spread. Replaces the old "consistency" ranking, which used raw season
-- totals and ranked players who scored 0 every year as the most consistent.
SELECT
  `player_name`, `pos`,
  COUNT(*)                                   AS seasons,
  ROUND(AVG(`ppg`), 2)                       AS avg_ppg,
  ROUND(STDDEV(`ppg`), 2)                    AS std_ppg,
  ROUND(STDDEV(`ppg`) / NULLIF(AVG(`ppg`), 0), 3) AS cv_ppg,
  ROUND(MAX(`ppg`), 2)                       AS best_ppg,
  ROUND(MIN(`ppg`), 2)                       AS worst_ppg
FROM fantasy_football_combined
WHERE `games_played` >= 8
GROUP BY `player_name`, `pos`
HAVING seasons >= 2
ORDER BY `pos`, avg_ppg DESC;

-- Query 4: Positional finish each season (QB1, RB12, ...) and the standard
-- 12-team starter tiers: QB/TE top 12, RB top 24, WR top 36 (incl. flex).
WITH ranked AS (
  SELECT c.*,
    ROW_NUMBER() OVER (PARTITION BY `pos`, `yr` ORDER BY `pts` DESC, `player_name`) AS pos_finish
  FROM fantasy_football_combined c
)
SELECT
  `player_name`, `pos`, `yr`, `games_played`, `pts`, `ppg`, pos_finish,
  CASE
    WHEN pos_finish <= CASE `pos` WHEN 'RB' THEN 12 WHEN 'WR' THEN 12 ELSE 6 END THEN 'Elite starter'
    WHEN pos_finish <= CASE `pos` WHEN 'RB' THEN 24 WHEN 'WR' THEN 36 ELSE 12 END THEN 'Starter'
    WHEN pos_finish <= CASE `pos` WHEN 'RB' THEN 36 WHEN 'WR' THEN 48 ELSE 18 END THEN 'Bench depth'
    ELSE 'Replacement level'
  END AS tier
FROM ranked
ORDER BY `pos`, `yr`, pos_finish;

-- Query 5: Value over replacement (VOR) per season. Replacement = the last
-- starter at each position in a 12-team league (QB12, RB24, WR36, TE12).
WITH ranked AS (
  SELECT c.*,
    ROW_NUMBER() OVER (PARTITION BY `pos`, `yr` ORDER BY `pts` DESC, `player_name`) AS pos_finish
  FROM fantasy_football_combined c
),
replacement AS (
  SELECT `pos`, `yr`, `pts` AS replacement_pts
  FROM ranked
  WHERE pos_finish = CASE `pos` WHEN 'RB' THEN 24 WHEN 'WR' THEN 36 ELSE 12 END
)
SELECT
  r.`player_name`, r.`pos`, r.`yr`, r.pos_finish, r.`pts`,
  p.replacement_pts,
  ROUND(r.`pts` - p.replacement_pts, 2) AS vor
FROM ranked r
JOIN replacement p ON r.`pos` = p.`pos` AND r.`yr` = p.`yr`
ORDER BY r.`pos`, r.`yr`, r.pos_finish;

-- Query 6: Season-to-season pairs. One row per player with qualifying seasons
-- in consecutive years. The Python model turns these into year-over-year
-- correlations by position ("how predictable is this position?").
SELECT
  a.`player_name`, a.`pos`, a.`yr` AS yr, b.`yr` AS next_yr,
  a.`ppg` AS ppg, b.`ppg` AS next_ppg,
  a.`target_share` AS target_share, b.`target_share` AS next_target_share,
  a.`target_count` AS targets, a.`games_played` AS games, b.`games_played` AS next_games
FROM fantasy_football_combined a
JOIN fantasy_football_combined b
  ON a.`player_name` = b.`player_name` AND a.`pos` = b.`pos` AND b.`yr` = a.`yr` + 1
WHERE a.`games_played` >= 8 AND b.`games_played` >= 8
ORDER BY a.`pos`, a.`player_name`, a.`yr`;

-- Query 7: Complete export (every player-season, no row limit)
SELECT
  `player_name`, `team`, `pos`, `yr`, `season_rank`, `games_played`,
  `yards`, `rec_count`, `target_count`, `target_share`, `pts`, `ppg`
FROM fantasy_football_combined
ORDER BY `pos`, `yr`, `season_rank`;
