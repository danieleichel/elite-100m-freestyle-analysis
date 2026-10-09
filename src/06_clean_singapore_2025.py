import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_MEN = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "men"
    / "singapore_2025_100_free.csv"
)

RAW_WOMEN = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "women"
    / "singapore_2025_100_free.csv"
)

PROCESSED_MEN_DIR = PROJECT_ROOT / "data" / "processed" / "men"
PROCESSED_WOMEN_DIR = PROJECT_ROOT / "data" / "processed" / "women"

PROCESSED_MEN_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_WOMEN_DIR.mkdir(parents=True, exist_ok=True)


def swim_time_to_seconds(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if ":" in value:
        minutes, seconds = value.split(":")
        return float(minutes) * 60 + float(seconds)

    try:
        return float(value)
    except ValueError:
        return None


def clean_data(input_file, output_file):

    df = pd.read_csv(input_file)

    # Standard numeric columns
    standard_numeric = [
        "age",
        "lane",
        "place",
        "heat_place",
        "reaction_time"
    ]

    for column in standard_numeric:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Swimming time columns
    time_columns = [
        "first_50",
        "second_50",
        "final_time"
    ]

    for column in time_columns:
        df[column] = df[column].apply(swim_time_to_seconds)

    # Derived pacing variables
    df["dropoff_seconds"] = (
        df["second_50"]
        - df["first_50"]
    )

    df["dropoff_percent"] = (
        (
            df["second_50"]
            - df["first_50"]
        )
        / df["first_50"]
    ) * 100

    df["pacing_ratio"] = (
        df["second_50"]
        / df["first_50"]
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(f"\nSaved cleaned file: {output_file}")
    print(f"Rows: {len(df)}")

    print("\nNon-missing final times:")
    print(df["final_time"].notna().sum())

    print("\nFinal time summary:")
    print(df["final_time"].describe())

    print("\nDropoff percent summary:")
    print(df["dropoff_percent"].describe())


clean_data(
    RAW_MEN,
    PROCESSED_MEN_DIR / "singapore_2025_100_free_clean.csv"
)

clean_data(
    RAW_WOMEN,
    PROCESSED_WOMEN_DIR / "singapore_2025_100_free_clean.csv"
)
