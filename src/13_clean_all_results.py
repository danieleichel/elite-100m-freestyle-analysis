import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


RAW_MEN = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "men"
    / "all_major_meets_100_free.csv"
)

RAW_WOMEN = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "women"
    / "all_major_meets_100_free.csv"
)


MEN_OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "men"
    / "all_major_meets_100_free_clean.csv"
)

WOMEN_OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "women"
    / "all_major_meets_100_free_clean.csv"
)


MEN_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
WOMEN_OUTPUT.parent.mkdir(parents=True, exist_ok=True)


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


def clean_dataset(input_file, output_file, label):

    df = pd.read_csv(input_file)

    numeric_columns = [
        "competition_year",
        "age",
        "lane",
        "place",
        "heat_place",
        "reaction_time"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    time_columns = [
        "first_50",
        "second_50",
        "final_time"
    ]

    for column in time_columns:
        df[column] = df[column].apply(
            swim_time_to_seconds
        )

    # Core pacing measures
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

    # Useful performance variable
    df["back_half_fraction"] = (
        df["second_50"]
        / df["final_time"]
    )

    # Flag complete race observations
    df["complete_pacing_record"] = (
        df[
            [
                "first_50",
                "second_50",
                "final_time"
            ]
        ]
        .notna()
        .all(axis=1)
    )

    df.to_csv(
        output_file,
        index=False
    )

    print()
    print("=" * 60)
    print(label)
    print("=" * 60)

    print(f"Rows: {len(df)}")
    print(
        "Complete pacing records:",
        df["complete_pacing_record"].sum()
    )

    print()
    print("Final time summary:")
    print(df["final_time"].describe())

    print()
    print("Dropoff percent summary:")
    print(df["dropoff_percent"].describe())

    print()
    print("Rows by round:")
    print(df["race_round"].value_counts())


clean_dataset(
    RAW_MEN,
    MEN_OUTPUT,
    "MEN"
)

clean_dataset(
    RAW_WOMEN,
    WOMEN_OUTPUT,
    "WOMEN"
)
