import sqlite3
from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_FILE = (
    PROJECT_ROOT
    / "data"
    / "swimming_analysis.db"
)

MEN_ANALYSIS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "men"
    / "men_analysis_sample.csv"
)

WOMEN_ANALYSIS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "women"
    / "women_analysis_sample.csv"
)

PHYSICAL_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "athlete_master_physical_clean.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

men = pd.read_csv(
    MEN_ANALYSIS_FILE
)

women = pd.read_csv(
    WOMEN_ANALYSIS_FILE
)

race_results = pd.concat(
    [
        men,
        women
    ],
    ignore_index=True
)

athletes = pd.read_csv(
    PHYSICAL_FILE
)


# ============================================================
# BUILD SQLITE DATABASE
# ============================================================

DATABASE_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

connection = sqlite3.connect(
    DATABASE_FILE
)

cursor = connection.cursor()


# ============================================================
# WRITE TABLES
# ============================================================

race_results.to_sql(
    "race_results",
    connection,
    if_exists="replace",
    index=False
)

athletes.to_sql(
    "athletes",
    connection,
    if_exists="replace",
    index=False
)


# ============================================================
# CREATE INDEXES
# ============================================================

cursor.execute(
    """
    CREATE INDEX IF NOT EXISTS
    idx_race_results_swimmer_id
    ON race_results(swimmer_id)
    """
)

cursor.execute(
    """
    CREATE INDEX IF NOT EXISTS
    idx_race_results_year
    ON race_results(competition_year)
    """
)

cursor.execute(
    """
    CREATE INDEX IF NOT EXISTS
    idx_race_results_round
    ON race_results(race_round)
    """
)

cursor.execute(
    """
    CREATE INDEX IF NOT EXISTS
    idx_race_results_sex
    ON race_results(sex)
    """
)

cursor.execute(
    """
    CREATE INDEX IF NOT EXISTS
    idx_athletes_swimmer_id
    ON athletes(swimmer_id)
    """
)


# ============================================================
# CREATE ELITE ANALYSIS VIEW
# ============================================================

cursor.execute(
    """
    DROP VIEW IF EXISTS elite_race_results
    """
)

cursor.execute(
    """
    CREATE VIEW elite_race_results AS
    SELECT *
    FROM race_results
    WHERE primary_elite_sample = 1
    """
)


connection.commit()


# ============================================================
# VALIDATION
# ============================================================

race_count = cursor.execute(
    """
    SELECT COUNT(*)
    FROM race_results
    """
).fetchone()[0]


male_races = cursor.execute(
    """
    SELECT COUNT(*)
    FROM race_results
    WHERE sex = 'Men'
    """
).fetchone()[0]


female_races = cursor.execute(
    """
    SELECT COUNT(*)
    FROM race_results
    WHERE sex = 'Women'
    """
).fetchone()[0]


elite_count = cursor.execute(
    """
    SELECT COUNT(*)
    FROM elite_race_results
    """
).fetchone()[0]


elite_men = cursor.execute(
    """
    SELECT COUNT(*)
    FROM elite_race_results
    WHERE sex = 'Men'
    """
).fetchone()[0]


elite_women = cursor.execute(
    """
    SELECT COUNT(*)
    FROM elite_race_results
    WHERE sex = 'Women'
    """
).fetchone()[0]


athlete_count = cursor.execute(
    """
    SELECT COUNT(*)
    FROM athletes
    """
).fetchone()[0]


# ============================================================
# PRINT SUMMARY
# ============================================================

print("=" * 80)
print("SQLITE DATABASE CREATED")
print("=" * 80)

print(
    f"Database: "
    f"{DATABASE_FILE}"
)

print()

print(
    f"All race observations: "
    f"{race_count}"
)

print(
    f"Men: "
    f"{male_races}"
)

print(
    f"Women: "
    f"{female_races}"
)

print()

print(
    f"Elite race observations: "
    f"{elite_count}"
)

print(
    f"Elite men: "
    f"{elite_men}"
)

print(
    f"Elite women: "
    f"{elite_women}"
)

print()

print(
    f"Athletes: "
    f"{athlete_count}"
)


# ============================================================
# SHOW DATABASE OBJECTS
# ============================================================

print()
print("Tables:")

tables = cursor.execute(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
    """
).fetchall()

for table in tables:
    print(
        f"- {table[0]}"
    )


print()
print("Views:")

views = cursor.execute(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'view'
    ORDER BY name
    """
).fetchall()

for view in views:
    print(
        f"- {view[0]}"
    )


# ============================================================
# CLOSE CONNECTION
# ============================================================

connection.close()
