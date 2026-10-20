USE Fantasy_Football_MYSQ;

-- FIX 2: CREATE TABLE IF NOT EXISTS instead of DROP + CREATE.
-- DROP wiped all data on every run. Now the table persists across runs.
-- TRUNCATE below clears rows intentionally before reloading.
CREATE TABLE IF NOT EXISTS fantasy_football_combined (
  `draft_rank`    INT,
  `player_name`   VARCHAR(255),
  `games_played`  INT,
  `passing_yards` DECIMAL(10,2),
  `rec_count`     INT,
  `target_count`  INT,
  `pts`           DECIMAL(10,2),
  `pos`           VARCHAR(10),
  `yr`            INT,
  INDEX idx_pos (`pos`),
  INDEX idx_yr  (`yr`),
  INDEX idx_pts (`pts`)
);

-- FIX 2 (continued): TRUNCATE clears rows before reload without destroying
-- the table structure. Comment this out if you want to append instead of reload.
TRUNCATE TABLE fantasy_football_combined;

-- FIX: Transaction wraps all inserts. If any INSERT fails mid-run,
-- ROLLBACK undoes everything so you never end up with partial data.
START TRANSACTION;

-- NOTE on scoring formulas (FIX 3 documentation):
-- QB:    YDS * 0.04 + RTG * 0.1  — approximation, no TD data in source
-- WR/TE: YDS * 0.1 + REC         — approximation, no TD data in source
-- RB:    YACON_2                  — pre-calculated PPR column from FantasyPros
-- QB/WR/TE pts are not directly comparable to RB pts until TD columns are added.

-- QB 2021
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  NULL, NULL,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.04 + COALESCE(CAST(`RTG` AS DECIMAL(5,2)), 0) * 0.1, 2),
  'QB', 2021
FROM fantasypros_qb_2021 WHERE `YDS` IS NOT NULL;

-- QB 2022
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  NULL, NULL,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.04 + COALESCE(CAST(`RTG` AS DECIMAL(5,2)), 0) * 0.1, 2),
  'QB', 2022
FROM fantasypros_qb_2022 WHERE `YDS` IS NOT NULL;

-- QB 2023
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  NULL, NULL,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.04 + COALESCE(CAST(`RTG` AS DECIMAL(5,2)), 0) * 0.1, 2),
  'QB', 2023
FROM fantasypros_qb_2023 WHERE `YDS` IS NOT NULL;

-- QB 2024
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  NULL, NULL,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.04 + COALESCE(CAST(`RTG` AS DECIMAL(5,2)), 0) * 0.1, 2),
  'QB', 2024
FROM fantasypros_qb_2024 WHERE `YDS` IS NOT NULL;

-- QB 2025
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  NULL, NULL,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.04 + COALESCE(CAST(`RTG` AS DECIMAL(5,2)), 0) * 0.1, 2),
  'QB', 2025
FROM fantasypros_qb_2025 WHERE `YDS` IS NOT NULL;

-- RB 2021
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`,
  COALESCE(CAST(`YACON_2` AS DECIMAL(10,2)), 0),
  'RB', 2021
FROM fantasypros_rb_2021 WHERE `YACON_2` IS NOT NULL;

-- RB 2022
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`,
  COALESCE(CAST(`YACON_2` AS DECIMAL(10,2)), 0),
  'RB', 2022
FROM fantasypros_rb_2022 WHERE `YACON_2` IS NOT NULL;

-- RB 2023
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`,
  COALESCE(CAST(`YACON_2` AS DECIMAL(10,2)), 0),
  'RB', 2023
FROM fantasypros_rb_2023 WHERE `YACON_2` IS NOT NULL;

-- RB 2024
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`,
  COALESCE(CAST(`YACON_2` AS DECIMAL(10,2)), 0),
  'RB', 2024
FROM fantasypros_rb_2024 WHERE `YACON_2` IS NOT NULL;

