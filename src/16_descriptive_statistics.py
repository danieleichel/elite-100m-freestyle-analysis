import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


MEN_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "men"
    / "men_analysis_sample.csv"
)

WOMEN_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "women"
    / "women_analysis_sample.csv"
)


def describe_primary_sample(file_path, label):

    df = pd.read_csv(file_path)

    # Keep only the primary elite sample
    sample = df[
        df["primary_elite_sample"] == True
    ].copy()

    variables = [
        "final_time",
        "first_50",
        "second_50",
        "dropoff_seconds",
        "dropoff_percent",
        "pacing_ratio",
        "reaction_time",
        "age"
    ]

    print()
    print("=" * 75)
    print(label)
    print("=" * 75)

    print(f"Sample size: {len(sample)}")

    print()
    print("DESCRIPTIVE STATISTICS:")
    print(
        sample[variables]
        .describe()
        .T
        .round(3)
        .to_string()
    )

    print()
    print("OBSERVATIONS BY ROUND:")
    print(
        sample["race_round"]
        .value_counts()
        .to_string()
    )

    print()
    print("OBSERVATIONS BY YEAR:")
    print(
        sample.groupby("competition_year")
        .size()
        .to_string()
    )

    print()
    print("UNIQUE SWIMMERS:")
    print(sample["swimmer_id"].nunique())

    print()
    print("AVERAGE NUMBER OF SWIMS PER SWIMMER:")
    print(
        round(
            len(sample)
            / sample["swimmer_id"].nunique(),
            2
        )
    )


describe_primary_sample(
    MEN_FILE,
    "MEN - PRIMARY ELITE SAMPLE"
)

describe_primary_sample(
    WOMEN_FILE,
    "WOMEN - PRIMARY ELITE SAMPLE"
)
