import pandas as pd
from pathlib import Path
from scipy.stats import pearsonr, spearmanr


# ============================================================
# PATHS
# ============================================================

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

DESCRIPTIVE_OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "descriptive_statistics.csv"
)

ROUND_OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "descriptive_statistics_by_round.csv"
)

CORRELATION_OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "correlation_analysis.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

men = pd.read_csv(
    MEN_FILE
)

women = pd.read_csv(
    WOMEN_FILE
)

men["sex"] = "Men"
women["sex"] = "Women"

df = pd.concat(
    [men, women],
    ignore_index=True
)


if "primary_elite_sample" in df.columns:

    df = df[
        df["primary_elite_sample"] == True
    ].copy()


print("=" * 80)
print("DESCRIPTIVE AND CORRELATION ANALYSIS")
print("=" * 80)

print(
    f"Total elite swims: "
    f"{len(df)}"
)

print(
    f"Unique swimmers: "
    f"{df['swimmer_id'].nunique()}"
)

print()


# ============================================================
# STEP 1
# DESCRIPTIVE STATISTICS
# ============================================================

print("=" * 80)
print("STEP 1 - DESCRIPTIVE STATISTICS")
print("=" * 80)


variables = [
    "final_time",
    "first_50",
    "second_50",
    "dropoff_seconds",
    "dropoff_percent",
    "reaction_time",
    "age"
]


descriptive_results = []


for sex in [
    "Men",
    "Women"
]:

    print()
    print(
        sex.upper()
    )
    print("-" * 80)

    sex_data = df[
        df["sex"] == sex
    ].copy()

    for variable in variables:

        if variable not in sex_data.columns:
            continue

        series = (
            sex_data[
                variable
            ]
            .dropna()
        )

        if len(series) == 0:
            continue

        result = {
            "sex":
                sex,

            "variable":
                variable,

            "n":
                len(series),

            "mean":
                series.mean(),

            "std":
                series.std(
                    ddof=1
                ),

            "min":
                series.min(),

            "q25":
                series.quantile(
                    0.25
                ),

            "median":
                series.median(),

            "q75":
                series.quantile(
                    0.75
                ),

            "max":
                series.max()
        }

        descriptive_results.append(
            result
        )

        print(
            f"{variable:20s} "
            f"n={len(series):3d}  "
            f"mean={series.mean():.4f}  "
            f"sd={series.std(ddof=1):.4f}"
        )


descriptive_df = pd.DataFrame(
    descriptive_results
)


descriptive_df.to_csv(
    DESCRIPTIVE_OUTPUT,
    index=False
)


print()


# ============================================================
# STEP 2
# DESCRIPTIVE STATISTICS BY ROUND
# ============================================================

print("=" * 80)
print("STEP 2 - DESCRIPTIVES BY ROUND")
print("=" * 80)


round_results = []


for sex in [
    "Men",
    "Women"
]:

    for race_round in [
        "Semifinals",
        "Finals"
    ]:

        subset = df[
            (
                df["sex"] == sex
            )
            &
            (
                df["race_round"] == race_round
            )
        ].copy()

        if len(subset) == 0:
            continue

        for variable in [
            "final_time",
            "first_50",
            "second_50",
            "dropoff_percent"
        ]:

            series = (
                subset[
                    variable
                ]
                .dropna()
            )

            if len(series) == 0:
                continue

            round_results.append({
                "sex":
                    sex,

                "race_round":
                    race_round,

                "variable":
                    variable,

                "n":
                    len(series),

                "mean":
                    series.mean(),

                "std":
                    series.std(
                        ddof=1
                    ),

                "median":
                    series.median()
            })


round_df = pd.DataFrame(
    round_results
)


round_df.to_csv(
    ROUND_OUTPUT,
    index=False
)


print(
    round_df.to_string(
        index=False
    )
)


print()


# ============================================================
# STEP 3
# CORRELATION ANALYSIS
# ============================================================

print("=" * 80)
print("STEP 3 - CORRELATION ANALYSIS")
print("=" * 80)


correlation_variables = [
    "first_50",
    "second_50",
    "dropoff_seconds",
    "dropoff_percent",
    "reaction_time",
    "age"
]


correlation_results = []


for sex in [
    "Men",
    "Women"
]:

    print()
    print(
        sex.upper()
    )
    print("-" * 80)

    sex_data = df[
        df["sex"] == sex
    ].copy()

    for variable in (
        correlation_variables
    ):

        if variable not in sex_data.columns:
            continue

        subset = (
            sex_data[[
                "final_time",
                variable
            ]]
            .dropna()
        )

        if len(subset) < 5:
            continue

        pearson_r, pearson_p = pearsonr(
            subset[
                variable
            ],
            subset[
                "final_time"
            ]
        )

        spearman_r, spearman_p = (
            spearmanr(
                subset[
                    variable
                ],
                subset[
                    "final_time"
                ]
            )
        )

        correlation_results.append({
            "sex":
                sex,

            "variable":
                variable,

            "n":
                len(subset),

            "pearson_r":
                pearson_r,

            "pearson_p":
                pearson_p,

            "spearman_r":
                spearman_r,

            "spearman_p":
                spearman_p
        })

        print(
            f"{variable:20s} "
            f"n={len(subset):3d}  "
            f"Pearson r={pearson_r:+.3f}  "
            f"p={pearson_p:.4f}"
        )


correlation_df = pd.DataFrame(
    correlation_results
)


correlation_df.to_csv(
    CORRELATION_OUTPUT,
    index=False
)


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 80)
print("DESCRIPTIVE ANALYSIS COMPLETE")
print("=" * 80)

print()

print(
    "Saved tables:"
)

print(
    DESCRIPTIVE_OUTPUT
)

print(
    ROUND_OUTPUT
)

print(
    CORRELATION_OUTPUT
)
