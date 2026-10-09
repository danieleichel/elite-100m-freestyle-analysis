import pandas as pd
import statsmodels.formula.api as smf
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


def analyze_trend(file_path, label):

    df = pd.read_csv(file_path)

    sample = df[
        df["primary_elite_sample"] == True
    ].copy()

    # Center year for easier interpretation
    sample["year_centered"] = (
        sample["competition_year"]
        - sample["competition_year"].mean()
    )

    model = smf.ols(
        """
        dropoff_percent ~
        year_centered +
        reaction_time +
        age +
        C(race_round)
        """,
        data=sample
    ).fit()

    print()
    print("=" * 80)
    print(label)
    print("=" * 80)

    print("\nMODEL SUMMARY:")
    print(
        model.summary2().tables[1]
    )

    print("\nKEY MODEL STATISTICS:")
    print(f"R-squared: {model.rsquared:.4f}")
    print(f"Adjusted R-squared: {model.rsquared_adj:.4f}")

    year_beta = model.params["year_centered"]
    year_p = model.pvalues["year_centered"]

    print()
    print(
        f"Estimated annual change in dropoff: "
        f"{year_beta:.4f} percentage points"
    )

    print(
        f"P-value for year trend: "
        f"{year_p:.6f}"
    )

    # Mean dropoff by competition year
    yearly = (
        sample.groupby("competition_year")
        ["dropoff_percent"]
        .agg(["mean", "std", "count"])
        .round(3)
    )

    print()
    print("MEAN DROPOFF BY YEAR:")
    print(yearly.to_string())


analyze_trend(
    MEN_FILE,
    "MEN - PACING TREND OVER TIME"
)

analyze_trend(
    WOMEN_FILE,
    "WOMEN - PACING TREND OVER TIME"
)
