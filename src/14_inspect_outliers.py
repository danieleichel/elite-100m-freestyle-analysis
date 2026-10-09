import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MEN_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "men"
    / "all_major_meets_100_free_clean.csv"
)

WOMEN_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "women"
    / "all_major_meets_100_free_clean.csv"
)


def inspect_dataset(file_path, label):

    df = pd.read_csv(file_path)

    print()
    print("=" * 80)
    print(label)
    print("=" * 80)

    # --------------------------------------------------
    # 1. Slowest performances
    # --------------------------------------------------

    print("\n10 SLOWEST VALID TIMES:")

    slowest = (
        df[df["final_time"].notna()]
        .sort_values(
            "final_time",
            ascending=False
        )
        .head(10)
    )

    print(
        slowest[
            [
                "competition_year",
                "meet_name",
                "race_round",
                "swimmer_name",
                "represented_country",
                "first_50",
                "second_50",
                "final_time",
                "dropoff_percent"
            ]
        ].to_string(index=False)
    )

    # --------------------------------------------------
    # 2. Largest pacing dropoff
    # --------------------------------------------------

    print("\n10 LARGEST DROPOFF VALUES:")

    largest_dropoff = (
        df[df["dropoff_percent"].notna()]
        .sort_values(
            "dropoff_percent",
            ascending=False
        )
        .head(10)
    )

    print(
        largest_dropoff[
            [
                "competition_year",
                "meet_name",
                "race_round",
                "swimmer_name",
                "represented_country",
                "first_50",
                "second_50",
                "final_time",
                "dropoff_percent"
            ]
        ].to_string(index=False)
    )

    # --------------------------------------------------
    # 3. Negative dropoff
    # --------------------------------------------------

    print("\nNEGATIVE DROPOFF OBSERVATIONS:")

    negative_dropoff = df[
        df["dropoff_percent"] < 0
    ]

    if len(negative_dropoff) == 0:
        print("None")
    else:
        print(
            negative_dropoff[
                [
                    "competition_year",
                    "meet_name",
                    "race_round",
                    "swimmer_name",
                    "represented_country",
                    "first_50",
                    "second_50",
                    "final_time",
                    "dropoff_percent"
                ]
            ].to_string(index=False)
        )

    # --------------------------------------------------
    # 4. Splits present but final time missing
    # --------------------------------------------------

    print("\nSPLITS PRESENT BUT FINAL TIME MISSING:")

    missing_final = df[
        df["first_50"].notna()
        & df["second_50"].notna()
        & df["final_time"].isna()
    ]

    if len(missing_final) == 0:
        print("None")
    else:
        print(
            missing_final[
                [
                    "competition_year",
                    "meet_name",
                    "race_round",
                    "swimmer_name",
                    "represented_country",
                    "first_50",
                    "second_50",
                    "final_time"
                ]
            ].to_string(index=False)
        )

    print(
        f"\nNumber of these rows: "
        f"{len(missing_final)}"
    )


inspect_dataset(
    MEN_FILE,
    "MEN"
)

inspect_dataset(
    WOMEN_FILE,
    "WOMEN"
)
