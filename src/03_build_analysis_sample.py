import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MEN_CLEAN_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "men"
    / "all_major_meets_100_free_clean.csv"
)

WOMEN_CLEAN_FILE = (
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

OUTLIER_OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "analysis_sample_outliers.csv"
)


# ============================================================
# SETTINGS
# ============================================================

VALID_ROUNDS = [
    "Semifinals",
    "Finals"
]

OUTLIER_THRESHOLD = 20.0


# ============================================================
# HELPER FUNCTION
# ============================================================

def build_sample(
    input_file,
    output_file,
    sex_label
):

    df = pd.read_csv(
        input_file
    )

    print()
    print("=" * 80)
    print(sex_label.upper())
    print("=" * 80)

    print(
        f"Clean rows loaded: "
        f"{len(df)}"
    )

    # --------------------------------------------------------
    # Inspect extreme pacing values
    # --------------------------------------------------------

    outliers = df[
        df["dropoff_percent"].notna()
        &
        (
            df["dropoff_percent"].abs()
            > OUTLIER_THRESHOLD
        )
    ].copy()

    if len(outliers) > 0:

        print()
        print(
            f"Potential pacing outliers "
            f"(|dropoff| > {OUTLIER_THRESHOLD}%): "
            f"{len(outliers)}"
        )

        display_columns = [
            column
            for column in [
                "swimmer_name",
                "competition_name",
                "competition_year",
                "race_round",
                "first_50",
                "second_50",
                "final_time",
                "dropoff_percent"
            ]
            if column in outliers.columns
        ]

        print(
            outliers[
                display_columns
            ].to_string(
                index=False
            )
        )

    else:

        print()
        print(
            "No extreme pacing outliers "
            f"above {OUTLIER_THRESHOLD}%."
        )

    # --------------------------------------------------------
    # Define elite semifinal/final sample
    # --------------------------------------------------------

    df[
        "primary_elite_sample"
    ] = (
        df[
            "race_round"
        ].isin(
            VALID_ROUNDS
        )
        &
        df[
            "first_50"
        ].notna()
        &
        df[
            "second_50"
        ].notna()
        &
        df[
            "final_time"
        ].notna()
        &
        df[
            "dropoff_percent"
        ].notna()
    )

    analysis = df[
        df[
            "primary_elite_sample"
        ]
    ].copy()

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print(
        f"Primary analysis rows: "
        f"{len(analysis)}"
    )

    print(
        f"Unique swimmers: "
        f"{analysis['swimmer_id'].nunique()}"
    )

    print()

    print(
        "Rows by round:"
    )

    print(
        analysis[
            "race_round"
        ].value_counts()
    )

    average_swims = (
        len(analysis)
        /
        analysis[
            "swimmer_id"
        ].nunique()
    )

    print()

    print(
        f"Average elite swims per swimmer: "
        f"{average_swims:.2f}"
    )

    # --------------------------------------------------------
    # Save full file with sample flag
    # --------------------------------------------------------

    df.to_csv(
        output_file,
        index=False
    )

    outliers[
        "sex"
    ] = sex_label

    return (
        df,
        analysis,
        outliers
    )


# ============================================================
# RUN MEN
# ============================================================

men_full, men_analysis, men_outliers = (
    build_sample(
        MEN_CLEAN_FILE,
        MEN_OUTPUT,
        "Men"
    )
)


# ============================================================
# RUN WOMEN
# ============================================================

women_full, women_analysis, women_outliers = (
    build_sample(
        WOMEN_CLEAN_FILE,
        WOMEN_OUTPUT,
        "Women"
    )
)


# ============================================================
# SAVE OUTLIER TABLE
# ============================================================

all_outliers = pd.concat(
    [
        men_outliers,
        women_outliers
    ],
    ignore_index=True
)


all_outliers.to_csv(
    OUTLIER_OUTPUT,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 80)
print("ANALYSIS SAMPLE BUILD COMPLETE")
print("=" * 80)

print()

print(
    f"Men analysis rows: "
    f"{len(men_analysis)}"
)

print(
    f"Women analysis rows: "
    f"{len(women_analysis)}"
)

print(
    f"Combined elite swims: "
    f"{len(men_analysis) + len(women_analysis)}"
)

print()

print(
    "Saved files:"
)

print(
    MEN_OUTPUT
)

print(
    WOMEN_OUTPUT
)

print(
    OUTLIER_OUTPUT
)
