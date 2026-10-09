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


def cluster_analysis(file_path, label):

    df = pd.read_csv(file_path)

    sample = df[
        df["primary_elite_sample"] == True
    ].copy()

    sample["year_centered"] = (
        sample["competition_year"]
        - sample["competition_year"].mean()
    )

    sample = sample.dropna(
        subset=[
            "dropoff_percent",
            "reaction_time",
            "age",
            "race_round",
            "swimmer_id"
        ]
    )

    # Standard OLS
    ols_model = smf.ols(
        """
        dropoff_percent ~
        year_centered +
        reaction_time +
        age +
        C(race_round)
        """,
        data=sample
    ).fit()

    # Same regression, but standard errors clustered by swimmer
    clustered_model = smf.ols(
        """
        dropoff_percent ~
        year_centered +
        reaction_time +
        age +
        C(race_round)
        """,
        data=sample
    ).fit(
        cov_type="cluster",
        cov_kwds={
            "groups": sample["swimmer_id"]
        }
    )

    print()
    print("=" * 80)
    print(label)
    print("=" * 80)

    variables = [
        "year_centered",
        "reaction_time",
        "age",
        "C(race_round)[T.Semifinals]"
    ]

    results = []

    for variable in variables:

        results.append({
            "variable": variable,

            "ols_coef":
                ols_model.params[variable],

            "ols_se":
                ols_model.bse[variable],

            "ols_p":
                ols_model.pvalues[variable],

            "cluster_coef":
                clustered_model.params[variable],

            "cluster_se":
                clustered_model.bse[variable],

            "cluster_p":
                clustered_model.pvalues[variable]
        })

    results_df = pd.DataFrame(results)

    print()
    print(
        results_df
        .round(4)
        .to_string(index=False)
    )

    print()
    print(
        f"Number of observations: "
        f"{len(sample)}"
    )

    print(
        f"Number of swimmer clusters: "
        f"{sample['swimmer_id'].nunique()}"
    )


cluster_analysis(
    MEN_FILE,
    "MEN - CLUSTER ROBUST REGRESSION"
)

cluster_analysis(
    WOMEN_FILE,
    "WOMEN - CLUSTER ROBUST REGRESSION"
)
