import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MEN_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "men"
    / "all_major_meets_100_free.csv"
)

WOMEN_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "women"
    / "all_major_meets_100_free.csv"
)


def validate_dataset(file_path, label):

    df = pd.read_csv(file_path)

    print()
    print("=" * 70)
    print(label)
    print("=" * 70)

    print(f"Total rows: {len(df)}")
    print(f"Unique swimmers: {df['swimmer_id'].nunique()}")
    print(f"Competitions: {df['competition_id'].nunique()}")

    print()
    print("ROWS BY YEAR:")
    print(
        df.groupby("competition_year")
        .size()
        .to_string()
    )

    print()
    print("ROWS BY MEET:")
    print(
        df.groupby(
            ["competition_year", "meet_name"]
        )
        .size()
        .to_string()
    )

    print()
    print("ROWS BY ROUND:")
    print(
        df["race_round"]
        .value_counts(dropna=False)
        .to_string()
    )

    print()
    print("MISSING VALUES:")
    print(
        df.isna()
        .sum()
        .to_string()
    )

    print()
    print("EXACT DUPLICATE ROWS:")
    print(df.duplicated().sum())

    print()
    print("DUPLICATE SWIM CHECK:")

    duplicate_swims = df.duplicated(
        subset=[
            "competition_id",
            "swimmer_id",
            "race_round",
            "final_time"
        ],
        keep=False
    )

    print(
        f"Potential duplicate swims: "
        f"{duplicate_swims.sum()}"
    )

    print()
    print("UNUSUAL ROUND NAMES:")

    valid_rounds = [
        "Heats",
        "Semifinals",
        "Finals"
    ]

    unusual = df[
        ~df["race_round"].isin(valid_rounds)
    ]["race_round"].value_counts(dropna=False)

    if len(unusual) == 0:
        print("None")
    else:
        print(unusual.to_string())

    print()
    print("FINAL TIME EXAMPLES:")
    print(df["final_time"].head(15).to_string(index=False))


validate_dataset(
    MEN_FILE,
    "MEN'S 100M FREESTYLE"
)

validate_dataset(
    WOMEN_FILE,
    "WOMEN'S 100M FREESTYLE"
)
