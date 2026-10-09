-- ============================================================
-- 1. Average pacing dropoff by sex and round
-- ============================================================

SELECT
    sex,
    race_round,
    COUNT(*) AS n,
    ROUND(AVG(dropoff_percent), 3) AS avg_dropoff_percent
FROM elite_race_results
GROUP BY
    sex,
    race_round
ORDER BY
    sex,
    race_round;


-- ============================================================
-- 2. Average final time by sex and round
-- ============================================================

SELECT
    sex,
    race_round,
    COUNT(*) AS n,
    ROUND(AVG(final_time), 3) AS avg_final_time
FROM elite_race_results
GROUP BY
    sex,
    race_round
ORDER BY
    sex,
    race_round;


-- ============================================================
-- 3. Fastest elite performances
-- ============================================================

SELECT
    swimmer_name,
    sex,
    competition_year,
    meet_name,
    race_round,
    final_time
FROM elite_race_results
ORDER BY
    final_time ASC
LIMIT 20;


-- ============================================================
-- 4. Swimmers with the most elite race observations
-- ============================================================

SELECT
    swimmer_name,
    sex,
    COUNT(*) AS elite_races
FROM elite_race_results
GROUP BY
    swimmer_id,
    swimmer_name,
    sex
ORDER BY
    elite_races DESC,
    swimmer_name
LIMIT 20;


-- ============================================================
-- 5. Average pacing dropoff by year
-- ============================================================

SELECT
    competition_year,
    sex,
    COUNT(*) AS n,
    ROUND(AVG(dropoff_percent), 3) AS avg_dropoff_percent
FROM elite_race_results
GROUP BY
    competition_year,
    sex
ORDER BY
    competition_year,
    sex;


-- ============================================================
-- 6. Join race results with athlete physical characteristics
-- ============================================================

SELECT
    r.swimmer_name,
    r.sex,
    r.final_time,
    r.first_50,
    r.second_50,
    r.dropoff_percent,
    a.height_cm,
    a.weight_kg
FROM elite_race_results AS r
LEFT JOIN athletes AS a
    ON r.swimmer_id = a.swimmer_id
WHERE
    a.height_cm IS NOT NULL
ORDER BY
    r.final_time ASC
LIMIT 20;
