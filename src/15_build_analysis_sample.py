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


MEN_OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "men"
    / "men_analysis_sample.csv"
)

WOMEN_OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "women"
    / "women_analysis_sample.csv"
)


def build_analysis_sample(input_file, output_file, label):

    df = pd.read_csv(input_file)

    # --------------------------------------------------
    # All valid pacing observations
    # --------------------------------------------------

    df["valid_pacing_sample"] = (
        df["first_50"].notna()
        & df["second_50"].notna()
        & df["final_time"].notna()
    )

    # --------------------------------------------------
    # Primary elite sample
    # Semifinals and finals only
    # --------------------------------------------------

    df["primary_elite_sample"] = (
        df["race_round"].isin(
            ["Semifinals", "Finals"]
        )
        & df["valid_pacing_sample"]
    )

    # --------------------------------------------------
    # Finalists only
    # Useful later as an additional sensitivity analysis
    # --------------------------------------------------

    df["final_only_sample"] = (
        (df["race_round"] == "Finals")
        & df["valid_pacing_sample"]
    )

    df.to_csv(
        output_file,
        index=False
    )

    print()
    print("=" * 60)
    print(label)
    print("=" * 60)

    print(f"Total observations: {len(df)}")

    print(
        "Valid pacing observations:",
        df["valid_pacing_sample"].sum()
    )

    print(
        "Primary elite observations:",
        df["primary_elite_sample"].sum()
    )

    print(
        "Final observations:",
        df["final_only_sample"].sum()
    )

    print()
    print("Primary sample by round:")

    print(
        df[
            df["primary_elite_sample"]
        ]["race_round"]
        .value_counts()
    )


build_analysis_sample(
    MEN_FILE,
    MEN_OUTPUT,
    "MEN"
)

build_analysis_sample(
    WOMEN_FILE,
    WOMEN_OUTPUT,
    "WOMEN"
)
