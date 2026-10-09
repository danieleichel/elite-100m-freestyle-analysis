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


def correlation_analysis(file_path, label):

    df = pd.read_csv(file_path)

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

    # Pearson correlation
    pearson = (
        sample[variables]
        .corr(method="pearson")
        .round(3)
    )

    print("\nPEARSON CORRELATION MATRIX:")
    print(pearson.to_string())

    # Spearman correlation
    spearman = (
        sample[variables]
        .corr(method="spearman")
        .round(3)
    )

    print("\nSPEARMAN CORRELATION MATRIX:")
    print(spearman.to_string())

    # Focus on correlations with final time
    print("\nCORRELATIONS WITH FINAL TIME:")

    comparison = pd.DataFrame({
        "Pearson": pearson["final_time"],
        "Spearman": spearman["final_time"]
    })

    print(
        comparison
        .sort_values(
            "Pearson",
            ascending=False
        )
        .to_string()
    )


correlation_analysis(
    MEN_FILE,
    "MEN - PRIMARY ELITE SAMPLE"
)

correlation_analysis(
    WOMEN_FILE,
    "WOMEN - PRIMARY ELITE SAMPLE"
)