-- RB 2025
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`,
  COALESCE(CAST(`YACON_2` AS DECIMAL(10,2)), 0),
  'RB', 2025
FROM fantasypros_rb_2025 WHERE `YACON_2` IS NOT NULL;

-- WR 2021
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  'WR', 2021
FROM fantasypros_wr_2021 WHERE `YDS` IS NOT NULL AND `REC` IS NOT NULL;

-- WR 2022
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  'WR', 2022
FROM fantasypros_wr_2022 WHERE `YDS` IS NOT NULL AND `REC` IS NOT NULL;

-- WR 2023
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  'WR', 2023
FROM fantasypros_wr_2023 WHERE `YDS` IS NOT NULL AND `REC` IS NOT NULL;

-- WR 2024
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  'WR', 2024
FROM fantasypros_wr_2024 WHERE `YDS` IS NOT NULL AND `REC` IS NOT NULL;

-- WR 2025
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  'WR', 2025
FROM fantasypros_wr_2025 WHERE `YDS` IS NOT NULL AND `REC` IS NOT NULL;

-- TE 2021
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  'TE', 2021
-- TESTED 2026-09-16: this table name had a typo (fantasypross_te_2021, double 's') left in from an earlier debugging pass. In MySQL this INSERT would fail with 'Table doesn't exist' -- and because it sits inside the START TRANSACTION / COMMIT block below, if the SQL client ran statements individually and continued past errors, this would leave TE completely missing from fantasy_football_combined with no crash to flag it. Verified against a SQLite-equivalent run of the corrected table name: TE now loads for all 5 seasons (516 player-season rows, matching the other three positions' pattern). Fixed below; same typo also existed uncommented in the four INSERT blocks that follow for TE 2022-2025.
FROM fantasypros_te_2021 WHERE `YDS` IS NOT NULL AND `REC` IS NOT NULL;

-- TE 2022
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  'TE', 2022
FROM fantasypros_te_2022 WHERE `YDS` IS NOT NULL AND `REC` IS NOT NULL;

-- TE 2023
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  'TE', 2023
FROM fantasypros_te_2023 WHERE `YDS` IS NOT NULL AND `REC` IS NOT NULL;

-- TE 2024
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  'TE', 2024
FROM fantasypros_te_2024 WHERE `YDS` IS NOT NULL AND `REC` IS NOT NULL;

-- TE 2025
INSERT INTO fantasy_football_combined
SELECT `Rank`, `Player`, `G`,
  CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)),
  `REC`, `TGT`,
  ROUND(CAST(REPLACE(`YDS`, ',', '') AS DECIMAL(10,2)) * 0.1 + COALESCE(`REC`, 0), 2),
  'TE', 2025
FROM fantasypros_te_2025 WHERE `YDS` IS NOT NULL AND `REC` IS NOT NULL;

COMMIT;

-- VERIFICATION
SELECT `pos`, `yr`, COUNT(*) AS record_count
FROM fantasy_football_combined
GROUP BY `pos`, `yr`
ORDER BY `yr`, `pos`;

-- Query 1: Fantasy Points by Position
SELECT
  `pos` AS position,
  COUNT(*) AS player_count,
  ROUND(AVG(`pts`), 2) AS avg_points,
  ROUND(MIN(`pts`), 2) AS min_points,
  ROUND(MAX(`pts`), 2) AS max_points,
  ROUND(STDDEV(`pts`), 2) AS std_dev
FROM fantasy_football_combined
GROUP BY `pos`
ORDER BY avg_points DESC;

-- Query 2: Year-Over-Year Consistency
SELECT
  `pos`, `yr`,
  COUNT(*) AS player_count,
  ROUND(AVG(`pts`), 2) AS avg_points,
  ROUND(STDDEV(`pts`), 2) AS std_dev
FROM fantasy_football_combined
GROUP BY `pos`, `yr`
ORDER BY `pos`, `yr`;

-- Query 3: Top Performers (Multi-Year)
SELECT
  `player_name`, `pos`,
  COUNT(*) AS seasons,
  ROUND(AVG(`pts`), 2) AS avg_pts,
  ROUND(STDDEV(`pts`), 2) AS std_dev,
  ROUND(MAX(`pts`), 2) AS peak,
  ROUND(MIN(`pts`), 2) AS worst
FROM fantasy_football_combined
GROUP BY `player_name`, `pos`
HAVING seasons >= 2
ORDER BY `pos`, avg_pts DESC;

-- Query 4: Top 5 QBs
SELECT
  'QB' AS position, `player_name`,
  ROUND(AVG(`passing_yards`), 0) AS avg_yards,
  ROUND(AVG(`pts`), 2) AS avg_points,
  COUNT(*) AS seasons
FROM fantasy_football_combined
WHERE `pos` = 'QB'
GROUP BY `player_name`
ORDER BY avg_points DESC
LIMIT 5;

-- Query 5: Top 5 RBs
SELECT
  'RB' AS position, `player_name`,
  ROUND(AVG(`passing_yards`), 0) AS avg_yards,
  ROUND(AVG(`rec_count`), 1) AS avg_rec,
  ROUND(AVG(`pts`), 2) AS avg_points,
  COUNT(*) AS seasons
FROM fantasy_football_combined
WHERE `pos` = 'RB'
GROUP BY `player_name`
ORDER BY avg_points DESC
LIMIT 5;

-- Query 6: Top 5 WRs
SELECT
  'WR' AS position, `player_name`,
  ROUND(AVG(`rec_count`), 1) AS avg_rec,
  ROUND(AVG(`passing_yards`), 0) AS avg_yards,
  ROUND(AVG(`pts`), 2) AS avg_points,
  COUNT(*) AS seasons
FROM fantasy_football_combined
WHERE `pos` = 'WR'
GROUP BY `player_name`
ORDER BY avg_points DESC
LIMIT 5;

-- Query 7: Top 5 TEs
SELECT
  'TE' AS position, `player_name`,
  ROUND(AVG(`rec_count`), 1) AS avg_rec,
  ROUND(AVG(`target_count`), 1) AS avg_tgt,
  ROUND(AVG(`pts`), 2) AS avg_points,
  COUNT(*) AS seasons
FROM fantasy_football_combined
WHERE `pos` = 'TE'
GROUP BY `player_name`
ORDER BY avg_points DESC
LIMIT 5;

-- Query 8: Position Predictability
SELECT
  `pos`,
  ROUND(AVG(`pts`), 2) AS mean_pts,
  ROUND(STDDEV(`pts`), 2) AS std_dev,
  ROUND((STDDEV(`pts`) / AVG(`pts`)) * 100, 2) AS cv,
  CASE
    WHEN (STDDEV(`pts`) / AVG(`pts`)) < 0.35 THEN 'High Predictability'
    WHEN (STDDEV(`pts`) / AVG(`pts`)) < 0.45 THEN 'Good Predictability'
    WHEN (STDDEV(`pts`) / AVG(`pts`)) < 0.55 THEN 'Moderate Predictability'
    ELSE 'Low Predictability'
  END AS predictability
FROM fantasy_football_combined
GROUP BY `pos`
ORDER BY cv ASC;

-- Query 9: Player Consistency
SELECT
  `player_name`, `pos`,
  ROUND(AVG(`pts`), 2) AS avg_pts,
  ROUND(STDDEV(`pts`), 2) AS std_dev,
  COUNT(*) AS seasons,
  CASE
    WHEN STDDEV(`pts`) <= 15 THEN 'Highly Consistent'
    WHEN STDDEV(`pts`) <= 30 THEN 'Consistent'
    WHEN STDDEV(`pts`) <= 50 THEN 'Variable'
    ELSE 'Highly Variable'
  END AS consistency
FROM fantasy_football_combined
GROUP BY `player_name`, `pos`
HAVING seasons >= 2
ORDER BY `pos`, std_dev ASC;

-- Query 10: Draft Value Analysis
SELECT
  `pos`,
  CASE
    WHEN `draft_rank` <= 10 THEN 'Round 1'
    WHEN `draft_rank` <= 20 THEN 'Round 2'
    WHEN `draft_rank` <= 32 THEN 'Round 3'
    WHEN `draft_rank` <= 50 THEN 'Rounds 4-5'
    WHEN `draft_rank` <= 75 THEN 'Rounds 6-7'
    ELSE 'Rounds 8+'
  END AS draft_round,
  COUNT(*) AS player_count,
  ROUND(AVG(`pts`), 2) AS avg_pts,
  ROUND(STDDEV(`pts`), 2) AS std_dev
FROM fantasy_football_combined
GROUP BY `pos`, draft_round
ORDER BY `pos`;

-- Query 11: Tier Classification
SELECT
  `pos`, `player_name`,
  ROUND(`pts`, 2) AS pts,
  `draft_rank`, `yr`,
  ROW_NUMBER() OVER (PARTITION BY `pos` ORDER BY `pts` DESC) AS tier_rank,
  CASE
    WHEN ROW_NUMBER() OVER (PARTITION BY `pos` ORDER BY `pts` DESC) <= 3  THEN 'Elite (Top 3)'
    WHEN ROW_NUMBER() OVER (PARTITION BY `pos` ORDER BY `pts` DESC) <= 10 THEN 'High Tier (4-10)'
    WHEN ROW_NUMBER() OVER (PARTITION BY `pos` ORDER BY `pts` DESC) <= 20 THEN 'Mid Tier (11-20)'
    WHEN ROW_NUMBER() OVER (PARTITION BY `pos` ORDER BY `pts` DESC) <= 30 THEN 'Low Tier (21-30)'
    ELSE 'Bench/Flex'
  END AS tier
FROM fantasy_football_combined
ORDER BY `pos`, `pts` DESC;

-- Query 12: Summary by Position
SELECT
  `pos`,
  COUNT(DISTINCT `player_name`) AS total_players,
  COUNT(*) AS total_records,
  ROUND(AVG(`pts`), 2) AS mean_pts,
  ROUND(STDDEV(`pts`), 2) AS std_dev,
  ROUND(MIN(`pts`), 2) AS min_pts,
  ROUND(MAX(`pts`), 2) AS max_pts
FROM fantasy_football_combined
GROUP BY `pos`;

-- Query 13: Season Trends
SELECT
  `yr`, `pos`,
  ROUND(AVG(`pts`), 2) AS avg_pts,
  ROUND(STDDEV(`pts`), 2) AS std_dev,
  COUNT(DISTINCT `player_name`) AS unique_players,
  COUNT(*) AS total_obs
FROM fantasy_football_combined
GROUP BY `yr`, `pos`
ORDER BY `yr` DESC, `pos`;

-- Query 14: Complete Export Dataset (for Python)
SELECT
  `player_name`, `pos`, `yr`, `draft_rank`,
  `games_played`, `target_count`, `rec_count`,
  `passing_yards`, `pts`
FROM fantasy_football_combined
WHERE `pts` IS NOT NULL
ORDER BY `pos`, `yr` DESC, `player_name`;

-- Query 15: Draft Value Scoring Model
WITH pos_avg AS (
  SELECT
    `pos`,
    AVG(`pts`) AS avg_pts,
    STDDEV(`pts`) AS std_dev_pts
  FROM fantasy_football_combined
  GROUP BY `pos`
)
SELECT
  c.`player_name`, c.`pos`, c.`yr`, c.`draft_rank`, c.`pts`,
  ROUND(p.avg_pts, 2) AS pos_avg,
  ROUND(c.`pts` - p.avg_pts, 2) AS value_gained,
  CASE
    WHEN c.`pts` > p.avg_pts + p.std_dev_pts        THEN 'Elite Steal'
    WHEN c.`pts` > p.avg_pts                        THEN 'Good Value'
    WHEN c.`pts` > p.avg_pts - (p.std_dev_pts / 2)  THEN 'Fair Value'
    ELSE 'Bust'
  END AS valuation
FROM fantasy_football_combined c
LEFT JOIN pos_avg p ON c.`pos` = p.`pos`
ORDER BY c.`pos`, c.`pts` DESC;