import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MEN_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "men"
    / "singapore_2025_100_free.csv"
)

WOMEN_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "women"
    / "singapore_2025_100_free.csv"
)


def validate_file(file_path, label):

    df = pd.read_csv(file_path)

    print(f"\n--- {label} ---")

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nRace rounds:")
    print(df["race_round"].value_counts())

    print("\nMissing values:")
    print(df.isna().sum())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    print("\nUnique swimmers:")
    print(df["swimmer_id"].nunique())

    print("\nFinal time summary:")
    print(df["final_time"].describe())

    print("\nFirst 5 rows:")
    print(df.head())


validate_file(MEN_FILE, "MEN")
validate_file(WOMEN_FILE, "WOMEN")
