import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MEN_RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "men"
    / "all_major_meets_100_free.csv"
)

WOMEN_RAW_FILE = (
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

VALIDATION_OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "cleaning_validation_summary.csv"
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
    "competition_id",
    "meet_name",
    "competition_year",
    "swimmer_id",
    "swimmer_name",
    "race_round",
    "first_50",
    "second_50",
    "final_time"
]


# ============================================================
# SWIMMING TIME PARSER
# ============================================================

def parse_swim_time(value):

    if pd.isna(value):
        return pd.NA

    text = str(value).strip()

    if text in [
        "",
        "-",
        "nan",
        "None"
    ]:
        return pd.NA

    # Format such as 1:02.45
    if ":" in text:

        try:

            minutes, seconds = (
                text.split(
                    ":",
                    1
                )
            )

            return (
                float(minutes) * 60
                + float(seconds)
            )

        except ValueError:
            return pd.NA

    # Normal seconds format such as 48.72
    try:
        return float(text)

    except ValueError:
        return pd.NA


# ============================================================
# CLEANING FUNCTION
# ============================================================

def clean_dataset(
    input_file,
    output_file,
    sex_label
):

    print()
    print("=" * 80)
    print(sex_label.upper())
    print("=" * 80)

    df = pd.read_csv(
        input_file
    )

    print(
        f"Raw rows loaded: "
        f"{len(df)}"
    )

    # --------------------------------------------------------
    # Validate required columns
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"{sex_label}: missing required columns: "
            f"{missing_columns}"
        )

    # --------------------------------------------------------
    # Parse swimming times correctly
    # --------------------------------------------------------

    for column in [
        "first_50",
        "second_50",
        "final_time"
    ]:

        df[column] = (
            df[column]
            .apply(
                parse_swim_time
            )
        )

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Standard numeric columns
    # --------------------------------------------------------

    numeric_columns = [
        "competition_year",
        "age",
        "lane",
        "place",
        "heat_place",
        "reaction_time"
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # --------------------------------------------------------
    # Exact duplicates
    # --------------------------------------------------------

    exact_duplicates = (
        df.duplicated().sum()
    )

    df = (
        df
        .drop_duplicates()
        .reset_index(
            drop=True
        )
    )

    # --------------------------------------------------------
    # Potential duplicate swims
    # --------------------------------------------------------

    duplicate_key = [
        "competition_id",
        "swimmer_id",
        "race_round"
    ]

    if "lane" in df.columns:

        duplicate_key.append(
            "lane"
        )

    possible_duplicate_swims = (
        df.duplicated(
            subset=duplicate_key,
            keep=False
        ).sum()
    )

    # --------------------------------------------------------
    # Calculate pacing variables
    # --------------------------------------------------------

    df[
        "dropoff_seconds"
    ] = (
        df["second_50"]
        - df["first_50"]
    )

    df[
        "dropoff_percent"
    ] = (
        (
            df["second_50"]
            - df["first_50"]
        )
        /
        df["first_50"]
        * 100
    )

    df[
        "pacing_ratio"
    ] = (
        df["second_50"]
        /
        df["first_50"]
    )

    # --------------------------------------------------------
    # Split consistency
    # --------------------------------------------------------

    df[
        "split_sum"
    ] = (
        df["first_50"]
        + df["second_50"]
    )

    df[
        "split_difference"
    ] = (
        df["final_time"]
        - df["split_sum"]
    )

    df[
        "split_consistency_flag"
    ] = False

    df.loc[
        df["split_difference"].notna()
        &
        (
            df[
                "split_difference"
            ].abs()
            > 0.05
        ),
        "split_consistency_flag"
    ] = True

    # --------------------------------------------------------
    # Plausibility flags
    # --------------------------------------------------------

    df[
        "time_flag"
    ] = False

    df.loc[
        df["final_time"].notna()
        &
        (
            (df["final_time"] < 40)
            |
            (df["final_time"] > 120)
        ),
        "time_flag"
    ] = True

    df[
        "split_flag"
    ] = False

    df.loc[
        df["first_50"].notna()
        &
        (
            (df["first_50"] < 15)
            |
            (df["first_50"] > 60)
        ),
        "split_flag"
    ] = True

    df.loc[
        df["second_50"].notna()
        &
        (
            (df["second_50"] < 15)
            |
            (df["second_50"] > 60)
        ),
        "split_flag"
    ] = True

    # --------------------------------------------------------
    # Complete pacing records
    # --------------------------------------------------------

    complete_pacing = (
        df[
            [
                "first_50",
                "second_50",
                "final_time"
            ]
        ]
        .notna()
        .all(
            axis=1
        )
        .sum()
    )

    # --------------------------------------------------------
    # Print validation
    # --------------------------------------------------------

    print(
        f"Rows after duplicate removal: "
        f"{len(df)}"
    )

    print(
        f"Exact duplicates removed: "
        f"{exact_duplicates}"
    )

    print(
        f"Potential duplicate swims: "
        f"{possible_duplicate_swims}"
    )

    print(
        f"Unique swimmers: "
        f"{df['swimmer_id'].nunique()}"
    )

    print(
        f"Complete pacing records: "
        f"{complete_pacing}"
    )

    print()

    for column in [
        "age",
        "lane",
        "place",
        "heat_place",
        "reaction_time",
        "first_50",
        "second_50",
        "final_time"
    ]:

        print(
            f"Missing {column}: "
            f"{df[column].isna().sum()}"
        )

    print()

    print(
        f"Split consistency flags: "
        f"{df['split_consistency_flag'].sum()}"
    )

    print(
        f"Time plausibility flags: "
        f"{df['time_flag'].sum()}"
    )

    print(
        f"Split plausibility flags: "
        f"{df['split_flag'].sum()}"
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    df.to_csv(
        output_file,
        index=False
    )

    summary = {
        "sex":
            sex_label,

        "rows":
            len(df),

        "unique_swimmers":
            df[
                "swimmer_id"
            ].nunique(),

        "exact_duplicates_removed":
            exact_duplicates,

        "possible_duplicate_swims":
            possible_duplicate_swims,

        "complete_pacing_records":
            complete_pacing,

        "missing_age":
            df["age"].isna().sum(),

        "missing_lane":
            df["lane"].isna().sum(),

        "missing_place":
            df["place"].isna().sum(),

        "missing_heat_place":
            df["heat_place"].isna().sum(),

        "missing_reaction_time":
            df[
                "reaction_time"
            ].isna().sum(),

        "missing_first_50":
            df[
                "first_50"
            ].isna().sum(),

        "missing_second_50":
            df[
                "second_50"
            ].isna().sum(),

        "missing_final_time":
            df[
                "final_time"
            ].isna().sum(),

        "split_consistency_flags":
            df[
                "split_consistency_flag"
            ].sum(),

        "time_flags":
            df[
                "time_flag"
            ].sum(),

        "split_flags":
            df[
                "split_flag"
            ].sum()
    }

    return df, summary


# ============================================================
# MEN
# ============================================================

men_clean, men_summary = clean_dataset(
    MEN_RAW_FILE,
    MEN_OUTPUT,
    "Men"
)


# ============================================================
# WOMEN
# ============================================================

women_clean, women_summary = clean_dataset(
    WOMEN_RAW_FILE,
    WOMEN_OUTPUT,
    "Women"
)


# ============================================================
# SAVE VALIDATION SUMMARY
# ============================================================

validation_df = pd.DataFrame(
    [
        men_summary,
        women_summary
    ]
)


validation_df.to_csv(
    VALIDATION_OUTPUT,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 80)
print("DATA CLEANING COMPLETE")
print("=" * 80)

print()

print(
    "Saved clean files:"
)

print(
    MEN_OUTPUT
)

print(
    WOMEN_OUTPUT
)

print()

print(
    "Validation summary:"
)

print(
    VALIDATION_OUTPUT
)
